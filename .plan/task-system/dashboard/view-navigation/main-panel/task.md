---
title: "Main panel — active-node card + children DAG"
status: not-started
depends_on:
  - server-partials
  - routing-shell
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Fill the main panel: the active node's own content, then its direct children as a clickable DAG. Load `frontend-design:frontend-design` before touching markup or CSS. Live server only; edit `skills/task-system/scripts/templates/base.html`. Build on `routing-shell` (the `#active-node` / `#children-dag` regions and `setActive`) and `server-partials` (the `/node/{path}` route). This task and `sidebar-nav` both edit `base.html`, so they run serially — coordinate edits to shared functions.

**Active-node card — implement `loadActiveNode(path)`** (the stub from `routing-shell`): fetch `GET /node/{path}` into `#active-node`, then render its markdown sections and load comments by reusing the existing pipeline unchanged — `renderMarkdown` ([`base.html:679`](../../../../../skills/task-system/scripts/templates/base.html#L679)), the section render-on-reveal logic from `expandTaskDetails` ([`base.html:1105`](../../../../../skills/task-system/scripts/templates/base.html#L1105)), and `loadComments(path)`. Sections default to **expanded** in the card (this is the focused detail view). Show the task's title + status badge at the top of the panel (the breadcrumb already shows the path).

**Children DAG — implement `loadChildrenDag(path)`** (the stub from `routing-shell`):

- **Leaf** active node → render nothing in `#children-dag` (card only).
- **Children with at least one inter-child dependency** (`Task.has_child_dependency_graph()` is true) → fetch the existing `GET /dag?root={path}` ([`plan_dashboard.py:481`](../../../../../skills/task-system/scripts/plan_dashboard.py#L481)) — which already returns exactly the direct-children sibling graph — run `mermaid.run`, then call the existing `wireDagNodeClicks(container)` ([`base.html:943`](../../../../../skills/task-system/scripts/templates/base.html#L943)). **Change its terminal action from `revealTask(path)` to `setActive(path)`** so clicking a child descends.
- **Children with no inter-dependencies** → render a plain clickable child-card grid (slug + title + status badge per child), each calling `setActive(childPath)` — cheaper and clearer than an edgeless mermaid graph.
- Render the DAG **after** the card paints so the detail is interactive immediately; cache rendered output keyed by `(path, child-status-signature)` and skip re-render when navigating back to an unchanged node.

**Remove the superseded code.** Delete the global DAG tab path `renderDagView()` ([`base.html:917`](../../../../../skills/task-system/scripts/templates/base.html#L917)) and the inline per-node `toggleDagPanel()` accordion ([`base.html` ~975]) — both are replaced by the children-DAG region. Leave `dag.html`, the `node_id↔path` map, and `wireDagNodeClicks` (reused). The `revealTask`→`setActive` alias from `routing-shell` means Kanban cards now open the workspace at the clicked task; confirm that end-to-end here.

## Validation

- Selecting a node (sidebar row, breadcrumb, child node, Kanban card, or deep-link) renders its sections (markdown rendered, comments loaded) in `#active-node` and, below, its direct-children DAG; clicking a child node descends (active = child, hash + breadcrumb + sidebar update).
- A leaf node shows only the card, no DAG region. A parent whose children have no dependencies shows a clickable child-card grid; a parent with inter-child edges shows the mermaid graph, status-colored, in both themes.
- Comment gutters and markdown (links rewritten to `vscode://`, images via `/files/`) work in the card exactly as in the old tree body.
- Navigating back to a previously viewed node does not re-run mermaid (cache hit); a child whose status changed does re-render.
- No references remain to `renderDagView` or `toggleDagPanel`; `node --check` on the main script passes; live-server drive (HTTP + headless browser where available) shows the full drill loop with no console errors. `pytest skills/task-system/scripts/test_task_system.py` still passes.
