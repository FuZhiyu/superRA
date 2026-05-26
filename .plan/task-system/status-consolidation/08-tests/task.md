---
title: "Update and extend test suite"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 02-data-layer
  - 03-cli-scripts
  - 04-migration-tooling
tags: [code, tests]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update existing tests and add new ones to cover the unified status model.

**`test_task_system.py`:**
- Remove `review_status` from all test fixture helpers (lines 40, 63)
- Remove `review_status="approved"` from fixture task creation (lines 85, 121)
- Remove `review_status` assertions (line 147)
- Remove `review_status` from frontmatter parse assertions (line 385)
- Update or remove `test_bad_review_status_value` test (line 837)
- Update all frontmatter strings in test fixtures (lines 383, 780, 808)

**`test_dashboard.py`:**
- Remove `review_status` from test fixture helper (lines 29, 32)
- Remove `review_status="approved"` from fixture creation (line 53)

**New tests to add:**
- Test that `_task_io.py` silently ignores `review_status` in old task files (forward-compatible reading)
- Test the migration mapping: given various `(status, review_status)` combinations, verify the upgrade produces the correct unified `status`
- Test that `compute_frontier()` behavior is unchanged after the field removal
- Test `--upgrade-status` dry-run and actual upgrade modes

## Results
