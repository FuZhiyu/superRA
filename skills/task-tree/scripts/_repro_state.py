#!/usr/bin/env python3
"""Runner state for the reproduction graph: hashes, lock reading, status.

Stdlib only, so ``repro status`` / ``explain`` / ``dag`` / ``tier`` — and the
`task read` and dashboard views that consume their JSON — run without pytask.
Only ``repro build`` needs the engine; it lives in ``repro_run.py``.

The committed ``pytask.lock`` is the record of what each step last built. Its
node ids are the logical (``${VAR}``-form) paths this module also uses, so a
lock written on one checkout reads on another; the states it stores are the
hashes ``node_state`` computes here, which is what lets a build-free reader
recompute freshness with the same rule pytask applies.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

if __package__:
    from ._repro import REPRO_SECTION, TIERS, Graph, Step, normalize_tier
    from ._task_io import parse_body_sections, resolve_path
else:  # pragma: no cover - direct-script path
    sys.path.insert(0, str(Path(__file__).parent))
    from _repro import REPRO_SECTION, TIERS, Graph, Step, normalize_tier
    from _task_io import parse_body_sections, resolve_path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - 3.10 falls back to repro_run.py
    tomllib = None  # type: ignore[assignment]

TOML_AVAILABLE = tomllib is not None

STATE_DIRNAME = ".superra-repro"
LOCK_FILENAME = "pytask.lock"

# Step states. A step takes the first one its own evidence supports, in this
# order; the cascade then lifts a `fresh` step whose upstream is not fresh.
STATUSES = ("fresh", "stale", "missing", "failed", "external")


class ReproStateError(RuntimeError):
    """A runner-state operation that cannot proceed."""


# ---------------------------------------------------------------------------
# State directory
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunnerPaths:
    """Where the runner keeps its per-machine state and its committed lock."""

    project_root: Path
    state_dir: Path

    @property
    def logs_dir(self) -> Path:
        return self.state_dir / "logs"

    @property
    def runs_dir(self) -> Path:
        return self.state_dir / "runs"

    @property
    def stamps_dir(self) -> Path:
        return self.state_dir / "stamps"

    @property
    def cache_file(self) -> Path:
        return self.state_dir / "hashes.json"

    @property
    def lock_file(self) -> Path:
        return self.project_root / LOCK_FILENAME

    def log_file(self, step: str) -> Path:
        return self.logs_dir / f"{step}.log"

    def log_ref(self, step: str) -> str:
        """Project-relative log path — what reports and records carry."""
        return f"{STATE_DIRNAME}/logs/{step}.log"

    def run_file(self, step: str) -> Path:
        return self.runs_dir / f"{step}.json"


def runner_paths(project_root: Path) -> RunnerPaths:
    root = Path(project_root)
    return RunnerPaths(project_root=root, state_dir=root / STATE_DIRNAME)


def ensure_state_dir(paths: RunnerPaths) -> None:
    """Create the state directory and keep it out of git."""
    for directory in (paths.state_dir, paths.logs_dir, paths.runs_dir, paths.stamps_dir):
        directory.mkdir(parents=True, exist_ok=True)
    gitignore = paths.project_root / ".gitignore"
    entry = f"{STATE_DIRNAME}/"
    try:
        existing = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
        if entry in existing.split() or STATE_DIRNAME in existing.split():
            return
        prefix = "" if not existing or existing.endswith("\n") else "\n"
        with gitignore.open("a", encoding="utf-8") as handle:
            handle.write(f"{prefix}{entry}\n")
    except OSError:  # a read-only checkout still builds
        pass


def stamp_ref(step_name: str) -> str:
    """Logical path of a check step's stamp — its product, so pytask can skip it."""
    return f"{STATE_DIRNAME}/stamps/{step_name}.stamp"


# ---------------------------------------------------------------------------
# Content hashing
# ---------------------------------------------------------------------------

class HashCache:
    """Content hashes keyed on (size, mtime_ns), persisted as JSON.

    A hit costs one ``stat``; a miss reads the file. Inode is deliberately not
    part of the key: Dropbox does not preserve it across machines.
    """

    def __init__(self, path: Path | None = None):
        self.path = path
        self.full_reads = 0
        self._entries: dict[str, list] = {}
        self._dirty = False
        if path is not None and path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                loaded = {}
            if isinstance(loaded, dict):
                self._entries = {
                    k: v for k, v in loaded.items() if isinstance(v, list) and len(v) == 3
                }

    def file_hash(self, path: Path) -> str | None:
        """sha256 of a file's content, or None when it is not a readable file."""
        try:
            info = path.stat()
        except OSError:
            return None
        return self._hashed(path, info)

    def _hashed(self, path: Path, info: os.stat_result) -> str | None:
        if not stat.S_ISREG(info.st_mode):
            return None
        key = str(path)
        cached = self._entries.get(key)
        if cached and cached[0] == info.st_size and cached[1] == info.st_mtime_ns:
            return cached[2]
        digest = hashlib.sha256()
        try:
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(block)
        except OSError:
            return None
        self.full_reads += 1
        value = digest.hexdigest()
        self._entries[key] = [info.st_size, info.st_mtime_ns, value]
        self._dirty = True
        return value

    def tree_hash(self, path: Path) -> str | None:
        """One hash over every file under a directory, by relative path."""
        digest = hashlib.sha256()
        entries: list[tuple[str, str]] = []
        for parent, dirnames, filenames in os.walk(path):
            dirnames.sort()
            for filename in sorted(filenames):
                child = Path(parent) / filename
                child_hash = self.file_hash(child)
                if child_hash is None:
                    continue
                entries.append((os.path.relpath(child, path).replace(os.sep, "/"), child_hash))
        for name, value in sorted(entries):
            digest.update(f"{name}\0{value}\n".encode())
        return f"dir:{digest.hexdigest()}"

    def path_state(self, path: Path) -> str | None:
        """State of a file or directory: its content hash, or None if absent.

        One ``stat`` decides both the branch and, for a file, the cache key.
        """
        try:
            info = path.stat()
        except OSError:
            return None
        if stat.S_ISDIR(info.st_mode):
            return self.tree_hash(path)
        return self._hashed(path, info)

    def flush(self) -> None:
        """Persist, but never create the state directory — `ensure_state_dir` owns
        that, so a tree with no steps stays untouched."""
        if self.path is None or not self._dirty or not self.path.parent.is_dir():
            return
        try:
            self.path.write_text(json.dumps(self._entries), encoding="utf-8")
        except OSError:
            return
        self._dirty = False


def sidecar_targets(graph: Graph) -> dict[str, str]:
    """Logical out path -> the resolved path the runner hashes in its place.

    A sidecar-tracked out is hashed through its sidecar wherever it appears —
    as its producer's product and as any consumer's dep — so producer and
    consumer agree on one state for one lock id, and the large file is never
    read.
    """
    return {
        out.path.logical: out.sidecar.resolved
        for step in graph.steps
        for out in step.outs
        if out.sidecar is not None
    }


Node = tuple[str, str, str | None]  # lock id, path to hash, path that must exist


def step_nodes(step: Step, tracked: dict[str, str]) -> tuple[list[Node], list[Node]]:
    """(deps, products) of a step as `Node` triples.

    The third element is set only for a sidecar-tracked path: the sidecar
    stands in for hashing, never for existence, so a deleted out still reports
    missing.
    """
    deps = [
        (d.logical, tracked.get(d.logical, d.resolved), _tracked_origin(d.logical, d.resolved, tracked))
        for d in step.deps
    ]
    if step.kind == "check":
        stamp = stamp_ref(step.name)
        return deps, [(stamp, stamp, None)]
    products = [
        (o.path.logical, (o.sidecar or o.path).resolved, o.path.resolved if o.sidecar else None)
        for o in step.outs
    ]
    return deps, products


def _tracked_origin(logical: str, resolved: str, tracked: dict[str, str]) -> str | None:
    return resolved if logical in tracked else None


def directory_dep_nodes(graph: Graph, step: Step, tracked: dict[str, str]) -> list[Node]:
    """Nodes for the directory outs that cover this step's deps.

    `_repro._producing_step` reads a dep below a directory out as produced by
    that directory, and the status cascade follows the resulting `step_edges`.
    The engine bridge sees only per-path nodes, so without these it would carry
    no edge and could run the consumer first.
    """
    covering: list[tuple[str, Node]] = []
    for owner in graph.steps:
        if owner.name == step.name:
            continue
        for out in owner.outs:
            covering.append(
                (
                    out.path.resolved,
                    (
                        out.path.logical,
                        (out.sidecar or out.path).resolved,
                        out.path.resolved if out.sidecar else None,
                    ),
                )
            )
    covering.sort(key=lambda entry: len(entry[0]), reverse=True)

    declared = {d.logical for d in step.deps}
    extra: list[Node] = []
    for dep in step.deps:
        for directory, node in covering:
            if dep.resolved.startswith(directory + "/"):
                if node[0] not in declared:
                    declared.add(node[0])
                    extra.append(node)
                break
    return extra


def node_state(
    cache: HashCache, project_root: Path, node: Node
) -> str | None:
    """State of a node: absent when its required path is gone, else its hash."""
    _, hashed, must_exist = node
    if must_exist is not None and not absolute(project_root, must_exist).exists():
        return None
    return path_state(cache, project_root, hashed)


def path_state(cache: HashCache, project_root: Path, resolved: str) -> str | None:
    return cache.path_state(absolute(project_root, resolved))


def absolute(project_root: Path, resolved: str) -> Path:
    path = Path(resolved)
    return path if path.is_absolute() else project_root / path


# ---------------------------------------------------------------------------
# Step spec — the per-step state that gives the shared task state granularity
# ---------------------------------------------------------------------------

def spec_node_id(step_name: str) -> str:
    return f"{step_name}::spec"


def spec_hashes(step: Step) -> tuple[str, str]:
    """The two halves of a step's state: what was declared, and what it resolved to.

    A `${VAR}` that only ever reaches `cmd` — a mode flag, a seed, a switched
    `${OUT}` root — moves the second half alone, so `status` can name the
    resolution rather than accusing the author of editing the declaration.
    Node *ids* stay logical; states have always tracked what the invocation
    resolved to.
    """
    declared = {
        "cmd": step.cmd_logical,
        "kind": step.kind,
        "params": {str(k): step.params[k] for k in sorted(step.params)},
        "deps": sorted(d.logical for d in step.deps),
        "outs": sorted(o.path.logical for o in step.outs),
        "sidecars": sorted(
            o.sidecar.logical for o in step.outs if o.sidecar is not None
        ),
    }
    return _payload_hash(declared), _payload_hash({"cmd_resolved": step.cmd})


def spec_hash(step: Step) -> str:
    """Both halves as one node state, declared half first."""
    return "{}:{}".format(*spec_hashes(step))


def _payload_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Lock and run records
# ---------------------------------------------------------------------------

@dataclass
class LockEntry:
    """One step's record in ``pytask.lock``, keyed by logical node id."""

    depends_on: dict[str, str] = field(default_factory=dict)
    produces: dict[str, str] = field(default_factory=dict)


def read_lock(path: Path) -> dict[str, LockEntry]:
    """Parse ``pytask.lock`` into step name -> recorded node states."""
    if tomllib is None:  # pragma: no cover - 3.10 routes through repro_run.py
        raise ReproStateError(
            "reading pytask.lock needs Python 3.11+ (tomllib); run `superra repro` "
            "through uv so the runner picks a newer interpreter"
        )
    if not path.is_file():
        return {}
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReproStateError(f"{path} could not be read: {exc}") from None
    entries: dict[str, LockEntry] = {}
    for raw in document.get("task", []) or []:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            continue
        entries[raw["id"]] = LockEntry(
            depends_on=dict(raw.get("depends_on") or {}),
            produces=dict(raw.get("produces") or {}),
        )
    return entries


def write_run_record(paths: RunnerPaths, step: str, record: dict) -> None:
    """Record one step's outcome; one file per step keeps parallel runs race-free."""
    paths.runs_dir.mkdir(parents=True, exist_ok=True)
    paths.run_file(step).write_text(json.dumps(record), encoding="utf-8")


def read_run_record(paths: RunnerPaths, step: str) -> dict:
    try:
        loaded = json.loads(paths.run_file(step).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@dataclass
class Change:
    """One node whose recorded state no longer matches what is on disk."""

    node: str
    kind: str      # dependency | output | spec
    change: str    # changed | missing

    def to_dict(self) -> dict:
        return {"node": self.node, "kind": self.kind, "change": self.change}


@dataclass
class StepStatus:
    step: Step
    status: str = "fresh"
    reason: str = "up to date"
    changes: list[Change] = field(default_factory=list)
    duration: float | None = None
    last_run: float | None = None
    log: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.step.name,
            "task": self.step.task_path,
            "tier": self.step.tier,
            "kind": self.step.kind,
            "cmd": self.step.cmd_logical,
            "status": self.status,
            "reason": self.reason,
            "changes": [c.to_dict() for c in self.changes],
            "duration": self.duration,
            "last_run": self.last_run,
            "log": self.log,
            "deps": [d.to_dict() for d in self.step.deps],
            "outs": [o.to_dict() for o in self.step.outs],
        }


@dataclass
class StatusReport:
    project_root: Path
    tier: str
    graph: Graph
    entries: list[StepStatus] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    selected: set[str] | None = None

    @property
    def reported(self) -> list[StepStatus]:
        if self.selected is not None:
            return [e for e in self.entries if e.step.name in self.selected]
        if self.tier == "all":
            return self.entries
        return [e for e in self.entries if e.step.tier == self.tier]

    @property
    def external_inputs(self) -> list:
        """Boundary inputs of the reported steps, so the tier scopes both lists."""
        names = {e.step.name for e in self.reported}
        return [
            e
            for e in self.graph.external_inputs
            if names.intersection(e.consumers)
        ]

    @property
    def ok(self) -> bool:
        stale = any(e.status != "fresh" for e in self.reported)
        errors = any(f.severity == "error" for f in self.graph.findings)
        return not stale and not errors

    def entry(self, name: str) -> StepStatus | None:
        for candidate in self.entries:
            if candidate.step.name == name:
                return candidate
        return None

    def to_dict(self) -> dict:
        reported = self.reported
        summary = {name: 0 for name in STATUSES}
        for entry in reported:
            summary[entry.status] += 1
        summary["total"] = len(reported)
        return {
            "root": str(self.project_root),
            "tier": self.tier,
            "targets": self.targets,
            "ok": self.ok,
            "summary": summary,
            "steps": [e.to_dict() for e in reported],
            "external_inputs": [e.to_dict() for e in self.external_inputs],
            "findings": [f.to_dict() for f in self.graph.findings],
        }


def compute_status(
    graph: Graph,
    paths: RunnerPaths,
    *,
    tier: str = "required",
    targets: Iterable[str] = (),
    cache: HashCache | None = None,
) -> StatusReport:
    """Classify every step, then report the tier or explicit target closure.

    Every step is classified because a required step's freshness depends on its
    upstream steps whatever tier they carry.
    """
    tier = normalize_tier(tier)
    targets = list(targets)
    selected = None
    if targets:
        names, unknown = select_steps(graph, targets, tier)
        if unknown:
            raise ReproStateError(f"no step or task matches {', '.join(unknown)}")
        selected = set(names)
    cache = HashCache(paths.cache_file) if cache is None else cache
    lock = read_lock(paths.lock_file)
    tracked = sidecar_targets(graph)
    missing_external = {e.path.logical for e in graph.external_inputs if not e.exists}
    report = StatusReport(
        project_root=paths.project_root, tier=tier, graph=graph,
        targets=targets, selected=selected,
    )

    for step in graph.steps:
        report.entries.append(
            _classify(
                step, lock.get(step.name), paths, cache, tracked, missing_external
            )
        )
    _cascade(report, graph)
    cache.flush()
    return report


def _classify(
    step: Step,
    entry: LockEntry | None,
    paths: RunnerPaths,
    cache: HashCache,
    tracked: dict[str, str],
    missing_external: set[str],
) -> StepStatus:
    result = StepStatus(step=step)
    record = read_run_record(paths, step.name)
    result.duration = record.get("duration")
    result.last_run = record.get("ended_at")
    if record.get("log"):
        result.log = record["log"]

    blocked = [d.logical for d in step.deps if d.logical in missing_external]
    if blocked:
        result.status = "external"
        result.reason = _plural(
            f"external input {blocked[0]} is missing", len(blocked) - 1
        )
        result.changes = [
            Change(node=p, kind="dependency", change="missing") for p in blocked
        ]
        return result

    if entry is None:
        result.status = "missing"
        result.reason = "never built"
    else:
        _compare(result, step, entry, paths, cache, tracked)

    # A failed run is reported only while the step still has work to do. Once
    # inputs are restored and everything matches the lock again, the tree is
    # consistent and `build` correctly skips — so `status` says `fresh` rather
    # than wedging on a record that no longer describes disk.
    if result.status != "fresh" and record.get("outcome") == "failed":
        result.status = "failed"
        # Keep whatever moved since that run — a dep edited after the failure is
        # the trigger a rerun answers to, and the log is where the last one died.
        log_ref = result.log or paths.log_ref(step.name)
        result.reason = f"{result.reason}; last run failed, see {log_ref}"
    return result


def _compare(
    result: StepStatus,
    step: Step,
    entry: LockEntry,
    paths: RunnerPaths,
    cache: HashCache,
    tracked: dict[str, str],
) -> None:
    """Set *result* from the lock entry against what is on disk now."""
    deps, products = step_nodes(step, tracked)
    absent = [
        node[0]
        for node in products
        if node_state(cache, paths.project_root, node) is None
    ]
    if absent:
        result.status = "missing"
        result.reason = _plural(f"output {absent[0]} is missing", len(absent) - 1)
        result.changes = [
            Change(node=p, kind="output", change="missing") for p in absent
        ]
        return

    changes = _changed_nodes(step, entry, paths, cache, deps, products)
    if not changes:
        return
    result.status = "stale"
    result.changes = changes
    first = changes[0]
    if first.kind == "spec":
        head = (
            "the resolved command changed"
            if first.change == "resolved"
            else "the step definition changed"
        )
    else:
        head = f"{first.kind} {first.node} {first.change}"
    result.reason = _plural(head, len(changes) - 1)


def _changed_nodes(
    step: Step,
    entry: LockEntry,
    paths: RunnerPaths,
    cache: HashCache,
    deps: list[Node],
    products: list[Node],
) -> list[Change]:
    """Recorded node states that no longer match disk, in reporting order."""
    changes: list[Change] = []
    spec_id = spec_node_id(step.name)
    recorded_spec = entry.depends_on.get(spec_id)
    declared, resolved = spec_hashes(step)
    if recorded_spec != f"{declared}:{resolved}":
        # Same declared half, different resolved half: a `${VAR}` moved, not the
        # section. A lock written before the split has no declared half to match.
        resolved_only = (
            recorded_spec is not None and recorded_spec.split(":", 1)[0] == declared
        )
        changes.append(
            Change(
                node=spec_id,
                kind="spec",
                change="resolved" if resolved_only else "changed",
            )
        )

    for node in deps:
        recorded = entry.depends_on.get(node[0])
        if recorded is None:
            continue  # a newly declared dep already moved the spec hash
        current = node_state(cache, paths.project_root, node)
        if current is None:
            changes.append(Change(node=node[0], kind="dependency", change="missing"))
        elif current != recorded:
            changes.append(Change(node=node[0], kind="dependency", change="changed"))

    for node in products:
        recorded = entry.produces.get(node[0])
        if recorded is None:
            continue
        current = node_state(cache, paths.project_root, node)
        if current is not None and current != recorded:
            changes.append(Change(node=node[0], kind="output", change="changed"))
    return changes


def _cascade(report: StatusReport, graph: Graph) -> None:
    """Lift a fresh step to stale when anything it reads is not fresh."""
    by_name = {e.step.name: e for e in report.entries}
    upstream: dict[str, list[str]] = {name: [] for name in by_name}
    for src, dst, _ in graph.step_edges:
        if dst in upstream and src in by_name:
            upstream[dst].append(src)

    for name in _topological(by_name, upstream):
        entry = by_name[name]
        if entry.status != "fresh":
            continue
        for parent in upstream[name]:
            if by_name[parent].status != "fresh":
                entry.status = "stale"
                entry.reason = (
                    f"upstream step {parent!r} is {by_name[parent].status}"
                )
                break


def _topological(by_name: dict, upstream: dict[str, list[str]]) -> list[str]:
    """Steps in dependency order; a cycle falls back to name order."""
    ordered: list[str] = []
    seen: set[str] = set()
    visiting: set[str] = set()

    def _visit(name: str) -> None:
        if name in seen or name in visiting:
            return
        visiting.add(name)
        for parent in upstream.get(name, []):
            _visit(parent)
        visiting.discard(name)
        seen.add(name)
        ordered.append(name)

    for name in sorted(by_name):
        _visit(name)
    return ordered


def _plural(head: str, extra: int) -> str:
    if extra <= 0:
        return head
    return f"{head} (and {extra} more)"


# ---------------------------------------------------------------------------
# Target selection
# ---------------------------------------------------------------------------

def select_steps(
    graph: Graph, targets: Iterable[str], tier: str
) -> tuple[list[str], list[str]]:
    """Resolve build targets to step names, returning (selected, unknown targets).

    A target is a step name or a task path (that task and its descendants).
    Ancestors of every selection come along so a target can be built from a
    cold tree; the tier filter only chooses the default selection.
    """
    tier = normalize_tier(tier)
    targets = [t for t in targets if t]
    unknown: list[str] = []
    selected: set[str] = set()
    if targets:
        for target in targets:
            if graph.step(target) is not None:
                selected.add(target)
                continue
            owned = [
                s.name
                for s in graph.steps
                if s.task_path == target or s.task_path.startswith(f"{target}/")
            ]
            if owned:
                selected.update(owned)
            else:
                unknown.append(target)
    else:
        selected = {
            s.name for s in graph.steps if tier == "all" or s.tier == tier
        }

    upstream: dict[str, list[str]] = {s.name: [] for s in graph.steps}
    for src, dst, _ in graph.step_edges:
        if dst in upstream:
            upstream[dst].append(src)
    queue = list(selected)
    while queue:
        name = queue.pop()
        for parent in upstream.get(name, []):
            if parent not in selected:
                selected.add(parent)
                queue.append(parent)
    order = {s.name: i for i, s in enumerate(graph.steps)}
    return sorted(selected, key=lambda n: order.get(n, 0)), unknown


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

_MARKS = {
    "fresh": "✓",
    "stale": "~",
    "missing": "?",
    "failed": "✗",
    "external": "!",
}


def format_status(report: StatusReport) -> str:
    entries = report.reported
    if not entries:
        return f"No steps registered at tier {report.tier}; no result verified."
    width = max(len(e.step.name) for e in entries)
    lines = []
    for entry in sorted(entries, key=lambda e: e.step.name):
        duration = f"  {entry.duration:.1f}s" if entry.duration else ""
        lines.append(
            f"{_MARKS[entry.status]} {entry.step.name:<{width}}  "
            f"{entry.status:<8}  {entry.reason}{duration}"
        )
    counts = ", ".join(
        f"{sum(1 for e in entries if e.status == name)} {name}"
        for name in STATUSES
        if any(e.status == name for e in entries)
    )
    lines.append("")
    scope = (
        f"for {', '.join(report.targets)} (including producer ancestors)"
        if report.targets else f"at tier {report.tier}"
    )
    lines.append(f"{len(entries)} step(s) {scope}: {counts}")
    missing = [e for e in report.external_inputs if not e.exists]
    if missing:
        lines.append("")
        lines.append("Missing external inputs:")
        lines.extend(f"  {e.path.logical}" for e in missing)
    errors = [f for f in report.graph.findings if f.severity == "error"]
    if errors:
        lines.append("")
        lines.append(f"{len(errors)} graph error(s); run `superra task check`.")
    return "\n".join(lines)


def format_explain(report: StatusReport, step_name: str) -> str:
    entry = report.entry(step_name)
    if entry is None:
        known = ", ".join(sorted(s.name for s in report.graph.steps)) or "(none)"
        raise ReproStateError(f"unknown step {step_name!r}; registered steps: {known}")
    step = entry.step
    lines = [
        f"{step.name}  [{entry.status}]  {entry.reason}",
        f"  task:  {step.task_path or '(root)'}",
        f"  tier:  {step.tier}    kind: {step.kind}",
        f"  cmd:   {step.cmd_logical}",
    ]
    if step.cmd != step.cmd_logical:
        lines.append(f"  runs:  {step.cmd}")
    if step.params:
        lines.append(f"  params: {json.dumps(step.params, sort_keys=True)}")
    if entry.duration:
        lines.append(f"  last:  {entry.duration:.1f}s at {_stamp(entry.last_run)}")
    if entry.log:
        lines.append(f"  log:   {entry.log}")
    if entry.changes:
        lines.append("  changed since the last build:")
        lines.extend(f"    {c.kind}: {c.node} ({c.change})" for c in entry.changes)
    upstream = sorted(
        {src for src, dst, _ in report.graph.step_edges if dst == step.name}
    )
    if upstream:
        lines.append("  upstream steps:")
        for name in upstream:
            parent = report.entry(name)
            lines.append(f"    {name}: {parent.status if parent else 'unknown'}")
    lines.append("  deps:")
    lines.extend(f"    {d.logical}" for d in step.deps)
    lines.append("  outs:")
    if step.kind == "check":
        lines.append(f"    {stamp_ref(step.name)} (check stamp)")
    for out in step.outs:
        suffix = f"  (sidecar {out.sidecar.logical})" if out.sidecar else ""
        lines.append(f"    {out.path.logical}{suffix}")
    return "\n".join(lines)


def _stamp(value: float | None) -> str:
    if not value:
        return "unknown time"
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(value))


_MERMAID_ID_RE = re.compile(r"[^a-zA-Z0-9_-]")


def render_dag(graph: Graph, *, mermaid: bool = False) -> str:
    steps = graph.steps
    edges = graph.step_edges
    if not mermaid:
        if not steps:
            return "No steps registered."
        lines = [
            f"{s.name}  ({s.task_path or '(root)'}, {s.tier})"
            for s in sorted(steps, key=lambda s: s.name)
        ]
        lines.append("")
        if edges:
            lines.extend(f"{src} --> {dst}   [{via}]" for src, dst, via in edges)
        else:
            lines.append("(no step edges)")
        return "\n".join(lines)

    if not steps:
        return "graph LR\n    %% no steps"
    lines = ["graph LR"]
    for step in steps:
        node = _MERMAID_ID_RE.sub("_", step.name)
        style = ":::check" if step.kind == "check" else f":::{step.tier}"
        lines.append(f'    {node}["{step.name}"]{style}')
    for src, dst, via in edges:
        label = via.rsplit("/", 1)[-1]
        lines.append(f"    {_MERMAID_ID_RE.sub('_', src)} -->|{label}| {_MERMAID_ID_RE.sub('_', dst)}")
    lines.append("")
    lines.append("    classDef required fill:#c8e6c9,stroke:#43a047,color:#1b5e20")
    lines.append("    classDef on-demand fill:#e0e0e0,stroke:#999,color:#333")
    lines.append("    classDef check fill:#bbdefb,stroke:#1976d2,color:#0d47a1")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tier mutation
# ---------------------------------------------------------------------------

def set_tier(plan_root: Path, task_path: str, tier: str) -> str:
    """Set the ``tier`` key of a task's ``## Reproduction`` block."""
    tier = normalize_tier(tier)
    if tier not in TIERS:
        raise ReproStateError(f"unknown tier: {tier}")
    task_file = resolve_path(plan_root, task_path) / "task.md"
    if not task_file.is_file():
        raise ReproStateError(f"task not found: {task_path}")
    text = task_file.read_text(encoding="utf-8")
    section = parse_body_sections(text).get(REPRO_SECTION)
    if section is None:
        raise ReproStateError(
            f"task {task_path} has no ## {REPRO_SECTION} section to set a tier on"
        )

    lines = text.split("\n")
    fence = _fence_bounds(lines)
    if fence is None:
        raise ReproStateError(
            f"task {task_path}: the ## {REPRO_SECTION} body is not one fenced yaml block"
        )
    start, end = fence
    for index in range(start, end):
        if re.match(r"^tier\s*:", lines[index]):
            lines[index] = f"tier: {tier}"
            break
    else:
        lines.insert(start, f"tier: {tier}")
    task_file.write_text("\n".join(lines), encoding="utf-8")
    return f"{task_path}: tier set to {tier}"


def _fence_bounds(lines: list[str]) -> tuple[int, int] | None:
    """(first line inside, line of the closing fence) of the Reproduction block."""
    heading = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {REPRO_SECTION}":
            heading = index
            break
    if heading is None:
        return None
    opened = None
    for index in range(heading + 1, len(lines)):
        stripped = lines[index].strip()
        if opened is None:
            if stripped.startswith("```"):
                opened = index
            elif stripped.startswith("## "):
                return None
        elif stripped == "```":
            return opened + 1, index
    return None


__all__ = [
    "Change",
    "HashCache",
    "LockEntry",
    "ReproStateError",
    "RunnerPaths",
    "STATE_DIRNAME",
    "STATUSES",
    "absolute",
    "StatusReport",
    "StepStatus",
    "TOML_AVAILABLE",
    "compute_status",
    "directory_dep_nodes",
    "ensure_state_dir",
    "format_explain",
    "format_status",
    "node_state",
    "path_state",
    "read_lock",
    "read_run_record",
    "render_dag",
    "runner_paths",
    "sidecar_targets",
    "select_steps",
    "set_tier",
    "spec_hash",
    "spec_node_id",
    "step_nodes",
    "stamp_ref",
    "write_run_record",
]
