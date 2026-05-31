---
title: "Server + template partials for master-detail"
status: not-started
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Add the two server endpoints and the template refactor the drill-down workspace needs, without changing any existing client behavior yet. This is the foundation the client tasks build on. Load `frontend-design:frontend-design` before touching markup. Work on the live server only (`skills/task-system/scripts/plan_dashboard.py` + `skills/task-system/scripts/templates/`); leave the static `generate`/`DASHBOARD_HTML` path untouched.

**1. `GET /nav` — navigation-only tree partial.** A variant of the tree that renders rows but **no task body / no sections** — just the `.task-row` (toggle caret, slug, title, status badge, progress, comment badge) plus the recursive children container. Mirror the existing index render structure in [`plan_dashboard.py:408`](../../../../../skills/task-system/scripts/plan_dashboard.py#L408) and the depth handling in [`task_node.html:116`](../../../../../skills/task-system/scripts/templates/task_node.html#L116): inline to depth 2, mark depth ≥3 children with `data-needsLoad='true'` for lazy load. Preserve the per-node attributes the rest of the system keys off: `id="task-<path-id>"`, `data-path`, `data-status`, and `sse-swap="task:<path>"` (so SSE row swaps keep working). Add a new template `nav_node.html` (the nav-only macro) and a nav-variant of the lazy-children fragment paralleling [`task_children.html`](../../../../../skills/task-system/scripts/templates/task_children.html); the existing `/task/{path}` lazy route renders the *full* node, so add a nav-scoped lazy route (e.g. `GET /nav/{path}`) or a query flag so deep sidebar children load body-free.

**2. `GET /node/{path}` — active-node body-only partial.** Renders **only** the body half of a single task: metadata pills + the `## ` markdown sections, each as the existing `data-section` block with its lazy `<script type="text/x-markdown">` payload and `.commentable-block` structure — i.e. exactly what [`task_node.html:40`](../../../../../skills/task-system/scripts/templates/task_node.html#L40) emits for the body, for one task, with no row and no children. Resolve the task with the existing `_find_task(path)` ([`plan_dashboard.py`](../../../../../skills/task-system/scripts/plan_dashboard.py)) and 404 on miss. Because the section markup, `data-section`/`data-block` attributes, and markdown payloads are byte-for-byte the same as today, the client's `renderMarkdown`, `loadComments`, and comment-form code will consume it unchanged.

**3. Refactor `task_node.html` to share the body.** Extract the body block (sections + meta pills; **drop** the old inline `.dag-panel` accordion at [`task_node.html:78`](../../../../../skills/task-system/scripts/templates/task_node.html#L78) — the children-DAG region replaces it in the `main-panel` task) into a shared Jinja macro that both `/node/{path}` and the existing full-node render call, so there is one source of truth for body markup. The existing index/tree render must remain byte-equivalent through this refactor (verify by diffing rendered output before/after).

This task ships no visible UI change — the new routes are additive and the refactor is behavior-preserving. The client tasks wire them in.

## Validation

- `GET /nav` returns rows for the whole tree, no `.task-body`/`.section-content` elements, with `data-path` / `id="task-..."` / `sse-swap` intact; depth ≥3 children are lazy-load stubs.
- `GET /nav/<deep/path>` (or the chosen lazy route) returns body-free children for a deep node.
- `GET /node/<path>` returns only that task's body (sections + meta), with `data-section`/`data-block` and the markdown `<script>` payloads identical to what the full node emits; `GET /node/<missing>` → 404.
- The refactor leaves the index page render unchanged — diff the served `/` HTML (or the full-node fragment) before vs. after and confirm only the intended removal (inline dag-panel) differs.
- `py_compile` clean; existing `pytest skills/task-system/scripts/test_task_system.py` still passes (143). Add a lightweight check (FastAPI `TestClient` if it fits the suite, else a live-server HTTP smoke) for `/nav` and `/node/{path}` shape + the 404.
- Serve the dashboard (`python skills/task-system/scripts/plan_dashboard.py serve --root .plan`) and confirm the existing Tree/DAG/Kanban tabs still render (nothing wired to the new routes yet).
