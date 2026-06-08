# Orchestrator diagnostic — the spin reproduces; root cause pinned

The first implementation pass returned BLOCKED ("does not reproduce on this stack"). That was a **measurement-window artifact**, not a non-reproduction. Orchestrator diligence found live spinning processes and pinned the C-level root cause with `sample(1)` (no sudo needed for own-user processes). Recorded here so the fix lands against a real red.

## The spin is live right now

Three processes spinning sustained at ~56% CPU (verified CPU-time advancing ~2.3 s per 4 s wall):

| PID | What it is | Orphaned `notify-rs fsevents loop` threads |
|---|---|---|
| 72994 | first impl pass's own leftover `run_server.py` (this worktree's venv) | 1 |
| 69765 | first impl pass's own leftover `run_server.py` | 1 |
| 33961 | the **real installed dashboard** (`~/.local/share/uv/tools/superra-task-system`, serving a real project's task tree) | **2** (leaks accumulate per disconnect) |

The first pass's own repro servers are spinning at 56% — its 12–16 s post-disconnect measurement windows ended before the spin's delayed onset, so it recorded 0.0% and concluded "no spin." The spin is real and has a delayed/ramping onset.

## Root cause (from `sample` of PID 72994, [orchestrator_sample_main_72994.txt](orchestrator_sample_main_72994.txt))

Main event-loop thread, 2707 samples:
- **~1252** in `select_kqueue_control_impl → kevent` — but returning immediately (near-zero timeout), not idle-blocked.
- **~955** in `context_run → task_step → task_step_impl → …` — the loop is actively stepping a ready task every iteration.

So the loop cycles `kevent(timeout≈0) → task_step → kevent → …` forever instead of sleeping. The driver: the watchfiles **`notify-rs fsevents loop` native (Rust) thread is still alive after `_stop_watcher`**. `_stop_watcher` does `task.cancel()` on the `awatch` async generator ([plan_dashboard.py:487](../../../../../skills/task-system/scripts/plan_dashboard.py#L487)), which unwinds the Python coroutine but never runs `RustNotify.__exit__` — so the native fsevents source/fd is never closed. The orphaned source keeps the kqueue perpetually readable, waking the loop on every pass. Each disconnect orphans one more native thread (PID 33961 shows two), which is why CPU climbs and zombies accumulate.

## What this means for the fix and its validation gate

- The objective's red→green gate **is** achievable; the first pass just didn't capture the red. Capture it with either a longer post-disconnect window, or — preferred, deterministic — an assertion that **no `watchfiles`/`notify-rs` native watcher thread survives `_stop_watcher`** (red under the current `task.cancel()`, green after the fix).
- The fix is candidate (a): cooperative `watchfiles.awatch(..., stop_event=…)` set in `_stop_watcher` instead of `task.cancel()`, so the watch loop reaches its clean `return` and `RustNotify.__exit__` closes the native thread/fd. Preserve the per-worktree lock and crashed-watcher-respawn guard.
- Env angle is secondary: the leak is in *our* teardown (cancel vs. cooperative stop), not strictly a watchfiles-version bug — though pinning a known-good `watchfiles` is reasonable defense-in-depth.

The three live spinning PIDs are safe to kill once a fresh red is captured (33961 is the user's real dashboard — killing it only stops a uselessly-spinning server; it will relaunch on next `serve`).
