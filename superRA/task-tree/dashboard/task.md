---
title: "HTML Dashboard"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
tags: []
created: 2026-05-23
---

## Objective

Build `plan_dashboard.py`: generate self-contained HTML dashboard from `.plan/` tree. Single-page recursive expand/collapse where all tasks are visible at once with progressive disclosure. Tree, DAG (Mermaid), and Kanban views. Distinctive typography and professional palette. Dark/light mode.

## Results

The dashboard evolved well past the original single-file static HTML the Objective scopes. It is now a **FastAPI live server** that renders [base.html](../../../skills/task-tree/scripts/templates/base.html) plus htmx-swapped partials in a master-detail workspace, with a **standalone-mode render** of the same template for static export. The server-side machinery (routes, SSE broadcast, watcher lifecycle, idle monitor, Jinja render helpers, standalone build, CLI, background supervisor) lives in [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py).

The retired first cut (1014-line static template with a `__TASK_DATA_JSON__` blob and a three-tab Tree/DAG/Kanban shell) is gone; the matured architecture is summarized here and delivered across the child tasks:

- **[view-navigation](view-navigation/task.md)** — the master-detail workspace, sidebar tree, breadcrumb, DAG (Mermaid) and kanban surfaces, and client routing.
- **[unify-static-export](unify-static-export/task.md)** — one template (`base.html`) drives both the live server and the static export via a `window.STANDALONE` branch, replacing the separate static generator.
- **[self-contained-export](self-contained-export/task.md)** — the static export base64-embeds figures so a downloaded file is figure-portable offline.
- **[multi-worktree-serving](multi-worktree-serving/task.md)** — one server/port per repo resolves any worktree per request via `?wt=<wt_id>`; switching is client navigation, not a server-wide swap.
- **[serve-lifecycle](serve-lifecycle/task.md)** — background-by-default launch with idempotent reuse, idle self-exit, `stop`, and a loopback-default `--host` bind.

Preserved throughout: distinctive typography (Source Serif 4 + IBM Plex Mono via Google Fonts CDN), the warm parchment/ink palette with muted status tints, dark/light mode, progressive disclosure, the DAG/kanban views, and the XSS posture (JSON escaping, `textContent` for DOM writes, `html: false` on markdown-it with controlled rewrites).

**Design debt (recorded for a future extraction pass):** [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) has grown to ~2,190 lines mixing seven concerns (data layer/index, SSE broadcast, watcher lifecycle, idle monitor, Jinja render helpers, routes, standalone build, CLI, background supervisor). The background supervisor (~300 lines of PID/daemon logic) and the standalone build (~340 lines) have no FastAPI coupling and are clean extraction candidates, following the precedent of [dashboard_artifact_workflow.py](../../../skills/task-tree/scripts/dashboard_artifact_workflow.py).

