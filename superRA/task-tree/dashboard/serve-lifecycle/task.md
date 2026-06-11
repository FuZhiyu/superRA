---
title: "Background-by-default serving with idle auto-shutdown"
status: approved
depends_on:
  - multi-worktree-serving
tags: []
created: 2026-06-04
---

## Objective

Make the dashboard server **self-managing** so launching it is fire-and-forget for both agents and humans: it runs in the background by default (returning the terminal immediately), reuses an already-running server instead of spawning a duplicate, and exits on its own after a period with no open tabs. The headline invariant: **the server exits after 5 continuous minutes with zero open tabs across all worktrees.** A foreground/console mode stays available behind a flag.

**The problem.** `serve` runs `uvicorn.run(app, …)` — a foreground, blocking process held until Ctrl+C ([plan_dashboard.py:1631](../../../../skills/task-tree/scripts/plan_dashboard.py#L1631)). The per-worktree *watcher* layer is already lazy and self-cleaning — a worktree's watcher starts on its first `/events` client and is torn down by `_stop_watcher` when that worktree's last client detaches ([plan_dashboard.py:801](../../../../skills/task-tree/scripts/plan_dashboard.py#L801)) — but the **server process itself never exits** while idle. With one shared server/port per repo across many worktrees and sessions ([plan_dashboard.py:1529](../../../../skills/task-tree/scripts/plan_dashboard.py#L1529)), foreground serving either blocks a terminal or, when backgrounded by hand, leaks orphan processes nobody cleans up. The fix lifts the watcher layer's already-proven "self-clean when the last client leaves" idea up to the process, and removes the manual-backgrounding burden.

**The shape of the fix** (decomposed into the child tasks):

- **[01 — idle auto-shutdown](01-idle-shutdown/task.md).** A background monitor exits the server after 5 continuous minutes with zero open SSE connections summed across all worktrees, with periodic heartbeats so dead connections (laptop sleep, dropped network) are pruned rather than counted as live forever. This is the linchpin: it is what makes background-by-default *safe to leak* — a detached server always self-cleans within the idle window.
- **[02 — background launch, `--foreground`, idempotent reuse, stop](02-background-launch/task.md).** `serve` detaches a background child by default, waits for it to bind, prints the URL + PID + log path, and returns; `--foreground` keeps it blocking in the current terminal with logs on stdout; an already-running server for this repo is reused (open a tab, do not spawn a second); a `stop` subcommand terminates the background server. Depends on 01 — land the self-cleaning behavior before defaulting to background.

### Design decisions (settled at planning; reopen via the change protocol if implementation invalidates them)

1. **"Idle" = no open tab, not no focused tab.** The signal is the count of live `/events` SSE connections summed across all worktrees. An open-but-unfocused/background tab keeps its `EventSource` alive and **counts as a client**; only closing the tab (or a dropped connection) decrements it. Focus/visibility-based shutdown was considered and rejected: it would kill the server on every alt-tab to the editor, and it tears the server down *while a tab is still open*, sending that tab's auto-reconnecting `EventSource` into a connection-refused loop.
2. **Idle timeout = 5 minutes, continuous.** The timer runs from process start (zero tabs at launch); any open connection holds it; it fires only after 5 unbroken minutes at zero. A server nobody ever opens therefore exits ~5 minutes after launch, which is correct — nobody is using it.
3. **Self-exit via a `uvicorn.Server` handle, not `uvicorn.run`.** The serve path instantiates `uvicorn.Server(Config(...))` so a monitor coroutine can set `server.should_exit = True`; `uvicorn.run` exposes no such handle. The foreground path uses the same mechanism so its lifecycle matches background.
4. **Heartbeat pruning is required for an accurate count.** A periodic SSE heartbeat (the existing initial-only `: heartbeat` at [plan_dashboard.py:791](../../../../skills/task-tree/scripts/plan_dashboard.py#L791) becomes periodic) forces a broken-pipe on dead connections so the per-worktree client sets shrink; otherwise a zombie connection (slept laptop) keeps the server alive indefinitely.
5. **Background is the default; `--foreground` is the opt-in.** Default `serve` detaches a child in a new session (`start_new_session`), redirects its stdout/stderr to a log file, writes a PID file, polls the port until it binds (short timeout), prints URL + PID + log path, opens the browser unless `--no-open`, and returns 0. **On bind failure within the timeout, print the tail of the log and exit non-zero** so a startup error (port conflict, traceback) is surfaced, not swallowed. `--foreground` runs the server blocking in the current process with logs on stdout.
6. **Self-daemonize, do not rely on the harness.** A detached, self-cleaning server is correct for agents precisely because it auto-exits within the idle window; agents that need to watch logs use `--foreground` under their harness's background-run facility. The launch must detach cleanly enough to survive the launching shell exiting (proper new-session detachment + stdio redirected to the log file).
7. **Idempotent launch.** Before spawning, check the PID file and port for this repo: if a healthy dashboard is already serving, **do not spawn a second** — open a browser tab (unless `--no-open`) and report "already running". A stale PID file (process gone) is cleaned up and a fresh server is spawned. This pairs with the existing one-port-per-repo derivation.
8. **`stop` subcommand.** `stop` reads the PID file and terminates the background server for this repo; it is a no-op (clean exit) when nothing is running.
9. **PID/log files are per-repo, under the git common dir.** Both are keyed to the same repo identity as the port (`git_common_dir`, [plan_dashboard.py:1607](../../../../skills/task-tree/scripts/plan_dashboard.py#L1607)) and stored under that common dir (e.g. `<git-common-dir>/superra-dashboard.pid` / `.log`), so they are repo-scoped, shared across the repo's worktrees (matching one-server-per-repo), and cleaned with the repo. Fall back to plan-root keying when there is no git common dir, mirroring `_default_port`.
10. **Bind loopback by default; `--host` is the LAN opt-in.** The server is unauthenticated and exposes project files (`/files/{path}`), the full task tree (`/export`), and disk-writing comment routes. Background-by-default makes any binding a long-lived ambient surface, so it must default to `127.0.0.1` (loopback only), consistent with every printed `http://localhost:<port>` URL. An explicit `--host` flag (e.g. `--host 0.0.0.0`) is the deliberate opt-in for trusted-LAN serving; it threads through both the foreground `serve()` and the detached background child so the two bind identically. (Recorded post-implementation: the original serve path bound `0.0.0.0` with no opt-in — corrected to this loopback default.)

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Concurrent worktrees of this repo exist; keep all edits and commits on this worktree's branch.

This task touches `skills/task-tree/scripts/*` (the task-tree package) only. No Codex-generated agent files are involved. Treat `plan_dashboard.py` as skill-package code; do not hand-edit any `skills/task-tree/build/lib/...` build output.

Run the CLI and tests from live source:

- CLI: `uv run --project skills/task-tree superra dashboard …` (or `… plan_dashboard.py serve …`).
- Tests: `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`.

### User-facing doc surfaces to keep current

The launch behavior is documented in three places that the [serve-docs](../serve-docs/task.md) task established as the owners; update them in the task that changes behavior (mostly 02):

- `skills/task-tree/SKILL.md` §Dashboard — the canonical CLI form, now background-by-default plus `--foreground` / `stop`.
- `skills/task-tree/references/internals.md` §Dashboard — cross-references SKILL.md; note the self-exit-on-idle lifecycle.
- `README.md` — the one-line dashboard mention stays accurate (launch returns immediately; server self-exits when idle).

There is no separate serve wrapper to update: launching goes through `superra dashboard` itself, which returns faster under background-default (the legacy `.plan/serve` shortcut is gone with the `.plan/` → `superRA/` rename).

## Validation

Against one running server (one port) over this repo:

- `serve` (default) returns to the shell promptly, having printed the URL, PID, and log path, with the browser opening to a working dashboard; a second `serve` while it is running does **not** start a second process — it reports "already running" and (unless `--no-open`) opens a tab.
- `serve --foreground` blocks the terminal with logs on stdout (today's behavior, minus the manual Ctrl+C-only lifecycle).
- With every tab closed, the background server exits on its own within the idle window; with the idle timeout shrunk for the test, this is deterministic. While at least one tab is open, it does **not** exit.
- A dead/zombie connection (simulated) is pruned by the heartbeat so it does not hold the server open.
- `stop` terminates a running background server and is a clean no-op when none is running. A stale PID file does not block a fresh launch.
- A `serve` that fails to bind (e.g. forced port conflict) exits non-zero and surfaces the underlying error rather than silently backgrounding a dead process.
- The full task-tree suite passes, including new idle-shutdown and launch-lifecycle tests.

## Planner Guidance

- Build on the per-worktree client registry from multi-worktree-serving — `_worktree_clients` / `_worktree_watchers` / `_worktree_locks` ([plan_dashboard.py:83](../../../../skills/task-tree/scripts/plan_dashboard.py#L83)). The global open-connection count for the idle monitor is `sum(len(s) for s in _worktree_clients.values())`; the monitor lives alongside the per-worktree watchers, not inside them.
- 01 is server-internal and low-risk; 02 is the process-management surface (detachment, PID/log files, bind-wait, idempotency) and carries the portability risk. Land and review 01 first so background-default ships only once self-clean is proven.
- Keep the `lifespan` watcher-teardown ([plan_dashboard.py:603](../../../../skills/task-tree/scripts/plan_dashboard.py#L603)) intact; the idle monitor triggers a clean server shutdown, after which lifespan still cancels every watcher.
- Mirror the multi-worktree-serving subtree's decomposition and Results-citation style (file links + line ranges).

## Critical Files

- [`skills/task-tree/scripts/plan_dashboard.py`](../../../../skills/task-tree/scripts/plan_dashboard.py) — the server and the `serve` CLI; both child tasks live here.
- [`skills/task-tree/scripts/test_dashboard.py`](../../../../skills/task-tree/scripts/test_dashboard.py) — server test patterns (TestClient, fixtures) the new tests extend.
- [`superRA/task-tree/dashboard/multi-worktree-serving/`](../multi-worktree-serving) — the sibling whose per-worktree client tracking this builds on, and the decomposition/citation style to mirror.

## Results

The dashboard server is now self-managing, so launching it is fire-and-forget for both agents and humans. `serve` launches in the **background by default** and returns the shell immediately; a second launch for the same repo **reuses the running server** instead of spawning a duplicate; and the server **exits on its own after 5 continuous minutes with zero open tabs**. `--foreground` keeps a blocking console mode, and `stop` terminates the background server. Because a detached server always self-cleans within the idle window, background-by-default carries no orphan cost — the concern that originally argued against it.

**[01 — idle auto-shutdown](01-idle-shutdown/task.md)** (approved). The serve path moved to a `uvicorn.Server` handle so a single process-wide idle monitor can request graceful shutdown. It exits once the open-connection count — `sum(len(s) for s in _worktree_clients.values())`, summed across all worktrees — has been zero continuously for `IDLE_TIMEOUT` (default 300 s, injectable for tests), and periodic SSE heartbeats prune dead connections so a slept-laptop zombie cannot hold the server open. "Idle" is no-open-tab, not no-focused-tab (design decision 1).

**[02 — background launch + stop](02-background-launch/task.md)** (approved). A thin supervisor spawns that in-process server detached (new session, stdio to a log file under the git common dir), waits for bind, writes a `<pid> <port>` PID file, and prints URL + PID + log path. Idempotent reuse probes the **recorded bound port** — necessary because `_default_port` walks to the next free port when its derived port is occupied, so a later launch's freshly derived port can differ from what the running server actually bound. Bind failure surfaces a non-zero exit with the log tail rather than leaking a dead background process; `stop` terminates (SIGTERM→SIGKILL) and clears the PID file. PID/log files are keyed to the git common dir, shared across the repo's worktrees, matching one-server-per-repo. Docs (SKILL.md §Dashboard, internals.md, README.md) updated to the new lifecycle.

**Verification.** Full task-tree suite green from live source — **484 passed** (461 baseline + 23 new across `TestIdleShutdownLifespan`, `TestRuntimeFileKeying`, `TestPidHelpers`, `TestBackgroundLaunch`). The real `superra dashboard` CLI path was driven end-to-end: background launch returns in ~0.8 s, idempotent reuse (same PID, no duplicate), `stop` + clean no-op second stop, `--foreground` blocking with idle self-exit, and detachment surviving the launching subshell's exit — with no leaked dashboard processes.

