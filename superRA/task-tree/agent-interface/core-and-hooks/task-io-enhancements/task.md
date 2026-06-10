---
title: "Core Library Enhancements"
status: revise
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Enhance `skills/task-tree/scripts/_task_io.py` with functions needed by hooks and the new ordering model. All functions are stdlib-only, return data (no side effects), and are importable by both hooks and CLI scripts.

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

Added five functions to `skills/task-tree/scripts/_task_io.py`:

1. **`_topological_sort(tasks)`** — Kahn's algorithm with `heapq` for alphabetical tie-breaking; falls back to alphabetical order if cycles prevent full sort.
2. **`_walk_children()`** — Replaced `sorted(subdirs)` alphabetical ordering with a call to `_topological_sort()` on the parsed child tasks so `depends_on` drives sibling ordering.
3. **`validate_frontmatter(task)`** — Checks `status`, `review_status`, `integration_status` against their enum sets, and checks `depends_on`/`tags` are list-of-strings, and `title` is non-empty.
4. **`validate_dependencies(task, siblings)`** — Checks each `depends_on` entry is a known sibling name.
5. **`detect_cycles(tasks)`** — DFS-based cycle detection among a sibling group.
6. **`validate_plan(plan_root)`** — Walks the entire plan tree, runs all three validations at each level, returns prefixed warning strings.

All 53 existing tests pass.

## Review Notes

> 1. [MAJOR] This approved task retained its prior `## Review Notes` (4 MINOR items) after approval, violating the contract rule that the reviewer removes the section content entirely at APPROVE ([task-file-contract.md](../../../../../skills/task-tree/references/task-file-contract.md)); the items were also stale — the missing test coverage item was later satisfied by the `tests` sibling. Replaced here per the replace-don't-stack rule; remove this section at re-approval.
