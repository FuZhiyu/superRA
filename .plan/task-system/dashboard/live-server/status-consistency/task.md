---
title: "Fix status and review_status consistency"
status: not-started
review_status: ~
integration_status: ~
depends_on:  []
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

