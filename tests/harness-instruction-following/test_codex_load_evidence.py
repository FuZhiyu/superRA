#!/usr/bin/env python3
"""CI-safe unit tests for the Codex skill-load + dispatch evidence layer.

Drives :mod:`codex_load_evidence` and the :mod:`subagent_start_hook` handler on
synthetic inputs — no codex-cli, no model call. Covers the green case plus the
red cases the parent objective names: canary absent (skill body did not load);
and a dispatch log with no implementer/reviewer sentinel.
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
    CanaryReport,
    CanarySpec,
    DispatchReport,
    append_subagent_start,
    command_strings_from_events,
    dispatched_agent_types,
    evaluate_canaries,
    evaluate_canary,
    evaluate_dispatch_log,
    handle_subagent_start_payload,
    load_artifact,
)


def test_default_ci_path_never_imports_codex_cli():
    # The evidence layer must not pull in any codex-cli package on the default
    # pytest path. There is no canonical importable codex-cli module name, so we
    # assert the module imports cleanly and is itself the only thing required.
    assert importlib.util.find_spec("codex_load_evidence") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


# --------------------------------------------------------------------------- #
# Canary evaluator
# --------------------------------------------------------------------------- #


def test_green_canary_present_in_command():
    spec = CanarySpec(skill="communicate", token="CANARY_VERDANT_7Q")
    report = CanaryReport()
    evaluate_canary(
        report,
        spec,
        command_strings=[
            "python3 skills/communicate/scripts/check_markdown.py CANARY_VERDANT_7Q.md",
        ],
    )
    report.assert_ok()


def test_green_canary_command_satisfies():
    spec = CanarySpec(skill="academic-writing", token="CANARY_COBALT_9")
    report = CanaryReport()
    evaluate_canary(
        report,
        spec,
        command_strings=["echo CANARY_COBALT_9"],
    )
    report.assert_ok()


def test_red_canary_absent_from_commands():
    spec = CanarySpec(
        skill="communicate",
        token="CANARY_VERDANT_7Q",
    )
    report = CanaryReport()
    evaluate_canary(
        report,
        spec,
        command_strings=["ls -la", "cat README.md"],
    )
    assert not report.ok


def test_evaluate_canaries_collects_all_failures():
    specs = [
        CanarySpec(skill="a", token="TOKEN_A"),
        CanarySpec(skill="b", token="TOKEN_B"),
    ]
    report = CanaryReport()
    evaluate_canaries(report, specs, command_strings=["echo TOKEN_A"])
    assert not report.ok


def test_command_strings_from_events_pulls_codex_command_execution():
    jsonl = "\n".join(
        json.dumps(obj)
        for obj in [
            {"type": "command_execution", "command": "echo CANARY_TEAL_2"},
            {"type": "agent_message", "text": "done"},
            {"type": "command_execution", "command": "ls"},
        ]
    )
    events = parse_codex_jsonl_str(jsonl)
    commands = command_strings_from_events(events)
    assert "echo CANARY_TEAL_2" in commands
    assert "ls" in commands

    spec = CanarySpec(skill="x", token="CANARY_TEAL_2")
    report = CanaryReport()
    evaluate_canary(report, spec, command_strings=commands)
    report.assert_ok()


# --------------------------------------------------------------------------- #
# SubagentStart payload handler
# --------------------------------------------------------------------------- #


def test_handle_payload_extracts_agent_type():
    assert (
        handle_subagent_start_payload(
            {"hook_event_name": "SubagentStart", "agent_type": "default"}
        )
        == "default"
    )


def test_handle_payload_accepts_alternate_key_spellings():
    assert (
        handle_subagent_start_payload({"subagent_type": "default"})
        == "default"
    )
    assert handle_subagent_start_payload({"name": "default"}) == (
        "default"
    )


def test_handle_payload_disambiguates_by_agent_type_not_session_id():
    # A payload that carries only session_id (no agent type) must NOT produce a
    # session-keyed line — disambiguation is by agent type per the objective.
    assert handle_subagent_start_payload({"session_id": "abc-123"}) is None


def test_append_subagent_start_writes_log(tmp_path):
    log = tmp_path / "nested" / "dispatch.log"
    assert append_subagent_start(log, {"agent_type": "default"}) == (
        "default"
    )
    assert append_subagent_start(log, {"agent_type": "default"}) == (
        "default"
    )
    # No agent type -> nothing appended.
    assert append_subagent_start(log, {"session_id": "x"}) is None
    assert dispatched_agent_types(log.read_text()) == [
        "default",
        "default",
    ]


# --------------------------------------------------------------------------- #
# Dispatch-log evaluator
# --------------------------------------------------------------------------- #


def test_green_dispatch_log_has_both_seats():
    report = DispatchReport()
    evaluate_dispatch_log(report, "default\ndefault\n", minimum_dispatches=2)
    report.assert_ok()


def test_red_dispatch_log_has_only_one_seat():
    report = DispatchReport()
    evaluate_dispatch_log(report, "default\n", minimum_dispatches=2)
    assert not report.ok


def test_red_dispatch_log_empty():
    report = DispatchReport()
    evaluate_dispatch_log(report, "")
    assert not report.ok


# --------------------------------------------------------------------------- #
# Live hook executable (handler only; no codex)
# --------------------------------------------------------------------------- #


def test_subagent_start_hook_executable_appends(tmp_path):
    log = tmp_path / "dispatch.log"
    payload = json.dumps(
        {"hook_event_name": "SubagentStart", "agent_type": "default"}
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
    assert dispatched_agent_types(log.read_text()) == ["default"]


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
