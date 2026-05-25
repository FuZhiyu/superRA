---
title: "Filesystem watcher and SSE live reload"
status: implemented
review_status: revise
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

## Review Notes

1. **[MAJOR]** SSE event name mismatch breaks per-task live updates. The server broadcasts `event: task-updated` ([plan_dashboard.py:193](skills/task-system/scripts/plan_dashboard.py#L193)), but each task node's template declares `sse-swap="task:{{ task.path }}"` ([task_node.html:20](skills/task-system/scripts/templates/task_node.html#L20)), e.g., `sse-swap="task:server"`. htmx SSE extension matches on event name — `task-updated` never matches `task:server`, so individual task updates are silently dropped. Fix: either change `_broadcast("task-updated", ...)` to emit per-task event names like `task:<path>` with raw HTML as data (matching the `sse-swap` attribute), or add custom JavaScript that listens for `task-updated`, parses the JSON payload, and performs the DOM swap.

2. **[MAJOR]** `summary-updated` SSE data is multi-line HTML, which breaks SSE framing. `_broadcast()` ([plan_dashboard.py:133](skills/task-system/scripts/plan_dashboard.py#L133)) formats the message as `f"event: {event}\ndata: {data}\n\n"` — a single `data:` prefix for the entire payload. When `data` contains newlines (as `summary_bar.html` rendering does), the SSE parser only sees the first line as data; subsequent lines lack the `data:` prefix and are ignored or misinterpreted per the SSE spec. Fix: either (a) join the HTML onto a single line before sending, (b) wrap it in JSON via `json.dumps()` as the `task-updated` event already does, or (c) prefix every line with `data:` per SSE spec.

3. **[MAJOR]** `full-reload` SSE event is broadcast by the server on structural changes (task add/delete) ([plan_dashboard.py:185](skills/task-system/scripts/plan_dashboard.py#L185)), but no client-side handler exists — `full-reload` does not appear in any template or JavaScript. Structural changes are invisible to the browser until manual refresh. Fix: add a client-side listener (e.g., `sse-swap` target that triggers `location.reload()`, or a custom `EventSource` listener in JavaScript) for `full-reload` events.

4. **[MINOR]** Debounce comment is misleading. The comment "Debounce: collect all changes over a 200ms window" ([plan_dashboard.py:154-155](skills/task-system/scripts/plan_dashboard.py#L154)) implies the `asyncio.sleep(0.2)` merges subsequent changes, but `changes` is already bound before the sleep. The real debouncing happens inside `watchfiles.awatch` (default 1600ms). The sleep just adds 200ms latency. Either remove the sleep or update the comment to clarify its actual purpose.
