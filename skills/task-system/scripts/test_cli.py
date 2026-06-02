#!/usr/bin/env python3
"""Tests for the packaged superra command surface."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import cli


def _write_task_md(path: Path, title: str, status: str = "not-started", results: str = "") -> None:
    body = "## Objective\n\nTest objective.\n"
    if results:
        body += f"\n## Results\n\n{results}\n"
    path.write_text(
        "\n".join(
            [
                "---",
                f'title: "{title}"',
                f"status: {status}",
                "depends_on: []",
                "tags: []",
                "created: 2026-01-01",
                "---",
                "",
                body,
            ]
        ),
        encoding="utf-8",
    )


@pytest.fixture
def task_root(tmp_path: Path) -> Path:
    root = tmp_path / "superRA"
    root.mkdir()
    _write_task_md(root / "task.md", "Root")

    first = root / "01-first"
    first.mkdir()
    _write_task_md(first / "task.md", "First", "approved", results="- done")

    second = root / "02-second"
    second.mkdir()
    _write_task_md(second / "task.md", "Second")
    return root


def test_task_read_autodetects_root_from_nested_cwd(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(task_root / "01-first")

    cli.main(["task", "read", "01-first", "--json"])

    data = json.loads(capsys.readouterr().out)
    assert data["task"]["path"] == "01-first"
    assert data["task"]["title"] == "First"


def test_task_tree_autodetect_prefers_superra_over_plan(
    tmp_path: Path,
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    legacy = tmp_path / ".plan"
    legacy.mkdir()
    _write_task_md(legacy / "task.md", "Legacy")
    monkeypatch.chdir(tmp_path)

    cli.main(["task", "tree", "--json"])

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Root"


def test_task_tree_autodetects_legacy_plan_when_superra_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    legacy = tmp_path / ".plan"
    legacy.mkdir()
    _write_task_md(legacy / "task.md", "Legacy")
    monkeypatch.chdir(tmp_path)

    cli.main(["task", "tree", "--json"])

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Legacy"


def test_task_create_uses_autodetected_root_for_legacy_wrapper(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["task", "create", "03-third", "--title", "Third"])

    created = task_root / "03-third" / "task.md"
    assert created.exists()
    assert 'title: "Third"' in created.read_text(encoding="utf-8")
    assert not (task_root / "serve").exists()


def test_task_comment_list_preserves_json_mode(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["task", "comment", "list", "01-first", "--json"])

    assert json.loads(capsys.readouterr().out) == []


@pytest.mark.parametrize(
    "argv",
    [
        ["task", "update", "../outside", "--title", "Escaped"],
        ["task", "status", "cascade", "../outside", "--status", "approved"],
        ["task", "result", "add", "../outside", "--finding", "Escaped"],
        ["task", "dep", "add", "../outside", "01-first"],
        ["task", "dep", "remove", "../outside", "01-first"],
        ["task", "rename", "../outside", "outside-renamed"],
        ["task", "rename", "01-first", "../outside-renamed"],
    ],
)
def test_mutation_commands_reject_paths_outside_root(
    task_root: Path,
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    outside = task_root.parent / "outside"
    outside.mkdir()
    _write_task_md(outside / "task.md", "Outside")
    before = (outside / "task.md").read_text(encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        cli.main([*argv, "--root", str(task_root)])

    assert excinfo.value.code == 1
    assert "escapes plan root" in capsys.readouterr().err
    assert (outside / "task.md").read_text(encoding="utf-8") == before


def test_dep_add_rejects_path_like_dependency_slug(
    task_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    outside = task_root.parent / "outside"
    outside.mkdir()
    _write_task_md(outside / "task.md", "Outside")

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["task", "dep", "add", "02-second", "../outside", "--root", str(task_root)])

    assert excinfo.value.code == 1
    assert "dependency must be a sibling slug" in capsys.readouterr().err
    second = (task_root / "02-second" / "task.md").read_text(encoding="utf-8")
    assert "../outside" not in second


def test_status_fix_routes_existing_update_fix_mode(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["task", "status", "fix"])

    out = capsys.readouterr().out
    assert "Scanning" in out


def test_dashboard_export_is_top_level_command(
    task_root: Path,
    tmp_path: Path,
) -> None:
    output = tmp_path / "dashboard.html"

    cli.main(["dashboard", "export", "--root", str(task_root), "--output", str(output)])

    assert output.exists()
    assert "Root" in output.read_text(encoding="utf-8")


def test_packaged_entry_point_exports_dashboard_from_package_data(
    task_root: Path,
    tmp_path: Path,
) -> None:
    if shutil.which("uv") is None:
        pytest.skip("uv is required to exercise the packaged console entry point")

    output = tmp_path / "packaged-dashboard.html"
    result = subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(SKILL_DIR),
            "superra",
            "dashboard",
            "export",
            "--root",
            str(task_root),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    html = output.read_text(encoding="utf-8")
    assert "Root" in html
    assert "window.STANDALONE = true" in html
    assert "markdown-it" in html


def test_backward_compatible_direct_script_query(
    task_root: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "task_query.py"),
            "--plan-root",
            str(task_root),
            "--tree",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["title"] == "Root"


def test_task_dashboard_is_not_registered(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["task", "dashboard", "--help"])

    assert excinfo.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
