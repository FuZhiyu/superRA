---
title: "FastAPI server and task data layer"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Build the FastAPI application that serves the dashboard. Reuse the existing task-tree parser from `plan_dashboard.py` (or `plan_task_io.py`).

**Routes:**
- `GET /` — serves the full dashboard page (base template + top-level task skeleton)
- `GET /task/{path:path}` — returns an HTML fragment for a task node and its direct children (htmx partial)
- `GET /events` — SSE endpoint for live updates (see `live-reload` subtask)
- `GET /static/{file}` — serves shared CSS/JS if extracted (optional)

**Data layer:**
- On startup, walk `.plan/` and parse `task.md` files into the existing task-tree data structure
- Keep an in-memory task index (`dict[path, TaskNode]`) for fast lookups
- On file-change events (from the watcher), re-parse only the changed `task.md` and update the index
- Parse task body sections (objective, results, decisions, review notes) for section-level rendering

**Key constraints:**
- The server module should be importable and runnable via `uvicorn` programmatically
- Reuse existing `plan_task_io.py` parsing logic — don't duplicate the YAML frontmatter parser
- Task tree root is configurable (default: `.plan/` in cwd) so subtrees can be served independently
