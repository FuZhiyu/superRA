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
   skill-unique observable action that is only producible if the named skill body
   loaded: either a prescribed command (surfacing as a ``command_execution``
   event in the JSONL) or a sentinel value written into the output artifact. The
   :func:`evaluate_canary` evaluator scans both sources for the canary token.
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
    message). ``token`` is the high-entropy sentinel string that proves the skill
    body was in context. The token is checked against two sources, either of
    which satisfies the canary:

    - ``in_command``: the token appears in a ``command_execution`` command string
      (a command the skill body told the agent to run), and/or
    - ``in_artifact_field``: a JSON path (dotted, e.g. ``"loading.canary"``) in
      the output artifact whose value must equal the token.

    A spec sets at least one source. Keeping the convention to "token in command
    OR token at artifact field" lets the stage (11) and domain (12) smokes reuse
    one evaluator with per-skill ``CanarySpec`` rows and no bespoke parsing.
    """

    skill: str
    token: str
    in_command: bool = True
    in_artifact_field: str | None = None


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


def _artifact_value_at(artifact: dict | None, dotted_path: str):
    """Return the value at a dotted JSON path, or a sentinel ``_MISSING``."""

    if artifact is None:
        return _MISSING
    node = artifact
    for part in dotted_path.split("."):
        if not isinstance(node, dict) or part not in node:
            return _MISSING
        node = node[part]
    return node


_MISSING = object()


def evaluate_canary(
    report: CanaryReport,
    spec: CanarySpec,
    *,
    command_strings: Sequence[str] = (),
    artifact: dict | None = None,
) -> None:
    """Check one canary against command strings and/or the output artifact.

    ``command_strings`` is the list of ``command_execution`` command strings from
    the codex JSONL (extract via :func:`command_strings_from_events`).
    ``artifact`` is the parsed output-artifact JSON (or ``None`` if absent).

    The canary passes if the token is found in any required source. A spec that
    enables ``in_command`` is satisfied by the token in any command; a spec with
    ``in_artifact_field`` is satisfied by that field equalling the token. The
    canary fails only if none of its enabled sources carry the token — an absent
    canary is a real "skill body did not load" finding to escalate, not a test
    bug.
    """

    found_in_command = False
    if spec.in_command:
        found_in_command = any(spec.token in cmd for cmd in command_strings)

    found_in_artifact = False
    if spec.in_artifact_field is not None:
        value = _artifact_value_at(artifact, spec.in_artifact_field)
        found_in_artifact = value is not _MISSING and value == spec.token

    if found_in_command or found_in_artifact:
        where = []
        if found_in_command:
            where.append("command")
        if found_in_artifact:
            where.append(f"artifact field {spec.in_artifact_field!r}")
        report.observations.append(
            f"canary for skill {spec.skill!r} present in {' and '.join(where)}"
        )
        return

    sources = []
    if spec.in_command:
        sources.append("any command_execution command")
    if spec.in_artifact_field is not None:
        sources.append(f"artifact field {spec.in_artifact_field!r}")
    report.missing.append(
        f"canary for skill {spec.skill!r} (token {spec.token!r}) absent from "
        f"{' / '.join(sources)} — the skill-unique side effect was not produced, "
        f"so the skill body did not load"
    )


def evaluate_canaries(
    report: CanaryReport,
    specs: Iterable[CanarySpec],
    *,
    command_strings: Sequence[str] = (),
    artifact: dict | None = None,
) -> None:
    """Run :func:`evaluate_canary` for every spec, collecting all failures."""

    for spec in specs:
        evaluate_canary(
            report,
            spec,
            command_strings=command_strings,
            artifact=artifact,
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
    that never appears is a missing-dispatch finding; the caller decides whether
    a documented direct-mode fallback (handled out-of-band by the smoke) excuses
    it.
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
