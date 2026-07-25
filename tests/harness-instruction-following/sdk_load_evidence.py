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
- **Always-loaded skills** (``using-superra``, ``report-in-markdown``) are
  preloaded via agent frontmatter ``skills: [...]``; they emit no ``Skill``
  tool_use and the SDK init message lists only *available* skills, not per-agent
  preloaded ones, so the ``Skill`` hook cannot see them. They are covered by the
  static frontmatter contract check (:func:`check_always_loaded_frontmatter`).
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
    skills a fixture's manifest entry should trigger. Always-loaded skills are
    not loaded through the ``Skill`` tool; cover those with
    :func:`check_always_loaded_frontmatter`, not here.
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
# Always-loaded frontmatter contract (CI-safe, static)
# --------------------------------------------------------------------------- #


# The skills both role specs must preload via frontmatter. These never load
# through the Skill tool, so they are verified statically here.
ALWAYS_LOADED_SKILLS = ("superRA:using-superra", "superRA:report-in-markdown")

# Role specs that carry the always-loaded contract in frontmatter.
ROLE_SPEC_FILES = ("agents/implementer.md", "agents/reviewer.md")


def parse_frontmatter_skills(spec_text: str) -> list[str]:
    """Parse the ``skills:`` list from an agent role-spec YAML frontmatter block.

    Stdlib-only (no PyYAML dependency on the CI path): reads the leading
    ``---``-delimited block and extracts the inline ``skills: [a, b]`` list. Both
    role specs use the inline-list form; a block-list form (``skills:`` then
    ``- a``) is also accepted so the checker is robust to a reformat. Returns the
    skill names stripped of surrounding quotes/whitespace, or ``[]`` if there is
    no frontmatter or no ``skills:`` key.
    """

    if not spec_text.startswith("---"):
        return []
    end = spec_text.find("\n---", 3)
    if end == -1:
        return []
    block = spec_text[3:end]

    lines = block.splitlines()
    for i, raw in enumerate(lines):
        line = raw.rstrip()
        m = re.match(r"\s*skills:\s*(.*)$", line)
        if not m:
            continue
        rest = m.group(1).strip()
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1]
            return [_clean_skill(tok) for tok in inner.split(",") if tok.strip()]
        # Block-list form: subsequent "- name" lines.
        items: list[str] = []
        for follow in lines[i + 1 :]:
            fm = re.match(r"\s*-\s*(.+)$", follow)
            if not fm:
                break
            items.append(_clean_skill(fm.group(1)))
        return items
    return []


def _clean_skill(token: str) -> str:
    return token.strip().strip("'\"").strip()


def check_always_loaded_frontmatter(
    report: SkillLoadReport,
    repo_root: Path | str,
    *,
    role_spec_files: Iterable[str] = ROLE_SPEC_FILES,
    required_skills: Iterable[str] = ALWAYS_LOADED_SKILLS,
) -> None:
    """Assert every role spec declares every always-loaded skill in ``skills:``.

    CI-safe and static: parses each role-spec frontmatter and records a failure
    for any role spec missing the file or missing a required always-loaded skill.
    A missing declaration means the preloaded-skill contract regressed — that is
    a real loading-contract finding, not a test bug.
    """

    root = Path(repo_root)
    required = list(required_skills)
    for rel in role_spec_files:
        path = root / rel
        if not path.exists():
            report.missing.append(f"role spec {rel} not found at {path}")
            continue
        declared = parse_frontmatter_skills(path.read_text(encoding="utf-8"))
        for skill in required:
            if skill in declared:
                report.observations.append(
                    f"{rel} declares always-loaded skill {skill!r}"
                )
            else:
                report.missing.append(
                    f"{rel} frontmatter skills: is missing always-loaded skill "
                    f"{skill!r} (declared: {declared})"
                )
