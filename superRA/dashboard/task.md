---
title: "Dashboard: Deep-Link Buttons, Sidebar Focus, and One-Server Launcher"
status: approved
depends_on: []
---

## Objective

Dashboard improvements and fixes, all in the task-tree dashboard (`skills/task-tree/scripts/`):

1. Add an "Open worktree in VS Code" control that deep-links the active worktree's checkout root into VS Code, alongside the existing per-task "Open task.md" button.
2. Fix the bug where navigating to a task by URL hash on a fresh load does not focus (reveal/expand/highlight) that task's row in the sidebar.
3. Add a short, optional note to the quickstart prerequisite section that the dashboard supports VS Code deep links.
4. Fix the launcher so a repo runs exactly one background server on its deterministic port, reused across worktrees, instead of accumulating duplicate servers that serve stale/wrong-worktree data.

### Context

The dashboard already ships a robust VS Code deep-link mechanism: the per-task "Open task.md" button builds a `vscode://file/<abs_path>` URI (`skills/task-tree/scripts/templates/base.html`, `taskFileVscodeHref`), and the file path already follows the active worktree via `RESOLVED_ROOT` / `PROJECT_ROOT`, which are re-pointed per `?wt=` token when the worktree list loads. The deep-link work extends that same mechanism to open a *folder* (the worktree root) and fixes a sidebar-focus bug on initial deep-link load — the client-side URI-handler design is preserved (no server-side `code` shell-out). The launcher work is server-side (`plan_dashboard.py`): one server per repo, keyed by the git common dir and served to every worktree via `?wt=`.

### Conventions

- Dashboard frontend is the single large `skills/task-tree/scripts/templates/base.html` (inline JS + CSS); server is `skills/task-tree/scripts/plan_dashboard.py`. Tests live under `skills/task-tree/scripts/` (`test_dashboard.py` and friends). `plan_dashboard.py` is bundled tooling that runs in arbitrary target projects — keep it stdlib-only, no `uv`-env provisioning.
- Run the task-tree CLI/tests from live source per the repo CLAUDE.md (`uv run --script`, or `python3` for the stdlib core; tests via `uv run --with pytest --with pyyaml ... python -m pytest skills/task-tree/scripts`).
- Scope every edit to this worktree's absolute path (`/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/dashboard-vscode-worktree`); concurrent superRA worktrees exist.

## Results

All four shipped, verified, and integration-approved. A header "Open worktree in VS Code" deep-link button ([worktree-open-button](worktree-open-button/task.md)); the sidebar deep-link focus fix — expand the umbrella nav container before the ancestor walk so top-level targets are no longer hidden ([sidebar-deeplink-focus](sidebar-deeplink-focus/task.md)); an optional VS Code deep-link note in the quickstart prerequisite ([docs-vscode-note](docs-vscode-note/task.md)); and the one-server-per-repo launcher fix — deterministic port, `/healthz` repo-identity probe, repo-aware reuse/candidate-walk, and no-linger race handling ([single-server](single-server/task.md)). Full `test_dashboard.py` / task-tree script suite: 705 passed.
