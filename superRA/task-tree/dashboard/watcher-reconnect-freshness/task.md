---
title: "Fresh Dashboard State After Watcher Reconnect"
status: not-started
depends_on:  []
---

## Objective

Ensure a dashboard worktree rebuilds cached task-tree state whenever its stopped watcher is started again, so edits made with no connected client appear immediately on reconnect. Add a regression test that seeds cached state, stops the watcher, edits task.md on disk, reconnects, and verifies the refreshed content without another filesystem event. Preserve the existing register-before-ensure ordering, per-worktree isolation, and bounded cooperative teardown behavior. Scope implementation to skills/task-tree/scripts/plan_dashboard.py and its dashboard tests; generated artifacts: none.

## Results
