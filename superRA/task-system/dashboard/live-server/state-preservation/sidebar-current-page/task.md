---
title: "Keep the current page expanded and preserve open branches across reload"
status: implemented
depends_on: []
tags: []
created: 2026-06-07
---

## Objective

Bring sidebar state preservation up to the master-detail architecture (see the parent task's architecture note). Two concrete annoyances remain in the live UI:

1. **The current page is not expanded to its own children.** `updateSidebar(path)` expands the active task's ancestor chain (`for i < segs.length - 1`) and highlights its row, but leaves the active node's own caret closed — so after navigating into a task the user must manually open it to see what is inside. The sidebar should always show the current page expanded one level.

2. **A `task.md` update folds the sidebar back to the top level.** A structural change (or a `task.md` edit that changes the task's child set) broadcasts `full-reload`; `onFullReload` rebuilds `#nav-tree` from `/nav` (all branches closed) and only re-expands the active path's ancestors via `setActive` → `updateSidebar`. Every other branch the user had opened collapses. The rebuild should restore the tree to the open/closed shape the user left it in.

**Files:** `skills/task-system/scripts/templates/base.html` (sidebar nav + the `full-reload` handler).

## Results

Implemented in [base.html](skills/task-system/scripts/templates/base.html), reusing the existing `expandNavNode` lazy-expand primitive (which adds the `expanded` class, shows `.task-children`, and lazy-loads depth ≥ 3 branches via `/nav/{path}` on first open).

**Current page expands to its children.** `updateSidebar(path)` now calls `await expandNavNode(target)` on the active node after the ancestor walk and before highlighting/scrolling it. Leaf nodes are a no-op (guarded inside `expandNavNode`), so selecting a leaf task still just highlights it.

**Open branches survive a rebuild.** Added a capture/restore pair:
- `getExpandedNavPaths()` snapshots the `data-path` of every `.task-node` whose own caret is `expanded`.
- `restoreExpandedNavPaths(paths)` re-opens them after a fresh `/nav`, sorted shallow-to-deep (by `path.split('/').length`) so each parent is expanded — and its children lazy-loaded into the DOM — before its descendants are reached. Paths whose task was deleted are simply absent and skipped.

`onFullReload` captures the open branches **before** `loadNavTree` wipes them and restores them **after** the rebuild (before `setActive`), so a structural edit reopens the tree where the user left it instead of folding to the root. `setActive` then re-asserts the active highlight and expands the current page on top of the restored shape.

### Validation

- **Dashboard test suite:** 117 passed, 2 skipped (`uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts/test_dashboard.py -q`). Added two regression classes: `TestSidebarStatePreservation` (capture/restore helpers present; restore is shallow-to-deep; `onFullReload` captures-before-rebuild-then-restores; `updateSidebar` expands the current page) and `TestWorktreeSelectorLiveRefresh` (see the multi-worktree-serving follow-up).
- **Real served path:** dashboard serves `/` and `/nav` at HTTP 200 with all four new JS hooks present in the rendered page (`getExpandedNavPaths`, `restoreExpandedNavPaths`, `initWorktreeSelectorRefresh`, `await expandNavNode(target)`).
- **Remaining manual check:** a browser click-through (expand sibling branches, edit a `task.md` that triggers `full-reload`, confirm the branches stay open and the active page stays expanded) is the final confirmation; the wiring follows the proven `expandNavNode` ancestor-walk path.
