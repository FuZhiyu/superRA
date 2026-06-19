#!/usr/bin/env python3
"""Shared parsing and assertions for harness instruction-following transcripts.

The helpers accept Claude stream JSON and Codex JSONL without depending on a
single exact event schema. They preserve event order and use recursive searches
over JSON keys/values so tests can assert structural evidence while tolerating
minor harness shape changes.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None

WRITE_TOOL_NAMES = {
    "apply_patch",
    "edit",
    "multiedit",
    "notebookedit",
    "str_replace",
    "update_file",
    "write",
    "write_file",
}

READ_TOOL_NAMES = {
    "open",
    "read",
    "read_file",
    "view",
}

WRITE_EVENT_NEEDLES = (
    "file_change",
    "fs_write",
    "write_file",
)

MUTATING_COMMAND_RE = re.compile(
    r"(^|\s)(apply_patch|cat\s+<<|tee\s+|touch\s+|mv\s+|cp\s+|rm\s+|"
    r"python3?\s+-\s*<<|perl\s+-0?pi\b|sed\s+-i\b)"
)


@dataclass
class TranscriptEvent:
    """A normalized event with recursive text search helpers."""

    index: int
    raw: JsonValue
    strings: tuple[str, ...]
    key_values: tuple[tuple[str, str], ...]
    tool_names: tuple[str, ...]
    commands: tuple[str, ...]

    @classmethod
    def from_raw(cls, index: int, raw: JsonValue) -> "TranscriptEvent":
        key_values = tuple(_iter_key_values(raw))
        strings = tuple(_iter_strings(raw))
        tool_names = tuple(
            value for key, value in key_values
            if key in {"name", "tool", "tool_name", "toolName", "recipient"}
        )
        commands = tuple(
            value for key, value in key_values
            if key in {"cmd", "command", "shell_command"}
        )
        return cls(
            index=index,
            raw=raw,
            strings=strings,
            key_values=key_values,
            tool_names=tool_names,
            commands=commands,
        )

    @property
    def haystack(self) -> str:
        parts: list[str] = []
        parts.extend(self.strings)
        parts.extend(f"{key}={value}" for key, value in self.key_values)
        return "\n".join(parts)

    def contains_all(self, needles: Sequence[str]) -> bool:
        text = self.haystack
        return all(needle in text for needle in needles)

    def contains_any(self, needles: Sequence[str]) -> bool:
        text = self.haystack
        return any(needle in text for needle in needles)

    def is_write_event(self) -> bool:
        lowered_tools = {name.lower() for name in self.tool_names}
        if lowered_tools & WRITE_TOOL_NAMES:
            return True
        lowered_text = self.haystack.lower()
        if any(needle in lowered_text for needle in WRITE_EVENT_NEEDLES):
            return True
        return any(MUTATING_COMMAND_RE.search(command) for command in self.commands)

    def is_read_of(self, path: str) -> bool:
        if path not in self.haystack:
            return False
        lowered_tools = {name.lower() for name in self.tool_names}
        if lowered_tools & READ_TOOL_NAMES:
            return True
        return any(_command_reads_path(command, path) for command in self.commands)


@dataclass
class AssertionReport:
    """Collect every missing behavior from one transcript/artifact check."""

    missing: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.missing.append(message)

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Missing transcript evidence:\n{joined}")


def parse_json_events(text: str) -> list[TranscriptEvent]:
    """Parse line-delimited JSON or a JSON list/object into ordered events."""

    raw_events: list[JsonValue] = []
    stripped = text.strip()
    if not stripped:
        return []

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                raw_events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON event on line {lineno}: {exc}") from exc
    else:
        raw_events = parsed if isinstance(parsed, list) else [parsed]

    return [TranscriptEvent.from_raw(index, raw)
            for index, raw in enumerate(raw_events)]


def parse_jsonl(path: Path | str) -> list[TranscriptEvent]:
    return parse_json_events(Path(path).read_text(encoding="utf-8"))


def parse_claude_stream_json(path: Path | str) -> list[TranscriptEvent]:
    """Parse `claude -p --output-format=stream-json` output."""

    return parse_jsonl(path)


def parse_codex_jsonl(path: Path | str) -> list[TranscriptEvent]:
    """Parse `codex exec --json` output."""

    return parse_jsonl(path)


def check_event_before_write(
    report: AssertionReport,
    events: Sequence[TranscriptEvent],
    label: str,
    needles: Sequence[str],
    *,
    write_path: str | None = None,
) -> None:
    """Require an event containing all needles before the first write event."""

    boundary = first_write_index(events, write_path=write_path)
    found = next(
        (event for event in events[:boundary] if event.contains_all(needles)),
        None,
    )
    report.require(
        found is not None,
        f"{label}: expected {list(needles)} before first write"
        + (f" to {write_path}" if write_path else ""),
    )


def check_task_reads_before_write(
    report: AssertionReport,
    events: Sequence[TranscriptEvent],
    task_paths: Iterable[str],
    *,
    write_path: str = "loading-evidence.json",
) -> None:
    for task_path in task_paths:
        check_event_before_write(
            report,
            events,
            f"task read for {task_path}",
            ["superra task read", task_path],
            write_path=write_path,
        )


def check_file_reads_before_write(
    report: AssertionReport,
    events: Sequence[TranscriptEvent],
    paths: Iterable[str],
    *,
    write_path: str = "loading-evidence.json",
) -> None:
    boundary = first_write_index(events, write_path=write_path)
    for path in paths:
        report.require(
            any(event.is_read_of(path) for event in events[:boundary]),
            f"file read for {path}: expected read before first write to {write_path}",
        )


def check_orchestrator_dispatches(
    report: AssertionReport,
    events: Sequence[TranscriptEvent],
    *,
    implementer_needles: Sequence[str] = ("superra_implementer",),
    reviewer_needles: Sequence[str] = ("superra_reviewer",),
    fallback_needles: Sequence[str] | None = None,
) -> None:
    """Require implementer/reviewer dispatch evidence or record fallback."""

    has_implementer = any(event.contains_all(implementer_needles)
                          for event in events)
    has_reviewer = any(event.contains_all(reviewer_needles)
                       for event in events)
    if has_implementer and has_reviewer:
        report.observations.append("orchestrator dispatch events observed")
        return

    if fallback_needles and any(event.contains_all(fallback_needles)
                                for event in events):
        report.skipped.append(
            "subagent dispatch events unavailable; documented fallback observed"
        )
        return

    if not has_implementer:
        report.missing.append(
            f"orchestrator dispatch: missing implementer event {list(implementer_needles)}"
        )
    if not has_reviewer:
        report.missing.append(
            f"orchestrator dispatch: missing reviewer event {list(reviewer_needles)}"
        )


def check_json_artifact(
    report: AssertionReport,
    actual_path: Path | str,
    expected_path: Path | str,
) -> None:
    """Compare expected scalar leaves against an artifact and report all misses."""

    actual = json.loads(Path(actual_path).read_text(encoding="utf-8"))
    expected = json.loads(Path(expected_path).read_text(encoding="utf-8"))

    actual_scalars = dict(_iter_scalar_paths(actual))
    for path, expected_value in _iter_scalar_paths(expected):
        if path not in actual_scalars:
            report.missing.append(f"artifact {path}: missing expected value")
        elif actual_scalars[path] != expected_value:
            report.missing.append(
                f"artifact {path}: expected {expected_value!r}, "
                f"got {actual_scalars[path]!r}"
            )


def first_write_index(
    events: Sequence[TranscriptEvent],
    *,
    write_path: str | None = None,
) -> int:
    for event in events:
        if not event.is_write_event():
            continue
        if write_path is None or write_path in event.haystack:
            return event.index
    return len(events)


def _iter_key_values(value: JsonValue) -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str):
                yield str(key), item
            yield from _iter_key_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_key_values(item)


def _iter_strings(value: JsonValue) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _iter_scalar_paths(value: JsonValue, prefix: str = "$") -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_scalar_paths(item, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_scalar_paths(item, f"{prefix}[{index}]")
    else:
        yield prefix, value


def _command_reads_path(command: str, path: str) -> bool:
    if path not in command:
        return False
    read_tokens = ("cat ", "sed ", "nl ", "rg ", "grep ", "python ", "python3 ")
    return any(token in command for token in read_tokens)
