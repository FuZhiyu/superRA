---
title: "Update and extend test suite"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 02-data-layer
  - 03-cli-scripts
  - 04-migration-tooling
  - 10-tree-diagnostics
tags: [code, tests]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update existing tests and add new ones to cover the unified status model, `archived` status, `--cascade`, and the diagnostic tool.

**`test_task_system.py` — field removal:**
- Remove `review_status` and `integration_status` from all test fixture helpers
- Remove assertions for both fields
- Update or remove `test_bad_review_status_value` test
- Update all frontmatter strings in test fixtures

**`test_dashboard.py` — field removal:**
- Remove both fields from test fixture helpers and fixture creation

**New tests — archived status:**
- `archived` tasks excluded from `compute_frontier()`
- `archived` tasks excluded from `compute_status()` rollup (parent with 2 approved + 1 archived = approved)
- `archived` tasks don't block dependents (sibling depends on archived task → dependency satisfied)

**New tests — cascade:**
- `--cascade approved` on branch task sets all descendant leaves to `approved`
- `--cascade not-started` resets all descendant leaves
- `--cascade archived` archives all descendant leaves
- `--cascade` with `in-progress`/`implemented`/`revise` errors
- Warning when setting status on branch task without `--cascade`

**New tests — migration:**
- Migration mapping: given various `(status, review_status, integration_status)` triples, verify the upgrade produces the correct unified `status`
- Forward-compatible reading: `_task_io.py` silently ignores `review_status`/`integration_status` in old task files
- `--upgrade-status` dry-run and actual upgrade modes
- `## Workflow Status` section removal

**New tests — diagnostics:**
- Detects: invalid status values, rollup mismatches, broken dependencies, cycles, archived dependency warnings, stale fields
- `--json` output is parseable
- Exit codes: 0 clean, 1 issues found

## Results
