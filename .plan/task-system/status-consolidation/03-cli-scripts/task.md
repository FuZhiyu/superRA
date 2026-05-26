---
title: "Update CLI scripts for unified status"
status: not-started
review_status: ~
integration_status: ~
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
