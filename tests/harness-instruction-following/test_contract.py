#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "bundle-two-tasks"
PLAN_ROOT = FIXTURE_ROOT / "superRA"
SAMPLES = SCRIPT_DIR / "samples"

sys.path.insert(0, str(SCRIPT_DIR))

from transcript_assertions import (  # noqa: E402
    AssertionReport,
    check_file_reads_before_write,
    check_orchestrator_dispatches,
    check_task_reads_before_write,
    parse_claude_stream_json,
    parse_codex_jsonl,
    parse_json_events,
)


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str) -> dict:
    return json.loads(read_text(relative_path))


def markdown_table_rows(text: str, heading: str) -> list[list[str]]:
    """Return data cells from the first Markdown table under *heading*."""
    section = text.split(heading, 1)[1]
    next_heading = re.search(r"\n#{1,3} ", section)
    if next_heading:
        section = section[: next_heading.start()]

    rows = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:]


def inline_code(cell: str) -> tuple[str, ...]:
    return tuple(re.findall(r"`([^`]+)`", cell))


def all_hook_commands(manifest: dict) -> list[str]:
    return [
        hook["command"]
        for groups in manifest["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]


def hook_commands_for(manifest: dict, event: str) -> list[str]:
    return [
        hook["command"]
        for group in manifest["hooks"].get(event, [])
        for hook in group["hooks"]
    ]


def hook_matchers_for(manifest: dict, event: str) -> set[str]:
    return {
        group.get("matcher", "")
        for group in manifest["hooks"].get(event, [])
    }


def run_task_read(path: str, *, as_json: bool = False) -> str:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "skills" / "task-tree" / "scripts" / "task_read.py"),
        "--plan-root",
        str(PLAN_ROOT),
        "--path",
        path,
    ]
    if as_json:
        cmd.append("--json")
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_load_contract_indexes_every_ci_safe_contract_area():
    contract = read_json("tests/harness-instruction-following/load_contract.json")
    by_area = {entry["area"]: entry for entry in contract["entries"]}

    expected = {
        "manifest-always-loaded": "ci_safe_static",
        "manifest-stage-loads": "ci_safe_static",
        "manifest-domain-loads": "ci_safe_static",
        "harness-adapter-routing": "ci_safe_static",
        "role-task-read-contract": "ci_safe_fixture",
        "generated-agent-drift": "ci_safe_static",
        "task-read-ancestor-context": "ci_safe_fixture",
        "task-read-comments": "ci_safe_fixture",
        "task-read-dependency-status": "ci_safe_fixture",
        "dependency-results-non-inheritance": "ci_safe_fixture",
        "hook-registries": "ci_safe_static",
        "workflow-superimplement-orchestration": "ci_safe_fixture",
        "agent-orchestration-dispatch-templates": "ci_safe_fixture",
        "codex-orchestration-adapter": "ci_safe_static",
    }
    for area, classification in expected.items():
        assert area in by_area
        assert classification in by_area[area]["classification"]


def test_every_load_contract_entry_carries_covered_by():
    """Each LC entry names the test(s)/scripts that exercise it.

    Keeps the audit and the suite in sync: a new contract entry without a
    ``covered_by`` block, or a block missing a layer it claims to satisfy via
    ``classification``, fails here rather than drifting silently from the README
    matrix.
    """
    contract = read_json("tests/harness-instruction-following/load_contract.json")
    # Each classification token maps to one or more required covered_by groups.
    # A group is a set of acceptable layer keys (any one populated satisfies it):
    # the fixture token accepts either the ``ci_safe_fixture`` or ``fixture_unit``
    # key. ``manual_live_both`` requires both single-harness layers, so it lists
    # two groups.
    classification_to_groups = {
        "ci_safe_static": [("ci_safe_static",)],
        "ci_safe_fixture": [("ci_safe_fixture", "fixture_unit")],
        "manual_live_claude": [("manual_live_claude",)],
        "manual_live_codex": [("manual_live_codex",)],
        "manual_live_both": [("manual_live_claude",), ("manual_live_codex",)],
    }
    for entry in contract["entries"]:
        lc_id = entry["id"]
        covered = entry.get("covered_by")
        assert isinstance(covered, dict) and covered, (
            f"{lc_id} has no covered_by block"
        )
        for token in entry["classification"]:
            for group in classification_to_groups[token]:
                assert any(covered.get(layer) for layer in group), (
                    f"{lc_id} classification {token!r} requires a populated "
                    f"covered_by entry among {group}"
                )


def test_skill_load_manifest_tables_match_contract():
    manifest = read_text("skills/using-superra/SKILL.md")
    stage_rows = markdown_table_rows(manifest, "### Stage")
    stage_loads = {
        inline_code(row[0])[0]: inline_code(row[2])
        for row in stage_rows
    }
    assert stage_loads == {
        "planning-review": ("skills/superplan/references/planning-review.md",),
        "implementation": (),
        "protection": ("result-protection",),
        "sync": ("semantic-merge",),
        "integration": ("refactor-and-integrate",),
        "maturation": ("task-tree", "superplan", "writing"),
    }

    domain_rows = markdown_table_rows(manifest, "### Domain")
    assert {inline_code(row[0])[0] for row in domain_rows} == {
        "econ-data-analysis",
        "theory-modeling",
        "writing",
        "slide-design",
    }


def test_codex_tool_map_matches_contract():
    codex = read_text("skills/using-superra/references/codex-instructions.md")
    rows = markdown_table_rows(codex, "## Codex Tool Map")
    mappings = {
        inline_code(row[0])[0]: inline_code(row[1])
        for row in rows
        if inline_code(row[0])
    }

    assert mappings["AskUserQuestion"] == ("request_user_input",)
    assert mappings["TodoWrite"] == ("update_plan",)
    assert mappings['Agent(subagent_type: "superRA:implementer")'] == (
        'spawn_agent(agent_type="superra_implementer")',
    )
    assert mappings['Agent(subagent_type: "superRA:reviewer")'] == (
        'spawn_agent(agent_type="superra_reviewer")',
    )
    assert mappings["SendMessage"] == ("send_input",)


def test_codex_generated_agent_drift_check_is_ci_safe():
    subprocess.run(
        [
            sys.executable,
            str(
                REPO_ROOT
                / "skills"
                / "codex-superra-setup"
                / "scripts"
                / "sync_codex_agents.py"
            ),
            "--scope",
            "project",
            "--check",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_hook_registry_boundaries_for_claude_and_codex():
    claude = read_json("hooks/hooks.json")
    codex = read_json("hooks/hooks-codex.json")

    assert set(claude["hooks"]) == {"UserPromptSubmit", "PreToolUse", "PostToolUse"}
    assert set(codex["hooks"]) == {
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "Stop",
    }

    claude_commands = all_hook_commands(claude)
    assert any("autoload-superra" in command for command in claude_commands)
    assert any("ensure-using-superra" in command for command in claude_commands)
    assert any("ensure-agent-orchestration" in command for command in claude_commands)
    assert any("merge-guard" in command for command in claude_commands)
    assert any("task-hook" in command for command in claude_commands)
    assert "Skill" in hook_matchers_for(claude, "PreToolUse")
    assert {"Edit|Write", "Bash", "ExitPlanMode"} <= hook_matchers_for(
        claude,
        "PostToolUse",
    )

    codex_commands = all_hook_commands(codex)
    assert any("autoload-superra" in command for command in codex_commands)
    assert any("merge-guard" in command for command in codex_commands)
    assert any("task-hook" in command for command in codex_commands)
    assert any("codex-plan-stop" in command for command in codex_commands)
    assert not any("ensure-using-superra" in command for command in codex_commands)
    assert not any("ensure-agent-orchestration" in command for command in codex_commands)
    assert "Skill" not in hook_matchers_for(codex, "PreToolUse")
    assert {"Edit|Write", "Bash"} <= hook_matchers_for(codex, "PostToolUse")
    assert hook_commands_for(codex, "Stop")


def test_task_read_fixture_contract_surfaces_context_without_dependency_results():
    output = run_task_read("agent-loading-bundle/02-primary-loading-task")

    assert "ROOT_CONTEXT_SENTINEL_ALPINE" in output
    assert "PARENT_CONTEXT_SENTINEL_RIVER" in output
    assert "PRIMARY_TARGET_SENTINEL_COBALT" in output
    assert "COMMENT_SENTINEL_AMBER" in output
    assert "01-approved-dependency (approved)" in output
    assert "DEPENDENCY_TITLE_SENTINEL_BRASS" in output
    assert "DEPENDENCY_RESULTS_EXCLUSION_SENTINEL_NEVER_INHERIT" not in output

    data = json.loads(
        run_task_read("agent-loading-bundle/02-primary-loading-task", as_json=True)
    )
    assert data["open_comments"][0]["body"] == "COMMENT_SENTINEL_AMBER"
    assert data["dependencies"][0]["effective_status"] == "approved"
    assert data["dependencies"][0]["title"].endswith(
        "DEPENDENCY_TITLE_SENTINEL_BRASS"
    )


def test_parser_contract_samples_and_negative_ordering_cases():
    sample_events = parse_claude_stream_json(SAMPLES / "claude-stream.bundle.jsonl")
    report = AssertionReport()
    check_task_reads_before_write(
        report,
        sample_events,
        [
            "agent-loading-bundle/02-primary-loading-task",
            "agent-loading-bundle/03-secondary-loading-task",
        ],
    )
    check_file_reads_before_write(
        report,
        sample_events,
        [
            "markers/primary-marker.txt",
            "markers/secondary-marker.txt",
            "markers/shared-marker.json",
        ],
    )
    report.assert_ok()

    late_events = parse_json_events(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": "loading-evidence.json"},
                    }
                ),
                json.dumps(
                    {
                        "type": "tool_use",
                        "name": "Bash",
                        "input": {
                            "command": (
                                "./superRA/superra task read "
                                "agent-loading-bundle/02-primary-loading-task"
                            )
                        },
                    }
                ),
            ]
        )
    )
    late_report = AssertionReport()
    check_task_reads_before_write(
        late_report,
        late_events,
        ["agent-loading-bundle/02-primary-loading-task"],
    )
    assert len(late_report.missing) == 1

    missing_events = parse_json_events(
        json.dumps(
            {
                "type": "assistant",
                "message": "I read both tasks and will write the JSON.",
            }
        )
    )
    missing_report = AssertionReport()
    check_task_reads_before_write(
        missing_report,
        missing_events,
        [
            "agent-loading-bundle/02-primary-loading-task",
            "agent-loading-bundle/03-secondary-loading-task",
        ],
    )
    assert len(missing_report.missing) == 2


def test_codex_orchestrator_sample_has_structural_dispatches():
    events = parse_codex_jsonl(SAMPLES / "codex-jsonl.orchestrator.jsonl")
    report = AssertionReport()

    check_orchestrator_dispatches(report, events)

    report.assert_ok()
    assert report.observations == ["orchestrator dispatch events observed"]


def test_live_fixture_stays_cheap_and_mock_only():
    fixture_text = "\n".join(
        [
            read_text(
                "tests/fixtures/task-trees/bundle-two-tasks/"
                "superRA/agent-loading-bundle/task.md"
            ),
            read_text(
                "tests/fixtures/task-trees/bundle-two-tasks/"
                "superRA/agent-loading-bundle/02-primary-loading-task/task.md"
            ),
            read_text(
                "tests/fixtures/task-trees/bundle-two-tasks/"
                "superRA/agent-loading-bundle/03-secondary-loading-task/task.md"
            ),
        ]
    )
    lower = fixture_text.lower()

    assert "loading-evidence.json" in fixture_text
    assert "marker" in lower
    assert "sentinel" in lower
    for forbidden in (
        "install",
        "package",
        "pytest",
        "npm",
        "cargo",
        "real implementation",
        "broad repository exploration",
    ):
        assert forbidden not in lower
