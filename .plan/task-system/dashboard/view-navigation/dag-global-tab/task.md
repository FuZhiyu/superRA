---
title: "Design B — clickable, subtree-clustered global DAG tab"
status: implemented
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
- Node-id↔path mapping is unique (no two tasks collapse to the same node). Serve the dashboard (`python skills/task-system/scripts/plan_dashboard.py serve --root .plan`) and confirm in both light and dark themes.

## Results

Rewrote the global DAG tab in [dag.html](../../../../../skills/task-system/scripts/templates/dag.html) to cluster by subtree and wired clickable nodes through the `navigate-to-task` `revealTask(path)` primitive via new JS in [base.html](../../../../../skills/task-system/scripts/templates/base.html). The `/dag` route and the `collect_all_tasks` data it passes were left unchanged — all the work is in the two templates.

### Cluster by subtree
The flat `graph LR` over every task is replaced with one Mermaid `subgraph` per parent path. Tasks are grouped by their parent (`'/'.join(path.split('/')[:-1])`), each cluster labeled with the parent task's title (root-level tasks fall under a `root` cluster). Status coloring is preserved per node; cross-cluster dependency edges still draw. At the current 99-task / 16-group tree the view is legible as labeled bordered clusters instead of one blob ([dag.html:78-104](../../../../../skills/task-system/scripts/templates/dag.html#L78)).

### Clickable nodes + unique node-id↔path mapping
Click wiring is done in JS **after** Mermaid renders (`wireDagNodeClicks(container)` called from `renderDagView`), not via Mermaid's `click ... call` directive — that directive needs `securityLevel: 'loose'`, a global Mermaid-config change this task should not make. The template emits an authoritative `node_id → task path` map as a `data-node-paths` attribute on `.dag-controls` (`| tojson`); after render, each `g.node` SVG id (`mermaid-<runId>-flowchart-<nodeId>-<n>`) is parsed back to its `node_id`, looked up in the map, and given a click handler that calls `revealTask(path)` ([base.html:933-961](../../../../../skills/task-system/scripts/templates/base.html#L933)).

The historical slug (`/` and `-` → `_`) is lossy in principle (`a-b/c` and `a/b-c` both collapse to `a_b_c`). I made node-id generation collision-safe: the first path to claim a slug keeps it, later collisions get a `__N` suffix, and the `node_id → path` map is the single source of truth for clicks — so even on a collision the click still resolves to the correct task. The current tree has no collisions (verified: 99 node ids ↔ 99 unique paths, every diagram node present in the map).

### Two render-correctness fixes the rewrite required
- **Label HTML-escaping (`| e`).** Node/subgraph labels are now HTML-escaped. One task title contains literal `<template>` / `<script ...>` text; without escaping, setting the partial via `innerHTML` made the browser parse those as real tags, corrupting the `.mermaid` element's `textContent` and bleeding `</div>` into the Mermaid source — a fatal parse error. Escaping keeps the browser from mis-parsing while Mermaid (which reads decoded `textContent`) still sees the literal label. This latent bug also existed in the old flat template.
- **Edge guard.** Dependency edges are only emitted when the resolved target is in the node-id map, so a stale/unresolvable `depends_on` can't emit a dangling Mermaid edge.

A `.dag-hint` caption and a `.dag-node-clickable` hover affordance (theme-aware via `--accent`) were added to `base.html`'s CSS.

### Verification
Served on a throwaway port and driven with Playwright (headless Chromium) against the live tree:
- DAG view renders **99 nodes in 16 clusters**, zero console/page errors, in both light and dark themes (Mermaid `neutral` theme stays light-background but legible against the dark page chrome — the global Mermaid theme init is shared config outside this task's scope).
- Clicking a deeply nested node (`task-system/dashboard/view-navigation/dag-global-tab`) switches to the tree view, opens the target body, and renders all its sections (`2/2`); clicking a root-level node (`dynamic-workflows`) opens its body. Both via the real wired handler.
- All **99 nodes** got click handlers; node-id↔path map round-trips uniquely (99/99).
- `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py` — **143 passed**.

The `## Validation` serve command is correct (`python skills/task-system/scripts/plan_dashboard.py serve --root .plan`); flags are `--root` / `--port` / `--no-open`.
