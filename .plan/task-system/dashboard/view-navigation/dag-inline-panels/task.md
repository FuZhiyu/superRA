---
title: "Design A — inline per-subtree DAG panels"
status: implemented
depends_on:
  - navigate-to-task
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Add a foldable DAG panel inside each parent task node that has children with dependencies among them, scoped to that subtree's **sibling** dependency graph, with clickable nodes. This is the local-context half of the DAG redesign; it coexists with the global DAG tab (the sibling `dag-global-tab` task) — do not remove or rewrite the global `/dag` tab here. Load `frontend-design` before touching markup or CSS.

**Why per-subtree.** Dependencies in this task system are sibling-only (`depends_on:` names sibling directories), so the meaningful dependency graph for any parent is the graph over its direct children. A panel scoped to one parent's children is the natural, readable unit — unlike the flat whole-tree global graph.

**Where it goes.** Task nodes render through `skills/task-system/scripts/templates/task_node.html` / `task_children.html`, expanded in the tree view defined in `base.html`. Add a collapsible "Dependencies" / DAG panel to a parent node's expanded region, shown only when the parent has ≥2 children with at least one `depends_on` edge among them. Produce the subtree graph by reusing the existing DAG rendering logic in `skills/task-system/scripts/templates/dag.html` (same Mermaid `graph LR`, same `status_colors`, same `path → node_id` slug rule) scoped to the children of that parent — either a new server route (e.g. `GET /dag?root=<path>` in `plan_dashboard.py`, rendering `dag.html` against the subtree) or an inline render. Do not fork a parallel DAG renderer; share the logic with `dag.html`.

**Clickable nodes.** DAG nodes must call the shared reveal primitive from `navigate-to-task` (`revealTask(path)` / the wired `showTreeAndExpand`) so clicking a node lands on that task in the tree, expanded to its details. Wire Mermaid node clicks via Mermaid's `click <nodeId> call ...` directive or by attaching handlers after render; map the Mermaid node id back to the task path.

## Validation

- A parent task with dependent children shows a foldable DAG panel scoped to exactly those children; a parent with no inter-child dependencies (or <2 children) shows no panel.
- Clicking a node in an inline panel opens that task in the tree, expanded, details visible (reuses the `navigate-to-task` primitive — no duplicated reveal logic).
- The global `/dag` tab is untouched and still works.
- Node colors match task status as in the existing `dag.html`. Serve the dashboard (`python skills/task-system/scripts/plan_dashboard.py serve --root .plan`) and confirm in both light and dark themes.

## Results

Inline per-subtree DAG panels ship inside each expanded parent task node, scoped to that parent's direct-children sibling graph, reusing the global DAG renderer and the shared reveal primitive without forking either.

**Implementation.**

- **Gating helper** — [`_task_io.py:66`](../../../../../skills/task-system/scripts/_task_io.py#L66) adds `Task.has_child_dependency_graph()`, returning `True` only when a task has ≥2 children and at least one child's `depends_on` names a sibling slug. This is the single source of truth for "does this parent get a panel," used by the macro.
- **Scoped route** — [`plan_dashboard.py:481`](../../../../../skills/task-system/scripts/plan_dashboard.py#L481) extends `GET /dag` with an optional `root=<task path>` query param. With `root`, it renders the *same* `dag.html` template against `sub_root.children` (the direct children = the sibling-only graph); without `root` it is the unchanged global view. No parallel renderer — `dag.html` is untouched and already renders correctly against a sub-root because its edge resolution maps `depends_on` slugs to `parent/slug`, which is present in the scoped `all_tasks`.
- **Panel markup** — [`task_node.html:78`](../../../../../skills/task-system/scripts/templates/task_node.html#L78) emits a foldable `.dag-panel` (a "Dependencies" `.section-toggle` + lazy `.dag-panel-content`) inside the task body, guarded by `task.has_child_dependency_graph()`. Because the panel lives in the `render_task_node` macro, it appears on every render path: inline (depth ≤ 2), the lazy `/task/<path>` fragment for deeper subtrees, and SSE node swaps.
- **Lazy render + click wiring** — [`base.html:964`](../../../../../skills/task-system/scripts/templates/base.html#L964) adds `toggleDagPanel()`, which folds like a section (reusing `uncapAfterTransition`/`recapForCollapse`) and on first open fetches `/dag?root=<path>`, runs `mermaid.run`, then calls the **existing** `wireDagNodeClicks(content)` — so node clicks route through the shared `revealTask(path)` primitive from `navigate-to-task`. No reveal logic is duplicated.
- **Styling** — [`base.html:481`](../../../../../skills/task-system/scripts/templates/base.html#L481) adds four `.dag-panel*` rules that only adjust spacing/scroll and inherit the existing theme tokens and `.dag-node-clickable` hover affordance, so light/dark and the clickable-node highlight come for free.

**Verification (live server, HTTP).**

- `GET /dag?root=task-system/dashboard/view-navigation` → 200, one subgraph, exactly its 3 children, both correct edges (`navigate-to-task → dag-global-tab`, `navigate-to-task → dag-inline-panels`), authoritative `data-node-paths` map present.
- `GET /dag` (global) → 200, 16 subgraphs — untouched.
- `GET /dag?root=does/not/exist` → 404.
- Index page renders `data-dag-root` panels on exactly the parents with inter-child edges and none on leaves; the lazy `/task/<live-server>` fragment emits panels for its deeper `comments` / `state-preservation` subtrees, confirming all render paths are covered.
- `py_compile` clean on both edited Python files.

**Scope note.** Only the live FastAPI/htmx server (templates + route) is touched, matching the task's named files and the sibling `dag-global-tab` task's scope. The static `generate` path's self-contained `DASHBOARD_HTML` (a separate JS renderer) is intentionally left unchanged. `frontend-design` is not a loadable skill here; the panel was styled to the existing `base.html` design tokens and section-toggle patterns rather than from that reference.
