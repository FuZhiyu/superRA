---
title: "Jinja2 templates and htmx frontend"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - ../server
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Create the Jinja2 templates that render the dashboard UI. Port the visual design from the existing static HTML dashboard (typography, palette, dark/light mode) into reusable templates.

**Templates:**
- `base.html` — full page shell: header bar, theme toggle, view switcher, summary bar, CDN script tags (htmx, mermaid, markdown-it), SSE connection setup
- `task_node.html` — single task row fragment: title, status badge, expand/collapse toggle, `hx-get` for lazy children loading, `sse-swap` for live updates. This is the htmx partial returned by `GET /task/{path}`
- `task_detail.html` — expanded task body: collapsible sections (objective, results, decisions, review notes) rendered via markdown-it
- `summary_bar.html` — status counts and progress bar, refreshable via SSE
- `kanban.html` — kanban board view (htmx partial)
- `dag.html` — mermaid DAG view (htmx partial)

**Design:**
- Port existing CSS variables (light/dark tokens, status colors, typography) from `dashboard.html`
- Tree connector lines via `border-left` (existing pattern)
- Progressive disclosure: title row → children + section toggles → rendered markdown
- Search and status filter in the header, using `hx-get` with query params to fetch filtered results
- Breadcrumb showing current view scope (useful when serving a subtree)

**htmx patterns:**
- `hx-get="/task/{path}"` on expand toggle — fetches children fragment
- `hx-target="#{path}-children"` — swaps into the children container
- `hx-swap="innerHTML"` — replace children content
- `hx-ext="sse"` + `sse-connect="/events"` on the main container
- `sse-swap="task:{path}"` on each task node — auto-update on change

**Markdown link resolution:**
- Relative file paths in markdown links (`[text](path/to/file.py:42)`) rewrite to `vscode://file/{absolute_path}:42` URIs — click to open in VSCode at that line
- Heuristic: if href doesn't start with `http://`, `https://`, or `#`, treat as a file path
- Image embeds (`![alt](path/to/fig.png)`) rewrite `src` to `/files/path/to/fig.png`, served by a `StaticFiles` mount on the project root
