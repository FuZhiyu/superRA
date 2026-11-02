"""Pure composition of logical task prerequisites and file-derived step edges."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _task_io import Task
    from _repro import Step

SATISFIED = {"implemented", "approved", "revise"}
ACTIONABLE = {"not-started", "in-progress", "implemented", "revise"}
CYCLE_REMEDY = "make this boundary one-way: move the step, or split the shared producer into its own task"


def task_index(root: Task) -> dict[str, Task]:
    result = {root.path: root}
    for child in root.children:
        result.update(task_index(child))
    return result


def within(path: str, parent: str) -> bool:
    return not parent or path == parent or path.startswith(parent + "/")


def archived_paths(root: Task) -> set[str]:
    tasks = task_index(root)
    parked = [p for p, t in tasks.items() if t.status == "archived"]
    return {p for p in tasks if any(within(p, a) for a in parked)}


def cycle_path(edges) -> list[str] | None:
    adjacency = {}
    for source, target in edges:
        adjacency.setdefault(source, set()).add(target)
    seen, visiting, chain = set(), set(), []

    def visit(node):
        if node in visiting:
            return chain[chain.index(node):] + [node]
        if node in seen:
            return None
        visiting.add(node)
        chain.append(node)
        for target in sorted(adjacency.get(node, ())):
            cycle = visit(target)
            if cycle:
                return cycle
        chain.pop()
        visiting.remove(node)
        seen.add(node)
        return None

    for node in sorted(adjacency):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def cyclic_components(edges) -> list[set[str]]:
    """Strongly connected components that hold a cycle, in a stable order."""
    adjacency: dict[str, list[str]] = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, [])
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[set[str]] = []

    def visit(node: str) -> None:
        index[node] = low[node] = len(index)
        stack.append(node)
        on_stack.add(node)
        for target in sorted(adjacency[node]):
            if target not in index:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], index[target])
        if low[node] == index[node]:
            component = set()
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.add(member)
                if member == node:
                    break
            if len(component) > 1 or node in adjacency[node]:
                components.append(component)

    for node in sorted(adjacency):
        if node not in index:
            visit(node)
    return sorted(components, key=min)


def shortest_loop(pairs) -> list[str]:
    """The shortest loop through *pairs*, first by node name on a tie."""
    adjacency = {}
    for source, target in sorted(pairs):
        adjacency.setdefault(source, []).append(target)
    best = []
    for start in sorted(adjacency):
        paths, seen = deque([[start]]), {start}
        while paths:
            path = paths.popleft()
            for target in adjacency.get(path[-1], ()):
                if target == start:
                    if not best or len(path) + 1 < len(best):
                        best = [*path, start]
                    paths.clear()
                    break
                if target not in seen:
                    seen.add(target)
                    paths.append([*path, target])
    return best


def _node_label(node: str) -> str:
    return node[5:].rsplit("/", 1)[-1] if node.startswith("task:") else f"step {node[5:]}"


def _edge_reason(reasons: list[dict]) -> str:
    named = sorted({e.get("via") or e["declaration"] for e in reasons})
    return named[0] + (f" and {len(named) - 1} more" if len(named) > 1 else "")


def _loop_through(pairs, edge: tuple[str, str]) -> list[str]:
    """The shortest loop using *edge*; empty when none does."""
    source, target = edge
    adjacency = {}
    for a, b in sorted(pairs):
        adjacency.setdefault(a, []).append(b)
    paths, seen = deque([[target]]), {target}
    while paths:
        path = paths.popleft()
        if path[-1] == source:
            return [source, *path]
        for node in adjacency.get(path[-1], ()):
            if node not in seen:
                seen.add(node)
                paths.append([*path, node])
    return []


def _cycle_message(cycle: dict, loop: list[str], added: tuple[str, str] | None = None) -> str:
    edges = cycle["edges"]
    size = f" ({len(cycle['members'])} nodes in all)" if len(cycle["members"]) > len(loop) - 1 else ""
    return (
        f"task cycle at {cycle['boundary'] or '(root)'}: {' -> '.join(map(_node_label, loop))}{size}; "
        + "; ".join(f"{_node_label(a)} -> {_node_label(b)} by {_edge_reason(edges[a, b])}"
                    + (" (new edge)" if (a, b) == added else "")
                    for a, b in zip(loop, loop[1:]))
        + f"; {CYCLE_REMEDY}"
    )


def _task_cycles(boundary: str, edges: dict) -> list[dict]:
    """Loops at one boundary, as ``{boundary, members, edges, message}``.

    A loop of steps alone is a step cycle and a loop of `depends_on` alone a
    `depends_on` cycle; both already have their own error.
    """
    cycles = []
    for members in cyclic_components(edges):
        inner = [pair for pair in edges if pair[0] in members and pair[1] in members]
        if not any(node.startswith("task:") for node in members) or all(
            reason["kind"] == "logical" for pair in inner for reason in edges[pair]
        ):
            continue
        cycle = {"boundary": boundary, "members": members, "edges": {pair: edges[pair] for pair in inner}}
        cycles.append({**cycle, "message": _cycle_message(cycle, shortest_loop(inner))})
    return cycles


def _refusal_message(cycle: dict, earlier_edges: set[tuple[str, str]]) -> str:
    """Describe *cycle* through an edge the edit added, which the default witness can miss."""
    added = sorted(set(cycle["edges"]) - earlier_edges)
    if not added:
        return cycle["message"]
    loops = {edge: _loop_through(cycle["edges"], edge) for edge in added}
    edge = min(added, key=lambda pair: len(loops[pair]))
    return _cycle_message(cycle, loops[edge], edge)


def new_cycles(before: Dependencies, after: Dependencies, moved: tuple[str, str] | None = None) -> list[str]:
    """Messages of loops in *after* whose tasks no single loop in *before* contains.

    Containment covers a new loop, a new member, and two loops merging; an edit
    inside a loop or one that shrinks it adds nothing. Steps are not compared, so
    renaming one inside a loop adds nothing either. *moved* is a task's ``(old, new)``
    path, so a moved loop still matches itself.
    """
    def relocate(path: str) -> str:
        return moved[1] + path[len(moved[0]):] if moved and path and within(path, moved[0]) else path

    def relocate_node(node: str) -> str:
        return "task:" + relocate(node[5:]) if node.startswith("task:") else node

    def tasks_in(cycle: dict) -> set[str]:
        return {node for node in cycle["members"] if node.startswith("task:")}

    known: dict[str, list[set[str]]] = {}
    for boundary, cycles in before.cycles.items():
        known.setdefault(relocate(boundary), []).extend(
            {relocate_node(n) for n in tasks_in(cycle)} for cycle in cycles)
    earlier_edges: dict[str, set[tuple[str, str]]] = {}
    for boundary, view in before.boundaries.items():
        earlier_edges.setdefault(relocate(boundary), set()).update(
            (relocate_node(e["from"]), relocate_node(e["to"])) for e in view["edges"])
    return [_refusal_message(cycle, earlier_edges.get(boundary, set()))
            for boundary, cycles in after.cycles.items() for cycle in cycles
            if not any(tasks_in(cycle) <= old for old in known.get(boundary, ()))]


@dataclass
class Dependencies:
    tasks: dict[str, Task] = field(default_factory=dict)
    archived: set[str] = field(default_factory=set)
    boundaries: dict[str, dict] = field(default_factory=dict)
    edges: list[dict] = field(default_factory=list)
    logical: list[dict] = field(default_factory=list)
    files: list[dict] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    cycles: dict[str, list[dict]] = field(default_factory=dict)  # boundary -> task-level loops
    complete: bool = True

    @property
    def valid(self):
        return self.complete and not any(f["severity"] == "error" for f in self.findings)

    def to_dict(self):
        return {
            "valid": self.valid, "complete": self.complete,
            "archived_tasks": sorted(self.archived),
            "tasks": [{"path": p, "title": t.title, "status": t.effective_status(),
                       "parent": p.rsplit("/", 1)[0] if "/" in p else ""}
                      for p, t in sorted(self.tasks.items()) if p not in self.archived
                      and not (not p and t.title == "(no root task.md)")],
            "edges": self.edges, "boundaries": self.boundaries,
            "findings": self.findings,
        }

    def order_tree(self):
        if not self.valid:
            return
        for path, task in self.tasks.items():
            view = self.boundaries.get(path)
            if view is None:
                continue
            pending = set(view["nodes"])
            ordered = []
            while pending:
                ready = sorted(n for n in pending if not any(
                    e["to"] == n and e["from"] in pending for e in view["edges"]))
                if not ready:
                    break
                ordered.extend(ready)
                pending.difference_update(ready)
            ranks = {n: i for i, n in enumerate(ordered)}
            task.children.sort(key=lambda c: (ranks.get("task:" + c.path, len(ranks)), c.path))

    def cycles_touching(self, paths):
        """Messages of the task-level loops holding one of *paths*, a group around it, or its step."""
        def holds(boundary, node, path):
            return within(path, node[5:]) if node.startswith("task:") else path == boundary

        return {cycle["message"] for boundary, cycles in self.cycles.items() for cycle in cycles
                if any(holds(boundary, node, path) for node in cycle["members"] for path in paths)}

    def prerequisite_edges(self, path):
        """`depends_on` edges gating this task, declared on it or an ancestor."""
        return [e for e in self.logical if within(path, e["to"])]

    def prerequisites(self, path):
        return sorted({e["from"] for e in self.prerequisite_edges(path)})

    def blockers(self, path):
        blocked = []
        for edge in self.prerequisite_edges(path):
            status = self.tasks[edge["from"]].effective_status()
            if status not in SATISFIED:
                blocked.append({"path": edge["from"], "status": status, "declared_by": edge["to"]})
        return blocked

    def ready(self, path):
        return self.valid and path not in self.archived and not self.blockers(path)

    def inputs(self, path):
        """File edges into this task's steps from producers outside it."""
        return [e for e in self.files if within(e["to"], path) and not within(e["from"], path)]

    def frontier(self):
        if not self.valid:
            return []
        rows = []
        for path, task in self.tasks.items():
            if path in self.archived or not task.is_leaf or task.status not in ACTIONABLE:
                continue
            if not path and task.title == "(no root task.md)":
                continue
            if any(t.status == "postponed" and within(path, p) for p, t in self.tasks.items()):
                continue
            if self.ready(path):
                rows.append({"path": path, "title": task.title, "status": task.status})
        return rows


def project(owner, step, boundary):
    if owner == boundary:
        return "step:" + step if step else None
    if not within(owner, boundary):
        return None
    tail = owner[len(boundary) + 1:] if boundary else owner
    return "task:" + ((boundary + "/") if boundary else "") + tail.split("/")[0]


def compose(root: Task, steps: list[Step], step_edges: list[tuple[str, str, str]], *, step_labels: dict[str, str] | None = None) -> Dependencies:
    """Gate readiness on `depends_on`; project file edges onto every boundary as a view."""
    result = Dependencies(tasks=task_index(root), archived=archived_paths(root))
    owner = {s.name: s.task_path for s in steps}
    evidence = []
    step_labels = step_labels or {}
    for source, target, via in step_edges:
        evidence.append({"kind": "inferred", "from": owner[source], "to": owner[target],
                         "producer": step_labels.get(source, source), "consumer": step_labels.get(target, target), "via": via})
    result.files = [e for e in evidence if e["to"] not in result.archived and e["from"] != e["to"]]
    for path, task in result.tasks.items():
        if path in result.archived:
            continue
        if task.parse_error:
            result.complete = False
            result.findings.append(dict(task_path=path, category="dependency", severity="error",
                                        message=f"task parsing incomplete: {task.parse_error}"))
        for dep in task.depends_on:
            parent = path.rsplit("/", 1)[0] if "/" in path else ""
            source = f"{parent}/{dep}".lstrip("/")
            if not path or not dep or source not in result.tasks or "/" in dep or "\\" in dep or dep in {".", ".."}:
                result.findings.append(dict(task_path=path, category="dependency", severity="error",
                                            message=f"depends_on '{dep}' does not resolve to any sibling task"))
                continue
            if source == path:
                result.findings.append(dict(task_path=path, category="dependency", severity="error",
                    message=f"depends_on cycle: {path} -> {path}; {path}/task.md depends_on: {dep}"))
            evidence.append({"kind": "logical", "from": source, "to": path,
                             "declaration": f"{path}/task.md depends_on: {dep}"})

    active_evidence = [e for e in evidence if e["from"] not in result.archived and e["to"] not in result.archived]
    result.logical = [e for e in active_evidence if e["kind"] == "logical" and e["from"] != e["to"]]
    for boundary, task in result.tasks.items():
        if boundary in result.archived:
            continue
        nodes = ["task:" + c.path for c in task.children if c.path not in result.archived]
        nodes += ["step:" + s.name for s in steps if s.task_path == boundary]
        edges = {}
        for item in active_evidence:
            source = project(item["from"], item.get("producer"), boundary)
            target = project(item["to"], item.get("consumer"), boundary)
            if source is None or target is None or source == target:
                continue
            edges.setdefault((source, target), []).append(item)
        result.boundaries[boundary] = {"nodes": sorted(nodes), "edges": [
            {"from": a, "to": b, "evidence": reasons} for (a, b), reasons in sorted(edges.items())]}
        # A task-level loop warns: an error would empty the frontier for the whole tree.
        for cycle in _task_cycles(boundary, edges):
            result.cycles.setdefault(boundary, []).append(cycle)
            result.findings.append(dict(task_path=boundary, category="dependency", severity="warning",
                                        message=cycle["message"]))
        logical = {pair: [e for e in reasons if e["kind"] == "logical"] for pair, reasons in edges.items()}
        logical = {pair: reasons for pair, reasons in logical.items() if reasons}
        cycle = cycle_path(logical)
        if cycle:
            detail = "; ".join(e["declaration"] for a, b in zip(cycle, cycle[1:]) for e in logical[a, b])
            result.findings.append(dict(task_path=boundary, category="dependency", severity="error",
                message=f"depends_on cycle at {boundary or '(root)'}: {' -> '.join(cycle)}; {detail}"))

    grouped = {}
    for view in result.boundaries.values():
        for edge in view["edges"]:
            if edge["from"].startswith("task:") and edge["to"].startswith("task:"):
                grouped.setdefault((edge["from"][5:], edge["to"][5:]), []).extend(edge["evidence"])
    result.edges = [{"from": a, "to": b, "evidence": reasons} for (a, b), reasons in sorted(grouped.items())]
    for edge in result.logical:
        # A postponed consumer is not blocked by a postponed prerequisite.
        if (result.tasks[edge["from"]].effective_status() == "postponed"
                and result.tasks[edge["to"]].effective_status() != "postponed"):
            result.findings.append(dict(task_path=edge["to"], category="dependency", severity="warning",
                message=f"depends on postponed task {edge['from']!r} (blocked until resumed)"))
    # Archival removes edges, but downstream authors still need the lost provenance.
    outgoing = {}
    for item in evidence:
        outgoing.setdefault(item["from"], []).append(item)
    archived_roots = [p for p in result.archived
                      if not any(a != p and within(p, a) for a in result.archived)]
    for archived in sorted(archived_roots):
        queue = [(archived, [])]
        seen = {archived}
        while queue:
            path, trail = queue.pop(0)
            inherited = [{"from": path, "to": c.path, "kind": "containment"}
                         for c in result.tasks[path].children]
            for item in outgoing.get(path, []) + inherited:
                target = item["to"]
                if target in seen:
                    continue
                seen.add(target)
                chain = trail + [item]
                queue.append((target, chain))
                if target not in result.archived:
                    detail = " -> ".join([archived] + [e["to"] for e in chain])
                    files = [e["via"] for e in chain if "via" in e]
                    result.findings.append(dict(task_path=target, category="dependency", severity="warning",
                        message=f"archived prerequisite {archived!r}: {detail}" + (f" via {', '.join(files)}" if files else "")))
    return result
