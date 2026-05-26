---
title: "Update CLI scripts for unified status"
status: implemented
depends_on:
  - 02-data-layer
tags: [code]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update all task-system CLI scripts to remove `review_status` and `integration_status` references, add `archived` status support, and add `--cascade` for branch tasks.

**`task_update.py`:**
- Remove `--review-status` and `--integration-status` CLI arguments
- Remove corresponding parameters, conditional update logic, and function passing
- Add `--cascade` flag: when setting status on a branch task, cascade to all descendant leaves. Warn (not error) when setting status on a branch task without `--cascade` — "This task has children; stored status is overridden by computed rollup."
- `--cascade` only valid for `approved`, `not-started`, and `archived` (the states with clear recursive semantics). Error on `--cascade` with `in-progress`, `implemented`, or `revise`.

**`task_create.py`:**
- Remove `review_status: ~` and `integration_status: ~` from the task template

**`task_read.py`:**
- Remove `review_status` and `integration_status` from frontmatter field order for readable output
- Remove both from JSON output

**`task_query.py`:**
- Remove `review_status` and `integration_status` from JSON serialization
- Note: `archived` exclusion from frontier and rollup is handled in `_task_io.py` (task 02), not here. Verify `task_query.py` renders archived tasks correctly in `--tree` output (e.g., with a distinct badge).

## Results

All four CLI scripts updated for the unified status model:

**`task_update.py`** ([task_update.py](skills/task-system/scripts/task_update.py)):
- Removed `--review-status` and `--integration-status` CLI arguments and corresponding `update_task` parameters
- Removed imports of `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` (no longer exported by `_task_io`)
- Added `--cascade` flag with validation: only allowed with `--status`, only for branch tasks, only for `approved`/`not-started`/`archived`. Errors on `--cascade` with `in-progress`/`implemented`/`revise`.
- Cascade walks descendant leaves via `walk_plan`, skips archived descendants unless cascading `archived` itself
- Branch tasks without `--cascade` get a warning: "This task has children; stored status is overridden by computed rollup."

**`task_create.py`** ([task_create.py](skills/task-system/scripts/task_create.py)):
- Removed `review_status: ~` and `integration_status: ~` from `TASK_TEMPLATE`

**`task_read.py`** ([task_read.py](skills/task-system/scripts/task_read.py)):
- Removed `review_status` and `integration_status` from `field_order` in `_render_frontmatter_readable`
- Added `_STALE_FIELDS` set to suppress old fields in the fallback rendering loop (handles legacy files still containing these fields)
- Removed both fields from `task_data` dict in `render_json`

**`task_query.py`** ([task_query.py](skills/task-system/scripts/task_query.py)):
- Removed `review_status` and `integration_status` from `tree_to_json` serialization
- Added `archived` icon (`▪`) to `STATUS_ICONS` for tree rendering
- Added `archived` class to Mermaid DAG `status_colors` and `classDef` output

**Verification:** 21/21 CLI-related tests pass. One pre-existing test failure (`test_parse_leaf_task`) is from the data-layer change (task 02 removed `review_status` from `Task`); that test belongs to task 08-tests.
