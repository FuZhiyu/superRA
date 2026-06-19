#!/usr/bin/env python3
"""CI-safe unit tests for the Claude Agent-SDK skill-load evidence layer.

Drives :mod:`sdk_load_evidence` on synthetic hook records and on the real
in-repo role specs — no live model call, and ``claude_agent_sdk`` is never
imported. Covers:

- on-demand skill ordering: green plus the two red cases the parent objective
  names (required skill missing; skill loaded only after the first edit);
- the static always-loaded frontmatter contract (green against the real role
  specs; red against a synthetic spec missing a skill);
- the reusable behavioral-canary checker task 10 consumes (green + red).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from sdk_load_evidence import (  # noqa: E402
    ALWAYS_LOADED_SKILLS,
    BehavioralCanarySpec,
    SkillLoadReport,
    check_always_loaded_frontmatter,
    check_behavioral_canary,
    check_skills_loaded_before_first_edit,
    evidence_from_hook_records,
    normalize_skill_name,
    parse_frontmatter_skills,
)


def test_default_ci_path_never_imports_claude_agent_sdk():
    # Importing the evidence layer (and this test) must not pull in the SDK; the
    # live runner that imports it is only touched on the RUN_LIVE_HARNESS path.
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("sdk_load_evidence") is not None


# --------------------------------------------------------------------------- #
# On-demand skill-load ordering
# --------------------------------------------------------------------------- #


def test_green_required_skills_load_before_first_edit():
    evidence = evidence_from_hook_records(
        skill_tool_events=[
            ("econ-data-analysis", 0),
            ("writing", 1),
        ],
        edit_event_indices=[5],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "writing"],
    )

    report.assert_ok()
    assert len(report.observations) == 2


def test_red_required_skill_never_loaded():
    # A stage/domain skill the manifest should trigger never loads — a real
    # loading-contract finding to escalate; the assertion must fail.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("econ-data-analysis", 0)],
        edit_event_indices=[3],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "writing"],
    )

    assert not report.ok
    assert len(report.missing) == 1
    assert "writing" in report.missing[0]
    assert "never loaded" in report.missing[0]


def test_red_skill_loaded_only_after_first_edit():
    # The skill loaded, but after the agent already started editing — the
    # load-before-mutation invariant is violated.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("econ-data-analysis", 0), ("writing", 4)],
        edit_event_indices=[2],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "writing"],
    )

    assert not report.ok
    assert len(report.missing) == 1
    assert "writing" in report.missing[0]
    assert "before the first edit" in report.missing[0]


def test_no_edit_session_counts_any_load_as_before_edit():
    # A session that never edits has no boundary, so any load passes the ordering
    # check (the read-only / pure-read fixture path).
    evidence = evidence_from_hook_records(
        skill_tool_events=[("econ-data-analysis", 0)],
        edit_event_indices=[],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(report, evidence, ["econ-data-analysis"])

    report.assert_ok()


def test_all_failures_collected_together():
    evidence = evidence_from_hook_records(
        skill_tool_events=[("writing", 6)],
        edit_event_indices=[1],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "writing"],
    )

    assert len(report.missing) == 2
    assert "econ-data-analysis" in report.missing[0]
    assert "never loaded" in report.missing[0]
    assert "writing" in report.missing[1]
    assert "before the first edit" in report.missing[1]


# --------------------------------------------------------------------------- #
# Plugin-prefix-insensitive skill-name matching
# --------------------------------------------------------------------------- #


def test_normalize_skill_name_strips_plugin_prefix():
    assert normalize_skill_name("superRA:result-protection") == "result-protection"
    assert normalize_skill_name("result-protection") == "result-protection"
    # Only the leading <plugin>: segment is stripped (one colon).
    assert normalize_skill_name("superRA:a:b") == "a:b"


def test_loaded_skill_names_strips_plugin_prefix():
    # The Skill tool records loads plugin-qualified; the property normalizes so a
    # bare manifest name matches.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:result-protection", 0)],
    )
    assert evidence.loaded_skill_names == {"result-protection"}
    assert evidence.loaded_skill_names_raw == {"superRA:result-protection"}


def test_qualified_load_satisfies_bare_expected_skill():
    # Live regression: expected bare `result-protection` is satisfied by an
    # observed plugin-qualified `superRA:result-protection` load. The load is
    # real, so this must be green, not a false negative.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:result-protection", 0)],
        edit_event_indices=[3],
    )
    report = SkillLoadReport()
    check_skills_loaded_before_first_edit(report, evidence, ["result-protection"])
    report.assert_ok()


def test_bare_load_satisfies_qualified_expected_skill():
    # Symmetric: expected qualified name satisfied by an observed bare load.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("semantic-merge", 0)],
        edit_event_indices=[3],
    )
    report = SkillLoadReport()
    check_skills_loaded_before_first_edit(report, evidence, ["superRA:semantic-merge"])
    report.assert_ok()


def test_qualified_observations_still_reject_genuinely_absent_skill():
    # Normalization must not turn the negative case green: a skill that genuinely
    # never loaded is still reported missing even amid plugin-qualified loads.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:result-protection", 0), ("superRA:using-superra", 1)],
        edit_event_indices=[3],
    )
    report = SkillLoadReport()
    check_skills_loaded_before_first_edit(report, evidence, ["semantic-merge"])
    assert not report.ok
    assert "semantic-merge" in report.missing[0]
    assert "never loaded" in report.missing[0]


# --------------------------------------------------------------------------- #
# Always-loaded frontmatter contract (static)
# --------------------------------------------------------------------------- #


def test_parse_frontmatter_inline_list():
    text = (
        "---\n"
        "name: implementer\n"
        "skills: [superRA:using-superra, superRA:report-in-markdown]\n"
        "---\n"
        "body\n"
    )
    assert parse_frontmatter_skills(text) == [
        "superRA:using-superra",
        "superRA:report-in-markdown",
    ]


def test_parse_frontmatter_block_list():
    text = (
        "---\n"
        "name: implementer\n"
        "skills:\n"
        "  - superRA:using-superra\n"
        "  - superRA:report-in-markdown\n"
        "---\n"
        "body\n"
    )
    assert parse_frontmatter_skills(text) == [
        "superRA:using-superra",
        "superRA:report-in-markdown",
    ]


def test_parse_frontmatter_no_block():
    assert parse_frontmatter_skills("no frontmatter here") == []


def test_green_always_loaded_frontmatter_real_role_specs():
    # The real agents/implementer.md and agents/reviewer.md must both declare
    # both always-loaded skills — this is the live preloaded-skill contract.
    report = SkillLoadReport()
    check_always_loaded_frontmatter(report, REPO_ROOT)
    report.assert_ok()
    # two specs x two skills
    assert len(report.observations) == 4


def test_red_always_loaded_frontmatter_missing_skill(tmp_path):
    # A role spec missing report-in-markdown is a regressed preloaded contract.
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "implementer.md").write_text(
        "---\nname: implementer\nskills: [superRA:using-superra]\n---\nbody\n",
        encoding="utf-8",
    )
    (tmp_path / "agents" / "reviewer.md").write_text(
        "---\nname: reviewer\n"
        "skills: [superRA:using-superra, superRA:report-in-markdown]\n---\nbody\n",
        encoding="utf-8",
    )
    report = SkillLoadReport()
    check_always_loaded_frontmatter(report, tmp_path)

    assert not report.ok
    assert len(report.missing) == 1
    assert "implementer.md" in report.missing[0]
    assert "superRA:report-in-markdown" in report.missing[0]


def test_red_always_loaded_frontmatter_missing_file(tmp_path):
    report = SkillLoadReport()
    check_always_loaded_frontmatter(report, tmp_path)
    # both specs absent → one missing-file failure each
    assert len(report.missing) == 2
    assert all("not found" in m for m in report.missing)


def test_always_loaded_skills_constant_is_qualified():
    # The contract checks the plugin-qualified names that appear in frontmatter.
    assert ALWAYS_LOADED_SKILLS == (
        "superRA:using-superra",
        "superRA:report-in-markdown",
    )


# --------------------------------------------------------------------------- #
# Behavioral canary (reusable checker; fixtures owned by task 10)
# --------------------------------------------------------------------------- #


def test_green_behavioral_canary_rule_applied():
    # report-in-markdown prescribes file refs as markdown links with line anchors.
    spec = BehavioralCanarySpec(
        skill="superRA:report-in-markdown",
        rule="file references cited as markdown links with line anchors",
        pattern=r"\[[^\]]+\]\([^)]+#L\d+\)",
    )
    output = "See [sdk_load_harness.py:42](sdk_load_harness.py#L42) for the hook."
    report = SkillLoadReport()

    check_behavioral_canary(report, spec, output)

    report.assert_ok()
    assert len(report.observations) == 1


def test_red_behavioral_canary_rule_absent():
    # Output uses a backtick path instead of the prescribed markdown-link form —
    # the preloaded skill rule did not shape it.
    spec = BehavioralCanarySpec(
        skill="superRA:report-in-markdown",
        rule="file references cited as markdown links with line anchors",
        pattern=r"\[[^\]]+\]\([^)]+#L\d+\)",
    )
    output = "See `sdk_load_harness.py` line 42 for the hook."
    report = SkillLoadReport()

    check_behavioral_canary(report, spec, output)

    assert not report.ok
    assert len(report.missing) == 1
    assert "superRA:report-in-markdown" in report.missing[0]
    assert "did not shape the output" in report.missing[0]


# --------------------------------------------------------------------------- #
# Read-channel evidence (reference loads via the Read tool; task 11)
# --------------------------------------------------------------------------- #

_REF = "skills/superplan/references/planning-review.md"


def test_read_channel_records_path_and_orders_before_edit():
    evidence = evidence_from_hook_records(
        read_tool_events=[(f"/install/{_REF}", 1)],
        edit_event_indices=[3],
    )
    assert evidence.read_paths == {f"/install/{_REF}"}
    assert evidence.first_read_index(_REF) == 1
    assert evidence.read_before_first_edit(_REF) is True


def test_read_channel_after_edit_is_not_before():
    evidence = evidence_from_hook_records(
        read_tool_events=[(f"/install/{_REF}", 5)],
        edit_event_indices=[2],
    )
    assert evidence.read_before_first_edit(_REF) is False


def test_read_channel_no_edit_counts_any_read_as_before():
    evidence = evidence_from_hook_records(
        read_tool_events=[(f"/install/{_REF}", 0)],
        edit_event_indices=[],
    )
    assert evidence.read_before_first_edit(_REF) is True


def test_read_channel_missing_reference_returns_none():
    evidence = evidence_from_hook_records(
        read_tool_events=[("/install/skills/superplan/SKILL.md", 0)],
    )
    assert evidence.first_read_index(_REF) is None
    assert evidence.read_before_first_edit(_REF) is False
