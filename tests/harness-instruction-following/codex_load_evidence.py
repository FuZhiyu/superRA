#!/usr/bin/env python3
"""Codex skill-load + subagent-dispatch evidence model and assertions.

This module is the CI-safe Codex counterpart to ``sdk_load_evidence.py`` (the
Claude SDK harness). It never imports or requires ``codex-cli`` and never makes a
model call: it defines the two evidence channels a live Codex run produces and
the assertion helpers the downstream stage/domain/always-loaded smokes (10-12)
run against them.

Why two channels (see ``references/load-testing-research.md``): ``codex exec
--json`` exposes neither a ``skill_loaded`` event nor a ``spawn_agent`` item, so
on Codex both skill loading and subagent dispatch must be established
out-of-band:

1. **Canary / side-effect** — the fixture task instructs the agent to perform a
   skill-unique command that surfaces as a ``command_execution`` event in the
   JSONL. :func:`evaluate_canary` checks that command evidence.
2. **``SubagentStart`` hook log** — a ``SubagentStart`` hook (matcher = agent
   type) appends an agent-type sentinel to a log file on every dispatch, so
   orchestrator dispatch is verifiable even though the JSONL hides it. The hook
   payload is disambiguated by the agent-type field, never by ``session_id``.
   :func:`handle_subagent_start_payload` is the payload handler the live hook and
   the unit test share; :func:`evaluate_dispatch_log` checks the resulting log.

Both evaluators take already-parsed inputs (the codex JSONL events via the shared
``transcript_assertions`` parser and the dispatch log text), so
the default ``pytest`` path drives them on synthetic inputs with no codex-cli and
no model call.

Codex event shapes are pinned to codex-cli 0.140.0 (``type``/``agent_message``,
``command_execution``, ``file_change``) per the research doc; the canary
evaluator reuses ``transcript_assertions`` recursive search so a minor shape
change degrades gracefully rather than crashing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

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
# Canary / side-effect evidence
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CanarySpec:
    """A skill-unique observable the fixture task requires a loaded skill to emit.

    ``skill`` is the skill whose body prescribes the action (for the failure
    message). ``token`` is the high-entropy sentinel string checked against
    ``command_execution`` command strings.
    """

    skill: str
    token: str


@dataclass
class CanaryReport:
    """Collect every failed canary expectation from one evidence check."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Codex canary evidence failures:\n{joined}")


def evaluate_canary(
    report: CanaryReport,
    spec: CanarySpec,
    *,
    command_strings: Sequence[str] = (),
) -> None:
    """Check one canary against command strings.

    ``command_strings`` is the list of ``command_execution`` command strings from
    the codex JSONL (extract via :func:`command_strings_from_events`).
    """

    if any(spec.token in cmd for cmd in command_strings):
        report.observations.append(
            f"canary for skill {spec.skill!r} present in command"
        )
        return

    report.missing.append(
        f"canary for skill {spec.skill!r} (token {spec.token!r}) absent from "
        "command_execution commands — the skill-unique side effect was not produced, "
        f"so the skill body did not load"
    )


def evaluate_canaries(
    report: CanaryReport,
    specs: Iterable[CanarySpec],
    *,
    command_strings: Sequence[str] = (),
) -> None:
    """Run :func:`evaluate_canary` for every spec, collecting all failures."""

    for spec in specs:
        evaluate_canary(
            report,
            spec,
            command_strings=command_strings,
        )


def command_strings_from_events(events: Sequence) -> list[str]:
    """Extract ``command_execution`` command strings from parsed codex events.

    Accepts the ``TranscriptEvent`` objects produced by
    ``transcript_assertions.parse_codex_jsonl``; each event already exposes a
    ``commands`` tuple keyed off ``cmd``/``command``/``shell_command``. Returns a
    flat list so :func:`evaluate_canary` can scan it directly.
    """

    out: list[str] = []
    for event in events:
        out.extend(getattr(event, "commands", ()))
    return out


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
            report.observations.append(f"dispatch sentinel {agent_type!r} logged")
        else:
            report.missing.append(
                f"SubagentStart log missing dispatch sentinel {agent_type!r} "
                f"(observed: {dispatched})"
            )


def load_artifact(path: Path | str) -> dict | None:
    """Read and parse an output artifact, returning ``None`` if absent."""

    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
