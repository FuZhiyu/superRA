---
title: "Live Server Dashboard"
status: revise
depends_on: []
tags: []
created: 2026-05-24
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

## Results

### Fixes

Single-bug fixes folded in from their former standalone subtasks during tree consolidation (full detail in git history at the cited commits):

- **Section order + HTML escaping** — unified `task_node.html` section rendering to preserve document order; added `| safe` on template content (`19da922`).
- **Math entity escaping** — replaced `<template>` with `<script type="text/x-markdown">` so KaTeX gets literal `>` instead of `&gt;` (`ccd67c8`).
- **Comment badge walk-up** — badge bubbling checks children visibility (not body-open state) and stops at the first visible ancestor, so counts land on the correct tree level (`0c422e7`).
- **Relative path resolution** — relative links/images in rendered markdown resolve against the task's own `.plan/<path>/` directory, not the project root (`adf3944`).
- **Rebuild discovers children** — `rebuild_task()` re-walks the task directory on partial updates so new/removed subtasks are discovered; broadcasts full-reload when the child set changes (`dafb5ec`).
- **Status consistency** — added status/`review_status` ordering validation and a `task_update.py --fix` mode to correct branch-status mismatches (`78fc53a`; superseded by the later single-status model).
- **Root task rendering** — root `.plan/task.md` renders as a tree node when it has body content, with a children-only fallback otherwise (`f8dbb69`).
- **Section expand uncap** — removed the max-height cap on task/section bodies after expand (`4372f68`).
