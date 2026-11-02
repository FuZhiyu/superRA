"""Task-level cycles: a new loop at a task boundary is refused, an existing one warns."""
from __future__ import annotations

import json

import pytest

from conftest import _write_task_md
from test_task_dependencies import frontier, graph, run, task
from _task_dependencies import shortest_loop


def snapshot(root):
    return {p: p.read_bytes() for p in root.rglob("task.md")}


def warnings(root):
    check = json.loads(run(root, "task", "check", "--category", "dependency", "--json").stdout)
    return [f["message"] for f in check["findings"] if "task cycle" in f["message"]]


def groups(root, *names):
    for name in names:
        task(root, name)


@pytest.fixture
def looped(tmp_path):
    """Groups `a` and `b` read each other's outputs; their steps do not loop."""
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a1", [], ["a1.txt"]), ("a2", ["b1.txt"], ["a2.txt"])])
    task(root, "b", steps=[("b1", ["a1.txt"], ["b1.txt"])])
    return root


def test_an_existing_file_loop_warns_and_blocks_nothing(looped):
    assert graph(looped).dependencies.valid
    assert len(warnings(looped)) == 1
    message = warnings(looped)[0]
    assert "task cycle at (root): a -> b -> a" in message
    assert "a -> b by a1.txt" in message and "b -> a by b1.txt" in message
    assert "make this boundary one-way" in message
    assert set(frontier(looped)) == {"a", "b"}
    assert run(looped, "repro", "build", ".", "--dry-run").returncode == 0


def test_an_existing_mixed_loop_warns(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", deps=["b"], steps=[("a", [], ["a.txt"])])
    task(root, "b", steps=[("b", ["a.txt"], [])])
    assert "a -> b by a.txt" in warnings(root)[0]
    assert "b -> a by a/task.md depends_on: b" in warnings(root)[0]
    assert graph(root).dependencies.valid


def test_a_depends_on_loop_keeps_its_error_alone(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", deps=["b"])
    task(root, "b", deps=["a"])
    assert warnings(root) == []
    assert not graph(root).dependencies.valid


def test_a_step_loop_keeps_its_error_alone(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("x", ["y.txt"], ["x.txt"]), ("y", ["x.txt"], ["y.txt"])])
    assert warnings(root) == []


def test_a_nested_boundary_reports_its_parent(tmp_path):
    root = tmp_path / "superRA"
    task(root, "g")
    task(root, "g/a", steps=[("a1", [], ["a1.txt"]), ("a2", ["b1.txt"], ["a2.txt"])])
    task(root, "g/b", steps=[("b1", ["a1.txt"], ["b1.txt"])])
    assert len(warnings(root)) == 1
    assert "task cycle at g: a -> b -> a" in warnings(root)[0]


def test_a_loop_through_a_parents_own_step_counts(tmp_path):
    root = tmp_path / "superRA"
    task(root, "p", steps=[("s", ["c1.txt"], ["s.txt"])])
    task(root, "p/c", steps=[("c1", [], ["c1.txt"]), ("c2", ["d.txt"], ["c2.txt"])])
    task(root, "p/d", steps=[("d", ["s.txt"], ["d.txt"])])
    assert "task cycle at p: step s -> d -> c -> step s" in warnings(root)[0]


def test_setup_child_report_in_a_parent_stays_valid(tmp_path):
    root = tmp_path / "superRA"
    task(root, "p", steps=[("setup", [], ["s.txt"]), ("report", ["c.txt"], ["r.txt"])])
    task(root, "p/c", steps=[("c", ["s.txt"], ["c.txt"])])
    assert warnings(root) == []


def test_a_new_member_is_refused(looped):
    task(looped, "c", steps=[("c1", ["a1.txt"], ["c1.txt"])])
    before = snapshot(looped)
    refused = run(looped, "task", "dep", "add", "b", "c")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr
    assert snapshot(looped) == before


def test_merging_two_loops_is_refused(looped):
    task(looped, "c", steps=[("c1", [], ["c1.txt"]), ("c2", ["d1.txt"], ["c2.txt"])])
    task(looped, "d", steps=[("d1", ["c1.txt"], ["d1.txt"]), ("d2", ["c1.txt", "a1.txt"], [])])
    assert len(warnings(looped)) == 2  # d reads a: joined one way, not yet one loop
    refused = run(looped, "task", "dep", "add", "a", "d")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr


def test_an_edge_inside_a_loop_passes(looped):
    added = run(looped, "task", "dep", "add", "b", "a")
    assert added.returncode == 0, added.stderr
    assert len(warnings(looped)) == 1


def test_shrinking_a_loop_passes_and_clears_the_warning(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", deps=["b"], steps=[("a", [], ["a.txt"])])
    task(root, "b", steps=[("b", ["a.txt"], [])])
    removed = run(root, "task", "dep", "remove", "a", "b")
    assert removed.returncode == 0, removed.stderr
    assert warnings(root) == []


def test_an_archived_member_breaks_the_loop_and_returning_it_is_refused(tmp_path):
    root = tmp_path / "superRA"
    task(root, "a", steps=[("a1", [], ["a1.txt"]), ("a2", ["b1.txt"], ["a2.txt"])])
    task(root, "b", status="archived", steps=[("b1", ["a1.txt"], ["b1.txt"])])
    assert warnings(root) == []
    before = snapshot(root)
    refused = run(root, "task", "update", "b", "--status", "not-started")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr
    assert snapshot(root) == before


def test_a_move_that_loops_two_groups_is_refused(tmp_path):
    root = tmp_path / "superRA"
    groups(root, "g1", "g2")
    task(root, "g1/p", steps=[("p", [], ["p.txt"])])
    task(root, "g2/r", steps=[("r", ["p.txt"], ["r.txt"])])
    task(root, "g2/q", steps=[("q", ["r.txt"], [])])
    assert warnings(root) == []
    before = snapshot(root)
    refused = run(root, "task", "move", "g2/q", "g1/q")
    assert refused.returncode == 1 and "task cycle at (root): g2 -> g1 -> g2" in refused.stderr
    assert snapshot(root) == before and (root / "g2/q/task.md").exists()


def test_a_move_that_breaks_a_loop_passes(tmp_path):
    root = tmp_path / "superRA"
    groups(root, "g1", "g2")
    task(root, "g1/p", steps=[("p", [], ["p.txt"])])
    task(root, "g1/q", steps=[("q", ["r.txt"], [])])
    task(root, "g2/r", steps=[("r", ["p.txt"], ["r.txt"])])
    assert len(warnings(root)) == 1
    moved = run(root, "task", "move", "g1/q", "g2/q")
    assert moved.returncode == 0, moved.stderr
    assert warnings(root) == []


@pytest.mark.parametrize("source, target", [("a", "renamed"), ("b", "renamed")])
def test_renaming_a_member_keeps_its_loop(looped, source, target):
    moved = run(looped, "task", "move", source, target)
    assert moved.returncode == 0, moved.stderr
    assert len(warnings(looped)) == 1


def test_renaming_a_group_carries_a_loop_inside_it(tmp_path):
    root = tmp_path / "superRA"
    task(root, "g")
    task(root, "g/a", steps=[("a1", [], ["a1.txt"]), ("a2", ["b1.txt"], ["a2.txt"])])
    task(root, "g/b", steps=[("b1", ["a1.txt"], ["b1.txt"])])
    moved = run(root, "task", "move", "g", "h")
    assert moved.returncode == 0, moved.stderr
    assert "task cycle at h: a -> b -> a" in warnings(root)[0]


def test_a_long_loop_names_one_short_witness():
    pairs = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("b", "a")]
    assert shortest_loop(pairs) == ["a", "b", "a"]


def test_a_large_loop_stays_one_finding(tmp_path):
    root = tmp_path / "superRA"
    names = [f"t{i}" for i in range(8)]
    for index, name in enumerate(names):
        task(root, name, steps=[
            (f"{name}f", [f"{names[index - 1]}f.txt"] if index else [], [f"{name}f.txt"]),
            (f"{name}b", [f"{names[(index + 1) % 8]}b.txt"] if index < 7 else [], [f"{name}b.txt"]),
        ])
    assert len(warnings(root)) == 1
    assert warnings(root)[0].count(" -> ") <= 8


def archived_group(root):
    """`p/c` and `b` read each other's outputs, but `p` rolls up to archived."""
    task(root, "p", status="archived")
    task(root, "p/c", status="archived", steps=[("c1", [], ["c1.txt"]), ("c2", ["b1.txt"], [])])
    task(root, "b", steps=[("b1", ["c1.txt"], ["b1.txt"])])


def test_reactivating_an_archived_group_is_refused(tmp_path):
    root = tmp_path / "superRA"
    archived_group(root)
    assert warnings(root) == []
    before = snapshot(root)
    refused = run(root, "task", "update", "p/c", "--status", "not-started")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr
    assert snapshot(root) == before


def test_a_move_into_an_archived_group_is_refused(tmp_path):
    root = tmp_path / "superRA"
    task(root, "b", steps=[("b1", [], ["b1.txt"]), ("b2", ["d1.txt"], [])])
    task(root, "d", steps=[("d1", ["b1.txt"], ["d1.txt"])])
    task(root, "g", status="archived")
    task(root, "g/old", status="archived")
    refused = run(root, "task", "move", "d", "g/d")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr


def test_archiving_a_group_keeps_its_stored_status_and_returning_it_is_refused(tmp_path):
    root = tmp_path / "superRA"
    task(root, "g", steps=[("g1", [], ["g1.txt"]), ("g2", ["b1.txt"], [])])
    task(root, "g/c")
    task(root, "b", steps=[("b1", ["g1.txt"], ["b1.txt"])])
    assert len(warnings(root)) == 1
    archived = run(root, "task", "update", "g", "--status", "archived")
    assert archived.returncode == 0, archived.stderr
    assert "archived prerequisite 'g'" in archived.stderr
    assert warnings(root) == []
    refused = run(root, "task", "update", "g", "--status", "not-started")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr
    path = root / "g" / "task.md"
    edited = path.read_text().replace("status: archived", "status: not-started")
    assert "task cycle at (root)" in hook_gate()._refusal({path: edited})


def stored_archived_loop(root):
    """Group `g` is stored archived over an active child, which hides its loop with `b`."""
    task(root, "g", status="archived", steps=[("g1", [], ["g1.txt"]), ("g2", ["b1.txt"], [])])
    task(root, "g/c")
    task(root, "b", steps=[("b1", ["g1.txt"], ["b1.txt"])])


def test_a_cascade_elsewhere_passes_a_group_hiding_a_loop(tmp_path):
    root = tmp_path / "superRA"
    stored_archived_loop(root)
    task(root, "k")
    task(root, "k/leaf")
    done = run(root, "task", "status", "cascade", "k", "--status", "archived")
    assert done.returncode == 0, done.stderr
    assert warnings(root) == []


def test_renaming_inside_a_group_hiding_a_loop_passes(tmp_path):
    root = tmp_path / "superRA"
    stored_archived_loop(root)
    moved = run(root, "task", "move", "g/c", "g/c2")
    assert moved.returncode == 0, moved.stderr
    assert warnings(root) == []


def test_a_new_child_that_reactivates_an_archived_group_is_refused(tmp_path):
    root = tmp_path / "superRA"
    task(root, "g", status="archived", steps=[("g1", [], ["g1.txt"]), ("g2", ["b1.txt"], [])])
    task(root, "g/c", status="archived")
    task(root, "b", steps=[("b1", ["g1.txt"], ["b1.txt"])])
    assert warnings(root) == []
    refused = run(root, "task", "create", "g/d", "--title", "D")
    assert refused.returncode == 1 and "task-level cycle" in refused.stderr
    assert not (root / "g" / "d").exists()


def test_a_refusal_names_the_edge_it_adds(looped):
    task(looped, "c", steps=[("c1", ["a2.txt"], [])])
    refused = run(looped, "task", "dep", "add", "b", "c")
    assert "c -> b -> a -> c" in refused.stderr
    assert "(new edge)" in refused.stderr.split("c -> b by")[1].split(";")[0]


def test_a_new_loop_at_a_new_boundary_is_described_through_its_edge(tmp_path):
    root = tmp_path / "superRA"
    groups(root, "p")
    task(root, "p/a", steps=[("a1", [], ["a1.txt"])])
    task(root, "p/b", steps=[("b1", ["a1.txt"], ["b1.txt"])])
    refused = run(root, "task", "dep", "add", "p/a", "b")
    assert refused.returncode == 1
    assert "task cycle at p: b -> a -> b" in refused.stderr
    assert "(new edge)" in refused.stderr


def hook_gate():
    import sys
    from pathlib import Path
    hooks = str(Path(__file__).resolve().parents[3] / "hooks")
    if hooks not in sys.path:
        sys.path.insert(0, hooks)
    import task_cycle_gate
    return task_cycle_gate


def test_an_edit_leaving_the_graph_alone_builds_none(looped, monkeypatch):
    import _task_snapshot
    gate = hook_gate()
    monkeypatch.setattr(_task_snapshot, "edit_adds_cycles", lambda *_: pytest.fail("built a graph"))
    path = looped / "a" / "task.md"
    assert gate._refusal({path: path.read_text().replace("Fixture task.", "Reworded.")}) is None


def test_a_cycle_warning_reaches_a_member_once_per_session(looped):
    import task_hook
    first = task_hook._reconcile(looped, task_path="a", scope=["a"], session_key="s1")
    again = task_hook._reconcile(looped, task_path="a", scope=["a"], session_key="s1")
    fresh = task_hook._reconcile(looped, task_path="b", scope=["b"], session_key="s2")
    assert any("task cycle" in line for line in first)
    assert not any("task cycle" in line for line in again)
    assert any("task cycle" in line for line in fresh)


def test_a_cycle_warning_skips_a_task_outside_the_loop(looped):
    import task_hook
    task(looped, "c")
    feedback = task_hook._reconcile(looped, task_path="c", scope=["c"], session_key="s3")
    assert not any("task cycle" in line for line in feedback)


def test_a_member_nested_in_a_looped_group_hears_of_the_loop(tmp_path):
    import task_hook
    root = tmp_path / "superRA"
    groups(root, "g1", "g2")
    task(root, "g1/p", steps=[("p", [], ["p.txt"])])
    task(root, "g1/q", steps=[("q", ["r.txt"], [])])
    task(root, "g2/r", steps=[("r", ["p.txt"], ["r.txt"])])
    feedback = task_hook._reconcile(root, task_path="g1/q", scope=["g1/q"], session_key="s4")
    assert any("task cycle at (root)" in line for line in feedback)


def stepped_parent(root):
    """`p`'s own step sits in a loop with its child `p/c`."""
    task(root, "p", steps=[("setup", ["c2.txt"], ["s.txt"])])
    task(root, "p/c", steps=[("c1", ["s.txt"], ["c1.txt"]), ("c2", [], ["c2.txt"])])


def test_renaming_a_step_inside_a_loop_passes_the_gate(tmp_path):
    root = tmp_path / "superRA"
    stepped_parent(root)
    path = root / "p" / "task.md"
    assert len(warnings(root)) == 1
    assert hook_gate()._refusal({path: path.read_text().replace("setup", "prep")}) is None


def test_the_task_owning_a_looped_step_hears_of_the_loop(tmp_path):
    import task_hook
    root = tmp_path / "superRA"
    stepped_parent(root)
    feedback = task_hook._reconcile(root, task_path="p", scope=["p"], session_key="s5")
    assert any("task cycle at p" in line for line in feedback)


@pytest.mark.parametrize("damage", [
    lambda text: text.replace('deps: ["b1.txt"]', 'deps: ["b1.txt"'),  # the whole section
    lambda text: text.replace("cmd: echo a2\n", ""),  # one step
])
def test_repairing_a_broken_section_in_a_loop_passes_the_gate(looped, damage):
    path = looped / "a" / "task.md"
    intact = path.read_text()
    broken = damage(intact)
    assert broken != intact
    path.write_text(broken)
    assert warnings(looped) == []
    assert hook_gate()._refusal({path: intact}) is None


def test_the_gate_refuses_reactivating_an_archived_group(tmp_path):
    root = tmp_path / "superRA"
    archived_group(root)
    path = root / "p" / "c" / "task.md"
    edited = path.read_text().replace("status: archived", "status: not-started")
    assert "task cycle at (root)" in hook_gate()._refusal({path: edited})
