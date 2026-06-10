---
title: "Add LaTeX math rendering"
status: approved
depends_on: []
tags: []
created: 2026-05-25
---

## Objective

The dashboard renders task body sections with markdown-it, which already handles standard markdown syntax (bold, italic, headers, lists, tables, code blocks). However it does not support LaTeX math (`$...$` inline or `$$...$$` display). Task objectives with formulas render as raw LaTeX text.

**Add KaTeX support:**
- Load KaTeX CSS and JS from CDN in `base.html`
- Add the `markdown-it-texmath` plugin (or `markdown-it-katex`) via CDN to hook KaTeX into the markdown-it pipeline
- Configure the markdown-it instance in the `<script>` block to use the math plugin
- Support both inline `$x^2$` and display `$$\sum_{i=1}^n x_i$$` math
- Ensure KaTeX styles work with both light and dark theme tokens

**Files to modify:**
- `skills/task-tree/scripts/templates/base.html` — add KaTeX CDN links, load math plugin, configure markdown-it instance
- `skills/task-tree/scripts/plan_dashboard.py` — update the static `DASHBOARD_HTML` template with same changes (for `generate` subcommand backward compat)

**Validation:** Serve the dashboard on a `.plan/` tree that has a task with LaTeX math in its objective. Verify inline and display math render correctly in both light and dark modes.

## Results

Added KaTeX math rendering to the dashboard via CDN resources in both `base.html` (live server) and `plan_dashboard.py` (static generate):

- **CDN resources loaded** (after markdown-it, before mermaid):
  - `katex@0.16/dist/katex.min.css` — KaTeX stylesheet
  - `katex@0.16/dist/katex.min.js` — KaTeX rendering engine
  - `markdown-it-texmath@1/texmath.min.js` — markdown-it plugin that hooks KaTeX into the parser

- **Plugin configured**: `md.use(texmath, { engine: katex, delimiters: 'dollars' })` — supports `$...$` (inline) and `$$...$$` (display math)

- **Theme integration**: `.katex { color: var(--text); }` ensures math inherits the dashboard's light/dark text color token. `.katex-display { margin: 0.75em 0; }` gives display math vertical breathing room.

- **Verified**: Restarted the live server on port 8888; page source confirms CDN links, CSS overrides, and plugin initialization are all present and correctly ordered.
