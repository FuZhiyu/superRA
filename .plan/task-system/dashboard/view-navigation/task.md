---
title: "Master-detail drill-down workspace"
status: approved
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-31
---

**Sync impact:** Cluster `revnote-stale-cleanup` removed this task's stale `## Revision Notes` section (the merged-in `validate_revision_notes` rule flags revision notes on `approved` tasks); cluster `task-io-additive` notes that `Task.has_child_dependency_graph()` is now dead code after this task's mermaid removal. Source: root task.md `## Sync Map`.

## Objective

Replace the dashboard's three-tab presentation shell (Tree / global DAG / Kanban) with a single **master-detail drill-down workspace** that makes the task tree navigable by drilling layer by layer instead of expanding one giant scroll. Kanban stays as a separate board. The work is on the live FastAPI/htmx server only (`skills/task-system/scripts/plan_dashboard.py` + `skills/task-system/scripts/templates/`); the static `generate` / `DASHBOARD_HTML` path is legacy and self-contained and stays out of scope.

**The interaction model.** One client variable, `activePath`, is the single source of truth; everything else is a pure function of it. The screen has three regions:

- **Left — a persistent navigation tree (sidebar).** The full hierarchy, collapsible, rows stripped to navigation only (slug + title + status badge + progress + comment badge, no body). Clicking a row sets it active; a disclosure caret folds/unfolds children locally. The active row is highlighted and its ancestors auto-expand and scroll into view.
- **Main panel, top — a breadcrumb.** `root › … › active`; each crumb ascends by setting that ancestor active.
- **Main panel, body — the active node's own content + its direct children as clickable cards.** First the active task's rendered markdown sections (objective/results/etc.), then **the node's direct children rendered as status-colored `.child-card`s** — a flat grid when no child depends on a sibling, and a layered topological card flow with per-card `↳ after:` footers when there are inter-child dependencies. Clicking a child card descends (active = that child). A leaf node shows just its content, no children panel. This is the key inversion the user asked for: a node's subtasks are presented *in the main panel*, not as an expandable tree.

**Deep linking.** The URL hash is the task path verbatim (`#/<task/path>`); any subtree is directly addressable and becomes the "top layer." Browser back/forward and reload restore the active node. Kanban cards and every child card ultimately navigate by setting `activePath`, which updates the hash.

**Why this replaces the old design.** Sibling-only dependencies make a dependency graph an inherently per-subtree artifact, so one flat global DAG reads as noise; drilling shows exactly one sibling-scoped graph at a time. And the old "reveal in one giant tree" navigation (`revealTask`) is structurally fragile — it silently fails when any ancestor isn't in the DOM, which is the broken click-jump the user observed. The drill-down model fetches the active node by full path directly, so navigation never depends on the whole tree being materialized.

## Design Principles

Every UI task below loads `frontend-design:frontend-design` and holds to these (the user is authoring their own `frontend-design` skill later; use the available one now and keep the visual/interaction bar high):

- **`activePath` is the only navigation state.** Sidebar highlight, breadcrumb, active-node fetch, and children panel are all derived from it. No second source of truth.
- **Clean htmx/router boundary.** htmx owns declarative SSE row swaps (sidebar rows, summary bar); the hand-written hash router owns `activePath`-driven `fetch`es (`/node`, `/dag?root=`). An SSE swap never calls `setActive` (no history writes from the server channel). Guard restores (load, `popstate`) with a `restoring` flag so they use `replaceState`, not `pushState`.
- **Reuse the proven pipelines unchanged:** markdown lazy-render (`renderMarkdown`, `<script type="text/x-markdown">`), the comment subsystem (`/api/task/...`, `.commentable-block` anchors, `loadComments`, `_commentEditPaths` suppression), the `/dag?root=` fragment as the children data source (`data-node-paths` for the child set, parsed client-side by `parseChildrenDag` into cards — no mermaid), theme tokens (CSS custom properties, `data-theme`, localStorage), and descendant-aware search. Repoint, don't rewrite.
- **Responsiveness:** sidebar collapses to an overlay drawer on narrow screens (focus trap + backdrop).
- **Accessibility:** sidebar is a `role="tree"` with roving `tabindex`, `↑↓→←/Enter` keys, and `aria-expanded`/`aria-selected`; honor `prefers-reduced-motion`.
- **Children-panel cost control:** the panel is direct-children only (already small) and built client-side from the `/dag?root=` fragment — no mermaid, no SVG render. Cache the built HTML keyed by `(activePath, child-status+edge-signature)` so navigating back to an unchanged node is a no-op; a child whose status or sibling deps changed busts the cache. The flat-grid vs. layered-flow choice is made client-side from the parsed edge set (`buildChildGrid` when no inter-child edge, `buildChildFlow` otherwise) — no server-side gate.

## User Decisions (2026-05-30)

- **Replace, not add.** The drill-down workspace replaces the Tree tab and the global DAG tab; Kanban is kept as a board that jumps into the workspace. View buttons collapse to **Workspace** / **Kanban**; the **DAG** button is removed.
- **Children-as-DAG in the main panel.** A node's subtasks are shown via the per-subtree DAG in the main panel (user: "just put the DAG of the current subtasks there").
- **frontend-design skill.** The user will refine their own `frontend-design` skill later; the available `frontend-design:frontend-design` plugin skill is used in the meantime.

## Decomposition

A serial pipeline — **not parallel.** Every task heavily edits the same `base.html` (~1950 lines) and/or `plan_dashboard.py`, so concurrent worktrees would conflict; dispatch one at a time in dependency order.

- `server-partials` — add `GET /nav` (navigation-only tree partial) and `GET /node/{path}` (active-node body-only partial); refactor `task_node.html` so the body block is a shared macro. Foundation. Deps: none.
- `routing-shell` — the three-region layout shell, the `activePath` hash router (`parseHash`/`setActive`/`hashchange`/`popstate`/`restoring` guard), the breadcrumb, the Workspace/Kanban toggle (DAG button removed), and `revealTask`→`setActive` alias. Region loaders are stubs. Deps: `server-partials`.
- `sidebar-nav` — render `#nav-tree` from `/nav`; row-click→`setActive`, caret→local fold, active highlight + ancestor auto-expand + scroll, deep-link ancestor-walk lazy-load, sidebar search. Deps: `server-partials`, `routing-shell`.
- `main-panel` — active-node card (`/node/{path}` + reused markdown/comments) and children panel (`/dag?root=` parsed client-side into clickable `.child-card`s whose click→`setActive`; leaf→omit; no inter-child dep→flat grid, else layered topological flow); remove mermaid entirely along with the old global `renderDagView` and inline `toggleDagPanel`. Deps: `server-partials`, `routing-shell`.
- `sse-simplify` — replace `captureNodeState`/`restoreNodeState`/`_pendingSwapState` with the single-active-node SSE model. Deps: `sidebar-nav`, `main-panel`.
- `a11y-responsive` — keyboard nav, responsive drawer, focus management, reduced-motion. Deps: `sidebar-nav`, `main-panel`.

## Results

Integration cleanup landed after the workstream was approved and synced (three commits):

- **Dead-code prune.** Removed `Task.has_child_dependency_graph()` from [`_task_io.py`](../../../../skills/task-system/scripts/_task_io.py); its only caller was the removed mermaid panel. Net governing diff for the method is now zero (it was added on this branch for that panel). No test exercised it.
- **Doc currency.** Refreshed the stale mermaid-era descriptions in this task body (Objective body bullet, deep-linking and design-principles bullets, Decomposition `main-panel` bullet) to the shipped card-flow reality: direct children render as `.child-card`s — flat grid when no inter-child dependency, layered topological flow with `↳ after:` footers otherwise; mermaid removed; `has_child_dependency_graph` gone.
- **Tests (headline deliverable).** Added 15 tests to [`test_dashboard.py`](../../../../skills/task-system/scripts/test_dashboard.py): suite went **229 → 244**.
  - `TestChildrenDagContract` (5) — pins the `GET /dag?root=<path>` server contract the cards parse: a branching-dependency parent (a→b, a→c, b→d) carries exactly its direct children in `data-node-paths`, the per-child status fill colors, and the `dep_id --> child_id` edges in prerequisite→dependent direction; a no-dependency parent yields no `-->` edges; a leaf yields an empty child set.
  - `TestMermaidRemoval` (4) — regression guard: `base.html` and the served page carry no mermaid CDN `<script src>`, no `mermaid.initialize`/`mermaid.run`, no `wireDagNodeClicks` (asserts the live references are gone, not the bare `mermaid` token that survives in a descriptive comment).
  - `TestChildFlowClientLogic` (6, node-backed) — extracts the pure builders (`buildChildFlow`/`buildChildGrid`/`childCardHTML`/`childrenSig`/`escapeHtml`/`escapeAttr`/`SUBTASK_HEADER`/`DAG_FILL_STATUS`) from `base.html` and runs them under `node` via `subprocess` (skips when `node` is absent). Asserts topological tier order (`[[a],[b,c],[d]]`), cycle-safety (a↔b cycle still terminates and flushes the unresolvable pair into the last tier with every child placed once), direct-only `after:` footers, and that `childrenSig` busts on a status change *and* on a dependency change. The genuinely new client logic is exercised, not just the server contract — DOM-bound functions (`parseChildrenDag`/`loadChildrenDag`) are deliberately out of the node harness and covered instead by the contract tests.

**Final diff self-check:** `git diff aad548e3..HEAD`; surviving cleanup hunks are (1) net-zero `_task_io.py` method removal, (2) this task's mermaid→card doc refresh + this Results section, (3) additive-only `test_dashboard.py` (+319 lines: imports, two fixtures, three test classes). No suspicious hunks — no `skills/*`/`agents/*` instruction edits, no base-side restorations, no formatting churn. Project Doc Audit walk-up (root `README.md`/`CLAUDE.md`/`AGENTS.md`) found no stale references to the pruned method, the removed mermaid panel, or a hard-coded test count.
