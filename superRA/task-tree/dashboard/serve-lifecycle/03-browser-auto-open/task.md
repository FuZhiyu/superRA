---
title: "Dashboard Browser Auto-Open"
status: approved
depends_on:
  - 02-background-launch

tags: []
created: 2026-06-10
---

## Objective

Fix the background dashboard launcher so `superra dashboard` and idempotent reuse actually open the browser by default after the server is reachable, while preserving `--no-open` and `--foreground` behavior. Add regression coverage for the default background and already-running paths so a daemon-thread race cannot silently disable browser opening again. Verify with the focused task-tree tests and a smoke run that avoids leaving a dashboard process behind.

## Planner Guidance

The diagnosis is that `_open_browser_async()` sleeps on a daemon thread in the short-lived parent process; `serve_background()` returns before that thread reaches `webbrowser.open()`. Prefer a small lifecycle-local fix over broader process-management refactoring.

## Results

### Key Findings
- Fixed the default background launch and already-running reuse paths to call `webbrowser.open(...)` synchronously after the server is confirmed reachable, instead of scheduling `_open_browser_async()` on a daemon thread in the short-lived launcher process ([plan_dashboard.py](/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/rename-task-tree/skills/task-tree/scripts/plan_dashboard.py:1915), [plan_dashboard.py](/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/rename-task-tree/skills/task-tree/scripts/plan_dashboard.py:1969)).
- Preserved the detached child server's `--no-open` flag, so the child process still never opens an extra browser tab; foreground mode still uses `_open_browser_async()` because the foreground server process remains alive.
- Added regression coverage for both default background launch and idempotent reuse, asserting the browser-open call has happened before `serve_background()` returns ([test_task_tree.py](/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/rename-task-tree/skills/task-tree/scripts/test_task_tree.py:4830), [test_task_tree.py](/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/rename-task-tree/skills/task-tree/scripts/test_task_tree.py:4846)).

### Verification
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_task_tree.py::TestBackgroundLaunch -q` — 9 passed.
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` — 612 passed, 2 skipped.
- Smoke launch from outside the git worktree with `--no-open --idle-timeout 2` returned `Dashboard running at http://localhost:8998`; the server self-exited and `stop` removed the stale PID file. Existing unrelated foreground dashboard processes on ports 8996 and 8576 were left running.
