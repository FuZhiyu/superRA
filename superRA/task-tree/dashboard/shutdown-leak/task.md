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

Watcher shutdown now gives real `awatch` teardown a two-second cooperative grace
period, insulated from repeated ASGI caller cancellation. If it does not finish,
the watcher is cancelled and gets a separately bounded half-second to unwind.
If a cancellation-suppressing watcher defeats both phases, a short daemon
watchdog terminates this auxiliary, non-persistent dashboard process. Caller
cancellation is propagated after cleanup, ordinary watcher failures remain
observable, and the narrow benign `awatch` exception filter is preserved
([plan_dashboard.py:541-671](../../../../skills/task-tree/scripts/plan_dashboard.py#L541-L671)).

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
[test_dashboard.py:4175-4295](../../../../skills/task-tree/scripts/test_dashboard.py#L4175-L4295)).

After the fix, the detached regression completes two launch/connect/concurrent
RST/shutdown cycles. Each child is a distinct session leader, records native
watcher return and suppressed hard cancellation, exits with status zero,
releases its port, and is no longer alive before the next cycle. This establishes
process and OS-resource cleanup for the exercised interleaving; it does not
claim that the historical orphan samples uniquely identify this path.

Verification:

- The focused bounded-teardown, watchdog-ownership, and detached-process
  regressions pass: 5 passed.
- The complete dashboard suite passes: 279 passed with two existing warnings.
- The full task-tree script suite passes: 710 passed, with four existing
  warnings.

### Permanent Protection

The researcher confirmed two behaviors as key results requiring permanent
regression protection:

1. Watcher teardown remains bounded under repeated caller cancellation even when
   the watcher suppresses hard cancellation. The focused test covers the
   cooperative bound, forced-cancel bound, terminal process watchdog, caller
   cancellation propagation, and late task cleanup
   ([test_dashboard.py:1063-1130](../../../../skills/task-tree/scripts/test_dashboard.py#L1063-L1130)).
2. Repeated detached dashboard cycles survive eight concurrent abrupt SSE resets
   and finish with the real watchfiles coroutine returned, the child PID dead,
   and its port closed
   ([test_dashboard.py:4175-4295](../../../../skills/task-tree/scripts/test_dashboard.py#L4175-L4295)).

Both tests follow the repository's self-contained pytest convention and run
without a separate analysis pipeline or saved-output dependency. Their timing
bounds are control-flow deadlines rather than floating-point result tolerances;
the focused test injects short test-only bounds, while the process test uses a
five-second observation window around sub-second shutdown phases.

Red--green--green verification on 2026-07-11:

- Baseline: both protected tests passed together (2 passed).
- Bounded teardown red: inverting `completed_within_bound` failed at the intended
  assertion; restoring the expectation passed (1 passed).
- Detached lifecycle red: replacing the native-cleanup marker expectation with
  a sentinel failed against the observed `native watcher closed` and
  `hard cancel suppressed` marker; restoring it passed (1 passed).
- Full task-tree script suite after restoration: 710 passed with four existing
  warnings.

### Integration

The missing pre-fit JUnit artifact was caused by an armed process-exit watchdog
from an in-process dashboard server: a slow watcher completed after both teardown
bounds, but its uncancelled timer later terminated pytest. The watchdog is now
returned to `_stop_watcher()` and cancelled on late task completion. Only the
module's own `serve()` lifecycle on the main thread can arm a process-level exit;
external ASGI hosts and background-thread embeddings cannot, while a standalone
dashboard process retains the terminal fail-safe
([plan_dashboard.py:541-561](../../../../skills/task-tree/scripts/plan_dashboard.py#L541-L561),
[plan_dashboard.py:629-655](../../../../skills/task-tree/scripts/plan_dashboard.py#L629-L655)).
Focused regressions verify late completion disarms the timer without calling
`os._exit`, embedded servers on either the main or a background thread create no
timer, and a genuinely detached cancellation-suppressing server still exits
([test_dashboard.py:1132-1232](../../../../skills/task-tree/scripts/test_dashboard.py#L1132-L1232),
[test_dashboard.py:4175-4295](../../../../skills/task-tree/scripts/test_dashboard.py#L4175-L4295)).

Post-fit verification produced both requested JUnit artifacts: the verbose
dashboard suite passed 279 tests through the colliding-repositories case, and
the full task-tree script suite passed 710 tests with four existing warnings.
Both XML files parsed with zero errors and failures. All declared version
manifests are in sync, the version audit found no undeclared current-version
surface, and the patch release is recorded in the release notes. The project-doc
audit found the root README and contributor guide current, with no module-level
dashboard docs requiring changes.

**Final diff self-check:** refreshed with
`git diff dcfbd1fbcda03ed8defda1e39a2c7b14ff27d23f` after the ownership and audit
corrections; surviving change classes are bounded watcher shutdown,
`serve()`-scoped process-watchdog ownership, real lifecycle regressions and
permanent protection, task-tree status/evidence, and the researcher-requested
patch-release surfaces; the only cross-task hunk is the user-requested
pre-existing [docs-site postponement](../../docs-site/task.md), and no
scope-ambiguous hunk remains.

## Review Notes

1. **MAJOR:** Main-thread identity is not process ownership. The watchdog guard
   suppresses `os._exit` only outside the main thread, so an externally embedded
   ASGI host running this FastAPI app on its normal main-thread event loop still
   arms a timer whose target is `os._exit`
   ([plan_dashboard.py:541-557](../../../../skills/task-tree/scripts/plan_dashboard.py#L541-L557)).
   The regression covers only a background-thread embedding
   ([test_dashboard.py:1198-1218](../../../../skills/task-tree/scripts/test_dashboard.py#L1198-L1218)),
   leaving an embedded main-thread host vulnerable even though late watcher
   completion now disarms the timer. Establish explicit standalone-process
   ownership at the dashboard's own serve entry point, require that ownership
   before arming the process watchdog, and cover both a main-thread embedded
   host that must not arm and the detached child that must retain the fail-safe.
   → implemented: watchdog ownership now requires an active module-owned
   `serve()` lifecycle plus the main thread; direct main-thread and
   background-thread embedding regressions create no timer, while the detached
   process regression retains the fail-safe
   ([plan_dashboard.py:541-561](../../../../skills/task-tree/scripts/plan_dashboard.py#L541-L561),
   [test_dashboard.py:1199-1232](../../../../skills/task-tree/scripts/test_dashboard.py#L1199-L1232),
   [test_dashboard.py:4175-4295](../../../../skills/task-tree/scripts/test_dashboard.py#L4175-L4295)).

2. **MAJOR:** The committed version-audit evidence is not true at the governing
   HEAD. `scripts/bump-version.sh --audit` reports the task's exact
   current-version references as undeclared, contradicting both the claimed
   clean audit and the fresh Final diff self-check
   ([task.md:157-169](task.md#L157-L169)). The five declared manifests are in
   sync, but the integration record itself makes the audit non-clean under the
   audit's repository-wide undeclared-file check
   ([bump-version.sh:88-139](../../../../scripts/bump-version.sh#L88-L139)).
   Make permanent task evidence intentionally outside the version-bump audit (or
   remove the self-referential current-version literals), rerun `--audit`, and
   refresh the Results with the output that holds at the committed tree.
   → implemented: replaced exact current-version literals in this task with
   durable patch-release wording; `scripts/bump-version.sh --check` reports all
   declared manifests in sync and `--audit` reports no undeclared files
   ([bump-version.sh:50-139](../../../../scripts/bump-version.sh#L50-L139)).
