---
title: "Update core data layer to remove review_status"
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

Update `_task_io.py` to remove the `review_status` field from the data model. This is the foundation all other tasks depend on.

Changes:

1. **Remove `VALID_REVIEW_STATUSES` constant** (line 20). Validation of `review_status` in `parse_task()` (lines 227-232) is removed.
2. **Remove `review_status` from `Task` dataclass** (line 32). Remove the field and its default.
3. **Update `parse_frontmatter` / `parse_task`** — stop reading `review_status` from YAML. If encountered in an old file, ignore silently (forward-compatible reading).
4. **Update `serialize_frontmatter` / `write_task`** — remove `review_status` from `field_order` (line 166) and from `write_task` (line 267).
5. **Update frontmatter validation** (line 512-515 range) — remove `review_status` validation.

The `integration_status` field and its constant `VALID_INTEGRATION_STATUSES` stay unchanged.

Verify: `compute_status()` and `compute_frontier()` already ignore `review_status` — confirm no changes needed.

## Results
