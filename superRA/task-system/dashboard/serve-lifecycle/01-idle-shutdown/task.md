---
title: "Server self-exits after idle timeout"
status: not-started
depends_on: []
tags: []
created: 2026-06-04
---

## Objective

Make the running server **exit on its own after 5 continuous minutes with zero open tabs**, where "open tab" means a live `/events` SSE connection and the count is summed across all worktrees. Add periodic SSE heartbeats so a connection that died without a clean close (slept laptop, dropped network) is pruned from the client sets instead of holding the server open forever.

This is the server-internal half of the [parent](../task.md) feature and ships first; it has no launch-mode changes. The parent's design decisions 1–4 are binding here.

**Concretely:**

1. **Switch the serve path to a `uvicorn.Server` handle.** Replace `uvicorn.run(app, …)` ([plan_dashboard.py:1631](../../../../../skills/task-system/scripts/plan_dashboard.py#L1631)) with an instantiated `uvicorn.Server(uvicorn.Config(app, host=…, port=…, log_level=…))` run via its async `serve()`, so a monitor coroutine can request shutdown by setting `server.should_exit = True`. `uvicorn.run` exposes no such handle. Foreground and (later) background both go through this path so their lifecycle is identical.
2. **Track a global open-connection count and run an idle monitor.** The live count is `sum(len(s) for s in _worktree_clients.values())` over the per-worktree client registry ([plan_dashboard.py:83](../../../../../skills/task-system/scripts/plan_dashboard.py#L83)). A monitor coroutine — started from `lifespan` ([plan_dashboard.py:603](../../../../../skills/task-system/scripts/plan_dashboard.py#L603)) and cancelled on shutdown — tracks how long the count has been zero; once it has been zero continuously for the idle timeout, it sets `server.should_exit = True`. The timer starts at process launch (zero tabs initially) and is reset/held whenever the count is non-zero. **The idle timeout must be injectable** (constructor arg / parameter / module constant) so tests can drive it with a sub-second value; default 5 minutes (300 s).
3. **Make heartbeats periodic to prune dead connections.** The `/events` generator currently yields a single initial `: heartbeat` ([plan_dashboard.py:791](../../../../../skills/task-system/scripts/plan_dashboard.py#L791)). Send heartbeats on an interval so writing to a dead connection raises and the generator's `finally` removes that queue from `_worktree_clients` ([plan_dashboard.py:801](../../../../../skills/task-system/scripts/plan_dashboard.py#L801)), keeping the count accurate. Choose a heartbeat interval well under the idle timeout (e.g. 15–30 s). Preserve the existing register-queue-before-watch ordering and the last-client `_stop_watcher` teardown.

## Validation

- **Exits when idle:** with the idle timeout shrunk to a sub-second test value and no clients, the monitor sets `should_exit` within roughly the timeout; the server stops cleanly and `lifespan` still cancels every per-worktree watcher.
- **Stays up while watched:** with at least one `/events` client connected, the monitor does **not** trigger shutdown across several timeout windows; closing that last client then lets it exit within one window.
- **Heartbeat prunes the dead:** a connection whose consumer has gone away is dropped from `_worktree_clients` after a heartbeat cycle, so it stops counting toward the open-tab total. Prefer testing the idle decision against the connection-count state rather than wall-clock timing where possible.
- **No regression:** the existing SSE behavior (initial event delivery, per-worktree broadcast scoping, last-client watcher teardown) still holds; the full task-system suite passes (`uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts -q`).

## Planner Guidance

- Keep the idle decision separable from wall-clock where you can — e.g. a small helper that, given the current open-connection count and the elapsed-zero duration, returns whether to exit — so the core logic is unit-testable without sleeping for the real timeout.
- The monitor is one coroutine for the whole process, not one per worktree; the per-worktree watchers stay exactly as multi-worktree-serving left them.
- `should_exit` triggers uvicorn's normal graceful shutdown, which runs the `lifespan` exit path; do not add a second teardown for the watchers.

## Results
