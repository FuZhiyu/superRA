---
title: "Bubble comment badges up through collapsed tree nodes"
status: implemented
review_status: implemented
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Currently, unresolved comment badges only appear on section toggles (e.g., "Objective 2") inside an expanded task body. When the task node or any ancestor is collapsed, the badge disappears — the user has no way to know that comments exist deeper in the tree without expanding every node.

Fix: bubble comment badges up through the tree so they appear on the **deepest collapsed ancestor** that contains tasks with unresolved comments. When a user collapses a subtree, the comment count aggregates onto that node's task row. When they expand it, the badge moves down to the next collapsed level (or to the section toggles if the task body is fully expanded).

**Requires two changes:**

**1. Server: tree-wide comment summary endpoint.** Add `GET /api/comments/summary` to `plan_dashboard.py`. Walk the entire plan tree, check each task directory for `comments.yaml`, count unresolved comments, and return `{taskPath: unresolvedCount}` for all tasks with count > 0. The frontend currently fetches comments per-task only on expand — it cannot know about comments in collapsed subtrees without this endpoint.

**2. Client: badge bubbling logic.** Add `updateTreeCommentBadges()` to `base.html`:
- Fetch `/api/comments/summary` to get `{taskPath: count}` for all tasks with unresolved comments.
- For each task path with comments, find its `.task-node` in the DOM. Walk up the DOM through ancestor `.task-node` elements. Find the **deepest ancestor whose `.task-body` is not `.open`** (i.e., collapsed). That is the display target.
- If the task itself is collapsed (body not open), the badge goes on its own `.task-row`.
- If the task is expanded and sections are visible, section-level badges handle it (existing `updateSectionBadges` behavior).
- Aggregate: if multiple descendant tasks have comments and they all bubble up to the same collapsed ancestor, sum their counts into one badge on that ancestor's row.
- Use the same `.section-comment-badge` CSS class (or a `.tree-comment-badge` variant) on the task row, positioned after the status badge or progress indicator.

**Call sites — when to recalculate:**
- On initial page load (after DOM ready).
- On `toggleTask()` — expanding or collapsing a node changes which ancestor is the "deepest collapsed," so badges need to shift.
- On SSE `comments.yaml` change events — re-fetch `/api/comments/summary` and recalculate.

**Edge cases:**
- Multiple tasks with comments at different depths under the same collapsed ancestor → sum into one badge.
- A task has comments in multiple sections (e.g., Objective has 2, Results has 1) → task-level count is 3.
- Comments exist but are all resolved → no badge (count = 0).
- Task is fully expanded with sections visible → no tree-level badge, section badges handle it (existing behavior).

Files:
- `skills/task-system/scripts/plan_dashboard.py` — new `/api/comments/summary` endpoint
- `skills/task-system/scripts/templates/base.html` — `updateTreeCommentBadges()` function, CSS for tree-level badge, call sites in `toggleTask()` and SSE handler

## Results

### Server: `GET /api/comments/summary`
Added endpoint at [plan_dashboard.py:422-439](skills/task-system/scripts/plan_dashboard.py#L422). Recursively walks `_root_task` tree, calls `load_comments()` on each task's `dir_path`, counts unresolved comments, and returns `{taskPath: unresolvedCount}` for tasks with count > 0. Guarded by `_COMMENTS_AVAILABLE` and `_root_task` checks.

### Client: `updateTreeCommentBadges()`
Added function at [base.html:1099-1145](skills/task-system/scripts/templates/base.html#L1099). Logic:
- Fetches `/api/comments/summary` for all unresolved counts
- For each task path with comments, finds its `.task-node` in the DOM. If the node isn't rendered (lazy-loaded depth >= 2), walks up path segments (`split('/')` + `pop()`) until finding a rendered ancestor
- If the task's `.task-body` is open, skips (section-level badges handle it)
- Otherwise, walks up ancestor `.task-node` elements to find the deepest collapsed ancestor
- Aggregates counts from multiple descendants onto the same collapsed ancestor via a `Map`
- Renders `.tree-comment-badge` spans on the target `.task-row` elements
- Clears all existing `.tree-comment-badge` elements before recalculating

### CSS
Shared base styling for `.section-comment-badge` and `.tree-comment-badge` (accent-background pill). Section badges keep `margin-left: auto` (right-aligned in section toggles); tree badges use `margin-left: 4px` (inline after status badge/progress in task rows). Badge is inserted after `.task-progress` or `.badge` element in the row rather than appended at the end.

### Call sites
- `DOMContentLoaded` event listener for initial page load
- At the end of `toggleTask()` after expand/collapse
- SSE `task:` message handler (300ms delay to let swap render first)

### Tests
4 new tests added to [test_dashboard.py](skills/task-system/scripts/test_dashboard.py):
- `test_comments_summary_empty` — returns `{}` with no comments
- `test_comments_summary_counts_unresolved` — correct counts across multiple tasks
- `test_comments_summary_excludes_resolved` — resolved comments not counted
- `test_comments_summary_nested_tasks` — includes child task comments

All 57 tests pass (53 existing + 4 new).
