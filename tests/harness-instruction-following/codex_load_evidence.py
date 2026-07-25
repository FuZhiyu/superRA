#!/usr/bin/env python3
"""Codex skill-load + subagent-dispatch evidence model and assertions.

This module is the CI-safe Codex counterpart to ``sdk_load_evidence.py`` (the
Claude SDK harness). It never imports or requires ``codex-cli`` and never makes a
model call. It parses observable command executions and hook-backed dispatch
records for downstream harness checks.

``codex exec --json`` exposes neither a ``skill_loaded`` event nor a
``spawn_agent`` item. Observable command checks therefore validate parsed
``command_execution`` records, while subagent dispatch uses a
``SubagentStart`` hook log:

1. **Command execution** — command predicates match the executable and ordered
   arguments, and reject a nonzero exit code when the event supplies one.
2. **``SubagentStart`` hook log** — a ``SubagentStart`` hook (matcher = agent
   type) appends an agent-type sentinel to a log file on every dispatch, so
   orchestrator dispatch is verifiable even though the JSONL hides it. The hook
   payload is disambiguated by the agent-type field, never by ``session_id``.
   :func:`handle_subagent_start_payload` is the payload handler the live hook and
   the unit test share; :func:`evaluate_dispatch_log` checks the resulting log.

Both evaluators take already-parsed inputs (the codex JSONL events via the shared
``transcript_assertions`` parser, the artifact JSON, the dispatch log text), so
the default ``pytest`` path drives them on synthetic inputs with no codex-cli and
no model call.

Codex event shapes are pinned to codex-cli 0.140.0 (``type``/``agent_message``,
``command_execution``, ``file_change``) per the research doc.
"""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from structured_findings import Finding, add_missing, add_observation

# Payload keys a codex SubagentStart hook may use to name the dispatched agent
# type. The matcher is the agent type, but the payload also carries it; we accept
# the plausible spellings so a minor codex-cli payload-shape change degrades to a
# different key rather than dropping the sentinel. session_id is deliberately NOT
# in this set — disambiguation is by agent type, per the objective.
_AGENT_TYPE_KEYS = (
    "agent_type",
    "agentType",
    "subagent_type",
    "subagentType",
    "agent",
    "name",
)


# --------------------------------------------------------------------------- #
# Command-execution evidence
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CommandSpec:
    """One exact executable and ordered argument vector.

    Arguments compare exactly unless their zero-based position is listed in
    ``path_arg_indices``; those positions accept the exact value or a path with
    that value as its suffix.
    """

    subject: str
    executable: str
    args: tuple[str, ...]
    path_arg_indices: frozenset[int] = frozenset()


@dataclass(frozen=True)
class CommandExecution:
    """One parsed Codex ``command_execution`` event."""

    command: str
    exit_code: int | None


@dataclass
class CommandEvidenceReport:
    """Collect command-execution findings."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Codex command evidence failures:\n{joined}")


def _path_suffix_matches(expected: str, actual: str) -> bool:
    return actual == expected or actual.endswith(f"/{expected}")


def _execution_matches(spec: CommandSpec, execution: CommandExecution) -> bool:
    try:
        tokens = shlex.split(execution.command)
    except ValueError:
        return False
    if not tokens:
        return False
    if tokens[0] != spec.executable:
        return False
    actual_args = tokens[1:]
    if len(actual_args) != len(spec.args):
        return False
    for index, (expected, actual) in enumerate(zip(spec.args, actual_args)):
        if index in spec.path_arg_indices:
            if not _path_suffix_matches(expected, actual):
                return False
        elif actual != expected:
            return False
    return True


def evaluate_command_specs(
    report: CommandEvidenceReport,
    specs: Iterable[CommandSpec],
    executions: Sequence[CommandExecution],
) -> None:
    """Require one successful matching execution for every command spec."""

    for spec in specs:
        matches = [
            execution
            for execution in executions
            if _execution_matches(spec, execution)
        ]
        successful = [
            execution
            for execution in matches
            if execution.exit_code == 0
        ]
        if successful:
            execution = successful[0]
            add_observation(
                report,
                "COMMAND_EXECUTED",
                f"observed successful command execution for {spec.subject!r}",
                subject=spec.subject,
                actual={
                    "command": execution.command,
                    "exit_code": execution.exit_code,
                },
            )
            continue
        if matches:
            completed = [
                execution for execution in matches if execution.exit_code is not None
            ]
            if not completed:
                add_missing(
                    report,
                    "COMMAND_INCOMPLETE",
                    f"matching command execution for {spec.subject!r} did not complete",
                    subject=spec.subject,
                    actual=[execution.command for execution in matches],
                )
                continue
            add_missing(
                report,
                "COMMAND_FAILED",
                f"matching command execution for {spec.subject!r} failed",
                subject=spec.subject,
                actual=[execution.exit_code for execution in completed],
            )
            continue
        add_missing(
            report,
            "COMMAND_NOT_EXECUTED",
            f"no command execution matched {spec.subject!r}",
            subject=spec.subject,
            actual={
                "executable": spec.executable,
                "args": list(spec.args),
            },
        )


def _iter_command_nodes(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if value.get("type") == "command_execution":
            yield value
            return
        for child in value.values():
            yield from _iter_command_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_command_nodes(child)


def command_executions_from_events(events: Sequence) -> list[CommandExecution]:
    """Extract structured command executions from parsed Codex events."""

    executions: list[CommandExecution] = []
    for event in events:
        for node in _iter_command_nodes(getattr(event, "raw", None)):
            command = node.get("command")
            exit_code = node.get("exit_code")
            if not isinstance(command, str):
                continue
            executions.append(
                CommandExecution(
                    command=command,
                    exit_code=exit_code if isinstance(exit_code, int) else None,
                )
            )
    return executions


# --------------------------------------------------------------------------- #
# SubagentStart dispatch-log evidence
# --------------------------------------------------------------------------- #


def _agent_type_from_payload(payload: dict) -> str | None:
    """Pull the agent type from a SubagentStart payload (defensive on key name)."""

    for key in _AGENT_TYPE_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def handle_subagent_start_payload(payload: dict) -> str | None:
    """Return the log line a SubagentStart hook should append, or ``None``.

    Shared by the live hook executable (:mod:`subagent_start_hook`) and the unit
    test. Disambiguation is by the agent-type field, not ``session_id``: a
    payload with no recognizable agent type yields ``None`` (the hook appends
    nothing) rather than a session-keyed line. The returned line is the bare
    agent-type sentinel, so the dispatch log is a newline-delimited list of
    dispatched agent types.
    """

    agent_type = _agent_type_from_payload(payload)
    if agent_type is None:
        return None
    return agent_type


def append_subagent_start(log_path: Path | str, payload: dict) -> str | None:
    """Apply :func:`handle_subagent_start_payload` and append to the log file.

    Returns the appended agent type, or ``None`` when the payload named no agent
    type (nothing appended). Creates the parent directory if needed so the hook
    is robust to a fresh temp profile.
    """

    line = handle_subagent_start_payload(payload)
    if line is None:
        return None
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return line


@dataclass
class DispatchReport:
    """Collect missing dispatch sentinels from one dispatch-log check."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Codex dispatch-log failures:\n{joined}")


def dispatched_agent_types(log_text: str) -> list[str]:
    """Parse a SubagentStart dispatch log into the list of dispatched types."""

    return [line.strip() for line in log_text.splitlines() if line.strip()]


def evaluate_dispatch_log(
    report: DispatchReport,
    log_text: str,
    required_agent_types: Iterable[str] = (
        "superra_implementer",
        "superra_reviewer",
    ),
) -> None:
    """Require each named agent type to appear in the SubagentStart log.

    The SubagentStart hook supersedes JSONL-based dispatch detection for the
    Codex orchestrator path (the JSONL hides ``spawn_agent``). A required type
    that never appears is a missing-dispatch finding.
    """

    dispatched = dispatched_agent_types(log_text)
    for agent_type in required_agent_types:
        if agent_type in dispatched:
            add_observation(
                report,
                "DISPATCH_LOGGED",
                f"dispatch sentinel {agent_type!r} logged",
                subject=agent_type,
            )
        else:
            add_missing(
                report,
                "DISPATCH_LOG_MISSING",
                f"SubagentStart log missing dispatch sentinel {agent_type!r} "
                f"(observed: {dispatched})",
                subject=agent_type,
                actual=dispatched,
            )


def load_artifact(path: Path | str) -> dict | None:
    """Read and parse an output artifact, returning ``None`` if absent."""

    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
