---
title: "Jinja2 templates and htmx frontend"
status: approved
depends_on:
  - server
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Results

Created 6 Jinja2 templates under [`skills/task-system/scripts/templates/`](skills/task-system/scripts/templates/):

1. **`base.html`** (25KB) -- Full page shell with all CSS ported from the static dashboard (97 selectors, light/dark themes), plus 11 comment-related CSS rules. Includes CDN script tags (htmx 2.x, htmx SSE extension, markdown-it 14, mermaid 11), Google Fonts (Source Serif 4, IBM Plex Mono), sticky header bar with summary stats and controls, SSE connection via `hx-ext="sse"` on the main content div, and all JavaScript for theme toggle, view switching, search/filter, markdown rendering with link rewriting, task expand/collapse, section expand/collapse with lazy markdown rendering, and kanban card navigation.

2. **`task_node.html`** -- Jinja2 macro `render_task_node(task, project_root, depth=0)`. Renders task row (toggle, slug, title, status badge), collapsible body with section toggles (Objective, Results, Decisions, Review Notes, plus any extra `##` sections), metadata pills (depends_on, script, tags, input, output), and children container. Inline children rendered for depth < 2; deeper children lazy-loaded via htmx. Each node has `sse-swap="task:{path}"` for live updates. Raw markdown stored in `<template>` tags, rendered client-side by markdown-it on first section expand.

3. **`task_children.html`** -- Partial fragment returned by `GET /task/{path}`. Imports and uses the `render_task_node` macro at depth=2 (triggering lazy-load for further nesting).

4. **`summary_bar.html`** -- Stats fragment showing leaf count, group count, approved ratio, progress bar, and last updated date. Swapped via SSE `summary-updated` events.

5. **`kanban.html`** -- Kanban board with 5 status columns (Not Started, In Progress, Implemented, Revise, Approved). Shows only leaf tasks, filtered by `effective_status()`. Cards clickable to navigate to tree view.

6. **`dag.html`** -- Mermaid DAG diagram generated from task dependencies with status-colored nodes.

**Verification:** All 6 templates parse as valid Jinja2 and render successfully with mock Task objects. CSS cross-check confirms 0 missing selectors from the original dashboard.

## Revision Notes

**Lazy-load broken for depth >= 3 (htmx v2 script execution).** The recursive lazy-load mechanism for deeply nested tasks is broken. `task_node.html` (lines 138-146) injects an inline `<script>` tag to set `node.dataset.needsLoad = 'true'` on nodes at depth >= 2, enabling their children to be fetched via `htmx.ajax('GET', '/task/' + path)` on first expand. However, htmx v2 does **not** execute `<script>` tags in swapped content by default (security change from v1). When a parent node is lazy-loaded (e.g., expanding `comments` fetches `/task/comments` and injects its children including `comment-ui` via `innerHTML` swap), the `<script>` in the injected `comment-ui` node never executes. Result: `needsLoad` is never set, so clicking `comment-ui` expands its body but never triggers the fetch for its own children — the 4 subtasks are invisible. This affects any task at depth >= 3 in the tree (e.g., `task-system > dashboard > live-server > comments > comment-ui > [children]`). Depths 0-1 are unaffected (inline-rendered). Depth 2 works because the initial page template renders the `<script>` server-side (not via htmx swap). Fix options: (a) set `htmx.config.allowScriptTags = true`, (b) replace the `<script>` approach with an `htmx:afterSwap` event listener that scans injected nodes for `[data-needs-load]` attributes, or (c) move the `needsLoad` flag to a `data-` attribute on the HTML element itself (no script needed) and scan after swap.

## Decisions

- Markdown content stored in `<template>` tags inside `rendered-md` divs, rendered client-side by markdown-it on first section expand (lazy rendering).
- Link rewriting implemented in a `renderMarkdown()` JS function: relative paths become `vscode://file/{project_root}/{path}`, relative image srcs become `/files/{src}`.
- DAG and kanban views fetched from server endpoints (`/dag`, `/kanban`) rather than rendered inline, keeping the initial page load lightweight.
- Children at depth >= 2 lazy-loaded via htmx `GET /task/{path}` on first expand; depths 0-1 rendered inline for immediate visibility.
- Search/filter operates client-side by toggling `.hidden` class on `.task-node` elements, with descendant-aware matching

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
