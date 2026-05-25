---
title: "Fix status and review_status consistency"
status: implemented
review_status: implemented
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

## Review Notes

1. **[MAJOR]** `--fix` mode introduces new consistency violations. When a branch task has `review_status: approved` and `status: approved`, rolling status down to `in-progress` (from children) creates a `review_status > status` violation — the very rule this task implements. Evidence: [task_update.py:117-122](skills/task-system/scripts/task_update.py#L117) changes `status` without checking or adjusting `review_status`; running `validate_plan` after `--fix` reports 2 new violations (`task-system/dashboard` and `comments/comment-ui`). Fix: after setting `task.status = rolled_up`, also reset `review_status` to `~` if the new status is below `implemented` (since review cannot logically advance past status), or at minimum skip the status rolldown when it would introduce a review_status inconsistency and emit a specific warning explaining why.
   → implemented: after rolling status down, `fix_status_consistency()` now resets `review_status` to `~` when new status < `implemented`, and resets `integration_status` to `~` when `review_status` != `approved`. Added test `test_fix_mode_resets_review_status_when_status_rolled_down`. Re-ran `--fix` against live tree — zero remaining violations. ([task_update.py:126-137](skills/task-system/scripts/task_update.py#L126), [test_task_system.py:1331-1362](skills/task-system/scripts/test_task_system.py#L1331))

2. **[MINOR]** Review badge CSS committed under wrong task. The `.badge-review` CSS in `base.html` was committed in the math-rendering commit (b76518b) rather than the status-consistency commit (511b8ac). Functionally correct (both are in the same branch), but the status-consistency commit's `task_node.html` references CSS classes that were introduced by a different task's commit. No action needed — noting for commit hygiene only.
   → orchestrator: accepted as noted, no action required — both commits land in the same PR.
