---
title: "Loud Failures and Truthful SSE Bookkeeping"
status: not-started
depends_on:
  - event-loop-offload
---

## Objective

The dashboard server fails loudly and its connection bookkeeping stays truthful.

- A `task.md` that fails to parse during a watcher rebuild is surfaced — at minimum a server-side log line and a visible error state on that node in the client — instead of silently serving the last-good parse with no signal.
- A slow SSE client whose queue overflows has its connection ended rather than being silently unsubscribed, restoring the invariant the idle monitor depends on: registered queues == open connections (today the server can idle-exit under a live but stalled tab).
- The root-or-children inline template string that is duplicated verbatim in three places becomes one shared precompiled template, and the per-call `env.from_string` render helpers use precompiled templates.
- Stale dispatch-context comments ("task 01", "task 02", "created by another agent") are removed from the module.
- Validation: a test covers parse-error surfacing (broken fixture task.md → error state, not silent staleness); a test covers queue-overflow ending the SSE stream and the idle count staying consistent; both suites green.

## Planner Guidance

Findings (2026-07-19 review, [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py)): the silent swallow is `except Exception: return state.task_index.get(task_path), False` at 249-251; the eviction desync is `_broadcast` discarding a full queue at 333-340 while the client's generator keeps the connection open (its `finally` cleanup at 1090-1096 never runs), so `_open_connection_count` undercounts; duplicated template strings at 1012-1021 / 1040-1049 / 1494-1503; `from_string` per call (bypasses the template cache) at 791 and 807; stale comments at 121, 349, 1060 and nearby.

For ending an overflowed client: you cannot enqueue a sentinel into a full queue — consider draining-and-replacing with a close sentinel, tracking evicted queues that the generator checks each loop, or cancelling the response task. Design is the implementer's; the binding requirement is only that the connection ends and the count stays truthful.
