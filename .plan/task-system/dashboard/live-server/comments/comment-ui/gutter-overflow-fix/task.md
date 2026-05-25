---
title: "Fix gutter button clipping from overflow:hidden"
status: not-started
review_status: ~
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

