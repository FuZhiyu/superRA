---
title: "Apply migration to this worktree's .plan/"
status: approved
depends_on:
  - 04-migration-tooling
  - 08-tests
tags:
  - migration
script: 
input: []
output: []
created: 2026-05-26
---

## Objective

Run the upgrade tool on the dashboard-redesign worktree's `.plan/` directory to remove `review_status` from all existing task files.

1. Run with `--dry-run` first and verify the migration mapping produces correct results for every task.
2. Apply the migration.
3. Run `task_query.py --tree` to confirm the tree renders correctly with no errors.
4. Run the full test suite to confirm nothing is broken.
5. Regenerate the dashboard and confirm it renders correctly.
6. Commit the migrated task files as a single atomic commit.

This task also covers migrating any other active `.plan/` directories in other worktrees, if they exist and are relevant.

## Results

Ran `plan_migrate.py --upgrade-status` on `.plan/` in the `dashboard-redesign` worktree.

**Dry-run verification:** 59 task files identified for migration. Key migration decisions confirmed correct:
- Tasks where `review_status` (or `integration_status`) was more advanced than `status` were promoted (e.g., `status=implemented` + `review_status=approved` -> `status=approved`).
- Tasks with no override stayed at their current status level.
- All `review_status` and `integration_status` frontmatter fields stripped.

**Post-migration verification:**
- `task_query.py --tree` renders correctly with proper status indicators.
- Full test suite: 188/188 tests pass ([test_task_tree.py](skills/task-tree/scripts/test_task_tree.py), [test_dashboard.py](skills/task-tree/scripts/test_dashboard.py)).
- `task_check.py --category status`: zero findings. No stale fields remain.
- Dashboard regenerated at [.plan/dashboard.html](.plan/dashboard.html).

**Pre-existing issues (not introduced by this migration):** 15 dependency-resolution errors (relative `../` paths in `live-server/` subtree) and 7 rollup mismatches where parent `status` was not auto-updated to match children. These are structural issues from earlier tasks.