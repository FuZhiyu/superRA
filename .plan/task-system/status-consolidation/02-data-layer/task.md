---
title: "Update core data layer to remove review_status and integration_status"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 01-design
tags: [code]
script: skills/task-system/scripts/_task_io.py
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update `_task_io.py` to remove both `review_status` and `integration_status` from the data model. This is the foundation all other tasks depend on.

Changes:

1. **Remove `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` constants** (lines 20-21). Remove their validation in `parse_task()`.
2. **Remove `review_status` and `integration_status` from `Task` dataclass** (lines 32-33). Remove the fields and their defaults.
3. **Update `parse_frontmatter` / `parse_task`** — stop reading these fields from YAML. If encountered in an old file, ignore silently (forward-compatible reading).
4. **Update `serialize_frontmatter` / `write_task`** — remove both fields from `field_order` and from `write_task`.
5. **Update frontmatter validation** — remove validation for both fields.

Verify: `compute_status()` and `compute_frontier()` already ignore both fields — confirm no changes needed.

## Results
