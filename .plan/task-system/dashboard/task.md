---
title: "HTML Dashboard"
status: in-progress
review_status: implemented
integration_status: ~
depends_on:
  - core-data-layer
  - cli-scripts
tags: []
script: skills/task-system/scripts/plan_dashboard.py
created: 2026-05-23
updated: 2026-05-26
---

## Objective

Build `plan_dashboard.py`: a live-updating server-based dashboard for `.plan/` task trees. FastAPI + Jinja2 + htmx architecture with SSE hot-reload — the browser auto-updates when task files change. Tree, DAG (Mermaid), and Kanban views with progressive disclosure (expand/collapse). Distinctive typography and professional palette. Dark/light mode.

## Results

### Key Findings
- Live server: FastAPI + Jinja2 templates + htmx fragment swapping + watchfiles SSE
- Typography: Source Serif 4 (display) + IBM Plex Mono (body/data) via Google Fonts CDN
- Warm parchment/ink palette with muted status tints
- Progressive disclosure: expand a task node → `hx-get` fetches rendered children as HTML fragments
- Live reload: watchfiles monitors `.plan/`, pushes SSE events, htmx swaps updated fragments
- DAG and Kanban views preserved as alternate views
- Zero install friction: `uv run --with fastapi,uvicorn,jinja2,watchfiles` resolves deps at runtime
- Port derived deterministically from plan root path (8100–8999) for multi-worktree support
