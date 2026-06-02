---
title: "GitHub-style comment editing UX"
status: approved
depends_on: []
tags: []
created: 2026-05-25
---

## Objective

Redesign the comment editing UX to follow GitHub-style patterns. Three issues to fix:

**1. Button replacement during editing.** Currently `startEditComment()` hides the body and inserts a textarea + Save/Cancel, but the original Edit/Resolve/Delete action buttons remain visible. Fix: when entering edit mode, hide the actions div and show only Save/Cancel controls. On save or cancel, restore the original action buttons.

**2. Single-edit mode.** Currently multiple comments can be opened for editing simultaneously. When one is saved (`saveEdit()` calls `loadComments()` which re-renders all threads), other open editors lose their state — the user perceives this as "all of them are saved" but actually edits are lost. Fix: track the currently-editing comment globally. When `startEditComment()` is called on a new comment, auto-save the previous edit if content changed, or cancel it if unchanged. Only one comment editor open at any time.

**3. Newline display.** Comment bodies with newlines (e.g., multi-paragraph feedback) display as a single line because `body.textContent = c.body` doesn't render `\n` in HTML. Fix: add `white-space: pre-wrap` to the `.comment-body` CSS rule so newlines display correctly.

File: `skills/task-system/scripts/templates/base.html` — JS functions `startEditComment()` (line 1147), `renderCommentThread()` (line 1061), and CSS `.comment-body` (line 514).

## Results

All three changes implemented in [`base.html`](skills/task-system/scripts/templates/base.html):

**1. Button replacement** ([base.html:1180](skills/task-system/scripts/templates/base.html#L1180)). On entering edit mode, the actions div (Edit/Resolve/Delete) is hidden via `actionsDiv.style.display = 'none'`. Save/Cancel controls replace it. Both `saveEdit()` and `cancelEdit()` restore the actions div on exit.

**2. Single-edit mode** ([base.html:907](skills/task-system/scripts/templates/base.html#L907), [base.html:1148-1172](skills/task-system/scripts/templates/base.html#L1148)). Global `_activeCommentEdit` tracks the open editor. `_dismissActiveEdit()` closes any active editor before a new one opens: auto-saves if content changed (fire-and-forget API PATCH with local DOM text update, no `loadComments` re-render), cancels if unchanged. This avoids the race condition where `loadComments` from auto-save would destroy a newly-opened editor on the same task.

**3. Newline display** ([base.html:514](skills/task-system/scripts/templates/base.html#L514)). Added `white-space: pre-wrap` to `.comment-body` CSS so `\n` in comment bodies renders as visual line breaks.

All 53 existing dashboard tests pass.
