---
title: "HTML Dashboard"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
tags: []
script: skills/task-system/scripts/plan_dashboard.py
created: 2026-05-23
---

## Objective

Build `plan_dashboard.py`: generate self-contained HTML dashboard from `.plan/` tree. Single-page recursive expand/collapse where all tasks are visible at once with progressive disclosure. Tree, DAG (Mermaid), and Kanban views. Distinctive typography and professional palette. Dark/light mode.

## Results

### Key Findings
- 1014-line HTML template, single-page recursive design
- Typography: Source Serif 4 (display) + IBM Plex Mono (body/data) via Google Fonts CDN
- Warm parchment/ink palette with muted status tints
- Progressive disclosure: 3 levels — title row → children + section toggles → rendered markdown
- Tree connector lines via `border-left`, CSS transitions for expand/collapse
- DAG and Kanban views preserved as alternate views
- XSS: JSON escaping, textContent for DOM, `html: false` on markdown-it
- Task data embedded as JSON blob replacing `__TASK_DATA_JSON__` placeholder
