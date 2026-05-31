---
title: "Three-region shell + activePath hash router"
status: implemented
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

## Results

The master-detail shell and the `activePath` hash router are in place in [`base.html`](../../../../../skills/task-system/scripts/templates/base.html). Region content loaders are wired but intentionally empty stubs — `sidebar-nav` and `main-panel` fill them next. All work is on the live server template; the static `generate`/`DASHBOARD_HTML` path is untouched.

**Layout — three-region grid.** Replaced the three sibling view containers (`#view-tree` / `#view-dag` / `#view-kanban` + the server-rendered tree) and the old `showView('tree'|'dag'|'kanban')` toggle with a `#workspace` CSS grid: a persistent left `<aside id="nav-tree" role="tree">` and a `<main class="detail-panel">` holding the breadcrumb (`#crumbs`), the active-node card (`#active-node`), and the children-DAG region (`#children-dag`) — all empty here. `#view-kanban` is retained as the Kanban board, shown when Workspace is toggled off. The `render_task_node` import is gone from `base.html` (the index no longer server-renders the tree; the sidebar loads it from `/nav`). The header chrome (title, summary bar with its `sse-swap`, search box, theme toggle) is unchanged, and the `#workspace`/`#view-kanban` regions stay inside the existing `.main-content` SSE container (`sse-connect="/events"` + `#sse-full-reload` preserved).

**Layout CSS.** The body is now a flex column (`height: 100vh`) with a non-shrinking header and a flex-filling `.main-content`, so the sidebar and detail panel each scroll independently below the header without a magic header-height constant; the Kanban board keeps its legacy centered, page-scrolling layout via `#view-kanban:not(.hidden)`. The breadcrumb, sidebar rail, and detail panel pick up the existing editorial palette (Source Serif 4 display / IBM Plex Mono, warm paper tones, terracotta accent) and theme tokens.

**View toggle.** Collapsed the three view buttons to **Workspace** (default, `#btn-workspace`) and **Kanban** (`#btn-kanban`); the standalone **DAG** button is removed. `showView('workspace'|'kanban')` toggles `#workspace`/`#view-kanban` and only fetches Kanban on demand (as before).

**Router — `activePath` is the single source of truth.** Added `parseHash()` (reads `#/<task/path>` → path verbatim, `#/`/empty → root), `setActive(path)` (the one entry point: sets `activePath`; on user nav `pushState`s `#/<path>`; switches to Workspace if Kanban is showing; then calls `updateBreadcrumb` + the stubbed `updateSidebar`/`loadActiveNode`/`loadChildrenDag`), a `restoring` flag so load/`popstate` use `replaceState`/no-write (never `pushState`), the `popstate` listener, and `initRouter()` (resolves the initial hash, defaults `#/`, normalizes with `replaceState`, then activates) called from `DOMContentLoaded`.

**Breadcrumb.** `updateBreadcrumb(path)` rebuilds `#crumbs` as `root › seg › … › active`; each non-active crumb is a `<button>` calling `setActive(ancestorPath)`, the active crumb is inert (`disabled` + `aria-current="page"`). Segment labels prefer a `pathTitles` lookup (populated by `sidebar-nav`) and fall back to the slug for now.

**Stubs.** `updateSidebar`/`loadActiveNode`/`loadChildrenDag` are no-ops with explicit `/* stub: <task> */` markers and a header comment naming which sibling task fills each, so the router is fully wired and observable (breadcrumb + `activePath` + history) before the regions have content.

**Re-aliased the old primitive.** Deleted the giant-tree ancestor-expansion body of `revealTask` and its now-orphaned `expandTaskDetails` helper; `revealTask(path)`/`showTreeAndExpand(path)` are now thin aliases (`showView('workspace'); setActive(path)`), so Kanban cards ([`kanban.html:30`](../../../../../skills/task-system/scripts/templates/kanban.html#L30)) and DAG-node clicks (`wireDagNodeClicks`) keep working. The deep-link ancestor-walk that expands the sidebar lands in `sidebar-nav`.

**Clean boundary.** No SSE handler calls `setActive`; the existing SSE capture/restore code is left in place (gutted later in `sse-simplify`). With `#view-tree` gone, the SSE full-reload handler's `getElementById('view-tree')` returns null and falls back to `location.reload()` — harmless and superseded by `sse-simplify`. `applyFilters` and `updateTreeCommentBadges` query `.task-node`/`#view-tree`, which the empty shell lacks, so they no-op cleanly until `sidebar-nav` populates the rail.

**Validation.**
- The index renders the shell (`#nav-tree`/`#crumbs`/`#active-node`/`#children-dag`/`#workspace`), keeps `#view-kanban`, and the `#btn-dag` button and `#view-tree`/`#view-dag` containers are gone (verified via `TestClient` on `/`).
- The rendered page script passes `node --check`.
- A mock-DOM harness drives the router and confirms (23/23 checks): `parseHash` variants; `setActive('a/b/c')` sets `activePath`, `pushState`s `#/a/b/c`, and builds `root›a›b›c` with `c` active; clicking a non-active crumb ascends and pushes the ancestor hash; the root crumb returns to `""`; `popstate` re-applies a hash with **no** `pushState`; `initRouter` uses `replaceState` (no push) and defaults empty hash to `#/`; and the `revealTask`/`showTreeAndExpand` aliases set `activePath` and switch to Workspace.
- `/`, `/nav`, `/kanban`, `/dag`, `/tree` all serve 200; header chrome (`#summary-bar`, `#search-box`, `toggleTheme`, `#header-title`, SSE connect/full-reload) intact.
- `py_compile` clean; `pytest test_task_system.py` 152 passed; `pytest test_dashboard.py` 56 passed (the one remaining failure, `test_template_escapes_closing_template_tag`, is **pre-existing** — red on the base commit before this change, unrelated to the shell).

**Test updated.** `test_index_contains_task_nodes` asserted the index embedded the server-rendered task-node tree; that contract changed (the tree now loads client-side from `/nav`). Renamed to `test_index_contains_workspace_shell` and re-pointed it at the shell regions + the Workspace/Kanban toggle (and the absence of `#btn-dag`).
