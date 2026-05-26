---
title: "Update dashboard rendering"
status: implemented
depends_on:
  - 02-data-layer
tags: [code]
script: skills/task-system/scripts/plan_dashboard.py
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Verify and update `plan_dashboard.py` and the live-server dashboard for the unified status model.

The dashboard already uses `effective_status()` for rendering, so this task may be mostly verification. Specifically:

- Confirm neither `review_status` nor `integration_status` appear in the dashboard code, JSON data layer, or templates. If any traces exist, remove them.
- Confirm the kanban and tree views render correctly with only `status`.
- Add `archived` to the status color/badge mapping (e.g., a distinct color or icon so archived tasks are visually distinguishable).
- Confirm `archived` tasks are handled sensibly in all views (tree, DAG, kanban) — they should appear but be visually muted or in a separate kanban column.

## Results

### Stale field cleanup

**Dashboard code** ([plan_dashboard.py](skills/task-system/scripts/plan_dashboard.py)) and **templates** ([base.html](skills/task-system/scripts/templates/base.html), [kanban.html](skills/task-system/scripts/templates/kanban.html), [dag.html](skills/task-system/scripts/templates/dag.html), [summary_bar.html](skills/task-system/scripts/templates/summary_bar.html), [task_node.html](skills/task-system/scripts/templates/task_node.html)) — no traces of `review_status` or `integration_status` found. The data layer (`_task_io.py`) and JSON serialization (`task_query.py:tree_to_json`) were already clean.

**Test helper** ([test_dashboard.py:39](skills/task-system/scripts/test_dashboard.py#L39)) — `_write_task_md` previously wrote `review_status` and `integration_status` fields. Removed both from the helper and the fixture that passed `review_status="approved"`.

### Archived status support

Added `archived` handling across all views:

- **CSS badge** ([base.html:267](skills/task-system/scripts/templates/base.html#L267), [plan_dashboard.py:821](skills/task-system/scripts/plan_dashboard.py#L821)): gray/muted `.badge-archived` class with `opacity: 0.7`, using dedicated `--st-arch` / `--st-arch-t` color tokens for both light and dark themes.
- **Status filter dropdown** ([base.html:579](skills/task-system/scripts/templates/base.html#L579), [plan_dashboard.py:1079](skills/task-system/scripts/plan_dashboard.py#L1079)): added `archived` option.
- **Kanban** ([kanban.html:14](skills/task-system/scripts/templates/kanban.html#L14), [plan_dashboard.py:1482](skills/task-system/scripts/plan_dashboard.py#L1482)): added Archived column (6 columns total).
- **DAG** ([dag.html:13](skills/task-system/scripts/templates/dag.html#L13), [plan_dashboard.py:1444](skills/task-system/scripts/plan_dashboard.py#L1444)): added `#f5f5f5` (light gray) color for archived nodes.
- **Summary bar** ([summary_bar.html](skills/task-system/scripts/templates/summary_bar.html)): archived leaves excluded from task count and progress denominator; archived count displayed separately when > 0. Static HTML version updated identically.
- **Tree view**: archived tasks render with the muted badge via the existing `badge-{{ eff_status }}` mechanism in `task_node.html` — no template change needed.

### Test updates

- Kanban column count assertions updated from 5 to 6 in both `test_kanban_returns_6_columns` and `test_kanban_has_6_status_columns`.
- All 57 dashboard tests pass. All 102 main task system tests pass.
