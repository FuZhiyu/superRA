#!/usr/bin/env python3
"""PreToolUse gate for approved tasks with blocking review findings."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


_PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update) File: (?P<path>.+)$")


def _empty() -> None:
    print("{}")


def _deny(path: Path) -> None:
    reason = (
        f"Cannot approve {path}: `## Review Notes` still contains `[BLOCKING]`. "
        "Run narrow re-review and remove confirmed findings, or keep the task in revision."
    )
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


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills" / "task-tree" / "scripts"


def _approved_with_blocking_review_notes(text: str) -> bool:
    try:
        scripts = str(_scripts_dir())
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        from _task_validate import approved_with_blocking_review_notes

        return approved_with_blocking_review_notes(text)
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


def _patch_targets(command: str, cwd: Path) -> list[tuple[Path, list[str]]]:
    targets: list[tuple[Path, list[str]]] = []
    current: tuple[Path, list[str]] | None = None
    for line in command.splitlines():
        match = _PATCH_FILE_RE.match(line)
        if match:
            current = (_resolve(match.group("path"), cwd), [])
            targets.append(current)
        elif line.startswith("*** "):
            current = None
        elif current is not None:
            current[1].append(line)
    return targets


def _patch_result(path: Path, lines: list[str]) -> str | None:
    """Apply one Codex update/add patch to text without touching the file."""
    try:
        current = path.read_text(encoding="utf-8")
    except OSError:
        current = ""
    source = current.splitlines()
    trailing_newline = current.endswith("\n") or not current
    cursor = 0
    output: list[str] = []
    hunks: list[list[str]] = []
    hunk: list[str] = []
    for line in lines:
        if line.startswith("@@"):
            if hunk:
                hunks.append(hunk)
                hunk = []
            continue
        hunk.append(line)
    if hunk:
        hunks.append(hunk)

    for hunk in hunks:
        old = [line[1:] for line in hunk if line[:1] in (" ", "-")]
        new = [line[1:] for line in hunk if line[:1] in (" ", "+")]
        if not old:
            if source:
                return None
            output.extend(new)
            continue
        found = next(
            (
                i
                for i in range(cursor, len(source) - len(old) + 1)
                if source[i:i + len(old)] == old
            ),
            None,
        )
        if found is None:
            return None
        output.extend(source[cursor:found])
        output.extend(new)
        cursor = found + len(old)
    output.extend(source[cursor:])
    result = "\n".join(output)
    return result + ("\n" if trailing_newline and result else "")


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
            _deny(path)
            return
    elif tool_name == "apply_patch":
        command = tool_input.get("command", "")
        if isinstance(command, str):
            for path, lines in _patch_targets(command, cwd):
                result = _patch_result(path, lines) if _is_task_md(path) else None
                if result is not None and _approved_with_blocking_review_notes(result):
                    _deny(path)
                    return

    _empty()


if __name__ == "__main__":
    main()
