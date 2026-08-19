#!/usr/bin/env python3
"""CI-safe unit tests for the Claude Agent-SDK skill-load evidence layer.

Drives :mod:`sdk_load_evidence` on synthetic hook records and on the real
in-repo role skills — no live model call, and ``claude_agent_sdk`` is never
imported. Covers:

- on-demand skill ordering: green plus the two red cases the parent objective
  names (required skill missing; skill loaded only after the first edit);
- the static always-loaded load-instruction contract (green against the real role
  skills; red against a synthetic skill missing one);
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
    LOAD_INSTRUCTION_HEADING,
    ROLE_SKILL_FILES,
    SkillLoadReport,
    check_always_loaded_load_instruction,
    check_skills_loaded_before_first_edit,
    evidence_from_hook_records,
    normalize_skill_name,
    parse_section,
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
            ("academic-writing", 1),
        ],
        edit_event_indices=[5],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "academic-writing"],
    )

    report.assert_ok()


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
        ["econ-data-analysis", "academic-writing"],
    )

    assert not report.ok


def test_red_skill_loaded_only_after_first_edit():
    # The skill loaded, but after the agent already started editing — the
    # load-before-mutation invariant is violated.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("econ-data-analysis", 0), ("academic-writing", 4)],
        edit_event_indices=[2],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "academic-writing"],
    )

    assert not report.ok


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
        skill_tool_events=[("academic-writing", 6)],
        edit_event_indices=[1],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["econ-data-analysis", "academic-writing"],
    )

    assert not report.ok


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


# --------------------------------------------------------------------------- #
# Always-loaded load-instruction contract (static)
# --------------------------------------------------------------------------- #


def test_parse_section_stops_at_next_same_level_heading():
    text = (
        "# Title\n\n"
        "## Before You Start\n\n"
        "1. Load `superRA:using-superra`.\n\n"
        "### Nested\n\n"
        "still inside\n\n"
        "## Execution Protocol\n\n"
        "outside\n"
    )
    section = parse_section(text, "## Before You Start")
    assert "superRA:using-superra" in section
    assert "still inside" in section
    assert "outside" not in section


def test_parse_section_missing_heading():
    assert parse_section("no headings here", "## Before You Start") == ""


def _write_role_skill(root, rel, skills):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    listed = "".join(f"`{skill}` " for skill in skills)
    path.write_text(
        f"---\nname: x\n---\n\n{LOAD_INSTRUCTION_HEADING}\n\n1. Load {listed}.\n",
        encoding="utf-8",
    )


def test_green_always_loaded_load_instruction_real_role_skills():
    # Both real role skills must instruct loading every always-loaded skill —
    # this is what replaces the retired agent-frontmatter autoload.
    report = SkillLoadReport()
    check_always_loaded_load_instruction(report, REPO_ROOT)
    report.assert_ok()


def test_red_always_loaded_load_instruction_missing_skill(tmp_path):
    # A role skill whose load instruction drops an always-loaded skill regressed
    # the contract.
    _write_role_skill(tmp_path, ROLE_SKILL_FILES[0], ["superRA:econ-data-analysis"])
    _write_role_skill(tmp_path, ROLE_SKILL_FILES[1], ALWAYS_LOADED_SKILLS)
    report = SkillLoadReport()
    check_always_loaded_load_instruction(report, tmp_path)

    assert not report.ok


def test_red_always_loaded_load_instruction_missing_file(tmp_path):
    report = SkillLoadReport()
    check_always_loaded_load_instruction(report, tmp_path)
    assert not report.ok


def test_always_loaded_skills_constant_is_qualified():
    # The contract checks the plugin-qualified names the load instruction names.
    assert ALWAYS_LOADED_SKILLS == (
        "superRA:using-superra",
        "superRA:communicate",
    )


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
