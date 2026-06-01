---
title: "Fix gutter button and comment form UX bugs"
status: approved
depends_on: []
tags: []
created: 2026-05-25
---

## Objective

Fix three related bugs in the comment gutter/form interaction: (1) the plus button is clipped/only half shown (comment #1), (2) clicking plus on a block with existing comments cycles through existing comments' resolve/delete buttons one by one before showing the new comment form (comment #4), (3) adding a comment causes the section to fold back, forcing the user to re-expand (comment #5).

## Results

All three bugs fixed in [base.html](skills/task-system/scripts/templates/base.html):

1. **Clipped gutter button**: Changed `.commentable-block` to use `padding-left: 28px; margin-left: -28px` so the block reserves space for the gutter button. Moved button from `left: -28px` to `left: 0` with `z-index: 1`. The button is now fully visible within the padding area instead of relying on parent overflow.

2. **Form toggle cycling**: Changed `showCommentForm` from toggle behavior (remove existing form and return) to focus behavior (if a form already exists, focus its textarea). The `+` button now always either shows the form or focuses the existing one — no removal/re-creation cycle.

3. **Section folding after comment**: The root cause is that saving a `comments.yaml` triggers the file watcher, which broadcasts an SSE `task:{path}` event, causing htmx to do an `outerHTML` swap of the entire task node — resetting all expand/collapse state. Fixed by adding a suppression mechanism: local comment operations (POST/PATCH/DELETE) record a timestamp in `_commentEditPaths`, and an `htmx:sseBeforeMessage` listener cancels the SSE swap for that task within a 3-second window. The client already refreshes comments via `loadComments()` after the API call succeeds, so the SSE swap is redundant.

