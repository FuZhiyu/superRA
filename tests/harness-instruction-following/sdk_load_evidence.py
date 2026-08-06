#!/usr/bin/env python3
"""Skill-load evidence model and assertions for the Claude Agent-SDK harness.

This module is the CI-safe half of the Claude skill-load verification harness.
It never imports ``claude_agent_sdk`` and never makes a model call: it defines
the structured evidence a live SDK run produces (which on-demand skills loaded,
in what order, and where the first edit/write fell) plus the assertion helpers
the downstream live smokes (10-12) run against that evidence.

The live runner in ``sdk_load_harness.py`` produces a :class:`SkillLoadEvidence`
from real in-process ``PreToolUse(matcher="Skill")`` hook callbacks; the unit
test in ``test_sdk_load_evidence.py`` produces one from synthetic hook records.
Both drive the same assertion layer, so the green/red logic is exercised in
default CI with ``claude_agent_sdk`` absent.

Two separate channels, kept distinct (see load-testing-research.md):

- **On-demand skills** (stage/domain loads from the Skill-Load Manifest) load
  through the ``Skill`` tool, so the ``Skill`` PreToolUse hook records them by
  name. That is what :class:`SkillLoadEvidence` carries.
- **Always-loaded skills** (``using-superra``) are pulled in by the role skill's
  §Before You Start load instruction. Whether the harness
  surfaces those loads as ``Skill`` events depends on how the agent batches them,
  so the durable observable is the instruction itself, checked statically by
  :func:`check_always_loaded_load_instruction`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SkillLoadRecord:
    """One observed on-demand skill load via the ``Skill`` tool.

    ``event_index`` is the position of the load in the session's event stream
    (monotonic across all recorded hook callbacks), used to order skill loads
    against the first edit/write. ``source`` is always ``"skill_tool"`` — the
    only channel that records an on-demand load by name.
    """

    name: str
    event_index: int
    source: str = "skill_tool"


@dataclass(frozen=True)
class ReadLoadRecord:
    """One observed file read via the ``Read`` tool.

    The second evidence channel: stage references such as
    ``skills/superplan/references/planning-review.md`` are loaded via ``Read``,
    not the ``Skill`` tool, so the ``Skill`` hook never sees them. A
    ``PreToolUse(matcher="Read")`` hook records every read path here so a
    reference-file load expectation can be checked the same way a skill load is.

    ``path`` is the raw file path from the ``Read`` tool_input (whatever the SDK
    payload carried). ``event_index`` orders the read against skill loads and the
    first edit. ``source`` mirrors :class:`SkillLoadRecord`: ``"read_tool"`` for a
    top-level read, ``"subagent_read_tool"`` for a read inside a dispatched
    subagent.
    """

    path: str
    event_index: int
    source: str = "read_tool"


def normalize_skill_name(name: str) -> str:
    """Strip the ``superRA:`` (or any ``<plugin>:``) prefix from a skill name.

    The Skill-Load Manifest and the test tables name skills bare
    (``result-protection``); the ``Skill`` tool records them plugin-qualified
    (``superRA:result-protection``). Both spell the same skill, so every
    skill-name comparison normalizes both sides through this helper — a load
    recorded as ``superRA:result-protection`` satisfies an expected
    ``result-protection`` and vice versa. Only the leading ``<plugin>:`` segment
    is stripped (one colon), leaving any colon inside a name untouched.
    """

    _, sep, rest = name.partition(":")
    return rest if sep else name


@dataclass
class SkillLoadEvidence:
    """Structured evidence from one Claude Agent-SDK session.

    Produced by the live runner from real ``Skill`` PreToolUse hook callbacks, or
    by the unit test from synthetic records. ``first_edit_index`` is the event
    index of the first edit/write tool_use, or ``None`` when the session
    performed no edit.

    Skill-name lookups (:attr:`loaded_skill_names`, :meth:`first_load_index`,
    :meth:`loaded_before_first_edit`) are plugin-prefix-insensitive: the queried
    name and the recorded name are both normalized via :func:`normalize_skill_name`
    so a manifest-bare name matches a ``Skill``-tool plugin-qualified load.
    """

    skill_loads: list[SkillLoadRecord] = field(default_factory=list)
    first_edit_index: int | None = None
    read_loads: list[ReadLoadRecord] = field(default_factory=list)

    @property
    def loaded_skill_names(self) -> set[str]:
        """Every on-demand skill name the ``Skill`` hook observed loading.

        Plugin-prefix-stripped (via :func:`normalize_skill_name`) so membership
        tests against manifest-bare names match regardless of whether the load
        was recorded as ``superRA:result-protection`` or ``result-protection``.
        """

        return {normalize_skill_name(record.name) for record in self.skill_loads}

    @property
    def loaded_skill_names_raw(self) -> set[str]:
        """Every on-demand skill name exactly as the ``Skill`` hook recorded it."""

        return {record.name for record in self.skill_loads}

    @property
    def read_paths(self) -> set[str]:
        """Every file path the ``Read`` hook observed reading."""

        return {record.path for record in self.read_loads}

    def first_read_index(self, ref_path: str) -> int | None:
        """Earliest event index at which a path ending in ``ref_path`` was read.

        Matched by suffix so a manifest-relative reference path
        (``skills/superplan/references/planning-review.md``) matches the absolute
        or workspace-relative path the SDK ``Read`` payload carries — the agent
        reads it through the plugin install path, not the manifest-relative one.
        """

        indices = [
            record.event_index
            for record in self.read_loads
            if _read_path_matches(record.path, ref_path)
        ]
        return min(indices) if indices else None

    def read_before_first_edit(self, ref_path: str) -> bool:
        """True if ``ref_path`` was read before the first edit/write.

        A session with no edit counts any read as "before the edit" — there is
        no edit to precede (mirrors :meth:`loaded_before_first_edit`).
        """

        read_index = self.first_read_index(ref_path)
        if read_index is None:
            return False
        if self.first_edit_index is None:
            return True
        return read_index < self.first_edit_index

    def first_load_index(self, skill_name: str) -> int | None:
        """Earliest event index at which ``skill_name`` was observed loading.

        Plugin-prefix-insensitive: ``result-protection`` matches a load recorded
        as ``superRA:result-protection`` and vice versa (see
        :func:`normalize_skill_name`).
        """

        target = normalize_skill_name(skill_name)
        indices = [
            record.event_index
            for record in self.skill_loads
            if normalize_skill_name(record.name) == target
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


def _normalize_read_path(path: str) -> str:
    """Normalize a read path for suffix matching: forward slashes, no leading ./."""

    p = str(path).replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def _read_path_matches(observed: str, ref_path: str) -> bool:
    """True if ``observed`` is the same file as the manifest-relative ``ref_path``.

    The manifest names a repo-relative reference path; the SDK ``Read`` payload
    carries the path the agent actually opened (absolute or workspace-relative
    through the plugin install). Match by path-segment suffix so
    ``.../skills/superplan/references/planning-review.md`` satisfies the manifest
    entry ``skills/superplan/references/planning-review.md`` without a substring
    false positive on an unrelated path that merely contains the same characters.
    """

    obs = _normalize_read_path(observed).split("/")
    ref = _normalize_read_path(ref_path).split("/")
    if not ref:
        return False
    return obs[-len(ref):] == ref


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

    This checks *on-demand* (Skill-tool) loads only — pass the stage/domain
    skills a fixture's manifest entry should trigger. Cover the always-loaded
    pair with :func:`check_always_loaded_load_instruction`, not here.
    """

    loaded = evidence.loaded_skill_names
    for skill in required_skills:
        if normalize_skill_name(skill) not in loaded:
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
    edit_event_indices: Sequence[int] = (),
    read_tool_events: Sequence[tuple[str, int]] = (),
) -> SkillLoadEvidence:
    """Build evidence from synthetic hook records (test + harness shared path).

    ``skill_tool_events`` is ``(skill_name, event_index)`` pairs from
    ``PreToolUse(matcher="Skill")`` callbacks. ``read_tool_events`` is
    ``(read_path, event_index)`` pairs from ``PreToolUse(matcher="Read")``
    callbacks (the reference-load channel). ``edit_event_indices`` is the event
    indices of edit/write tool_use blocks; the minimum is the first edit.
    """

    skill_loads = [
        SkillLoadRecord(name=name, event_index=index, source="skill_tool")
        for name, index in skill_tool_events
    ]
    read_loads = [
        ReadLoadRecord(path=path, event_index=index, source="read_tool")
        for path, index in read_tool_events
    ]
    first_edit_index = min(edit_event_indices) if edit_event_indices else None
    return SkillLoadEvidence(
        skill_loads=skill_loads,
        first_edit_index=first_edit_index,
        read_loads=read_loads,
    )


# --------------------------------------------------------------------------- #
# Always-loaded load-instruction contract (CI-safe, static)
# --------------------------------------------------------------------------- #


# The skills every role skill must pull in before acting.
ALWAYS_LOADED_SKILLS = ("superRA:using-superra", "superRA:communicate")

# Role skills that carry the always-loaded contract as a body load instruction.
ROLE_SKILL_FILES = ("skills/implement-task/SKILL.md", "skills/review-task/SKILL.md")

# The section whose first step is the load instruction.
LOAD_INSTRUCTION_HEADING = "## Before You Start"


def parse_section(skill_text: str, heading: str) -> str:
    """Return the body under ``heading``, up to the next same-or-higher heading.

    Stdlib-only (no PyYAML dependency on the CI path). Returns ``""`` when the
    heading is absent.
    """

    level = len(heading) - len(heading.lstrip("#"))
    lines = skill_text.splitlines()
    try:
        start = lines.index(heading.rstrip())
    except ValueError:
        return ""
    body: list[str] = []
    for line in lines[start + 1 :]:
        m = re.match(r"(#+)\s", line)
        if m and len(m.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body)


def check_always_loaded_load_instruction(
    report: SkillLoadReport,
    repo_root: Path | str,
    *,
    role_skill_files: Iterable[str] = ROLE_SKILL_FILES,
    required_skills: Iterable[str] = ALWAYS_LOADED_SKILLS,
    heading: str = LOAD_INSTRUCTION_HEADING,
) -> None:
    """Assert every role skill instructs loading every always-loaded skill.

    CI-safe and static: reads each role skill's ``heading`` section and records a
    failure for any missing file, missing section, or missing always-loaded skill
    name. Dispatch reaches the role skill by name and the role skill reaches the
    always-loaded skills by this instruction — dropping it regresses the loading
    contract for every dispatched agent on every harness.
    """

    root = Path(repo_root)
    required = list(required_skills)
    for rel in role_skill_files:
        path = root / rel
        if not path.exists():
            report.missing.append(f"role skill {rel} not found at {path}")
            continue
        section = parse_section(path.read_text(encoding="utf-8"), heading)
        if not section.strip():
            report.missing.append(f"{rel} has no {heading!r} section")
            continue
        for skill in required:
            if skill in section:
                report.observations.append(
                    f"{rel} {heading} instructs loading {skill!r}"
                )
            else:
                report.missing.append(
                    f"{rel} {heading} does not instruct loading always-loaded "
                    f"skill {skill!r}"
                )
