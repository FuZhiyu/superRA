---
title: "task_check.py cleanup: collapse _walk_plan_tolerant"
status: approved
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Clean up `task_check.py` after the parser-robustness lenient-parse change. `_walk_plan_tolerant` ([task_check.py](../../../skills/task-tree/scripts/task_check.py)) wraps `parse_task` in `try/except ValueError` to survive the old hard-raise on invalid status. Now that `parse_task` is lenient (warns and preserves the raw status), that `ValueError` branch is dead for the status case.

Two issues to address:

1. Collapse `_walk_plan_tolerant` to a plain `walk_plan` call since the `ValueError` guard is no longer needed for status parsing.
2. Account for the decode-error path before collapsing: `UnicodeDecodeError` is a `ValueError` subclass, and the recovery path in `_walk_plan_tolerant` re-runs `read_text(encoding="utf-8")`, which re-raises and escapes the handler. Since `_walk_children` now catches `(OSError, UnicodeDecodeError)` and warns+skips, the `task check` tolerant walk can simply delegate to `walk_plan` directly.

**Scope:** touch only `skills/task-tree/scripts/task_check.py` and `skills/task-tree/scripts/test_task_tree.py` (update tests that exercise the tolerant-walk path).

## Results

Collapsed `_walk_plan_tolerant` into a direct `walk_plan` call in [task_check.py](../../../skills/task-tree/scripts/task_check.py).

**Changes:**

- [task_check.py:24-32](../../../skills/task-tree/scripts/task_check.py#L24-L32): Swapped `parse_task` for `walk_plan` in the `_task_io` import; removed `parse_task`.
- [task_check.py:370-388](../../../skills/task-tree/scripts/task_check.py#L370-L388): Replaced `_walk_plan_tolerant(plan_root)` call with `walk_plan(plan_root)` in `run_checks`; deleted the entire `_walk_plan_tolerant` function (~75 lines including its two inner helpers).
- [test_task_tree.py:3915](../../../skills/task-tree/scripts/test_task_tree.py#L3915): Updated `test_task_check_paths_root_relative_on_forest` to call `_task_io.walk_plan(forest_root)` instead of the removed `task_check._walk_plan_tolerant(forest_root)`.

**Rationale for deletion:** `_walk_plan_tolerant` existed to survive `ValueError` raised by `parse_task` on invalid status values. Since the parser-robustness change made `parse_task` lenient (warns instead of raises for unknown status), the `ValueError` branch was dead for the status case. The `UnicodeDecodeError` recovery path was also broken: it re-ran `read_text(encoding="utf-8")` which would re-raise, escaping the handler. `_task_io._walk_children` now catches `(OSError, UnicodeDecodeError)` and warns+skips, making the tolerant walk redundant.

**Verification:** Test suite ran 646 passed, 2 skipped (matches baseline exactly).
