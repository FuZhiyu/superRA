#!/usr/bin/env python3
"""PostToolUse hook: validate task.md and rebuild dashboard on edit/write.

Fires after Edit or Write tool calls. If the edited file is a task.md
under a .plan/ directory, runs plan validation and regenerates the
dashboard. Always exits 0 — never blocks the agent.

Claude Code PostToolUse stdin format:
  {
    "tool_name": "Edit" | "Write" | ...,
    "tool_input": {"file_path": "/abs/path/to/file", ...},
    "tool_response": {...}
  }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _scripts_dir() -> Path:
    return Path(__file__).parent


def _ensure_scripts_on_path() -> None:
    """Add the scripts directory to sys.path so _task_io and plan_dashboard are importable."""
    scripts = str(_scripts_dir())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def main() -> None:
    # Read tool call info from stdin (Claude Code PostToolUse protocol)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name = data.get("tool_name", "") or data.get("tool", "")
    tool_input = data.get("tool_input", {}) or {}
    file_path_str = tool_input.get("file_path", "")

    # Fast path: only act on Edit or Write targeting a task.md in .plan/
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    if not file_path_str:
        sys.exit(0)

    file_path = Path(file_path_str)

    # Must be named task.md
    if file_path.name != "task.md":
        sys.exit(0)

    # Must be inside a .plan/ directory somewhere in the path
    parts = file_path.parts
    if not any(p.startswith(".plan") for p in parts):
        sys.exit(0)

    # Locate plan root by walking up from the task.md's directory
    _ensure_scripts_on_path()
    import _task_io as task_io
    plan_root = task_io._find_plan_root(file_path.parent)
    if plan_root is None:
        sys.exit(0)

    # Run validation — print warnings to stderr so the agent sees them
    try:
        warnings = task_io.validate_plan(plan_root)
        if warnings:
            print(f"[task-hook] Validation warnings for {plan_root}:", file=sys.stderr)
            for w in warnings:
                print(f"  WARNING: {w}", file=sys.stderr)
    except Exception as exc:
        print(f"[task-hook] Validation error: {exc}", file=sys.stderr)

    # Propagate parent status up the tree — best-effort, never fail
    try:
        task_path = str(file_path.parent.relative_to(plan_root))
        if task_path == ".":
            task_path = ""
        updated = task_io.propagate_parent_status(plan_root, task_path)
        if updated:
            print(f"[task-hook] Propagated status to {updated} ancestor(s).", file=sys.stderr)
    except Exception as exc:
        print(f"[task-hook] Status propagation failed (non-fatal): {exc}", file=sys.stderr)

    # Regenerate dashboard — best-effort, never fail
    try:
        import plan_dashboard
        plan_dashboard.generate_dashboard(plan_root)
    except Exception as exc:
        print(f"[task-hook] Dashboard rebuild failed (non-fatal): {exc}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
