---
title: "Background-by-default launch, --foreground flag, idempotent reuse, stop"
status: not-started
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

## Results
