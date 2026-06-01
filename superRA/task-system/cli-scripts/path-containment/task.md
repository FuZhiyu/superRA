---
title: "Path Containment for Task Creation"
status: not-started
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Harden `skills/task-system/scripts/task_create.py` so task creation cannot write outside the selected task root.

### Context

PR #29 review flagged that `create_task()` builds `task_dir = plan_root / task_path` without normalizing or checking containment. Inputs such as `--path ../escaped` can create `task.md` outside the task tree. This violates the task-system boundary and should be rejected before any filesystem mutation.

### Scope

- Resolve `plan_root` and the requested task directory before creating directories or files.
- Reject task paths that escape the resolved task root, including `..` traversal and absolute paths outside the root.
- Keep normal relative task paths working, including nested paths with existing parent tasks.
- Ensure dependency validation still checks only sibling task directories inside the contained parent directory.
- Add regression tests in `skills/task-system/scripts/test_task_system.py` for traversal, absolute-path rejection, and a valid nested create.

### Validation

- The new tests fail on the current implementation and pass after the containment fix.
- Existing task-system tests continue to pass for task creation, dependency validation, and serve-script generation.
- The implementation does not broaden `task_create.py` into a general path-sanitization framework; keep the containment check local and explicit.

## Results

