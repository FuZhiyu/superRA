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
