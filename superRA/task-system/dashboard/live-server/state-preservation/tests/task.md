---
title: "Tests for state preservation"
status: implemented
depends_on:
  - structural-reload
tags: []
created: 2026-05-26
---

## Objective

Add server-side tests for the new watcher behavior and the `/tree` route. Client-side state capture/restore is JavaScript and tested manually via the validation criteria in the sibling tasks; this task covers the Python-testable parts.

**Test cases for `_watch_plan_root()` behavior (or the extracted helper logic):**
- Content change to a `task.md` → `rebuild_task()` called, `task:{path}` event broadcast (not `full-reload`)
- Structural addition (new `task.md` created) → `rebuild_tree()` called, `task:{parent_path}` event broadcast (not `full-reload`)
- Structural deletion → `rebuild_tree()` called, `task:{parent_path}` event broadcast
- `children_changed` from `rebuild_task()` → tree rebuilt, parent-scoped event broadcast
- Root-level structural change → `full-reload` fallback

**Test cases for `/tree` route:**
- Returns HTML fragment (not a full page) containing task nodes
- Response contains `task-node` divs with correct `data-path` attributes
- Returns updated content after `rebuild_tree()`

**Test infrastructure:** Use the existing test patterns in `skills/task-system/scripts/tests/`. Create temporary `.plan/` directories with `tmp_path` fixtures. For SSE broadcast assertions, mock `_broadcast()` or capture its calls.

**Files to create/modify:**
- `skills/task-system/scripts/tests/test_state_preservation.py` (new)

**Validation:**
- All tests pass with `pytest skills/task-system/scripts/tests/test_state_preservation.py`
- Tests do not depend on a running server (use `TestClient` from `starlette.testclient` for route tests)

## Results

Created [`skills/task-system/scripts/tests/test_state_preservation.py`](skills/task-system/scripts/tests/test_state_preservation.py) with 36 tests across 6 test classes:

- **TestRebuildTaskChildrenChanged** (7 tests): Verifies `rebuild_task()` returns `children_changed=True` only when child directories are added/removed, returns `(None, False)` for deleted tasks, and correctly updates the flat index.
- **TestRenderTaskNodeDepth** (5 tests): Verifies `_task_depth()` path-to-depth mapping, explicit vs inferred depth in `_render_task_node()`, children rendered inline at depth < 3, and lazy-loaded via `needsLoad` marker at depth >= 3.
- **TestTreeRoute** (7 tests): Verifies `/tree` returns 200, returns an HTML fragment (no `<html>`/`<head>`/`<body>` tags), contains `task-node` divs with correct `data-path` and `sse-swap` attributes, reflects tree changes after `rebuild_tree()`, and renders root as a node when root has body content.
- **TestWatcherDecisionLogic** (10 tests): Simulates the watcher's change classification logic to verify: content changes produce `task:{path}` events, structural additions/deletions produce `task:{parent_path}` events, root-level structural changes with no body fall back to `full-reload`, root with body produces `task:` event, `children_changed` produces `task:{path}` event (with `skip_init` to exercise the real `children_changed=True` code path), non-task files are ignored, multiple content changes in a batch each get their own event, and `summary-updated` is emitted after both content and structural changes.
- **TestBroadcastIntegration** (3 tests): Verifies SSE frame formatting for `task:{path}`, `full-reload`, and `summary-updated` events.
- **TestTaskDepth** (4 tests): Unit tests for `_task_depth()` helper covering root, top-level, nested, and deeply nested paths.

All 36 tests pass. Tests use `tmp_path` fixtures for temporary `.plan/` directories and `starlette.testclient.TestClient` for route tests; no running server required.

### Superseded (2026-06-07)

These tests target the old watcher contract (per-parent `task:{parent_path}` fragments on structural change, `_render_task_node` depth, the `/tree` route) that the master-detail migration retired — the live structural path now emits a single `full-reload` and the client rebuilds the sidebar from `/nav` (see the `structural-reload` child's Superseded note). `test_state_preservation.py` still passes against the surviving legacy helpers (`_render_task_node`, `/tree`), but it no longer characterizes the live state-preservation path. Current-architecture regression coverage lives in `test_dashboard.py::TestSidebarStatePreservation` and `TestWorktreeSelectorLiveRefresh`, added with the `sidebar-current-page` child.

