---
title: "Simplify live-reload to the single-active-node model"
status: not-started
depends_on:
  - sidebar-nav
  - main-panel
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Replace the heavy SSE state capture/restore machinery with the lighter model the master-detail layout allows. Load `frontend-design:frontend-design` before touching markup. Live server only; edit `skills/task-system/scripts/templates/base.html`. Runs after `sidebar-nav` and `main-panel` because it targets their regions.

**Why it simplifies.** The old `captureNodeState`/`restoreNodeState`/`_pendingSwapState` system (~300 lines, [`base.html:1143`](../../../../../skills/task-system/scripts/templates/base.html#L1143)–1349 plus the `htmx:sseBeforeMessage`/`afterSwap` handlers) existed because one giant tree held all expand/section/scroll/markdown-render state across `outerHTML` swaps. Under the new model, the only "open, detailed" node is `activePath`; everything else is a body-free sidebar row. So per-node state to preserve collapses to "is the swapped node the active one?" plus the small `sidebarOpenPaths` fold set.

**New SSE behavior.** The watcher still emits `task:<path>`, `summary-updated`, and `full-reload` ([`plan_dashboard.py:178`](../../../../../skills/task-system/scripts/plan_dashboard.py#L178)). Handle them as:

- `task:<path>` where `path === activePath` → re-fetch `GET /node/{path}` and re-render the active card (re-run section render + `loadComments`). Preserve the comment-edit suppression window: keep the `_commentEditPaths` 3-second guard ([`base.html` ~1355]) so a local comment write isn't clobbered by its own SSE echo.
- `task:<path>` for any path → swap that row in the sidebar (status badge / progress / comment badge only — cheap, no body, no capture/restore). If `parent(path) === activePath`, also re-render the children-DAG (a child's status color, or an added/removed sibling, changes the graph) — honor the `(path, child-status-signature)` cache from `main-panel`.
- `summary-updated` → unchanged (header bar).
- `full-reload` (structural add/delete, worktree switch) → re-fetch `/nav` into the sidebar, then re-run `setActive(activePath)` to restore highlight + breadcrumb + main panel and the `sidebarOpenPaths` folds. If `activePath` no longer exists, fall back to its nearest surviving ancestor and `replaceState` the corrected hash.

**Delete** the now-unused `captureNodeState`, `restoreNodeState`, `_pendingSwapState`, and the old full-tree-oriented `htmx:sseBeforeMessage`/`afterSwap` bodies — but keep htmx's declarative `sse-swap` on sidebar rows and the summary bar (htmx owns those; the router never calls `setActive` from an SSE handler). Remove any dead helpers left orphaned by the deletion; mention (do not delete) anything unrelated.

## Validation

- Editing the active task's `task.md` on disk live-updates its card (and comments) without losing the active selection or breadcrumb; a pending local comment edit is not clobbered by the echo.
- Editing a non-active task updates only its sidebar row; if it is a child of the active node, the children-DAG re-renders (and is a cache no-op when nothing relevant changed).
- Adding/deleting a task dir (or switching worktree) rebuilds the sidebar and restores `activePath` (or its nearest surviving ancestor); folds and highlight come back.
- `captureNodeState`/`restoreNodeState`/`_pendingSwapState` are gone with no remaining references; `node --check` passes; live-server drive confirms each SSE path with no console errors. `pytest skills/task-system/scripts/test_task_system.py` still passes.
