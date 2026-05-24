---
title: "Core Library Enhancements"
status: not-started
review_status: ~
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Enhance `skills/task-system/scripts/_task_io.py` with functions needed by hooks and the new ordering model. All functions are stdlib-only, return data (no side effects), and are importable by both hooks and CLI scripts.

### 1. Topological sort for children

Replace alphabetical sorting in `walk_plan()` with DAG-based topological sort using `depends_on`. Tasks with no dependencies come first; tasks that depend on others come after their dependencies. Ties broken alphabetically. This replaces numeric-prefix ordering entirely.

Current code in `walk_plan()` sorts children with `sorted(subdirs)`. Replace with a topological sort that reads each child's `depends_on` field to determine order.

### 2. Validation functions

Called by both the PostToolUse hook and diagnostic CLI:

- `validate_frontmatter(task) -> list[str]` — check:
  - `status` is one of: `not-started`, `in-progress`, `implemented`, `revise`, `approved`
  - `review_status` is one of: `~`, `implemented`, `revise`, `approved`
  - `integration_status` is one of: `~`, `implemented`, `revise`, `approved`
  - `depends_on` is a list of strings
  - `tags` is a list of strings
  - `title` is a non-empty string

- `validate_dependencies(task, siblings) -> list[str]` — check all `depends_on` entries reference existing sibling directory names. `siblings` is a list of sibling directory names.

- `detect_cycles(tasks) -> list[str]` — check for circular dependencies in the sibling DAG. Takes a list of Task objects (siblings). Uses transitive closure. Return cycle descriptions.

- `validate_plan(plan_root) -> list[str]` — walk the entire plan tree, run all validations at each level, return aggregated list of warning strings prefixed with task path.

## Results

