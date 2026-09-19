"""Public command journeys for hierarchical inferred/logical dependencies."""
from __future__ import annotations

import json
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
    for name, inputs, outputs in steps:
        block += f"  - name: {name}\n    cmd: echo {name}\n    deps: {json.dumps(inputs)}\n    outs: {json.dumps(outputs)}\n"
    _write_task_md(directory / "task.md", path or "Root", status,
                   depends_on=deps, reproduction=block, objective="Fixture task.")


def run(root, *args):
    argv = ["repro", "--root", str(root), *args[1:]] if args[0] == "repro" else [*args, "--root", str(root)]
    return subprocess.run([sys.executable, str(CLI), *argv],
                          capture_output=True, text=True)


def graph(root):
    return build_graph(root, env={})


def test_public_frontier_read_and_dag_share_inferred_edge(tmp_path):
    root = tmp_path / "superRA"
    task(root, "z-source", steps=[("source", [], ["data.txt"])])
    task(root, "a-consumer", steps=[("consumer", ["data.txt"], ["result.txt"])])
    result = run(root, "task", "frontier", "--json")
    assert result.returncode == 0, result.stderr
    assert [r["path"] for r in json.loads(result.stdout)] == ["z-source"]
    read = json.loads(run(root, "task", "read", "a-consumer", "--json").stdout)
    assert [d["path"] for d in read["dependencies"]] == ["z-source"]
    assert read["dependency_graph"]["edges"][0]["evidence"][0]["via"] == "data.txt"
    dag = run(root, "task", "dag")
    assert "task:z-source" in dag.stdout and "inferred" in dag.stdout
    task(root, "z-source", status="implemented", steps=[("source", [], ["data.txt"])])
    assert [r["path"] for r in json.loads(run(root, "task", "frontier", "--json").stdout)] == ["a-consumer", "z-source"]


def test_unlink_only_removes_explicit_evidence(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["a.txt"])])
    task(root, "b", deps=["a"], steps=[("b", ["a.txt"], ["b.txt"])])
    assert {e["kind"] for e in graph(root).dependencies.edges[0]["evidence"]} == {"logical", "inferred"}
    result = run(root, "task", "dep", "remove", "b", "a")
    assert result.returncode == 0, result.stderr
    assert "Inferred dependency remains" in result.stdout
    assert graph(root).task_edges == [("a", "b")]


@pytest.mark.parametrize("kind", ["mixed", "grouping", "step", "nested"])
def test_cycles_cannot_be_hidden_by_frontier_or_scoped_build(tmp_path, kind):
    root = tmp_path / "superRA"
    if kind == "mixed":
        task(root, "a", deps=["b"], steps=[("a", [], ["a.txt"])])
        task(root, "b", steps=[("b", ["a.txt"], ["b.txt"])])
    elif kind == "step":
        task(root, "a", steps=[("a", ["b.txt"], ["a.txt"]), ("b", ["a.txt"], ["b.txt"])])
    elif kind == "grouping":
        task(root, "a", steps=[("a1", [], ["a.txt"]), ("a2", ["b.txt"], ["a2.txt"])])
        task(root, "b", steps=[("b1", ["a.txt"], ["b1.txt"]), ("b2", [], ["b.txt"])])
    else:
        task(root, "a", deps=["b"])
        task(root, "b")
        task(root, "a/x", steps=[("a", [], ["a.txt"])])
        task(root, "b/y", steps=[("b", ["a.txt"], ["b.txt"])])
    check = run(root, "task", "check", "--category", "dependency", "--json")
    assert check.returncode == 1
    assert any("cycle" in f["message"] for f in json.loads(check.stdout)["findings"])
    assert run(root, "task", "frontier", "--json").returncode == 1
    scoped = run(root, "task", "dag", "a", "--json")
    assert scoped.returncode == 1
    assert json.loads(scoped.stdout)["valid"] is False
    # The runner's build precondition consumes Graph.findings even for a target.
    from _task_snapshot import require_valid
    with pytest.raises(ValueError, match="cycle"):
        require_valid(graph(root))
    import importlib.util
    if importlib.util.find_spec("pytask"):
        built = run(root, "repro", "build", "a", "--dry-run")
        assert built.returncode == 1 and "cycle" in built.stderr


def test_parent_setup_child_report_keeps_identity_and_exposes_own_work(tmp_path):
    root = tmp_path / "superRA"
    task(root, "", steps=[("setup", [], ["setup.txt"]), ("report", ["child.txt"], ["report.txt"])])
    before = {s.name: spec_hash(s) for s in graph(root).steps}
    task(root, "child", steps=[("child", ["setup.txt"], ["child.txt"])])
    current = graph(root)
    assert current.dependencies.valid
    assert {s.name: spec_hash(s) for s in current.steps if s.name in before} == before
    assert current.task_edges == []
    result = run(root, "task", "frontier", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [{"path": "", "title": "Root", "status": "not-started", "kind": "own-work", "steps": ["setup"]}]
    rows = current.dependencies.frontier({"setup": "fresh", "child": "missing", "report": "missing"})
    assert [r["path"] for r in rows] == ["child"]
    read = json.loads(run(root, "task", "read", "child", "--json").stdout)
    assert read["readiness"]["blockers"][0]["states"] == {"step:setup": "missing"}
    assert "step:setup (missing)" in run(root, "task", "read", "child").stdout
    rows = current.dependencies.frontier({"setup": "fresh", "child": "fresh", "report": "missing"})
    assert next(r for r in rows if r.get("kind") == "own-work")["steps"] == ["report"]


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


def test_link_cycle_preflight_changes_no_files(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["a.txt"])])
    task(root, "b", steps=[("b", ["a.txt"], ["b.txt"])])
    before = {p: p.read_bytes() for p in root.rglob("task.md")}
    result = run(root, "task", "dep", "add", "a", "b")
    assert result.returncode == 1 and "cycle" in result.stderr
    assert before == {p: p.read_bytes() for p in root.rglob("task.md")}


def test_move_preflight_rejects_new_grouping_cycle_atomically(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a")
    task(root, "b")
    task(root, "a/start", steps=[("start", [], ["start.txt"])])
    task(root, "b/middle", steps=[("middle", ["start.txt"], ["middle.txt"])])
    task(root, "b/end", steps=[("end", ["middle.txt"], ["end.txt"])])
    assert graph(root).dependencies.valid
    before = {p: p.read_bytes() for p in root.rglob("task.md")}
    result = run(root, "task", "move", "b/end", "a/end")
    assert result.returncode == 1 and "cycle" in result.stderr
    assert before == {p: p.read_bytes() for p in root.rglob("task.md")}


def test_resolution_once_and_structural_repair_without_shell(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a", [], ["${OUT}/a.txt"])])
    task(root, "b", steps=[("b", ["output/a.txt"], ["b.txt"])])
    (root / "config.yaml").write_text('reproduction:\n  vars:\n    OUT:\n      shell: "echo probe >> probes; echo output"\n')
    result = run(root, "task", "read", "b", "--json")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "probes").read_text().splitlines() == ["probe"]
    assert json.loads(result.stdout)["dependencies"][0]["path"] == "a"
    structural = json.loads(run(root, "task", "tree", "--json").stdout)
    assert structural["dependencies_complete"] is False
    assert structural["effective_depends_on"] is None
    assert all(row["effective_depends_on"] is None for row in structural["children"])
    assert (tmp_path / "probes").read_text().splitlines() == ["probe"]
    (root / "config.yaml").write_text('reproduction:\n  vars:\n    OUT:\n      shell: "false"\n')
    assert run(root, "task", "frontier", "--json").returncode == 1
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


def test_archived_logical_cycle_does_not_block_and_self_link_is_rejected(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", status="archived", deps=["b"])
    task(root, "b", deps=["a"])
    assert graph(root).dependencies.valid
    result = run(root, "task", "frontier", "--json")
    assert [row["path"] for row in json.loads(result.stdout)] == ["b"]
    result = run(root, "task", "dep", "add", "b", "b")
    assert result.returncode == 1 and "cycle" in result.stderr


def test_resume_archived_cycle_is_preflighted(tmp_path):
    from task_update import update_task
    root = tmp_path / "superRA"
    task(root, "a", status="archived", deps=["b"])
    task(root, "b", deps=["a"])
    before = (root / "a/task.md").read_bytes()
    with pytest.raises(SystemExit):
        update_task(root, "a", status="not-started")
    assert (root / "a/task.md").read_bytes() == before


def test_dashboard_boundary_payload_uses_global_snapshot(tmp_path):
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
    assert payload["valid"] is True
    assert payload["boundary"]["edges"][0]["evidence"][0]["via"] == "a.txt"


def test_create_preflight_can_repair_dangling_edge_but_rejects_cycle(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", deps=["b"])
    result = run(root, "task", "create", "b", "--title", "B", "--depends-on", "a")
    assert result.returncode == 1 and "cycle" in result.stderr
    assert not (root / "b").exists()
    result = run(root, "task", "create", "b", "--title", "B")
    assert result.returncode == 0, result.stderr
    assert graph(root).dependencies.valid


def test_logical_prerequisites_do_not_expand_replay_and_archival_cannot_be_targeted(tmp_path):
    from _repro_state import select_steps
    root = tmp_path / "superRA"
    task(root, "logical", steps=[("logical", [], ["logical.txt"])])
    task(root, "target", deps=["logical"], steps=[("target", [], ["target.txt"])])
    task(root, "old", status="archived", steps=[("old", [], ["old.txt"])])
    current = graph(root)
    assert current.dependencies.prerequisites("target") == ["logical"]
    assert select_steps(current, ["target"], "all") == (["target"], [])
    assert select_steps(current, ["old"], "all") == ([], ["old"])
    assert "old" not in select_steps(current, [], "all")[0]


def test_archived_logical_warning_reaches_inheriting_descendants(tmp_path):
    root = tmp_path / "superRA"
    task(root, "old", status="archived")
    task(root, "group", deps=["old"])
    task(root, "group/child", steps=[("child", [], ["child.txt"])])
    task(root, "end", steps=[("end", ["child.txt"], ["end.txt"])])
    warnings = [f for f in graph(root).findings if "archived prerequisite" in f.message]
    assert {f.task_path for f in warnings} == {"group", "group/child", "end"}


def test_built_parent_keeps_freshness_when_child_is_added(tmp_path):
    import importlib.util
    if not importlib.util.find_spec("pytask"):
        pytest.skip("pytask is required for the execution journey")
    root = tmp_path / "superRA"
    task(root, "", steps=[("setup", [], ["setup.txt"])])
    parent = root / "task.md"
    parent.write_text(parent.read_text().replace("cmd: echo setup", "cmd: printf seed > setup.txt"))
    first = run(root, "repro", "build", "setup")
    assert first.returncode == 0, first.stdout + first.stderr
    from _repro_state import read_run_record, runner_paths
    paths = runner_paths(tmp_path)
    setup_record = read_run_record(paths, "setup")
    task(root, "", steps=[("setup", [], ["setup.txt"]), ("report", ["child.txt"], ["report.txt"])])
    parent.write_text(parent.read_text().replace("cmd: echo setup", "cmd: printf seed > setup.txt").replace("cmd: echo report", "cmd: cat child.txt > report.txt"))
    task(root, "child", steps=[("child", ["setup.txt"], ["child.txt"])])
    child = root / "child/task.md"
    child.write_text(child.read_text().replace("cmd: echo child", "cmd: cat setup.txt > child.txt"))
    status = run(root, "repro", "status", "setup", "--json")
    assert status.returncode == 0, status.stderr
    assert json.loads(status.stdout)["steps"][0]["status"] == "fresh"
    assert [row["path"] for row in json.loads(run(root, "task", "frontier", "--json").stdout)] == ["child"]
    built = run(root, "repro", "build", "report")
    assert built.returncode == 0, built.stdout + built.stderr
    assert (tmp_path / "report.txt").read_text() == "seed"
    assert read_run_record(paths, "setup") == setup_record


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
    assert not graph(root).dependencies.valid
