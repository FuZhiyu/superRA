"""Where records and state live: the task root by default, the project root until `repro migrate`."""
from __future__ import annotations

import json
import os
import re

import _repro_layout
from _repro_acceptance import mutation_lock
from _repro_state import STATE_DIRNAME, RunnerPaths, adopt_root_state, runner_paths
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
    assert ("`git rm -r -q --cached --ignore-unmatch -- repro-lock.json repro-acceptance "
            "&& git add -- superRA/.repro`") in out
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


def test_root_level_state_stays_put_while_a_build_holds_its_lock(project):
    assert project.run("build", *CHAIN) == 0
    legacy = project.root / STATE_DIRNAME
    os.rename(project.paths.state_dir, legacy)
    with mutation_lock(RunnerPaths(project_root=project.root, state_dir=legacy)):
        adopt_root_state(project.root)
        assert legacy.is_dir() and not (project.plan_root / ".repro" / "local").exists()
    adopt_root_state(project.root)
    assert not legacy.exists() and (project.plan_root / ".repro" / "local" / "hashes.json").is_file()


def test_a_project_whose_task_root_is_dot_plan_keeps_hook_and_runner_state_there(tmp_path):
    """The hooks pass no task root: a legacy `.plan/` tree must not grow a stray `superRA/`."""
    import task_hook
    proj = tmp_path / "proj"
    (proj / ".plan").mkdir(parents=True)
    state = proj / ".plan" / ".repro" / "local"
    assert _repro_layout.state_dir(proj) == state and runner_paths(proj).state_dir == state
    task_hook._record_mention(proj, "s1", "Code/a.sh")
    assert task_hook._mentioned(proj, "s1", "Code/a.sh")
    assert (state / ".gitignore").read_text() == "*\n"  # git lists nothing the hook wrote
    assert not (proj / "superRA").exists()
    assert task_hook._repro_plan_root_for_file(proj / "Code" / "a.sh") == proj / ".plan"


WHOLE_TREE = """\
---
title: "All"
status: not-started
depends_on: []
---

## Objective

List the tree.

## Reproduction

```yaml
steps:
  - name: tree
    cmd: ls superRA > output/tree.txt
    deps:
      - superRA
    outs:
      - output/tree.txt
```
"""


def test_a_directory_dep_covering_the_task_root_leaves_the_records_and_state_out(project):
    assert project.run("build", *CHAIN) == 0
    project.write("superRA/04-all/task.md", WHOLE_TREE)
    assert project.run("build", "04-all") == 0  # its own log and lock entry do not change its dep
    assert project.states("04-all") == {"tree": "fresh"}
    assert project.run("build", "03-x") == 0  # rewrites the lock, a log, and a run record
    assert project.states("04-all") == {"tree": "fresh"}
