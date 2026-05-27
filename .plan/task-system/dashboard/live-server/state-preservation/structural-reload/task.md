---
title: "Replace full-reload with incremental tree update"
status: implemented
review_status: approved
integration_status: ~
depends_on:
  - capture-restore
tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

When a structural change occurs (task.md added or deleted, child directories change), the server currently broadcasts `full-reload` which triggers `location.reload()` in the client — destroying all UI state. Replace this with an incremental approach that fetches and swaps only the affected subtree.

**Current flow (server, `_watch_plan_root()` in `plan_dashboard.py`):**
- `watchfiles.Change.added` or `.deleted` for a `task.md` → sets `structural_change = True` → calls `rebuild_tree()` → broadcasts `full-reload`
- `rebuild_task()` returns `children_changed = True` → broadcasts `full-reload`

**Target flow:**
1. Server rebuilds the tree (as today) but instead of broadcasting `full-reload`, identifies the nearest parent of the structural change and broadcasts a `task:{parent_path}` event with the re-rendered parent node fragment.
2. Client receives the `task:{parent_path}` event. The capture-restore mechanism from the sibling task handles `outerHTML` swaps, so the parent swap replaces the parent subtree and then re-expands captured paths within the new subtree.

**Server-side changes (`plan_dashboard.py`, `_watch_plan_root()`):**
- For `watchfiles.Change.added`: determine the parent task path of the new `task.md`. After `rebuild_tree()`, look up the parent in `_task_index`, render its node fragment via `_render_task_node()`, and broadcast `task:{parent_path}`.
- For `watchfiles.Change.deleted`: same approach — find the parent, re-render, broadcast the parent's update.
- For `children_changed` from `rebuild_task()`: the task whose children changed is already known. After `rebuild_tree()` (to ensure full consistency), re-render that task node and broadcast `task:{task_path}`.
- Keep `full-reload` as a last-resort fallback only for cases where the root task itself is structurally affected or the tree is in an inconsistent state. This should be rare.

**Client-side changes (`base.html`):**
- The capture-restore mechanism from the sibling task already handles `outerHTML` swaps on task nodes, so parent-level swaps work automatically — a parent swap replaces the parent and all its children, and the restore logic re-expands captured paths within the new subtree.
- Improve the `full-reload` fallback: instead of `location.reload()`, fetch the tree HTML fragment via AJAX and swap `#view-tree`, with state capture/restore around the swap. Fall back to `location.reload()` only if AJAX fails.

**Server-side route addition:**
- Add `GET /tree` route that returns just the task tree HTML (the rendered nodes without the page chrome) for use by the AJAX-based full-reload fallback.

**Depth consideration:** `_render_task_node()` currently hardcodes `depth=3`, which means child nodes inside the fragment won't render their own children inline — they'll get `data-needsLoad='true'` for lazy loading. This is fine for small subtrees but may produce collapsed-looking results for deeply nested tasks. If this is a problem in practice, consider passing the correct depth based on the task's position in the tree.

**Files to modify:**
- `skills/task-system/scripts/plan_dashboard.py` — watcher logic, new route
- `skills/task-system/scripts/templates/base.html` — full-reload handler

**Validation:**
- Create a new `task.md` in a subdirectory while the dashboard is open → the new task appears in the tree without losing expanded/scroll state elsewhere
- Delete a `task.md` → the task disappears without a full reload
- Rapid structural changes (create + delete in quick succession) → dashboard stays stable, no flicker or state loss

## Results

Implemented incremental tree updates for structural changes across three areas.

**Server-side watcher (`_watch_plan_root()` in [plan_dashboard.py:183](skills/task-system/scripts/plan_dashboard.py#L183)):**
- Replaced the single `structural_change` boolean with `structural_parent_paths: set[str]` that collects the parent path of each added/deleted `task.md`.
- After `rebuild_tree()`, iterates over `structural_parent_paths`, looks up each parent in `_task_index`, renders its node fragment, and broadcasts `task:{parent_path}` instead of `full-reload`.
- For `children_changed` from `rebuild_task()`, re-renders the affected task and broadcasts `task:{task_path}` instead of `full-reload`.
- Falls back to `full-reload` only when the root task itself is structurally affected (and has no body node in the DOM) or the parent is missing from the index.

**Depth-aware rendering ([plan_dashboard.py:324](skills/task-system/scripts/plan_dashboard.py#L324)):**
- Added `_task_depth(task_path)` helper that computes depth from slash count in the path.
- Changed `_render_task_node()` to accept an optional `depth` parameter (defaults to auto-computed from path). This ensures parent-scoped broadcasts render children inline at the correct depth rather than always using `depth=3`.

**New `/tree` route ([plan_dashboard.py:399](skills/task-system/scripts/plan_dashboard.py#L399)):**
- Added `GET /tree` endpoint returning just the task tree HTML (same rendering logic as `base.html` but without page chrome) for the AJAX-based full-reload fallback.

**Client-side full-reload handler ([base.html:1192](skills/task-system/scripts/templates/base.html#L1192)):**
- Replaced `location.reload()` with an AJAX fetch of `/tree` that calls `captureNodeState(treeContainer)` to capture all UI state (expanded paths, open sections, rendered markdown, children visibility, scroll position, comment form drafts), swaps `#view-tree` innerHTML, and restores state via `restoreNodeState()`.
- Falls back to `location.reload()` only if the AJAX fetch fails.

**Testing:** All 56 existing dashboard tests pass (1 pre-existing failure in `test_template_escapes_closing_template_tag` unrelated to this change). Python syntax and Jinja2 template parsing verified.

