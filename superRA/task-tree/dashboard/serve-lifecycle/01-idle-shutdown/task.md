---
title: "Server self-exits after idle timeout"
status: approved
depends_on: []
tags: []
created: 2026-06-04
---

## Objective

Make the running server **exit on its own after 5 continuous minutes with zero open tabs**, where "open tab" means a live `/events` SSE connection and the count is summed across all worktrees. Add periodic SSE heartbeats so a connection that died without a clean close (slept laptop, dropped network) is pruned from the client sets instead of holding the server open forever.

This is the server-internal half of the [parent](../task.md) feature and ships first; it has no launch-mode changes. The parent's design decisions 1–4 are binding here.

**Concretely:**

1. **Switch the serve path to a `uvicorn.Server` handle.** Replace `uvicorn.run(app, …)` ([plan_dashboard.py:1631](../../../../../skills/task-tree/scripts/plan_dashboard.py#L1631)) with an instantiated `uvicorn.Server(uvicorn.Config(app, host=…, port=…, log_level=…))` run via its async `serve()`, so a monitor coroutine can request shutdown by setting `server.should_exit = True`. `uvicorn.run` exposes no such handle. Foreground and (later) background both go through this path so their lifecycle is identical.
2. **Track a global open-connection count and run an idle monitor.** The live count is `sum(len(s) for s in _worktree_clients.values())` over the per-worktree client registry ([plan_dashboard.py:83](../../../../../skills/task-tree/scripts/plan_dashboard.py#L83)). A monitor coroutine — started from `lifespan` ([plan_dashboard.py:603](../../../../../skills/task-tree/scripts/plan_dashboard.py#L603)) and cancelled on shutdown — tracks how long the count has been zero; once it has been zero continuously for the idle timeout, it sets `server.should_exit = True`. The timer starts at process launch (zero tabs initially) and is reset/held whenever the count is non-zero. **The idle timeout must be injectable** (constructor arg / parameter / module constant) so tests can drive it with a sub-second value; default 5 minutes (300 s).
3. **Make heartbeats periodic to prune dead connections.** The `/events` generator currently yields a single initial `: heartbeat` ([plan_dashboard.py:791](../../../../../skills/task-tree/scripts/plan_dashboard.py#L791)). Send heartbeats on an interval so writing to a dead connection raises and the generator's `finally` removes that queue from `_worktree_clients` ([plan_dashboard.py:801](../../../../../skills/task-tree/scripts/plan_dashboard.py#L801)), keeping the count accurate. Choose a heartbeat interval well under the idle timeout (e.g. 15–30 s). Preserve the existing register-queue-before-watch ordering and the last-client `_stop_watcher` teardown.

## Validation

- **Exits when idle:** with the idle timeout shrunk to a sub-second test value and no clients, the monitor sets `should_exit` within roughly the timeout; the server stops cleanly and `lifespan` still cancels every per-worktree watcher.
- **Stays up while watched:** with at least one `/events` client connected, the monitor does **not** trigger shutdown across several timeout windows; closing that last client then lets it exit within one window.
- **Heartbeat prunes the dead:** a connection whose consumer has gone away is dropped from `_worktree_clients` after a heartbeat cycle, so it stops counting toward the open-tab total. Prefer testing the idle decision against the connection-count state rather than wall-clock timing where possible.
- **No regression:** the existing SSE behavior (initial event delivery, per-worktree broadcast scoping, last-client watcher teardown) still holds; the full task-tree suite passes (`uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`).

## Planner Guidance

- Keep the idle decision separable from wall-clock where you can — e.g. a small helper that, given the current open-connection count and the elapsed-zero duration, returns whether to exit — so the core logic is unit-testable without sleeping for the real timeout.
- The monitor is one coroutine for the whole process, not one per worktree; the per-worktree watchers stay exactly as multi-worktree-serving left them.
- `should_exit` triggers uvicorn's normal graceful shutdown, which runs the `lifespan` exit path; do not add a second teardown for the watchers.

## Results

Three changes to [plan_dashboard.py](../../../../../skills/task-tree/scripts/plan_dashboard.py) implement the idle-shutdown mechanism; 10 new tests verify it.

**1. `uvicorn.Server` handle** ([plan_dashboard.py:1648-1662](../../../../../skills/task-tree/scripts/plan_dashboard.py#L1648-L1662))

`uvicorn.run(…)` is replaced by a new `serve(port)` function that instantiates `uvicorn.Server(uvicorn.Config(…))`, stores the handle in the module-level `_server` variable, and runs it via `asyncio.run(_server.serve())`. The idle monitor sets `_server.should_exit = True` through this handle to trigger uvicorn's normal graceful shutdown.

**2. Idle monitor** ([plan_dashboard.py:497-537](../../../../../skills/task-tree/scripts/plan_dashboard.py#L497-L537))

Three additions:

- `IDLE_TIMEOUT = 300.0` and `HEARTBEAT_INTERVAL = 20.0` module constants; tests drive `_idle_monitor(timeout=…)` directly, and `lifespan` reads `IDLE_TIMEOUT` at launch.
- `_open_connection_count()` — `sum(len(s) for s in _worktree_clients.values())`.
- `_should_idle_exit(open_count, idle_seconds, timeout)` — pure function, no side effects; returns True when `open_count == 0` and `idle_seconds >= timeout`. Tests drive this directly without sleeping.
- `_idle_monitor(timeout, poll)` — coroutine that polls every `poll` seconds; accumulates `idle_elapsed` while count is zero, resets when non-zero, sets `_server.should_exit = True` and returns once the threshold is crossed.

`lifespan` ([plan_dashboard.py:651-677](../../../../../skills/task-tree/scripts/plan_dashboard.py#L651-L677)) creates the monitor task at startup and cancels it in a `finally` block on shutdown (so uvicorn's graceful shutdown, which re-enters the lifespan context, always cleans up the monitor before cancelling watchers).

**3. Periodic heartbeats** ([plan_dashboard.py:852-877](../../../../../skills/task-tree/scripts/plan_dashboard.py#L852-L877))

The SSE event loop wraps `queue.get()` in `asyncio.wait_for(…, timeout=HEARTBEAT_INTERVAL)`; on `TimeoutError` it yields `: heartbeat\n\n`. Writing to a dead connection raises `BrokenPipeError` / `ConnectionResetError`, which falls through to the `finally` block where the queue is removed from `_worktree_clients` — keeping the open-connection count accurate for the idle monitor.

**Validation:** 461 passed, 2 warnings (451 pre-existing + 10 new).

```
uv run --project skills/task-tree --with pytest --with httpx \
    python -m pytest skills/task-tree/scripts -q
# 461 passed, 2 warnings in 31.34s
```

New tests in `TestIdleShutdown` cover: `_should_idle_exit` (5 cases), `_open_connection_count` (2 cases), `_idle_monitor` exits with zero connections, monitor does not exit while client present, monitor fires after last client leaves.

## Review Notes

Approved — core mechanism is correct and verified end-to-end (drove the real `lifespan` with a sub-second `IDLE_TIMEOUT`: monitor starts, sets `should_exit` while idle, stays up with a client present, exits after the last client leaves, and the exit path drains watchers cleanly; full suite 461 passed). The items below are non-blocking cleanups; fold them into the next pass on this file (task 02 touches the same `serve()`/`main()` code).

→ orchestrator: all three carried to [02-background-launch](../02-background-launch/task.md) §Planner Guidance for in-lane fix (same file/test module); the Results echo flagged in item 1 is corrected above in this commit. Step 3 verifies these are cleared when 02 is approved.

1. MINOR — Stale comment references a nonexistent symbol. [plan_dashboard.py:67](../../../../../skills/task-tree/scripts/plan_dashboard.py#L67) says "Tests override this via `_idle_timeout` before calling `serve()`", but there is no `_idle_timeout` symbol (the constant is `IDLE_TIMEOUT`) and no committed test overrides it before calling `serve()` — the tests drive `_idle_monitor(timeout=…)` directly. The Results note ("tests override `IDLE_TIMEOUT` before calling `serve()`") repeats the same inaccuracy. Fix: reword the comment to describe the actual injection (`_idle_monitor`'s `timeout` parameter; `IDLE_TIMEOUT` is also picked up by `lifespan` at call time if set before launch) and correct the Results line.

2. MINOR — Dead import. [plan_dashboard.py:1710](../../../../../skills/task-tree/scripts/plan_dashboard.py#L1710) keeps `import uvicorn` in `main()`, but this change moved the only uvicorn use into `serve()` (which has its own local import), leaving line 1710 unused. Remove it.

3. MINOR — Two stated Validation criteria have no committed test. The real `serve`/`lifespan` self-exit path and the heartbeat-prunes-a-dead-connection path are asserted in Results but covered only by isolated `_idle_monitor`/`_should_idle_exit` unit tests (the existing `/events` test consumes just the initial heartbeat and never reaches the new `wait_for`/periodic-heartbeat branch). This is consistent with planner guidance (unit-test the decision, avoid wall-clock), and I confirmed the wiring manually, so it is non-blocking — but a small lifespan-level test (sub-second `IDLE_TIMEOUT`, assert `should_exit` fires and watchers are drained) would lock in the linchpin behavior against regression.
