---
title: "Test Suite"
status: revise
depends_on:
  - core-data-layer
  - cli-scripts
  - migration
  - dashboard
  - auto-rebuild
tags: []
script: skills/task-tree/scripts/test_task_tree.py
created: 2026-05-23
---

## Objective

Build `test_task_tree.py`: fixtures for flat and nested plan trees, tests for frontmatter parsing, task CRUD, tree walking, status rollup, frontier computation, migration, dashboard generation, body section parsing, auto-rebuild, and v1→v2 migration idempotency. All fixtures use v2 format (`## Objective`).

## Results

### Key Findings
- 53 tests, all passing in ~0.1s
- Coverage: frontmatter parsing (7 edge cases), task CRUD (10 tests including error paths), tree walking (2), status rollup (3), frontier computation (5 including nested DAG), migration (2), dashboard (1), body sections (4), auto-rebuild (2), v2 migration (2)
- `TestAutoRebuild` verifies dashboard content changes (not just file existence)
- `TestMigrateV2` verifies idempotency on already-v2 files

## Review Notes

1. **[MAJOR]** [task.md:22-24](task.md#L22) — Results claim "53 tests, all passing in ~0.1s", a per-area breakdown that matches nothing in the live suite, and a `TestAutoRebuild` class that no longer exists (replaced by [`TestNoAutoRebuild`](../../../skills/task-tree/scripts/test_task_tree.py#L1705), which asserts the opposite contract). Verified reality: 612 passed / 2 skipped in ~99s across 7 modules; `script:` ([task.md:11](task.md#L11)) names only `test_task_tree.py`. As the named Test Suite task this is the workstream's testing record; claims are off by an order of magnitude. Fix: rewrite Results to the live module inventory and counts (or an explicitly dated build record with a forward pointer to the live suite) and widen `script:` to `skills/task-tree/scripts/`.
2. **[MAJOR]** [test_task_tree.py:1044](../../../skills/task-tree/scripts/test_task_tree.py#L1044), [test_task_tree.py:4352](../../../skills/task-tree/scripts/test_task_tree.py#L4352) — the module (5143 lines, 52 classes, 330 tests) mixes data layer, CLI scripts, migration, hooks, dashboard rendering (`TestDashboard`), server lifecycle (`TestIdleShutdown*`, `TestBackgroundLaunch`, `TestPidHelpers`, `TestRuntimeFileKeying`), and multi-worktree forest detection, even though dedicated modules exist for those concerns ([test_dashboard.py](../../../skills/task-tree/scripts/test_dashboard.py), 2198 lines; `test_multi_worktree.py`; `test_worktree_selector.py`). `plan_dashboard` is tested in two files with no boundary rule, so new tests have two plausible homes and reviewers two places to check. Fix: split by tested module and move the dashboard/server classes into `test_dashboard.py`.
3. **[MINOR]** [test_task_tree.py:49](../../../skills/task-tree/scripts/test_task_tree.py#L49) — `_write_task_md` is independently defined six times with divergent signatures ([test_cli.py:21](../../../skills/task-tree/scripts/test_cli.py#L21), [test_dashboard.py:42](../../../skills/task-tree/scripts/test_dashboard.py#L42), [test_worktree_selector.py:31](../../../skills/task-tree/scripts/test_worktree_selector.py#L31), [tests/test_comments.py:51](../../../skills/task-tree/scripts/tests/test_comments.py#L51), [tests/test_state_preservation.py:34](../../../skills/task-tree/scripts/tests/test_state_preservation.py#L34)); no `conftest.py` exists, so the task-file template used by tests can drift six ways. Fix: hoist one helper into a shared `conftest.py`.
4. **[MINOR]** two test-placement conventions coexist — loose `scripts/test_*.py` alongside the [`scripts/tests/`](../../../skills/task-tree/scripts/tests/__init__.py) package — with no rule for which a new test joins. Fix: pick one during the item-2 split.
