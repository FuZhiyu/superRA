#!/usr/bin/env python3
"""CI-safe tests for always-loaded structural and command evidence."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from always_loaded_live import (  # noqa: E402
    CODEX_ALWAYS_LOADED_COMMANDS,
    AlwaysLoadedBehaviorReport,
    always_loaded_artifact_matches,
    check_claude_always_loaded_static,
    evaluate_always_loaded_behavior,
    expected_always_loaded_artifact,
)
from codex_load_evidence import (  # noqa: E402
    CommandEvidenceReport,
    command_executions_from_events,
    evaluate_command_specs,
)
from sdk_load_evidence import SkillLoadReport, evidence_from_hook_records  # noqa: E402
from transcript_assertions import parse_json_events  # noqa: E402

FIXTURE_ROOT = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "task-trees"
    / "always-loaded-canary"
)


def test_default_ci_path_never_imports_sdk_or_codex():
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("always_loaded_live") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


def test_expected_artifact_is_schema_and_path_identity_only():
    assert expected_always_loaded_artifact() == {
        "schema": "superra.always-loaded-evidence/v1",
        "task_path": "always-loaded-task",
        "output_path": "always-loaded-evidence.json",
    }


def test_always_loaded_artifact_match_rejects_extra_fields():
    artifact = expected_always_loaded_artifact()
    assert always_loaded_artifact_matches(artifact)
    assert not always_loaded_artifact_matches({**artifact, "instruction": "extra"})


def test_green_claude_role_mutation_with_zero_on_demand_loads():
    evidence = evidence_from_hook_records(edit_event_indices=[3])
    report = AlwaysLoadedBehaviorReport()
    evaluate_always_loaded_behavior(
        report,
        evidence,
        expected_always_loaded_artifact(),
    )
    report.assert_ok()
    assert len(report.observations) == 1


def test_red_claude_missing_role_mutation():
    report = AlwaysLoadedBehaviorReport()
    evaluate_always_loaded_behavior(
        report,
        evidence_from_hook_records(),
        expected_always_loaded_artifact(),
    )
    assert not report.ok


def test_red_claude_wrong_artifact_schema():
    report = AlwaysLoadedBehaviorReport()
    evaluate_always_loaded_behavior(
        report,
        evidence_from_hook_records(edit_event_indices=[1]),
        {"schema": "wrong"},
    )
    assert not report.ok


def test_red_claude_always_loaded_skill_loaded_on_demand():
    report = AlwaysLoadedBehaviorReport()
    evaluate_always_loaded_behavior(
        report,
        evidence_from_hook_records(
            skill_tool_events=[("superRA:report-in-markdown", 0)],
            edit_event_indices=[2],
        ),
        expected_always_loaded_artifact(),
    )
    assert not report.ok


def test_green_codex_actual_commands_observed():
    events = parse_json_events(
        "\n".join(
            json.dumps(item)
            for item in [
                {
                    "type": "command_execution",
                    "command": "./superRA/superra task read always-loaded-task",
                    "exit_code": 0,
                },
                {
                    "type": "command_execution",
                    "command": "python3 /plugin/skills/report-in-markdown/scripts/check_markdown.py "
                    "superRA/always-loaded-task/task.md",
                    "exit_code": 0,
                },
            ]
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(
        report,
        CODEX_ALWAYS_LOADED_COMMANDS,
        command_executions_from_events(events),
    )
    report.assert_ok()
    assert len(report.observations) == 2


def test_red_codex_missing_markdown_command():
    events = parse_json_events(
        json.dumps(
            {
                "type": "command_execution",
                "command": "./superRA/superra task read always-loaded-task",
                "exit_code": 0,
            }
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(
        report,
        CODEX_ALWAYS_LOADED_COMMANDS,
        command_executions_from_events(events),
    )
    assert not report.ok


def test_red_codex_missing_task_read_command():
    events = parse_json_events(
        json.dumps(
            {
                "type": "command_execution",
                "command": "python3 /plugin/skills/report-in-markdown/scripts/check_markdown.py "
                "superRA/always-loaded-task/task.md",
                "exit_code": 0,
            }
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(
        report,
        CODEX_ALWAYS_LOADED_COMMANDS,
        command_executions_from_events(events),
    )
    assert not report.ok


def test_red_codex_command_mentions_do_not_count():
    events = parse_json_events(
        "\n".join(
            json.dumps(item)
            for item in [
                {
                    "type": "command_execution",
                    "command": "printf './superRA/superra task read always-loaded-task'",
                    "exit_code": 0,
                },
                {
                    "type": "command_execution",
                    "command": "rg check_markdown.py tests",
                    "exit_code": 0,
                },
            ]
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(
        report,
        CODEX_ALWAYS_LOADED_COMMANDS,
        command_executions_from_events(events),
    )
    assert not report.ok


def test_red_codex_failed_commands_do_not_count():
    events = parse_json_events(
        "\n".join(
            json.dumps(item)
            for item in [
                {
                    "type": "command_execution",
                    "command": "./superRA/superra task read always-loaded-task",
                    "exit_code": 2,
                },
                {
                    "type": "command_execution",
                    "command": "python3 /plugin/skills/report-in-markdown/scripts/check_markdown.py "
                    "superRA/always-loaded-task/task.md",
                    "exit_code": 1,
                },
            ]
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(
        report,
        CODEX_ALWAYS_LOADED_COMMANDS,
        command_executions_from_events(events),
    )
    assert not report.ok


def test_green_static_backbone_real_role_specs():
    report = SkillLoadReport()
    check_claude_always_loaded_static(report, REPO_ROOT)
    report.assert_ok()
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


def test_committed_expected_artifact_matches_structural_contract():
    expected = json.loads(
        (
            FIXTURE_ROOT
            / "expected"
            / "always-loaded-evidence.expected.json"
        ).read_text(encoding="utf-8")
    )
    assert always_loaded_artifact_matches(expected)
