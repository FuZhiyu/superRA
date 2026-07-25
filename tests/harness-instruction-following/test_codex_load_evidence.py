#!/usr/bin/env python3
"""CI-safe unit tests for the Codex skill-load + dispatch evidence layer.

Drives :mod:`codex_load_evidence` and the :mod:`subagent_start_hook` handler on
synthetic inputs — no codex-cli, no model call. Covers structured command
execution evidence and dispatch logs.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from codex_load_evidence import (  # noqa: E402
    CommandEvidenceReport,
    CommandSpec,
    DispatchReport,
    append_subagent_start,
    command_executions_from_events,
    dispatched_agent_types,
    evaluate_command_specs,
    evaluate_dispatch_log,
    handle_subagent_start_payload,
    load_artifact,
)
from structured_findings import finding_codes, findings_for  # noqa: E402


def test_default_ci_path_never_imports_codex_cli():
    # The evidence layer must not pull in any codex-cli package on the default
    # pytest path. There is no canonical importable codex-cli module name, so we
    # assert the module imports cleanly and is itself the only thing required.
    assert importlib.util.find_spec("codex_load_evidence") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


# --------------------------------------------------------------------------- #
# Command-execution evaluator
# --------------------------------------------------------------------------- #


def test_green_command_executable_args_and_success():
    spec = CommandSpec(
        subject="markdown-check",
        executable="python3",
        args=("skills/report-in-markdown/scripts/check_markdown.py", "report.md"),
    )
    events = parse_codex_jsonl_str(
        json.dumps(
            {
                "type": "command_execution",
                "command": "python3 skills/report-in-markdown/scripts/check_markdown.py report.md",
                "exit_code": 0,
            }
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(report, (spec,), command_executions_from_events(events))
    report.assert_ok()
    assert finding_codes(report, outcome="observed") == ["COMMAND_EXECUTED"]


def test_red_printf_mention_is_not_execution():
    spec = CommandSpec(
        subject="task-read",
        executable="./superRA/superra",
        args=("task", "read", "always-loaded-task"),
    )
    events = parse_codex_jsonl_str(
        json.dumps(
            {
                "type": "command_execution",
                "command": "printf './superRA/superra task read always-loaded-task'",
                "exit_code": 0,
            }
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(report, (spec,), command_executions_from_events(events))
    assert finding_codes(report, outcome="missing") == ["COMMAND_NOT_EXECUTED"]


def test_red_search_mention_is_not_execution():
    spec = CommandSpec(
        subject="markdown-check",
        executable="python3",
        args=("skills/report-in-markdown/scripts/check_markdown.py", "report.md"),
    )
    events = parse_codex_jsonl_str(
        json.dumps(
            {
                "type": "command_execution",
                "command": "rg check_markdown.py tests",
                "exit_code": 0,
            }
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(report, (spec,), command_executions_from_events(events))
    assert finding_codes(report, outcome="missing") == ["COMMAND_NOT_EXECUTED"]


def test_red_matching_command_with_nonzero_exit():
    spec = CommandSpec(subject="task-read", executable="tool", args=("read",))
    events = parse_codex_jsonl_str(
        json.dumps(
            {
                "type": "command_execution",
                "command": "tool read",
                "exit_code": 7,
            }
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(report, (spec,), command_executions_from_events(events))
    assert finding_codes(report, outcome="missing") == ["COMMAND_FAILED"]


def test_red_completed_failure_overrides_started_event_without_outcome():
    spec = CommandSpec(subject="task-read", executable="tool", args=("read",))
    events = parse_codex_jsonl_str(
        "\n".join(
            json.dumps(item)
            for item in [
                {
                    "type": "item.started",
                    "item": {"type": "command_execution", "command": "tool read"},
                },
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": "tool read",
                        "exit_code": 3,
                    },
                },
            ]
        )
    )
    report = CommandEvidenceReport()
    evaluate_command_specs(report, (spec,), command_executions_from_events(events))
    assert finding_codes(report, outcome="missing") == ["COMMAND_FAILED"]


def test_command_executions_preserve_command_and_outcome():
    jsonl = "\n".join(
        json.dumps(obj)
        for obj in [
            {"type": "command_execution", "command": "tool one", "exit_code": 0},
            {"type": "agent_message", "text": "done"},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "tool two",
                    "exit_code": 2,
                },
            },
        ]
    )
    events = parse_codex_jsonl_str(jsonl)
    executions = command_executions_from_events(events)
    assert [(item.command, item.exit_code) for item in executions] == [
        ("tool one", 0),
        ("tool two", 2),
    ]


# --------------------------------------------------------------------------- #
# SubagentStart payload handler
# --------------------------------------------------------------------------- #


def test_handle_payload_extracts_agent_type():
    assert (
        handle_subagent_start_payload(
            {"hook_event_name": "SubagentStart", "agent_type": "superra_implementer"}
        )
        == "superra_implementer"
    )


def test_handle_payload_accepts_alternate_key_spellings():
    assert (
        handle_subagent_start_payload({"subagent_type": "superra_reviewer"})
        == "superra_reviewer"
    )
    assert handle_subagent_start_payload({"name": "superra_implementer"}) == (
        "superra_implementer"
    )


def test_handle_payload_disambiguates_by_agent_type_not_session_id():
    # A payload that carries only session_id (no agent type) must NOT produce a
    # session-keyed line — disambiguation is by agent type per the objective.
    assert handle_subagent_start_payload({"session_id": "abc-123"}) is None


def test_append_subagent_start_writes_log(tmp_path):
    log = tmp_path / "nested" / "dispatch.log"
    assert append_subagent_start(log, {"agent_type": "superra_implementer"}) == (
        "superra_implementer"
    )
    assert append_subagent_start(log, {"agent_type": "superra_reviewer"}) == (
        "superra_reviewer"
    )
    # No agent type -> nothing appended.
    assert append_subagent_start(log, {"session_id": "x"}) is None
    assert dispatched_agent_types(log.read_text()) == [
        "superra_implementer",
        "superra_reviewer",
    ]


# --------------------------------------------------------------------------- #
# Dispatch-log evaluator
# --------------------------------------------------------------------------- #


def test_green_dispatch_log_has_both_sentinels():
    report = DispatchReport()
    evaluate_dispatch_log(report, "superra_implementer\nsuperra_reviewer\n")
    report.assert_ok()
    assert finding_codes(report, outcome="observed") == ["DISPATCH_LOGGED"] * 2


def test_red_dispatch_log_missing_reviewer():
    report = DispatchReport()
    evaluate_dispatch_log(report, "superra_implementer\n")
    assert not report.ok
    assert finding_codes(report, outcome="missing") == ["DISPATCH_LOG_MISSING"]
    assert (
        findings_for(report, "DISPATCH_LOG_MISSING")[0].subject
        == "superra_reviewer"
    )


def test_red_dispatch_log_empty():
    report = DispatchReport()
    evaluate_dispatch_log(report, "")
    assert finding_codes(report, outcome="missing") == ["DISPATCH_LOG_MISSING"] * 2


# --------------------------------------------------------------------------- #
# Live hook executable (handler only; no codex)
# --------------------------------------------------------------------------- #


def test_subagent_start_hook_executable_appends(tmp_path):
    log = tmp_path / "dispatch.log"
    payload = json.dumps(
        {"hook_event_name": "SubagentStart", "agent_type": "superra_reviewer"}
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "subagent_start_hook.py")],
        input=payload,
        capture_output=True,
        text=True,
        env={"SUPERRA_SUBAGENT_LOG": str(log), "PATH": ""},
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "{}"
    assert dispatched_agent_types(log.read_text()) == ["superra_reviewer"]


def test_subagent_start_hook_survives_malformed_payload(tmp_path):
    log = tmp_path / "dispatch.log"
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "subagent_start_hook.py")],
        input="not json",
        capture_output=True,
        text=True,
        env={"SUPERRA_SUBAGENT_LOG": str(log), "PATH": ""},
    )
    assert result.returncode == 0
    assert not log.exists()


def test_load_artifact_missing_returns_none(tmp_path):
    assert load_artifact(tmp_path / "absent.json") is None


# --------------------------------------------------------------------------- #
# helper
# --------------------------------------------------------------------------- #


def parse_codex_jsonl_str(text):
    from transcript_assertions import parse_json_events

    return parse_json_events(text)
