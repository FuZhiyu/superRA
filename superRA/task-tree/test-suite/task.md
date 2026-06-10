---
title: "Test Suite"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
  - migration
  - dashboard
  - auto-rebuild
tags: []
script: skills/task-tree/scripts/
created: 2026-05-23
---

## Objective

Build `test_task_tree.py`: fixtures for flat and nested plan trees, tests for frontmatter parsing, task CRUD, tree walking, status rollup, frontier computation, migration, dashboard generation, body section parsing, auto-rebuild, and v1→v2 migration idempotency. All fixtures use v2 format (`## Objective`).

## Results

### Key Findings
- 612 tests passing / 2 skipped; ~99s across 7 test modules
- Modules: `test_task_tree.py` (data layer, CLI scripts, migration, hooks, multi-concern), `test_dashboard.py` (dashboard rendering, server lifecycle, standalone export, artifact workflow), `test_cli.py`, `test_multi_worktree.py`, `test_worktree_selector.py`, `tests/test_comments.py`, `tests/test_state_preservation.py`
- `test_task_tree.py` split: dashboard and server lifecycle classes moved to `test_dashboard.py`; boundary rule established (test files follow their tested module)
- `conftest.py` created: canonical `_write_task_md` helper (supporting all kwarg variants), `_write_tiny_png`, `_serve_plan`, and `plan_with_branches` fixture; the two largest test files (`test_task_tree.py`, `test_dashboard.py`) import from it — `test_cli.py`, `test_worktree_selector.py`, `tests/test_comments.py`, and `tests/test_state_preservation.py` still carry local `_write_task_md` variants and can migrate incrementally
- `TestNoAutoRebuild` locks in the no-auto-rebuild contract (hook does validation/status propagation only)
- `TestMigrateV2` verifies idempotency on already-v2 files
- Two-location layout retained: loose `scripts/test_*.py` for broad-scope files; `scripts/tests/` package for focused sub-concern modules

## Review Notes

1. **[MINOR]** [task.md:25](task.md#L25) — Results claim "[conftest.py] eliminates six independent copies across modules." Only `test_task_tree.py` and `test_dashboard.py` were migrated to import from conftest; `test_cli.py`, `test_worktree_selector.py`, `tests/test_comments.py`, and `tests/test_state_preservation.py` still carry local `_write_task_md` definitions. The minimum fix objective ("hoist one helper into a shared `conftest.py`") was met. Fix: update the claim to "migrates the two largest test files (test_task_tree.py, test_dashboard.py) to the canonical conftest helper" or remove the "eliminates six copies" wording.
   → implemented: rewrote the claim — only the two largest files import from conftest; the four remaining local variants are named explicitly as incremental-migration candidates ([task.md:25](task.md#L25))
