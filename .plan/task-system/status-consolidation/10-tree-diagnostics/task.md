---
title: "Build task_check.py diagnostic tool"
status: not-started
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
