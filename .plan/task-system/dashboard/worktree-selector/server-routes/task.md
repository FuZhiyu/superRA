---
title: "Server-Side Switching"
status: not-started
review_status: ~
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
