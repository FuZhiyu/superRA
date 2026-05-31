---
title: "Three-region shell + activePath hash router"
status: not-started
depends_on:
  - server-partials
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Build the master-detail layout shell and the `activePath` hash router — the skeleton every other client task hangs off. Region content loaders are stubs here; `sidebar-nav` and `main-panel` fill them. Load `frontend-design:frontend-design` before touching markup or CSS. Live server only; edit `skills/task-system/scripts/templates/base.html` (and minimal CSS there).

**Layout.** Replace the three sibling view containers and the `showView` toggle at [`base.html:642`](../../../../../skills/task-system/scripts/templates/base.html#L642) and [`base.html:747`](../../../../../skills/task-system/scripts/templates/base.html#L747) with a three-region grid: a persistent left **sidebar** (`#nav-tree`, empty container here), and a **main panel** holding a breadcrumb (`#crumbs`), an active-node card (`#active-node`, empty here), and a children-DAG region (`#children-dag`, empty here). Keep the existing header (title, summary bar with its `sse-swap`, search box, theme toggle) [`base.html:617`](../../../../../skills/task-system/scripts/templates/base.html#L617). Collapse the three view buttons to **Workspace** (default) and **Kanban**; **remove the DAG button**. `#view-kanban` stays as the Kanban board container, shown when Workspace is toggled off.

**Router — `activePath` is the single source of truth.**

- `parseHash()` reads `location.hash` as `#/<task/path>` and returns the path verbatim (`#/` → root, empty path).
- `setActive(path)` is the one entry point: set `activePath`; unless restoring, `history.pushState` the new hash; then call `updateBreadcrumb(path)` and the (stubbed) `updateSidebar(path)` / `loadActiveNode(path)` / `loadChildrenDag(path)`. Switch to the Workspace view if Kanban is showing.
- A `restoring` flag makes load-time and `popstate` navigation use `replaceState` (load) / no history write (`popstate`), never `pushState` — so the browser's own back/forward stack drives navigation without double entries.
- Wire `hashchange`/`popstate` → `setActive(parseHash())` with the guard; on initial load, `replaceState` the resolved hash (default `#/`) and `setActive` it.

**Breadcrumb.** `updateBreadcrumb(path)` rebuilds `#crumbs` from `path.split('/')`: `root › seg › … › active`, each non-active crumb a button calling `setActive(ancestorPath)`; the active crumb is inert. Resolve segment display titles from data the sidebar/server provides (a path→title lookup; for the stub, the slug is an acceptable placeholder until `sidebar-nav` supplies titles).

**Re-alias the old primitive.** Replace `revealTask(path)` / `showTreeAndExpand(path)` ([`base.html:1044`](../../../../../skills/task-system/scripts/templates/base.html#L1044), [`base.html:1138`](../../../../../skills/task-system/scripts/templates/base.html#L1138)) with a thin alias that switches to Workspace and calls `setActive(path)`, so the Kanban cards ([`kanban.html:30`](../../../../../skills/task-system/scripts/templates/kanban.html#L30)) and any other caller keep working. Delete the giant-tree ancestor-expansion body of the old `revealTask` (its replacement, the deep-link ancestor-walk, lands in `sidebar-nav`).

**Keep the boundary clean.** The router uses explicit `fetch` for `activePath`-driven content (as `renderKanbanView` already does). Do not let SSE handlers call `setActive`. Leave the existing SSE capture/restore code in place for now (it is gutted in `sse-simplify`); just ensure it does not fight the new layout.

## Validation

- Loading `#/` shows the shell: sidebar container, breadcrumb reading `root`, empty main regions; loading `#/task-system/dashboard` sets `activePath` to that path and the breadcrumb shows the full ancestor chain.
- In the console, `setActive('a/b/c')` updates `activePath`, pushes `#/a/b/c`, and rebuilds the breadcrumb; clicking a non-active crumb ascends; browser back/forward move between visited nodes via `popstate` with no duplicate history entries.
- The Workspace/Kanban toggle switches regions; the DAG button is gone; Kanban cards (calling the `revealTask` alias) switch to Workspace and set the clicked path active (card→content wiring completes in `main-panel`, but the active-path + breadcrumb update is observable now).
- Reload on a deep hash restores `activePath` (content rendering arrives with `sidebar-nav`/`main-panel`; here, confirm the hash/breadcrumb/active-state restore).
- Extract the page's main script and `node --check` passes; serve and confirm no console errors and the header/summary-bar/theme/search still work.
