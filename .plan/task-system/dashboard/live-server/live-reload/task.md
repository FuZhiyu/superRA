---
title: "Filesystem watcher and SSE live reload"
status: not-started
review_status: ~
integration_status: ~
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
