---
title: "Fix rebuild_task() to discover new children"
status: not-started
review_status: ~
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

