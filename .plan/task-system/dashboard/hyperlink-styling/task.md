---
title: "Restyle dashboard hyperlinks"
status: not-started
depends_on:  []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Hyperlinks in the generated dashboard render as classic browser blue (and purple when visited), which clashes with the dashboard's warm accent palette and overall design. Restyle them to fit the dashboard's visual language.

Load `frontend-design` before touching markup or CSS. Locate where the blue links actually come from — the dashboard renders task markdown via markdown-it, so the offending anchors are most likely in the rendered-markdown content and any served/exported views that don't inherit a themed `a` rule. Find the real source rather than assuming; check both `skills/task-system/scripts/templates/base.html` and the live-server / serve path.

Style links to use the existing accent tokens (`--accent` / `--accent-hover`) with a tasteful hover and an on-theme visited state — no raw `#0000EE` default blue or default purple — and keep them legible in both light and dark themes (the dashboard has a `[data-theme="dark"]` block). Underline treatment should match the dashboard's restrained aesthetic.

Validation: links across the tree/task views render in the dashboard's accent style in both themes, with distinct normal/hover/visited states and no default-blue anywhere; regenerate or serve the dashboard to confirm.

## Results

