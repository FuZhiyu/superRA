---
title: "Master-detail drill-down workspace"
status: approved
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Replace the dashboard's three-tab presentation shell (Tree / global DAG / Kanban) with a single **master-detail drill-down workspace** that makes the task tree navigable by drilling layer by layer instead of expanding one giant scroll. Kanban stays as a separate board. The work is on the live FastAPI/htmx server only (`skills/task-system/scripts/plan_dashboard.py` + `skills/task-system/scripts/templates/`); the static `generate` / `DASHBOARD_HTML` path is legacy and self-contained and stays out of scope.

**The interaction model.** One client variable, `activePath`, is the single source of truth; everything else is a pure function of it. The screen has three regions:

- **Left — a persistent navigation tree (sidebar).** The full hierarchy, collapsible, rows stripped to navigation only (slug + title + status badge + progress + comment badge, no body). Clicking a row sets it active; a disclosure caret folds/unfolds children locally. The active row is highlighted and its ancestors auto-expand and scroll into view.
- **Main panel, top — a breadcrumb.** `root › … › active`; each crumb ascends by setting that ancestor active.
- **Main panel, body — the active node's own content + its children as a DAG.** First the active task's rendered markdown sections (objective/results/etc.), then **a clickable mermaid DAG of that node's direct children** (the sibling dependency graph, status-colored). Clicking a child node descends (active = that child). A leaf node shows just its content, no DAG. This is the key inversion the user asked for: a node's subtasks are presented *as a DAG in the main panel*, not as an expandable tree.

**Deep linking.** The URL hash is the task path verbatim (`#/<task/path>`); any subtree is directly addressable and becomes the "top layer." Browser back/forward and reload restore the active node. Kanban cards and every DAG node ultimately navigate by setting `activePath`, which updates the hash.

**Why this replaces the old design.** Sibling-only dependencies make a dependency graph an inherently per-subtree artifact, so one flat global DAG reads as noise; drilling shows exactly one sibling-scoped graph at a time. And the old "reveal in one giant tree" navigation (`revealTask`) is structurally fragile — it silently fails when any ancestor isn't in the DOM, which is the broken click-jump the user observed. The drill-down model fetches the active node by full path directly, so navigation never depends on the whole tree being materialized.

## Design Principles

Every UI task below loads `frontend-design:frontend-design` and holds to these (the user is authoring their own `frontend-design` skill later; use the available one now and keep the visual/interaction bar high):

- **`activePath` is the only navigation state.** Sidebar highlight, breadcrumb, active-node fetch, and children-DAG are all derived from it. No second source of truth.
- **Clean htmx/router boundary.** htmx owns declarative SSE row swaps (sidebar rows, summary bar); the hand-written hash router owns `activePath`-driven `fetch`es (`/node`, `/dag?root=`). An SSE swap never calls `setActive` (no history writes from the server channel). Guard restores (load, `popstate`) with a `restoring` flag so they use `replaceState`, not `pushState`.
- **Reuse the proven pipelines unchanged:** markdown lazy-render (`renderMarkdown`, `<script type="text/x-markdown">`), the comment subsystem (`/api/task/...`, `.commentable-block` anchors, `loadComments`, `_commentEditPaths` suppression), mermaid wiring (`wireDagNodeClicks` + `data-node-paths`), theme tokens (CSS custom properties, `data-theme`, localStorage), and descendant-aware search. Repoint, don't rewrite.
- **Responsiveness:** sidebar collapses to an overlay drawer on narrow screens (focus trap + backdrop).
- **Accessibility:** sidebar is a `role="tree"` with roving `tabindex`, `↑↓→←/Enter` keys, and `aria-expanded`/`aria-selected`; honor `prefers-reduced-motion`.
- **Mermaid cost control:** the children-DAG is direct-children only (already small); render it after the card paints, and cache rendered SVG keyed by `(activePath, child-status-signature)` so navigating back is a no-op. Render the no-inter-dependency case as a plain clickable child-card grid (no mermaid) — `Task.has_child_dependency_graph()` distinguishes the cases.

## User Decisions (2026-05-30)

- **Replace, not add.** The drill-down workspace replaces the Tree tab and the global DAG tab; Kanban is kept as a board that jumps into the workspace. View buttons collapse to **Workspace** / **Kanban**; the **DAG** button is removed.
- **Children-as-DAG in the main panel.** A node's subtasks are shown via the per-subtree DAG in the main panel (user: "just put the DAG of the current subtasks there").
- **frontend-design skill.** The user will refine their own `frontend-design` skill later; the available `frontend-design:frontend-design` plugin skill is used in the meantime.

## Decomposition

A serial pipeline — **not parallel.** Every task heavily edits the same `base.html` (~1950 lines) and/or `plan_dashboard.py`, so concurrent worktrees would conflict; dispatch one at a time in dependency order.

- `server-partials` — add `GET /nav` (navigation-only tree partial) and `GET /node/{path}` (active-node body-only partial); refactor `task_node.html` so the body block is a shared macro. Foundation. Deps: none.
- `routing-shell` — the three-region layout shell, the `activePath` hash router (`parseHash`/`setActive`/`hashchange`/`popstate`/`restoring` guard), the breadcrumb, the Workspace/Kanban toggle (DAG button removed), and `revealTask`→`setActive` alias. Region loaders are stubs. Deps: `server-partials`.
- `sidebar-nav` — render `#nav-tree` from `/nav`; row-click→`setActive`, caret→local fold, active highlight + ancestor auto-expand + scroll, deep-link ancestor-walk lazy-load, sidebar search. Deps: `server-partials`, `routing-shell`.
- `main-panel` — active-node card (`/node/{path}` + reused markdown/comments) and children-DAG (`/dag?root=` + `wireDagNodeClicks`→`setActive`; leaf→omit; no-dep→card grid); remove the old global `renderDagView` and inline `toggleDagPanel`. Deps: `server-partials`, `routing-shell`.
- `sse-simplify` — replace `captureNodeState`/`restoreNodeState`/`_pendingSwapState` with the single-active-node SSE model. Deps: `sidebar-nav`, `main-panel`.
- `a11y-responsive` — keyboard nav, responsive drawer, focus management, reduced-motion. Deps: `sidebar-nav`, `main-panel`.

## Revision Notes

**2026-05-30 — substantive pivot.** The original decomposition (`navigate-to-task`, `dag-global-tab`, `dag-inline-panels`) was implemented, reviewed, approved, and shown to the user on the live server. The user found (a) the click-jump broken — it lands on a folded top-level view — and (b) the global DAG too messy, and asked for nested drill-down with a master-detail UI (sidebar nav-tree + main panel showing a node's content and its children as a DAG, breadcrumb, deep links). Those three tasks were removed and replaced by the six above. Some of their committed code is **reused, not reverted**: the subtree-clustered, HTML-escaped `dag.html` and its collision-safe `node_id↔path` map, `wireDagNodeClicks`, and the `GET /dag?root=<path>` direct-children route all feed the new children-DAG region. The replaced pieces are `revealTask`'s giant-tree expansion (becomes a thin alias to `setActive`), the global `renderDagView` tab, and the inline `toggleDagPanel` per-node accordion.
