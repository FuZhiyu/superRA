---
title: "Design A — inline per-subtree DAG panels"
status: not-started
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
- Node colors match task status as in the existing `dag.html`. Serve the dashboard (`bash .plan/serve`) and confirm in both light and dark themes.
