---
title: "Simplify live-reload to the single-active-node model"
status: implemented
depends_on:
  - sidebar-nav
  - main-panel
tags: []
created: 2026-05-30
updated: 2026-05-31
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

## Results

Replaced the heavy SSE capture/restore machinery in [`base.html`](../../../../../skills/task-system/scripts/templates/base.html) with the single-active-node model. Net deletion of ~290 lines of client state machinery.

**Deleted.** `captureNodeState` (~75 lines), `restoreNodeState` (~120 lines), the `_pendingSwapState` map, the old full-tree `htmx:afterSwap` restore/markdown handler, the dead `htmx:sseMessage` comment-reload listener (it never fired — see below), and the old `#sse-full-reload` handler that fetched `/tree` into the removed `view-tree` container. No remaining references to any deleted symbol.

**New SSE model.** All live-reload now hangs off `htmx:sseBeforeMessage`, which is the only reliable hook (verified against htmx-ext-sse@2 source):
- **`task:<path>` dispatch** ([`base.html`](../../../../../skills/task-system/scripts/templates/base.html) `htmx:sseBeforeMessage` listener → `onTaskUpdate`). htmx still owns the declarative `sse-swap="task:<path>"` body-free row swap. `onTaskUpdate(path)`: if `path === activePath`, re-run `loadActiveNode` (same `/node` fetch + section render + `loadComments` pipeline as a fresh nav) and re-assert the nav-active highlight that the outerHTML row swap wipes (deferred one tick past the swap); else if `parentPath(path) === activePath`, re-run `loadChildrenDag(activePath)` — its existing `(path, child-status-signature)` cache makes this a no-op when nothing graph-relevant changed.
- **comment-edit suppression** preserved exactly: `withinCommentEditWindow` gates the same `_commentEditPaths` 3-second guard. Within the window the row swap is `preventDefault`-ed and the card refresh is skipped, so a local comment write isn't clobbered by its own echo; outside it, live updates resume.
- **`full-reload`** ([`base.html`](../../../../../skills/task-system/scripts/templates/base.html) `#sse-full-reload` `htmx:sseBeforeMessage` → `onFullReload`): re-fetch `/nav` into the sidebar, then re-run `setActive(activePath)` in `restoring` mode (no history write). If `activePath` no longer exists, `resolveSurvivingPath` walks up to the nearest still-present ancestor and `replaceState`s the corrected hash.
- **`summary-updated`** unchanged (declarative htmx innerHTML swap on the summary bar).

**Two integration bugs found and fixed during the live drive (both pre-existing latent, exposed by removing capture/restore):**
1. **`htmx:sseMessage` never reaches a body listener for outerHTML swaps.** htmx-ext-sse fires `sseMessage` on the *old* row *after* the `hx-swap="outerHTML"` swap has already detached it, so it never bubbles to `document.body`. The old comment-reload listener keyed off `htmx:sseMessage` was therefore dead. All `task:<path>` dispatch was moved to `htmx:sseBeforeMessage` (fires on the still-attached row, before the swap).
2. **`#sse-full-reload` never fired `htmx:beforeSwap`.** With `hx-swap="none"` the sse extension calls `api.swap` with a none-spec and emits no core `htmx:beforeSwap`. Rewired to `htmx:sseBeforeMessage`.

The active-row highlight loss (the fresh nav fragment carries no `nav-active` class) is handled by re-running `updateSidebar(activePath)` one tick after the swap.

**Server coordination (scope note).** The matching server-side half of this SSE model — `_watch_plan_root` emitting a single `full-reload` on a structural add/delete (instead of per-parent full-body `task:<parent>` fragments) and a body-free `_render_nav_node` fragment on a content edit (instead of `_render_task_node`) — was present as an **uncommitted, unattributed working-tree change** in [`plan_dashboard.py`](../../../../../skills/task-system/scripts/plan_dashboard.py) (`_watch_plan_root`, ~lines 243–281) when this task started; HEAD's committed server still did the old per-parent full-body fragment broadcast. The client model implemented here depends on that server contract, so the server diff is committed together with the client change. It is scoped entirely to the structural-vs-content branch of `_watch_plan_root` and touches nothing else.

**Verification.** Headless-Chromium drive of `plan_dashboard.py serve` against a 5-node fixture on the real repo filesystem (FSEvents-reliable; the macOS `/tmp` watcher silently drops events), each behavior confirmed with no console errors:
- Active task edit live-updates its card without losing selection or breadcrumb; hash stays `#/alpha/one`.
- Non-active child edit swaps only that sidebar row and re-renders the active node's children-DAG; an unrelated (non-child) edit leaves the children-DAG untouched (cache no-op); active selection/breadcrumb stable.
- Comment-edit suppression: during the 3s guard after a local comment write, the SSE echo triggers **zero** `loadActiveNode` re-fetches; post-guard edits resume live updates.
- Structural add rebuilds the sidebar (new row appears) and restores `activePath`.
- Deleting the active task falls back to its nearest surviving ancestor and `replaceState`s the corrected hash.

`node --check` on the extracted inline script passes; `pytest test_task_system.py + test_dashboard.py` = 209 passed (152 + 57), unchanged from baseline.
