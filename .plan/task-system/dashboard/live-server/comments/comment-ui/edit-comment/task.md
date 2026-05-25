---
title: "Add comment editing support"
status: implemented
review_status: approved
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Allow users to edit existing comments in-place. Add an Edit button alongside Resolve/Delete on each comment. Clicking Edit replaces the comment body with an editable textarea pre-filled with the current text, with Save/Cancel controls. On save, PATCH the comment body via the API and re-render the thread (comment #2).

## Results

### Server-side changes

- Added `edit_comment(task_dir, comment_id, body)` function to [_comments.py](skills/task-system/scripts/_comments.py) that updates a comment's body text and saves to `comments.yaml`.
- Extended the PATCH route in [plan_dashboard.py](skills/task-system/scripts/plan_dashboard.py) to accept an optional JSON body with `{"body": "..."}`. When present, it calls `edit_comment` instead of `resolve_comment`. Without a body (or empty JSON), it falls back to the existing resolve-toggle behavior, preserving backward compatibility.

### Frontend changes

- Added Edit button to each comment in `renderCommentThread` in [base.html](skills/task-system/scripts/templates/base.html), positioned before Resolve and Delete.
- `startEditComment` function: hides the body text, inserts a pre-filled textarea and Save/Cancel buttons. Save sends `PATCH /api/task/{path}/comment/{id}` with the new body. Cancel restores the original text.
- Edit textarea supports the same keyboard shortcuts as the new-comment form: Cmd/Ctrl+Enter to save, Escape to cancel.

