---
title: "Background-by-default launch, --foreground flag, idempotent reuse, stop"
status: approved
depends_on:
  - 01-idle-shutdown
tags: []
created: 2026-06-04
---

## Objective

Change `serve` so it **backgrounds by default**: spawn the server detached, wait for it to bind, print the URL + PID + log path, open the browser, and return the shell — instead of blocking on `uvicorn.run` ([plan_dashboard.py:1631](../../../../../skills/task-system/scripts/plan_dashboard.py#L1631)). Add a `--foreground` flag for the old blocking/console behavior, make launch idempotent (reuse a running server rather than spawn a duplicate), and add a `stop` subcommand. This is the process-management half of the [parent](../task.md) feature; it depends on [01-idle-shutdown](../01-idle-shutdown/task.md) because background-default is only safe once the server self-cleans. The parent's design decisions 5–9 are binding here.

**Concretely:**

1. **Background by default.** Default `serve` launches the server in a new session (detached so it survives the launching shell — e.g. `subprocess.Popen(..., start_new_session=True)` re-invoking the foreground path, or an equivalent clean double-fork), with the child's stdout/stderr redirected to the log file. The parent waits by **polling the port until it binds** (short timeout); on success it prints the URL, PID, and log path and opens the browser unless `--no-open`, then exits 0. **On bind failure within the timeout it prints the tail of the log and exits non-zero** so a startup error (port conflict, traceback) surfaces instead of leaving a dead background process. The detached child runs the foreground serve path from 01 (the `uvicorn.Server` + idle monitor), so the background server self-exits on idle like any other.
2. **`--foreground` flag.** Runs the server blocking in the current process with logs on stdout — today's behavior minus the Ctrl+C-only lifecycle (it also self-exits on idle via 01). This is the console/debug mode.
3. **Idempotent launch.** Before spawning, check the PID file and the repo's port: if a healthy dashboard for this repo is already serving, do **not** spawn a second — report "already running at `<url>`" and open a browser tab unless `--no-open`. A stale PID file (no live process / port not actually serving) is cleaned up and a fresh server is spawned.
4. **`stop` subcommand.** Reads the PID file and terminates the background server for this repo; a clean no-op when nothing is running. Remove the PID file on stop.
5. **PID/log file location.** Both are keyed to the same repo identity as the port — `git_common_dir` ([plan_dashboard.py:1607](../../../../../skills/task-system/scripts/plan_dashboard.py#L1607)) — and stored under it (e.g. `<git-common-dir>/superra-dashboard.pid` and `.log`), so they are repo-scoped and shared across the repo's worktrees, matching one-server-per-repo. Fall back to plan-root keying when there is no git common dir, mirroring `_default_port` ([plan_dashboard.py:1529](../../../../../skills/task-system/scripts/plan_dashboard.py#L1529)).

**Doc updates (this task, per [serve-docs](../../serve-docs/task.md) ownership):**

- `skills/task-system/SKILL.md` §Dashboard — make the canonical CLI form reflect background-by-default, `--foreground`, and `stop`; keep it concise.
- `skills/task-system/references/internals.md` §Dashboard — note the new lifecycle (returns immediately; reuses a running server; self-exits on idle), cross-referencing SKILL.md rather than duplicating.
- `README.md` — keep the one-line dashboard mention accurate.

## Validation

- **Backgrounds and returns:** default `serve` returns to the shell promptly after printing URL + PID + log path; the dashboard is reachable and the browser opened (unless `--no-open`). The process survives the launching shell exiting.
- **Idempotent:** a second `serve` while one is running prints "already running" and does not start a second process (verify via PID file / `pgrep` / port owner); with `--no-open` it does not open a tab.
- **Foreground:** `serve --foreground` blocks with logs on stdout and serves correctly.
- **Stop:** `stop` terminates a running background server and removes the PID file; `stop` with nothing running exits cleanly. A stale PID file does not block a fresh `serve`.
- **Bind failure surfaces:** a `serve` forced into a bind failure exits non-zero and prints the underlying error/log tail rather than silently backgrounding a dead process.
- **Self-exit intact:** a backgrounded server with all tabs closed still self-exits within the (test-shrunk) idle window from 01.
- **Suite green:** the full task-system suite passes (`uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts -q`).

## Planner Guidance

- The cleanest structure: keep one internal "run the server in this process" entry (the 01 `uvicorn.Server` path) and have both `--foreground` and the detached child call it; the default `serve` becomes a thin supervisor that spawns that child, waits for bind, writes the PID file, and returns.
- Reuse the existing port derivation and `get_git_common_dir()` ([plan_dashboard.py:1607](../../../../../skills/task-system/scripts/plan_dashboard.py#L1607)) for the repo key; do not invent a second repo-identity scheme.
- Process-spawning tests are heavier than unit tests — a pragmatic approach is to launch a real background server with a sub-second idle timeout and assert: it returns, the PID file appears, a second launch is rejected, `stop` works, and it self-exits. Keep these few and deterministic.
- Detachment correctness is the main portability risk (macOS/darwin): verify the child genuinely outlives the parent shell and that stdio is redirected to the log file (no inherited TTY).
- **Carry-forward MINOR cleanups from [01's review](../01-idle-shutdown/task.md) — resolve in-lane since you are already editing this file and test module:** (a) the comment near the idle constants at the top of `plan_dashboard.py` references a nonexistent `_idle_timeout` symbol and misdescribes timeout injection — reword it to the actual mechanism (`_idle_monitor`'s `timeout` parameter; `lifespan` reads `IDLE_TIMEOUT` at launch); (b) remove the dead `import uvicorn` left in `main()` after that import moved into `serve()`; (c) add a lifespan-level regression test that drives the real `lifespan` with a sub-second `IDLE_TIMEOUT` and asserts the server self-exits while idle, stays up while a client is connected, and drains watchers — plus a heartbeat-prunes-a-dead-connection test — locking in the linchpin behavior beyond the existing pure-function unit tests.

## Results

`serve` is now background-by-default: a thin supervisor spawns the in-process server detached, waits for it to bind, writes a PID file, prints URL + PID + log path, and returns the shell. `--foreground` keeps the blocking/console behavior, launch is idempotent, and a `stop` subcommand terminates the background server. 23 new tests cover the new code; full suite 484 passed (461 baseline + 23).

### What changed in [plan_dashboard.py](../../../../../skills/task-system/scripts/plan_dashboard.py)

**One in-process serve path, two callers.** `serve(port)` ([plan_dashboard.py:1638](../../../../../skills/task-system/scripts/plan_dashboard.py#L1638)) stays the single `uvicorn.Server` + idle-monitor entry from 01. Both `--foreground` (in `main`) and the detached background child call it, so the background server self-exits on idle exactly like a foreground one — this is what makes background-default safe to leak (parent design decision 6).

**Supervisor layer** ([plan_dashboard.py:1803-1902](../../../../../skills/task-system/scripts/plan_dashboard.py#L1803-L1902)). `serve_background(plan_root, port, git_common_dir, ...)`:
- **Idempotent reuse** — `_running_pid` ([plan_dashboard.py:1761](../../../../../skills/task-system/scripts/plan_dashboard.py#L1761)) checks the PID file and probes the recorded port; if a live process is serving it, the launch reports "already running" and opens a tab (unless `--no-open`) instead of spawning a second. A stale PID file (dead process / port not serving) is cleaned up and a fresh server spawned.
- **Detachment** — `subprocess.Popen(..., start_new_session=True, stdin=DEVNULL, stdout=stderr=log file)` re-invokes the script's foreground path. New session + no inherited TTY means the child survives the launching shell exiting (verified manually: a server launched inside a subshell stayed reachable after that subshell exited).
- **Bind wait / failure** — `_wait_for_bind` ([plan_dashboard.py:1782](../../../../../skills/task-system/scripts/plan_dashboard.py#L1782)) polls the port; on success the PID file is written and URL/PID/log printed; on timeout the child is terminated, the log tail is printed to stderr, and the call returns non-zero so a startup error (port conflict, traceback) surfaces rather than leaving a dead background process.

**`stop_background`** ([plan_dashboard.py:1931](../../../../../skills/task-system/scripts/plan_dashboard.py#L1931)) reads the PID file, terminates the process (SIGTERM then SIGKILL, via `_terminate` at [plan_dashboard.py:1904](../../../../../skills/task-system/scripts/plan_dashboard.py#L1904)), and removes the PID file. Clean no-op (exit 0) when nothing is running or the PID file is stale.

**PID/log file keying** ([plan_dashboard.py:1670-1685](../../../../../skills/task-system/scripts/plan_dashboard.py#L1670-L1685)). `superra-dashboard.pid` / `.log` live under `_runtime_dir` = the git common dir (falling back to plan root, mirroring `_default_port`), so they share the repo identity of the port and are visible to all the repo's worktrees — matching one-server-per-repo.

**PID file records `<pid> <port>`** ([plan_dashboard.py:1688-1723](../../../../../skills/task-system/scripts/plan_dashboard.py#L1688-L1723)). The deterministic `_default_port` walks to the next free port when its derived port is occupied, so a freshly derived port on a later launch can differ from the port the running server actually bound. Recording the port and probing *that* on reuse is what makes the idempotency check correct; `_read_pid` stays back-compatible (returns pid only, tolerates a legacy pid-only file).

**Zombie-safe liveness** ([plan_dashboard.py:1725-1751](../../../../../skills/task-system/scripts/plan_dashboard.py#L1725-L1751)). `_pid_alive` reaps a terminated child (non-blocking `waitpid`) before the signal-0 probe, so when launch and stop run in the same interpreter (tests) a just-killed child is reported dead rather than lingering as a zombie. In normal CLI use launch and stop are separate processes and the `waitpid` is a no-op.

**CLI surface.** `serve --foreground` and `--idle-timeout` (hidden testing knob) added to `plan_dashboard.py`'s `serve` subparser; new `stop` subparser; `main` routes foreground/background and the `stop` branch ([plan_dashboard.py:2028-2070](../../../../../skills/task-system/scripts/plan_dashboard.py#L2028-L2070)). The packaged `superra dashboard` wrapper ([cli.py:84](../../../../../skills/task-system/scripts/cli.py#L84), [cli.py:241](../../../../../skills/task-system/scripts/cli.py#L241)) gains `--foreground` pass-through and a `dashboard stop` subcommand.

### Carried-forward 01-review MINORs (resolved in-lane)

- **(a) Stale comment** — the idle-constant comment ([plan_dashboard.py:66-69](../../../../../skills/task-system/scripts/plan_dashboard.py#L66-L69)) referenced a nonexistent `_idle_timeout` symbol; reworded to the real injection (`_idle_monitor`'s `timeout` parameter, or set `IDLE_TIMEOUT` before launch and `lifespan` reads it).
- **(b) Dead import** — removed the unused `import uvicorn` from `main()`.
- **(c) Lifespan/heartbeat regression tests** — added `TestIdleShutdownLifespan` ([test_task_system.py:3751](../../../../../skills/task-system/scripts/test_task_system.py#L3751)): drives the real `serve()`/`lifespan` with a sub-second `IDLE_TIMEOUT` and asserts the server self-exits while idle, stays up across several windows while an `/events` client is connected, and that the periodic heartbeat prunes a dropped SSE connection from the open count.

### Tests ([test_task_system.py](../../../../../skills/task-system/scripts/test_task_system.py))

- `TestIdleShutdownLifespan` (3) — real-server self-exit / stays-up-while-connected / heartbeat-prunes-dead-connection.
- `TestRuntimeFileKeying` (3) — PID/log keyed to git common dir, plan-root fallback, shared across a repo's worktrees.
- `TestPidHelpers` (10) — `_read_pid` / `_read_pid_port` parsing (incl. legacy pid-only), liveness probe, stale-file cleanup, recorded-port reuse.
- `TestBackgroundLaunch` (7) — background launch writes PID + returns; idempotent second launch reuses (same PID); `stop` terminates + removes PID; `stop` no-op when nothing running; stale PID file does not block a fresh launch; bind failure exits non-zero with no leaked PID file; a backgrounded server with no clients self-exits within a shrunk idle window.

```
uv run --project skills/task-system --with pytest --with httpx \
    python -m pytest skills/task-system/scripts -q
# 484 passed, 4 warnings in 46.47s
```

Manual end-to-end (real `superra dashboard` CLI, this repo's `superRA/` tree): default launch returns in ~0.8s printing URL + PID + log path; a second launch reports "already running" with the same PID/port (no duplicate); `stop` terminates it; a second `stop` is a clean no-op; `--foreground` blocks with uvicorn logs on stdout and self-exits on a shrunk idle timeout; a server launched inside a subshell survived that subshell exiting. No leaked dashboard processes after the full suite.

### Docs updated (per [serve-docs](../../serve-docs/task.md) ownership)

- [SKILL.md §Dashboard routing](../../../../../skills/task-system/SKILL.md) — the dashboard row now states background-by-default, reuse, `--foreground`, and `stop`.
- [internals.md §Dashboard](../../../../../skills/task-system/references/internals.md) — added a **Lifecycle** paragraph (returns immediately, reuses a running server, self-exits on idle, PID/log under the git common dir) and the `--foreground` / `stop` command forms.
- [README.md](../../../../../README.md) — the one-line dashboard mention now notes it launches in the background, reuses a running server, and self-exits when idle.

## Review Notes

Approved — objective met and verified end-to-end (real CLI: background launch returns immediately printing URL + PID + log path under the git common dir; second launch reuses the same PID without spawning a duplicate; `stop` terminates and removes the PID file; second `stop` is a clean no-op; `--foreground` blocks and serves). Full suite re-run independently: 484 passed. The two items below are non-blocking cleanups for whoever next edits this test module.

→ orchestrator: both resolved inline at Step 3 — dead `_spawn`/`_port` helpers and the stale docstring phrasing removed; the global `IDLE_TIMEOUT` set scoped to the `--foreground` branch (the background path already passes `idle_timeout` to the child). Verified by a full-suite re-run.

1. MINOR — dead test helpers. [test_task_system.py:4022-4030](../../../../../skills/task-system/scripts/test_task_system.py#L4022-L4030): `TestBackgroundLaunch._spawn` and `._port` are defined but never called — every test in the class re-derives `TestIdleShutdownLifespan()._free_port()` inline and calls `serve_background` directly. Remove the unused helpers (and the class docstring's "via IDLE_TIMEOUT in its environment-independent default" phrasing, which no longer matches how `idle_timeout` is actually passed).

2. MINOR — redundant global mutation in the supervisor branch. [plan_dashboard.py:2040-2042](../../../../../skills/task-system/scripts/plan_dashboard.py#L2040-L2042): when `--idle-timeout` is set without `--foreground`, `main` sets the module-global `IDLE_TIMEOUT` and then calls `serve_background(..., idle_timeout=args.idle_timeout)`. The supervisor parent never calls `serve()`, so the parent's global mutation has no effect (the child receives the value via its `--idle-timeout` CLI arg). Harmless but dead; the global set can be scoped to the `--foreground` branch.
