---
title: "Cross-worktree isolation + SSE-scoping integration tests"
status: not-started
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
