---
title: "Apply migration to this worktree's .plan/"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 04-migration-tooling
  - 08-tests
tags: [migration]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
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
