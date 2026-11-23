"""Where records and state live: the task root by default, the project root until `repro migrate`."""
from __future__ import annotations

import json
import os
import re

from _repro_state import STATE_DIRNAME, runner_paths
from test_repro_runner import CHAIN, Project, project  # noqa: F401


def _to_root_layout(project: Project) -> None:
    """Rewind a built project to the root-level layout it had before the records moved."""
    home = project.plan_root / ".repro"
    os.rename(home / "lock.json", project.root / "repro-lock.json")
    if (home / "acceptance").is_dir():
        os.rename(home / "acceptance", project.root / "repro-acceptance")
    os.rename(home / "local", project.root / STATE_DIRNAME)
    home.rmdir()
    project.paths = runner_paths(project.root)


def test_a_project_with_root_level_records_keeps_reading_and_writing_them_there(project):
    assert project.run("build", *CHAIN) == 0
    before = project.states(*CHAIN)
    _to_root_layout(project)
    assert project.paths.records_dir is None and project.paths.state_dir == project.root / STATE_DIRNAME
    assert project.states(*CHAIN) == before  # the check's stamp included
    project.write("Code/a.sh", "mkdir -p output\necho changed > output/a.txt\n")
    assert project.run("build", *CHAIN) == 0
    assert set(project.states(*CHAIN).values()) == {"fresh"}
    assert "build-a" in json.loads(project.read("repro-lock.json"))["steps"]
    assert not (project.plan_root / ".repro").exists()
    assert f"{STATE_DIRNAME}/" in project.read(".gitignore").split()


def test_migrate_moves_records_and_state_and_stales_nothing(project, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# harmless\n")
    assert project.run("accept", "01-a", "--reason", "Comment-only edit") == 0
    _to_root_layout(project)
    before = project.states(*CHAIN)
    assert set(before.values()) == {"fresh"}

    capsys.readouterr()
    assert project.run("migrate", "--dry-run") == 0
    assert "Would move into superRA/.repro/:" in capsys.readouterr().out
    assert (project.root / "repro-lock.json").is_file() and not (project.plan_root / ".repro").exists()

    assert project.run("migrate") == 0
    out = capsys.readouterr().out
    assert re.search(r"repro-lock\.json\s+->  superRA/\.repro/lock\.json", out)
    assert re.search(r"repro-acceptance/\s+->  superRA/\.repro/acceptance/", out)
    assert re.search(r"\.superra-repro/\s+->  superRA/\.repro/local/", out)
    assert "`git add -A -- repro-lock.json repro-acceptance superRA/.repro`" in out
    for gone in ("repro-lock.json", "repro-acceptance", STATE_DIRNAME):
        assert not (project.root / gone).exists()
    project.paths = runner_paths(project.root)
    assert project.paths.lock_file == project.plan_root / ".repro" / "lock.json"
    assert (project.paths.acceptance_dir / "build-a.json").is_file()
    assert (project.paths.state_dir / ".gitignore").read_text() == "*\n"
    assert project.states(*CHAIN) == before

    assert project.run("migrate") == 0
    assert "Nothing to migrate" in capsys.readouterr().out


def test_a_root_level_lock_beside_task_root_records_warns_and_is_never_overwritten(project, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("repro-lock.json", project.read("superRA/.repro/lock.json"))
    capsys.readouterr()
    assert project.run("status", *CHAIN) == 0
    assert "Warning: repro-lock.json at the project root: not read" in capsys.readouterr().err
    assert project.run("migrate") == 1
    assert "superRA/.repro/lock.json already exists" in capsys.readouterr().err
    assert (project.root / "repro-lock.json").is_file()


def test_root_level_state_moves_into_the_task_root_once_the_records_are_there(project):
    """A checkout that pulls migrated records still has its own state at the project root."""
    assert project.run("build", *CHAIN) == 0
    os.rename(project.paths.state_dir, project.root / STATE_DIRNAME)
    assert runner_paths(project.root).state_dir == project.root / STATE_DIRNAME  # until a command adopts it
    assert project.run("status", *CHAIN) == 0
    assert not (project.root / STATE_DIRNAME).exists()
    assert (project.paths.stamps_dir / "check-b.stamp").is_file()
    assert set(project.states(*CHAIN).values()) == {"fresh"}
