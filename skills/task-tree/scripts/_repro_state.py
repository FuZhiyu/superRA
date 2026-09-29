#!/usr/bin/env python3
"""Runner state for the reproduction graph: hashes, the lock, status.

Stdlib only. ``repro build`` (in ``repro_run.py``) decides run-or-skip with
the same ``compute_status`` that ``repro status`` / ``explain``, `task read`,
and the dashboard use.

The committed ``repro-lock.json`` is the record of what each step last built.
Its node ids are the logical (``${VAR}``-form) paths this module also uses, so
a lock written on one checkout reads on another. A project without it reads a
legacy ``pytask.lock`` (with ``repro-builds.json``) converted in memory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import stat
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

if __package__:
    from ._repro import Graph, Step
else:  # pragma: no cover - direct-script path
    sys.path.insert(0, str(Path(__file__).parent))
    from _repro import Graph, Step

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - 3.10 re-execs to read a legacy lock
    tomllib = None  # type: ignore[assignment]

TOML_AVAILABLE = tomllib is not None

STATE_DIRNAME = ".superra-repro"
LOCK_FILENAME = "repro-lock.json"
LOCK_VERSION = 1
LEGACY_LOCK_FILENAME = "pytask.lock"
LEGACY_BUILDS_FILENAME = "repro-builds.json"

# Serializes every read-modify-write of a committed record (the lock, the
# acceptance ledger) across `-j` worker threads.
RECORD_LOCK = threading.RLock()

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

    @property
    def legacy_lock_file(self) -> Path:
        return self.project_root / LEGACY_LOCK_FILENAME

    @property
    def legacy_builds_file(self) -> Path:
        return self.project_root / LEGACY_BUILDS_FILENAME

    @property
    def reads_legacy_lock(self) -> bool:
        """No ``repro-lock.json`` yet, but a ``pytask.lock`` to convert."""
        return not self.lock_file.is_file() and self.legacy_lock_file.is_file()

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
    """Logical path of a check step's stamp — its product, so a passed check can skip."""
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
        self._flush_lock = threading.Lock()
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
        """One hash over every file under a directory, by relative path.

        Symlinked files and subdirectories are followed, each real directory
        once. A broken link or an unreadable file makes the whole directory
        unreadable (None) rather than silently leaving it out.
        """
        digest = hashlib.sha256()
        entries: list[tuple[str, str]] = []
        visited: set[tuple[int, int]] = set()
        unreadable: list[OSError] = []
        for parent, dirnames, filenames in os.walk(path, onerror=unreadable.append, followlinks=True):
            info = os.stat(parent)
            if (info.st_dev, info.st_ino) in visited:
                dirnames[:] = []
                continue
            visited.add((info.st_dev, info.st_ino))
            dirnames.sort()
            for filename in sorted(filenames):
                child = Path(parent) / filename
                try:
                    child_info = child.stat()
                except OSError:
                    return None  # a broken link
                if not stat.S_ISREG(child_info.st_mode):
                    continue
                child_hash = self._hashed(child, child_info)
                if child_hash is None:
                    return None  # unreadable
                entries.append((os.path.relpath(child, path).replace(os.sep, "/"), child_hash))
        if unreadable:
            return None
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
        with self._flush_lock:  # `-j` workers share one cache
            try:
                self.path.write_text(json.dumps(dict(self._entries)), encoding="utf-8")
            except OSError:
                return
            self._dirty = False


Node = tuple[str, str, str | None]  # lock id, path to hash, path that must exist


def output_nodes(graph: Graph) -> dict[str, Node]:
    """Resolved output paths mapped to their producer's portable node identity.

    Consumers reuse that identity and its sidecar even when their declarations
    spell the same resolved path differently.
    """
    return {
        out.path.resolved: (
            out.path.logical,
            (out.sidecar or out.path).resolved,
            out.path.resolved if out.sidecar else None,
        )
        for step in graph.steps
        for out in step.outs
    }


def step_nodes(step: Step, outputs: dict[str, Node]) -> tuple[list[Node], list[Node]]:
    """(deps, products) with producer identities and sidecar existence checks."""
    deps = [outputs.get(d.resolved, (d.logical, d.resolved, None)) for d in step.deps]
    if step.kind == "check":
        stamp = stamp_ref(step.name)
        return deps, [(stamp, stamp, None)]
    return deps, [outputs[o.path.resolved] for o in step.outs]


def directory_dep_nodes(graph: Graph, step: Step) -> list[Node]:
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


def dependency_state(cache: HashCache, project_root: Path, node: Node, recorded: str | None = None) -> str | None:
    """A saved artifact remains usable when its producer's sidecar is absent."""
    value = None if recorded and recorded.startswith('saved-input:') else node_state(cache, project_root, node)
    if value is None and node[2] is not None:
        digest = cache.path_state(absolute(project_root, node[2]))
        if digest is not None:
            return f"saved-input:{digest}"
    return value


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
    """One step's record in the lock, keyed by logical node id.

    ``depends_on`` carries the step spec as its ``<step>::spec`` node. What the
    step was built on never decides freshness, so it takes no part in equality.
    """

    depends_on: dict[str, str] = field(default_factory=dict)
    produces: dict[str, str] = field(default_factory=dict)
    built_on: dict = field(default_factory=dict, compare=False)


def lock_entry(name: str, raw: dict) -> LockEntry:
    """A ``repro-lock.json`` step entry as the in-memory lock entry."""
    depends_on = dict(raw.get("deps") or {})
    if raw.get("spec") is not None:
        depends_on[spec_node_id(name)] = raw["spec"]
    return LockEntry(depends_on=depends_on, produces=dict(raw.get("outs") or {}),
                     built_on=dict(raw.get("built_on") or {}))


def lock_record(name: str, entry: LockEntry) -> dict:
    """The ``repro-lock.json`` step entry for an in-memory lock entry."""
    spec_id = spec_node_id(name)
    return {
        "spec": entry.depends_on.get(spec_id),
        "deps": {k: v for k, v in entry.depends_on.items() if k != spec_id},
        "outs": dict(entry.produces),
        "built_on": dict(entry.built_on),
    }


def empty_lock() -> dict:
    return {"version": LOCK_VERSION, "steps": {}}


def parse_lock(text: str | None) -> dict:
    """A ``repro-lock.json`` document, normalized; raises ValueError when malformed."""
    document = json.loads(text) if text else empty_lock()
    if not isinstance(document, dict) or not isinstance(document.get("steps", {}), dict):
        raise ValueError("expected an object with a 'steps' object")
    if document.get("version", LOCK_VERSION) != LOCK_VERSION:
        raise ValueError(f"unsupported lock version {document.get('version')!r}")
    return {
        "version": LOCK_VERSION,
        "steps": {name: raw for name, raw in document.get("steps", {}).items() if isinstance(raw, dict)},
    }


def legacy_lock_id(depends_on: dict, produces: dict) -> str:
    """How ``repro-builds.json`` linked a record to its ``pytask.lock`` entry."""
    blob = json.dumps({"depends_on": depends_on, "produces": produces}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def convert_legacy(lock_text: str | None, builds_text: str | None = None) -> dict:
    """``pytask.lock`` plus ``repro-builds.json`` as a ``repro-lock.json`` document.

    pytask's ``state`` field is dropped; a build record joins its entry only
    when its ``lock_id`` still names that entry.
    """
    if tomllib is None:
        raise ReproStateError(
            "reading pytask.lock needs Python 3.11+ (tomllib); run `superra repro` "
            "through uv so the runner picks a newer interpreter"
        )
    raw_lock = tomllib.loads(lock_text) if lock_text else {}
    try:
        builds = json.loads(builds_text) if builds_text else {}
    except ValueError:
        builds = {}
    builds = builds if isinstance(builds, dict) else {}
    document = empty_lock()
    for raw in raw_lock.get("task", []) or []:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            continue
        name = raw["id"]
        entry = LockEntry(depends_on=dict(raw.get("depends_on") or {}), produces=dict(raw.get("produces") or {}))
        record = builds.get(name)
        if isinstance(record, dict) and record.get("lock_id") == legacy_lock_id(entry.depends_on, entry.produces):
            entry.built_on = {"platform": record.get("platform")}
        document["steps"][name] = lock_record(name, entry)
    return document


_LEGACY_DOCUMENTS: dict[tuple, dict] = {}


def read_lock_document(path: Path) -> dict:
    """The lock at *path* (``repro-lock.json``), or the legacy pair beside it, as one document."""
    legacy = path.parent / LEGACY_LOCK_FILENAME
    try:
        if path.is_file():
            return parse_lock(path.read_text(encoding="utf-8"))
        if legacy.is_file():
            builds = path.parent / LEGACY_BUILDS_FILENAME
            key = (legacy.read_text(encoding="utf-8"),
                   builds.read_text(encoding="utf-8") if builds.is_file() else None)
            if key not in _LEGACY_DOCUMENTS:  # one TOML parse per process, not one per reader
                _LEGACY_DOCUMENTS.clear()
                _LEGACY_DOCUMENTS[key] = convert_legacy(*key)
            document = _LEGACY_DOCUMENTS[key]
            return dict(document, steps=dict(document["steps"]))
    except (OSError, ValueError) as exc:
        source = path if path.is_file() else legacy
        raise ReproStateError(f"{source} could not be read: {exc}") from None
    return empty_lock()


def read_lock(path: Path) -> dict[str, LockEntry]:
    """Step name -> recorded node states, from ``repro-lock.json`` or a legacy ``pytask.lock``."""
    document = read_lock_document(path)
    return {name: lock_entry(name, raw) for name, raw in document["steps"].items()}


def _write_lock_document(paths: RunnerPaths, document: dict) -> None:
    from _repro_acceptance import atomic_json
    atomic_json(paths.lock_file, document)


def write_lock_entry(paths: RunnerPaths, name: str, entry: LockEntry) -> None:
    """Record one step's successful build; the file is rewritten only when the entry changes."""
    with RECORD_LOCK:
        document = read_lock_document(paths.lock_file)
        record = lock_record(name, entry)
        if document["steps"].get(name) == record and paths.lock_file.is_file():
            return
        document["steps"][name] = record
        _write_lock_document(paths, document)


def prune_lock(paths: RunnerPaths, keep: set[str]) -> None:
    """Drop entries of steps no longer in the tree; convert a legacy lock on the way."""
    with RECORD_LOCK:
        if not paths.lock_file.is_file() and not paths.legacy_lock_file.is_file():
            return
        document = read_lock_document(paths.lock_file)
        pruned = {name: raw for name, raw in document["steps"].items() if name in keep}
        if paths.lock_file.is_file() and pruned == document["steps"]:
            return
        document["steps"] = pruned
        _write_lock_document(paths, document)


def write_run_record(paths: RunnerPaths, step: str, record: dict) -> None:
    """Record one step's outcome; one file per step keeps parallel runs race-free."""
    paths.runs_dir.mkdir(parents=True, exist_ok=True)
    from _repro_acceptance import atomic_json
    atomic_json(paths.run_file(step), record)


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
    acceptance: dict | None = None
    local_status: str | None = None
    local_reason: str | None = None
    boundary_inputs: list[dict] = field(default_factory=list)
    external_consumers: list[str] = field(default_factory=list)
    acceptance_invalid: str | None = None
    boundary_verified: list[dict] = field(default_factory=list)  # sidecar saved inputs whose bytes checked out

    def to_dict(self) -> dict:
        return {
            "name": self.step.name,
            "task": self.step.task_path,
            "kind": self.step.kind,
            "cmd": self.step.cmd_logical,
            "status": self.status,
            "reason": self.reason,
            "local_status": self.local_status or self.status,
            "local_reason": self.local_reason or self.reason,
            "boundary_inputs": self.boundary_inputs,
            "external_consumers": self.external_consumers,
            "changes": [c.to_dict() for c in self.changes],
            "duration": self.duration,
            "last_run": self.last_run,
            "log": self.log,
            "acceptance": (
                {key: self.acceptance[key] for key in
                 ("id", "basis", "reason", "reviews", "evidence", "recorded_at", "actor")
                 if key in self.acceptance}
                if self.acceptance else None
            ),
            "deps": [d.to_dict() for d in self.step.deps],
            "outs": [o.to_dict() for o in self.step.outs],
        }


@dataclass
class StatusReport:
    project_root: Path
    graph: Graph
    entries: list[StepStatus] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    selected: set[str] | None = None
    upstream: bool = False
    boundary_inputs: list[dict] = field(default_factory=list)

    @property
    def reported(self) -> list[StepStatus]:
        if self.selected is not None:
            return [e for e in self.entries if e.step.name in self.selected]
        return self.entries

    @property
    def external_inputs(self) -> list:
        """Boundary inputs of the reported steps, so the selection scopes both lists."""
        names = {e.step.name for e in self.reported}
        return [
            e
            for e in self.graph.external_inputs
            if names.intersection(e.consumers)
        ]

    @property
    def ok(self) -> bool:
        from _repro import step_errors
        stale = any(e.status != "fresh" for e in self.reported)
        return not stale and not step_errors(self.graph, {e.step.name for e in self.reported})[0]

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
            "targets": self.targets,
            "upstream": self.upstream,
            "boundary_inputs": self.boundary_inputs,
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
    targets: Iterable[str] = (),
    cache: HashCache | None = None,
    acceptance_ledger: dict | None = None,
    completed_locks: dict[str, LockEntry] | None = None,
    upstream: bool = False,
    scope: Iterable[str] | None = None,
) -> StatusReport:
    """Classify a selection against saved inputs, optionally including producers.

    *scope* widens what counts as in scope for saved inputs beyond the selection:
    a build checks one step at a time, but a producer anywhere in its build
    selection is never a saved input.
    """
    targets = list(targets)
    names, unknown = select_steps(graph, targets, include_ancestors=upstream)
    if unknown:
        raise ReproStateError(f"no step or task matches {', '.join(unknown)}")
    needed = set(names)
    selected = needed
    cache = HashCache(paths.cache_file) if cache is None else cache
    lock = read_lock(paths.lock_file)
    lock.update(completed_locks or {})
    outputs = output_nodes(graph)
    missing_external = {e.path.logical for e in graph.external_inputs if not e.exists}
    memo: dict = {}
    report = StatusReport(
        project_root=paths.project_root, graph=graph,
        targets=targets, selected=selected, upstream=upstream,
    )

    for step in graph.steps:
        if step.name not in needed:
            continue
        entry = _classify(
            step, lock.get(step.name), paths, cache, outputs, missing_external, memo
        )
        entry.external_consumers = external_consumers(graph, step)
        report.entries.append(entry)
    from _repro_scope import boundary_inputs, check_boundary_receipt
    report.boundary_inputs = boundary_inputs(graph, needed | set(scope or ()), paths, cache, lock, consumers=needed)
    for entry in report.entries:
        current_boundary = [b for b in report.boundary_inputs if entry.step.name in b['consumers']]
        check_boundary_receipt(entry, graph, paths, cache, lock.get(entry.step.name), current_boundary)
        entry.boundary_inputs = current_boundary or entry.boundary_inputs
    from _repro_acceptance import apply_to_status
    apply_to_status(report, paths, cache, acceptance_ledger, lock)
    cache.flush()
    return report


def external_consumers(graph: Graph, step: Step) -> list[str]:
    """Steps in other tasks that read *step*'s outs.

    One input to a significance judgment, never the verdict: a selected check,
    a maintained-path producer, and an out a document cites are all significant
    with an empty list here.
    """
    refs = set()
    for src, dst, _ in graph.step_edges:
        if src != step.name:
            continue
        consumer = graph.step(dst)
        if consumer is not None and consumer.task_path != step.task_path:
            refs.add(f"{consumer.task_path or '.'}#{consumer.name}")
    return sorted(refs)


def _classify(
    step: Step,
    entry: LockEntry | None,
    paths: RunnerPaths,
    cache: HashCache,
    outputs: dict[str, Node],
    missing_external: set[str],
    memo: dict,
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

    elsewhere = False
    if entry is None:
        result.status = "missing"
        result.reason = "never built"
    else:
        elsewhere = _compare(result, step, entry, paths, cache, outputs, memo)

    if record.get("outcome") in ("running", "pending"):
        result.status = "failed"
        result.reason = "previous execution was interrupted; rerun required"

    # Restoring inputs can clear an ordinary failure. A forced failure must be
    # retried even with unchanged bytes: it invalidates the cached success. A
    # check that failed here outweighs its pass on another machine.
    if record.get("outcome") == "failed" and (
        result.status != "fresh" or record.get("forced", False) or elsewhere
    ):
        if result.status == "fresh":
            result.reason = "forced rerun required" if record.get("forced", False) else "rerun required"
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
    outputs: dict[str, Node],
    memo: dict,
) -> bool:
    """Set *result* from the lock entry against what is on disk now.

    Returns whether the step is a check that passed at these inputs only elsewhere.
    """
    deps, products = step_nodes(step, outputs)
    absent = [
        node[0]
        for node in products
        if node_state(cache, paths.project_root, node) is None
    ]
    if absent:
        if step.kind == "check" and not _changed_nodes(step, entry, paths, cache, deps, []):
            # The stamp is machine-local; the committed lock says it passed at these inputs.
            from _repro_provenance import check_elsewhere_reason
            result.reason = check_elsewhere_reason(paths, memo, step.name, entry)
            return True
        result.status = "missing"
        result.reason = _plural(f"output {absent[0]} is missing", len(absent) - 1)
        result.changes = [
            Change(node=p, kind="output", change="missing") for p in absent
        ]
        return False

    changes = _changed_nodes(step, entry, paths, cache, deps, products)
    if not changes:
        return False
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
    return False


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
            if recorded_spec == f"{declared}:{resolved}":
                # A runner identity correction can change the key without a
                # declaration edit. Require the engine to record the new key.
                changes.append(Change(node=node[0], kind="dependency", change="added"))
            continue  # a newly declared dep already moved the spec hash
        current = dependency_state(cache, paths.project_root, node, recorded)
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

def bare_step(graph: Graph, name: str) -> Step | None:
    """The active step a bare name selects; archived steps never compete for it."""
    matches = [s for s in graph.steps if s.name == name]
    if len(matches) > 1:
        forms = ", ".join(f"'{s.task_path or '.'}#{s.name}'" for s in matches)
        raise ReproStateError(f"step name {name!r} is ambiguous; select one of {forms}")
    return graph.step(name) if matches else None


def select_steps(
    graph: Graph, targets: Iterable[str], *, include_ancestors: bool = False
) -> tuple[list[str], list[str]]:
    """Resolve build targets to step names, returning (selected, unknown targets).

    A target is a task path (that task and its descendants), a qualified
    ``task#step``, or a bare step name that is unique. Ancestors are opt-in. No targets selects every active step; the CLI
    requires explicit targets.
    """
    targets = [t for t in targets if t]
    unknown: list[str] = []
    selected: set[str] = set()
    if targets:
        for target in targets:
            task_path, sep, step_name = target.partition('#')
            task_path = task_path.removeprefix('./').rstrip('/')
            if task_path == '.':
                task_path = ''
            if sep:
                step = graph.step(step_name)
                if step is not None and step.task_path == task_path:
                    selected.add(step.name)
                else:
                    unknown.append(target)
                continue
            owned = [
                s.name
                for s in graph.steps
                if not task_path or s.task_path == task_path or s.task_path.startswith(f"{task_path}/")
            ]
            task_exists = bool(owned) or not task_path or bool(
                graph.dependencies and task_path in graph.dependencies.tasks
                and task_path not in graph.dependencies.archived
            )
            if owned:
                selected.update(owned)
            elif task_exists:
                raise ReproStateError(f"task {target!r} selects no steps; no result verified")
            else:
                step = bare_step(graph, target)
                if step is not None:
                    selected.add(step.name)
                else:
                    unknown.append(target)
    else:
        selected = {s.name for s in graph.steps}

    if not include_ancestors:
        return [s.name for s in graph.steps if s.name in selected], unknown

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
        return "No steps registered; no result verified."
    width = max(len(e.step.name) for e in entries)
    lines = []
    for entry in sorted(entries, key=lambda e: e.step.name):
        duration = f"  {entry.duration:.1f}s" if entry.duration else ""
        readers = f"outside readers: {len(entry.external_consumers)}"
        lines.append(
            f"{_MARKS[entry.status]} {entry.step.name:<{width}}  "
            f"{entry.status:<8}  {readers:<19}  {entry.reason}{duration}"
        )
    counts = ", ".join(
        f"{sum(1 for e in entries if e.status == name)} {name}"
        for name in STATUSES
        if any(e.status == name for e in entries)
    )
    lines.append("")
    if {s.name for s in report.graph.steps} <= {e.step.name for e in entries}:
        scope = "for every registered step"
    else:
        scope = f"for {', '.join(report.targets)}"
        scope += " (including producer ancestors)" if report.upstream else " (selected steps only)"
    lines.append(f"{len(entries)} step(s) {scope}: {counts}")
    if report.boundary_inputs:
        lines.append("Saved inputs from outside scope (upstream freshness not verified):")
        for item in report.boundary_inputs:
            lines.append(f"  {item['logical']} — {item['producer']}: {item['provenance']}")
    missing = [e for e in report.external_inputs if not e.exists]
    if missing:
        lines.append("")
        lines.append("Missing external inputs:")
        lines.extend(f"  {e.path.logical}" for e in missing)
    errors = [f for f in report.graph.findings if f.severity == "error"]
    if errors:
        lines.append("")
        lines.append(f"{len(errors)} graph error(s); run `superra task check`.")
    stale = {e.step.name for e in entries if e.status != "fresh"}
    pointed = [t for t in (report.targets or ["."])
               if stale & set(select_steps(report.graph, [t], include_ancestors=report.upstream)[0])]
    if pointed:
        lines.append("Why not fresh: " + "; ".join(f"superra repro explain {shlex.quote(t)}" for t in pointed))
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
            f"{s.name}  ({s.task_path or '(root)'})"
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
        style = ":::check" if step.kind == "check" else ""
        lines.append(f'    {node}["{step.name}"]{style}')
    for src, dst, via in edges:
        label = via.rsplit("/", 1)[-1]
        lines.append(f"    {_MERMAID_ID_RE.sub('_', src)} -->|{label}| {_MERMAID_ID_RE.sub('_', dst)}")
    lines.append("")
    lines.append("    classDef check fill:#bbdefb,stroke:#1976d2,color:#0d47a1")
    return "\n".join(lines)


__all__ = [
    "Change",
    "HashCache",
    "LOCK_FILENAME",
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
    "external_consumers",
    "format_status",
    "node_state",
    "path_state",
    "lock_entry",
    "prune_lock",
    "read_lock",
    "read_lock_document",
    "write_lock_entry",
    "read_run_record",
    "render_dag",
    "runner_paths",
    "output_nodes",
    "select_steps",
    "spec_hash",
    "spec_node_id",
    "step_nodes",
    "stamp_ref",
    "write_run_record",
]
