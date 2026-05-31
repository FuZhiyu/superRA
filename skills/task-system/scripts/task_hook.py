#!/usr/bin/env python3
"""PostToolUse hook: validate task.md and rebuild dashboard on edit/write/move.

Fires after Edit/Write tool calls (targeting a task.md) and after Bash tool
calls that structurally mutate a .plan/ task tree (mv, rm, cp, mkdir, ...).
In both cases it runs the same best-effort reconcile — validate the tree,
propagate parent status, rebuild the dashboard. Always exits 0 — never blocks
the agent.

Claude Code PostToolUse stdin format:
  {
    "tool_name": "Edit" | "Write" | "Bash" | ...,
    "tool_input": {"file_path": "/abs/path/to/file", "command": "...", ...},
    "tool_response": {...}
  }
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _scripts_dir() -> Path:
    return Path(__file__).parent


def _ensure_scripts_on_path() -> None:
    """Add the scripts directory to sys.path so _task_io and plan_dashboard are importable."""
    scripts = str(_scripts_dir())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def _reconcile(plan_root: Path, task_path: str | None) -> None:
    """Validate, propagate parent status, and rebuild the dashboard for a plan tree.

    Each step is best-effort in its own try/except so a failure in one never
    aborts the others or the process. When task_path is None (a structural move
    whose precise location is unknown), parent status is recomputed across the
    whole tree rather than along a single ancestor chain.
    """
    _ensure_scripts_on_path()
    import _task_io as task_io

    # Validate — print warnings to stderr so the agent sees them.
    try:
        warnings = task_io.validate_plan(plan_root)
        if warnings:
            print(f"[task-hook] Validation warnings for {plan_root}:", file=sys.stderr)
            for w in warnings:
                print(f"  WARNING: {w}", file=sys.stderr)
    except Exception as exc:
        print(f"[task-hook] Validation error: {exc}", file=sys.stderr)

    # Propagate parent status up the tree — best-effort, never fail.
    try:
        if task_path is None:
            updated = _propagate_whole_tree(task_io, plan_root)
        else:
            updated = task_io.propagate_parent_status(plan_root, task_path)
        if updated:
            print(f"[task-hook] Propagated status to {updated} ancestor(s).", file=sys.stderr)
    except Exception as exc:
        print(f"[task-hook] Status propagation failed (non-fatal): {exc}", file=sys.stderr)

    # Regenerate dashboard — best-effort, never fail.
    try:
        import plan_dashboard
        plan_dashboard.generate_dashboard(plan_root)
    except Exception as exc:
        print(f"[task-hook] Dashboard rebuild failed (non-fatal): {exc}", file=sys.stderr)


def _propagate_whole_tree(task_io, plan_root: Path) -> int:
    """Recompute parent status across every branch in the tree.

    propagate_parent_status only walks the ancestors of one task_path, so a
    structural move (which can change several branches at once) needs every
    leaf's ancestor chain recomputed. Propagating from each leaf covers all
    intermediate parents; counts are summed for the stderr note.
    """
    root = task_io.walk_plan(plan_root)
    leaf_paths: list[str] = []

    def _collect(task) -> None:
        if task.is_leaf:
            if task.path:
                leaf_paths.append(task.path)
        else:
            for child in task.children:
                _collect(child)

    _collect(root)

    updated = 0
    for leaf_path in leaf_paths:
        updated += task_io.propagate_parent_status(plan_root, leaf_path)
    return updated


# Filesystem-mutating verbs that can restructure a .plan/ task tree.
_MUTATING_RE = re.compile(
    r"(?:^|[\s;&|(])(?:git\s+mv|mv|rm|rmdir|cp|mkdir)(?:\s|$)"
)
# Path-like tokens that mention a .plan directory.
_PLAN_TOKEN_RE = re.compile(r"(?:^|[\s'\"=])((?:[^\s'\"=]*/)?\.plan[^\s'\";|&]*)")


def _find_plan_root_for_token(task_io, token: str, cwd: Path) -> Path | None:
    """Resolve a .plan-containing command token to its plan root directory.

    The token may be a source that no longer exists (post-move) or a
    destination that does not exist yet, so this does not rely on the path
    existing. It splits on the first '.plan' segment and returns the directory
    up to and including it, resolved against cwd when relative.
    """
    raw = Path(token)
    base = raw if raw.is_absolute() else (cwd / raw)
    parts = base.parts
    plan_idx = None
    for i, part in enumerate(parts):
        if part == ".plan" or part.startswith(".plan"):
            plan_idx = i
            break
    if plan_idx is None:
        return None
    plan_root = Path(*parts[: plan_idx + 1])
    if (plan_root / "task.md").exists() or plan_root.is_dir():
        return plan_root
    # The .plan dir itself may have been moved/removed; walk up to an existing one.
    return plan_root if plan_root.exists() else None


def _handle_bash(data: dict) -> None:
    """Reconcile any .plan tree touched by a structural Bash command."""
    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command:
        sys.exit(0)

    # Gate: must reference .plan AND contain a mutating verb. A read-only
    # command that merely mentions .plan (task_query.py, grep .plan, ...) is
    # not a structural change and must early-exit.
    if ".plan" not in command:
        sys.exit(0)
    if not _MUTATING_RE.search(command):
        sys.exit(0)

    _ensure_scripts_on_path()
    import _task_io as task_io

    cwd = Path.cwd()
    plan_roots: list[Path] = []
    seen: set[Path] = set()

    for match in _PLAN_TOKEN_RE.finditer(command):
        token = match.group(1)
        root = _find_plan_root_for_token(task_io, token, cwd)
        if root is None:
            continue
        resolved = root.resolve() if root.exists() else root
        if resolved in seen:
            continue
        seen.add(resolved)
        plan_roots.append(root)

    # Fallback: no resolvable token but the command still touched .plan — try
    # the .plan/ under the process working directory.
    if not plan_roots:
        candidate = cwd / ".plan"
        if candidate.is_dir():
            plan_roots.append(candidate)

    for plan_root in plan_roots:
        if not (plan_root / "task.md").exists() and not plan_root.is_dir():
            continue
        _reconcile(plan_root, task_path=None)

    sys.exit(0)


def _handle_edit_write(data: dict) -> None:
    """Reconcile the plan tree for an Edit/Write of a task.md."""
    tool_input = data.get("tool_input", {}) or {}
    file_path_str = tool_input.get("file_path", "")
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

    _ensure_scripts_on_path()
    import _task_io as task_io
    plan_root = task_io._find_plan_root(file_path.parent)
    if plan_root is None:
        sys.exit(0)

    task_path = str(file_path.parent.relative_to(plan_root))
    if task_path == ".":
        task_path = ""

    _reconcile(plan_root, task_path=task_path)
    sys.exit(0)


def main() -> None:
    # Read tool call info from stdin (Claude Code PostToolUse protocol)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name = data.get("tool_name", "") or data.get("tool", "")

    if tool_name == "Bash":
        _handle_bash(data)
    elif tool_name in ("Edit", "Write"):
        _handle_edit_write(data)

    sys.exit(0)


if __name__ == "__main__":
    main()
