---
title: "Sidebar navigation tree"
status: implemented
depends_on:
  - server-partials
  - routing-shell
tags: []
created: 2026-05-30
updated: 2026-05-30
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

**Lazy-load fix (`markLazyNodes`).** `nav_node.html` flags depth≥3 branches for lazy load via an inline `<script>` that sets `dataset.needsLoad` — but inline scripts injected via `innerHTML` do not execute, so deep branches were never loadable (deep-link reload silently failed). Instead of touching the shared (already-approved) macro, the sidebar flags lazy branches client-side after each fragment injection: a node whose `.task-children` container exists but is empty is a lazy branch (leaf nodes have no `.task-children` at all). `markLazyNodes()` runs after `/nav` and each `/nav/{path}` load. `toggleNavCaret`/`expandNavNode` consume `needsLoad` and fetch `GET /nav/{path}`.

**Root-row id.** `navNodeId(path)` mirrors the macro's `id="task-{{ (path|replace('/','-')) or 'root' }}"` so the root task (empty path, which *does* render as a row in this tree because the root `task.md` has a body) resolves to `task-root`, not `task-`.

**Breadcrumb titles.** `indexNavTitles()` harvests path→title from every nav row into the shared `pathTitles` map (re-run after lazy loads), so `routing-shell`'s `updateBreadcrumb` shows real titles. Verified crumbs render e.g. `root › Task System Skill › HTML Dashboard`.

**Search.** Repointed `applyFilters` from the removed `#view-tree` to `#nav-tree`; the descendant-aware `nodeMatchesSearch`/`nodeMatchesStatus` traversal is unchanged and operates over the shared `.task-node`/`.task-children` chrome. Verified descendant-aware filtering (an ancestor with no own-match stays visible when a loaded descendant matches) in both light and dark themes.

### Verification

- `node --check` on the extracted main script: **OK** (rendered via the real Jinja env, so the template also compiles).
- Headless Chromium against the live server (`plan_dashboard.py serve`): root load (57 rows, 56 titles); caret fold is local (`activePath` unchanged); row-click sets active + exactly-one highlight + real-title breadcrumb + hash; root row highlights as `task-root`; **deep-link reload at depth 5** (`#/task-system/dashboard/live-server/comments/comment-ui/edit-comment`) resolves — target in DOM, all 5 ancestor toggles expanded, target row highlighted; a bogus `setActive('does/not/exist')` produces no console error and leaves `activePath` set with zero highlighted rows; search descendant-aware in both themes. **No console errors** in any scenario.
- `pytest test_task_system.py` 152 passed; `pytest test_dashboard.py test_worktree_selector.py` 110 passed.

**Scoping note for `main-panel`.** Edits are confined to: the `.nav-active` CSS block, `applyFilters`'s one-line selector retarget, replacing the `updateSidebar` stub, the new sidebar JS block (between `initRouter` and the `revealTask` alias), and the `DOMContentLoaded` handler. The `loadActiveNode`/`loadChildrenDag` stubs and the `#active-node`/`#children-dag` containers are untouched.
