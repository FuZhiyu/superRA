#!/usr/bin/env python3
"""PreToolUse gate: a `task.md` edit cannot add a task-level cycle.

`## Reproduction` has no CLI, so direct edits are the main way a cycle is
created. An edit that leaves the graph's inputs alone costs no graph build.
Anything the gate cannot reconstruct or parse passes; what lands that way
surfaces as the `task check` warning.
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

from task_approval_gate import (
    _deny,
    _edit_result,
    _empty,
    _ensure_scripts_on_path,
    _is_task_md,
    _resolve,
    _write_result,
)


def _proposed(tool_name: str, tool_input: dict, cwd: Path) -> dict[Path, str]:
    """Each `task.md` the call writes, with its reconstructed text."""
    if tool_name in ("Edit", "Write"):
        raw = tool_input.get("file_path", "")
        path = _resolve(raw, cwd) if isinstance(raw, str) and raw else None
        if path is None or not _is_task_md(path):
            return {}
        result = _edit_result(path, tool_input) if tool_name == "Edit" else _write_result(tool_input)
        return {path: result} if result is not None else {}
    command = tool_input.get("command", "")
    if tool_name != "apply_patch" or not isinstance(command, str) or not command:
        return {}
    _ensure_scripts_on_path()
    from _apply_patch import apply_to_text, parse_patch

    edits: dict[Path, str] = {}
    for patch in parse_patch(command):
        path = _resolve(patch.path, cwd)
        if patch.kind == "delete" or patch.move_to or not _is_task_md(path):
            continue
        result = apply_to_text(patch, _disk_text(path))
        if result is not None:
            edits[path] = result
    return edits


def _disk_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _graph_inputs(text: str) -> tuple:
    """What a task contributes to the graph: archival, `depends_on`, its steps."""
    _ensure_scripts_on_path()
    from _task_io import parse_body_sections, parse_frontmatter

    fm, body = parse_frontmatter(text)
    return (
        fm.get("status") == "archived",
        fm.get("depends_on") or None,
        parse_body_sections(body).get("Reproduction"),
    )


def _refusal(edits: dict[Path, str]) -> str | None:
    changed = {p: t for p, t in edits.items() if _graph_inputs(t) != _graph_inputs(_disk_text(p))}
    if not changed:
        return None
    from _task_io import _find_plan_root, is_opaque_task_path
    from _task_snapshot import edit_adds_cycles
    from task_hook import _writes_frozen

    by_root: dict[Path, dict[Path, str]] = {}
    for path, text in changed.items():
        root = _find_plan_root(path.parent)
        if root is not None and root.is_dir() and not is_opaque_task_path(path, root):
            by_root.setdefault(root.resolve(), {})[path] = text
    for root, overlays in by_root.items():
        if _writes_frozen(root):
            continue
        added = edit_adds_cycles(root, overlays)
        if added:
            return (
                "This edit would add a task-level cycle, which makes the graph very hard to "
                "trace. Restructure it; there is no override.\n" + "\n".join(added)
            )
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input") or {}
        tool_name = data.get("tool_name", "") or data.get("tool", "")
        cwd = Path(data.get("cwd", "") or os.getcwd())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reason = _refusal(_proposed(tool_name, tool_input, cwd))
    except Exception:
        _empty()
        return
    if reason:
        _deny(reason)
    else:
        _empty()


if __name__ == "__main__":
    main()
