---
title: "Update dashboard rendering"
status: not-started
review_status: ~
integration_status: ~
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
