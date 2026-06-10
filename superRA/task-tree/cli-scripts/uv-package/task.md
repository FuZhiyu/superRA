---
title: "Package task-tree for uv"
status: approved
depends_on: []
tags: []
created: 2026-06-02
---

## Objective

Make the task-tree code runnable as a Python package from `skills/task-tree/` through `uv`, while preserving existing direct script invocations during the transition.

### Scope

- Add package metadata under `skills/task-tree/` rather than repo root.
- Move or expose runtime modules under a package namespace suitable for console entry points, e.g. `superra_task_tree`.
- Package dashboard `templates/` and `vendor/` assets so installed wheels and `uvx --from` executions can render the dashboard without source-relative path assumptions.
- Define console entry points for the stable task-tree CLI. The primary command should be `superra`; a dashboard alias may be kept only if it reduces friction without creating a second source of truth.
- Keep compatibility wrappers for existing `skills/task-tree/scripts/*.py` commands until all active docs, hooks, and tests have migrated.

### Validation

- `uvx --from ./skills/task-tree superra task --help` runs in this checkout.
- `uvx --from ./skills/task-tree superra dashboard --help` runs without importing modules from `skills/task-tree/scripts` via `sys.path` hacks.
- Existing direct invocations used by the current tests still work.

## Planner Guidance

Use `importlib.resources` or an equivalent package-data mechanism for dashboard templates and vendored assets. Avoid adding a root `pyproject.toml` unless package tooling proves impossible under `skills/task-tree/`.

## Results

### Key Findings

- Added `skills/task-tree/pyproject.toml` so `uvx --from ./skills/task-tree superra ...` builds the task-tree utility as the `superra-task-tree` package, exposes the `superra` console script, maps the package namespace to the existing `scripts/` directory, and includes dashboard templates/vendor/font assets as package data ([../../../../skills/task-tree/pyproject.toml:1](../../../../skills/task-tree/pyproject.toml#L1)).
- Added a packaged `superra` CLI that keeps `superra dashboard` as the top-level dashboard command, exposes the stable `superra task ...` command groups, delegates to existing script modules for transition compatibility, and does not register `superra task dashboard` ([../../../../skills/task-tree/scripts/cli.py:37](../../../../skills/task-tree/scripts/cli.py#L37), [../../../../skills/task-tree/scripts/cli.py:179](../../../../skills/task-tree/scripts/cli.py#L179), [../../../../skills/task-tree/scripts/cli.py:190](../../../../skills/task-tree/scripts/cli.py#L190)).
- Added the package namespace marker for the existing scripts directory and updated dashboard resource lookup so package imports use `PackageLoader` / `importlib.resources` while direct script execution keeps the existing source-directory fallback ([../../../../skills/task-tree/scripts/__init__.py:1](../../../../skills/task-tree/scripts/__init__.py#L1), [../../../../skills/task-tree/scripts/plan_dashboard.py:301](../../../../skills/task-tree/scripts/plan_dashboard.py#L301), [../../../../skills/task-tree/scripts/plan_dashboard.py:1034](../../../../skills/task-tree/scripts/plan_dashboard.py#L1034)).
- Fixed the packaged hook dispatcher so `superra task hook post-tool-use` calls `task_hook.main()` without an argv parameter, while leaving direct script execution unchanged ([../../../../skills/task-tree/scripts/cli.py:11](../../../../skills/task-tree/scripts/cli.py#L11), [../../../../skills/task-tree/scripts/cli.py:170](../../../../skills/task-tree/scripts/cli.py#L170)).
- Removed task-root `serve` wrapper generation from task creation, so both packaged and direct `task_create.py` paths create only the task directory/file and preserve any pre-existing `serve` file without writing a new one ([../../../../skills/task-tree/scripts/task_create.py:51](../../../../skills/task-tree/scripts/task_create.py#L51), [../../../../skills/task-tree/scripts/test_task_tree.py:520](../../../../skills/task-tree/scripts/test_task_tree.py#L520)).
- Bumped the local package version through `0.1.2` so `uvx --from ./skills/task-tree` rebuilds the revised package in environments that cached earlier local smoke-test wheels ([../../../../skills/task-tree/pyproject.toml:7](../../../../skills/task-tree/pyproject.toml#L7), [../../../../skills/task-tree/scripts/__init__.py:7](../../../../skills/task-tree/scripts/__init__.py#L7)).

### Verification

- `python3 -m py_compile skills/task-tree/scripts/cli.py skills/task-tree/scripts/plan_dashboard.py`
- `uvx --from ./skills/task-tree superra task --help`
- `uvx --from ./skills/task-tree superra dashboard --help`
- `uvx --from ./skills/task-tree superra task dashboard --help` exits 2 with `invalid choice: 'dashboard'`, confirming the package CLI does not expose the rejected command shape.
- `uvx --from ./skills/task-tree superra dashboard export --root superRA --output /tmp/superra-package-dashboard.html --subtree task-tree/cli-scripts/uv-package`
- `uvx --from ./skills/task-tree superra task read task-tree/cli-scripts/uv-package --root superRA --no-ancestors`
- `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py -v` passed 210 tests.
- `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_dashboard.py skills/task-tree/scripts/test_worktree_selector.py -v` passed 132 tests.
- `python3 -m py_compile skills/task-tree/scripts/cli.py skills/task-tree/scripts/task_create.py skills/task-tree/scripts/task_hook.py`
- `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py::TestTaskCreate skills/task-tree/scripts/test_task_tree.py::TestTaskHook -v` passed 24 tests.
- `uvx --from ./skills/task-tree superra task hook post-tool-use`
- `uvx --from ./skills/task-tree superra task create root-task --root "$tmpdir/superRA" --title "Root Task"` on a fresh temporary task tree, followed by `test ! -e "$tmpdir/superRA/serve"`.
