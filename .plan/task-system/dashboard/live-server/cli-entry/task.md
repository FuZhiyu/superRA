---
title: "CLI entry point and uv run integration"
status: implemented
review_status: implemented
integration_status: ~
depends_on:
  - ../server
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Provide a single-command entry point for launching the live dashboard, with zero-install setup via `uv run --with`.

**CLI interface:**
- `plan-dashboard serve [--root .plan/] [--port 8080] [--no-open]`
- `--root` — path to the `.plan/` directory (default: `.plan/` in cwd)
- `--port` — server port (default: 8080)
- `--no-open` — skip auto-opening the browser
- On launch: start uvicorn, print URL, open browser via `webbrowser.open()`

**uv integration:**
- The script should work as `uv run --with fastapi,uvicorn,jinja2,watchfiles plan_dashboard.py serve`
- Add inline script metadata (PEP 723) at the top of `plan_dashboard.py` so `uv run plan_dashboard.py serve` auto-resolves dependencies without `--with`:
  ```python
  # /// script
  # requires-python = ">=3.10"
  # dependencies = ["fastapi", "uvicorn", "jinja2", "watchfiles"]
  # ///
  ```
- This makes the launch command simply: `uv run plan_dashboard.py serve`

**Backward compatibility:**
- Keep the existing `plan_dashboard.py generate` command for static HTML generation as a fallback
- The `serve` subcommand is additive — doesn't break existing usage

## Results

Implemented in [`plan_dashboard.py`](skills/task-system/scripts/plan_dashboard.py).

**CLI subcommands:**
- `serve [--root .plan/] [--port 8080] [--no-open]` — starts FastAPI via `uvicorn.run()`, auto-opens browser after 1s delay unless `--no-open`
- `generate --plan-root PATH [--output PATH]` — backward-compatible static HTML generation, preserves the full `DASHBOARD_HTML` template from the old script

**PEP 723 inline metadata:**
```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn[standard]", "jinja2", "watchfiles", "pyyaml"]
# ///
```

Launch: `uv run skills/task-system/scripts/plan_dashboard.py serve`
