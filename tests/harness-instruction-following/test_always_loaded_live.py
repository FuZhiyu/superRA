#!/usr/bin/env python3
"""CI-safe unit tests for the always-loaded skill live coverage (task 10).

Drives the two always-loaded canary layers on synthetic inputs — no model call,
no ``claude_agent_sdk`` / codex-cli import:

- **Claude introspection canary** (:func:`always_loaded_live.evaluate_introspection_canary`):
  green when the dispatched agent's answer recites report-in-markdown's
  discriminating rule (links *with line anchors*, *not* backtick paths) with zero
  on-demand ``Skill`` loads of the always-loaded skill; red on a NO_RULE answer, a
  backtick-path answer, and the autoload-violation case (the skill was loaded on
  demand, so the answer does not establish the always-loaded contract).
- **Codex canaries** (09's :func:`codex_load_evidence.evaluate_canary`): green when
  each always-loaded skill's skill-unique token appears in a command or the output
  artifact; red when absent (skill body did not load).
- The deterministic backbone (08's static frontmatter contract) reused via
  :func:`always_loaded_live.check_claude_always_loaded_static`: green against the
  real role specs, red against a synthetic spec missing a skill.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from always_loaded_live import (  # noqa: E402
    CODEX_ALWAYS_LOADED_CANARIES,
    CODEX_REPORT_IN_MARKDOWN_CANARY,
    CODEX_USING_SUPERRA_CANARY,
    INTROSPECTION_AUTOLOAD_SKILL,
    INTROSPECTION_CANARY,
    IntrospectionCanaryReport,
    check_claude_always_loaded_static,
    evaluate_introspection_canary,
)
from codex_load_evidence import CanaryReport, evaluate_canaries  # noqa: E402
from sdk_load_evidence import (  # noqa: E402
    SkillLoadReport,
    evidence_from_hook_records,
)


def test_default_ci_path_never_imports_sdk_or_codex():
    # The task-10 evaluators must drive without the live deps on the CI path.
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("always_loaded_live") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


# --------------------------------------------------------------------------- #
# Claude introspection canary (discriminating)
# --------------------------------------------------------------------------- #


def _no_loads():
    # Zero Skill-tool loads -> the autoload signal (what Claude actually produces
    # for an always-loaded skill).
    return evidence_from_hook_records(skill_tool_events=[], edit_event_indices=[])


def test_green_introspection_rule_recited_with_zero_loads():
    answer = (
        "I cite source files as markdown links with line anchors, like "
        "[file.py:42](file.py#L42), and never as backtick-wrapped paths."
    )
    report = IntrospectionCanaryReport()
    evaluate_introspection_canary(report, answer, _no_loads())
    report.assert_ok()
    assert len(report.observations) == 1


def test_red_introspection_no_rule_answer():
    # The agent has no such rule in context -> the always-loaded skill is missing.
    report = IntrospectionCanaryReport()
    evaluate_introspection_canary(report, "NO_RULE", _no_loads())
    assert not report.ok
    assert any("did not shape the answer" in m for m in report.missing)


def test_red_introspection_backtick_default_answer():
    # A bare model-default answer (backtick path, no anchor/contrast) must NOT
    # pass — that is exactly the non-discriminating case the canary rejects.
    answer = "I usually write the file path in backticks, like `file.py`, line 42."
    report = IntrospectionCanaryReport()
    evaluate_introspection_canary(report, answer, _no_loads())
    assert not report.ok
    assert any(INTROSPECTION_CANARY.skill in m for m in report.missing)


def test_red_introspection_anchor_without_backtick_contrast_is_not_enough():
    # Mentions anchors but not the discriminating "not backticks" contrast: too
    # close to a model default to count, so it must fail.
    answer = "I cite files as markdown links with line anchors."
    report = IntrospectionCanaryReport()
    evaluate_introspection_canary(report, answer, _no_loads())
    assert not report.ok


def test_red_introspection_rule_recited_but_skill_loaded_on_demand():
    # The rule is recited, but the always-loaded skill was loaded on demand via
    # the Skill tool -> the answer does not establish the *autoload* contract.
    answer = (
        "Cite files as markdown links with line anchors, not backtick-wrapped "
        "paths."
    )
    evidence = evidence_from_hook_records(
        skill_tool_events=[(INTROSPECTION_AUTOLOAD_SKILL, 0)],
        edit_event_indices=[],
    )
    report = IntrospectionCanaryReport()
    evaluate_introspection_canary(report, answer, evidence)
    assert not report.ok
    assert any("loaded on demand" in m for m in report.missing)


def test_introspection_collects_both_failures_together():
    # Wrong answer AND an on-demand load -> both failures reported at once.
    evidence = evidence_from_hook_records(
        skill_tool_events=[(INTROSPECTION_AUTOLOAD_SKILL, 0)],
        edit_event_indices=[],
    )
    report = IntrospectionCanaryReport()
    evaluate_introspection_canary(report, "NO_RULE", evidence)
    assert len(report.missing) == 2


# --------------------------------------------------------------------------- #
# Codex always-loaded canaries (role-spec body-load path)
# --------------------------------------------------------------------------- #


def test_green_codex_both_canaries_from_command_and_artifact():
    report = CanaryReport()
    evaluate_canaries(
        report,
        CODEX_ALWAYS_LOADED_CANARIES,
        command_strings=[
            "python3 skills/report-in-markdown/scripts/check_markdown.py task.md",
            "./superRA/superra task read always-loaded-task",
        ],
        artifact={
            "report_in_markdown_canary": "check_markdown.py",
            "using_superra_canary": "superra task read",
        },
    )
    report.assert_ok()
    # two skills, each satisfied
    assert len(report.observations) == 2


def test_green_codex_canaries_from_artifact_only():
    # Even with no recorded commands, the artifact fields carry both tokens.
    report = CanaryReport()
    evaluate_canaries(
        report,
        CODEX_ALWAYS_LOADED_CANARIES,
        command_strings=[],
        artifact={
            "report_in_markdown_canary": "check_markdown.py",
            "using_superra_canary": "superra task read",
        },
    )
    report.assert_ok()


def test_red_codex_report_in_markdown_canary_absent():
    # report-in-markdown body never loaded: neither the self-diagnose command nor
    # the artifact token is present.
    report = CanaryReport()
    evaluate_canaries(
        report,
        [CODEX_REPORT_IN_MARKDOWN_CANARY],
        command_strings=["ls -la", "cat task.md"],
        artifact={"report_in_markdown_canary": "WRONG"},
    )
    assert not report.ok
    assert "superRA:report-in-markdown" in report.missing[0]
    assert "did not load" in report.missing[0]


def test_red_codex_using_superra_canary_absent():
    report = CanaryReport()
    evaluate_canaries(
        report,
        [CODEX_USING_SUPERRA_CANARY],
        command_strings=["cat README.md"],
        artifact={"using_superra_canary": "read the file"},
    )
    assert not report.ok
    assert "superRA:using-superra" in report.missing[0]


def test_red_codex_both_canaries_absent_collected_together():
    report = CanaryReport()
    evaluate_canaries(report, CODEX_ALWAYS_LOADED_CANARIES, command_strings=[])
    assert len(report.missing) == 2


# --------------------------------------------------------------------------- #
# Deterministic backbone: static frontmatter contract (08, reused)
# --------------------------------------------------------------------------- #


def test_green_static_backbone_real_role_specs():
    report = SkillLoadReport()
    check_claude_always_loaded_static(report, REPO_ROOT)
    report.assert_ok()
    # two specs x two skills
    assert len(report.observations) == 4


def test_red_static_backbone_missing_skill(tmp_path):
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
    check_claude_always_loaded_static(report, tmp_path)
    assert not report.ok
    assert "superRA:report-in-markdown" in report.missing[0]


# --------------------------------------------------------------------------- #
# Fixture sanity: the committed expected artifact matches the canary tokens
# --------------------------------------------------------------------------- #


def test_codex_fixture_expected_artifact_satisfies_canaries():
    import json

    expected = json.loads(
        (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "task-trees"
            / "always-loaded-canary"
            / "expected"
            / "always-loaded-evidence.expected.json"
        ).read_text(encoding="utf-8")
    )
    report = CanaryReport()
    evaluate_canaries(
        report,
        CODEX_ALWAYS_LOADED_CANARIES,
        command_strings=[],
        artifact=expected,
    )
    report.assert_ok()
