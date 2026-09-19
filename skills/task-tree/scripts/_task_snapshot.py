"""Filesystem/state adapters for the pure task-dependency snapshot."""
from __future__ import annotations

from _repro import build_graph
from _task_dependencies import task_index
from _task_io import walk_plan


def require_valid(graph):
    errors = [f.to_text() for f in graph.findings if f.severity == "error"]
    if errors or not graph.dependencies.valid:
        raise ValueError("effective dependency graph is invalid:\n" + "\n".join(errors))


def preflight(plan_root, edit):
    """Validate an in-memory proposed tree before any filesystem mutation."""
    root = walk_plan(plan_root)
    edit(root, task_index(root))
    graph = build_graph(plan_root, root=root)
    require_valid(graph)
    return graph


def own_step_states(graph, plan_root):
    """Only internal step prerequisites need artifact state for task readiness."""
    from _repro_state import compute_status, runner_paths
    names = sorted({node[5:] for view in graph.dependencies.boundaries.values()
                    for node in view["nodes"] if node.startswith("step:")
                    and graph.dependencies.tasks[graph.step(node[5:]).task_path].children})
    if not names or not graph.dependencies.valid:
        return {}
    report = compute_status(graph, runner_paths(plan_root.resolve().parent), tier="all", targets=names)
    return {e.step.name: e.status for e in report.entries}


def frontier_rows(graph, plan_root):
    require_valid(graph)
    return graph.dependencies.frontier(own_step_states(graph, plan_root))
