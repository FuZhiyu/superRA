#!/usr/bin/env python3
"""PreToolUse Markdown gate and one-shot task-status snapshot support."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
import tempfile
from pathlib import Path


COMMUNICATE = "superRA:communicate"
STATE_DIR_ENV = "SUPERRA_COMMUNICATE_STATE_DIR"
TASK_ROOT_NAMES = ("superRA", ".plan")
_PATCH_PATH_RE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File: (?P<path>.+)$|^\*\*\* Move to: (?P<move_to>.+)$"
)
_STATUS_RE = re.compile(r"^status:\s*([^\s#]+)", re.MULTILINE)
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


def _is_task_root_part(part: str) -> bool:
    return part in TASK_ROOT_NAMES or part.startswith(".plan.")


def task_context(target: Path) -> str | None:
    """Return the nearest existing task owner's root-relative path."""
    start = target.parent
    candidates = [start, *start.parents]
    for candidate in candidates:
        if not (candidate / "task.md").is_file():
            continue
        parts = candidate.parts
        indexes = [i for i, part in enumerate(parts) if _is_task_root_part(part)]
        if not indexes:
            continue
        root_index = indexes[-1]
        root = Path(*parts[: root_index + 1])
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            continue
        return "" if str(relative) == "." else relative.as_posix()
    return None


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


def _transcript_has_task_read(evidence: dict[str, list[str]], task_path: str) -> bool:
    escaped = re.escape(task_path or ".")
    pattern = rf"(?:\./)?superRA/superra\s+task\s+read\s+(?:['\"])?{escaped}(?:['\"])?(?=$|[\s;&|}},])"
    if any(re.search(pattern, command, re.IGNORECASE) for command in evidence["command"]):
        return True
    generic = rf"\bsuperra\s+task\s+read\s+(?:['\"])?{escaped}(?:['\"])?(?=$|[\s;&|}},])"
    return any(re.search(generic, command, re.IGNORECASE) for command in evidence["command"])


def _state_key(data: dict) -> str | None:
    session_id = data.get("session_id", "")
    tool_use_id = data.get("tool_use_id", "")
    if (
        not isinstance(session_id, str)
        or not session_id
        or not isinstance(tool_use_id, str)
        or not tool_use_id
    ):
        return None
    return hashlib.sha256(f"{session_id}\0{tool_use_id}".encode()).hexdigest()


def state_path(data: dict) -> Path | None:
    key = _state_key(data)
    if key is None:
        return None
    default = Path(tempfile.gettempdir()) / "superra-communicate-hook"
    root = Path(os.environ.get(STATE_DIR_ENV, default))
    return root / f"{key}.json"


def _read_status(path: Path) -> str | None:
    if path.name != "task.md" or not path.is_file():
        return None
    try:
        match = _STATUS_RE.search(path.read_text(encoding="utf-8"))
    except OSError:
        return None
    return match.group(1) if match else None


def save_status_snapshot(data: dict, targets: list[Path]) -> None:
    path = state_path(data)
    if path is None:
        return
    statuses = []
    for target in targets:
        status = _read_status(target)
        if status is not None:
            statuses.append({"path": str(target), "status": status})
    if not statuses:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"targets": statuses}, separators=(",", ":"))
        path.write_text(payload, encoding="utf-8")
    except OSError:
        return


def consume_status_snapshot(data: dict) -> list[dict] | None:
    """Consume a pre-tool snapshot; None means no keyed snapshot exists."""
    path = state_path(data)
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        path.unlink()
    except (OSError, ValueError, TypeError):
        return None
    targets = payload.get("targets", []) if isinstance(payload, dict) else []
    return targets if isinstance(targets, list) else []


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

    missing: list[str] = []
    if not _transcript_has_skill(evidence):
        missing.append(f"load `{COMMUNICATE}`")

    contexts: list[str] = []
    for target in targets:
        context = task_context(target)
        if context is None:
            continue
        task_path = context
        if task_path not in contexts:
            contexts.append(task_path)
    for task_path in contexts:
        if not _transcript_has_task_read(evidence, task_path):
            missing.append(f"run `./superRA/superra task read {task_path or '.'}`")

    if missing:
        reason = (
            "Before editing Markdown, "
            + " and ".join(missing)
            + ", then retry the same tool call."
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

    save_status_snapshot(data, targets)
    _empty()


if __name__ == "__main__":
    main()
