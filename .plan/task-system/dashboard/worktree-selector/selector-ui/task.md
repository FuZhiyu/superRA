---
title: "Frontend Worktree Selector"
status: implemented
review_status: approved
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

## Results

All changes in [base.html](../../../../../skills/task-system/scripts/templates/base.html).

**CSS** (lines 160-175): `.worktree-selector` wrapper starts `display: none` (JS shows it when multiple worktrees exist), uses flexbox with 6px gap. `.wt-icon` uses `--text-mute` for the branch icon. The inner `.hc-select` gets `max-width: 240px` with `text-overflow: ellipsis` to prevent long branch names from stretching the header.

**HTML** (lines 596-600): Placed between `#header-title` and `#summary-bar` in the `.header` div. Contains a `&#9095;` (⎇) branch icon span and a `<select class="hc-select">` element. The `onchange` handler calls `switchWorktree(this.value)`.

**JavaScript** (lines 955-1015):
- `populateWorktreeSelector(data)`: Hides the selector if data has 0-1 worktrees. Otherwise builds `<option>` elements: branch name as primary label, ` -- plan_title` appended when available, `[agent]` prefix and `opacity: 0.6` for agent worktrees. Sets `selected` on the current worktree via `is_current`. Tracks `_wtPreviousValue` for error rollback.
- `fetchWorktrees()`: Fetches `GET /api/worktrees`, passes response to `populateWorktreeSelector`. Silently fails (selector stays hidden) on network error.
- `switchWorktree(planRoot)`: Sends `POST /api/worktree/switch` with `{plan_root}`. On success, updates `_wtPreviousValue` and lets the SSE `full-reload` event (broadcast by the server) trigger `location.reload()`. On error, shows `alert()` with the error message and reverts the dropdown to `_wtPreviousValue`.
- `fetchWorktrees()` called at script load time (line 1015). Re-fetch on full-reload is handled implicitly: `location.reload()` re-runs the entire page including `fetchWorktrees()`.

