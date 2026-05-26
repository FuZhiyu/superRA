---
title: "Filesystem watcher and SSE live reload"
status: approved
depends_on:
  - ../server
  - ../templates
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Wire up filesystem watching and Server-Sent Events so the dashboard updates automatically when `.plan/` files change on disk.

**Watcher:**
- Use `watchfiles.awatch()` to monitor `.plan/` recursively for `task.md` changes
- Run the watcher as a FastAPI background task (lifespan event)
- On change: identify the changed task path, re-parse that single `task.md`, update the in-memory index
- Debounce rapid changes (agents rewriting a file may trigger multiple events) — ~200ms window

**SSE endpoint:**
- `GET /events` returns a `text/event-stream` response
- Each connected browser holds an open SSE connection
- When a task changes, broadcast an SSE event: `event: task-updated\ndata: <rendered HTML fragment for the changed task>\n\n`
- htmx's SSE extension picks this up and swaps the fragment into the matching `sse-swap` target
- Also broadcast `event: summary-updated\ndata: <rendered summary bar>\n\n` so the status counts refresh

**Edge cases:**
- New task directory created → add to index, broadcast parent re-render (new child appears)
- Task directory deleted → remove from index, broadcast parent re-render
- SSE reconnection: browser auto-retries (SSE built-in), server should handle multiple concurrent connections via an async broadcast channel

## Results

Implemented in [`plan_dashboard.py`](skills/task-system/scripts/plan_dashboard.py).

**Watcher:** `_watch_plan_root()` uses `watchfiles.awatch(PLAN_ROOT)` as a background task started in the FastAPI lifespan. Filters for `task.md` and `comments.yaml` only. 200ms debounce via `asyncio.sleep(0.2)` after receiving changes.

**SSE broadcast:** `_broadcast(event, data)` sends SSE-formatted messages to all connected clients via `set[asyncio.Queue]`. Each `/events` connection gets its own queue (maxsize=256). Dead queues (full) are pruned on broadcast.

**Change handling:**
- Modified `task.md` / `comments.yaml` -> `rebuild_task(path)` + broadcast `task-updated` (HTML fragment) + `summary-updated`
- New/deleted `task.md` -> `rebuild_tree()` + broadcast `full-reload`

**SSE events emitted:**
- `event: task-updated` with `data: {"path": "...", "html": "..."}`
- `event: summary-updated` with `data: <rendered summary HTML>`
- `event: full-reload` with `data: {}`

