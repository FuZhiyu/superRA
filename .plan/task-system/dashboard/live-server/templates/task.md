---
title: "Jinja2 templates and htmx frontend"
status: implemented
review_status: revise
integration_status: ~
depends_on:
  - ../server
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

## Decisions

- Markdown content stored in `<template>` tags inside `rendered-md` divs, rendered client-side by markdown-it on first section expand (lazy rendering).
- Link rewriting implemented in a `renderMarkdown()` JS function: relative paths become `vscode://file/{project_root}/{path}`, relative image srcs become `/files/{src}`.
- DAG and kanban views fetched from server endpoints (`/dag`, `/kanban`) rather than rendered inline, keeping the initial page load lightweight.
- Children at depth >= 2 lazy-loaded via htmx `GET /task/{path}` on first expand; depths 0-1 rendered inline for immediate visibility.
- Search/filter operates client-side by toggling `.hidden` class on `.task-node` elements, with descendant-aware matching

## Review Notes

1. **[MAJOR] SSE event name mismatch -- live task updates will silently fail.** [task_node.html:20](skills/task-system/scripts/templates/task_node.html#L20) declares `sse-swap="task:{{ task.path }}"`, expecting per-task events like `event: task:server`. But the server ([plan_dashboard.py:193](skills/task-system/scripts/plan_dashboard.py#L193)) broadcasts `event: task-updated` with JSON data `{"path": "...", "html": "..."}`. htmx SSE extension matches `sse-swap` values against the SSE `event:` field, so no match ever occurs and individual task live-updates never fire. Additionally, the server sends JSON as the data payload, but `sse-swap` expects raw HTML to swap into the element. Fix: either (a) change the server to broadcast `event: task:<path>` with the HTML fragment as data (one event per changed task), or (b) change the template to use `sse-swap="task-updated"` and add client-side JS to parse the JSON and swap the right node. Option (a) is simpler and consistent with htmx patterns. This is a template/server contract issue -- whichever side changes, the other must match.

2. **[MAJOR] Status filter hides parent nodes that contain matching children.** [base.html:709-710](skills/task-system/scripts/templates/base.html#L709): the `applyFilters()` function checks `el.dataset.status !== status` per-node without descendant awareness. If a user filters by "approved", parent nodes whose `effective_status` is "in-progress" (because not all children are approved) will be hidden, making their approved children inaccessible. The reference dashboard uses `anyDescendantMatches()` which recurses through the data model for both status and search. The Jinja2 version only does descendant-aware matching for search text (lines 718-731), not for the status filter. Fix: add descendant-aware status checking -- if any descendant `.task-node` has a matching `data-status`, the parent should remain visible.

3. **[MINOR] XSS via unescaped `{{ task.title }}` and other frontmatter values.** The Jinja2 environment uses `autoescape=False` ([plan_dashboard.py:218](skills/task-system/scripts/plan_dashboard.py#L218)), so all `{{ }}` expressions output raw HTML. Task titles ([task_node.html:28](skills/task-system/scripts/templates/task_node.html#L28)), depends_on ([task_node.html:107](skills/task-system/scripts/templates/task_node.html#L107)), script, tags, input, output, and kanban card titles ([kanban.html:30](skills/task-system/scripts/templates/kanban.html#L30)) are rendered without escaping. A task title like `<img src=x onerror=alert(1)>` would execute. In this use case the threat model is low (data comes from the user's own `.plan/` files), but it's a correctness issue since well-formed HTML in titles (e.g., `<T>`) would render as HTML rather than display as text. Fix: use `{{ task.title | e }}` (or `| escape`) for non-markdown values. Alternatively, set `autoescape=True` in the Jinja2 environment and use `{% autoescape false %}` blocks or `| safe` only for the markdown `<template>` content.

4. **[MINOR] `</template>` in markdown content breaks lazy rendering.** [task_node.html:60](skills/task-system/scripts/templates/task_node.html#L60): markdown content is placed inside `<template>{{ content }}</template>` without escaping. If task body markdown contains the literal string `</template>` (e.g., in a code sample discussing HTML templates), the browser's HTML parser will close the `<template>` tag prematurely and render the remaining content as DOM. Fix: escape `</template>` occurrences in the content, e.g., via a Jinja2 filter that replaces `</template>` with `<\/template>` or HTML-entity-encodes the content inside the template tag.

5. **[MINOR] DAG `dep.lstrip('./')` strips characters, not prefix.** [dag.html:35](skills/task-system/scripts/templates/dag.html#L35): `dep.lstrip('./')` uses Python's `str.lstrip()` which strips any combination of the characters `.` and `/` from the left, not the prefix `../`. For the common cases (`../sibling` -> `sibling`, `sibling` -> `sibling`) it works correctly. But edge cases like `..../weird` would produce `weird` (stripping four dots), and a dep like `./local` would also be handled. Since the task system constrains `depends_on` to sibling names and the convention is `../sibling` for cross-parent refs, this is functional but fragile. A regex or `removeprefix` would be more robust.

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
