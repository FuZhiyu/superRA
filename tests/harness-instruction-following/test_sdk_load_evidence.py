#!/usr/bin/env python3
"""CI-safe unit tests for the Claude Agent-SDK skill-load evidence layer.

Drives :mod:`sdk_load_evidence` on synthetic hook records — no live call, and
``claude_agent_sdk`` is never imported. Covers the green case plus the two red
cases the parent objective names (required skill missing; skill loaded only after
the first edit), and the always-loaded-via-InstructionsLoaded channel.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from sdk_load_evidence import (  # noqa: E402
    SkillLoadReport,
    check_skills_loaded_before_first_edit,
    evidence_from_hook_records,
)


def test_default_ci_path_never_imports_claude_agent_sdk():
    # Importing the evidence layer (and this test) must not pull in the SDK; the
    # live runner that imports it is only touched on the RUN_LIVE_HARNESS path.
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("sdk_load_evidence") is not None


def test_green_required_skills_load_before_first_edit():
    evidence = evidence_from_hook_records(
        skill_tool_events=[
            ("using-superra", 0),
            ("report-in-markdown", 1),
            ("econ-data-analysis", 2),
        ],
        edit_event_indices=[5],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["using-superra", "report-in-markdown", "econ-data-analysis"],
    )

    report.assert_ok()
    assert len(report.observations) == 3


def test_green_always_loaded_skill_via_instructions_loaded_channel():
    # An always-loaded skill can surface via InstructionsLoaded (a SKILL.md load)
    # rather than a Skill tool_use, and must still satisfy the requirement.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("econ-data-analysis", 2)],
        instructions_loaded_events=[
            {
                "file_path": "skills/report-in-markdown/SKILL.md",
                "event_index": 0,
                "memory_type": "skill",
                "load_reason": "always_loaded",
                "skill_name": "report-in-markdown",
            },
        ],
        edit_event_indices=[5],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["report-in-markdown", "econ-data-analysis"],
    )

    report.assert_ok()


def test_red_required_skill_never_loaded():
    # report-in-markdown is claimed always-loaded; if it never appears, that is a
    # real loading-contract finding to escalate — the assertion must fail.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("using-superra", 0)],
        edit_event_indices=[3],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["using-superra", "report-in-markdown"],
    )

    assert not report.ok
    assert len(report.missing) == 1
    assert "report-in-markdown" in report.missing[0]
    assert "never loaded" in report.missing[0]


def test_red_skill_loaded_only_after_first_edit():
    # The skill loaded, but after the agent already started editing — the
    # load-before-mutation invariant is violated.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("using-superra", 0), ("econ-data-analysis", 4)],
        edit_event_indices=[2],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(
        report,
        evidence,
        ["using-superra", "econ-data-analysis"],
    )

    assert not report.ok
    assert len(report.missing) == 1
    assert "econ-data-analysis" in report.missing[0]
    assert "before the first edit" in report.missing[0]


def test_no_edit_session_counts_any_load_as_before_edit():
    # A session that never edits has no boundary, so any load passes the ordering
    # check (the read-only / pure-read fixture path).
    evidence = evidence_from_hook_records(
        skill_tool_events=[("using-superra", 0)],
        edit_event_indices=[],
    )
    report = SkillLoadReport()

    check_skills_loaded_before_first_edit(report, evidence, ["using-superra"])

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
        ["using-superra", "writing"],
    )

    assert len(report.missing) == 2
    assert "using-superra" in report.missing[0]
    assert "never loaded" in report.missing[0]
    assert "writing" in report.missing[1]
    assert "before the first edit" in report.missing[1]
