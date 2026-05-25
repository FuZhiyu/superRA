---
title: "Fix gutter button clipping from overflow:hidden"
status: implemented
review_status: approved
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

The `+` gutter button on commentable blocks is clipped (only partially visible). Root cause: `.section-content` uses `overflow: hidden` for its max-height expand/collapse animation. `.commentable-block` uses `margin-left: -28px` to create space for the absolutely-positioned gutter button at `left: 0`, but this negative margin extends outside the `.section-content` overflow boundary, clipping the button.

Fix: Remove the negative-margin approach entirely. Instead, use padding-only positioning within `.commentable-block` so the gutter button sits inside the content flow, within the overflow boundary. The `.section-content` already has `padding-left: 20px` — increase it to accommodate the button, or keep the button inside `.commentable-block`'s own padding without any negative margin.

File: `skills/task-system/scripts/templates/base.html` — CSS lines 496-506 (`.commentable-block` and `.comment-gutter-btn` rules).

## Results

Removed the negative-margin approach entirely. Three CSS changes in [`base.html`](skills/task-system/scripts/templates/base.html):

1. **`.section-content`** ([line 344](skills/task-system/scripts/templates/base.html#L344)): `padding-left: 20px` -> `4px`. Reduced because the commentable-block now provides its own indent via padding instead of relying on section-content padding minus negative margin.

2. **`.commentable-block`** ([line 497](skills/task-system/scripts/templates/base.html#L497)): removed `margin-left: -28px`, changed `padding-left: 28px` -> `24px`. The 24px padding area holds the 20px gutter button with 2px gap on each side. No content extends outside the `.section-content` overflow boundary.

3. **`.comment-gutter-btn`** ([line 500](skills/task-system/scripts/templates/base.html#L500)): `left: 0` -> `2px`. Centers the 20px button within the 24px padding area.

**Layout math:** Net text indent is `4px (section-content) + 24px (commentable-block) = 28px`, compared to the original `20px (section) - 28px (margin) + 28px (padding) = 20px`. An 8px increase — barely noticeable. The gutter button sits at `4px + 2px = 6px` from the section-content border edge, fully inside the padding box and visible under `overflow: hidden`.

All 53 existing dashboard tests pass.
