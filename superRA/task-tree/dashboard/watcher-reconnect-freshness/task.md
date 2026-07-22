---
title: "Fresh Dashboard State After Watcher Reconnect"
status: revise
depends_on: []
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
  ([test_dashboard.py:1240-1327](../../../../skills/task-tree/scripts/test_dashboard.py#L1240-L1327)).

### Result Protection

- The confirmed key result is fully protected by the existing pytest guards:
  the reconnect regression covers the offline edit, rebuilt cached objective,
  and client-observable `full-reload`; the watcher-start regression covers the
  no-duplicate live-watcher path; and the broadcast regression independently
  covers worktree isolation
  ([test_dashboard.py:1177-1193](../../../../skills/task-tree/scripts/test_dashboard.py#L1177-L1193),
  [test_dashboard.py:1240-1327](../../../../skills/task-tree/scripts/test_dashboard.py#L1240-L1327)).
- The guards satisfy the drift-test-quality checklist without another test:
  their names state the protected behavior, they run independently without a
  full pipeline or saved-output fixture, use exact deterministic assertions
  where no numerical tolerance applies, and follow the repository's pytest
  structure.
- Red-green verification is established by the implementation cycle: the two
  strengthened lifecycle guards failed against the cache-only implementation
  (missing queue event and reconnect timeout), then passed after the
  worktree-scoped startup broadcast was added. A fresh protection-stage run of
  the reconnect, no-duplicate, and isolation guards passed all 3 tests.

### Verification

- Verification passed: `test_dashboard.py` (308 tests) and the complete
  `skills/task-tree/scripts` suite (731 tests). Both runs reported only existing
  dependency and malformed-fixture warnings.

### Integration

- The watcher implementation already matches the host lifecycle and SSE
  patterns: it reuses the in-place worktree rebuild and scoped broadcast
  utilities, retains register-before-ensure ordering, and leaves bounded
  teardown unchanged. No code refactor was warranted.
- Project-doc audit covered root [README.md](../../../../README.md) and
  [CLAUDE.md](../../../../CLAUDE.md); both remain current, and no nearer module
  README or contributor guide exists for the changed files.

**Final diff self-check:** `git diff 2d4c8551629814cab303573322dfde1d26f2a318..HEAD`; surviving change classes are watcher-respawn cache refresh, worktree-scoped reconnect notification, lifecycle regressions, and the durable task record. The new approved task record and `skills/*` code/test hunks are retained because they directly implement and protect the reconnect-freshness objective; no scope-ambiguous or unjustified hunk remains.

## Revision Notes

- Researcher-approved maturation: merge this update task into `task-tree/dashboard`, preserve the protected reconnect-cache and client-refresh behavior as a short `## Results` subsection in that durable parent, and remove this child directory. This is a routine structural fold with no code-scope change.
