---
title: "Update core data layer: remove stale fields, add archived status"
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

Update `_task_io.py` to remove `review_status` and `integration_status` from the data model, and add the `archived` status. This is the foundation all other tasks depend on.

### Remove stale fields

1. **Remove `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` constants.** Remove their validation in `parse_task()`.
2. **Remove `review_status` and `integration_status` from `Task` dataclass.** Remove the fields and their defaults.
3. **Update `parse_frontmatter` / `parse_task`** — stop reading these fields from YAML. If encountered in an old file, ignore silently (forward-compatible reading).
4. **Update `serialize_frontmatter` / `write_task`** — remove both fields from `field_order` and from `write_task`.

### Add `archived` status

5. **Add `archived` to `VALID_STATUSES`** — `("not-started", "in-progress", "implemented", "revise", "approved", "archived")`.
6. **Update `compute_status()`** — filter out archived children before computing rollup. A parent with 2 approved + 1 archived = `approved`.
7. **Update `compute_frontier()`** — skip archived tasks (they should never appear on the frontier). Also: archived tasks don't block dependents — treat an archived dependency as satisfied.

### Verify

Confirm that `effective_status()` still works correctly with these changes — it delegates to `compute_status()` for branch tasks and reads `status` directly for leaves.

## Results
