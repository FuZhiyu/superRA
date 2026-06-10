---
title: "Fix watcher-teardown CPU spin on SSE disconnect"
status: approved
depends_on: 
  - 02-per-worktree-sse

tags: []
created: 2026-06-07
---

## Objective

Fix a CPU busy-loop that the per-worktree watcher teardown leaks on SSE client disconnect. When a worktree's last SSE client disconnects, the `/events` generator's `finally` calls `_stop_watcher(wt)`, which cancels that worktree's `watchfiles.awatch` task ([plan_dashboard.py `_stop_watcher`](../../../../../skills/task-tree/scripts/plan_dashboard.py#L517), called from the SSE `finally` at [L956](../../../../../skills/task-tree/scripts/plan_dashboard.py#L956)). After that cancel, the uvicorn event loop spins on the kqueue selector at ~50–68% of a core **permanently**, and the spinning process then ignores `SIGTERM`. Every dev session that opens then closes a dashboard tab leaves one spinning, unkillable zombie; these accumulate and silently pin multiple cores.

**The headline invariant (and validation gate).** After a connect → disconnect cycle — and after every client has disconnected — the idle server returns to its pre-client CPU baseline (≈0.1%) and exits promptly on `SIGTERM`. Pin it with a server-level reproduction: launch the real server, connect one SSE client to `/events`, disconnect it, then sample the process CPU over ~30 s; it must stay at baseline rather than climb. The full task-tree suite stays green, and a new regression test fails against the current teardown and passes after the fix.

**What is already ruled out** (do not re-litigate these; they are the boundary that localizes the defect to watcher teardown):
- Not the event-loop implementation: a bare uvicorn server with no watcher idles at ~0%.
- Not idle auto-shutdown: with zero clients from start, the server exits cleanly.
- Not the watcher while running: CPU is ~0.1% the whole time a client is connected and the watcher is live.
- Not `awatch` cancellation in isolation: a minimal `awatch` task cancelled outside the server does **not** spin (≈0.00 CPU). The spin reproduces only in the full server context — the SSE generator's `finally` calling `_stop_watcher` mid-connection-teardown — so the fix must be validated against the server-level repro, not a standalone snippet.

**Scope.** This task fixes the post-disconnect spin only. Engaging `uvloop` in `serve()` (the serve path currently runs `asyncio.run(_server.serve())` and never installs uvloop — [plan_dashboard.py:1728](../../../../../skills/task-tree/scripts/plan_dashboard.py#L1728)) is a separate, optional performance item that lives with the `serve()` path under `serve-lifecycle`; it is **out of scope here** and must not be bundled into this fix.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/watcher-teardown-spin`. Concurrent worktrees of this repo exist; keep all edits and commits on this worktree's branch (`watcher-teardown-spin`).

This task touches `skills/task-tree/scripts/*` (the task-tree package) only — no Codex-generated agent files. Treat `plan_dashboard.py` as skill-package code; do not hand-edit any `skills/task-tree/build/lib/...` build output. Run the CLI and tests from live source:
- CLI: `uv run --project skills/task-tree superra dashboard …` (or `… plan_dashboard.py serve …`).
- Tests: `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`.

## Planner Guidance

**Diagnostic first (optional, needs one sudo command from the researcher).** A `sudo py-spy dump --pid <pid>` on a process in the post-disconnect spin state pins the exact Python frame. The C-level sample already shows it stuck polling the selector at ~0 timeout — a perpetually-ready fd or callback the loop services on every pass. py-spy is diagnostic, not required: a candidate fix that demonstrably returns the server-level repro to baseline CPU is sufficient evidence on its own.

**Candidate fixes (test each against the server-level repro: connect → disconnect → measure CPU):**
- (a) Replace `task.cancel()` teardown with cooperative shutdown — pass an `asyncio.Event` as `watchfiles.awatch(..., stop_event=…)` ([the awatch call](../../../../../skills/task-tree/scripts/plan_dashboard.py#L458)) and set it in `_stop_watcher` instead of cancelling, so watchfiles closes its native fd/thread on its own terms.
- (b) Ensure the watchfiles native file-descriptor / thread is fully closed on teardown — the leaked, always-ready fd is the most likely loop-wakeup source.
- (c) Move `_stop_watcher` out of the disconnecting generator's `finally` (e.g. schedule teardown after the response fully unwinds) so cancellation does not race the connection teardown.

`_ensure_watcher`/`_stop_watcher` already serialize spawn and teardown under a per-worktree lock ([L486–L534](../../../../../skills/task-tree/scripts/plan_dashboard.py#L486)); preserve that invariant and the existing crashed-watcher-respawn guard whichever candidate lands.

**Environment angle.** `watchfiles` and the Python runtime are recent; the C-level "always-ready selector" symptom is consistent with a watchfiles teardown issue. Check whether a newer `watchfiles` fixes awatch-cancel cleanup, and whether the version should be pinned/upgraded in `skills/task-tree/pyproject.toml`.

**Regression test.** Add a test alongside the existing dashboard server tests ([test_multi_worktree.py](../../../../../skills/task-tree/scripts/test_multi_worktree.py) — watcher-lifecycle tests live here; [test_dashboard.py](../../../../../skills/task-tree/scripts/test_dashboard.py)) that drives a connect → disconnect on `/events` and asserts the loop quiesces (no pending always-ready callback / CPU stays at baseline). It must turn red against the current teardown and green after the fix; prefer asserting on a deterministic loop-state signal over wall-clock CPU where possible, since CPU sampling is flaky under CI.

## Critical Files
- [`skills/task-tree/scripts/plan_dashboard.py`](../../../../../skills/task-tree/scripts/plan_dashboard.py) — `_stop_watcher` (L517), the `/events` generator `finally` (L956), `_watch_worktree`/`awatch` (L458), `_ensure_watcher` (L486), `serve()` (L1714, uvloop note only).
- [`skills/task-tree/scripts/test_multi_worktree.py`](../../../../../skills/task-tree/scripts/test_multi_worktree.py) — watcher-lifecycle test patterns; the new regression test extends these.
- [`skills/task-tree/pyproject.toml`](../../../../../skills/task-tree/pyproject.toml) — `watchfiles` pin, if the environment angle pans out.

## Validation
Against the real server (one port) on this worktree:
- Launch the server, connect one SSE client to `/events`, disconnect it, sample process CPU over ~30 s → stays at the pre-client baseline (≈0.1%), does not climb.
- After all clients disconnect, the server still self-exits within the idle window and responds to `SIGTERM` promptly (no unkillable zombie).
- A new regression test fails against the current teardown and passes after the fix.
- Full task-tree suite green from live source.

## Results

**Status: fixed.** `_stop_watcher` now tears the per-worktree watcher down *cooperatively* via the `watchfiles.awatch(..., stop_event=…)` event (candidate (a)) instead of `task.cancel()`, so the watch loop reaches its clean `return` and watchfiles runs `RustNotify.__exit__`, closing the native `notify-rs fsevents loop` thread/fd. That native thread was the spin's driver: the old hard cancel orphaned it, leaving the event loop's kqueue perpetually readable so the loop cycled `kevent(timeout≈0) → task_step` forever at ~56% CPU per disconnect, accumulating one orphaned thread (and one un-`SIGTERM`-able zombie) per closed dashboard tab.

The first pass returned BLOCKED ("does not reproduce"); that was a measurement-window artifact — its 12–16 s post-disconnect windows ended before the spin's delayed onset. The orchestrator pinned the live spin and root cause with `sample(1)` ([orchestrator_root_cause.md](attachments/orchestrator_root_cause.md), [orchestrator_sample_main_72994.txt](attachments/orchestrator_sample_main_72994.txt)); this fix lands against that real red.

### The fix

- New module state `_worktree_stop_events: dict[str, asyncio.Event]` ([plan_dashboard.py:107](../../../../../skills/task-tree/scripts/plan_dashboard.py#L107)).
- `_watch_worktree(wt, stop_event)` passes the event straight to `awatch(..., stop_event=stop_event)` ([plan_dashboard.py:435](../../../../../skills/task-tree/scripts/plan_dashboard.py#L435)).
- `_ensure_watcher` mints a fresh `asyncio.Event` per spawn and stores it before creating the task ([plan_dashboard.py:499](../../../../../skills/task-tree/scripts/plan_dashboard.py#L499)). The fresh-per-spawn event preserves the **crashed-watcher-respawn guard**: a respawn after a `done()` watcher starts with an unset event, never torn down by a stale prior-generation signal. The per-worktree lock is unchanged.
- `_stop_watcher` pops both task and event under the lock, then **sets the event** (no `task.cancel()`) and awaits the task ([plan_dashboard.py:517](../../../../../skills/task-tree/scripts/plan_dashboard.py#L517)).

**One follow-on found and fixed during live verification.** Because `_stop_watcher` runs inside the disconnecting SSE generator's `finally` ([plan_dashboard.py:956](../../../../../skills/task-tree/scripts/plan_dashboard.py#L956)), awaiting the watcher task there exposes a *benign* watchfiles teardown-race in `awatch` itself — `UnboundLocalError: ... 'raw_changes'`, raised from its `anyio` task group as it exits (bare at this `await`, or wrapped in a `BaseExceptionGroup`). By that point the native fd is already closed (the spin is gone), so that specific leaf is not actionable; the pre-fix code surfaced it as a noisy 500-style ASGI traceback on every disconnect. `_stop_watcher` now swallows **only** that leaf, via the `_is_benign_awatch_teardown_race` predicate ([plan_dashboard.py:504](../../../../../skills/task-tree/scripts/plan_dashboard.py#L504)) applied both to a bare exception and (through `BaseExceptionGroup.split`) to a group — re-raising any group remainder or any non-benign exception so a **genuine watcher crash** (a fault in `_rebuild_and_broadcast` / tree-parse / disk error) is never hidden, since this `await task` is the only observer of the watcher task's exception. This is the spirit of candidate (c)'s "cancellation races connection teardown" caveat, handled at the teardown site rather than by relocating `_stop_watcher` out of the `finally` (which would be a larger structural change to the SSE path and is unnecessary — the stop event already releases the native resources).

`watchfiles` is **not pinned** and was left so: the root cause is our teardown (cancel vs. cooperative stop), not a watchfiles-version bug, so no `pyproject.toml` change is warranted.

### Red → green regression test

[test_multi_worktree.py `test_stop_watcher_closes_native_watcher_thread`](../../../../../skills/task-tree/scripts/test_multi_worktree.py#L423) drives the real `_ensure_watcher` → `_stop_watcher` lifecycle on a live worktree and asserts the orchestrator's preferred deterministic signal (over flaky wall-clock CPU):

- it patches `anyio.to_thread.run_sync` to count in-flight native `watcher.watch` calls, asserts ≥1 while watching and **0 after** `_stop_watcher` (no leaked native watch thread), and
- asserts the `awatch` task finished **not `cancelled()`** — i.e. by a clean `return`, which is exactly what runs `RustNotify.__exit__`. A hard `task.cancel()` ends the task `cancelled()`.

Captured red→green explicitly:
- **Red** against the pre-fix `task.cancel()` teardown (reverted `_stop_watcher` body in place, ran the test): `FAILED ... AssertionError: watcher was hard-cancelled instead of cooperatively stopped; RustNotify.__exit__ did not run on its own terms` (`<Task cancelled ...>`).
- **Green** after the cooperative-stop fix: `3 passed` (with the two sibling watcher-lifecycle tests).

### Live-process verification — supporting/sanity evidence only ([live_verify.py](attachments/live_verify.py))

The load-bearing red→green evidence is the **deterministic regression test above** (`not task.cancelled()` + native-watch-thread count) plus the orchestrator's `sample` of a live-spinning process ([orchestrator_sample_main_72994.txt](attachments/orchestrator_sample_main_72994.txt)). The live-process run below is **not a discriminating gate**: the server-level spin has a non-deterministic delayed/ramping onset (the same measurement-window artifact that made the first pass read 0.0%), so `live_verify.py` reports PASS against the *pre-fix* `task.cancel()` teardown as well. It is included only as a sanity check that the fixed server idles cleanly and that the ASGI-traceback follow-on is resolved — do not read its PASS as proof the fix changed behavior.

Launched the real in-process server (`plan_dashboard.py serve --foreground`), connected one SSE client to `/events`, disconnected, then `sample <pid> 1`'d the process across a 35 s post-disconnect window:

| Phase | CPU (`ps %cpu`) | `notify-rs fsevents loop` threads |
|---|---|---|
| while connected | 0.0% | 1 |
| t+5 s … t+35 s after disconnect | 0.0% at every sample | 0 at every sample |

`RESULT: PASS`, with **zero** `Exception in ASGI` / `UnboundLocalError` in the server log after the follow-on fix (the pre-fix cooperative-stop-only version logged the traceback on every disconnect; the narrowed catch resolves it while still re-raising any non-benign watcher exception).

### Suite + cleanup

- Full task-tree suite green from live source: **593 passed, 2 skipped** (the new test is the +1 over the prior 592).
- Cleaned up the prior pass's orphaned spinners per the dispatch: PIDs 72994 and 69765 (the BLOCKED pass's leftover `run_server.py`, ~58% each) ignored `SIGTERM` — confirming the objective's "unkillable zombie" symptom — and were `SIGKILL`'d. PID 33961 (the user's real installed dashboard, also spinning at ~58%) was **left running** for the orchestrator to surface to the user; restarting it via `serve` will pick up this fix.
- Removed the prior pass's now-superseded repro scripts/logs from `attachments/` (they documented the overturned non-reproduction); kept the orchestrator diagnostics and `live_verify.py`.
