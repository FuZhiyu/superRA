---
title: "Fix section order and HTML-escaping in task body rendering"
status: not-started
review_status: ~
integration_status: ~
depends_on:  []
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

