#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from transcript_assertions import (  # noqa: E402
    AssertionReport,
    check_interactive_canvas_order,
    check_main_seat_route,
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


def test_claude_agent_dispatch_events_are_structural():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "tool_use",
                "name": "Agent",
                "input": {
                    "subagent_type": "general-purpose",
                    "prompt": "Load `superRA:implement-task` skill.",
                },
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Agent",
                "input": {
                    "subagent_type": "general-purpose",
                    "prompt": "Load `superRA:review-task` skill.",
                },
            }),
        ])
    )
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    report.assert_ok()


def test_interactive_narration_does_not_excuse_missing_default_dispatch():
    events = parse_json_events(
        json.dumps({
            "type": "assistant",
            "message": (
                "The user requested interactive mode, so I will implement "
                "inline and ask before reviewer dispatch."
            ),
        })
    )
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    assert not report.ok


def test_interactive_canvas_fixture_records_before_question_and_review():
    events = parse_claude_stream_json(SAMPLES / "claude-stream.interactive.jsonl")
    report = AssertionReport()

    check_interactive_canvas_order(
        report,
        events,
        task_path="interactive-fixture/task.md",
        task_artifact=SAMPLES / "interactive-task.after.md",
    )

    report.assert_ok()


def test_interactive_canvas_evaluator_rejects_wrong_event_order():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "tool_use",
                "name": "AskUserQuestion",
                "input": {"options": ["Review now", "Defer", "Skip"]},
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Write",
                "input": {"file_path": "interactive-fixture/task.md"},
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Agent",
                "input": {
                    "subagent_type": "general-purpose",
                    "prompt": "Load `superRA:review-task` skill.",
                },
            }),
        ])
    )
    report = AssertionReport()

    check_interactive_canvas_order(
        report,
        events,
        task_path="interactive-fixture/task.md",
        task_artifact=SAMPLES / "interactive-task.after.md",
    )

    assert not report.ok


def test_interactive_canvas_evaluator_requires_structured_opt_in():
    events = parse_json_events(
        "\n".join([
            json.dumps({
                "type": "tool_use",
                "name": "Write",
                "input": {"file_path": "interactive-fixture/task.md"},
            }),
            json.dumps({
                "type": "tool_use",
                "name": "AskUserQuestion",
                "input": {},
            }),
            json.dumps({
                "type": "tool_use",
                "name": "Agent",
                "input": {
                    "subagent_type": "general-purpose",
                    "prompt": "Load `superRA:review-task` skill.",
                },
            }),
        ])
    )
    report = AssertionReport()

    check_interactive_canvas_order(
        report,
        events,
        task_path="interactive-fixture/task.md",
        task_artifact=SAMPLES / "interactive-task.after.md",
    )

    assert not report.ok


def test_main_reviewer_seat_fixture_loads_role_and_dispatches_implementer():
    events = parse_claude_stream_json(SAMPLES / "claude-stream.main-reviewer-seat.jsonl")
    report = AssertionReport()

    check_main_seat_route(report, events, main_role="reviewer")

    report.assert_ok()


def test_main_implementer_seat_fixture_loads_role_and_dispatches_reviewer():
    events = parse_claude_stream_json(SAMPLES / "claude-stream.main-implementer-seat.jsonl")
    report = AssertionReport()

    check_main_seat_route(report, events, main_role="implementer")

    report.assert_ok()


def test_main_seat_evaluator_detects_missing_role_load_and_opposite_dispatch():
    report = AssertionReport()

    check_main_seat_route(report, [], main_role="reviewer")

    assert not report.ok


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

    assert not report.ok


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

    assert not report.ok


def test_orchestrator_dispatch_narration_without_tool_event_fails():
    events = parse_json_events(
        json.dumps({
            "type": "assistant",
            "message": (
                "I should dispatch implement-task and "
                "review-task subagents."
            ),
        })
    )
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    assert not report.ok


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

    assert not report.ok


def test_parser_skips_non_json_banner_lines():
    # Real `codex exec --json` prints a non-JSON banner before the JSONL stream.
    text = "\n".join([
        "Reading additional input from stdin...",
        json.dumps({"type": "thread.started", "thread_id": "abc"}),
        json.dumps({
            "type": "item.completed",
            "item": {"type": "command_execution",
                     "command": "superra task read a/b"},
        }),
        "",
    ])
    events = parse_json_events(text)
    assert len(events) == 2
    assert any("superra task read a/b" in e.haystack for e in events)


def test_parser_still_raises_on_corrupt_json_event():
    # A line shaped like a JSON object but malformed is a hard error, not noise.
    text = "\n".join([
        "Reading additional input from stdin...",
        json.dumps({"type": "thread.started"}),
        '{"type": "item.completed", "item": {',  # truncated / corrupt
    ])
    try:
        parse_json_events(text)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError on corrupt JSON event line")


def test_task_read_detected_in_wrapped_quoted_command():
    # Real codex runs the wrapper through `zsh -lc '...'`, so the task-read
    # command reaches `superra` via the wrapper path and is terminated by a
    # closing quote rather than whitespace.
    events = parse_json_events("\n".join([
        json.dumps({"type": "thread.started"}),
        json.dumps({
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "/bin/zsh -lc './superRA/superra task read a/b-task'",
            },
        }),
        json.dumps({
            "type": "item.completed",
            "item": {"type": "command_execution",
                     "command": "/bin/zsh -lc \"cat > loading-evidence.json\""},
        }),
    ]))
    report = AssertionReport()
    check_task_reads_before_write(report, events, ["a/b-task"],
                                  write_path="loading-evidence.json")
    report.assert_ok()


def test_json_artifact_reports_all_scalar_mismatches(tmp_path):
    expected = FIXTURE_ROOT / "expected" / "loading-evidence.expected.json"
    actual = tmp_path / "loading-evidence.json"
    data = json.loads(expected.read_text(encoding="utf-8"))
    data["dependency_metadata"]["status"] = "not-started"
    del data["marker_files"]["shared"]
    actual.write_text(json.dumps(data), encoding="utf-8")
    report = AssertionReport()

    check_json_artifact(report, actual, expected)

    assert not report.ok
