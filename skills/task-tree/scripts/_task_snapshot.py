"""Filesystem/state adapters for the pure task-dependency snapshot."""
from __future__ import annotations

import sys

from _repro import build_graph
from _task_dependencies import task_index
from _task_io import walk_plan

INPUT_NOTE = "not blocking; rebuild before relying on it"
CURRENT = {"fresh", "saved"}


def dependency_errors(graph):
    return [f["message"] for f in graph.dependencies.findings if f["severity"] == "error"]


def require_valid(graph):
    if not graph.dependencies.valid:
        raise ValueError("depends_on graph is invalid:\n" + "\n".join(
            f"{f['task_path'] or '(root)'}: {f['message']}" for f in graph.dependencies.findings
            if f["severity"] == "error"))


def preflight(plan_root, edit):
    """Validate an in-memory proposed tree before any filesystem mutation.

    Refuses only `depends_on` errors the edit introduces; `edit_notes` on the
    returned graph names new warnings and the tasks that leave the frontier.
    """
    before = build_graph(plan_root, resolve_vars=False)
    root = walk_plan(plan_root)
    edit(root, task_index(root))
    graph = build_graph(plan_root, root=root, resolve_vars=False)
    old = set(dependency_errors(before))
    new = [m for m in dependency_errors(graph) if m not in old]
    if new:
        raise ValueError("the edit would make the depends_on graph invalid:\n" + "\n".join(new))
    seen = {(f["task_path"], f["message"]) for f in before.dependencies.findings}
    graph.edit_notes = [f"Warning: {f['task_path'] or '(root)'}: {f['message']}"
                        for f in graph.dependencies.findings
                        if f["severity"] == "warning" and (f["task_path"], f["message"]) not in seen]
    after = {row["path"] for row in graph.dependencies.frontier()}
    for row in before.dependencies.frontier():
        path = row["path"]
        if path not in after and path in graph.dependencies.tasks:
            waits = ", ".join(f"{b['path']} ({b['status']})" for b in graph.dependencies.blockers(path))
            if waits:
                graph.edit_notes.append(f"Now blocked: {path} waits on {waits}")
    return graph


def print_edit_notes(graph):
    """Print what a written edit changed: new dependency warnings, newly blocked tasks."""
    for note in graph.edit_notes:
        print(note, file=sys.stderr if note.startswith("Warning:") else sys.stdout)


def step_states(graph, plan_root, names):
    """Status entries for *names* and their producers, from one status pass."""
    from _repro_state import ReproStateError, compute_status, runner_paths
    if not names:
        return {}, None
    targets = [f'{graph.step(n).task_path or "."}#{n}' for n in sorted(names)]
    try:
        report = compute_status(graph, runner_paths(plan_root.resolve().parent), targets=targets, upstream=True)
    except ReproStateError as exc:
        return {}, str(exc)
    return {e.step.name: e for e in report.entries}, None


def task_inputs(graph, path, states, unavailable=None):
    """Each file this task reads from another task's step, with the producer's state."""
    deps = graph.dependencies
    exists = {e.path.logical: e.exists for e in graph.external_inputs}
    rows = {}
    for edge in deps.inputs(path):
        row = {"file": edge["via"], "producer": f"{edge['from'] or '.'}#{edge['producer']}",
               "consumer": f"{edge['to'] or '.'}#{edge['consumer']}"}
        if edge["from"] in deps.archived:
            missing = not exists.get(edge["via"], True)
            row.update(state="missing" if missing else "saved",
                       reason=f"archived producer; {'file is missing' if missing else 'file is present'}",
                       build=None)
        else:
            entry = states.get(edge["producer"])
            row.update(state=entry.status if entry else "unknown",
                       reason=entry.reason if entry else (unavailable or "producer state unavailable"),
                       build=f"superra repro build {edge['to'] or '.'} --upstream")
        rows[row["file"], row["producer"], row["consumer"]] = row
    return [rows[k] for k in sorted(rows)]


def input_producers(graph, paths):
    deps = graph.dependencies
    return {e["producer"] for p in paths for e in deps.inputs(p) if e["from"] not in deps.archived}


def format_input(row):
    line = f"input {row['file']} from {row['producer']}: {row['state']}"
    if row["reason"] and row["reason"] != row["state"]:
        line += f" ({row['reason']})"
    if row["state"] not in CURRENT:
        line += f" — {INPUT_NOTE}" + (f": {row['build']}" if row["build"] else "")
    return line


def frontier_rows(graph, plan_root):
    """Ready tasks, each with the inputs that are not fresh."""
    require_valid(graph)
    rows = graph.dependencies.frontier()
    states, unavailable = step_states(graph, plan_root, input_producers(graph, [r["path"] for r in rows]))
    for row in rows:
        row["inputs"] = [i for i in task_inputs(graph, row["path"], states, unavailable)
                         if i["state"] not in CURRENT]
    return rows
