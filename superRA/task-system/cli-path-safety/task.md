---
title: "CLI Path-Containment Safety"
status: not-started
depends_on:
  - cli-scripts
tags: []
created: 2026-06-01
---

## Objective

Reject task paths that escape the plan root in `skills/task-system/scripts/task_create.py`, resolving the PR #29 Codex P1 finding, and audit sibling CLI scripts for the same gap.

### Context

PR #29 review flagged that `create_task` builds `task_dir = plan_root / task_path` (around `task_create.py:96`) with no normalization or containment check before `task_dir.mkdir()` and the `task.md` write. A `--path ../escaped` input therefore creates and writes files outside the task tree, breaking the task-system boundary and allowing accidental or malicious writes to sibling directories from ordinary CLI usage.

### Scope

- In `task_create.py`, before any filesystem mutation, resolve `task_dir` and verify it is contained under the resolved `plan_root`; exit with a clear error (matching the existing `Error:` stderr style) when it is not. Keep the existing duplicate-directory and parent-exists checks.
- Audit the other path-taking CLI scripts that accept a relative task path — at least `task_rename.py` and `task_link.py`, plus any other script that joins user input onto `plan_root` — and apply the same containment guard, or document why a given script is already safe.
- Place the containment check in shared internals (`_task_io.py`) if more than one script needs it, rather than duplicating the logic per script.

### Validation

- A `task_create.py` test proves `--path ../escaped` (and an absolute path) is rejected before any directory is created or file written, while normal nested paths still succeed.
- Sibling-script audit is recorded in `## Results`: which scripts were guarded, which were already safe and why.
- `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py` passes.

## Results

