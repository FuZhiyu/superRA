"""Where records and state live: the task root by default, the project root until `repro migrate`."""
from __future__ import annotations

import json
import os
import re

import pytest

import _repro_layout
from _repro_acceptance import mutation_lock
from _repro_state import STATE_DIRNAME, ReproStateError, RunnerPaths, adopt_root_state, runner_paths
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
    from test_repro_acceptance import _dropbox_ignored
    assert _dropbox_ignored(state)  # a marker created the folder: Dropbox must leave it alone too


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


def test_hooks_and_runner_agree_on_the_task_root_that_holds_tasks(tmp_path):
    """A valid `.plan/` beside an empty `superRA/`: the runner picks `.plan/`, so the hooks must too."""
    import task_hook
    proj = tmp_path / "proj"
    (proj / "superRA").mkdir(parents=True)
    (proj / ".plan").mkdir()
    (proj / ".plan" / "task.md").write_text("---\ntitle: Root\nstatus: not-started\n---\n")
    assert _repro_layout.task_root(proj) == proj / ".plan"
    assert task_hook._repro_plan_root_for_file(proj / "Code" / "a.sh") == proj / ".plan"
    task_hook._record_mention(proj, "s1", "Code/a.sh")
    assert (proj / ".plan" / ".repro" / "local" / ".gitignore").is_file()
    assert list((proj / "superRA").iterdir()) == []


def test_root_level_records_use_root_level_state_whatever_else_exists(project):
    """An older superRA sharing the checkout writes its run records and stamps at the root."""
    assert project.run("build", *CHAIN) == 0
    _to_root_layout(project)
    (project.plan_root / ".repro" / "local" / "stamps").mkdir(parents=True)  # left by a migrated branch
    paths = runner_paths(project.root)
    assert paths.records_dir is None and paths.state_dir == project.root / STATE_DIRNAME
    assert set(project.states(*CHAIN).values()) == {"fresh"}


def test_a_command_that_resolved_its_paths_before_a_migration_is_refused(project):
    assert project.run("build", *CHAIN) == 0
    _to_root_layout(project)
    stale = runner_paths(project.root)
    assert project.run("migrate") == 0
    with pytest.raises(ReproStateError, match="moved while this command was starting"):
        with mutation_lock(stale):
            pass
    assert not (project.root / STATE_DIRNAME).exists() and not (project.root / "repro-lock.json").exists()


DOT_REPRO = """\
---
title: "Raw"
status: not-started
depends_on: []
---

## Objective

Read a folder that holds its own .repro directory.

## Reproduction

```yaml
steps:
  - name: raw
    cmd: cat raw/.repro/a.txt > output/raw.txt
    deps:
      - raw
    outs:
      - output/raw.txt
```
"""


def test_a_dot_repro_folder_inside_a_dependency_is_still_hashed(project):
    """Only the project's own `.repro` is left out of a directory dep."""
    assert project.run("build", *CHAIN) == 0
    project.write("raw/.repro/a.txt", "one\n")
    project.write("superRA/05-raw/task.md", DOT_REPRO)
    assert project.run("build", "05-raw") == 0
    assert project.states("05-raw") == {"raw": "fresh"}
    project.write("raw/.repro/a.txt", "two\n")
    assert project.states("05-raw") == {"raw": "stale"}


def _accepted_root_project(project) -> None:
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# harmless\n")
    assert project.run("accept", "01-a", "--reason", "Comment-only edit") == 0
    _to_root_layout(project)
    assert set(project.states(*CHAIN).values()) == {"fresh"}


def test_migrate_refuses_an_unreadable_legacy_ledger_and_moves_nothing(project, capsys):
    _accepted_root_project(project)
    project.write("repro-acceptance.json", "{not json")
    capsys.readouterr()
    assert project.run("migrate") == 1
    assert "repro-acceptance.json cannot be read" in capsys.readouterr().err
    assert project.read("repro-acceptance.json") == "{not json"
    assert (project.root / "repro-lock.json").is_file() and not (project.plan_root / ".repro").exists()


def test_a_migration_that_fails_part_way_is_undone(project, monkeypatch, capsys):
    _accepted_root_project(project)
    import _repro_migrate
    real = os.rename

    def rename(source, target):
        if str(source).endswith("build-a.json"):
            raise OSError("disk full")
        real(source, target)

    monkeypatch.setattr(_repro_migrate.os, "rename", rename)
    capsys.readouterr()
    assert project.run("migrate") == 1  # the lock had already moved when the record's move failed
    assert "disk full" in capsys.readouterr().err
    monkeypatch.undo()
    assert (project.root / "repro-lock.json").is_file() and (project.root / "repro-acceptance" / "build-a.json").is_file()
    assert not (project.plan_root / ".repro").exists()
    project.paths = runner_paths(project.root)
    assert set(project.states(*CHAIN).values()) == {"fresh"}


def test_records_split_by_a_merge_are_flagged_everywhere_and_migrate_reunites_them(project):
    """One branch moved the lock; another made its first acceptance at the root. Git keeps both."""
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# harmless\n")
    assert project.run("accept", "01-a", "--reason", "Comment-only edit") == 0
    os.rename(project.paths.acceptance_dir, project.root / "repro-acceptance")
    assert project.states("01-a") == {"build-a": "stale"}  # the acceptance is out of reach
    [finding] = [f for f in project.graph().findings if "repro-acceptance" in f.message]
    assert finding.severity == "warning" and "superra repro migrate" in finding.message  # task check, dashboard
    assert project.run("migrate") == 0
    assert not (project.root / "repro-acceptance").exists()
    assert project.states("01-a") == {"build-a": "fresh"}
    assert not [f for f in project.graph().findings if "project root" in f.message]


def test_migrate_quotes_the_paths_in_the_staging_command(tmp_path):
    from _repro_migrate import migrate
    root = tmp_path / "proj"
    plan = root / "Research Tasks"
    plan.mkdir(parents=True)
    (root / "repro-lock.json").write_text('{"version": 2, "steps": {}}\n')
    lines, code = migrate(root, plan)
    assert code == 0
    assert ("`git rm -r -q --cached --ignore-unmatch -- repro-lock.json "
            "&& git add -- 'Research Tasks/.repro'`") in "\n".join(lines)


def test_explain_searches_the_lock_at_both_locations_in_either_layout(project):
    from _repro_provenance import lock_refs
    assert project.run("build", *CHAIN) == 0
    both = ("superRA/.repro/lock.json", "repro-lock.json")
    assert lock_refs(project.paths)[:2] == both
    _to_root_layout(project)
    assert lock_refs(project.paths)[:2] == both


def test_migrate_stops_when_a_legacy_ledger_disagrees_with_a_task_root_record(project, capsys):
    """Records split by a merge: the ledger's review must not vanish in favour of a different one."""
    _accepted_root_project(project)
    record = json.loads((project.root / "repro-acceptance" / "build-a.json").read_text())
    ledger = {"version": 1, "steps": {"build-a": record}}
    os.rename(project.root / "repro-lock.json", project.plan_root / ".repro-lock.tmp")
    os.makedirs(project.plan_root / ".repro" / "acceptance")
    os.rename(project.plan_root / ".repro-lock.tmp", project.plan_root / ".repro" / "lock.json")
    os.rename(project.root / "repro-acceptance" / "build-a.json", project.plan_root / ".repro" / "acceptance" / "build-a.json")
    (project.root / "repro-acceptance").rmdir()
    project.write("repro-acceptance.json", json.dumps(ledger))
    capsys.readouterr()
    code = project.run("migrate")
    err = capsys.readouterr().err
    # The ledger holds the pre-reshape form of a record, so it either converts to the same bytes or is refused.
    assert (project.root / "repro-acceptance.json").exists() == (code == 1), err
    assert (project.plan_root / ".repro" / "acceptance" / "build-a.json").is_file()


def test_migrate_refuses_two_state_folders_when_it_moves_root_level_records(project, capsys):
    """After a branch switch the task root can hold another branch's state; the root-level one is the records' own."""
    assert project.run("build", *CHAIN) == 0
    _to_root_layout(project)
    (project.plan_root / ".repro" / "local").mkdir(parents=True)
    capsys.readouterr()
    assert project.run("migrate") == 1
    assert "both .superra-repro/ and superRA/.repro/local/ hold this machine's state" in capsys.readouterr().err
    assert (project.root / "repro-lock.json").is_file() and (project.root / STATE_DIRNAME).is_dir()


def test_migrate_waits_for_whoever_writes_records_in_the_layout_in_use(project, capsys):
    """Task-root records with a leftover at the root: an acceptance there holds the task-root lock, not the root one."""
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# harmless\n")
    assert project.run("accept", "01-a", "--reason", "Comment-only edit") == 0
    os.rename(project.paths.acceptance_dir, project.root / "repro-acceptance")
    capsys.readouterr()
    with mutation_lock(runner_paths(project.root)):
        assert project.run("migrate") == 1
    assert "another reproduction build or acceptance mutation is running" in capsys.readouterr().err
    assert (project.root / "repro-acceptance" / "build-a.json").is_file()
    assert project.run("migrate") == 0
    assert (project.plan_root / ".repro" / "acceptance" / "build-a.json").is_file()


def test_a_directory_dep_leaves_the_task_roots_repro_folder_out_in_the_root_layout_too(project):
    """A branch switch leaves `superRA/.repro/local/` beside root-level records; it is no part of the step's input."""
    assert project.run("build", *CHAIN) == 0
    project.write("superRA/04-all/task.md", WHOLE_TREE)
    assert project.run("build", "04-all") == 0
    _to_root_layout(project)
    assert project.states("04-all") == {"tree": "fresh"}
    project.write("superRA/.repro/local/stamps/left-behind.stamp", "x\n")
    assert project.states("04-all") == {"tree": "fresh"}


def test_a_symlinked_task_file_does_not_make_a_task_root(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".plan").mkdir(parents=True)
    (proj / ".plan" / "task.md").write_text("---\ntitle: Root\nstatus: not-started\n---\n")
    (proj / "superRA").mkdir()
    (proj / "superRA" / "task.md").symlink_to(proj / ".plan" / "task.md")
    assert _repro_layout.task_root(proj) == proj / ".plan"


def test_migrate_takes_the_lock_of_the_layout_in_use_even_on_a_fresh_checkout(project, capsys):
    """No state folder yet: an acceptance starting during the move must still find the lock held."""
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# harmless\n")
    assert project.run("accept", "01-a", "--reason", "Comment-only edit") == 0
    os.rename(project.paths.acceptance_dir, project.root / "repro-acceptance")
    import shutil
    shutil.rmtree(project.paths.state_dir)  # a fresh checkout: records from git, no machine state
    import _repro_migrate
    seen = []
    real = _repro_migrate._migrate

    def watched(*args):
        from _repro_acceptance import lock_holder
        seen.append(lock_holder(runner_paths(project.root)))
        return real(*args)

    _repro_migrate._migrate = watched
    try:
        assert project.run("migrate") == 0
    finally:
        _repro_migrate._migrate = real
    assert seen == [os.getpid()]  # held while the records are read, checked, and moved
    assert (project.plan_root / ".repro" / "acceptance" / "build-a.json").is_file()
    assert not (project.root / STATE_DIRNAME).exists()
