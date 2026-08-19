#!/usr/bin/env python3
"""PreToolUse gate for approved tasks with blocking review findings."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


_STATUS_APPROVED_RE = re.compile(r"^\s*status:\s*approved\s*$", re.MULTILINE)


def _empty() -> None:
    print("{}")


def _deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            separators=(",", ":"),
        )
    )


def _deny_violation(path: Path) -> None:
    _deny(
        f"Cannot approve {path}: `## Review Notes` still contains `[BLOCKING]`. "
        "Run narrow re-review and remove confirmed findings, or keep the task in revision. "
        "The gate cannot tell a quoted marker from a live finding: prose in Review Notes "
        "that merely mentions the marker must spell it out of band."
    )


def _deny_unverifiable(path: Path) -> None:
    _deny(
        f"Cannot verify this mutation of {path}: it sets `status: approved` while "
        "`## Review Notes` still carries `[BLOCKING]`. Clear the blocking findings "
        "first, or split the status flip from the notes edit so the result is checkable."
    )


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills" / "task-tree" / "scripts"


def _ensure_scripts_on_path() -> None:
    scripts = str(_scripts_dir())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def _approved_with_blocking_review_notes(text: str) -> bool:
    try:
        _ensure_scripts_on_path()
        from _task_validate import approved_with_blocking_review_notes

        return approved_with_blocking_review_notes(text)
    except Exception:
        return False


def _review_notes_have_blocking(path: Path) -> bool:
    """Whether the file on disk carries `[BLOCKING]` in `## Review Notes`."""
    try:
        text = path.read_text(encoding="utf-8")
        _ensure_scripts_on_path()
        from _task_io import parse_body_sections, parse_frontmatter

        _fm, body = parse_frontmatter(text)
        review_notes = parse_body_sections(body).get("Review Notes", "")
        return bool(re.search(r"\[BLOCKING\]", review_notes, re.IGNORECASE))
    except Exception:
        return False


def _resolve(raw: str, cwd: Path) -> Path:
    path = Path(raw.strip().strip("'\""))
    return path if path.is_absolute() else cwd / path


def _is_task_md(path: Path) -> bool:
    if path.name != "task.md":
        return False
    return any(
        part == "superRA" or part == ".plan" or part.startswith(".plan.")
        for part in path.parts
    )


def _edit_result(path: Path, tool_input: dict) -> str | None:
    try:
        current = path.read_text(encoding="utf-8")
    except OSError:
        return None
    old = tool_input.get("old_string")
    new = tool_input.get("new_string")
    if not isinstance(old, str) or not isinstance(new, str) or old not in current:
        return None
    if tool_input.get("replace_all"):
        return current.replace(old, new)
    return current.replace(old, new, 1)


def _write_result(tool_input: dict) -> str | None:
    content = tool_input.get("content")
    return content if isinstance(content, str) else None


def _handle_apply_patch(command: str, cwd: Path) -> None:
    try:
        _ensure_scripts_on_path()
        from _apply_patch import apply_to_text, parse_patch
    except Exception:
        _empty()
        return
    for patch in parse_patch(command):
        target = _resolve(patch.target_path, cwd)
        source = _resolve(patch.path, cwd)
        if not _is_task_md(target) and not _is_task_md(source):
            continue
        try:
            current = source.read_text(encoding="utf-8")
        except OSError:
            current = ""
        result = apply_to_text(patch, current)
        if result is not None:
            if _approved_with_blocking_review_notes(result):
                _deny_violation(target)
                return
            continue
        # Fail closed: the result cannot be reconstructed, so deny when the
        # patch's added lines set `status: approved` onto blocking review notes.
        added = "\n".join(patch.added_lines())
        if _STATUS_APPROVED_RE.search(added) and _review_notes_have_blocking(source):
            _deny_unverifiable(target)
            return
    _empty()


def _handle_bash(command: str, cwd: Path) -> None:
    """Conservative deny for in-place mutations whose results are unreconstructable."""
    try:
        _ensure_scripts_on_path()
        from _apply_patch import bash_markdown_mutation_targets
    except Exception:
        _empty()
        return
    if not re.search(r"status:\s*approved", command):
        _empty()
        return
    for raw in bash_markdown_mutation_targets(command):
        path = _resolve(raw, cwd)
        if _is_task_md(path) and _review_notes_have_blocking(path):
            _deny_unverifiable(path)
            return
    _empty()


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        _empty()
        return
    tool_name = data.get("tool_name", "") or data.get("tool", "")
    tool_input = data.get("tool_input", {}) or {}
    if not isinstance(tool_input, dict):
        _empty()
        return
    try:
        cwd = Path(data.get("cwd", "") or os.getcwd())
    except (TypeError, ValueError):
        _empty()
        return

    if tool_name in ("Edit", "Write"):
        raw = tool_input.get("file_path", "")
        if not isinstance(raw, str) or not raw:
            _empty()
            return
        path = _resolve(raw, cwd)
        if not _is_task_md(path):
            _empty()
            return
        result = _edit_result(path, tool_input) if tool_name == "Edit" else _write_result(tool_input)
        if result is not None and _approved_with_blocking_review_notes(result):
            _deny_violation(path)
            return
    elif tool_name == "apply_patch":
        command = tool_input.get("command", "")
        if isinstance(command, str) and command:
            _handle_apply_patch(command, cwd)
            return
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        if isinstance(command, str) and command:
            _handle_bash(command, cwd)
            return

    _empty()


if __name__ == "__main__":
    main()
