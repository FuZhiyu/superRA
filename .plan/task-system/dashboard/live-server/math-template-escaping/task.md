---
title: "Fix math rendering: replace <template> with <script type=text/x-markdown> to prevent HTML entity escaping"
status: implemented
review_status: approved
integration_status: ~
depends_on:
  - section-rendering-fixes
  - math-rendering
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Math expressions containing `>` (e.g. `$P_t>0$`, `$\rho>0$`) render as literal `&gt;` in KaTeX output. The earlier section-rendering-fixes task diagnosed this as a Jinja autoescaping issue and added `| safe`, but `autoescape=False` was already set — `| safe` is a no-op.

The real cause is the `<template>` → `innerHTML` round-trip. The HTML serialization algorithm (WHATWG spec §13.3) escapes `>` to `&gt;` in text node serialization. So:
1. Jinja renders `<template>$P_t>0$</template>` — literal `>` in the HTML source (correct)
2. Browser parses the HTML — `<template>` document fragment stores text with `>`
3. JS reads `tmpl.innerHTML` — browser serializes the fragment, converting `>` to `&gt;`
4. `renderMarkdown("$P_t&gt;0$")` → KaTeX renders literal `&gt;` instead of `>`

Fix: replace `<template>` with `<script type="text/x-markdown">`. Script elements store raw text that the browser never parses as HTML. `.textContent` returns verbatim content — no entity escaping.

Changes:
- `task_node.html`: `<template>{{ content | ... }}</template>` → `<script type="text/x-markdown">{{ content | replace('</script>', '<\\/script>') }}</script>`
- `base.html` (two sites): `querySelector('template')` + `.innerHTML` → `querySelector('script[type="text/x-markdown"]')` + `.textContent`

## Results

Replaced all 57 `<template>` tags with `<script type="text/x-markdown">` in the rendered dashboard. Both JS read sites (`toggleSection` lazy-render and `htmx:afterSwap` handler) updated to use `.textContent`. Verified: `$P_t>0$` in the root task's model inventory table now contains literal `>` in the script content, not `&gt;`.
