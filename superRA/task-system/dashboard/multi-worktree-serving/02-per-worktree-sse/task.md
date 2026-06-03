---
title: "Per-worktree SSE scoping + on-demand watchers"
status: not-started
depends_on: 
  - 01-per-worktree-state

tags: []
created: 2026-06-03
---

## Objective

Make live-reload **per-worktree**: an SSE client viewing worktree A receives only A's change events, and a file watcher runs for a worktree only while at least one client is viewing it. This removes the global broadcast that makes a switch flip every tab and lets one server watch several worktrees on demand without watching all of them all the time.

**Deliverables:**

1. Replace the single `_sse_clients` set ([plan_dashboard.py:82](../../../../../skills/task-system/scripts/plan_dashboard.py#L82)) with `_worktree_clients: dict[str, set[asyncio.Queue]]` keyed by worktree id. `/events` ([plan_dashboard.py:496](../../../../../skills/task-system/scripts/plan_dashboard.py#L496)) reads the worktree from `?wt=` (resolved via task 01's resolver, default = launch worktree), registers its queue under that worktree, and on disconnect removes it.
2. Replace the single `_watch_plan_root` / `_watcher_task` ([plan_dashboard.py:204](../../../../../skills/task-system/scripts/plan_dashboard.py#L204)) with per-worktree watchers: `_worktree_watchers: dict[str, asyncio.Task]`, `_ensure_watcher(wt)` started on the first client for a worktree, `_stop_watcher(wt)` when the last client for that worktree disconnects. The watcher watches that worktree's `plan_root` and, on change, invalidates that worktree's `WorktreeState` (task 01's hook) and broadcasts to that worktree's clients only.
3. Scope `_broadcast(event, data, wt)` ([plan_dashboard.py:182](../../../../../skills/task-system/scripts/plan_dashboard.py#L182)) to a worktree's client set. Preserve all existing event types and their semantics: `full-reload`, `summary-updated`, `task:<path>`, and the connection heartbeat.
4. Handle the lifecycle hazards explicitly (exploration flagged these as the risk center):
   - **Watcher-init race:** ensure the client's queue is registered before the watcher can emit, so no early event is lost.
   - **Crashed-watcher reuse:** `_ensure_watcher` must treat a present-but-`done()` task as absent and respawn, rather than silently returning a dead watcher.
   - **Teardown race:** a broadcast arriving after the last client left must no-op safely (`dict.get(wt, set())`), and `_stop_watcher` must `pop` (not leave) the task so it cannot zombie.
   - **Shutdown:** `lifespan()` cancels all per-worktree watchers, not just one.
5. Update `lifespan()` ([plan_dashboard.py:406](../../../../../skills/task-system/scripts/plan_dashboard.py#L406)) so startup no longer unconditionally spawns one global watcher; the launch worktree's watcher starts on its first client (or is seeded if simpler, but must still tear down per the rules above).

**Scope boundary.** This task owns SSE delivery and watcher lifecycle. It consumes task 01's `resolve_worktree` and `WorktreeState`-invalidation hook; it does not change client URL/selector code (task 03). The client still subscribes to `/events`; this task makes `/events` honor `?wt=`. Task 03 makes the client pass the right `?wt=` on the SSE connection.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Keep edits and commits on this worktree's branch.

## Validation

- Unit tests (extend the SSE tests in [test_dashboard.py](../../../../../skills/task-system/scripts/test_dashboard.py), e.g. `TestSSEBroadcast`): a broadcast to worktree A reaches only A's queues, never B's; a `task:<path>` edit under A produces an A-scoped event and nothing on B.
- Watcher lifecycle: connecting the first client for a worktree starts exactly one watcher; disconnecting the last stops it; a second client for the same worktree does not start a second watcher; a watcher whose task has crashed is respawned on the next client.
- No event loss on the init race (registered-before-emit), and a broadcast after last-disconnect does not raise.
- Full suite passes; single-worktree live-reload behaves as before.

## Planner Guidance

- The async hazards are the whole difficulty — write the lifecycle tests first and keep `_ensure_watcher` / `_stop_watcher` under a per-worktree lock (`_worktree_locks: dict[str, asyncio.Lock]`) to serialize spawn/teardown, separate from task 01's build lock.
- Keep the watcher body's change-detection logic (structural vs content edit, debounce) unchanged from [plan_dashboard.py:204-286](../../../../../skills/task-system/scripts/plan_dashboard.py#L204); only parameterize the root it watches and the worktree it broadcasts to. The rebuild-and-render-fragment step it calls is owned by task 01 (deliverable 4: the hook rebuilds the `WorktreeState` and returns the `summary-updated` / `task:<path>` fragments). If you find the watcher body still reading module globals to render fragments, that is task 01's gap — route it back, do not refactor 01's state model from inside this task.
- TestClient disables lifespan, so test the watcher/queue functions directly (as `TestSSEBroadcast` already does) rather than through a live server.
