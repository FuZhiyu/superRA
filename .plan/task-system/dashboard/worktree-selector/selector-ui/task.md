---
title: "Frontend Worktree Selector"
status: implemented
review_status: revise
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

## Review Notes

1. **[CRITICAL]** Option value uses wrong path — switch will always 404. [base.html:973](../../../../../skills/task-system/scripts/templates/base.html#L973) sets `opt.value = wt.path`, which is the **worktree root** (e.g., `/path/to/repo`). This value is sent as `plan_root` to `POST /api/worktree/switch` ([base.html:999](../../../../../skills/task-system/scripts/templates/base.html#L999)). The server's switch handler ([plan_dashboard.py:633](../../../../../skills/task-system/scripts/plan_dashboard.py#L633)) matches the incoming value against `w.plan_root` (e.g., `/path/to/repo/.plan`). These paths will never match, so every switch attempt returns 404. The objective explicitly requires "Option value is the absolute `.plan/` path." **Fix:** The `/api/worktrees` response does not include a `plan_root` field in each entry — only `path` (worktree root) and `has_plan` (boolean). Either (a) add a `plan_root` field to the response entries in `list_worktrees()` and use it as `opt.value` in the JS, or (b) change the server switch handler to accept and match worktree root paths. Option (a) aligns with the objective and is the cleaner fix.

2. **[MINOR]** CSS `text-overflow: ellipsis` without `overflow: hidden`. [base.html:174](../../../../../skills/task-system/scripts/templates/base.html#L174) sets `text-overflow: ellipsis` on `.worktree-selector .hc-select` but does not set `overflow: hidden` or `white-space: nowrap`. On native `<select>` elements the browser clips text by its own rendering, so this is cosmetic — but the `text-overflow` declaration is effectively a no-op without its companions. Consider adding `overflow: hidden` for completeness, or removing `text-overflow: ellipsis` since the `max-width` alone constrains the element.
