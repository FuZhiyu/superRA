#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from transcript_assertions import (  # noqa: E402
    AssertionReport,
    check_event_before_write,
    check_file_reads_before_write,
    check_json_artifact,
    check_orchestrator_dispatches,
    check_task_reads_before_write,
    parse_claude_stream_json,
    parse_codex_jsonl,
    parse_json_events,
)


FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "task-trees"
    / "bundle-two-tasks"
)
SAMPLES = SCRIPT_DIR / "samples"


def test_claude_sample_task_reads_and_marker_reads_before_write():
    events = parse_claude_stream_json(SAMPLES / "claude-stream.bundle.jsonl")
    report = AssertionReport()

    check_task_reads_before_write(
        report,
        events,
        [
            "agent-loading-bundle/02-primary-loading-task",
            "agent-loading-bundle/03-secondary-loading-task",
        ],
    )
    check_file_reads_before_write(
        report,
        events,
        [
            "markers/primary-marker.txt",
            "markers/secondary-marker.txt",
            "markers/shared-marker.json",
        ],
    )

    report.assert_ok()


def test_codex_sample_orchestrator_dispatch_events():
    events = parse_codex_jsonl(SAMPLES / "codex-jsonl.orchestrator.jsonl")
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    report.assert_ok()
    assert report.observations == ["orchestrator dispatch events observed"]


def test_claude_agent_dispatch_events_are_structural():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "tool_use",
                "name": "Agent",
                "input": {"subagent_type": "superRA:implementer"},
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Agent",
                "input": {"subagent_type": "superRA:reviewer"},
            }),
        ])
    )
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    report.assert_ok()
    assert report.observations == ["orchestrator dispatch events observed"]


def test_orchestrator_fallback_is_skip_not_failure():
    events = parse_json_events(
        json.dumps({
            "type": "assistant",
            "message": (
                "Switching to direct mode: the harness lacks subagent "
                "events, so I will play the reviewer role in-session."
            ),
        })
    )
    report = AssertionReport()

    check_orchestrator_dispatches(
        report,
        events,
        fallback_exception_needles=["lacks subagent", "trivial"],
        fallback_required_needles=["direct mode", "reviewer"],
    )

    report.assert_ok()
    assert report.skipped


def test_orchestrator_fallback_rejects_fabricated_reason():
    # Names "direct mode" and "reviewer" but no documented exception — the
    # exact masking the Objective forbids. Must fail, not skip-pass.
    events = parse_json_events(
        json.dumps({
            "type": "assistant",
            "message": (
                "I feel like using direct mode today, and I will pretend "
                "to be a reviewer too."
            ),
        })
    )
    report = AssertionReport()

    check_orchestrator_dispatches(
        report,
        events,
        fallback_exception_needles=[
            "lacks subagent", "user override", "trivial",
        ],
        fallback_required_needles=["direct mode", "reviewer"],
    )

    assert not report.skipped
    assert len(report.missing) == 2
    assert "missing implementer event" in report.missing[0]
    assert "missing reviewer event" in report.missing[1]


def test_task_read_narration_without_command_event_fails():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "assistant",
                "message": (
                    "I will run superra task read "
                    "agent-loading-bundle/02-primary-loading-task."
                ),
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Write",
                "input": {"file_path": "loading-evidence.json"},
            }),
        ])
    )
    report = AssertionReport()

    check_task_reads_before_write(
        report,
        events,
        ["agent-loading-bundle/02-primary-loading-task"],
    )

    assert len(report.missing) == 1
    assert "command event invoking superra task read" in report.missing[0]


def test_required_reads_must_precede_any_write_by_default():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "tool_use",
                "name": "Write",
                "input": {"file_path": "notes.md"},
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Bash",
                "input": {
                    "command": (
                        "./superRA/superra task read "
                        "agent-loading-bundle/02-primary-loading-task"
                    )
                },
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Read",
                "input": {"file_path": "markers/primary-marker.txt"},
            }),
        ])
    )
    report = AssertionReport()

    check_task_reads_before_write(
        report,
        events,
        ["agent-loading-bundle/02-primary-loading-task"],
    )
    check_file_reads_before_write(
        report,
        events,
        ["markers/primary-marker.txt"],
    )

    assert len(report.missing) == 2
    assert "02-primary-loading-task" in report.missing[0]
    assert "markers/primary-marker.txt" in report.missing[1]


def test_orchestrator_dispatch_narration_without_tool_event_fails():
    events = parse_json_events(
        json.dumps({
            "type": "assistant",
            "message": (
                "I should dispatch superra_implementer and "
                "superra_reviewer subagents."
            ),
        })
    )
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    assert len(report.missing) == 2
    assert "missing implementer event" in report.missing[0]
    assert "missing reviewer event" in report.missing[1]


def test_missing_requirements_are_collected_together():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "tool_use",
                "name": "Write",
                "input": {"file_path": "loading-evidence.json"},
            }),
        ])
    )
    report = AssertionReport()

    check_task_reads_before_write(
        report,
        events,
        [
            "agent-loading-bundle/02-primary-loading-task",
            "agent-loading-bundle/03-secondary-loading-task",
        ],
    )
    check_event_before_write(
        report,
        events,
        "marker read",
        ["markers/primary-marker.txt"],
        write_path="loading-evidence.json",
    )

    assert len(report.missing) == 3
    assert "02-primary-loading-task" in report.missing[0]
    assert "03-secondary-loading-task" in report.missing[1]
    assert "marker read" in report.missing[2]


def test_json_artifact_reports_all_scalar_mismatches(tmp_path):
    expected = FIXTURE_ROOT / "expected" / "loading-evidence.expected.json"
    actual = tmp_path / "loading-evidence.json"
    data = json.loads(expected.read_text(encoding="utf-8"))
    data["dependency_metadata"]["status"] = "not-started"
    del data["marker_files"]["shared"]
    actual.write_text(json.dumps(data), encoding="utf-8")
    report = AssertionReport()

    check_json_artifact(report, actual, expected)

    assert len(report.missing) == 2
    assert "$.dependency_metadata.status" in report.missing[0]
    assert "$.marker_files.shared" in report.missing[1]
