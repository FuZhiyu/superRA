---
title: "Cross-worktree isolation + SSE-scoping integration tests"
status: implemented
depends_on: 
  - 01-per-worktree-state
  - 02-per-worktree-sse
  - 03-worktree-url-routing

tags: []
created: 2026-06-03
---

## Objective

The end-to-end gate for the feature: prove that one server serving multiple worktrees keeps them **isolated** and that the URL drives worktree selection. Tasks 01–03 each ship their own unit tests; this task adds the integration tests that only make sense once all three land, and which are the real guarantee the user cares about.

**Deliverables — integration tests in [test_dashboard.py](../../../../../skills/task-system/scripts/test_dashboard.py) (or a new `test_multi_worktree.py` alongside it), building ≥2 task trees in `tmp_path` and registering them as discoverable worktrees:**

1. **Render isolation.** Concurrent requests with `?wt=A` and `?wt=B` to `/`, `/nav`, `/node/{path}`, `/dag`, and the comment routes each return the matching worktree's content; no field from one bleeds into the other. A request with no `?wt=` returns the launch worktree.
2. **Mutation isolation.** Creating/editing a comment or task under worktree A does not appear in worktree B's responses, and vice versa.
3. **SSE scoping.** A simulated change under worktree A delivers an SSE event to A's registered client(s) only; B's client receives nothing. Cover all event types in play (`full-reload`, `summary-updated`, `task:<path>`).
4. **Watcher lifecycle under multiplexing.** First A-client starts A's watcher; first B-client starts B's; dropping A's last client stops A's watcher but leaves B's running; a crashed watcher is respawned on the next client.
5. **Default + unknown worktree.** No `?wt=` → launch worktree; unknown `?wt=` → 404; standalone export path still renders a single worktree and ignores `?wt=`.

**Scope boundary.** Integration/isolation coverage only. If a test exposes a behavior gap, fix it in the owning task (01/02/03) — do not patch product behavior from inside this task; route the gap back via the orchestrator.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Keep edits and commits on this worktree's branch.

## Validation

- The new integration tests pass and genuinely exercise two concurrently-served worktrees through one app instance (not two servers).
- Running the full task-system suite is green: `uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts -q`.
- The isolation tests fail if the per-worktree resolver, SSE scoping, or watcher lifecycle is reverted — i.e. they actually pin the feature, not just smoke-test it.

## Planner Guidance

- Reuse the `TestClient` + `tmp_path` + `_write_task_md()` fixtures already in [test_dashboard.py](../../../../../skills/task-system/scripts/test_dashboard.py); the worktree-discovery tests in `test_worktree_selector.py` show how to register/mock discovered worktrees.
- TestClient disables lifespan (no live watcher), so drive watcher/queue lifecycle through the per-worktree functions directly, mirroring the existing `TestSSEBroadcast` approach.
- Write the isolation assertions to be red on a global-state regression (assert B is unchanged after an A-side mutation), so they protect the architecture going forward.

## Results

Added the cross-cutting integration/isolation suite in a new file [test_multi_worktree.py](../../../../../skills/task-system/scripts/test_multi_worktree.py) (17 tests) alongside `test_dashboard.py`. Every test drives **one** `plan_dashboard.app` instance serving **two** worktrees concurrently — never two servers — reusing `_write_task_md` from `test_dashboard.py` and the per-worktree plumbing (`_worktree_cache`, `_build_worktree_state`, `_worktree_id_for_plan_root`, `resolve_worktree`, `_rebuild_and_broadcast`, `_ensure_watcher`/`_stop_watcher`) from `plan_dashboard`.

The `two_worktrees` fixture differs from `test_dashboard.py`'s `two_worktree_client` in one deliberate way that closes advisory (1): worktree B is **not** hand-seeded into the cache. Instead `discover_worktrees` is monkeypatched to report both worktrees, so B is resolved lazily through `resolve_worktree → _discovered_worktree_map` on first use — exercising the real discovery → lazy-build path that the cache-seeding fixtures bypass.

Coverage by deliverable:

1. **Render isolation** (`TestRenderIsolation`, 6 tests) — `/`, `/nav`, `/node/{path}`, `/dag`, and the comment routes each render the `?wt=`-named worktree with no cross-bleed; a bare request renders the launch worktree (A).
2. **Mutation isolation** (`TestMutationIsolation`, 2 tests) — a comment create under A and a disk-edit+invalidate under A both leave B's responses **byte-for-byte unchanged** (captured-before / asserted-equal-after), so they go RED on a global-state regression rather than smoke-testing.
3. **SSE scoping** (`TestSSEScopingAcrossWorktrees`, 3 tests) — content edits (`task:<path>` + `summary-updated`), structural adds (`full-reload` + `summary-updated`), and concurrent A/B edits each reach only the mutating worktree's queue (`qb.empty()`); all event types in play are covered.
4. **Watcher lifecycle under multiplexing** (`TestWatcherLifecycleMultiplexed`, 2 tests) — A and B watchers are independent: stopping A leaves B running; a crashed A watcher respawns without disturbing B.
5. **Default + unknown + standalone** (`TestDiscoveryDrivenResolve`, 4 tests) — lazy-build-from-discovery for B; unknown `?wt=` → 404 across read routes; basename-collision disambiguation (two `…/shared/superRA` trees resolve distinctly by longest-unique-suffix, closing advisory (1)'s second half); and `/export?wt=B` produces a server-less single-worktree download (`window.STANDALONE = true`) scoped to B only.

**Architecture-pinning verified, not assumed.** I temporarily injected two regressions against a throwaway copy and confirmed RED, then restored the source clean:

- `resolve_worktree` collapsed to ignore `?wt=` (global launch-worktree behavior) → **13 of 16** tests failed (all render/mutation/discovery + the cross-worktree watcher tests).
- `_broadcast` collapsed to a global all-clients broadcast (ignore worktree scope) → the two scoped SSE tests' `qb.empty()` assertions failed.

The 3 tests that survive the resolver regression drive `_rebuild_and_broadcast` directly and pin SSE scoping independently of request resolution — correct separation.

**Validation gate:** full suite green from live source — `uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts -q` → **451 passed** (was 434 before this task; +17 new). No product behavior gap surfaced; every isolation property held under the real implementation, so no routing back to 01/02/03 was needed.
