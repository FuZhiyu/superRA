---
title: "Test Suite"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
  - migration
  - dashboard
---

## Objective

Build the task-tree test suite: fixtures for flat and nested trees, and tests for frontmatter parsing, task CRUD, tree walking, status rollup, frontier computation, migration, dashboard rendering, body-section parsing, the no-auto-rebuild hook contract, and migration idempotency.

## Results

The suite lives under `skills/task-tree/scripts/`, split by tested module across seven test modules and passing green.

### Key Findings
- Modules: `test_task_tree.py` (data layer, CLI scripts, migration, hooks), `test_dashboard.py` (dashboard rendering, server lifecycle, standalone export, artifact workflow), `test_cli.py`, `test_multi_worktree.py`, `test_worktree_selector.py`, `tests/test_comments.py`, `tests/test_state_preservation.py`. The boundary rule is that a test file follows its tested module.
- `conftest.py` provides the canonical `_write_task_md` helper, `_write_tiny_png`, `_serve_plan`, and the `plan_with_branches` fixture; the two largest test files import from it, and the remaining files can migrate off their local `_write_task_md` variants incrementally.
- `TestNoAutoRebuild` locks in the no-auto-rebuild contract (the hook does validation and status propagation only); `TestMigrateV2` verifies idempotency on already-migrated files.
- Two-location layout: loose `scripts/test_*.py` for broad-scope files, and the `scripts/tests/` package for focused sub-concern modules.
