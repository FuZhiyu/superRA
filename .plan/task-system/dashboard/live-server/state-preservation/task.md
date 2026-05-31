---
title: "Preserve UI state across SSE updates"
status: in-progress
depends_on: []
tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Fix the dashboard so that editing a `task.md` file does not destroy UI state. Currently, two problems cause data loss:

1. **Content changes** (task.md modified): The watcher broadcasts `task:{path}` SSE events, and htmx swaps the entire task node via `outerHTML`. This destroys expanded/collapsed state, open sections, scroll position, rendered markdown, and any in-flight comment forms.

2. **Structural changes** (task.md added/deleted, or child directories change): The watcher broadcasts `full-reload` which triggers `location.reload()`, destroying all client state.

**Goal:** After a task.md edit, the dashboard updates the changed content in place while preserving: (a) which task nodes are expanded/collapsed, (b) which sections are open/closed, (c) scroll position, (d) already-rendered markdown in open sections, (e) active filters and search, (f) comment form state. Structural changes (new/deleted tasks) should also preserve as much state as possible rather than doing a hard page reload.

**Files:** `skills/task-system/scripts/plan_dashboard.py` (server-side watcher and SSE broadcasting), `skills/task-system/scripts/templates/task_node.html` (task node template), `skills/task-system/scripts/templates/base.html` (client-side JS for SSE handling, toggle state, markdown rendering).

## Results

