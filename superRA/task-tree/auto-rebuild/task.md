---
title: "Auto-Rebuild Dashboard"
status: revise
depends_on:
  - core-data-layer
tags: []
created: 2026-05-23
---

## Objective

Add a lazy-import `generate_dashboard(plan_root)` call wrapped in `try/except Exception: pass` at the end of every mutating CLI function (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`). Best-effort — never blocks the primary mutation.

## Results

### Key Findings
- Auto-rebuild in all 5 mutation scripts (7 call sites total, including both branches of `task_link`)
- Early-return no-op paths correctly skip rebuild
- Adds ~0.1s per CLI call on a typical plan tree

## Review Notes

1. **CRITICAL** — [task_hook.py:11](../../../skills/task-tree/scripts/task_hook.py#L11), [test_task_tree.py:1705](../../../skills/task-tree/scripts/test_task_tree.py#L1705) — This entire task describes a feature that was deliberately removed but the task still asserts it as delivered. The Objective and Results claim auto-rebuild call sites in all 5 mutation scripts; today no mutation script imports `generate_dashboard` (it exists only inside [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py#L1665)), `task_hook.py` states "It does not write the dashboard; a static dashboard is produced only on explicit `superra dashboard export`", and `TestNoAutoRebuild` locks in the opposite behavior (`test_create_does_not_generate_dashboard`, `test_update_does_not_touch_existing_dashboard`). An approved task asserting behavior the test suite explicitly forbids misleads every agent reading this subtree. Fix: rewrite this task in place to record the design reversal (auto-rebuild built, then removed in favor of export-only dashboards) with a link to the removing change — or archive it with that note — per the task-file contract's Stale Content Checklist.
