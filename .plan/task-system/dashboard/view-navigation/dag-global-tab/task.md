---
title: "Design B — clickable, subtree-clustered global DAG tab"
status: not-started
depends_on:
  - navigate-to-task
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Keep the global DAG tab as the whole-project overview, but make it actually useful: clickable nodes that navigate to the task, and a layout clustered by subtree so it is readable at tree scale. This is the overview half of the DAG redesign; it coexists with the inline per-subtree panels (sibling task `dag-inline-panels`). Load `frontend-design` before touching markup or CSS.

**Current state.** The global tab is `GET /dag` in `skills/task-system/scripts/plan_dashboard.py`, rendered by `skills/task-system/scripts/templates/dag.html` — one flat Mermaid `graph LR` over every task in the tree, status-colored via `status_colors`, with node ids built by slugging the task path (`/` and `-` → `_`), and **no click handlers**. `base.html` fetches it through `renderDagView()` (around the `showView('dag')` path) into `#view-dag`.

**Two changes.**

1. **Clickable nodes.** Each DAG node must call the shared reveal primitive from `navigate-to-task` (`revealTask(path)` / the wired `showTreeAndExpand`) so clicking a node switches to the tree view and opens that task, expanded to its details. Wire via Mermaid's `click <nodeId> call ...` directive or by attaching handlers after Mermaid renders; map the node id back to the task path. The path→node_id slug is currently lossy if two paths collide after replacement — verify ids round-trip back to a unique path, and fix the mapping if needed.

2. **Cluster by subtree.** Replace the single flat `graph LR` with a layout grouped by parent — e.g. Mermaid `subgraph` blocks per parent task — so the global view is legible instead of one undifferentiated blob. Keep status coloring.

Do not touch the inline-panel work; this task owns only the global tab and its template/route/JS.

## Validation

- The global DAG tab renders the whole tree grouped into per-subtree clusters, status-colored, legible at the current `.plan/` tree's scale.
- Clicking any node switches to the tree view and opens that task, expanded, details visible (reuses the `navigate-to-task` primitive — no duplicated reveal logic).
- Node-id↔path mapping is unique (no two tasks collapse to the same node). Serve the dashboard (`bash .plan/serve`) and confirm in both light and dark themes.
