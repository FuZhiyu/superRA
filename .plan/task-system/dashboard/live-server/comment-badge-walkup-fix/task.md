---
title: "Fix comment badge walk-up to check children visibility, not body open state"
status: approved
depends_on:
  - comments
  - root-task-rendering
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

`updateTreeCommentBadges()` walks up ancestor `.task-node` elements to find a collapsed ancestor for badge placement. Two bugs:

1. **Wrong visibility check.** The walk-up checks `ancestorBody.classList.contains('open')` — whether the ancestor's *body sections* are expanded. But body expansion and children visibility are orthogonal: `toggleTask()` sets `children.style.display` and `body.classList.add('open')` together, but the relevant question is whether the *children container* is hidden. A task's children being visible means descendant task rows are shown in the tree; body sections being open means the task's own markdown content is visible. The badge should bubble based on children visibility, not body state.

2. **Walks to shallowest instead of stopping at first visible ancestor.** The loop never breaks — it always walks to the topmost collapsed ancestor. After root-task-rendering added the root node to the DOM, all badges aggregate onto the root row because it's always collapsed by default. The loop should break as soon as it hits an ancestor whose children are visible, since below that point the child rows are already shown.

Fix in `base.html` `updateTreeCommentBadges()`:
- Check `ancestorChildren.style.display === 'none'` instead of `!ancestorBody.classList.contains('open')`
- `break` when ancestor's children are visible (not hidden)

Files: `skills/task-system/scripts/templates/base.html`

## Results

Changed the walk-up loop in `updateTreeCommentBadges()`. Before: checked body `.open` class and never stopped, so badges always walked to the topmost collapsed ancestor (the root after root-task-rendering). After: checks `children.style.display === 'none'` and breaks on the first ancestor with visible children. Badges now appear on the correct tree level — each top-level task shows its own descendant comment count.
