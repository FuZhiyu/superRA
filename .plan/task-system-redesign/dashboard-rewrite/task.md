---
title: "Dashboard Rewrite"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - data-model
  - cli-format
tags: []
script: skills/task-system/scripts/plan_dashboard.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Complete rewrite of `DASHBOARD_HTML` in `plan_dashboard.py`. Replace sidebar/detail layout with single-page recursive expand/collapse where all tasks are visible at once. Use `frontend-design` skill for distinctive typography and visual design.

## Results

### Key Findings
- 1014-line HTML template (up from 469), single-page recursive design
- Typography: Source Serif 4 (display) + IBM Plex Mono (body/data) via Google Fonts CDN
- Warm parchment/ink palette with muted status tints
- Progressive disclosure: 3 levels — title row → children + section toggles → rendered markdown
- Tree connector lines via `border-left`, CSS transitions for expand/collapse
- DAG (Mermaid) and Kanban views preserved as alternate views
- XSS: JSON escaping, textContent for DOM, `html: false` on markdown-it
