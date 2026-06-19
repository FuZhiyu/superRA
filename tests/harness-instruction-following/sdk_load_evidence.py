#!/usr/bin/env python3
"""Skill-load evidence model and assertions for the Claude Agent-SDK harness.

This module is the CI-safe half of the Claude skill-load verification harness.
It never imports ``claude_agent_sdk`` and never makes a model call: it defines
the structured evidence a live SDK run produces (which skills loaded, in what
order, and where the first edit/write fell) plus the assertion helpers the
downstream live smokes (10-12) run against that evidence.

The live runner in ``sdk_load_harness.py`` produces a :class:`SkillLoadEvidence`
from real in-process hook callbacks; the unit test in
``test_sdk_load_evidence.py`` produces one from synthetic hook records. Both
drive the same assertion layer, so the green/red logic is exercised in default
CI with ``claude_agent_sdk`` absent.

Auto-loaded-vs-Skill-tool distinction (see load-testing-research.md): an
always-loaded skill (``using-superra``, ``report-in-markdown``) may surface via
an ``InstructionsLoaded`` event or a canary rather than a ``Skill`` tool_use.
``loaded_skill_names`` therefore unions both channels, so a required-skill
assertion can be satisfied by either.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SkillLoadRecord:
    """One observed skill load.

    ``event_index`` is the position of the load in the session's event stream
    (monotonic across all recorded hook callbacks), used to order skill loads
    against the first edit/write. ``source`` is ``"skill_tool"`` for an explicit
    ``Skill(...)`` tool_use or ``"instructions_loaded"`` for an auto-injected
    CLAUDE.md/rules/skill load surfaced by the ``InstructionsLoaded`` hook.
    """

    name: str
    event_index: int
    source: str = "skill_tool"


@dataclass(frozen=True)
class InstructionsLoadedRecord:
    """One ``InstructionsLoaded`` hook callback (CLAUDE.md / rules / memory)."""

    file_path: str
    event_index: int
    memory_type: str | None = None
    load_reason: str | None = None


@dataclass
class SkillLoadEvidence:
    """Structured evidence from one Claude Agent-SDK session.

    Produced by the live runner from real hook callbacks, or by the unit test
    from synthetic records. ``first_edit_index`` is the event index of the first
    edit/write tool_use, or ``None`` when the session performed no edit.
    """

    skill_loads: list[SkillLoadRecord] = field(default_factory=list)
    instructions_loaded: list[InstructionsLoadedRecord] = field(default_factory=list)
    first_edit_index: int | None = None

    @property
    def loaded_skill_names(self) -> set[str]:
        """Every skill name observed, across both load channels."""

        return {record.name for record in self.skill_loads}

    def first_load_index(self, skill_name: str) -> int | None:
        """Earliest event index at which ``skill_name`` was observed loading."""

        indices = [
            record.event_index
            for record in self.skill_loads
            if record.name == skill_name
        ]
        return min(indices) if indices else None

    def loaded_before_first_edit(self, skill_name: str) -> bool:
        """True if ``skill_name`` loaded before the first edit/write.

        A session with no edit (``first_edit_index is None``) counts any load as
        "before the edit" — there is no edit to precede.
        """

        load_index = self.first_load_index(skill_name)
        if load_index is None:
            return False
        if self.first_edit_index is None:
            return True
        return load_index < self.first_edit_index


@dataclass
class SkillLoadReport:
    """Collect every failed skill-load expectation from one evidence check."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Skill-load evidence failures:\n{joined}")


def check_skills_loaded_before_first_edit(
    report: SkillLoadReport,
    evidence: SkillLoadEvidence,
    required_skills: Iterable[str],
) -> None:
    """Require each named skill to have loaded, and loaded before the first edit.

    A clear failure names the missing skill (never loaded) or the late skill
    (loaded only after the first edit/write). Every required skill is checked so
    one run reports all failures at once.
    """

    loaded = evidence.loaded_skill_names
    for skill in required_skills:
        if skill not in loaded:
            report.missing.append(
                f"required skill {skill!r} never loaded "
                f"(observed: {sorted(loaded)})"
            )
            continue
        if not evidence.loaded_before_first_edit(skill):
            report.missing.append(
                f"required skill {skill!r} loaded at event "
                f"{evidence.first_load_index(skill)} but the first edit/write "
                f"was at event {evidence.first_edit_index} — skill must load "
                f"before the first edit"
            )
        else:
            report.observations.append(
                f"skill {skill!r} loaded before first edit"
            )


def evidence_from_hook_records(
    skill_tool_events: Sequence[tuple[str, int]] = (),
    instructions_loaded_events: Sequence[dict] = (),
    edit_event_indices: Sequence[int] = (),
) -> SkillLoadEvidence:
    """Build evidence from synthetic hook records (test + harness shared path).

    ``skill_tool_events`` is ``(skill_name, event_index)`` pairs from
    ``PreToolUse(matcher="Skill")`` callbacks. ``instructions_loaded_events`` is
    ``InstructionsLoaded`` payload dicts (``file_path``, ``event_index``, and
    optional ``memory_type`` / ``load_reason`` / ``skill_name``). An
    ``InstructionsLoaded`` event that names a skill also contributes a skill load
    via the ``instructions_loaded`` source, so always-loaded skills surfaced
    that way satisfy a required-skill assertion. ``edit_event_indices`` is the
    event indices of edit/write tool_use blocks; the minimum is the first edit.
    """

    skill_loads = [
        SkillLoadRecord(name=name, event_index=index, source="skill_tool")
        for name, index in skill_tool_events
    ]

    instructions_loaded: list[InstructionsLoadedRecord] = []
    for payload in instructions_loaded_events:
        instructions_loaded.append(
            InstructionsLoadedRecord(
                file_path=payload["file_path"],
                event_index=payload["event_index"],
                memory_type=payload.get("memory_type"),
                load_reason=payload.get("load_reason"),
            )
        )
        skill_name = payload.get("skill_name")
        if skill_name:
            skill_loads.append(
                SkillLoadRecord(
                    name=skill_name,
                    event_index=payload["event_index"],
                    source="instructions_loaded",
                )
            )

    first_edit_index = min(edit_event_indices) if edit_event_indices else None

    return SkillLoadEvidence(
        skill_loads=skill_loads,
        instructions_loaded=instructions_loaded,
        first_edit_index=first_edit_index,
    )
