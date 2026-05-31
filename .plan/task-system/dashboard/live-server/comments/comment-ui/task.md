---
title: "Comment UI in dashboard"
status: approved
depends_on:
  - sidecar-format
tags: []
created: 2026-05-24
updated: 2026-05-25
---

## Objective

Implement the frontend commenting UI in the dashboard templates. GitHub-style gutter buttons, inline comment threads, and resolve/delete controls.

**Rendering task bodies as commentable blocks:**
- Modify the markdown rendering pipeline to wrap each block-level element (paragraph, list, code block, blockquote) in a container div with a data attribute: `data-section="Objective" data-block="2"`
- This requires either a markdown-it plugin or post-processing the rendered HTML to inject wrappers

**Gutter interaction:**
- On hover over a block, show a `+` button in the left gutter
- Click opens an inline comment form below the block
- Form fields: comment body (textarea), submit button
- On submit: `hx-post="/task/{path}/comment"` with the anchor data and body
- htmx swaps in the updated comment thread below the block

**Comment thread rendering:**
- Existing comments render as a collapsible thread below their anchored block
- Each comment shows: author, timestamp, body, resolve button, delete button
- Resolved comments are visually dimmed but still visible (toggleable)
- Orphaned comments (anchor lost) render at the section heading level with a warning indicator

**Live updates via SSE:**
- When a comment is added/resolved/deleted, the file watcher detects the `comments.yaml` change
- SSE pushes an update event, htmx swaps in the refreshed comment thread

**Styling:**
- Comment thread background: subtle tint (like GitHub's yellow)
- Gutter button: unobtrusive, appears only on hover
- Follow existing dark/light theme tokens

## Results

Implemented the full comment UI across two template files:

**`task_node.html`** -- Added `data-section` attributes to section wrapper divs (both named and extra sections) so JavaScript can identify which section a commentable block belongs to.

**`base.html`** -- All changes in the `<script>` block:

1. **`renderMarkdown(text, sectionName)`** -- Extended with optional `sectionName` parameter. When provided, post-processes the rendered HTML to wrap each top-level block element (P, UL, OL, PRE, BLOCKQUOTE, TABLE, H1-H6) in a `.commentable-block` div with `data-section` and `data-block` attributes, plus a `+` gutter button.

2. **`toggleSection()`** -- Modified to read `data-section` from the parent wrapper and pass it to `renderMarkdown()`. After rendering, calls `loadComments()` to fetch and display existing comments inline.

3. **`showCommentForm(btn)`** -- Creates an inline form (textarea + Comment/Cancel buttons) below the block. On submit, POSTs to `/api/task/{path}/comment` with section, block_index, text_preview (first 60 chars), and body. On success, removes form and reloads comments.

4. **`loadComments(taskPath)`** -- Fetches all comments from `/api/task/{path}/comments`, groups them by section+block_index, finds the matching `.commentable-block` elements, and appends rendered threads. Orphaned comments (no matching block in DOM) render at the section level with a `.comment-orphan-warning` indicator.

5. **`renderCommentThread(comments, taskPath)`** -- Builds a `.comment-thread` div with `.comment-item` entries showing author, timestamp, body, Resolve/Unresolve button, and Delete button. Resolved comments get the `.comment-resolved` class.

6. **`resolveComment()` / `deleteComment()`** -- PATCH and DELETE to the API, then reload comments.

7. **SSE listener** -- Listens for `htmx:sseMessage` events. When a `task:{path}` event fires and the task has open sections, re-fetches comments after a 200ms delay (to let the SSE swap complete first).

8. **`htmx:afterSwap` handler** -- Updated to pass section name to `renderMarkdown()` when re-rendering already-open sections after an SSE swap.

All 143 existing tests pass unchanged. Uses the existing CSS classes (`.commentable-block`, `.comment-gutter-btn`, `.comment-thread`, `.comment-item`, `.comment-meta`, `.comment-body`, `.comment-resolved`, `.comment-form`, `.comment-orphan-warning`) and the existing `/api/` comment routes.
