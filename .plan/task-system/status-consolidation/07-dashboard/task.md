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

Update `plan_dashboard.py` and the live-server dashboard to stop rendering `review_status` as a separate field.

- Remove `review_status` from the JSON data embedded in the static dashboard HTML
- Remove `review_status` from the live-server's task data layer
- The kanban and tree views should continue using `effective_status()` which already reads only `status` — confirm no changes needed there
- If the dashboard currently shows `review_status` as a separate badge or column, remove it

The `integration_status` display stays unchanged.

## Results
