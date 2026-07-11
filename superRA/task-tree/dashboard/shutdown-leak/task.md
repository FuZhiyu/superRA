---
title: "Eliminate Orphaned Dashboard Shutdown Spins"
status: implemented
depends_on:  []
---

## Objective

Ensure the live dashboard cannot leave orphaned, CPU-spinning
`plan_dashboard.py` processes after SSE clients disconnect or idle shutdown
begins.

- Preserve multi-worktree SSE delivery and cooperative `watchfiles` teardown.
- Cover clean, abrupt, repeated, and concurrent client disconnects through the
  real Uvicorn/FastAPI/watchfiles path.
- After the last client leaves, idle shutdown must finish within a bounded
  interval: the process exits, its port closes, and no watcher task or native
  event resource remains active.
- Repeated launch/connect/disconnect/idle-exit cycles must not accumulate
  detached processes. Add a regression that fails on the observed lifecycle
  race and passes reliably on macOS.
- Keep the full task-tree script test suite green.

## Planner Guidance

On 2026-07-10, the live machine had more than twenty detached dashboard Python
processes (`PPID 1`) consuming roughly 20--73% CPU each. Several had run for
8--21 days. Multiple processes targeted the same repo and port, while sampled
logs repeatedly ended at `Shutting down` / `Waiting for background tasks to
complete` before a replacement server started. Brief stack samples placed the
hot loop in uvloop's idle callback while an async-generator exception path was
being thrown and formatted. This is process/resource leakage rather than heap
growth: sampled RSS was only about 13--42 MB.

The affected plugin copies and current `origin/main` source have the same
SHA-256 (`4520c382...`), so treat the current cooperative-stop implementation as
insufficient under at least one real teardown interleaving. The likely boundary
spans the per-worktree watcher lifecycle
([plan_dashboard.py:450-572](../../../../skills/task-tree/scripts/plan_dashboard.py#L450-L572)),
the lifespan cleanup
([plan_dashboard.py:745-769](../../../../skills/task-tree/scripts/plan_dashboard.py#L745-L769)),
and the SSE generator's `finally` block
([plan_dashboard.py:955-995](../../../../skills/task-tree/scripts/plan_dashboard.py#L955-L995)).
Do not assume the existing benign `awatch` exception filter proves that native
resources were released; establish the failing interleaving first.

Existing real-server coverage leaves the matching gap:

- A clean context-managed disconnect asserts that the server exits
  ([test_dashboard.py:3897-3937](../../../../skills/task-tree/scripts/test_dashboard.py#L3897-L3937)).
- The dead-client test checks only that the Python connection count reaches
  zero; its cleanup requests shutdown but does not assert that the server thread
  actually terminates
  ([test_dashboard.py:3939-4005](../../../../skills/task-tree/scripts/test_dashboard.py#L3939-L4005)).
- The detached-process test covers idle exit with no SSE client at all
  ([test_dashboard.py:4302-4331](../../../../skills/task-tree/scripts/test_dashboard.py#L4302-L4331)).

Start from a deterministic stress/regression case with several clients that
disconnect abruptly and concurrently, followed by bounded idle exit and a
second launch cycle. Instrument task, thread, and open-event-resource state as
needed to distinguish a stuck ASGI streaming task from a leaked
`watchfiles`/fsevents source. A single `curl --max-time` client exited cleanly
during planning, so the reproducer must exercise the multi-client/racy path
rather than merely duplicating that simple case.

## Results

The leak boundary was cancellation during cooperative watcher teardown. Before
the fix, cancelling `_stop_watcher()` after it had signalled the watchfiles stop
event propagated cancellation through `await task`, hard-cancelled the watcher,
and was then swallowed by `_stop_watcher()`. This could remove the watcher from
the Python registries while its native event source was still unwinding. The
deterministic regression failed on that behavior before the production change
([test_dashboard.py:1063-1111](../../../../skills/task-tree/scripts/test_dashboard.py#L1063-L1111)).

Watcher teardown now shields the watcher from caller cancellation, waits through
repeated cancellation until cooperative cleanup finishes, preserves the narrow
benign `awatch` exception filter, and then propagates cancellation to the ASGI
caller. The SSE generator no longer suppresses its cancellation after cleanup
([plan_dashboard.py:532-592](../../../../skills/task-tree/scripts/plan_dashboard.py#L532-L592),
[plan_dashboard.py:982-1014](../../../../skills/task-tree/scripts/plan_dashboard.py#L982-L1014)).

Real-server coverage now runs two complete Uvicorn/FastAPI/watchfiles cycles.
Each cycle connects eight SSE clients, resets them concurrently, and verifies a
bounded idle exit, closed port, zero connection count, and empty watcher and stop
event registries before relaunching
([test_dashboard.py:4054-4141](../../../../skills/task-tree/scripts/test_dashboard.py#L4054-L4141)).

Verification:

- The focused cancellation and real-server regressions pass: 2 passed.
- The watcher and idle-shutdown lifecycle groups pass: 10 passed.
- The full task-tree script suite passes: 707 passed, with four existing
  warnings.
