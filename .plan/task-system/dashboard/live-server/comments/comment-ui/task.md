---
title: "Comment UI in dashboard"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - ../sidecar-format
tags: []
created: 2026-05-24
updated: 2026-05-24
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
