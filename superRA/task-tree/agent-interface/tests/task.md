---
title: "Hook + CLI Tests"
status: approved
depends_on:
  - core-and-hooks
  - task-read
tags: []
created: 2026-05-24
---

## Objective

Add tests for new functionality to `skills/task-tree/scripts/test_task_tree.py`. Verify existing tests still pass.

### Validation functions (`_task_io.py`)

- `validate_frontmatter`: catches bad enum values (e.g., `status: done` → warning), wrong types (e.g., `depends_on: "foo"` instead of list)
- `validate_dependencies`: catches missing sibling references (e.g., `depends_on: [nonexistent]` → warning)
- `detect_cycles`: catches circular deps (A→B→C→A → warning with cycle description)
- `validate_plan`: aggregates all warnings with task path prefixes

### Topological sort

- Children sorted by dependency order, not alphabetical (e.g., if B depends on A, order is A, B even if B < A alphabetically)
- Independent tasks in alphabetical order (tiebreaker)
- Handles diamond dependencies correctly (A→C, B→C, both A and B independent → A, B alphabetical, then C)
- Gracefully handles missing deps (warning, falls back to alphabetical)

### `task_read.py`

- Reads leaf task with ancestor context chain (root → parent → current)
- Reads root task (no ancestors section)
- `--no-ancestors` flag skips ancestor chain
- `--json` produces valid JSON with `ancestors`, `task`, `dependencies` keys
- Auto-detect plan root from subdirectory (walk up from cwd)
- Shows sibling dependency status with title and effective status

### `task_hook.py`

- Ignores non-task.md files (exits 0 immediately)
- Runs validation on task.md edits, outputs warnings
- Exits 0 always (even on validation failures or import errors)

**Pipeline:** `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py -v`

## Results

Added 39 tests across 6 new test classes to [`test_task_tree.py`](skills/task-tree/scripts/test_task_tree.py). Total suite: 92 tests, all passing.

**New test classes:**

- `TestValidateFrontmatter` (6 tests) — bad enum values, wrong types for depends_on/tags, empty title
- `TestValidateDependencies` (4 tests) — valid deps, missing sibling ref, nonexistent dep, no deps
- `TestDetectCycles` (4 tests) — no cycle, simple 2-node cycle, 3-node cycle with `->` description, independent tasks
- `TestValidatePlan` (4 tests) — valid plan, missing dep warning, path prefix on warnings, cycle warning
- `TestTopologicalSort` (4 tests) — dep order, alphabetical tiebreaker, diamond, missing dep fallback
- `TestTaskRead` (10 tests) — ancestor chain, root task, `--no-ancestors`, JSON keys/ancestors list, sibling dep status, autodetect plan root, nested ancestor chain
- `TestTaskHook` (7 tests) — ignores non-task.md, ignores non-Edit/Write, exits 0 on valid/invalid task.md, warnings to stderr, empty stdin, file outside `.plan/`
