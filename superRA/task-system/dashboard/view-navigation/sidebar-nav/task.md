---
title: "Sidebar navigation tree"
status: approved
depends_on:
  - server-partials
  - routing-shell
tags: []
created: 2026-05-30
---

## Objective

Fill the `#nav-tree` sidebar with the persistent navigation tree and wire it to `activePath`. Load `frontend-design:frontend-design` before touching markup or CSS. Live server only; edit `skills/task-system/scripts/templates/base.html` (and the `nav_node` template if adjustments are needed). Build on the shell + router from `routing-shell` and the `/nav` route from `server-partials`.

**Render.** On load, fetch `GET /nav` into `#nav-tree`. Rows are navigation-only (no body). Each row has two affordances:

- the **disclosure caret** toggles that row's children **in the sidebar only** — a local fold state independent of `activePath` (a `sidebarOpenPaths` set). Reuse the existing expand/collapse CSS transitions; lazy-load depth ≥3 children via the nav lazy route from `server-partials` when a fold first opens.
- the **row label** calls `setActive(path)`.

**Implement `updateSidebar(path)`** (the stub from `routing-shell`): mark the row matching `activePath` with `.nav-active` (left accent bar + `--accent-soft` background, theme-aware), expand its full ancestor chain in the sidebar, and scroll it into view. Exactly one row is active at a time.

**Deep-link / not-yet-loaded targets.** When `setActive` targets a node whose sidebar row isn't in the DOM (deep path below the inline cutoff, or first load on a deep hash), walk `path.split('/')` and `await` each ancestor's nav lazy-load before descending — the proven ancestor-walk-and-await loop from the old `revealTask` ([`base.html:1053`](../../../../../skills/task-system/scripts/templates/base.html#L1053)), reused here against the nav route. The sidebar materializing is best-effort: the main panel fetches by full path directly (in `main-panel`), so a failed sidebar branch must not block content.

**Breadcrumb titles.** Supply a path→title lookup (from the rendered `/nav` rows or an inline JSON map) so `routing-shell`'s `updateBreadcrumb` shows real titles instead of slugs.

**Search.** Port the descendant-aware filter (`nodeMatchesSearch`/`nodeMatchesStatus`/`applyFilters`, [`base.html:872`](../../../../../skills/task-system/scripts/templates/base.html#L872)) to filter the sidebar rows (ancestor visible if any descendant matches), keeping the active row reachable.

## Validation

- The sidebar shows the full hierarchy; carets fold/unfold children locally without changing `activePath`; deep (≥3) branches lazy-load on first open.
- `setActive(path)` from any source highlights exactly the matching row, expands its ancestors, and scrolls it into view; the breadcrumb shows real titles.
- A deep-link reload (`#/a/b/c/d` below the inline cutoff) resolves: ancestors lazy-load and the target row ends up highlighted; if a sidebar branch fails to load, no JS error and `activePath` is still set.
- Sidebar search filters rows descendant-aware in both themes.
- Extract the main script and `node --check` passes; drive with the live server (HTTP and, where available, a headless browser) to confirm row-click navigation, caret folding, deep-link highlight, and search; no console errors. `pytest skills/task-system/scripts/test_task_system.py` still passes.

## Results

All work is in [`base.html`](../../../../../skills/task-system/scripts/templates/base.html) (sidebar concern only; the `#active-node`/`#children-dag` loaders are left as `main-panel` stubs). Implemented the `updateSidebar(path)` stub plus the sidebar load/wire/fold/search machinery.

**Sidebar tree + wiring.** `loadNavTree()` fetches `GET /nav` into `#nav-tree` on `DOMContentLoaded` *before* `initRouter()` so the first `setActive` lands on a real row. `initSidebarEvents()` installs a single delegated click handler on `#nav-tree` (survives the innerHTML swaps): a click on a non-leaf `.task-toggle` runs `toggleNavCaret()` (local fold only); a click anywhere else on a `.task-row` runs `setActive(path)`. Caret fold/unfold is sidebar-local — verified it leaves `activePath` unchanged.

**`updateSidebar(path)`** clears any prior `.nav-active` (exactly one active row), runs the ancestor-walk-and-await loop (reused from the old `revealTask`) to expand and lazy-load each ancestor so the target materializes, then adds `.nav-active` to the matching row and `scrollIntoView({block:'nearest'})`. New CSS `.nav-tree .task-row.nav-active` gives a left accent bar (`inset 3px 0 0 var(--accent)`) over `var(--accent-soft)` — theme-aware; confirmed `rgba(180,77,45,0.08)` (light) / `rgba(224,120,80,0.1)` (dark). It is fully best-effort: the ancestor walk and the active node-id lookup are wrapped/guarded so a missing or failed branch never throws and never blocks the main panel.

**Lazy-load flagging (`markLazyNodes`).** Depth≥3 branches must be flagged for lazy load. The mechanism is purely client-side: after each nav fragment injection, [`markLazyNodes()`](../../../../../skills/task-system/scripts/templates/base.html#L1255) sets `dataset.needsLoad='true'` on any node whose `.task-children` container exists but is empty (children exist server-side but weren't inlined). Leaf nodes have no `.task-children` at all, so they are never flagged. `markLazyNodes()` runs after `/nav` and each `/nav/{path}` load; `toggleNavCaret`/`expandNavNode` consume `needsLoad` and fetch `GET /nav/{path}`. The `nav_node.html` macro no longer emits any flag — the prior inline `<script>` that set `dataset.needsLoad` never executed under `innerHTML` injection and was removed at source (item 2); the macro now simply renders an empty `.task-children` container for the depth≥3 boundary, which is exactly the signal `markLazyNodes` keys off.

**Root-row id.** `navNodeId(path)` mirrors the macro's `id="task-{{ (path|replace('/','-')) or 'root' }}"` so the root task (empty path, which *does* render as a row in this tree because the root `task.md` has a body) resolves to `task-root`, not `task-`.

**Breadcrumb titles.** `indexNavTitles()` harvests path→title from every nav row into the shared `pathTitles` map (re-run after lazy loads), so `routing-shell`'s `updateBreadcrumb` shows real titles. Verified crumbs render e.g. `root › Task System Skill › HTML Dashboard`.

**Search.** [`applyFilters`](../../../../../skills/task-system/scripts/templates/base.html#L988) is pointed at `#nav-tree`; the descendant-aware `nodeMatchesSearch`/`nodeMatchesStatus` traversal operates over the shared `.task-node`/`.task-children` chrome. Two visibility axes are reconciled: `.hidden` (the filter axis, `display:none !important`) and sidebar fold (`.task-children` inline `display`, normally collapsed). Because the sidebar defaults fully collapsed, removing `.hidden` from a match is not enough — its ancestor `.task-children` chain stays `display:none`. So when a filter is active, [`revealFilterMatches`](../../../../../skills/task-system/scripts/templates/base.html#L1029) expands (sets `expanded` + `display:''`) the ancestor chain of every still-visible row whose own slug/title/path matches, making matches actually visible. The fold expansion never lazy-loads — it is scoped strictly to rows already in the DOM (see `setNavFold`, which mirrors `expandNavNode`'s class/display contract minus the fetch).

Fold state is preserved across search: on the no-filter→filter transition [`snapshotNavFolds`](../../../../../skills/task-system/scripts/templates/base.html#L1009) records each loaded non-leaf node's `expanded` state by path; on the filter→no-filter transition [`restoreNavFolds`](../../../../../skills/task-system/scripts/templates/base.html#L1024) restores it verbatim (nodes that appeared since default to collapsed). So clearing a search neither leaves the tree force-expanded nor collapses folds the user opened before searching.

**Documented limitation (accepted).** Search only reaches rows already in the DOM. Deep, not-yet-lazy-loaded branches (depth≥3 below the inline cutoff, unopened) are not searched — eagerly loading the entire tree just to search would defeat the lazy model. This is a deliberate, orchestrator-accepted scope boundary, not a defect; a user who opens a deep branch makes its rows searchable.

### Verification

- `node --check` on the extracted main script (rendered via the real Jinja env, so the template also compiles): **OK**.
- `/nav` payload carries **zero** `<script>` blocks and zero `needsLoad` strings after the macro change; `markLazyNodes` still flags the 4 depth-3 lazy branches client-side, and opening one fetches its children via `/nav/{path}`. Confirmed against the live server.
- **Search reveal from cold collapsed load** (headless Chromium, `plan_dashboard.py serve` on the real `.plan`, 57 rows): from the default fully-collapsed sidebar, typing `view-navigation` makes the matched row `visibleToUser:true` (`offsetParent` non-null, no hidden ancestor) in **both light and dark themes**. Clearing the search restores the prior fold state exactly (0 expanded → 0 expanded).
- **Fold restore with a manual fold present:** manually expand one branch (1 node expanded), search a *different* branch (`worktree-selector` → 3 expanded, match visible), clear → restored fold state equals the manual snapshot exactly (back to 1 expanded). Search neither force-expands nor collapses the user's prior fold.
- Caret fold is local (`activePath` unchanged); **deep-link reload at depth 5** (`#/task-system/dashboard/live-server/comments/comment-ui/edit-comment`) resolves — target in DOM, target row highlighted, exactly one `.nav-active`, `activePath` set. **No console errors** in any scenario, in either theme.
- `pytest test_task_system.py` **152 passed**; `pytest test_dashboard.py` **57 passed** (209 total). The one test that asserted the removed server-emitted `needsLoad` flag ([`test_task_system.py`](../../../../../skills/task-system/scripts/test_task_system.py#L2177) `test_nav_lazy_loads_deep_children`) was updated to assert the surviving invariant — depth≥3 children are not inlined and the boundary renders an empty `.task-children` container — keeping the baseline at 152.

**Scoping note for `main-panel`.** Edits are confined to: the `.nav-active` CSS block; the search block (`applyFilters` pointed at `#nav-tree` plus the new `snapshotNavFolds`/`setNavFold`/`restoreNavFolds`/`revealFilterMatches`/`nodeOwnRowMatches` helpers and the `preFilterFoldState` variable); replacing the `updateSidebar` stub; the sidebar JS block (between `initRouter` and the `revealTask` alias); and the `DOMContentLoaded` handler. In `nav_node.html`, the dead inline `<script>` lazy-flag block was removed and its docstring updated. In `test_task_system.py`, `test_nav_lazy_loads_deep_children` was repointed to the surviving invariant. The `loadActiveNode`/`loadChildrenDag` stubs and the `#active-node`/`#children-dag` containers are untouched.
