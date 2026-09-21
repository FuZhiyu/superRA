#!/usr/bin/env python3
"""CI-safe regression test for the live-trace confinement hook.

A traced session runs with ``permission_mode="acceptEdits"`` and an unrestricted
``Bash``, so before this hook nothing stopped one from resolving another checkout's
task tree and committing into it — the 2026-08-02 escape recorded in
``superRA/task-tree/agent-cwd-isolation``. :func:`sdk_load_harness.confinement_hook`
registers the plugin gate's decision in-process; these checks exercise the callback
directly, with no SDK import and no model call.
"""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from sdk_load_harness import confinement_hook


def _decide(workspace: Path, tool_name: str, tool_input: dict) -> dict:
    hook = confinement_hook(workspace)
    return asyncio.run(
        hook({"tool_name": tool_name, "tool_input": tool_input}, None, {})
    )


def _is_deny(result: dict) -> bool:
    return (
        result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    )


def _make_checkout(root: Path) -> Path:
    task = root / "superRA" / "alpha" / "task.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "---\ntitle: Alpha\nstatus: not-started\ndepends_on: []\n---\n\n"
        "## Objective\n\nDo the thing.\n\n## Results\n\n(empty)\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "."], cwd=root, check=True)
    return task


def test_confinement_denies_a_foreign_task_tree_write(tmp_path: Path) -> None:
    workspace = tmp_path / "fixture"
    workspace.mkdir()
    foreign_task = _make_checkout(tmp_path / "checkout")

    result = _decide(
        workspace,
        "Write",
        {"file_path": str(foreign_task), "content": "escaped results"},
    )
    assert _is_deny(result), result


def test_confinement_denies_a_commit_in_a_foreign_checkout(tmp_path: Path) -> None:
    workspace = tmp_path / "fixture"
    workspace.mkdir()
    _make_checkout(tmp_path / "checkout")
    foreign = tmp_path / "checkout"

    result = _decide(
        workspace,
        "Bash",
        {"command": f"cd {foreign} && git add -A && git commit -m wip"},
    )
    assert _is_deny(result), result


def test_confinement_permits_work_inside_the_traced_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "fixture"
    workspace.mkdir()
    own_task = _make_checkout(workspace)

    assert not _is_deny(
        _decide(workspace, "Write", {"file_path": str(own_task), "content": "results"})
    )
    assert not _is_deny(
        _decide(
            workspace,
            "Bash",
            {"command": f"cd {workspace} && git add -A && git commit -m wip"},
        )
    )
    assert not _is_deny(
        _decide(
            workspace,
            "Write",
            {"file_path": str(workspace / "loading-evidence.json"), "content": "{}"},
        )
    )
