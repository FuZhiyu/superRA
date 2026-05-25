---
title: "Comment sidecar format and server routes"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Define the sidecar YAML format for comments and implement the server-side routes for creating, listing, and resolving comments.

**Sidecar format** — `comments.yaml` next to each `task.md`:
```yaml
- id: 1
  author: Julie
  timestamp: 2026-05-24T10:30:00
  resolved: false
  anchor:
    section: "Objective"
    block_index: 2
    text_preview: "The server should work as"
  body: "Do we really need configurable root? YAGNI."
```

**Fields:**
- `id` — auto-incrementing integer within the file
- `author` — user name (configurable, default from git config)
- `timestamp` — ISO 8601
- `resolved` — boolean, toggleable
- `anchor.section` — the `## Heading` this comment is attached to
- `anchor.block_index` — 0-indexed block within the section (paragraph, list item, code block, etc.)
- `anchor.text_preview` — first ~60 chars of the block text, used for fuzzy re-anchoring when content shifts
- `body` — comment text (plain text or markdown)

**Server routes:**
- `POST /task/{path}/comment` — create a comment (body: `{section, block_index, text_preview, body}`)
- `GET /task/{path}/comments` — list all comments for a task (JSON)
- `PATCH /task/{path}/comment/{id}` — toggle resolved status
- `DELETE /task/{path}/comment/{id}` — delete a comment

**Anchor re-resolution:**
- On read, verify `block_index` still matches `text_preview`
- If mismatch, scan blocks in the section for a fuzzy match (substring containment) and update the index
- If no match found, mark the comment as `orphaned: true` and render it at the section level
