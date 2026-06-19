#!/usr/bin/env python3
"""Always-loaded skill live coverage (task 10), CI-safe core + manual live entry.

Verifies that **both** always-loaded skills — ``superRA:using-superra`` and
``superRA:report-in-markdown`` (load-contract LC001) — are in the dispatched
role's context before any task-file or code edit, in both harnesses, and
regression-guards that contract.

What is already established live (do not re-litigate; this module turns the
one-off confirmations into committed checks):

- **Claude autoloads** both skills via the agents' frontmatter ``skills: [...]``.
  An autoloaded skill is *invisible* to the ``Skill`` PreToolUse hook by
  construction: zero ``Skill``-tool loads is the expected, correct signal, not a
  failure. So the Claude side evidences the contract two ways:
    1. the **static frontmatter contract** (08's
       :func:`sdk_load_evidence.check_always_loaded_frontmatter`) — the
       deterministic backbone, asserting both role specs declare both skills; and
    2. a **live discriminating canary** — dispatch the real
       ``superRA:implementer`` with an introspection prompt that asks it to state
       its markdown file-citation rule *without loading any skill or reading any
       file*, then check the answer recites ``report-in-markdown``'s anchor-link
       rule **with zero ``Skill`` loads**. The rule must be one the base model
       would not produce unprompted; the bare file-link format is too close to a
       model default, so the canary keys off the rule's discriminating clause
       (links *with line anchors*, *not* backtick-wrapped paths) and rejects a
       backtick-path answer or a "no rule" answer.

- **Codex does not autoload**, so a frontmatter-only skill never enters context
  there; the role-spec body instruction is what loads the always-loaded skills.
  The Codex side uses 09's canary convention
  (:mod:`codex_load_evidence`): per-skill :class:`~codex_load_evidence.CanarySpec`
  rows whose skill-unique tokens are only producible if the skill body loaded —
  exercising the role-spec body-load path that substitutes for Claude's autoload.

This module's evaluators take already-captured inputs (the dispatched agent's
answer text + its skill-load evidence for Claude; command strings + the output
artifact for Codex), so the default ``pytest`` path drives them on synthetic
inputs with no model call and no SDK/codex-cli import. The live Claude entry
:func:`run_claude_introspection_canary` consumes 08's
:func:`sdk_load_harness.run_skill_load_session` (it does not re-implement evidence
capture) and is gated behind ``RUN_LIVE_HARNESS=1``.

The live SDK dispatch is nondeterministic (it leans on the top-level model to
issue the Task dispatch). The live entry therefore defaults to ``sonnet`` (which
dispatched reliably; haiku was flaky) and supports a small pass@k retry window so
a single flaky dispatch does not red the canary. A genuine failure — the rule
absent from a reliable dispatch, or a non-zero always-loaded ``Skill`` load — is
a real loading-contract finding to escalate, not an assertion to relax.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from codex_load_evidence import CanarySpec
from sdk_load_evidence import (
    ALWAYS_LOADED_SKILLS,
    BehavioralCanarySpec,
    SkillLoadEvidence,
    SkillLoadReport,
    check_always_loaded_frontmatter,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "always-loaded-canary"

# --------------------------------------------------------------------------- #
# Claude: discriminating introspection canary (always-loaded -> report-in-markdown)
# --------------------------------------------------------------------------- #

# The introspection prompt. It forbids loading any skill or reading any file, so
# a context-grounded recital of report-in-markdown's rule can only come from the
# autoloaded skill body — not from an on-demand Skill load (which the hook would
# catch) or a file read. Kept to one short answer turn per the parent objective.
INTROSPECTION_PROMPT = (
    "Without loading any skill and without reading any file, state in one or two "
    "sentences your rule for how to cite a source file inside a markdown report. "
    "If you have no such rule in your current context, answer exactly NO_RULE. "
    "Do not call the Skill tool, the Read tool, or any other tool — answer from "
    "the instructions already in your context."
)

# The discriminating canary spec. report-in-markdown's rule is "markdown links
# with line anchors, NOT backtick-wrapped paths". The bare link-with-anchor
# *format* is too close to a model default to discriminate, so the pattern keys
# off the rule's discriminating clauses: the answer must mention anchors/line
# anchors AND contrast against backtick-wrapped paths. A base model asked the
# same question unprompted recites neither the "line anchor" requirement nor the
# explicit "not backticks" contrast.
INTROSPECTION_CANARY = BehavioralCanarySpec(
    skill="superRA:report-in-markdown",
    rule=(
        "file references cited as markdown links with line anchors, not "
        "backtick-wrapped paths"
    ),
    pattern=(
        r"(?is)"  # case-insensitive, dotall
        r"(?=.*\b(?:line\s+)?anchors?\b)"  # mentions anchors / line anchors
        # contrasts against backtick-wrapped paths with a negation/contrast word
        r"(?=.*\b(?:not|never|instead\s+of|rather\s+than|avoid)\b"
        r".*\bback ?ticks?\b)"
        r".*"
    ),
)

# The skill name whose autoload makes the introspection answer load-bearing. The
# canary is only valid if this skill recorded ZERO Skill-tool loads (it was
# autoloaded, not loaded on demand). A non-zero count would mean the rule reached
# context through an on-demand load, which does not prove the always-loaded /
# autoload contract.
INTROSPECTION_AUTOLOAD_SKILL = "superRA:report-in-markdown"


@dataclass
class IntrospectionCanaryReport:
    """Result of one always-loaded introspection canary evaluation."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Always-loaded canary failures:\n{joined}")


def _skill_load_count(evidence: SkillLoadEvidence, skill: str) -> int:
    return sum(1 for record in evidence.skill_loads if record.name == skill)


def evaluate_introspection_canary(
    report: IntrospectionCanaryReport,
    answer_text: str,
    evidence: SkillLoadEvidence,
    *,
    spec: BehavioralCanarySpec = INTROSPECTION_CANARY,
    autoload_skill: str = INTROSPECTION_AUTOLOAD_SKILL,
) -> None:
    """Check the always-loaded introspection canary against one dispatch.

    Two conditions must both hold for the canary to pass:

    1. ``answer_text`` recites the skill's discriminating rule (``spec.pattern``
       matches) — the autoloaded skill body shaped the answer; and
    2. the dispatched agent recorded **zero** ``Skill``-tool loads of
       ``autoload_skill`` — proving the rule reached context by *autoload*, not by
       an on-demand load (which would not establish the always-loaded contract).

    A NO_RULE / backtick-path / empty answer fails condition 1; a non-zero load
    count fails condition 2. Either failure is a real always-loaded contract
    finding to escalate, not an assertion to relax.
    """

    load_count = _skill_load_count(evidence, autoload_skill)
    rule_recited = bool(re.search(spec.pattern, answer_text))

    if load_count != 0:
        report.missing.append(
            f"always-loaded skill {autoload_skill!r} was loaded on demand "
            f"{load_count} time(s) via the Skill tool — it must reach context by "
            f"autoload (zero Skill loads), so the introspection answer does not "
            f"establish the always-loaded contract"
        )
    if not rule_recited:
        report.missing.append(
            f"introspection answer does not recite {spec.skill!r}'s rule "
            f"({spec.rule}); the autoloaded skill body did not shape the answer. "
            f"answer was: {answer_text.strip()[:200]!r}"
        )
    if not report.missing:
        report.observations.append(
            f"always-loaded canary satisfied: {spec.skill!r} rule recited with "
            f"zero on-demand Skill loads (autoloaded)"
        )


def check_claude_always_loaded_static(
    report: SkillLoadReport,
    repo_root: Path | str = REPO_ROOT,
) -> None:
    """Deterministic backbone: both role specs declare both always-loaded skills.

    Thin pass-through to 08's static frontmatter contract, named here so the
    task-10 callers and tests read against one always-loaded entry point. This is
    the check that runs in CI; the live introspection canary corroborates it.
    """

    check_always_loaded_frontmatter(report, repo_root)


# --------------------------------------------------------------------------- #
# Codex: canary specs exercising the role-spec body-load path (no autoload)
# --------------------------------------------------------------------------- #

# report-in-markdown's self-diagnose CLI is named only in the skill body
# (`check_markdown.py`). The fixture task asks the agent to run it against the
# artifact, so the script name appears as a command_execution only if the skill
# body loaded. The token is the script basename — skill-unique and not something
# the base model would run unprompted on a sentinel-collection task.
CODEX_REPORT_IN_MARKDOWN_CANARY = CanarySpec(
    skill="superRA:report-in-markdown",
    token="check_markdown.py",
    in_command=True,
    in_artifact_field="report_in_markdown_canary",
)

# using-superra's Task Interface body prescribes reading a task with the wrapper
# `./superRA/superra task read <path>`, not a bare file Read. The fixture asks
# the agent to record the exact read-command convention it must follow, so the
# wrapper-read token at the artifact field is producible only if the
# using-superra body loaded. The command form also surfaces as a
# command_execution when the agent actually runs the read.
CODEX_USING_SUPERRA_CANARY = CanarySpec(
    skill="superRA:using-superra",
    token="superra task read",
    in_command=True,
    in_artifact_field="using_superra_canary",
)

CODEX_ALWAYS_LOADED_CANARIES = (
    CODEX_REPORT_IN_MARKDOWN_CANARY,
    CODEX_USING_SUPERRA_CANARY,
)


# --------------------------------------------------------------------------- #
# Live Claude entry (manual-only; consumes 08's harness)
# --------------------------------------------------------------------------- #


def _gate_is_open() -> bool:
    return os.environ.get("RUN_LIVE_HARNESS") == "1"


def run_claude_introspection_canary(
    *,
    cwd: Path | str,
    model: str | None = None,
    attempts: int = 3,
) -> IntrospectionCanaryReport:
    """Run the live Claude always-loaded introspection canary (manual-only).

    Dispatches the real ``superRA:implementer`` via 08's
    :func:`sdk_load_harness.run_skill_load_session` (capturing assistant text),
    then evaluates :func:`evaluate_introspection_canary`. Because the live SDK
    dispatch is nondeterministic, it runs up to ``attempts`` times (pass@k) and
    returns the first passing report, or the last failing report if none pass.

    Defaults to ``CLAUDE_MODEL`` or ``sonnet`` — sonnet dispatched reliably in the
    live confirmation; haiku was flaky. Gated on ``RUN_LIVE_HARNESS=1``; raises if
    the gate is closed so a stray CI import fails loudly instead of calling a
    model. Deferred import of the SDK runner keeps it off the CI path.
    """

    if not _gate_is_open():
        raise RuntimeError(
            "RUN_LIVE_HARNESS is not set to 1 — the always-loaded introspection "
            "canary is manual-only and must never run in default CI."
        )

    # Deferred: importing the runner pulls claude_agent_sdk on the live path only.
    from sdk_load_harness import run_skill_load_session

    resolved_model = model or os.environ.get("CLAUDE_MODEL", "sonnet")

    last_report = IntrospectionCanaryReport()
    for _ in range(max(1, attempts)):
        evidence = run_skill_load_session(
            INTROSPECTION_PROMPT,
            cwd=cwd,
            model=resolved_model,
            capture_text=True,
        )
        report = IntrospectionCanaryReport()
        evaluate_introspection_canary(report, evidence.assistant_text, evidence)
        if report.ok:
            return report
        last_report = report
    return last_report


def _main() -> int:
    if not _gate_is_open():
        print(
            "SKIP  RUN_LIVE_HARNESS is not set to 1 — the always-loaded "
            "introspection canary is opt-in and never runs in CI.\n"
            "      Set RUN_LIVE_HARNESS=1 (with claude-agent-sdk installed via "
            "uv run --with) to run it."
        )
        return 0

    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "ws"
        workspace.mkdir()
        # Minimal seeded tree so a real role dispatch resolves; the introspection
        # prompt does not read it, but the SDK session wants a cwd.
        (workspace / "superRA").mkdir()
        report = run_claude_introspection_canary(cwd=workspace)

    for obs in report.observations:
        print(f"OK: {obs}")
    if not report.ok:
        print("FAIL: always-loaded introspection canary did not pass:")
        for msg in report.missing:
            print(f"  - {msg}")
        print(
            "      A reliable-dispatch failure here is a real always-loaded "
            "loading-contract finding to escalate, not a test to relax."
        )
        return 1
    print("OK: report-in-markdown rule recited via autoload (zero Skill loads).")
    print(f"    always-loaded skills under contract: {list(ALWAYS_LOADED_SKILLS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
