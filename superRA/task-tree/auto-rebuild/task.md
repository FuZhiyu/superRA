---
title: "Auto-Rebuild Dashboard"
status: archived
depends_on:
  - core-data-layer
tags: []
created: 2026-05-23
---

## Objective

~~Originally~~ implemented auto-rebuild: add a lazy-import `generate_dashboard(plan_root)` call wrapped in `try/except Exception: pass` at the end of every mutating CLI function. The feature was built and then deliberately removed.

**Design reversal (recorded here per the Stale Content Checklist):** Auto-rebuild was removed in favor of export-only dashboards. Today no mutation script imports `generate_dashboard`; the dashboard is produced only on explicit `superra dashboard export`. This is enforced by `TestNoAutoRebuild` (`test_create_does_not_generate_dashboard`, `test_update_does_not_touch_existing_dashboard`) in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py) and stated in [task_hook.py](../../../skills/task-tree/scripts/task_hook.py): "It does not write the dashboard; a static dashboard is produced only on explicit `superra dashboard export`."

This task is archived because the feature it describes no longer exists and the test suite actively forbids it.

## Results

Feature was built (auto-rebuild in all 5 mutation scripts, 7 call sites total), then removed. The current behavior — export-only dashboard — is the intentional design. No implementation artifact to maintain.

