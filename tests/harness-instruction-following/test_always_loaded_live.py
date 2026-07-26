#!/usr/bin/env python3
"""CI-safe tests for always-loaded skill structural and command evidence."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from always_loaded_live import (  # noqa: E402
    CODEX_ALWAYS_LOADED_CANARIES,
    CODEX_REPORT_IN_MARKDOWN_CANARY,
    CODEX_USING_SUPERRA_CANARY,
    EXPECTED_ARTIFACT,
    check_claude_always_loaded_static,
)
from codex_load_evidence import CanaryReport, evaluate_canaries  # noqa: E402
from sdk_load_evidence import SkillLoadReport  # noqa: E402


def test_default_ci_path_never_imports_sdk_or_codex():
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("always_loaded_live") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


def test_green_codex_both_canaries_from_commands():
    report = CanaryReport()
    evaluate_canaries(
        report,
        CODEX_ALWAYS_LOADED_CANARIES,
        command_strings=[
            "python3 skills/report-in-markdown/scripts/check_markdown.py task.md",
            "./superRA/superra task read always-loaded-task",
        ],
    )
    report.assert_ok()


def test_red_codex_report_in_markdown_canary_absent():
    report = CanaryReport()
    evaluate_canaries(
        report,
        [CODEX_REPORT_IN_MARKDOWN_CANARY],
        command_strings=["ls -la", "cat task.md"],
    )
    assert not report.ok


def test_red_codex_using_superra_canary_absent():
    report = CanaryReport()
    evaluate_canaries(
        report,
        [CODEX_USING_SUPERRA_CANARY],
        command_strings=["cat README.md"],
    )
    assert not report.ok


def test_red_codex_both_canaries_absent_collected_together():
    report = CanaryReport()
    evaluate_canaries(report, CODEX_ALWAYS_LOADED_CANARIES, command_strings=[])
    assert not report.ok


def test_green_static_backbone_real_role_specs():
    report = SkillLoadReport()
    check_claude_always_loaded_static(report, REPO_ROOT)
    report.assert_ok()


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


def test_codex_fixture_expected_artifact_schema():
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
    assert expected == EXPECTED_ARTIFACT
