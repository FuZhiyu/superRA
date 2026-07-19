---
title: "Move Blocking Route Work off the Event Loop"
status: implemented
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

## Results

Four blocking spots now hand their pure-blocking core to `asyncio.to_thread`; every mutation of shared server state stays on the event loop.

- **`resolve_worktree`** is now `async def` ([plan_dashboard.py:893-925](../../../../skills/task-tree/scripts/plan_dashboard.py#L893-L925)). The cache-hit branch (the common case) is unchanged — a plain dict lookup on the loop. Only the cache-miss branch offloads: `_discovered_worktree_map()` (git subprocesses) and `_build_worktree_state()` (tree walk) run via `asyncio.to_thread`; the `_worktree_cache[wt_name] = state` write happens after the `await` returns, i.e. back on the loop thread, so the cache is never mutated from a worker thread. All 16 call sites were updated to `await resolve_worktree(request)`.
- **`/export`** ([plan_dashboard.py:1382](../../../../skills/task-tree/scripts/plan_dashboard.py#L1382)) offloads the `render_standalone_html` call — the tree re-walk, per-fragment render, and figure/vendor base64 encoding — via `asyncio.to_thread`.
- **`/api/worktrees`**: the entire body (discovery + basename disambiguation + entry assembly) is factored into a sync helper `_list_worktrees_sync()` ([plan_dashboard.py:1240-1301](../../../../skills/task-tree/scripts/plan_dashboard.py#L1240-L1301)) run via `asyncio.to_thread` from the route ([plan_dashboard.py:1305-1315](../../../../skills/task-tree/scripts/plan_dashboard.py#L1305-L1315)); it only reads module state (`PLAN_ROOT`, `_launch_wt_id`), no mutation.
- **`/api/comments/summary`**: the per-task `comments.yaml` walk is factored into `_comments_summary_sync()` ([plan_dashboard.py:1105-1119](../../../../skills/task-tree/scripts/plan_dashboard.py#L1105-L1119)) run via `asyncio.to_thread` from the route ([plan_dashboard.py:1123-1131](../../../../skills/task-tree/scripts/plan_dashboard.py#L1123-L1131)); it builds a local dict only.
- **New race surface closed**: offloading `/export`'s render onto a real OS thread meant it could now race a concurrent event-loop-thread route handler on the lazy-init `_jinja_env` module global's check-then-set (harmless in outcome — both branches build a working `Environment` — but avoidable). `lifespan()` now warms `_get_jinja_env()` once at startup ([plan_dashboard.py:806-812](../../../../skills/task-tree/scripts/plan_dashboard.py#L806-L812)), before any request can reach the threaded path.
- Deferred the advisory short-TTL `discover_worktrees` cache — not required by the objective's binding items, and `/api/worktrees` is now off-loop regardless, so its cost no longer freezes the server; left for a future task if dropdown-open latency is still a concern.

**Validation.** Added `TestEventLoopOffload` ([test_dashboard.py:4273-4368](../../../../skills/task-tree/scripts/test_dashboard.py#L4273-L4368)): a real `serve()` (real uvicorn loop + real threadpool, not `TestClient`'s single-threaded portal) with `render_standalone_html` monkeypatched to sleep 1.5s. While `/export` is in flight, an SSE heartbeat (0.2s interval) arrives in <1s and a concurrent `/healthz` completes in <1s.

Red/green check: running this test against the pre-change `plan_dashboard.py` (via `git show HEAD:...`) fails deterministically — `/healthz took 1.80s while /export was slow` — confirming the test catches the regression this task fixes; it passes on the current code.

Making `resolve_worktree` async required updating its direct (non-HTTP) callers in tests to run the coroutine to completion: [test_dashboard.py:620-621](../../../../skills/task-tree/scripts/test_dashboard.py#L620-L621) and five call sites in [test_multi_worktree.py](../../../../skills/task-tree/scripts/test_multi_worktree.py) now use `asyncio.run(...)`.

Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` — **697 passed, 2 skipped** (pre-existing `playwright+chromium unavailable` skips, unrelated to this change).
