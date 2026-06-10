---
title: "HTML Dashboard"
status: revise
depends_on:
  - core-data-layer
  - cli-scripts
tags: []
script: skills/task-tree/scripts/plan_dashboard.py
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

## Review Notes

1. **MAJOR** — `## Results` describes the retired first implementation, not the shipped system: the "1014-line HTML template", the `__TASK_DATA_JSON__` placeholder (zero hits in `skills/task-tree/scripts/`), and the three-tab Tree/DAG/Kanban shell are all gone. The current architecture is a FastAPI live server rendering the 4,358-line [base.html](../../../skills/task-tree/scripts/templates/base.html) + partials in a master-detail workspace, with a standalone-mode render for static export ([plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py)). This is the highest task of the dashboard subtree — where the contract's Stage-2 matured narrative should live — and per the stale-content checklist ("Results sections now incorporated into the current approach") it must be rewritten in place to summarize the current server + standalone architecture, with links down to the child tasks ([view-navigation](view-navigation/task.md), [unify-static-export](unify-static-export/task.md), [multi-worktree-serving](multi-worktree-serving/task.md), [serve-lifecycle](serve-lifecycle/task.md), [self-contained-export](self-contained-export/task.md)).
2. **MAJOR** — frontmatter carries `script: skills/task-tree/scripts/plan_dashboard.py` on a branch task with ~17 children; the task-file contract states branch tasks do not carry `script`/`input`/`output` (those belong on leaf tasks). Remove the field (orchestrator-owned change; flagging for the orchestrator since `script` is fixed at planning time).
3. **MINOR** — design debt worth recording in the rewritten Results: [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) has grown to 2,186 lines mixing seven concerns (data layer/index, SSE broadcast, watcher lifecycle, idle monitor, Jinja render helpers, routes, standalone export build, CLI, background process supervisor). The supervisor (~300 lines of PID/daemon logic) and the standalone build (~340 lines) have no FastAPI coupling and are clean extraction candidates, following the precedent of [dashboard_artifact_workflow.py](../../../skills/task-tree/scripts/dashboard_artifact_workflow.py).
