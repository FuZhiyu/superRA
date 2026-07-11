---
title: "Eliminate Orphaned Dashboard Shutdown Spins"
status: approved
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

Watcher shutdown now gives real `awatch` teardown a two-second cooperative grace
period, insulated from repeated ASGI caller cancellation. If it does not finish,
the watcher is cancelled and gets a separately bounded half-second to unwind.
If a cancellation-suppressing watcher defeats both phases, a short daemon
watchdog terminates this auxiliary, non-persistent dashboard process. Caller
cancellation is propagated after cleanup, ordinary watcher failures remain
observable, and the narrow benign `awatch` exception filter is preserved
([plan_dashboard.py:540-659](../../../../skills/task-tree/scripts/plan_dashboard.py#L540-L659)).

Both regressions failed against the reviewed unbounded implementation before
this change. The focused case applied repeated caller cancellation to a watcher
that finished neither cooperatively nor after hard cancellation; teardown
exceeded its configured bound. The corrected test creates the absent watchdog
helper when overlaid on `ad18ee19`; that replay reached and failed the intended
`completed_within_bound` assertion rather than stopping during setup
([test_dashboard.py:1073-1079](../../../../skills/task-tree/scripts/test_dashboard.py#L1073-L1079),
[test_dashboard.py:1108-1118](../../../../skills/task-tree/scripts/test_dashboard.py#L1108-L1118)).
The process case launched a new-session child,
connected eight real SSE clients, reset them concurrently, and reached Uvicorn's
`Waiting for background tasks to complete` state with the child alive and port
open. The child wraps the real watchfiles coroutine and writes a marker only
after that coroutine returns, then suppresses hard cancellation to exercise the
terminal process watchdog
([test_dashboard.py:1063-1129](../../../../skills/task-tree/scripts/test_dashboard.py#L1063-L1129),
[test_dashboard.py:4072-4189](../../../../skills/task-tree/scripts/test_dashboard.py#L4072-L4189)).

After the fix, the detached regression completes two launch/connect/concurrent
RST/shutdown cycles. Each child is a distinct session leader, records native
watcher return and suppressed hard cancellation, exits with status zero,
releases its port, and is no longer alive before the next cycle. This establishes
process and OS-resource cleanup for the exercised interleaving; it does not
claim that the historical orphan samples uniquely identify this path.

Verification:

- The focused bounded-teardown and detached-process regressions pass: 2 passed.
- The watcher, idle-shutdown, and background-idle lifecycle set passes: 11 passed.
- The full task-tree script suite passes: 707 passed, with four existing
  warnings.
