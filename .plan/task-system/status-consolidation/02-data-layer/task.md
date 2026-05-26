---
title: "Update core data layer: remove stale fields, add archived status"
status: implemented
review_status: implemented
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

All changes in [`_task_io.py`](skills/task-system/scripts/_task_io.py).

**Removed stale fields:**
- Deleted `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` constants ([`_task_io.py:20`](skills/task-system/scripts/_task_io.py#L20))
- Removed `review_status` and `integration_status` from `Task` dataclass ([`_task_io.py:24`](skills/task-system/scripts/_task_io.py#L24))
- `parse_task()` no longer reads these fields; silently ignores them if present in old files ([`_task_io.py:225`](skills/task-system/scripts/_task_io.py#L225))
- `write_task()` no longer writes these fields ([`_task_io.py:252`](skills/task-system/scripts/_task_io.py#L252))
- `serialize_frontmatter()` field_order no longer lists them ([`_task_io.py:165`](skills/task-system/scripts/_task_io.py#L165))
- `validate_frontmatter()` no longer validates them ([`_task_io.py:502`](skills/task-system/scripts/_task_io.py#L502))

**Added `archived` status:**
- Added to `VALID_STATUSES` tuple ([`_task_io.py:20`](skills/task-system/scripts/_task_io.py#L20))
- `compute_status()` filters out archived children before rollup; returns `archived` when all children are archived ([`_task_io.py:390`](skills/task-system/scripts/_task_io.py#L390))
- `_collect_frontier()` skips archived tasks (never on frontier) and treats archived dependencies as satisfied ([`_task_io.py:436`](skills/task-system/scripts/_task_io.py#L436))

**Forward compatibility verified:** Parsed the existing `.plan/` tree (60 tasks, many with old `review_status`/`integration_status` fields) successfully. All tasks parse without error; the stale fields are silently ignored.

**Behavioral verification:** 11 inline tests covering all changed code paths pass: VALID_STATUSES content, dataclass fields, compute_status with archived children (mixed, all-archived), compute_frontier with archived tasks and archived dependencies, serialize/validate without stale fields, effective_status delegation, and forward-compatible parsing of old frontmatter.
