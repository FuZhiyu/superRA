---
title: "Fresh Dashboard State After Watcher Reconnect"
status: revise
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

## Review Notes

1. **MAJOR** — Reconnect refreshes only the server-side cache; it never tells the
   reconnected dashboard to replace content that it rendered before the watcher
   restarted. `_ensure_watcher` rebuilds state and immediately starts the watcher
   without broadcasting or returning any refresh signal
   ([plan_dashboard.py:526-544](../../../../skills/task-tree/scripts/plan_dashboard.py#L526-L544)),
   while the SSE generator's first and only startup message is a heartbeat
   ([plan_dashboard.py:1162-1197](../../../../skills/task-tree/scripts/plan_dashboard.py#L1162-L1197)).
   The browser refreshes its visible task regions on a `full-reload` event
   ([dashboard.js:2592-2601](../../../../skills/task-tree/scripts/templates/dashboard.js#L2592-L2601)),
   so an already-open page whose SSE connection drops, is edited while its
   watcher is stopped, and then auto-reconnects remains visibly stale until a
   later filesystem event. The regression asserts the private cache after
   consuming that heartbeat, not refreshed content delivered to the client
   ([test_dashboard.py:1293-1301](../../../../skills/task-tree/scripts/test_dashboard.py#L1293-L1301)).
   Make watcher restart produce a client-observable refresh (without losing it
   across the preserved register-before-ensure ordering), and make the regression
   assert the reconnecting stream/UI receives the edited content without a later
   filesystem event. Cover the already-open-page reconnect path, not only a fresh
   route read from the newly rebuilt cache.
