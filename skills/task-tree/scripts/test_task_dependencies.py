"""Public command journeys for hierarchical inferred/logical dependencies."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from _repro import build_graph
from _repro_state import spec_hash
from _task_snapshot import frontier_rows
from conftest import _write_task_md

CLI = Path(__file__).with_name("cli.py")


def task(root, path, *, deps=(), status="not-started", steps=()):
    directory = root / path
    directory.mkdir(parents=True, exist_ok=True)
    block = "steps:\n" if steps else ""
    for name, inputs, outputs, *cmd in steps:
        block += f"  - name: {name}\n    cmd: {cmd[0] if cmd else 'echo ' + name}\n    deps: {json.dumps(inputs)}\n    outs: {json.dumps(outputs)}\n"
    _write_task_md(directory / "task.md", path or "Root", status,
                   depends_on=deps, reproduction=block, objective="Fixture task.")


def run(root, *args):
    argv = ["repro", "--root", str(root), *args[1:]] if args[0] == "repro" else [*args, "--root", str(root)]
    return subprocess.run([sys.executable, str(CLI), *argv],
                          capture_output=True, text=True)


def graph(root):
    return build_graph(root, env={})


def frontier(root):
    result = run(root, "task", "frontier", "--json")
    assert result.returncode == 0, result.stderr
    return {row["path"]: row for row in json.loads(result.stdout)}


def read(root, path):
    result = run(root, "task", "read", path, "--json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_file_edge_informs_but_never_gates_readiness(tmp_path):
    root = tmp_path / "superRA"
    task(root, "z-source", steps=[("source", [], ["data.txt"])])
    task(root, "a-consumer", steps=[("consumer", ["data.txt"], ["result.txt"]),
                                    ("second", ["data.txt"], ["second.txt"])])
    rows = frontier(root)
    assert set(rows) == {"a-consumer", "z-source"}
    [item] = rows["a-consumer"]["inputs"]
    assert item["file"] == "data.txt" and item["producer"] == "z-source#source"
    assert (item["state"], item["reason"]) == ("missing", "never built")
    assert item["build"] == "superra repro build a-consumer"
    assert item["consumers"] == ["a-consumer#consumer", "a-consumer#second"]
    human = run(root, "task", "frontier").stdout
    assert ("input data.txt from z-source#source: missing (never built) — not blocking; "
            "decide before relying on it") in human
    assert "by the stale rule" in human and "superra repro build <task> --dry-run" in human
    current = read(root, "a-consumer")
    assert current["dependencies"] == [] and current["readiness"]["ready"] is True
    assert current["readiness"]["inputs"][0]["file"] == "data.txt"
    assert current["dependency_graph"]["edges"][0]["evidence"][0]["via"] == "data.txt"
    dag = run(root, "task", "dag")
    assert "task:z-source" in dag.stdout and "inferred" in dag.stdout


def test_unlink_only_removes_explicit_evidence_and_names_the_file(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["a.txt"])])
    task(root, "b", deps=["a"], steps=[("b", ["a.txt"], ["b.txt"])])
    assert {e["kind"] for e in graph(root).dependencies.edges[0]["evidence"]} == {"logical", "inferred"}
    result = run(root, "task", "dep", "remove", "b", "a")
    assert result.returncode == 0, result.stderr
    assert "File edge remains: b reads a.txt from a." in result.stdout
    assert graph(root).task_edges == [("a", "b")]
    again = run(root, "task", "dep", "remove", "b", "a")
    assert "b reads a.txt from a, a file edge that orders builds but never gates starting work" in again.stderr


def test_depends_on_cycle_blocks_planning_but_not_builds(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", deps=["b"], steps=[("a", [], ["a.txt"])])
    task(root, "b", deps=["a"])
    check = run(root, "task", "check", "--category", "dependency", "--json")
    assert check.returncode == 1
    assert any("depends_on cycle" in f["message"] and "a/task.md depends_on: b" in f["message"]
               for f in json.loads(check.stdout)["findings"])
    assert run(root, "task", "frontier", "--json").returncode == 1
    scoped = run(root, "task", "dag", "a", "--json")
    assert scoped.returncode == 1 and json.loads(scoped.stdout)["valid"] is False
    assert run(root, "repro", "build", "a#a", "--dry-run").returncode == 0


def test_step_cycle_blocks_builds_but_not_planning(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", ["b.txt"], ["a.txt"]), ("b", ["a.txt"], ["b.txt"])])
    assert graph(root).dependencies.valid
    assert set(frontier(root)) == {"a"}
    built = run(root, "repro", "build", "a", "--dry-run")
    assert built.returncode == 1 and "step cycle: a -> b -> a" in built.stderr


def test_loops_from_grouping_file_edges_are_views(tmp_path):
    root = tmp_path / "superRA"
    task(root, "paper", steps=[("tables", [], ["tables.txt"])])
    task(root, "robustness", steps=[("robust", ["tables.txt"], ["robust.txt"])])
    task(root, "paper/estimate", steps=[("estimate", ["robust.txt"], ["estimate.txt"])])
    assert [f.message for f in graph(root).findings if f.severity == "error"] == []
    check = run(root, "task", "check", "--category", "dependency").stdout
    assert "All checks passed" in check or "0 error(s)" in check
    rows = frontier(root)
    assert set(rows) == {"robustness", "paper/estimate"}
    assert [i["file"] for i in rows["paper/estimate"]["inputs"]] == ["robust.txt"]
    assert read(root, "paper")["readiness"]["inputs"][0]["producer"] == "robustness#robust"


def test_depends_on_against_the_file_flow_warns_with_the_file(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["a.txt"])])
    task(root, "b", steps=[("b", ["a.txt"], ["b.txt"])])
    before = {p: p.read_bytes() for p in root.rglob("task.md")}
    result = run(root, "task", "dep", "add", "a", "b")
    assert result.returncode == 0, result.stderr
    assert ("depends_on 'b' runs against the file flow: b reads this task's output a.txt; "
            "not blocking, but best avoided") in result.stderr
    check = run(root, "task", "check", "--category", "dependency")
    assert "0 error(s), 1 warning(s)" in check.stdout and "runs against the file flow" in check.stdout
    assert set(frontier(root)) == {"b"}
    cycle = run(root, "task", "dep", "add", "b", "a")
    assert cycle.returncode == 1 and "depends_on cycle" in cycle.stderr and "b/task.md depends_on: a" in cycle.stderr
    assert (root / "b/task.md").read_bytes() == before[root / "b/task.md"]


def test_child_stays_ready_when_parent_setup_goes_stale(tmp_path):
    root = tmp_path / "superRA"
    (tmp_path / "setup.sh").write_text("printf seed > setup.txt\n")
    task(root, "", steps=[("setup", ["setup.sh"], ["setup.txt"], "sh setup.sh"),
                          ("report", ["child.txt"], ["report.txt"])])
    before = {s.name: spec_hash(s) for s in graph(root).steps}
    task(root, "child", status="in-progress", steps=[("child", ["setup.txt"], ["child.txt"])])
    assert {s.name: spec_hash(s) for s in graph(root).steps if s.name in before} == before
    assert run(root, "repro", "build", ".#setup").returncode == 0
    assert frontier(root)["child"]["inputs"] == []
    human = run(root, "task", "read", "child").stdout
    assert "Inputs Not Fresh" not in human and "1 input(s) fresh" in human
    (tmp_path / "setup.sh").write_text("printf changed > setup.txt\n")
    [item] = frontier(root)["child"]["inputs"]
    assert (item["file"], item["producer"], item["state"]) == ("setup.txt", ".#setup", "stale")
    assert "- input setup.txt from .#setup: stale" in run(root, "task", "read", "child").stdout


def test_archived_producer_with_missing_output_is_reported(tmp_path):
    root = tmp_path / "superRA"
    task(root, "old", status="archived", steps=[("old", [], ["old.txt"])])
    task(root, "m", steps=[("m", ["old.txt"], ["m.txt"])])
    [item] = frontier(root)["m"]["inputs"]
    assert (item["producer"], item["state"], item["build"]) == ("old#old", "missing", None)
    assert "archived producer" in item["reason"]
    dry = run(root, "repro", "build", "m", "--dry-run")
    assert dry.returncode == 1
    plan, _, gate = dry.stdout.partition("so the build would run nothing:")
    assert re.search(r"Would execute 1 step\(s\):\n  m  unknown", plan)
    assert re.search(r"old.txt\s+-\s+not on disk, and no step produces it  \(read by m\)", gate)
    assert "every selected step is fresh" not in dry.stdout
    (tmp_path / "old.txt").write_text("kept")
    assert frontier(root)["m"]["inputs"] == []


def test_unset_variable_blocks_only_the_builds(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["${OUT}/a.txt"])])
    task(root, "b", steps=[("b", [], ["b.txt"], "printf b > b.txt")])
    (root / "config.yaml").write_text("reproduction:\n  vars:\n    OUT:\n      env: NOPE_UNSET_VAR\n")
    assert set(frontier(root)) == {"a", "b"}
    assert "reproduction error" in run(root, "task", "frontier").stderr
    for args in [("task", "create", "c", "--title", "C"), ("task", "dep", "add", "c", "b"),
                 ("task", "move", "c", "d")]:
        result = run(root, *args)
        assert result.returncode == 0, (args, result.stderr)
    status = run(root, "repro", "status", "b")
    assert "graph error(s)" in status.stdout
    assert run(root, "repro", "build", "b").returncode == 0
    broken = run(root, "repro", "build", "a")
    assert broken.returncode == 1 and "unknown variable ${OUT}" in broken.stderr


@pytest.mark.parametrize("error", ["section", "duplicate"])
def test_an_error_blocks_only_the_builds_it_touches(tmp_path, error):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["a.txt"], "printf a > a.txt")])
    task(root, "c", steps=[("c", [], ["c.txt"])])
    if error == "section":
        (root / "c/task.md").write_text((root / "c/task.md").read_text().replace("steps:", "steps: [unclosed"))
    else:
        task(root, "b", steps=[("c", [], ["b.txt"])])
    assert any(f.severity == "error" for f in graph(root).findings)
    built = run(root, "repro", "build", "a")
    assert built.returncode == 0, built.stderr
    assert run(root, "repro", "status", "a").returncode == 0
    assert run(root, "repro", "build", "c").returncode == 1


def test_a_file_from_a_failed_declaration_is_never_used_silently(tmp_path):
    root = tmp_path / "superRA"
    task(root, "p", steps=[("p", [], ["p.txt"])])
    (root / "p/task.md").write_text((root / "p/task.md").read_text().replace("cmd: echo p", "cmd: echo p\n    bogus: 1"))
    task(root, "q", steps=[("q", ["p.txt"], ["q.txt"], "cat p.txt > q.txt")])
    (tmp_path / "p.txt").write_text("stale")
    built = run(root, "repro", "build", "q")
    assert built.returncode == 1
    assert "step 'q' reads p.txt, which task p declares in a step that failed to register" in built.stderr
    task(root, "r")
    (root / "r/task.md").write_text((root / "r/task.md").read_text() + "\n## Reproduction\n\n```yaml\nsteps: [unclosed\n```\n")
    task(root, "s", steps=[("s", ["raw.txt"], ["s.txt"], "cat raw.txt > s.txt")])
    (tmp_path / "raw.txt").write_text("raw")
    built = run(root, "repro", "build", "s")
    assert built.returncode == 0, built.stderr
    assert "Warning: task r: ## Reproduction did not parse" in built.stderr


def test_adding_a_subtask_names_the_tasks_it_blocks(tmp_path):
    root = tmp_path / "superRA"
    task(root, "data", status="approved", steps=[("panel", [], ["panel.txt"])])
    task(root, "analysis", deps=["data"], status="in-progress")
    result = run(root, "task", "create", "data/extra-check", "--title", "Extra check")
    assert result.returncode == 0, result.stderr
    assert "Now blocked: analysis waits on data (not-started)" in result.stdout
    assert set(frontier(root)) == {"data/extra-check"}


def test_archived_subtree_is_boundary_and_warns_transitive_consumers(tmp_path):
    root = tmp_path / "superRA"
    task(root, "old", status="archived")
    task(root, "old/source", steps=[("old", [], ["old.txt"])])
    task(root, "middle", steps=[("middle", ["old.txt"], ["mid.txt"])])
    task(root, "end", steps=[("end", ["mid.txt"], ["end.txt"])])
    current = graph(root)
    assert current.dependencies.valid
    assert {s.name for s in current.steps} == {"middle", "end"}
    assert [s.name for s in current.archived_steps] == ["old"]
    warnings = [f for f in current.findings if "archived prerequisite" in f.message]
    assert {f.task_path for f in warnings} == {"middle", "end"}
    assert next(e for e in current.external_inputs if e.path.logical == "old.txt").exists is False
    (tmp_path / "old.txt").write_text("retained artifact")
    assert next(e for e in graph(root).external_inputs if e.path.logical == "old.txt").exists
    assert all(not r["path"].startswith("old") for r in frontier_rows(graph(root), root))


def test_resolution_once_and_structural_repair_without_shell(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["${OUT}/a.txt"])])
    task(root, "b", steps=[("b", ["output/a.txt"], ["b.txt"])])
    (root / "config.yaml").write_text('reproduction:\n  vars:\n    OUT:\n      shell: "echo probe >> probes; echo output"\n')
    result = run(root, "task", "read", "b", "--json")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "probes").read_text().splitlines() == ["probe"]
    assert json.loads(result.stdout)["readiness"]["inputs"][0]["producer"] == "a#a"
    structural = json.loads(run(root, "task", "tree", "--json").stdout)
    assert structural["dependencies_complete"] is True
    assert [row["effective_depends_on"] for row in structural["children"]] == [[], []]
    assert (tmp_path / "probes").read_text().splitlines() == ["probe"]
    (root / "config.yaml").write_text('reproduction:\n  vars:\n    OUT:\n      shell: "false"\n')
    assert set(frontier(root)) == {"a", "b"}
    assert run(root, "task", "tree", "--json").returncode == 0


def test_parse_failure_does_not_advertise_frontier(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a")
    task(root, "b")
    (root / "a/task.md").write_bytes(b"\xff")
    assert run(root, "task", "frontier", "--json").returncode == 1
    assert run(root, "task", "tree", "--json").returncode == 0


def test_dependency_origins_keep_all_tracking_reasons(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", ["main.jl"], ["a.txt"])])
    (tmp_path / "main.jl").write_text('include("helper.jl")')
    (tmp_path / "helper.jl").write_text('value = 1')
    (root / "config.yaml").write_text('reproduction:\n  env_deps: [helper.jl]\n')
    origins = graph(root).step("a").dependency_origins
    assert origins["main.jl"] == [{"kind": "declared"}]
    assert origins["helper.jl"] == [{"kind": "include", "via": "main.jl"}, {"kind": "environment"}]


def test_dashboard_children_payload_uses_global_snapshot(tmp_path):
    import plan_dashboard as dashboard
    from _task_io import walk_plan
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["a.txt"])])
    task(root, "b", steps=[("b", ["a.txt"], ["b.txt"])])
    task(root, "old", status="archived")
    tree = walk_plan(root)
    current = build_graph(root, root=tree)
    payload = dashboard._children_graph_payload(tree, current)
    assert payload["edges"] == {"b": ["a"]}
    assert {n["path"] for n in payload["children"]} == {"a", "b"}
    assert set(payload) == {"children", "edges"}


def test_archived_names_and_outputs_cannot_suppress_active_producers(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a-archived", status="archived", steps=[("build", [], ["out.txt"])])
    task(root, "z-active", steps=[("build", [], ["out.txt"])])
    task(root, "consumer", steps=[("consume", ["out.txt"], ["result.txt"])])
    current = graph(root)
    assert current.dependencies.valid
    assert current.step("build").task_path == "z-active"
    assert current.producers["out.txt"] == "build"
    assert current.task_edges == [("z-active", "consumer")]
    assert not any("archived prerequisite" in f.message for f in current.findings)
    assert any("archived step name" in f.message for f in current.findings)
    task(root, "another-active", steps=[("build", [], ["different.txt"])])
    current = graph(root)
    assert any("already used" in f.message for f in current.findings if f.severity == "error")
    assert current.dependencies.valid
