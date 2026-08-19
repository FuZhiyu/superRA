#!/usr/bin/env python3
"""PreToolUse gate requiring Communicate before Markdown mutation."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path


COMMUNICATE = "superRA:communicate"
_PATCH_PATH_RE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File: (?P<path>.+)$|^\*\*\* Move to: (?P<move_to>.+)$"
)
_REDIRECT_MD_RE = re.compile(r"(?:^|[\s;|&])(?:\d*)>>?\s*(['\"]?[^\s;|&'\"]+\.md)['\"]?(?=$|[\s;|&])", re.IGNORECASE)
_TEE_MD_RE = re.compile(r"(?:^|[\s;|&])tee(?:\s+-[a-zA-Z]+)*\s+(['\"]?[^\s;|&'\"]+\.md)['\"]?(?=$|[\s;|&])", re.IGNORECASE)
_IN_PLACE_MD_RE = re.compile(
    r"(?:^|[\s;|&])(?:sed|perl)\s+[^;|&]*?-i(?:\S*)?\s+[^;|&]*?(['\"]?[^\s;|&'\"]+\.md)['\"]?(?=$|[\s;|&])",
    re.IGNORECASE,
)


def _empty() -> None:
    print("{}")


def _resolve(path: str, cwd: Path) -> Path:
    candidate = Path(path.strip().strip("'\""))
    return candidate if candidate.is_absolute() else cwd / candidate


def _patch_paths(command: str) -> list[str]:
    paths: list[str] = []
    for line in command.splitlines():
        match = _PATCH_PATH_RE.match(line)
        if match:
            path = (match.group("path") or match.group("move_to") or "").strip()
            if path:
                paths.append(path)
    return paths


def _bash_markdown_paths(command: str) -> list[str]:
    paths: list[str] = []
    for pattern in (_REDIRECT_MD_RE, _TEE_MD_RE, _IN_PLACE_MD_RE):
        paths.extend(match.group(1).strip("'\"") for match in pattern.finditer(command))
    for segment in re.split(r"(?:&&|\|\||[;|])", command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue
        if not tokens:
            continue
        executable = Path(tokens[0]).name
        operands = [token for token in tokens[1:] if not token.startswith("-")]
        if executable == "touch":
            paths.extend(token for token in operands if token.lower().endswith(".md"))
        elif executable in ("cp", "mv") and operands:
            destination = operands[-1]
            if destination.lower().endswith(".md"):
                paths.append(destination)
    return paths


def markdown_targets(data: dict) -> list[Path]:
    """Return confidently parsed Markdown mutation targets."""
    tool_name = data.get("tool_name", "") or data.get("tool", "")
    tool_input = data.get("tool_input", {}) or {}
    cwd_raw = data.get("cwd", "") or os.getcwd()
    try:
        cwd = Path(cwd_raw)
    except (TypeError, ValueError):
        return []

    raw_paths: list[str]
    if tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
        raw_paths = [file_path] if isinstance(file_path, str) and file_path else []
    elif tool_name == "apply_patch":
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        raw_paths = _patch_paths(command) if isinstance(command, str) and command else []
    elif tool_name == "Bash":
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        raw_paths = _bash_markdown_paths(command) if isinstance(command, str) and command else []
    else:
        return []

    targets: list[Path] = []
    seen: set[Path] = set()
    for raw_path in raw_paths:
        try:
            target = _resolve(raw_path, cwd)
        except (TypeError, ValueError):
            return []
        if target.suffix.lower() != ".md" or target in seen:
            continue
        seen.add(target)
        targets.append(target)
    return targets


def _transcript_evidence(text: str) -> dict[str, list[str]] | None:
    """Extract skill, command, and path fields from JSONL hook transcripts."""
    records = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not records:
        try:
            records.append(json.loads(text))
        except json.JSONDecodeError:
            return None

    evidence: dict[str, list[str]] = {"skill": [], "command": [], "path": []}

    def collect(value) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = key.lower()
                if isinstance(item, str):
                    if key_lower == "skill":
                        evidence["skill"].append(item)
                    elif key_lower in ("command", "cmd"):
                        evidence["command"].append(item)
                    elif key_lower in ("file_path", "path"):
                        evidence["path"].append(item)
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    for record in records:
        collect(record)
    return evidence


def _transcript_has_skill(evidence: dict[str, list[str]]) -> bool:
    if any(skill.lower() == COMMUNICATE.lower() for skill in evidence["skill"]):
        return True
    pattern = re.compile(r"skills[/\\]communicate[/\\]SKILL\.md", re.IGNORECASE)
    return any(pattern.search(value) for value in evidence["command"] + evidence["path"])


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        _empty()
        return

    # Claude exposes agent_id only inside a subagent tool call. The hard gate is
    # deliberately main-thread-only; harnesses without this evidence fail open.
    if data.get("agent_id"):
        _empty()
        return

    targets = markdown_targets(data)
    if not targets:
        _empty()
        return

    transcript_raw = data.get("transcript_path", "")
    if not isinstance(transcript_raw, str) or not transcript_raw:
        _empty()
        return
    transcript_path = Path(transcript_raw)
    try:
        transcript = transcript_path.read_text(encoding="utf-8")
    except OSError:
        _empty()
        return
    evidence = _transcript_evidence(transcript)
    if evidence is None:
        _empty()
        return

    if not _transcript_has_skill(evidence):
        reason = (
            f"Before editing Markdown, load `{COMMUNICATE}`, "
            "then retry the same tool call."
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
        return

    _empty()


if __name__ == "__main__":
    main()
