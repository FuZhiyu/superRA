---
title: "Path Containment for Task Creation"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Harden `skills/task-tree/scripts/task_create.py` so task creation cannot write outside the selected task root.

### Context

PR #29 review flagged that `create_task()` builds `task_dir = plan_root / task_path` without normalizing or checking containment. Inputs such as `--path ../escaped` can create `task.md` outside the task tree. This violates the task-tree boundary and should be rejected before any filesystem mutation.

### Scope

- Resolve `plan_root` and the requested task directory before creating directories or files.
- Reject task paths that escape the resolved task root, including `..` traversal and absolute paths outside the root.
- Keep normal relative task paths working, including nested paths with existing parent tasks.
- Ensure dependency validation still checks only sibling task directories inside the contained parent directory.
- Add regression tests in `skills/task-tree/scripts/test_task_tree.py` for traversal, absolute-path rejection, and a valid nested create.

### Validation

- The new tests fail on the current implementation and pass after the containment fix.
- Existing task-tree tests continue to pass for task creation, dependency validation, and serve-script generation.
- The implementation does not broaden `task_create.py` into a general path-sanitization framework; keep the containment check local and explicit.

## Results

### Fix

Added containment check in [`task_create.py`](skills/task-tree/scripts/task_create.py) inside `create_task()`, immediately after `task_dir` is constructed and before any filesystem read or write. The check resolves both `plan_root` and `task_dir` via `.resolve()`, then calls `resolved_task.relative_to(resolved_root)`. On `ValueError` it prints an error and calls `sys.exit(1)`.

The check is 8 lines, local to `create_task()`, and adds no new imports or helpers. It covers both `..` traversal (e.g. `../escaped`) and absolute paths outside the root, because both fail `relative_to` after resolution.

### Tests

Added three tests to `TestTaskCreate` in [`test_task_tree.py`](skills/task-tree/scripts/test_task_tree.py):

- `test_traversal_rejected` — `--path ../escaped` exits 1 and creates no file.
- `test_absolute_path_outside_root_rejected` — absolute path outside root exits 1 and creates no file.
- `test_valid_nested_create_succeeds` — a valid nested path (`04-parent/01-child`) succeeds.

### Verification

```
uv run pytest skills/task-tree/scripts/test_task_tree.py -v
# 208 passed in 2.62s
```

All three new tests were confirmed to fail on the pre-fix code (the `../escaped` case created the file successfully) and pass after the fix.
