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
_SKILL_MD_RE = re.compile(r"skills[/\\]communicate[/\\]SKILL\.md", re.IGNORECASE)
# Shell verbs whose invocation reads a file rather than mutating it. `sed`
# counts only with `-n` (print mode); bare `sed` rewrites.
_READ_VERBS = ("cat", "head", "tail", "bat", "less")


def _empty() -> None:
    print("{}")


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills" / "task-tree" / "scripts"


def _shared_module():
    try:
        scripts = str(_scripts_dir())
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import _apply_patch

        return _apply_patch
    except Exception:
        return None


def _resolve(path: str, cwd: Path) -> Path:
    candidate = Path(path.strip().strip("'\""))
    return candidate if candidate.is_absolute() else cwd / candidate


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
    elif tool_name in ("apply_patch", "Bash"):
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        shared = _shared_module()
        if shared is None or not isinstance(command, str) or not command:
            return []
        if tool_name == "apply_patch":
            raw_paths = shared.patch_paths(command)
        else:
            raw_paths = shared.bash_markdown_mutation_targets(command)
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
    """Extract skill loads, shell commands, and Read-tool paths from JSONL transcripts.

    Path fields count as evidence only when they belong to a Read tool call, so
    a `grep`/`Grep` hit or `git diff` mention of the skill file never clears the
    gate. Tool attribution is the nearest enclosing dict carrying a string
    ``name`` beside an ``input``/``arguments`` payload.
    """
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

    evidence: dict[str, list[str]] = {"skill": [], "command": [], "read_path": []}

    def collect(value, tool: str) -> None:
        if isinstance(value, dict):
            name = value.get("name")
            if isinstance(name, str) and (
                isinstance(value.get("input"), dict)
                or isinstance(value.get("arguments"), dict)
            ):
                tool = name
            for key, item in value.items():
                key_lower = key.lower()
                if isinstance(item, str):
                    if key_lower == "skill":
                        evidence["skill"].append(item)
                    elif key_lower in ("command", "cmd"):
                        evidence["command"].append(item)
                    elif key_lower in ("file_path", "path") and tool == "Read":
                        evidence["read_path"].append(item)
                collect(item, tool)
        elif isinstance(value, list):
            for item in value:
                collect(item, tool)

    for record in records:
        collect(record, "")
    return evidence


def _command_reads_skill(command: str) -> bool:
    """Whether a shell command reads the Communicate SKILL.md."""
    for segment in re.split(r"(?:&&|\|\||[;|])", command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue
        if not tokens:
            continue
        verb = tokens[0].rsplit("/", 1)[-1]
        if verb == "sed":
            # -n may sit inside a flag cluster (sed -ne '1,50p').
            if not any(re.match(r"-[a-zA-Z]*n", token) for token in tokens[1:]):
                continue
        elif verb not in _READ_VERBS:
            continue
        if any(_SKILL_MD_RE.search(token) for token in tokens[1:]):
            return True
    return False


def _transcript_has_skill(evidence: dict[str, list[str]]) -> bool:
    if any(skill.lower() == COMMUNICATE.lower() for skill in evidence["skill"]):
        return True
    if any(_SKILL_MD_RE.search(value) for value in evidence["read_path"]):
        return True
    return any(_command_reads_skill(value) for value in evidence["command"])


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        _empty()
        return

    # Claude exposes agent_id/agent_type only inside a subagent tool call. The
    # hard gate is deliberately main-thread-only; harnesses without this
    # evidence fail open.
    if data.get("agent_id") or data.get("agent_type"):
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
