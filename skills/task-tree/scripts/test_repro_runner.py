"""Tests for the `superra repro` runner (repro_run.py, _repro_state.py).

The stdlib half — hash cache, status classification, tier editing, DAG
rendering, target selection — runs everywhere. The build half needs pytask and
skips without it, so the pytask-free baseline suite still passes.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

import cli
import repro_run
from _repro import build_graph
from _repro_state import (
    STATE_DIRNAME,
    HashCache,
    compute_status,
    directory_dep_nodes,
    read_lock,
    render_dag,
    runner_paths,
    select_steps,
    sidecar_targets,
)

HAS_PYTASK = importlib.util.find_spec("pytask") is not None
needs_pytask = pytest.mark.skipif(not HAS_PYTASK, reason="pytask is not installed")


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
tier: canon
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
tier: canon
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
tier: local
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
tier: canon
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
tier: canon
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

    def status(self, tier: str = "canon"):
        return compute_status(self.graph(), self.paths, tier=tier)

    def states(self, tier: str = "all") -> dict[str, str]:
        return {e.step.name: e.status for e in self.status(tier=tier).reported}

    def run_times(self) -> dict[str, float]:
        """When each step last executed — unchanged means pytask skipped it."""
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

def test_cache_hit_costs_no_full_read(tmp_path):
    target = tmp_path / "data.bin"
    target.write_bytes(b"payload")
    cache_file = tmp_path / "hashes.json"

    first = HashCache(cache_file)
    digest = first.file_hash(target)
    assert first.full_reads == 1
    first.flush()

    second = HashCache(cache_file)
    assert second.file_hash(target) == digest
    assert second.full_reads == 0


def test_cache_rehashes_after_a_content_change(tmp_path):
    target = tmp_path / "data.bin"
    target.write_bytes(b"one")
    cache_file = tmp_path / "hashes.json"
    first = HashCache(cache_file)
    original = first.file_hash(target)
    first.flush()

    target.write_bytes(b"two")
    second = HashCache(cache_file)
    assert second.file_hash(target) != original
    assert second.full_reads == 1


def test_directory_state_covers_every_file_inside(tmp_path):
    directory = tmp_path / "tree"
    (directory / "nested").mkdir(parents=True)
    (directory / "nested" / "a.txt").write_text("a")
    cache = HashCache()
    before = cache.path_state(directory)

    (directory / "nested" / "b.txt").write_text("b")
    assert HashCache().path_state(directory) != before


def test_missing_path_has_no_state(tmp_path):
    assert HashCache().path_state(tmp_path / "absent") is None


# ---------------------------------------------------------------------------
# Status without a build
# ---------------------------------------------------------------------------

def test_unbuilt_steps_report_never_built(project):
    report = project.status()
    assert {e.step.name for e in report.reported} == {"build-a", "build-b", "check-b"}
    assert all(e.status == "missing" for e in report.reported)
    assert all(e.reason == "never built" for e in report.reported)
    assert report.ok is False


def test_missing_external_input_marks_the_step_external(project):
    project.write("Code/a.sh", "cp Data/raw.csv output/a.txt\n")
    project.write(
        "superRA/01-a/task.md", TASK_A.replace("      - Code/a.sh", "      - Data/raw.csv")
    )
    entry = project.status().entry("build-a")
    assert entry.status == "external"
    assert "Data/raw.csv" in entry.reason


def test_a_tree_with_no_steps_leaves_no_state_behind(project, tmp_path):
    bare = Project(tmp_path / "bare")
    bare.write(
        "superRA/01-a/task.md",
        '---\ntitle: "A"\nstatus: not-started\ndepends_on: []\n---\n\n## Objective\n\nNo steps.\n',
    )
    assert bare.run("status") == 0
    assert not (bare.root / STATE_DIRNAME).exists()
    assert not (bare.root / ".gitignore").exists()


def test_status_reports_only_the_requested_tier(project):
    assert set(project.states("canon")) == {"build-a", "build-b", "check-b"}
    assert set(project.states("local")) == {"build-x"}
    assert set(project.states("all")) == {"build-a", "build-b", "check-b", "build-x"}


# ---------------------------------------------------------------------------
# Target selection
# ---------------------------------------------------------------------------

def test_selection_defaults_to_the_tier(project):
    names, unknown = select_steps(project.graph(), [], "canon")
    assert names == ["build-a", "build-b", "check-b"]
    assert unknown == []


def test_a_step_target_pulls_its_ancestors(project):
    names, _ = select_steps(project.graph(), ["check-b"], "canon")
    assert set(names) == {"build-a", "build-b", "check-b"}


def test_a_task_path_target_selects_every_step_it_owns(project):
    names, _ = select_steps(project.graph(), ["02-b"], "canon")
    assert set(names) == {"build-a", "build-b", "check-b"}


def test_an_explicit_target_overrides_the_tier(project):
    names, _ = select_steps(project.graph(), ["build-x"], "canon")
    assert names == ["build-x"]


def test_an_unknown_target_is_reported(project):
    names, unknown = select_steps(project.graph(), ["build-z"], "canon")
    assert names == []
    assert unknown == ["build-z"]


# ---------------------------------------------------------------------------
# Tier command
# ---------------------------------------------------------------------------

def test_tier_replaces_the_existing_key(project):
    assert project.run("tier", "01-a", "local") == 0
    assert "tier: local" in project.read("superRA/01-a/task.md")
    assert project.graph().tiers["01-a"] == "local"


def test_tier_inserts_the_key_when_absent(project):
    project.write("superRA/01-a/task.md", TASK_A.replace("tier: canon\n", ""))
    assert project.run("tier", "01-a", "canon") == 0
    assert project.graph().tiers["01-a"] == "canon"


def test_tier_rejects_a_task_without_a_reproduction_section(project):
    project.write(
        "superRA/04-none/task.md",
        "---\ntitle: \"None\"\nstatus: not-started\ndepends_on: []\n---\n\n## Objective\n\nNo steps.\n",
    )
    assert project.run("tier", "04-none", "canon") == 1


# ---------------------------------------------------------------------------
# DAG rendering
# ---------------------------------------------------------------------------

def test_dag_text_lists_steps_and_edges(project):
    text = render_dag(project.graph())
    assert "build-a" in text
    assert "build-a --> build-b" in text


def test_dag_mermaid_renders_a_flowchart(project):
    text = render_dag(project.graph(), mermaid=True)
    assert text.startswith("graph LR")
    assert 'build-a["build-a"]:::canon' in text
    assert "build-a -->|a.txt| build-b" in text


def test_cli_routes_repro_to_the_runner(project, capsys):
    cli.main(["repro", "--plan-root", str(project.plan_root), "dag", "--mermaid"])
    assert capsys.readouterr().out.startswith("graph LR")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

@needs_pytask
def test_first_build_runs_every_step(project):
    assert project.run("build") == 0
    assert project.read("output/a.txt") == "hello\n"
    assert project.read("output/b.txt") == "hello\nhello\n"
    assert (project.root / STATE_DIRNAME / "stamps" / "check-b.stamp").is_file()
    assert project.states("canon") == {
        "build-a": "fresh",
        "build-b": "fresh",
        "check-b": "fresh",
    }


@needs_pytask
def test_state_directory_is_created_and_gitignored(project):
    project.run("build")
    assert (project.root / STATE_DIRNAME / "logs" / "build-a.log").is_file()
    assert f"{STATE_DIRNAME}/" in project.read(".gitignore").split()


@needs_pytask
def test_lock_ids_stay_in_logical_form(project):
    project.run("build")
    lock = read_lock(project.paths.lock_file)
    assert "${OUT}/a.txt" in lock["build-a"].produces
    assert "output/a.txt" not in lock["build-a"].produces
    assert "build-a::spec" in lock["build-a"].depends_on


@needs_pytask
def test_second_build_is_a_no_op(project):
    project.run("build")
    before = project.run_times()
    assert project.run("build") == 0
    assert project.run_times() == before


@needs_pytask
def test_touching_a_dep_with_identical_bytes_is_a_no_op(project):
    project.run("build")
    before = project.run_times()
    (project.root / "Code" / "a.sh").touch()
    assert project.states("canon")["build-a"] == "fresh"
    assert project.run("build") == 0
    assert project.run_times() == before


@needs_pytask
def test_a_dep_edit_reruns_exactly_the_affected_chain(project):
    project.run("build", "--tier", "all")
    before = project.run_times()
    project.write("Code/a.sh", "mkdir -p output\necho goodbye > output/a.txt\n")

    states = project.states("all")
    assert states["build-a"] == "stale"
    assert states["build-b"] == "stale"
    assert states["build-x"] == "fresh"

    assert project.run("build", "--tier", "all") == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert after["build-b"] != before["build-b"]
    assert after["check-b"] != before["check-b"]
    assert after["build-x"] == before["build-x"]


@needs_pytask
def test_regenerating_identical_bytes_does_not_cascade(project):
    project.run("build")
    before = project.run_times()
    project.write("Code/a.sh", "mkdir -p output\n# no behaviour change\necho hello > output/a.txt\n")

    assert project.run("build") == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert after["build-b"] == before["build-b"]
    assert after["check-b"] == before["check-b"]


@needs_pytask
def test_deleting_an_out_reports_missing_and_rebuilds_it(project):
    project.run("build")
    (project.root / "output" / "b.txt").unlink()

    entry = project.status().entry("build-b")
    assert entry.status == "missing"
    assert "${OUT}/b.txt" in entry.reason

    assert project.run("build") == 0
    assert project.read("output/b.txt") == "hello\nhello\n"
    assert project.states("canon")["build-b"] == "fresh"


@needs_pytask
def test_a_target_pulls_its_stale_ancestors(project):
    assert project.run("build", "check-b") == 0
    assert project.read("output/b.txt") == "hello\nhello\n"

    project.write("Code/a.sh", "mkdir -p output\necho other > output/a.txt\n")
    before = project.run_times()
    assert project.run("build", "build-b") == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert project.read("output/a.txt") == "other\n"


@needs_pytask
def test_a_check_step_reruns_when_its_deps_change(project):
    project.run("build")
    before = project.run_times()
    project.write("Code/a.sh", "mkdir -p output\necho changed > output/a.txt\n")
    project.run("build")
    assert project.run_times()["check-b"] != before["check-b"]


@needs_pytask
def test_a_failing_step_stops_its_descendants_and_exits_non_zero(project):
    project.run("build")
    project.write("Code/b.sh", "echo boom >&2\nexit 3\n")

    assert project.run("build") == 1
    entry = project.status().entry("build-b")
    assert entry.status == "failed"
    assert f"{STATE_DIRNAME}/logs/build-b.log" in entry.reason
    assert "boom" in project.read(f"{STATE_DIRNAME}/logs/build-b.log")
    assert project.states("canon")["check-b"] == "stale"


@needs_pytask
def test_force_reruns_a_fresh_step(project):
    project.run("build")
    before = project.run_times()
    assert project.run("build", "--force") == 0
    assert project.run_times()["build-a"] != before["build-a"]


@needs_pytask
def test_dry_run_changes_nothing(project):
    assert project.run("build", "--dry-run") == 0
    assert not (project.root / "output").exists()
    assert not project.paths.lock_file.exists()


@needs_pytask
def test_parallel_jobs_build_the_whole_graph(project):
    assert project.run("build", "--tier", "all", "-j", "2") == 0
    assert project.states("all") == {
        "build-a": "fresh",
        "build-b": "fresh",
        "check-b": "fresh",
        "build-x": "fresh",
    }


@needs_pytask
def test_a_params_change_reruns_only_that_step(project):
    project.run("build")
    before = project.run_times()
    project.write(
        "superRA/01-a/task.md",
        TASK_A.replace(
            '    outs:\n      - "${OUT}/a.txt"',
            '    params:\n      seed: 7\n    outs:\n      - "${OUT}/a.txt"',
        ),
    )
    entry = project.status().entry("build-a")
    assert entry.status == "stale"
    assert entry.reason == "the step definition changed"

    assert project.run("build") == 0
    after = project.run_times()
    assert after["build-a"] != before["build-a"]
    assert after["build-b"] == before["build-b"]


@needs_pytask
def test_a_sidecar_tracked_out_is_hashed_through_its_sidecar(project):
    project.write(
        "superRA/01-a/task.md",
        TASK_A.replace(
            '      - "${OUT}/a.txt"\n',
            '      - path: "${OUT}/a.txt"\n        sidecar: "${OUT}/a.txt.sha256"\n',
        ),
    )
    assert project.run("build", "build-a") == 0
    sidecar = project.read("output/a.txt.sha256")
    assert "${OUT}/a.txt" in sidecar

    lock = read_lock(project.paths.lock_file)
    assert lock["build-a"].produces["${OUT}/a.txt"] == HashCache().file_hash(
        project.root / "output" / "a.txt.sha256"
    )

    # A hand-edit of the out goes unnoticed until the sidecar is rewritten.
    project.write("output/a.txt", "tampered\n")
    assert project.states("canon")["build-a"] == "fresh"


@needs_pytask
def test_status_json_matches_the_documented_shape(project, capsys):
    project.run("build")
    capsys.readouterr()
    assert project.run("status", "--json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is True
    assert payload["tier"] == "canon"
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
        "name", "task", "tier", "kind", "cmd", "status", "reason", "changes",
        "duration", "last_run", "log", "deps", "outs",
    }
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


@needs_pytask
def test_status_json_reports_a_stale_step_and_exits_one(project, capsys):
    project.run("build")
    project.write("Code/b.sh", "cat output/a.txt > output/b.txt\n")
    capsys.readouterr()
    assert project.run("status", "--json") == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["ok"] is False
    step = next(s for s in payload["steps"] if s["name"] == "build-b")
    assert step["status"] == "stale"
    assert step["changes"] == [
        {"node": "Code/b.sh", "kind": "dependency", "change": "changed"}
    ]


@needs_pytask
def test_explain_names_the_changed_dependency(project, capsys):
    project.run("build")
    project.write("Code/b.sh", "cat output/a.txt > output/b.txt\n")
    capsys.readouterr()
    assert project.run("explain", "build-b") == 0
    out = capsys.readouterr().out

    assert "build-b  [stale]" in out
    assert "dependency: Code/b.sh (changed)" in out
    assert "build-a: fresh" in out


@needs_pytask
def test_explain_rejects_an_unknown_step(project):
    assert project.run("explain", "build-z") == 1


@needs_pytask
def test_a_second_status_reads_no_file_content(project):
    project.run("build")
    graph = project.graph()
    project.paths.cache_file.unlink()  # the build populated it; start cold

    first = HashCache(project.paths.cache_file)
    compute_status(graph, project.paths, tier="all", cache=first)
    assert first.full_reads > 0

    second = HashCache(project.paths.cache_file)
    compute_status(graph, project.paths, tier="all", cache=second)
    assert second.full_reads == 0


@needs_pytask
def test_a_graph_error_blocks_the_build(project, capsys):
    project.write(
        "superRA/03-x/task.md", TASK_X.replace("name: build-x", "name: build-a")
    )
    assert project.run("build", "--tier", "all") == 1
    assert "task check" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Directory outs
# ---------------------------------------------------------------------------

def test_a_directory_out_becomes_a_dep_node_of_its_consumer(dir_project):
    graph = dir_project.graph()
    consumer = graph.step("a-use")
    extra = directory_dep_nodes(graph, consumer, sidecar_targets(graph))
    assert [node[0] for node in extra] == ["${OUT}/parts"]
    assert directory_dep_nodes(graph, graph.step("z-gen"), {}) == []


def test_the_generated_task_carries_the_directory_edge(dir_project):
    graph = dir_project.graph()
    tasks = repro_run.make_tasks(
        graph, ["z-gen", "a-use"], dir_project.paths, HashCache()
    )
    consumer = next(task for task in tasks if task.name == "a-use")
    assert "${OUT}/parts" in {node.name for node in consumer.depends_on["deps"]}


@needs_pytask
@pytest.mark.parametrize("jobs", ["1", "2"])
def test_a_directory_out_orders_its_consumer(dir_project, jobs):
    assert dir_project.run("build", "-j", jobs) == 0
    assert dir_project.read("output/used.txt") == "v1\n"

    dir_project.write(
        "Code/gen.sh", "mkdir -p output/parts\necho v2 > output/parts/a.txt\n"
    )
    assert dir_project.run("build", "-j", jobs) == 0
    assert dir_project.read("output/used.txt") == "v2\n"
    assert dir_project.states("canon") == {"z-gen": "fresh", "a-use": "fresh"}


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


@needs_pytask
def test_deleting_a_sidecar_tracked_out_reports_missing_and_rebuilds_it(project):
    _use_a_sidecar(project)
    assert project.run("build", "build-a") == 0
    (project.root / "output" / "a.txt").unlink()

    entry = project.status().entry("build-a")
    assert entry.status == "missing"
    assert "${OUT}/a.txt" in entry.reason

    assert project.run("build", "build-a") == 0
    assert project.read("output/a.txt") == "hello\n"
    assert project.states("canon")["build-a"] == "fresh"


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
tier: canon
steps:
  - name: mode-step
    cmd: sh Code/mode.sh "${MODE}"
    deps:
      - Code/mode.sh
    outs:
      - "${OUT}/mode.txt"
```
"""


@needs_pytask
def test_a_var_that_only_reaches_cmd_invalidates_the_step(tmp_path, monkeypatch):
    proj = Project(tmp_path / "modeproj")
    proj.write("superRA/config.yaml", MODE_CONFIG)
    proj.write("superRA/01-mode/task.md", TASK_MODE)
    proj.write("Code/mode.sh", 'mkdir -p output\necho "$1" > output/mode.txt\n')

    monkeypatch.setenv("REPRO_TEST_MODE", "fast")
    assert proj.run("build") == 0
    assert proj.read("output/mode.txt") == "fast\n"
    assert proj.states("canon")["mode-step"] == "fresh"

    monkeypatch.setenv("REPRO_TEST_MODE", "slow")
    entry = proj.status().entry("mode-step")
    assert entry.status == "stale"
    assert entry.reason == "the step definition changed"

    assert proj.run("build") == 0
    assert proj.read("output/mode.txt") == "slow\n"


@needs_pytask
def test_restoring_the_input_clears_a_failed_step(project):
    project.run("build")
    original = project.read("Code/b.sh")
    project.write("Code/b.sh", "echo boom >&2\nexit 3\n")
    assert project.run("build") == 1
    assert project.status().entry("build-b").status == "failed"

    project.write("Code/b.sh", original)
    assert project.states("canon")["build-b"] == "fresh"
    assert project.run("status") == 0

    before = project.run_times()
    assert project.run("build") == 0
    assert project.run_times() == before


@needs_pytask
def test_a_failing_step_reports_its_message_without_python_frames(project, capsys):
    project.run("build", "build-a")
    project.write("Code/b.sh", "exit 3\n")
    capsys.readouterr()
    assert project.run("build") == 1

    out = capsys.readouterr().out
    assert "StepFailed: step 'build-b' exited 3" in out
    assert f"{STATE_DIRNAME}/logs/build-b.log" in out
    assert "_run_step" not in out
    assert "repro_run.py" not in out


def test_the_reexec_message_names_the_missing_piece(monkeypatch, capsys):
    monkeypatch.setattr(repro_run.shutil, "which", lambda _name: None)
    monkeypatch.delenv(repro_run.REEXEC_ENV, raising=False)

    assert repro_run._reexec([], "build") == 1
    assert "needs pytask" in capsys.readouterr().err

    assert repro_run._reexec([], "status") == 1
    err = capsys.readouterr().err
    assert "`superra repro status` needs Python 3.11+ (tomllib)" in err
    assert "pytask" not in err
