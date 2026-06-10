---
title: "FastAPI server and task data layer"
status: approved
depends_on: []
tags: []
created: 2026-05-24
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

## Results

Implemented in [`plan_dashboard.py`](skills/task-tree/scripts/plan_dashboard.py).

**Routes implemented:**
- `GET /` — renders `base.html` with `root_task`, `all_tasks`, `project_root`
- `GET /task/{path:path}` — renders `task_children.html` fragment for htmx expand
- `GET /events` — SSE endpoint with `text/event-stream`, per-client `asyncio.Queue` broadcast
- `GET /files/{path:path}` — serves project files for image embeds (path-traversal guarded)
- `POST /api/task/{path:path}/comment` — create comment
- `GET /api/task/{path:path}/comments` — list comments
- `PATCH /api/task/{path:path}/comment/{comment_id}` — toggle resolved
- `DELETE /api/task/{path:path}/comment/{comment_id}` — delete comment

**Data layer:**
- `rebuild_tree()` — full re-walk, builds `_task_index: dict[str, Task]`
- `rebuild_task(path)` — re-parse single task.md, patch in-tree, update index
- `_find_task(path)` — O(1) lookup

**Note:** Comment routes use `/api/` prefix instead of the spec's `/task/{path}/comments` to avoid ambiguity with FastAPI's greedy `{path:path}` parameter. The catch-all `/task/{path:path}` route is registered last.

## Decisions

- Comment routes moved to `/api/task/...` prefix. The `{path:path}` parameter in FastAPI is greedy and would match `/task/server/comments` as `path="server/comments"` before the more specific comment route. Using an `/api/` prefix avoids this ambiguity cleanly.
- `_comments.py` import is wrapped in try/except so the server works even if the comments module is not yet available.
- Jinja2 environment is lazy-initialized (not at import time) so the module can be imported for testing without templates present.
