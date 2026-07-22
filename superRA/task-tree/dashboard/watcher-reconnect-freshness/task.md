---
title: "Fresh Dashboard State After Watcher Reconnect"
status: approved
depends_on:  []
---

## Objective

Ensure a dashboard worktree rebuilds cached task-tree state whenever its stopped watcher is started again, so edits made with no connected client appear immediately on reconnect. Add a regression test that seeds cached state, stops the watcher, edits task.md on disk, reconnects, and verifies the refreshed content without another filesystem event. Preserve the existing register-before-ensure ordering, per-worktree isolation, and bounded cooperative teardown behavior. Scope implementation to skills/task-tree/scripts/plan_dashboard.py and its dashboard tests; generated artifacts: none.

## Results

- Watcher startup now rebuilds cached worktree state and emits a worktree-scoped
  `full-reload` only on the path that spawns a watcher. Because `/events`
  registers the reconnecting queue before calling `_ensure_watcher`, the client
  receives the refresh after its initial heartbeat; the live-watcher fast path
  returns without a duplicate event, and teardown is unchanged
  ([plan_dashboard.py:505-546](../../../../skills/task-tree/scripts/plan_dashboard.py#L505-L546)).
- The reconnect regression now seeds cached state, stops the watcher, edits
  `task.md` while disconnected, reconnects through `/events`, and asserts both
  the refreshed objective and the `full-reload` delivered on that stream. The
  watcher-start test also verifies a second ensure emits no duplicate refresh
  ([test_dashboard.py:1229-1316](../../../../skills/task-tree/scripts/test_dashboard.py#L1229-L1316)).
- Verification passed: `test_dashboard.py` (307 tests) and the complete
  `skills/task-tree/scripts` suite (730 tests). Both runs reported only existing
  dependency and malformed-fixture warnings.
