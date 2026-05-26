---
title: "Server-Side Switching"
status: implemented
review_status: implemented
integration_status: ~
depends_on: 
  - discovery

tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Add worktree listing and switching routes to `plan_dashboard.py` (`skills/task-system/scripts/plan_dashboard.py`). Refactor the module-level state to support hot-swapping `PLAN_ROOT` at runtime.

**New routes:**
- `GET /api/worktrees` — calls `discover_worktrees()` + `filter_worktrees()` + `sort_worktrees()`, returns JSON list with `path`, `branch`, `plan_title`, `is_current`, `has_plan`, `is_agent`, `last_activity` for each entry, ordered by last activity (most recent first). Include a `current` field with the active worktree path.
- `POST /api/worktree/switch` — accepts `{"plan_root": "<absolute-path>"}`. Validates the path is a known worktree with a valid `.plan/`. On success: updates `PLAN_ROOT`, rebuilds the tree, cancels the existing watcher and spawns a new one on the new root, updates `_project_root`, broadcasts `full-reload` SSE event, returns `{"ok": true, "plan_root": "...", "branch": "..."}`. On failure: returns 400/404, current state untouched.

**State management refactoring:**
- Store the watcher task in a module-level `_watcher_task: asyncio.Task | None` (currently created in `lifespan()` but not stored for later cancellation).
- Add `_current_worktree_path: str` to track which worktree is active.
- Switch sequence: cancel watcher → update `PLAN_ROOT` → `rebuild_tree()` → spawn new watcher → broadcast `full-reload`. Must be atomic from the client's perspective.

**Port derivation change:**
- Modify `_default_port()`: when a `git_common_dir` is available, hash it instead of `PLAN_ROOT`. This makes the port repo-stable across worktrees.
- In `main()`, call `get_git_common_dir()` before starting the server. If in a git repo, use the common dir for port derivation. Otherwise fall back to plan-root hash (backward compatible).

**Graceful degradation:** If not in a git repo, `/api/worktrees` returns a single entry (the current plan root) and the switch endpoint returns 404. The frontend hides the dropdown.

## Results

All changes are in [`plan_dashboard.py`](../../../../../skills/task-system/scripts/plan_dashboard.py).

**Module-level state additions** (lines 67-75):
- `_watcher_task: asyncio.Task | None` — stores the background watcher for cancellation on switch.
- `_current_worktree_path: str` — tracks the active worktree's absolute path.
- `_switch_lock: asyncio.Lock` — serializes concurrent switch requests.

**Top-level imports** (lines 32-39): `_parse_plan_title` added to the `_worktree_discovery` import block.

**`lifespan()` refactored** (lines 324-338): now stores the watcher task in `_watcher_task` and sets `_current_worktree_path` from `_project_root` at startup. Shutdown cancels via `_watcher_task` with a null guard.

**`GET /api/worktrees`** (lines 558-610): calls `discover_worktrees()` + `filter_worktrees()` + `sort_worktrees()`, returns JSON with `current` (active worktree path) and `worktrees` (list with `path`, `branch`, `plan_title`, `is_current`, `has_plan`, `is_agent`, `last_activity`). Non-git fallback returns a single entry for the current plan root; uses the top-level `_parse_plan_title` import.

**`POST /api/worktree/switch`** (lines 613-697): validates the requested `plan_root` against discovered worktrees, then performs the switch sequence under `_switch_lock`. Previous state (`PLAN_ROOT`, `_project_root`, `_current_worktree_path`) is saved before the watcher cancel. Steps 2-5 (update globals, rebuild tree, spawn watcher) are wrapped in try/except: on failure, globals are rolled back to saved values, a watcher is re-spawned on the old root, and a 500 error is returned. On success, broadcasts `full-reload` and returns `{"ok": true, "plan_root": "...", "branch": "..."}`.

**`_default_port()` updated**: accepts optional `git_common_dir` parameter. When provided, hashes the common dir instead of `PLAN_ROOT` so all worktrees of the same repo share one dashboard port. Falls back to plan-root hash when not in a git repo.

**`main()` updated**: calls `get_git_common_dir()` before port derivation and passes it to `_default_port()`. Startup log message shows the port derivation source.

## Review Notes

1. [MAJOR] **No rollback on switch sequence failure.** The "atomic switch sequence" in [plan_dashboard.py:646-670](../../../../../skills/task-system/scripts/plan_dashboard.py#L646) modifies global state incrementally (cancel watcher at step 1, update `PLAN_ROOT` at step 2) before calling `rebuild_tree()` at step 3. If `rebuild_tree()` raises (e.g., malformed task.md, filesystem permission error), the server is left in an inconsistent state: watcher cancelled and set to `None`, `PLAN_ROOT` pointing to the new root, but `_root_task`/`_task_index` holding the stale old tree and no watcher running. The objective states "On failure: returns 400/404, current state untouched" — this guarantee holds for pre-switch validation failures but not for errors during the switch sequence itself. **Fix:** Wrap steps 2-5 in a try/except that rolls back `PLAN_ROOT`, `_project_root`, and `_current_worktree_path` to their previous values and re-spawns a watcher on the old root if any step fails.
→ implemented: saved previous values before watcher cancel; wrapped steps 2-5 in try/except that rolls back all three globals and re-spawns a watcher on the old root, returning 500 on failure ([plan_dashboard.py:651-688](../../../../../skills/task-system/scripts/plan_dashboard.py#L651))

2. [MINOR] **No concurrency guard on switch endpoint.** Two concurrent `POST /api/worktree/switch` requests could interleave at the `await _watcher_task` point (step 1), causing both to proceed through the switch sequence independently. The second request's watcher task assignment at step 5 would orphan the watcher spawned by the first request. An `asyncio.Lock` around the switch sequence would prevent this. Low practical risk for a single-user dashboard, but worth noting.
→ implemented: added module-level `_switch_lock = asyncio.Lock()` (line 75) and wrapped the entire switch sequence with `async with _switch_lock:` ([plan_dashboard.py:75](../../../../../skills/task-system/scripts/plan_dashboard.py#L75), [plan_dashboard.py:650](../../../../../skills/task-system/scripts/plan_dashboard.py#L650))

3. [MINOR] **Private function import inside fallback branch.** [plan_dashboard.py:564](../../../../../skills/task-system/scripts/plan_dashboard.py#L564) imports `_parse_plan_title` from `_worktree_discovery` inside the function body of `list_worktrees`, even though `_worktree_discovery` is already imported at the module top level (lines 30-36). Either add `_parse_plan_title` to the top-level import or inline the title extraction logic to avoid the lazy import of a private symbol.
→ implemented: added `_parse_plan_title` to the top-level import from `_worktree_discovery` (line 34) and removed the inline import ([plan_dashboard.py:34](../../../../../skills/task-system/scripts/plan_dashboard.py#L34))
