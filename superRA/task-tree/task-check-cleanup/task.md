---
title: "task_check.py cleanup: collapse _walk_plan_tolerant"
status: not-started
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
