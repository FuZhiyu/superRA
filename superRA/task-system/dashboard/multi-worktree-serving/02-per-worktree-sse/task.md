---
title: "Per-worktree SSE scoping + on-demand watchers"
status: implemented
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

## Results

SSE delivery and the file-watcher lifecycle are now per-worktree in [plan_dashboard.py](../../../../../skills/task-system/scripts/plan_dashboard.py). A client viewing worktree A receives only A's change events, and a watcher for a worktree runs only while that worktree has at least one connected client. Task 01's `WorktreeState` model, `resolve_worktree`, and `rebuild_worktree_state` / `_rebuild_and_broadcast` hooks were consumed unchanged — only delivery and watcher lifecycle were rewritten on top of them.

**State model (replacing the single global SSE set + watcher):**

- `_worktree_clients: dict[str, set[asyncio.Queue]]` — per-worktree client queues.
- `_worktree_watchers: dict[str, asyncio.Task]` — the awatch task feeding each worktree's clients.
- `_worktree_locks: dict[str, asyncio.Lock]` — per-worktree spawn/teardown lock (`_worktree_lock(wt)` creates on first use), separate from task 01's per-state build lock.

**Delivery and lifecycle:**

- `_broadcast(event, data, wt)` is scoped to `_worktree_clients.get(wt, set())` — a broadcast for one worktree never reaches another's clients, and a broadcast for a worktree with no current clients is a safe no-op. Event types and framing (`full-reload`, `summary-updated`, `task:<path>`, heartbeat) are preserved.
- `_watch_worktree(wt)` is the former `_watch_plan_root` parameterized to one worktree: it watches that worktree's `plan_root` and routes each change batch through task 01's `_rebuild_and_broadcast(state, changes)`, whose change-detection logic (structural vs content, debounce) is unchanged. The fragment-render step reads from the resolved `WorktreeState`, not module globals, so no task-01 gap surfaced.
- `_ensure_watcher(wt)` / `_stop_watcher(wt)` run under the worktree's lock so a concurrent connect and disconnect cannot spawn a duplicate or tear down a live watcher.
- `/events` now takes the `Request`, resolves the worktree via `resolve_worktree(request).wt_id` (default = launch worktree), and **registers the client's queue before calling `_ensure_watcher`** so no event emitted during watcher startup is lost (init-race fix). On disconnect it removes the queue and, if it was the worktree's last client, calls `_stop_watcher`.
- `lifespan()` no longer spawns a global watcher at startup (watchers are demand-started per client) and on shutdown cancels **every** per-worktree watcher, not just one.

**Hazard handling (per deliverable 4):**

- *Watcher-init race:* queue registered before `_ensure_watcher` runs — verified by `test_events_registers_queue_before_ensuring_watcher`.
- *Crashed-watcher reuse:* `_ensure_watcher` treats a present-but-`done()` task as absent and respawns — verified by `test_crashed_watcher_is_respawned`.
- *Teardown race:* `_broadcast` uses `dict.get(wt, set())` (no-op on a vanished worktree); `_stop_watcher` `pop`s the task so it cannot zombie — verified by `test_broadcast_to_empty_worktree_is_noop` and `test_last_disconnect_stops_watcher`.
- *Shutdown:* `lifespan` iterates `list(_worktree_watchers)` and stops each.

**`/api/worktree/switch`** (the retiring global-switch endpoint, fully removed in task 03) no longer manages a watcher — per-worktree watchers are self-managing — and now broadcasts its `full-reload` scoped to the post-switch launch worktree's clients instead of all clients.

**Tests** (extending the existing SSE tests as directed):

- `TestSSEBroadcast` (test_dashboard.py): existing framing tests migrated to the `_broadcast(..., wt)` signature; added `test_broadcast_scoped_to_worktree` (A reaches only A, never B) and `test_broadcast_to_empty_worktree_is_noop`.
- `TestWatcherLifecycle` (new, test_dashboard.py): first-client-starts-exactly-one + no-duplicate-on-second, last-disconnect-stops, crashed-watcher-respawn, register-before-ensure ordering, and `test_content_edit_under_a_is_scoped_to_a` (a content edit under A drives a `task:01-first` event to A's queue and nothing on B).
- `test_events_sse_generator_yields_heartbeat` updated to drive `sse_events(request)` and assert per-worktree register/unregister + watcher start/stop on stream close.
- Updated the three `_broadcast`-framing tests in `tests/test_state_preservation.py::TestBroadcastIntegration` and the switch-broadcast test in `test_worktree_selector.py` to the new signature / per-worktree client set.

**Verification:** full task-system suite green — `~/.venv/bin/python -m pytest skills/task-system/scripts/ -q` → **440 passed** (the one warning is a pre-existing unrelated `task_check` status test). A live end-to-end smoke run (real `~`-rooted worktree, not `/tmp`) confirmed the runtime path: watcher starts on first client, no duplicate on second, a live `task.md` edit drives a worktree-scoped broadcast, another worktree's queue receives nothing, and the watcher stops on last disconnect.

**Deviation:** none material — followed the planner guidance (lifecycle tests, per-worktree lock, watcher body unchanged). One note: `_render_summary` / `_render_nav_node` already took explicit `WorktreeState`-sourced arguments (task 01 had already routed the fragment render off module globals), so no route-back to task 01 was needed.

**Caveat:** macOS resolves `/tmp` to `/private/tmp`, so task 01's `relative_to(plan_root)` in `_rebuild_and_broadcast` skips fs-event paths when the watched root is under `/tmp` (the smoke run therefore used a `~`-rooted tree). This is pre-existing task-01 behavior left unchanged per the scope boundary and does not affect real worktrees under `/Users/...`.

## Planner Guidance

- The async hazards are the whole difficulty — write the lifecycle tests first and keep `_ensure_watcher` / `_stop_watcher` under a per-worktree lock (`_worktree_locks: dict[str, asyncio.Lock]`) to serialize spawn/teardown, separate from task 01's build lock.
- Keep the watcher body's change-detection logic (structural vs content edit, debounce) unchanged from [plan_dashboard.py:204-286](../../../../../skills/task-system/scripts/plan_dashboard.py#L204); only parameterize the root it watches and the worktree it broadcasts to. The rebuild-and-render-fragment step it calls is owned by task 01 (deliverable 4: the hook rebuilds the `WorktreeState` and returns the `summary-updated` / `task:<path>` fragments). If you find the watcher body still reading module globals to render fragments, that is task 01's gap — route it back, do not refactor 01's state model from inside this task.
- TestClient disables lifespan, so test the watcher/queue functions directly (as `TestSSEBroadcast` already does) rather than through a live server.
