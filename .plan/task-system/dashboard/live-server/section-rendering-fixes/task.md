---
title: "Fix section order and HTML-escaping in task body rendering"
status: approved
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Two bugs in `task_node.html` section rendering:

**1. HTML entity escaping breaks LaTeX.** Content inside `<template>` tags is Jinja2 auto-escaped, turning `>` into `&gt;`, `<` into `&lt;`, etc. When markdown-it + KaTeX processes this text client-side, it sees literal `&gt;` instead of `>`, breaking math like `$x > 0$`. Fix: mark the template content as safe (`| safe` filter) since it goes into a `<template>` element that is never rendered directly by the browser — the JS `renderMarkdown()` function reads `tmpl.innerHTML` and processes it.

**2. Sections render in hardcoded order, not document order.** Lines 46-51 of `task_node.html` define a fixed list: Objective, Results, Decisions, Review Notes. Extra sections from the body follow after. The actual order in the task.md file is ignored. Fix: parse sections from `task.body` in order (like the 'extra sections' logic on lines 72-88 already does), but include ALL sections (not just unknown ones). Remove the hardcoded `sections` list and the separate 'known' vs 'extra' rendering — just iterate through sections as they appear in the markdown.

**Files to modify:**
- `skills/task-system/scripts/templates/task_node.html` — rewrite section rendering to be order-preserving and use `| safe` on template content.

**Validation:** 
- Check a task.md with LaTeX `$x > 0$` renders correctly (no `&gt;`).
- Check a task.md where Results comes after other sections renders in the correct document order.

## Results

Rewrote [`task_node.html`](skills/task-system/scripts/templates/task_node.html) section rendering:

1. **Unified section parser.** Replaced the two-pass approach (hardcoded known sections list on lines 46-51, then separate "extra sections" parser on lines 72-88) with a single pass that walks `task.body` line-by-line and collects ALL `## ` sections in document order. Sections now render in the order they appear in the task.md file.

2. **Added `| safe` filter.** Template content output now uses `{{ content | replace('</template>', '&lt;/template&gt;') | safe }}`. While `autoescape=False` is currently set in `plan_dashboard.py` (making `| safe` a no-op today), this future-proofs against autoescape being enabled and documents intent — template content is read by JS `renderMarkdown()`, never rendered directly by the browser.

**Verification (inline test):**
- Task with `$x > 0$` in Results: template content contains literal `>`, not `&gt;`.
- Task with non-standard section order (Results, Objective, Decisions, Custom): rendered HTML preserves that exact order.
- All 57 dashboard tests and 113 task system tests pass.
