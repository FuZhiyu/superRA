---
title: "Server + template partials for master-detail"
status: approved
depends_on: []
tags: []
created: 2026-05-30
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

## Results

Additive endpoints and a behavior-preserving body-macro refactor are in place; no visible UI change ships. All work is on the live server only — the static `generate`/`DASHBOARD_HTML` path is untouched.

**Body-sharing refactor.** Extracted the task-body block (sections + meta pills) from `render_task_node` into a shared `render_task_body(task, project_root)` macro in [`task_node.html`](../../../../../skills/task-system/scripts/templates/task_node.html). Both the full-node render and the new `/node/{path}` partial call it, so body markup has one source of truth. The old inline `.dag-panel` accordion was dropped (the children-DAG region replaces it in the `main-panel` task). A whitespace-normalized diff of the served `/tree` fragment before vs. after confirms the **only** semantic change is the two `.dag-panel` blocks disappearing — every `data-section` block, `<script type="text/x-markdown">` payload, `task-meta` pill, badge, row, and children container is byte-identical (modulo macro-extraction reindentation). `<div>` balance is preserved (58/58 → 52/52, the 6 removed divs being the two 3-div dag-panels).

**`GET /nav` — body-free sidebar tree.** New `nav_node.html` macro renders the `.task-row` chrome (toggle/slug/title/badge/progress) and the recursive children container, with **no** `.task-body` / sections. Preserves `id="task-<path-id>"`, `data-path`, `data-status`, and `sse-swap="task:<path>"` so SSE row swaps keep working. Inlines to depth 2; depth ≥3 children get the `data-needsLoad='true'` stub. Root-or-children logic mirrors `/tree`. Helper `_render_nav_node`; route in [`plan_dashboard.py`](../../../../../skills/task-system/scripts/plan_dashboard.py).

**`GET /nav/{path}` — nav-scoped lazy children.** New `nav_children.html` fragment (parallels `task_children.html`) renders body-free children of a deep node so the sidebar lazy-loads without pulling bodies. Greedy `{path:path}` route placed after the comment routes; 404 on miss.

**`GET /node/{path}` — active-node body-only partial.** New `node_body.html` calls the shared `render_task_body` macro, emitting only meta pills + `## ` sections (each a `data-section` block with its lazy markdown `<script>` payload), no row, no children. Resolved via `_find_task`, 404 on miss. A regression test confirms the `Objective`/`Results` section blocks it emits are byte-identical (whitespace-normalized) to what the full node emits, so the client's `renderMarkdown`/`loadComments`/comment-form code consumes it unchanged. (Note: `.commentable-block` wrappers are added client-side by `renderMarkdown` in `base.html`; the server emits the `data-section` block + markdown payload, which is the byte-for-byte-identical input the client already consumes.)

**Validation run.** `py_compile` clean. Full suite green at **152 passed** (143 baseline + 9 new in `TestMasterDetailPartials` using FastAPI `TestClient`, guarded by `pytest.importorskip("httpx")`): `/nav` body-free + attribute integrity, depth-≥3 lazy stubs, `/nav/{deep}` body-free children, `/node/{path}` body-only + meta pills + section-markup-equals-full-node, and both 404s. Existing `/`, `/tree`, `/dag`, `/kanban` all still 200.

**Out of scope, flagged for downstream.** `base.html` still carries the now-orphaned `toggleDagPanel` JS handler and `.dag-panel` CSS. They are dead but harmless — `toggleDagPanel` was only reachable via an inline `onclick` on the dag-panel element that is no longer emitted, with no load-time or `querySelectorAll` invocation, so the index page is unaffected at load. Left for the `main-panel` task that reworks `base.html` to introduce the children-DAG region, rather than expanding this task's scope.
