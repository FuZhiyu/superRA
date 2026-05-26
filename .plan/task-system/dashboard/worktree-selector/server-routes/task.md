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

**Module-level state additions** (lines 67-71):
- `_watcher_task: asyncio.Task | None` — stores the background watcher for cancellation on switch.
- `_current_worktree_path: str` — tracks the active worktree's absolute path.

**`lifespan()` refactored** (lines 321-335): now stores the watcher task in `_watcher_task` and sets `_current_worktree_path` from `_project_root` at startup. Shutdown cancels via `_watcher_task` with a null guard.

**`GET /api/worktrees`** (lines 554-607): calls `discover_worktrees()` + `filter_worktrees()` + `sort_worktrees()`, returns JSON with `current` (active worktree path) and `worktrees` (list with `path`, `branch`, `plan_title`, `is_current`, `has_plan`, `is_agent`, `last_activity`). Non-git fallback returns a single entry for the current plan root.

**`POST /api/worktree/switch`** (lines 610-676): validates the requested `plan_root` against discovered worktrees, then performs the atomic switch sequence: cancel watcher, update `PLAN_ROOT`, `rebuild_tree()`, update `_project_root` and `_current_worktree_path`, spawn new watcher, broadcast `full-reload`. Returns `{"ok": true, "plan_root": "...", "branch": "..."}` on success. Returns 400/404 with current state untouched on failure.

**`_default_port()` updated** (lines 1701-1712): accepts optional `git_common_dir` parameter. When provided, hashes the common dir instead of `PLAN_ROOT` so all worktrees of the same repo share one dashboard port. Falls back to plan-root hash when not in a git repo.

**`main()` updated** (lines 1773-1781): calls `get_git_common_dir()` before port derivation and passes it to `_default_port()`. Startup log message shows the port derivation source.
