---
title: "Fix status and review_status consistency"
status: implemented
review_status: approved
integration_status: ~
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Fix two consistency bugs in the task status system:

1. **Status/review_status mismatch validation.** A task with `status: not-started` cannot have `review_status: approved`. Add validation to `_task_io.py` that enforces the logical ordering: `review_status` cannot advance past `status` (e.g., review cannot be `approved` if status is not at least `implemented`). Add a `--fix` mode to `task_update.py` that scans the tree and corrects mismatches.

2. **Dashboard shows review_status.** The dashboard template (`task_node.html`) currently shows only `effective_status()` which is derived from `status:`. Add a secondary badge or indicator showing `review_status` when it differs from `~`, so the user can see both implementation and review progress at a glance.

**Files to modify:**
- `skills/task-system/scripts/_task_io.py` — add `validate_status_consistency(task)` function
- `skills/task-system/scripts/task_update.py` — add `--fix` flag that corrects mismatches
- `skills/task-system/scripts/templates/task_node.html` — add review_status badge
- `skills/task-system/scripts/templates/base.html` — add CSS for review badge

**Validation:** Run the fix against the current `.plan/` tree and verify that `live-server` and `comments` parent tasks have their status corrected. Add a test to `test_task_system.py` for the validation logic.

## Results

### Implementation

1. **`validate_status_consistency(task)`** added to [`_task_io.py:556-592`](skills/task-system/scripts/_task_io.py#L556). Enforces:
   - `review_status` cannot advance past `~` unless `status >= implemented`
   - `integration_status` cannot advance past `~` unless `review_status == approved`
   - Integrated into `validate_frontmatter()` so it runs on every validation pass (hooks, `validate_plan()`).

2. **`--fix` mode** added to [`task_update.py:100-145`](skills/task-system/scripts/task_update.py#L100). Scans the full tree, corrects branch (non-leaf) task `status` fields to match their rolled-up value from children. After rolling status down, also resets `review_status` to `~` when the new status is below `implemented`, and resets `integration_status` to `~` when `review_status` is no longer `approved`. Prints warnings for leaf-level consistency issues it cannot auto-fix.

3. **Review-status badge** in [`task_node.html:31-33`](skills/task-system/scripts/templates/task_node.html#L31). Shows a secondary outlined badge "review: {status}" when `review_status != '~'`, visually distinct from the primary filled status badge.

4. **CSS for review badge** in [`base.html:274-281`](skills/task-system/scripts/templates/base.html#L274). Outlined style with color matching the status semantic (yellow for implemented, red for revise, green for approved).

5. **8 tests** in [`test_task_system.py`](skills/task-system/scripts/test_task_system.py) `TestStatusConsistency` class covering validation logic, fix mode for branches, no-change for leaves, review_status reset on status rolldown, and integration with `validate_plan`.

### Validation Against Live Tree

Running `--fix` against the actual `.plan/` tree (after prior status rollups) additionally corrected 2 tasks with `review_status > status` violations:
- `task-system/dashboard`: `review_status` reset from `approved` to `~` (status below `implemented`)
- `task-system/dashboard/live-server/comments/comment-ui`: `review_status` reset from `approved` to `~` (status below `implemented`)

A second `--fix` pass confirms zero remaining inconsistencies. The only remaining `validate_plan` warnings are unrelated `depends_on` path-format issues (relative `../` references).

