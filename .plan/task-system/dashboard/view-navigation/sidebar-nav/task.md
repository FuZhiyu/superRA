---
title: "Sidebar navigation tree"
status: not-started
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
