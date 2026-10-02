"""Tests for the `superra repro` runner (repro_run.py, _repro_state.py)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import cli
import repro_run
from _repro import build_graph
from _repro_state import (
    STATE_DIRNAME,
    HashCache,
    compute_status,
    read_lock,
    render_dag,
    runner_paths,
)

CHAIN = ("01-a", "02-b")  # the a -> b -> check-b chain; 03-x stands apart

# ---------------------------------------------------------------------------
# Fixture project
# ---------------------------------------------------------------------------

CONFIG = """\
reproduction:
  vars:
    OUT: output
  runners:
    sh: sh {script}
"""

TASK_A = """\
---
title: "A"
status: not-started
depends_on: []
---

## Objective

Build a.

## Reproduction

```yaml
steps:
  - name: build-a
    cmd: sh Code/a.sh
    deps:
      - Code/a.sh
    outs:
      - "${OUT}/a.txt"
```
"""

TASK_B = """\
---
title: "B"
status: not-started
depends_on: []
---

## Objective

Build b and check it.

## Reproduction

```yaml
steps:
  - name: build-b
    runner: sh
    script: Code/b.sh
    deps:
      - "${OUT}/a.txt"
    outs:
      - "${OUT}/b.txt"
  - name: check-b
    kind: check
    cmd: test -s output/b.txt
    deps:
      - "${OUT}/b.txt"
```
"""

TASK_X = """\
---
title: "X"
status: not-started
depends_on: []
---

## Objective

An independent chain.

## Reproduction

```yaml
steps:
  - name: build-x
    cmd: sh Code/x.sh
    deps:
      - Code/x.sh
    outs:
      - "${OUT}/x.txt"
```
"""


TASK_GEN = """\
---
title: "Gen"
status: not-started
depends_on: []
---

## Objective

Write a directory of parts.

## Reproduction

```yaml
steps:
  - name: z-gen
    cmd: sh Code/gen.sh
    deps:
      - Code/gen.sh
    outs:
      - "${OUT}/parts"
```
"""

TASK_USE = """\
---
title: "Use"
status: not-started
depends_on: []
---

## Objective

Read one file out of that directory.

## Reproduction

```yaml
steps:
  - name: a-use
    cmd: sh Code/use.sh
    deps:
      - Code/use.sh
      - "${OUT}/parts/a.txt"
    outs:
      - "${OUT}/used.txt"
```
"""


class Project:
    """A fixture task tree plus the helpers the runner tests share."""

    def __init__(self, root: Path):
        self.root = root
        self.plan_root = root / "superRA"
        self.paths = runner_paths(root)

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def read(self, relative: str) -> str:
        return (self.root / relative).read_text(encoding="utf-8")

    def graph(self):
        return build_graph(self.plan_root, project_root=self.root)

    def run(self, *argv: str) -> int:
        try:
            repro_run.main(["--plan-root", str(self.plan_root), *argv])
        except SystemExit as exc:
            return int(exc.code or 0)
        return 0

    def status(self, *targets: str):
        return compute_status(self.graph(), self.paths, targets=targets)

    def states(self, *targets: str) -> dict[str, str]:
        return {e.step.name: e.status for e in self.status(*targets).reported}

    def run_times(self) -> dict[str, float]:
        """When each step last executed — unchanged means the build skipped it."""
        times = {}
        for record in sorted(self.paths.runs_dir.glob("*.json")):
            times[record.stem] = json.loads(record.read_text())["ended_at"]
        return times


@pytest.fixture
def project(tmp_path) -> Project:
    proj = Project(tmp_path / "proj")
    proj.write("superRA/config.yaml", CONFIG)
    proj.write("superRA/01-a/task.md", TASK_A)
    proj.write("superRA/02-b/task.md", TASK_B)
    proj.write("superRA/03-x/task.md", TASK_X)
    proj.write("Code/a.sh", "mkdir -p output\necho hello > output/a.txt\n")
    proj.write("Code/b.sh", "cat output/a.txt output/a.txt > output/b.txt\n")
    proj.write("Code/x.sh", "mkdir -p output\necho x > output/x.txt\n")
    return proj


@pytest.fixture
def dir_project(tmp_path) -> Project:
    """A producer whose out is a directory, and a consumer of one file inside it.

    The step names put the consumer first alphabetically, which is the order an
    unordered scheduler would run them in.
    """
    proj = Project(tmp_path / "dirproj")
    proj.write("superRA/config.yaml", CONFIG)
    proj.write("superRA/01-gen/task.md", TASK_GEN)
    proj.write("superRA/02-use/task.md", TASK_USE)
    proj.write("Code/gen.sh", "mkdir -p output/parts\necho v1 > output/parts/a.txt\n")
    proj.write("Code/use.sh", "cat output/parts/a.txt > output/used.txt\n")
    return proj


# ---------------------------------------------------------------------------
# Hash cache
# ---------------------------------------------------------------------------

def test_directory_state_covers_every_file_inside(tmp_path):
    directory = tmp_path / "tree"
    (directory / "nested").mkdir(parents=True)
    (directory / "nested" / "a.txt").write_text("a")
    cache = HashCache()
    before = cache.path_state(directory)

    (directory / "nested" / "b.txt").write_text("b")
    assert HashCache().path_state(directory) != before


# ---------------------------------------------------------------------------
# Status without a build
# ---------------------------------------------------------------------------

def test_unbuilt_steps_report_never_built(project):
    report = project.status(*CHAIN)
    assert {e.step.name for e in report.reported} == {"build-a", "build-b", "check-b"}
    assert all(e.status == "missing" for e in report.reported)
    assert all(e.reason == "never built" for e in report.reported)
    assert report.ok is False


def test_an_absent_input_no_step_produces_makes_its_consumer_unverified(project):
    project.write("Code/a.sh", "cp Data/raw.csv output/a.txt\n")
    project.write(
        "superRA/01-a/task.md", TASK_A.replace("      - Code/a.sh", "      - Data/raw.csv")
    )
    assert project.status(*CHAIN).entry("build-a").status == "missing"  # never built outranks it
    project.write("Data/raw.csv", "1\n")
    assert project.run("build", *CHAIN) == 0
    (project.root / "Data/raw.csv").unlink()
    report = project.status(*CHAIN)
    entry = report.entry("build-a")
    assert entry.status == "unverified"
    assert entry.reason == "dependency Data/raw.csv is not on disk, and no step produces it"
    assert entry.files[0] == {"node": "Data/raw.csv", "role": "dependency", "outcome": "unknown",
                              "online_only": False, "size": None}
    assert report.entry("build-b").status == "fresh"  # an unverified producer lifts nothing


def test_scoped_status_verifies_one_task_without_unrelated_steps(project, capsys):
    assert project.run("status", "03-x") == 1
    assert project.run("build", "03-x") == 0
    capsys.readouterr()
    assert project.run("status", "03-x", "--json") == 0
    report = json.loads(capsys.readouterr().out)
    assert report["targets"] == ["03-x"]
    assert [step["name"] for step in report["steps"]] == ["build-x"]
    assert project.states()["build-a"] == "missing"


def test_scoped_status_rejects_an_unknown_target(project, capsys):
    assert project.run("status", "unregistered") == 1
    assert "no step or task matches unregistered" in capsys.readouterr().err


@pytest.mark.parametrize("targets", [["02-b#check-b"]])
def test_scoped_status_hashes_only_selected_ancestors(project, targets):
    assert project.run("build", ".") == 0

    class RecordingCache(HashCache):
        def __init__(self):
            super().__init__()
            self.visited = set()

        def path_state(self, path):
            self.visited.add(path.relative_to(project.root).as_posix())
            return super().path_state(path)

    cache = RecordingCache()
    report = compute_status(project.graph(), project.paths, targets=targets, cache=cache, upstream=True)
    assert report.ok
    assert {e.step.name for e in report.entries} == {"build-a", "build-b", "check-b"}
    assert {"Code/a.sh", "output/a.txt", "output/b.txt"} <= cache.visited
    assert not {"Code/x.sh", "output/x.txt"} & cache.visited
    assert cache.full_reads > 0

    all_cache = RecordingCache()
    compute_status(project.graph(), project.paths, cache=all_cache)
    assert {"Code/x.sh", "output/x.txt"} <= all_cache.visited


def test_a_check_only_task_blocks_completion_once_it_is_in_scope(project):
    project.write("superRA/04-check/task.md", '''---
title: Selected protection
status: not-started
---

## Objective

Protect a.

## Reproduction

```yaml
steps:
  - name: protect-a
    kind: check
    cmd: 'false'
    deps:
      - "${OUT}/a.txt"
```
''')
    assert project.run("build", *CHAIN) == 0
    assert project.status(*CHAIN).ok
    assert not project.status(".").ok
    assert project.run("build", ".") == 1
    assert project.states()["protect-a"] == "failed"


# ---------------------------------------------------------------------------
# Target selection
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("command", ["build"])
def test_a_command_without_targets_is_rejected(project, command, capsys):
    assert project.run(command) == 2
    assert "name at least one task or task#step target" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [
    ["status", ".", "--tier", "canon"],
    ["build", ".", "--tier=required"],
    ["tier", "01-a", "required"],
    ["--root", "superRA", "tier", "01-a", "canon"],
])
def test_retired_tier_invocations_name_task_targets(argv, capsys):
    with pytest.raises(SystemExit) as exc:
        repro_run.main(argv)
    assert exc.value.code == 2
    assert "reproduction tiers are retired; name task or task#step targets" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# DAG rendering
# ---------------------------------------------------------------------------

def test_dag_mermaid_renders_a_flowchart(project):
    text = render_dag(project.graph(), mermaid=True)
    assert text.startswith("graph LR")
    assert 'build-a["build-a"]\n' in text
    assert 'check-b["check-b"]:::check' in text
    assert "build-a -->|a.txt| build-b" in text


def test_cli_routes_repro_to_the_runner(project, capsys):
    cli.main(["repro", "--plan-root", str(project.plan_root), "dag", "--mermaid"])
    assert capsys.readouterr().out.startswith("graph LR")


# ---------------------------------------------------------------------------
# Decision support
# ---------------------------------------------------------------------------

def test_status_and_explain_name_consumers_outside_the_owning_task(project, capsys):
    assert project.run("status", ".", "--json") == 1
    by_name = {s["name"]: s for s in json.loads(capsys.readouterr().out)["steps"]}
    assert by_name["build-a"]["external_consumers"] == ["02-b#build-b"]
    assert by_name["build-b"]["external_consumers"] == []  # check-b sits in 02-b
    assert by_name["build-x"]["external_consumers"] == []

    assert project.run("status", ".") == 1
    text = capsys.readouterr().out
    assert re.search(r"build-a\s+missing\s+outside readers: 1", text)
    assert re.search(r"build-x\s+missing\s+outside readers: 0", text)
    # A check with no cross-task consumer gets the fact, never a significance verdict.
    assert not re.search(r"task-local|\bshared\b", text)

    assert project.run("explain", "01-a#build-a") == 0
    assert "  outs read outside 01-a: 02-b#build-b" in capsys.readouterr().out
    assert project.run("explain", "03-x#build-x") == 0
    assert "  no step outside 03-x reads its outs" in capsys.readouterr().out


def test_dry_run_reports_what_each_step_last_cost(project, capsys):
    assert project.run("build", "01-a") == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# edited\n")
    capsys.readouterr()
    assert project.run("build", ".", "--dry-run") == 0
    output = capsys.readouterr().out
    assert "Would execute 4 step(s):" in output
    assert re.search(r"build-a\s+\d+\.\d+s", output)
    assert re.search(r"build-x\s+unknown", output)
    assert re.search(r"Last recorded cost: \d+\.\d+s, plus 3 step\(s\) with no recorded duration\.", output)
    assert "superra repro explain" in output and "superra repro accept" in output

    assert project.run("build", ".") == 0
    capsys.readouterr()
    assert project.run("build", ".", "--dry-run") == 0
    assert "Nothing to execute: every selected step is fresh." in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def test_first_build_runs_every_step(project):
    assert project.run("build", *CHAIN) == 0
    assert project.read("output/a.txt") == "hello\n"
    assert project.read("output/b.txt") == "hello\nhello\n"
    assert (project.root / STATE_DIRNAME / "stamps" / "check-b.stamp").is_file()
    assert project.states(*CHAIN) == {
        "build-a": "fresh",
        "build-b": "fresh",
        "check-b": "fresh",
    }


def test_state_directory_is_created_and_gitignored(project):
    project.run("build", *CHAIN)
    assert (project.root / STATE_DIRNAME / "logs" / "build-a.log").is_file()
    assert f"{STATE_DIRNAME}/" in project.read(".gitignore").split()


def test_lock_ids_stay_in_logical_form(project):
    project.run("build", *CHAIN)
    lock = read_lock(project.paths.lock_file)
    assert "${OUT}/a.txt" in lock["build-a"].produces
    assert "output/a.txt" not in lock["build-a"].produces
    assert "build-a::spec" in lock["build-a"].depends_on


def test_second_build_is_a_no_op(project):
    project.run("build", *CHAIN)
    before = project.run_times()
    assert project.run("build", *CHAIN) == 0
    assert project.run_times() == before


def test_touching_a_dep_with_identical_bytes_is_a_no_op(project):
    project.run("build", *CHAIN)
    before = project.run_times()
    (project.root / "Code" / "a.sh").touch()
    assert project.states(*CHAIN)["build-a"] == "fresh"
    assert project.run("build", *CHAIN) == 0
    assert project.run_times() == before


def test_a_dep_edit_reruns_exactly_the_affected_chain(project):
    project.run("build", ".")
    before = project.run_times()
    project.write("Code/a.sh", "mkdir -p output\necho goodbye > output/a.txt\n")

    states = project.states()
    assert states["build-a"] == "stale"
    assert states["build-b"] == "stale"
    assert states["build-x"] == "fresh"

    assert project.run("build", ".") == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert after["build-b"] != before["build-b"]
    assert after["check-b"] != before["check-b"]
    assert after["build-x"] == before["build-x"]


def test_regenerating_identical_bytes_does_not_cascade(project):
    project.run("build", *CHAIN)
    before = project.run_times()
    project.write("Code/a.sh", "mkdir -p output\n# no behaviour change\necho hello > output/a.txt\n")

    assert project.run("build", *CHAIN) == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert after["build-b"] == before["build-b"]
    assert after["check-b"] == before["check-b"]


def test_deleting_an_out_reports_missing_and_rebuilds_it(project):
    project.run("build", *CHAIN)
    (project.root / "output" / "b.txt").unlink()

    entry = project.status(*CHAIN).entry("build-b")
    assert entry.status == "missing"
    assert "${OUT}/b.txt" in entry.reason

    assert project.run("build", *CHAIN) == 0
    assert project.read("output/b.txt") == "hello\nhello\n"
    assert project.states(*CHAIN)["build-b"] == "fresh"


def test_a_failing_step_stops_its_descendants_and_exits_non_zero(project):
    project.run("build", *CHAIN)
    project.write("Code/b.sh", "echo boom >&2\nexit 3\n")

    assert project.run("build", *CHAIN) == 1
    entry = project.status(*CHAIN).entry("build-b")
    assert entry.status == "failed"
    assert f"{STATE_DIRNAME}/logs/build-b.log" in entry.reason
    assert "boom" in project.read(f"{STATE_DIRNAME}/logs/build-b.log")
    assert project.states(*CHAIN)["check-b"] == "stale"


TASK_JOIN = """\
---
title: "Join"
status: not-started
depends_on: []
---

## Objective

Join a slow and a failing branch.

## Reproduction

```yaml
steps:
  - name: a-slow
    cmd: sleep 1 && mkdir -p output && echo s > output/slow.txt
    outs:
      - "${OUT}/slow.txt"
  - name: b-fail
    cmd: exit 3
    outs:
      - "${OUT}/bad.txt"
  - name: join
    cmd: cat output/slow.txt output/bad.txt > output/join.txt
    deps:
      - "${OUT}/slow.txt"
      - "${OUT}/bad.txt"
    outs:
      - "${OUT}/join.txt"
```
"""


def test_a_failed_parent_skips_its_child_while_a_sibling_parent_runs(tmp_path, capsys):
    proj = Project(tmp_path / "join")
    proj.write("superRA/config.yaml", CONFIG)
    proj.write("superRA/01-join/task.md", TASK_JOIN)

    # The failure lands while a-slow, the parent listed first, is still running.
    assert proj.run("build", ".", "-j", "2") == 1
    out = capsys.readouterr().out
    assert "1 executed, 1 failed, 1 skipped" in out
    states = proj.states()
    assert states["a-slow"] == "fresh" and states["b-fail"] == "failed"


@pytest.mark.parametrize("flag,expected", [
    (("--force",), {"check-b"}),
    (("--upstream", "--force"), {"build-a", "build-b", "check-b"}),
])
def test_force_scope_preserves_freshness_and_unrelated_steps(project, flag, expected):
    assert project.run("build", ".") == 0
    before = project.run_times()
    assert project.run("build", "02-b#check-b", *flag, "-j", "2") == 0
    after = project.run_times()
    assert {name for name in after if before[name] != after[name]} == expected
    assert all(state == "fresh" for state in project.states().values())
    assert project.run("build", ".") == 0
    assert project.run_times() == after


@pytest.mark.parametrize("flag", [("--force",)])
def test_failed_forced_check_cannot_reuse_cached_success(project, monkeypatch, flag):
    project.write("Code/check.sh", 'test "$CHECK_OK" = yes\n')
    project.write("superRA/02-b/task.md", TASK_B.replace(
        "cmd: test -s output/b.txt", "cmd: sh Code/check.sh"
    ).replace(
        '    deps:\n      - "${OUT}/b.txt"',
        '    deps:\n      - Code/check.sh\n      - "${OUT}/b.txt"',
    ))
    monkeypatch.setenv("CHECK_OK", "yes")
    assert project.run("build", *CHAIN) == 0
    monkeypatch.setenv("CHECK_OK", "no")
    assert project.run("build", "02-b#check-b", *flag) == 1
    assert project.states()["check-b"] == "failed"
    assert project.run("build", *CHAIN) == 1
    monkeypatch.setenv("CHECK_OK", "yes")
    assert project.run("build", *CHAIN) == 0
    assert project.status(*CHAIN).ok


def test_a_params_change_reruns_only_that_step(project):
    project.run("build", *CHAIN)
    before = project.run_times()
    project.write(
        "superRA/01-a/task.md",
        TASK_A.replace(
            '    outs:\n      - "${OUT}/a.txt"',
            '    params:\n      seed: 7\n    outs:\n      - "${OUT}/a.txt"',
        ),
    )
    entry = project.status(*CHAIN).entry("build-a")
    assert entry.status == "stale"
    assert entry.reason == "the step definition changed"

    assert project.run("build", *CHAIN) == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert after["build-b"] == before["build-b"]


def test_a_sidecar_tracked_out_is_hashed_through_its_sidecar(project):
    project.write(
        "superRA/01-a/task.md",
        TASK_A.replace(
            '      - "${OUT}/a.txt"\n',
            '      - path: "${OUT}/a.txt"\n        sidecar: "${OUT}/a.txt.sha256"\n',
        ),
    )
    assert project.run("build", "01-a#build-a") == 0
    sidecar = project.read("output/a.txt.sha256")
    assert "${OUT}/a.txt" in sidecar

    lock = read_lock(project.paths.lock_file)
    assert lock["build-a"].produces["${OUT}/a.txt"] == HashCache().file_hash(
        project.root / "output" / "a.txt.sha256"
    )

    # A hand-edit of the out goes unnoticed until the sidecar is rewritten.
    project.write("output/a.txt", "tampered\n")
    assert project.states(*CHAIN)["build-a"] == "fresh"



def test_status_reads_only_the_lock_holders_steps_as_building(project, capsys):
    """An in-flight run record is executing only when the process holding the
    mutation lock wrote it; any other in-flight record is an interrupted run."""
    import os
    from _repro_acceptance import lock_holder, mutation_lock
    from _repro_state import write_run_record

    def build_b():
        capsys.readouterr()
        project.run("status", *CHAIN, "--json")
        return next(s for s in json.loads(capsys.readouterr().out)["steps"] if s["name"] == "build-b")

    project.run("build", *CHAIN)
    write_run_record(project.paths, "build-b", {"outcome": "running", "started_at": 1.0, "pid": 999999})
    assert lock_holder(project.paths) is None
    assert project.states(*CHAIN)["build-b"] == "failed"

    with mutation_lock(project.paths):  # an unrelated build or acceptance
        assert lock_holder(project.paths) == os.getpid()
        stale = build_b()
        write_run_record(project.paths, "build-b", {"outcome": "running", "started_at": 1.0, "pid": os.getpid()})
        live = build_b()
    assert stale["status"] == "failed" and stale["running"] is False
    assert live["running"] is True and live["started_at"] == 1.0
    assert live["reason"] == "building now" and live["status"] == "fresh"
    assert lock_holder(project.paths) is None

def test_status_json_matches_the_documented_shape(project, capsys):
    project.run("build", *CHAIN)
    capsys.readouterr()
    assert project.run("status", *CHAIN, "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is True
    assert payload["targets"] == list(CHAIN)
    assert payload["root"] == str(project.root)
    assert payload["summary"]["total"] == 3
    assert payload["summary"]["fresh"] == 3
    assert payload["findings"] == []
    assert {e["logical"] for e in payload["external_inputs"]} == {
        "Code/a.sh",
        "Code/b.sh",
    }
    assert all(e["exists"] for e in payload["external_inputs"])

    step = next(s for s in payload["steps"] if s["name"] == "build-b")
    assert set(step) == {
        "name", "task", "kind", "cmd", "status", "reason", "changes",
        "duration", "last_run", "log", "deps", "outs", "acceptance",
        "local_status", "local_reason", "boundary_inputs", "external_consumers",
        "running", "started_at", "origin", "files",
    }
    assert step["running"] is False
    assert step["origin"] is None
    size = lambda path: (project.root / path).stat().st_size
    assert step["files"] == [
        {"node": "Code/b.sh", "role": "dependency", "outcome": "matches", "online_only": False,
         "size": size("Code/b.sh")},
        {"node": "${OUT}/a.txt", "role": "dependency", "outcome": "matches", "online_only": False,
         "size": size("output/a.txt")},
        {"node": "${OUT}/b.txt", "role": "output", "outcome": "matches", "online_only": False,
         "size": size("output/b.txt")},
    ]
    assert step["task"] == "02-b"
    assert step["status"] == "fresh"
    assert step["duration"] > 0
    assert step["deps"] == [
        {"logical": "Code/b.sh", "resolved": "Code/b.sh"},
        {"logical": "${OUT}/a.txt", "resolved": "output/a.txt"},
    ]
    assert step["outs"] == [
        {"path": {"logical": "${OUT}/b.txt", "resolved": "output/b.txt"}, "sidecar": None}
    ]


def test_status_json_reports_a_stale_step_and_exits_one(project, capsys):
    project.run("build", *CHAIN)
    project.write("Code/b.sh", "cat output/a.txt > output/b.txt\n")
    capsys.readouterr()
    assert project.run("status", *CHAIN, "--json") == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is False
    step = next(s for s in payload["steps"] if s["name"] == "build-b")
    assert step["status"] == "stale"
    assert step["changes"] == [
        {"node": "Code/b.sh", "kind": "dependency", "change": "changed"}
    ]


def test_a_second_status_reads_no_file_content(project):
    project.run("build", *CHAIN)
    graph = project.graph()
    project.paths.cache_file.unlink()  # the build populated it; start cold

    first = HashCache(project.paths.cache_file)
    compute_status(graph, project.paths, cache=first)
    assert first.full_reads > 0

    second = HashCache(project.paths.cache_file)
    compute_status(graph, project.paths, cache=second)
    assert second.full_reads == 0


def test_a_graph_error_blocks_the_build(project, capsys):
    project.write(
        "superRA/03-x/task.md", TASK_X.replace("name: build-x", "name: build-a")
    )
    assert project.run("build", ".") == 1
    assert "task check" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Directory outs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("jobs", ["2"])
@pytest.mark.parametrize("sidecar", [False, True])
def test_path_aliases_share_producer_nodes(project, jobs, sidecar):
    if sidecar:
        _use_a_sidecar(project)
    project.write("superRA/01-a/task.md", project.read("superRA/01-a/task.md").replace(
        "name: build-a", "name: z-producer"
    ))
    project.write("superRA/02-b/task.md", TASK_B.replace(
        "name: build-b", "name: a-consumer"
    ).replace('      - "${OUT}/a.txt"', '      - output/a.txt'))
    assert project.run("build", "02-b#check-b", "--upstream", "-j", jobs) == 0
    assert project.read("output/b.txt") == "hello\nhello\n"
    assert project.status(*CHAIN).ok
    lock = read_lock(project.paths.lock_file)
    assert "${OUT}/a.txt" in lock["a-consumer"].depends_on
    assert "output/a.txt" not in lock["a-consumer"].depends_on
    before = project.run_times()
    assert project.run("build", "02-b#check-b", "--upstream", "-j", jobs) == 0
    assert project.run_times() == before

    project.write("Code/a.sh", "mkdir -p output\necho changed > output/a.txt\n")
    assert project.run("build", "02-b#check-b", "--upstream", "-j", jobs) == 0
    assert project.read("output/b.txt") == "changed\nchanged\n"
    assert project.status(*CHAIN).ok
    if sidecar:
        project.write("output/a.txt", "untracked bytes\n")
        before = project.run_times()
        assert project.status(*CHAIN).ok
        assert project.run("build", "02-b#check-b", "--upstream", "-j", jobs) == 0
        assert project.run_times() == before


@pytest.mark.parametrize("jobs", ["2"])
def test_a_directory_out_orders_its_consumer(dir_project, jobs):
    assert dir_project.run("build", ".", "-j", jobs) == 0
    assert dir_project.read("output/used.txt") == "v1\n"

    dir_project.write(
        "Code/gen.sh", "mkdir -p output/parts\necho v2 > output/parts/a.txt\n"
    )
    assert dir_project.run("build", ".", "-j", jobs) == 0
    assert dir_project.read("output/used.txt") == "v2\n"
    assert dir_project.states() == {"z-gen": "fresh", "a-use": "fresh"}


# ---------------------------------------------------------------------------
# Sidecars, resolved commands, and failure recovery
# ---------------------------------------------------------------------------

def _use_a_sidecar(project) -> None:
    project.write(
        "superRA/01-a/task.md",
        TASK_A.replace(
            '      - "${OUT}/a.txt"\n',
            '      - path: "${OUT}/a.txt"\n        sidecar: "${OUT}/a.txt.sha256"\n',
        ),
    )


MODE_CONFIG = """\
reproduction:
  vars:
    OUT: output
    MODE:
      env: REPRO_TEST_MODE
"""

TASK_MODE = """\
---
title: "Mode"
status: not-started
depends_on: []
---

## Objective

A step whose only variable reaches `cmd`.

## Reproduction

```yaml
steps:
  - name: mode-step
    cmd: sh Code/mode.sh "${MODE}"
    deps:
      - Code/mode.sh
    outs:
      - "${OUT}/mode.txt"
```
"""


def test_a_var_that_only_reaches_cmd_invalidates_the_step(tmp_path, monkeypatch):
    proj = Project(tmp_path / "modeproj")
    proj.write("superRA/config.yaml", MODE_CONFIG)
    proj.write("superRA/01-mode/task.md", TASK_MODE)
    proj.write("Code/mode.sh", 'mkdir -p output\necho "$1" > output/mode.txt\n')

    monkeypatch.setenv("REPRO_TEST_MODE", "fast")
    assert proj.run("build", ".") == 0
    assert proj.read("output/mode.txt") == "fast\n"
    assert proj.states()["mode-step"] == "fresh"

    monkeypatch.setenv("REPRO_TEST_MODE", "slow")
    entry = proj.status().entry("mode-step")
    assert entry.status == "stale"
    assert entry.reason == "the resolved command changed"

    assert proj.run("build", ".") == 0
    assert proj.read("output/mode.txt") == "slow\n"


def test_restoring_the_input_clears_a_failed_step(project):
    project.run("build", *CHAIN)
    original = project.read("Code/b.sh")
    project.write("Code/b.sh", "echo boom >&2\nexit 3\n")
    assert project.run("build", *CHAIN) == 1
    assert project.status(*CHAIN).entry("build-b").status == "failed"

    project.write("Code/b.sh", original)
    assert project.states(*CHAIN)["build-b"] == "fresh"
    assert project.run("status", *CHAIN) == 0

    before = project.run_times()
    assert project.run("build", *CHAIN) == 0
    assert project.run_times() == before


def test_a_failing_step_reports_its_message_without_python_frames(project, capsys):
    project.run("build", "01-a#build-a")
    project.write("Code/b.sh", "exit 3\n")
    capsys.readouterr()
    assert project.run("build", *CHAIN) == 1

    out = capsys.readouterr().out
    assert "StepFailed: step 'build-b' exited 3" in out
    assert f"{STATE_DIRNAME}/logs/build-b.log" in out
    assert "_run_step" not in out
    assert "repro_run.py" not in out

