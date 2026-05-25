---
title: "Fix rebuild_task() to discover new children"
status: implemented
review_status: implemented
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

rebuild_task() in plan_dashboard.py (lines 81-106) preserves stale children on partial updates. When a task.md modification event fires, the function re-parses the task but does updated.children = existing.children (line 100), blindly preserving the old children list. If subtask directories were created after the server started, or the watcher missed the Change.added FSEvents, those children are never discovered — the in-memory tree stays stale and the dashboard never renders them.

Fix: after re-parsing the task, re-walk the task directory for child subdirectories containing task.md. Build new child Task objects for any directories not already in the existing children list, and add them to the task index. Remove children whose directories no longer exist. Then replace the node in the tree as before. This makes every partial update self-healing — even if the watcher misses a structural event, the next modification to any ancestor discovers the new or removed children.

Also broadcast a full-reload SSE event (not just the task fragment) when the child set changes, so the frontend re-renders the full tree structure.

File: skills/task-system/scripts/plan_dashboard.py, function rebuild_task() at line 81.

## Results

**Changed files:**
- [plan_dashboard.py:81](skills/task-system/scripts/plan_dashboard.py#L81) -- `rebuild_task()` rewritten
- [plan_dashboard.py:127](skills/task-system/scripts/plan_dashboard.py#L127) -- new `_remove_from_index()` helper
- [plan_dashboard.py:218](skills/task-system/scripts/plan_dashboard.py#L218) -- `_watch_plan_root()` updated to handle `(task, children_changed)` tuple
- [test_dashboard.py:283](skills/task-system/scripts/test_dashboard.py#L283) -- existing tests updated, 3 new tests added

**What changed in `rebuild_task()`:**

1. Return signature changed from `Task | None` to `tuple[Task | None, bool]`. The bool (`children_changed`) is `True` when the set of child directory paths changed since the last index snapshot.
2. Instead of `updated.children = existing.children`, the function calls `_walk_children(task_dir, PLAN_ROOT)` to re-discover child subdirectories from disk. This uses the same `_walk_children` already used by `walk_plan` for the initial tree build, so topological sorting and recursive parsing are preserved.
3. Stale children (directories that no longer exist) are removed from `_task_index` via the new `_remove_from_index()` recursive helper. New children are added via `_build_index()`.
4. The caller in `_watch_plan_root()` unpacks the tuple. If any task's children changed during the batch, it broadcasts `full-reload` instead of per-task fragment SSE events.

**New tests (all pass):**
- `test_rebuild_task_discovers_new_children` -- child created after initial build is found by rebuild
- `test_rebuild_task_removes_deleted_children` -- child removed from disk is dropped from tree and index
- `test_rebuild_task_discovers_existing_children` -- (renamed from `test_rebuild_task_preserves_children`) existing children are re-discovered correctly with `children_changed=False`

**Test results:** 53/53 pass in `test_dashboard.py`, 92/92 pass in `test_task_system.py`.
