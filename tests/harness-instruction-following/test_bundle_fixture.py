#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = (
    REPO_ROOT / "tests" / "fixtures" / "task-trees" / "bundle-two-tasks"
)
TASK_READ = REPO_ROOT / "skills" / "task-tree" / "scripts" / "task_read.py"
PLAN_ROOT = FIXTURE_ROOT / "superRA"


def _task_read(path: str, *, as_json: bool = False) -> str:
    cmd = [
        sys.executable,
        str(TASK_READ),
        "--plan-root",
        str(PLAN_ROOT),
        "--path",
        path,
    ]
    if as_json:
        cmd.append("--json")
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_primary_task_read_surfaces_context_comments_and_dependency_metadata():
    output = _task_read("agent-loading-bundle/02-primary-loading-task")

    assert "ROOT_CONTEXT_SENTINEL_ALPINE" in output
    assert "PARENT_CONTEXT_SENTINEL_RIVER" in output
    assert "PRIMARY_TARGET_SENTINEL_COBALT" in output
    assert "COMMENT_SENTINEL_AMBER" in output
    assert "01-approved-dependency (approved)" in output
    assert "DEPENDENCY_TITLE_SENTINEL_BRASS" in output
    assert "DEPENDENCY_RESULTS_EXCLUSION_SENTINEL_NEVER_INHERIT" not in output


def test_secondary_task_read_gives_second_target_and_same_dependency_metadata():
    output = _task_read("agent-loading-bundle/03-secondary-loading-task")

    assert "ROOT_CONTEXT_SENTINEL_ALPINE" in output
    assert "PARENT_CONTEXT_SENTINEL_RIVER" in output
    assert "SECONDARY_TARGET_SENTINEL_LILAC" in output
    assert "01-approved-dependency (approved)" in output
    assert "DEPENDENCY_TITLE_SENTINEL_BRASS" in output


def test_task_read_json_carries_comments_and_dependency_status():
    data = json.loads(_task_read(
        "agent-loading-bundle/02-primary-loading-task",
        as_json=True,
    ))

    assert [ancestor["title"] for ancestor in data["ancestors"]] == [
        "Harness Loading Fixture Root",
        "Agent Loading Bundle",
    ]
    assert data["task"]["path"] == "agent-loading-bundle/02-primary-loading-task"
    assert data["open_comments"][0]["body"] == "COMMENT_SENTINEL_AMBER"
    assert data["dependencies"] == [
        {
            "path": "agent-loading-bundle/01-approved-dependency",
            "slug": "01-approved-dependency",
            "title": "Approved Dependency DEPENDENCY_TITLE_SENTINEL_BRASS",
            "status": "approved",
            "effective_status": "approved",
        }
    ]


def test_expected_artifact_contains_all_fixture_sentinel_groups():
    expected = json.loads(
        (FIXTURE_ROOT / "expected" / "loading-evidence.expected.json")
        .read_text(encoding="utf-8")
    )

    assert expected["task_read_context"] == {
        "root": "ROOT_CONTEXT_SENTINEL_ALPINE",
        "parent": "PARENT_CONTEXT_SENTINEL_RIVER",
        "primary_target": "PRIMARY_TARGET_SENTINEL_COBALT",
        "secondary_target": "SECONDARY_TARGET_SENTINEL_LILAC",
        "open_comment": "COMMENT_SENTINEL_AMBER",
    }
    assert expected["dependency_results_excluded"] is True
    assert expected["marker_files"] == {
        "primary": "PRIMARY_MARKER_SENTINEL_OBSIDIAN",
        "secondary": "SECONDARY_MARKER_SENTINEL_TOPAZ",
        "shared": "SHARED_MARKER_SENTINEL_JADE",
    }
