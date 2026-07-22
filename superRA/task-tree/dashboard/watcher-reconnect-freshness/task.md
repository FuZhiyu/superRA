---
title: "Fresh Dashboard State After Watcher Reconnect"
status: implemented
depends_on:  []
---

## Objective

Ensure a dashboard worktree rebuilds cached task-tree state whenever its stopped watcher is started again, so edits made with no connected client appear immediately on reconnect. Add a regression test that seeds cached state, stops the watcher, edits task.md on disk, reconnects, and verifies the refreshed content without another filesystem event. Preserve the existing register-before-ensure ordering, per-worktree isolation, and bounded cooperative teardown behavior. Scope implementation to skills/task-tree/scripts/plan_dashboard.py and its dashboard tests; generated artifacts: none.

## Results

- Watcher startup now rebuilds the cached worktree state only on the path that
  spawns a new watcher. This captures disk edits made while no client was
  connected while leaving the live-watcher fast path, per-worktree lock, fresh
  stop event, and cooperative teardown unchanged
  ([plan_dashboard.py:526-544](../../../../skills/task-tree/scripts/plan_dashboard.py#L526-L544)).
- Added a reconnect regression that seeds cached state, starts and stops the
  watcher, edits `task.md` while disconnected, reconnects through `/events`,
  verifies the cached objective is refreshed before the initial heartbeat, and
  confirms stream closure still removes the watcher
  ([test_dashboard.py:1265-1308](../../../../skills/task-tree/scripts/test_dashboard.py#L1265-L1308)).
- Verification passed: `test_dashboard.py` (307 tests) and the complete
  `skills/task-tree/scripts` suite (730 tests). Both runs reported only existing
  dependency and malformed-fixture warnings.
