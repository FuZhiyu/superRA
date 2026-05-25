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

1. **[MAJOR]** SSE swap for task nodes creates nested `<div class="task-node">` elements, corrupting the DOM. `_render_task_node()` ([plan_dashboard.py:247-254](skills/task-system/scripts/plan_dashboard.py#L247)) renders the full `render_task_node` macro output, which produces a complete `<div class="task-node" sse-swap="task:X">...</div>`. The `sse-swap` attribute on `task_node.html` line 20 defaults to `innerHTML` swap (no `hx-swap` override). So when the SSE event arrives, htmx replaces the **contents** of the existing `<div class="task-node">` with the **full** rendered node including its own `<div class="task-node">` wrapper — producing nested duplicate wrappers. Fix: add `hx-swap="outerHTML"` to the task-node div in [task_node.html:16-20](skills/task-system/scripts/templates/task_node.html#L16), so the entire element is replaced rather than its contents.

2. **[MAJOR]** `full-reload` handler at [base.html:839](skills/task-system/scripts/templates/base.html#L839) is dead code. It listens for `htmx:sseMessage` with `event.detail.type === 'full-reload'`, but the htmx SSE extension only dispatches `htmx:sseMessage` for events that have a matching `sse-swap` or `hx-trigger="sse:*"` element registered. Since no element in the DOM has `sse-swap="full-reload"` or `hx-trigger="sse:full-reload"`, the `EventSource` never registers a listener for the `full-reload` event name, so `htmx:sseMessage` never fires for it. Structural changes remain invisible to the browser. Fix: either (a) add a hidden element inside the SSE scope with `sse-swap="full-reload"` that triggers a reload, or (b) add `hx-trigger="sse:full-reload"` to an element within the SSE scope, or (c) use a direct `EventSource` listener instead of relying on htmx event dispatch.
