---
title: "Add keyboard shortcuts for comment interaction"
status: approved
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Add standard keyboard shortcuts for the comment form and thread: Cmd+Enter (Ctrl+Enter on Windows) to submit the comment, and Escape to cancel/close the comment form. These should work naturally when interacting with comments (comment #1).

## Results

Added keydown listener on the comment form textarea in [base.html](skills/task-system/scripts/templates/base.html):

- **Cmd+Enter / Ctrl+Enter**: submits the comment (calls `submitComment()`). Uses `e.metaKey` (Mac Cmd) and `e.ctrlKey` (Windows/Linux Ctrl) for cross-platform support.
- **Escape**: removes the comment form (same as clicking Cancel).

Both shortcuts call `e.preventDefault()` to avoid inserting a newline or triggering browser defaults.

