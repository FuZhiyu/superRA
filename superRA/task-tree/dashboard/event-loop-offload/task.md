---
title: "Move Blocking Route Work off the Event Loop"
status: not-started
depends_on:
  - standalone-state
---

## Objective

No route handler blocks the event loop with filesystem walks, git subprocesses, or asset encoding; SSE delivery and other requests stay live while a heavy request runs.

- `/export`, `/api/worktrees`, `/api/comments/summary`, and the worktree cache-miss path of `resolve_worktree` run their blocking work off-loop (plain `def` handlers via the threadpool, or `asyncio.to_thread` around the blocking core).
- Shared mutable server state stays race-free: mutation of `_worktree_cache`, client sets, and watcher maps remains single-threaded on the event loop (or is explicitly locked) — off-load only the pure-blocking work (git subprocesses, tree walks, rendering, base64 encoding) and apply results on the loop.
- Validation: a test demonstrates that during a slow `/export` (large fixture tree or injected delay) an SSE heartbeat and a concurrent cheap request still complete promptly; both suites green.

## Planner Guidance

Costs measured in the 2026-07-19 review: `discover_worktrees()` spawns N+2 git subprocesses — `worktree list`, `rev-parse`, and one `git log -1` **per worktree** — each with a 5-10s timeout ([_worktree_discovery.py:181-248](../../../../skills/task-tree/scripts/_worktree_discovery.py#L181-L248)); `/export` re-walks the tree, renders O(N) fragments, and base64-encodes every figure plus the 888KB vendor bundle ([plan_dashboard.py:1431-1466](../../../../skills/task-tree/scripts/plan_dashboard.py#L1431-L1466)); `/api/comments/summary` reads a `comments.yaml` per task (1173-1193). All handlers are `async def` today, so this work currently freezes heartbeats, other clients, and the watcher.

A short-TTL in-process cache for `discover_worktrees` results (it is called by `/api/worktrees` on every dropdown open) is a cheap additional win — advisory, not binding.
