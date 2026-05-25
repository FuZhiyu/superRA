---
title: "Live Server Dashboard"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - ../
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Replace the static single-file HTML dashboard with a live-updating server-based dashboard. Stack: FastAPI + Jinja2 + htmx + watchfiles, all resolved at runtime via `uv run --with`.

**Design decisions (from brainstorm):**
- Dynamic loading: only the expanded subtree's data is fetched, not the entire tree
- Single-page feel: htmx swaps HTML fragments in-place on expand/collapse, no full page reloads
- Live reload: watchfiles monitors `.plan/` for changes, pushes SSE events, htmx swaps updated fragments
- Zero install friction: `uv run --with fastapi,uvicorn,jinja2,watchfiles` resolves deps at runtime
- Preserve existing features: tree view, DAG (Mermaid), kanban, dark/light mode, search/filter, status summary bar

**Tech stack:**
- `fastapi` + `uvicorn` — async HTTP server
- `jinja2` — server-side HTML templates
- `watchfiles` — OS-native filesystem watcher (FSEvents/inotify)
- `htmx` (CDN) — dynamic HTML fragment swapping, SSE support
- `mermaid` (CDN) — DAG rendering
- `markdown-it` (CDN) — markdown rendering in task bodies

**Architecture:**
- Server reads `.plan/` tree on startup, serves HTML fragments per task node
- Expand a task → `hx-get="/task/<path>"` fetches rendered children
- SSE endpoint `/events` pushes `task-updated` events when watchfiles detects changes
- Each task node declares `sse-swap="task:<path>"` to auto-update on change
