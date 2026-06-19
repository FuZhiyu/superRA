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
  static frontmatter contract check (:func:`check_always_loaded_frontmatter`)
  and the live behavioral canary (:func:`check_behavioral_canary`), not by this
  evidence model. There is no ``InstructionsLoaded`` channel: that is not a
  registrable ``claude_agent_sdk`` hook event (the live run captured zero such
  events), so unioning it here would be unfounded.
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


@dataclass
class SkillLoadEvidence:
    """Structured evidence from one Claude Agent-SDK session.

    Produced by the live runner from real ``Skill`` PreToolUse hook callbacks, or
    by the unit test from synthetic records. ``first_edit_index`` is the event
    index of the first edit/write tool_use, or ``None`` when the session
    performed no edit.
    """

    skill_loads: list[SkillLoadRecord] = field(default_factory=list)
    first_edit_index: int | None = None
    assistant_texts: list[str] = field(default_factory=list)

    @property
    def loaded_skill_names(self) -> set[str]:
        """Every on-demand skill name the ``Skill`` hook observed loading."""

        return {record.name for record in self.skill_loads}

    @property
    def assistant_text(self) -> str:
        """All assistant text blocks from the session, joined.

        Empty unless the live runner was asked to capture text (the introspection
        canary in task 10 needs the dispatched agent's *answer*, not just its
        skill loads). Other callers ignore it.
        """

        return "\n".join(self.assistant_texts)

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

    This checks *on-demand* (Skill-tool) loads only — pass the stage/domain
    skills a fixture's manifest entry should trigger. Always-loaded skills are
    not loaded through the ``Skill`` tool; cover those with
    :func:`check_always_loaded_frontmatter` (static) and
    :func:`check_behavioral_canary` (live), not here.
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
    edit_event_indices: Sequence[int] = (),
) -> SkillLoadEvidence:
    """Build evidence from synthetic hook records (test + harness shared path).

    ``skill_tool_events`` is ``(skill_name, event_index)`` pairs from
    ``PreToolUse(matcher="Skill")`` callbacks. ``edit_event_indices`` is the
    event indices of edit/write tool_use blocks; the minimum is the first edit.
    """

    skill_loads = [
        SkillLoadRecord(name=name, event_index=index, source="skill_tool")
        for name, index in skill_tool_events
    ]
    first_edit_index = min(edit_event_indices) if edit_event_indices else None
    return SkillLoadEvidence(
        skill_loads=skill_loads,
        first_edit_index=first_edit_index,
    )


# --------------------------------------------------------------------------- #
# Always-loaded frontmatter contract (CI-safe, static)
# --------------------------------------------------------------------------- #


# The skills both role specs must preload via frontmatter. These never load
# through the Skill tool, so they are verified statically here and behaviorally
# (live) via check_behavioral_canary — not through the Skill PreToolUse hook.
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


# --------------------------------------------------------------------------- #
# Behavioral canary (reusable checker; fixtures owned by task 10)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class BehavioralCanarySpec:
    """A structural rule a *preloaded* skill prescribes, proven applied to output.

    Always-loaded skills are not observable through the ``Skill`` hook, so their
    loading is established behaviorally: the live agent's output obeys a
    format/decision only that skill's body defines. Task 10 supplies the
    fixtures (the prompt that triggers the rule and the expected output); task 08
    owns this reusable checker.

    - ``skill`` names the preloaded skill whose rule is under test (for the
      failure message), e.g. ``"superRA:report-in-markdown"``.
    - ``rule`` is a short human description of the prescribed behavior, e.g.
      "file references cited as markdown links with line anchors".
    - ``pattern`` is a regex the output must match to prove the rule was applied.
      A skill-unique structural rule (not a generic one the model would produce
      anyway) is what makes a match load-bearing.
    """

    skill: str
    rule: str
    pattern: str


def check_behavioral_canary(
    report: SkillLoadReport,
    spec: BehavioralCanarySpec,
    output_text: str,
) -> None:
    """Check one behavioral canary: the output applies the preloaded skill's rule.

    Passes if ``spec.pattern`` matches ``output_text`` (the rule the skill body
    prescribes shaped the output). Fails otherwise — a real "the preloaded skill
    body did not shape the output" finding, the live counterpart to the static
    frontmatter check. Reusable across task 10's canary fixtures; task 10 owns
    the ``BehavioralCanarySpec`` rows and the prompts that trigger them.
    """

    if re.search(spec.pattern, output_text):
        report.observations.append(
            f"behavioral canary for skill {spec.skill!r} satisfied "
            f"({spec.rule})"
        )
        return
    report.missing.append(
        f"behavioral canary for skill {spec.skill!r} failed: output does not "
        f"apply the rule {spec.rule!r} (pattern {spec.pattern!r} not found) — "
        f"the preloaded skill body did not shape the output"
    )
