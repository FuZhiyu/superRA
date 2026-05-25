---
title: "Bubble comment badges up through collapsed tree nodes"
status: not-started
review_status: ~
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

