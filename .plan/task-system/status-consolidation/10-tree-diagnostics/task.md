---
title: "Build task_check.py diagnostic tool"
status: implemented
review_status: ~
integration_status: ~
depends_on:
  - 02-data-layer
tags: [code, tooling]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Build a `task_check.py` CLI tool that validates tree integrity and reports issues. Read-only — no auto-fix mode.

### Checks

1. **Status validity.** All `status` values are in the valid enum (`not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`). Flag any unknown values or stale fields (`review_status`, `integration_status`) still present in frontmatter.
2. **Dependency integrity.** All `depends_on` references resolve to existing sibling directories. No circular dependencies in the DAG. Flag tasks depending on archived siblings.
3. **Rollup consistency.** For branch tasks: stored `status` matches `compute_status()` from children. Report mismatches.

### Output

Structured report: text by default, `--json` for machine consumption. Exit code 0 if clean, 1 if issues found. The output should be clear enough that an agent can parse it and decide what to fix.

## Results

Implemented [task_check.py](skills/task-system/scripts/task_check.py) — a read-only diagnostic CLI tool for task tree integrity.

### Implementation

**Three check categories**, each runnable independently via `--category`:

1. **Status validity** (`--category status`): Validates all `status` values against the enum (`not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`). Detects stale `review_status` and `integration_status` fields still present in frontmatter by reading the raw YAML (not just parsed Task objects).

2. **Dependency integrity** (`--category dependency`): Verifies all `depends_on` entries resolve to existing sibling directories. Runs cycle detection at each sibling level via `detect_cycles()`. Flags dependencies on archived tasks as warnings.

3. **Rollup consistency** (`--category rollup`): Compares stored `status` on branch tasks against `compute_status()` from children. Reports mismatches.

**Fault-tolerant tree walker** (`_walk_plan_tolerant`): Unlike `walk_plan()` which raises on invalid status values, the diagnostic tool catches `ValueError` from `parse_task()` and builds partial Task objects from raw frontmatter. This ensures the tool can still report all issues even when some tasks have invalid status values.

**Finding model**: Each finding carries `task_path`, `category`, `severity` (error/warning), and `message`. Severity mapping: invalid status = error, stale fields = warning, missing dependency = error, cycle = error, archived dependency = warning, rollup mismatch = warning.

### Usage

```
python3 task_check.py --plan-root .plan                    # text output, all checks
python3 task_check.py --plan-root .plan --json             # JSON output
python3 task_check.py --plan-root .plan --category rollup  # single category
```

Exit code 0 if clean, 1 if any issues found.

### Verification

Tested against the live `.plan/` tree in this worktree: correctly identifies 143 issues (15 errors from `../`-style dependency references that violate sibling-only constraint, 128 warnings from stale `review_status`/`integration_status` fields and rollup mismatches). Also verified with synthetic fixtures covering: clean tree (0 findings), invalid status, stale fields, missing dependencies, cycles, archived dependency warnings, and rollup mismatches.
