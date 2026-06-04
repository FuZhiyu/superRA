---
title: "Serve multiple worktrees on demand (per-request worktree resolution)"
status: revise
depends_on: []
tags: []
created: 2026-06-03
---

## Objective

Refactor the task dashboard server from a **single global "current worktree" root** to **serving any discovered worktree on demand, resolved per request**. After this work, the active worktree is a dimension of the request (carried in the browser URL), multiple browser tabs can view different worktrees of the same repo against one server/port without fighting over shared state, and the URL is bookmarkable / shareable to a specific worktree.

**The problem.** Today the server holds one global root in module singletons — `PLAN_ROOT`, `_root_task`, `_task_index`, `_project_root`, `_current_worktree_path` ([plan_dashboard.py:65-82](../../../../skills/task-system/scripts/plan_dashboard.py#L65)). Every route reads them; `POST /api/worktree/switch` ([plan_dashboard.py:757](../../../../skills/task-system/scripts/plan_dashboard.py#L757)) atomically mutates them and `_broadcast("full-reload")` to **all** SSE clients. So switching worktrees flips every open tab, and the browser URL never encodes which worktree is shown (the hash is task-path only). The user wants the worktree in the URL; the right way to get there is per-request resolution, not URL-encoding layered on top of mutable global state.

**The shape of the fix** (decomposed into the child tasks):
- **01 — per-worktree state cache + request resolution.** Replace the global singletons with a `worktree → (root_task, index, project_root, plan_root)` cache, built lazily per worktree and invalidated by that worktree's watcher. Add a `resolve_worktree(request)` helper and thread it through every handler. Default to the launch worktree when the request names none, preserving today's behavior and standalone export.
- **02 — per-worktree SSE + on-demand watchers.** Replace the single `_sse_clients` set and single watcher with per-worktree client sets and per-worktree watchers spun up on the first connected client and torn down on the last. Scope `_broadcast` and `/events` by worktree.
- **03 — worktree-in-URL routing.** Encode the worktree in the browser URL as a `?wt=<name>` query param; on load, resolve it and render that worktree; make the selector update the URL (navigate) instead of issuing a global server switch; keep `PROJECT_ROOT` (the vscode-link base) per-worktree; leave standalone (`file://`) export single-worktree and unaffected.
- **04 — cross-worktree integration tests.** The end-to-end gate: two worktrees served concurrently by one server stay isolated (tree, comments, SSE events), a `?wt=` URL loads the right tree, and switching one tab does not disturb another.

### Design decisions (settled at planning; reopen via the change protocol if implementation invalidates them)

1. **URL scheme = query param `?wt=<name>`**, not a path prefix. It leaves the hash router (`#/<task-path>`, the single source of truth) untouched, mirrors the existing `?root=` convention already used by `/dag` and `/export`, and is the smallest diff. Path-prefix (`/<worktree>/#/...`) was considered and rejected for this pass because it requires restructuring all FastAPI routes and resolving home-route ambiguity.
2. **Worktree id in the URL = the worktree directory basename** (e.g. `better-handoff`), not the absolute `plan_root` path. It is readable, matches how a user refers to a worktree, and the server resolves it against `discover_worktrees()`. If two discovered worktrees share a basename, the server falls back to longest-unique-suffix disambiguation; document the rule where it lives.
3. **The launch worktree is the default.** A request with no `?wt=` resolves to the worktree the server was started in — so existing links, the CLI `serve --root`, and standalone export behave exactly as today.
4. **Keep one process / one port per repo.** The port is already derived per `git_common_dir` so all of a repo's worktrees hash to the same port ([plan_dashboard.py:1295](../../../../skills/task-system/scripts/plan_dashboard.py#L1295)); this refactor multiplexes them inside the one process rather than spawning a server per worktree.
5. **`/api/worktree/switch` global mutation is retired.** "Switching" becomes navigating to a different `?wt=` URL. Keep the endpoint only if a non-URL consumer still needs it; otherwise remove it and its global broadcast.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Concurrent worktrees of this repo exist; keep all edits and commits on this worktree's branch.

This task touches `skills/task-system/scripts/*` (the task-system package). No Codex-generated agent files are involved. Treat changes to `plan_dashboard.py` / `templates/base.html` as skill-package code; do not hand-edit any `skills/task-system/build/lib/...` build output.

## Validation

The feature is correct when, against one running server (one port) over a repo with ≥2 worktrees each containing a `superRA/` tree:

- Opening `/?wt=<A>#/<task>` renders worktree A's tree; opening `/?wt=<B>#/<task>` in another tab renders worktree B's tree; **neither tab changes when the other loads or when a task file in the other worktree changes**.
- A live edit to a task file under worktree A pushes an SSE update to A's tab only; B's tab receives nothing.
- A request with no `?wt=` renders the launch worktree (today's behavior).
- Standalone (`file://`) export still renders a single worktree with the selector hidden and ignores `?wt=`.
- The full task-system test suite passes, including new per-worktree isolation and SSE-scoping tests.

## Planner Guidance

- The cleanest seam (per exploration): a `@dataclass WorktreeState` holding `(root_task, task_index, project_root, plan_root)`, a module dict `_worktree_cache: dict[str, WorktreeState]` keyed by the resolved worktree id, and a `resolve_worktree(request) -> WorktreeState` that reads `?wt=` (falling back to the launch worktree) and lazily builds+caches. Render helpers (`plan_dashboard.py:329-395`) already take explicit `task` / `project_root` args, so most handlers change by ~1-2 lines (resolve, then pass the resolved root instead of the global).
- `_set_module_state()` + the `/export` handler already snapshot/restore module state ([plan_dashboard.py:894](../../../../skills/task-system/scripts/plan_dashboard.py#L894), `:1021`) — a working precedent for per-request scoping; prefer evolving the cache over that ad-hoc save/restore.
- SSE (task 02) is the risk center. Mirror the structures exploration proposed: `_worktree_clients: dict[wt, set[Queue]]`, `_worktree_watchers: dict[wt, asyncio.Task]`, `_ensure_watcher(wt)` (guard with `task.done()` to survive a crashed watcher), `_stop_watcher(wt)` on last disconnect, and `_broadcast(event, data, wt)` keyed by worktree. `/events` takes the worktree from `?wt=`.
- Discovery is done — reuse `_worktree_discovery.discover_worktrees()` / `WorktreeInfo` ([_worktree_discovery.py](../../../../skills/task-system/scripts/_worktree_discovery.py)); do not reimplement worktree enumeration.
- Mirror the existing `worktree-selector/` subtree's decomposition and Results-citation style (file links + line ranges).

## Critical Files

- [`skills/task-system/scripts/plan_dashboard.py`](../../../../skills/task-system/scripts/plan_dashboard.py) — the server; all of tasks 01 and 02 live here.
- [`skills/task-system/scripts/templates/base.html`](../../../../skills/task-system/scripts/templates/base.html) — the client; task 03 (URL routing + selector) lives here.
- [`skills/task-system/scripts/_worktree_discovery.py`](../../../../skills/task-system/scripts/_worktree_discovery.py) — existing, tested worktree discovery; reuse, don't reimplement.
- [`skills/task-system/scripts/test_dashboard.py`](../../../../skills/task-system/scripts/test_dashboard.py) — server test patterns (TestClient, fixtures) tasks 01/02/04 extend.
- [`superRA/task-system/dashboard/worktree-selector/`](../worktree-selector/) — the sibling task tree to mirror for decomposition and citation style.

## Results

## Review Notes

Integration review of `0bdca4d5..HEAD` (HEAD `858b2ded`), INTEGRATION lens (per-task correctness was approved task-by-task and not re-litigated). Full suite green from live source: `uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts -q` → **451 passed**. Drift-test pinning independently verified by neutralizing `?wt=` resolution in a throwaway copy of `resolve_worktree` and running `test_multi_worktree.py` → **14 of 17 failed** (the 3 survivors drive `_rebuild_and_broadcast` directly and pin SSE scoping independent of request resolution, matching task 04's claim); source restored clean afterward. Codebase fit, minimum-diff, and dead-code sweeps all clean (see below). One blocking doc-audit finding.

1. **MAJOR — doc-audit.** [`references/internals.md`](../../../../skills/task-system/references/internals.md) §Dashboard ([internals.md:215](../../../../skills/task-system/references/internals.md#L215)) still describes the **retired** one-server-per-worktree model and never mentions the new per-request `?wt=` model this feature introduces. The walk-up from `skills/task-system/scripts/` reaches this as the governing dashboard/architecture doc. Two specific stale clauses on line 215: (a) "Port is derived deterministically from **the plan root path**" — the port is now derived from `git_common_dir` (`_default_port`, [plan_dashboard.py:1529-1542](../../../../skills/task-system/scripts/plan_dashboard.py#L1529)), with plan-root hashing only as a no-git fallback; (b) "so multiple worktrees can **each run their own dashboard** without conflicts" — that is exactly the model this feature retires. All worktrees of one repo now hash to the **same** port and are multiplexed inside one process, selected per request by `?wt=<basename>` in the browser URL; switching is client-side `pushState` navigation, not a `POST /api/worktree/switch` server mutation (that endpoint and `_current_worktree_path`/`_sse_clients`/`_watch_plan_root` are gone); SSE/file-watching is now per-worktree and on-demand. Fix: rewrite the §Dashboard port/multi-worktree sentence to describe one-server-per-repo + `?wt=` per-request resolution (port from `git_common_dir` so a repo's worktrees share one port and are served on demand, default = launch worktree, switch = navigate), and add a short note on the per-worktree on-demand SSE/watcher model so the section no longer describes a single global watcher. Lines 213/217 (serve resolution, auto-rebuild) remain accurate and need no change. (Line 215 predates this feature — last written `b858b47e1`, 2026-06-02 — but this diff is what makes the second clause actively wrong, so it is in-scope for this integration's doc audit.)
>    → implemented: rewrote `references/internals.md` §Dashboard line 215 — port now described as derived from the repository's git common directory (plan-root fallback) so a repo's worktrees share one server; added the per-request `?wt=<worktree-basename>` model (default = launch worktree, switch = in-page navigation, two tabs independent on one port) and the per-worktree on-demand SSE/watcher behavior, replacing the retired "each run their own dashboard" / single-global-watcher description.

**Non-findings confirmed (informational):**
- *Codebase fit — clean.* New names (`WorktreeState`, `resolve_worktree`, `_worktree_cache`, `_worktree_clients`, `_worktree_watchers`, `_worktree_locks`, `_launch_wt_id`; client `ACTIVE_WT`, `wtUrl`, `switchWorktree`, `launch_wt_id`) follow the module's existing conventions. No orphaned globals or dead code from the retired model survive a whole-package grep: `_current_worktree_path` / `_sse_clients` / `_watch_plan_root` / the `POST /api/worktree/switch` route and its client caller are fully removed (the `_get_current_worktree_path` git helper in `_worktree_discovery.py` is unrelated and retained by design); the stale `_watch_plan_root` doc/comment references task 02's review flagged as advisory were swept in `tests/test_state_preservation.py`; server-global `current`/`is_current` fields are gone.
- *Minimum diff — clean.* Every surviving hunk in the production files and the test files ties to an approved objective (per-worktree state/SSE/URL routing, switch retirement, the new `launch_wt_id`/`wt_id` `/api/worktrees` contract, the 17 integration tests). No debug prints, no `TODO`/`FIXME`, no commented-out experiments, no drive-by reformatting.
- *Final Diff Self-Check trail absent, not blocking here.* No `**Final diff self-check:**` line exists in any task's Results, but these tasks were implemented/approved through `superimplement` per-task, not via a `Stage: integration` refactor implementer pass, and Sync was intentionally skipped. The trail is the integrate-step implementer's discipline; its absence is expected given no such dispatch occurred and is not a task-level gap.
