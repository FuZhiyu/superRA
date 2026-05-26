---
title: "Frontend Worktree Selector"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - server-routes

tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

**Dispatch note:** Implementer agents for this task must load a frontend design skill for UI/UX quality.

Add a worktree selector dropdown to the dashboard header bar in `skills/task-system/scripts/templates/base.html`. The dropdown lets the user switch which worktree's `.plan/` is displayed.

**Placement:** In the `.header` div, between the title (`header-title`) and the summary bar (`header-stats`). Only rendered when multiple worktrees are available.

**HTML structure:**
- A `<select>` element styled consistently with the existing `.hc-select` status filter dropdown (see line ~587 of `base.html`)
- Options ordered by last activity (most recent first), matching the server response order.
- Each `<option>` shows the branch name as primary label, with plan title as secondary context if available. Agent worktrees (`is_agent`) may be visually distinguished (e.g. dimmed or labeled). The currently active worktree is `selected`.
- Option value is the absolute `.plan/` path.

**Behavior on selection change:**
- `fetch` POST to `/api/worktree/switch` with the selected plan root (use fetch, not htmx — the response is JSON, not HTML)
- On success: the `full-reload` SSE event fired by the server triggers the existing htmx full-reload handler (see `sse-swap="full-reload"` at line ~605), which refreshes the page. Update the header title to reflect the new worktree's root task title.
- On error: show a brief alert with the error message, revert the dropdown to the previous selection.

**Initialization:**
- On page load, `fetch GET /api/worktrees`. If only one worktree or not in a git repo, hide the dropdown. If multiple, populate and show it.
- Re-fetch the worktree list on each `full-reload` event (worktrees may appear/disappear).

**Visual design:** Match the warm parchment/ink palette. The dropdown should feel like a natural part of the header. Consider a small branch icon (Unicode `⑂` or `⎇`) as a visual label.
