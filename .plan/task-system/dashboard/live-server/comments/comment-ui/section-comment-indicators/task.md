---
title: "Show unresolved comment indicators on section headers"
status: implemented
review_status: implemented
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Add a visual indicator on each ## section header showing the count of unresolved comments in that section. The indicator must be visible even when the section is folded/collapsed, so users can see at a glance which sections have outstanding feedback without expanding them (comment #3).

## Results

Implemented in [base.html](skills/task-system/scripts/templates/base.html):

- Added `.section-comment-badge` CSS class: accent-colored pill badge (16px height, rounded, white text on accent background) positioned at the right end of the section-toggle row via `margin-left: auto`.
- Added `updateSectionBadges(taskPath, comments)` function: counts unresolved comments per section from the fetched comments array, then creates/updates/removes a `.section-comment-badge` span on each section-toggle. The badge shows the count and has a title tooltip ("N unresolved comment(s)").
- `updateSectionBadges` is called at the end of `loadComments` after rendering comment threads, so badges update whenever comments change.
- `loadComments` is now also called when a task node is expanded (in `toggleTask`), so section badges populate immediately on task expand — before any individual section is opened. This ensures the badge is visible on collapsed sections.

