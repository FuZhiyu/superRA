#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""The `superra repro` command surface: build, status, explain, dag.

`cli.py` routes `repro` here. Every subcommand is stdlib-only (with lazy
pyyaml) and runs on Python 3.10, except that reading a legacy ``pytask.lock``
needs ``tomllib``: then ``main`` re-execs this script through
``uv run --script``, whose block above asks for Python 3.11+.

``build`` runs the selected steps itself, in dependency order, one subprocess
per step (threads under ``-j``). It decides run or skip per step with the
``compute_status`` rule ``status`` reports, and writes each successful step's
entry into ``repro-lock.json`` as the step completes.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _repro import Graph, Out, Step, build_graph, step_errors  # noqa: E402
from _repro_acceptance import capture_receipt, check_sources, current_state, mutation_lock, supersede  # noqa: E402
from _repro_builds import platform_name  # noqa: E402
from _repro_scope import boundary_inputs, record_verified_inputs  # noqa: E402
from _repro_state import (  # noqa: E402
    LOCK_FILENAME,
    TOML_AVAILABLE,
    HashCache,
    Unread,
    LockEntry,
    ReproStateError,
    RunnerPaths,
    absolute,
    compute_status,
    dependency_state,
    directory_dep_nodes,
    ensure_state_dir,
    format_status,
    node_sizes,
    output_nodes,
    prune_lock,
    read_lock,
    read_run_record,
    render_dag,
    runner_paths,
    select_steps,
    spec_hash,
    stamp_ref,
    step_nodes,
    unread,
    unread_phrase,
    write_lock_entry,
    write_run_record,
)
from _task_io import TASK_ROOT_DIRNAME, resolve_plan_root_arg  # noqa: E402

REEXEC_ENV = "SUPERRA_REPRO_REEXEC"
NO_TARGET_ERROR = "name at least one task or task#step target; '.' selects every registered step"
TIER_RETIRED_ERROR = "reproduction tiers are retired; name task or task#step targets instead ('.' selects every registered step)"


class StepFailed(RuntimeError):
    """A step command exited non-zero."""


class NotStarted(Exception):
    """The build was interrupted before this step's attempt began."""


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

@dataclass
class Build:
    """One `repro build` invocation: its selection, the runs in flight, and outcomes."""

    graph: Graph
    paths: RunnerPaths
    names: list[str]
    cache: HashCache
    forced: set[str]
    dry_run: bool
    completed: dict[str, LockEntry] = field(default_factory=dict)
    outcomes: dict[str, tuple[str, str]] = field(default_factory=dict)  # name -> (outcome, detail)
    stopping: threading.Event = field(default_factory=threading.Event)
    running: dict[str, subprocess.Popen] = field(default_factory=dict)
    running_lock: threading.Lock = field(default_factory=threading.Lock)

    def target(self, step: Step) -> str:
        return f"{step.task_path or '.'}#{step.name}"

    def parents(self) -> dict[str, list[str]]:
        """Each selected step's producers inside the selection (directory outs included)."""
        selected = set(self.names)
        parents: dict[str, list[str]] = {name: [] for name in self.names}
        for src, dst, _ in self.graph.step_edges:
            if src in selected and dst in selected and src not in parents[dst]:
                parents[dst].append(src)
        return parents


def _decide(build: Build, step: Step):
    """This step's status under the rule `status` applies, over the whole build selection."""
    return compute_status(
        build.graph, build.paths, targets=[build.target(step)], cache=build.cache,
        completed_locks=build.completed, scope=build.names,
    ).entry(step.name)


def _missing_inputs(build: Build, step: Step, entry) -> str | None:
    """Why the step cannot start: a dependency not on disk, online-only even if cached, or unreadable."""
    root = build.paths.project_root
    deps, _ = step_nodes(step, output_nodes(build.graph))
    deps += directory_dep_nodes(build.graph, step)
    externals = {e.path.logical for e in build.graph.external_inputs}
    states = [(node[0], Unread("online-only")
               if build.cache.probe(absolute(root, node[2] or node[1]), walk=True)[0]
               else dependency_state(build.cache, root, node)) for node in deps]
    blocked = [(n, v) for n, v in states if v is None] or [(n, v) for n, v in states if unread(v)]
    if not blocked:
        return None
    node, value = blocked[0]
    why = "missing" if value is None and node not in externals else unread_phrase(value)
    more = f" (and {len(blocked) - 1} more)" if len(blocked) > 1 else ""
    return f"input {node} is {why}{more}"


def _run_step(build: Build, step: Step, entry) -> str:
    """Execute one step; returns the outcome (`executed` / `unchanged` / `would execute`)."""
    graph, paths = build.graph, build.paths
    check_sources(graph)
    forced = step.name in build.forced
    if not forced and entry.status == "fresh":
        if entry.boundary_verified and not build.dry_run:
            record_verified_inputs(paths, step.name, read_lock(paths.lock_file).get(step.name),
                                   entry.boundary_verified)
        return "unchanged"
    if not forced and entry.status == "unverified":
        return "unverified"  # never run on files this machine cannot check; its outputs are used as they are
    if build.dry_run:
        blocked = _missing_inputs(build, step, entry)
        if blocked:
            raise ReproStateError(f"step {step.name!r} cannot start: {blocked}")
        return "would execute"
    if build.stopping.is_set():  # before supersede and the run record touch anything
        raise NotStarted
    blocked = _missing_inputs(build, step, entry)
    if blocked:
        raise ReproStateError(f"step {step.name!r} cannot start: {blocked}")
    # A rerun an acceptance or an unverified saved input required stays owed
    # if it fails, like a forced one: restored bytes must not read as fresh.
    must_retry = forced or bool(entry.acceptance_invalid) or any(c.kind == "boundary" for c in entry.changes)
    committed = False
    try:
        log_path = paths.log_file(step.name)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        for out in step.outs:
            absolute(paths.project_root, out.path.resolved).parent.mkdir(parents=True, exist_ok=True)
            if out.sidecar is not None:
                absolute(paths.project_root, out.sidecar.resolved).parent.mkdir(parents=True, exist_ok=True)
        sidecar_before = {
            out.path.logical: _mtime(absolute(paths.project_root, out.sidecar.resolved))
            for out in step.outs
            if out.sidecar is not None
        }
        before = current_state(graph, step, paths, recorded=False)
        before["boundary_inputs"] = boundary_inputs(graph, build.names, paths, consumers={step.name})

        started = time.time()
        write_run_record(paths, step.name, {"outcome": "running", "forced": must_retry, "started_at": started,
                                            "pid": os.getpid()})
        with log_path.open("w", encoding="utf-8") as log:
            log.write(f"$ {step.cmd}\n")
            log.flush()
            with build.running_lock:
                if build.stopping.is_set():
                    raise StepFailed(f"step {step.name!r} was interrupted before it started")
                supersede(paths, step.name)  # acceptance survives until the step is committed to run
                committed = True
                process = subprocess.Popen(  # noqa: S602 - a declared shell step
                    step.cmd, shell=True, cwd=str(paths.project_root),
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                )
                build.running[step.name] = process
            try:
                returncode = process.wait()
            finally:
                with build.running_lock:
                    build.running.pop(step.name, None)
        record = {
            "outcome": "pending" if returncode == 0 else "failed",
            "forced": must_retry,
            "pid": os.getpid(),
            "exit_code": returncode,
            "duration": time.time() - started,
            "ended_at": time.time(),
            "log": paths.log_ref(step.name),
        }
        write_run_record(paths, step.name, record)
        if build.stopping.is_set():
            raise StepFailed(f"step {step.name!r} was interrupted; see {paths.log_ref(step.name)}")
        if returncode != 0:
            raise StepFailed(f"step {step.name!r} exited {returncode}; see {paths.log_ref(step.name)}")

        for out in step.outs:
            if out.sidecar is None:
                continue
            sidecar = absolute(paths.project_root, out.sidecar.resolved)
            if _mtime(sidecar) != sidecar_before[out.path.logical]:
                continue  # the step maintains its own sidecar
            _write_sidecar(paths.project_root, out, sidecar, build.cache)
        if step.kind == "check":
            stamp = paths.project_root / stamp_ref(step.name)
            stamp.parent.mkdir(parents=True, exist_ok=True)
            stamp.write_text(f"{spec_hash(step)}\n", encoding="utf-8")

        check_sources(graph)
        receipt = capture_receipt(graph, step, paths, before)
    except BaseException as exc:
        if committed or not build.stopping.is_set():
            supersede(paths, step.name)  # a failed step owes a rerun; an interrupt before its start does not
        record = read_run_record(paths, step.name)
        record.update(outcome="failed", forced=must_retry or record.get("forced", False), error=str(exc))
        write_run_record(paths, step.name, record)
        raise
    deps, products = step_nodes(step, output_nodes(graph))
    entry = LockEntry(depends_on=receipt["state"]["deps"], produces=receipt["state"]["products"],
                      built_on={"platform": platform_name()},
                      sizes=node_sizes(build.cache, paths.project_root,
                                       deps + directory_dep_nodes(graph, step) + products))
    write_lock_entry(paths, step.name, entry)
    build.completed[step.name] = entry
    record = read_run_record(paths, step.name)
    record["outcome"] = "success"
    write_run_record(paths, step.name, record)
    return "executed"


def _write_sidecar(project_root: Path, out: Out, sidecar: Path, cache: HashCache) -> None:
    """Record the out's content hash so later runs never read the large file."""
    digest = cache.path_state(absolute(project_root, out.path.resolved))
    if digest is None or unread(digest):
        return
    sidecar.write_text(f"{digest}  {out.path.logical}\n", encoding="utf-8")


def _mtime(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return None


def _stop(build: Build) -> None:
    """Ctrl-C: start nothing new and stop every running step's process group."""
    build.stopping.set()
    with build.running_lock:
        processes = list(build.running.values())
    for process in processes:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            pass


def _schedule(build: Build, n_workers: int) -> None:
    """Run the selection in dependency order; a failure skips its descendants only."""
    parents = build.parents()
    order = {name: index for index, name in enumerate(build.names)}
    pending = list(build.names)
    futures: dict = {}
    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        try:
            while pending or futures:
                for name in list(pending):
                    states = [build.outcomes.get(parent, ("",))[0] for parent in parents[name]]
                    culprit = next((p for p, state in zip(parents[name], states) if state in ("failed", "skipped")), None)
                    if culprit is not None:
                        build.outcomes[name] = ("skipped", f"ancestor {culprit} did not complete")
                        pending.remove(name)
                    elif build.dry_run and "would execute" in states:
                        build.outcomes[name] = ("would execute", "")
                        pending.remove(name)
                    elif all(parent in build.outcomes for parent in parents[name]) and not build.stopping.is_set():
                        step = build.graph.step(name)
                        futures[pool.submit(_attempt, build, step)] = name
                        pending.remove(name)
                if build.stopping.is_set():
                    for name in pending:
                        build.outcomes[name] = ("skipped", "build interrupted")
                    pending.clear()
                if not futures:
                    for name in pending:  # only a dependency cycle leaves nothing runnable
                        build.outcomes[name] = ("skipped", "dependency cycle")
                    pending.clear()
                    continue
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in sorted(done, key=lambda f: order[futures[f]]):
                    name = futures.pop(future)
                    build.outcomes[name] = future.result()
                    _report(build, name)
        except KeyboardInterrupt:
            _stop(build)
            for future in list(futures):
                name = futures.pop(future)
                if future.cancel():  # still queued behind the workers
                    build.outcomes[name] = ("skipped", "build interrupted")
                    continue
                try:
                    build.outcomes[name] = future.result()
                except KeyboardInterrupt:
                    build.outcomes[name] = ("failed", "interrupted")
            for name in pending:
                build.outcomes[name] = ("skipped", "build interrupted")
            raise


@contextmanager
def _interrupt_on_termination():
    """SIGTERM and SIGHUP stop the build as Ctrl-C does, so no step outlives it."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def interrupt(signum, frame):
        raise KeyboardInterrupt

    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGTERM, signal.SIGHUP)}
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def _attempt(build: Build, step: Step) -> tuple[str, str]:
    try:
        entry = _decide(build, step)
        return _run_step(build, step, entry), ""
    except NotStarted:
        return "skipped", "build interrupted"
    except (StepFailed, ReproStateError, OSError) as exc:
        return "failed", f"{type(exc).__name__}: {exc}"


_MARKS = {"executed": "✓", "unchanged": "·", "unverified": "○", "would execute": "~", "failed": "✗", "skipped": "-"}


def _report(build: Build, name: str) -> None:
    outcome, detail = build.outcomes[name]
    if build.dry_run:
        return
    print(f"{_MARKS[outcome]} {name}  {outcome}" + (f"\n  {detail}" if detail else ""), flush=True)


def run_build(
    graph: Graph,
    paths: RunnerPaths,
    names: list[str],
    *,
    n_workers: int = 1,
    force_names: list[str] | None = None,
    dry_run: bool = False,
) -> int:
    """Run every stale selected step; 0 when none failed, else 1."""
    from _repro_scope import BuildGuard
    graph._execution_names = frozenset(names)
    if graph.dependencies:
        signature = getattr(graph, '_acceptance_sources', (None, None))[1]
        graph._build_guard = BuildGuard(graph, graph.dependencies.tasks[""].dir_path, names, signature)
    check_sources(graph)
    cache = HashCache(paths.cache_file)
    boundary = boundary_inputs(graph, names, paths, cache)
    print('Execution scope: ' + ', '.join(names))
    for item in boundary:
        print(f"Saved input: {item['logical']} from {item['producer']} ({item['provenance']}; upstream not verified)")
    missing = [item for item in boundary if item['digest'] is None and not item.get('here')]
    if missing:
        raise ReproStateError('missing saved inputs: ' + ', '.join(f"{b['logical']} (producer {b['producer']})" for b in missing)
                              + '; select the producer or use --upstream')
    forced = set(force_names or ())
    forced.update(
        name for name in names
        if (record := read_run_record(paths, name)).get("outcome") in ("running", "pending")
        or (record.get("outcome") == "failed" and record.get("forced", False))
    )
    build = Build(graph=graph, paths=paths, names=list(names), cache=cache, forced=forced, dry_run=dry_run)
    interrupted = False
    with mutation_lock(paths), _interrupt_on_termination():
        try:
            _schedule(build, n_workers)
        except KeyboardInterrupt:
            interrupted = True
        if not dry_run and not interrupted:
            prune_lock(paths, {s.name for s in graph.steps} | {s.name for s in graph.archived_steps})
    cache.flush()
    if dry_run:
        pending = [name for name in names if build.outcomes.get(name, ("",))[0] == "would execute"]
        blocked = [name for name in names if build.outcomes.get(name, ("",))[0] in ("failed", "skipped")]
        for name in blocked:
            print(f"{_MARKS['failed']} {name}  cannot run\n  {build.outcomes[name][1]}")
        if pending or not blocked:
            print(format_cost(pending, paths))
        return 1 if blocked else 0
    counts = {}
    for outcome, _ in build.outcomes.values():
        counts[outcome] = counts.get(outcome, 0) + 1
    print(f"{len(names)} step(s): " + ", ".join(
        f"{counts[k]} {k}" for k in ("executed", "unchanged", "unverified", "failed", "skipped") if counts.get(k)))
    if interrupted:
        print("Interrupted: running steps were stopped and recorded as failed.", file=sys.stderr)
    legacy = [p.name for p in (paths.legacy_lock_file, paths.legacy_builds_file) if p.is_file()]
    if paths.lock_file.is_file() and legacy:
        print(f"{LOCK_FILENAME} now holds the build records; {', '.join(legacy)} no longer read. "
              f"Remove with `git rm {' '.join(legacy)}`.")
    return 1 if interrupted or counts.get("failed") or counts.get("skipped") else 0


# ---------------------------------------------------------------------------
# Decision support
# ---------------------------------------------------------------------------

def format_cost(names: list[str], paths: RunnerPaths) -> str:
    """What a `build --dry-run` would cost, from each step's last recorded run."""
    if not names:
        return "Nothing to execute: every selected step is fresh."
    width = max(len(name) for name in names)
    lines = [f"Would execute {len(names)} step(s):"]
    total = 0.0
    unknown = 0
    for name in names:
        duration = read_run_record(paths, name).get("duration")
        if duration is None:
            unknown += 1
            lines.append(f"  {name:<{width}}  unknown")
        else:
            total += duration
            lines.append(f"  {name:<{width}}  {duration:.1f}s")
    known = len(names) - unknown
    tail = f", plus {unknown} step(s) with no recorded duration" if unknown else ""
    lines.append(
        f"Last recorded cost: {total:.1f}s{tail}." if known
        else f"No step has a recorded duration; {unknown} step(s) never ran."
    )
    lines.append(
        "Alternatives: `superra repro explain <task>#<step>` for why a step is stale; "
        "`superra repro accept <target> --reason ...` to record the current results "
        "as reviewed instead of rerunning."
    )
    return "\n".join(lines)


def format_accept(result: dict) -> str:
    """Exactly which steps the acceptance covered, and what changed under each."""
    rows = result["steps"]
    written = sum(row["record"] is not None for row in rows)
    lines = [
        f"Accepted {written} step(s) as the reviewed baseline."
        if result.get("applied") else
        f"Would accept {written} step(s); no record was written."
    ]
    if result["reason"]:
        lines.append(f"  reason: {result['reason']}")
    width = max((len(row["step"]) for row in rows), default=0)
    for row in rows:
        changes = ", ".join(f"{c['kind']} {c['node']}" for c in row["changes"])
        if row["record"] is None:
            changes = "already fresh; its evidence stays as it is"
        lines.append(f"  {row['step']:<{width}}  {changes or 'unchanged since the recorded baseline'}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

MODEL = """\
Steps belong to tasks: a task's `## Reproduction` section registers its steps.
`build` runs them in dependency order, one subprocess per step.
A step is fresh when the content hashes of its deps, definition, and outs match
its last successful build or its reviewed acceptance.
Targets scope every command: a task path selects its own and descendant steps,
`task#step` or a unique step name selects one step, `.` selects the whole active tree. Files read from
producers outside the scope are saved inputs, used as they sit on disk.
A stale step is resolved two ways: execute it with `build`, or record the
current results as reviewed with `accept --reason ...`.
"""


def _sub(sub, name: str, purpose: str, examples: list[str]):
    return sub.add_parser(
        name,
        help=purpose,
        description=purpose + ".",
        epilog="Examples:\n" + "".join(f"  {line}\n" for line in examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="superra repro",
        description="Build and inspect the reproduction graph.\n\n" + MODEL,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--plan-root",
        "--root",
        dest="plan_root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = _sub(sub, "build", "Execute every stale step in the target scope", [
        "superra repro build 02-merge -j 4",
        "superra repro build 02-merge --upstream    # also its stale producers",
        "superra repro build 02-merge --dry-run     # what would run, and what it last cost",
        "superra repro build '02-merge#check-panel' --force",
    ])
    build.add_argument("targets", nargs="*", help="Task paths (including descendants), task#step selectors, or unique step names")
    build.add_argument("--upstream", action="store_true", help="Include transitive file-producer ancestors")
    build.add_argument("-j", "--jobs", type=int, default=1, dest="jobs")
    build.add_argument("--force", action="store_true", help="Rerun every step in the selected scope, including ancestors only with --upstream")
    build.add_argument("--dry-run", action="store_true", help="Report what would run and its last recorded cost")

    status = _sub(sub, "status", "Report each selected step's freshness and outside readers", [
        "superra repro status .",
        "superra repro status 02-merge '02-merge#check-panel'",
        "superra repro status . --upstream --json",
    ])
    status.add_argument("targets", nargs="*", help="Task paths, task#step selectors, or unique step names; saved inputs outside scope")
    status.add_argument("--upstream", action="store_true", help="Also assess transitive producer ancestors")
    status.add_argument("--json", action="store_true", dest="as_json")

    explain = _sub(sub, "explain", "Explain where each changed hash came from, with a next command per cause", [
        "superra repro explain 02-merge                 # causes grouped across the task's steps",
        "superra repro explain '02-merge#build-panel'   # one row per changed node",
        "superra repro explain build-panel              # a unique bare step name",
        "superra repro explain Output/panel.parquet     # a file's provenance, producer, and readers",
        "superra repro explain 02-merge --json --diff",
    ])
    explain.add_argument("target", help="A task path, task#step, unique step name, or declared file path")
    explain.add_argument("--diff", action="store_true", help="Show dependency diffs: in full for a step or file, and at all for a task (task views omit them by default)")
    explain.add_argument("--json", action="store_true", dest="as_json")

    impact = _sub(sub, "impact", "Predict which steps a change to a file would make stale, with recorded durations", [
        "superra repro impact Code/helpers.jl",
        "superra repro impact superRA/config.yaml       # steps using a runner, a variable, or env_deps",
        "superra repro impact Code/helpers.jl --scope 02-merge --json",
    ])
    impact.add_argument("paths", nargs="+")
    impact.add_argument("--scope", action="append", default=[], help="Repeatable task or task#step selection")
    impact.add_argument("--json", action="store_true", dest="as_json")

    accept = _sub(sub, "accept", "Record the current results as the reviewed baseline", [
        "superra repro accept 02-merge --reason 'Ran interactively and reviewed the panel'",
        "superra repro accept 02-merge --dry-run    # preview; writes nothing",
    ])
    accept.add_argument("targets", nargs="+", help="Task paths, task#step selectors, or unique step names")
    accept.add_argument("--reason", default="", help="Why the current results are valid (required to accept)")
    accept.add_argument("--review", action="append", default=[], metavar="NODE=RATIONALE", help="Optional per-node review note")
    accept.add_argument("--dry-run", action="store_true", help="Preview; write nothing")
    accept.add_argument("--json", action="store_true", dest="as_json")

    revoke = _sub(sub, "revoke", "Revoke selected step acceptances", [
        "superra repro revoke 02-merge",
    ])
    revoke.add_argument("targets", nargs="+", help="Task paths, task#step selectors, or unique step names")
    revoke.add_argument("--json", action="store_true", dest="as_json")

    dag = _sub(sub, "dag", "Render the step graph", [
        "superra repro dag",
        "superra repro dag --mermaid",
    ])
    dag.add_argument("--mermaid", action="store_true")
    return parser


LOCK_READERS = ("build", "status", "explain", "accept", "revoke", "impact")


def _reexec(argv: list[str], command: str) -> int:
    """Re-run this script under uv, whose PEP 723 block asks for Python 3.11+ (tomllib)."""
    missing = "Python 3.11+ (tomllib) to read the legacy pytask.lock"
    if os.environ.get(REEXEC_ENV):
        print(
            f"Error: {missing} is still unavailable after the runner re-execed; "
            f"make `uv` available on PATH.",
            file=sys.stderr,
        )
        return 1
    uv = shutil.which("uv")
    if uv is None:
        print(
            f"Error: `superra repro {command}` needs {missing}. Install `uv`, which "
            f"lets the runner provision it, or run superRA on Python 3.11 or newer.",
            file=sys.stderr,
        )
        return 1
    env = dict(os.environ, **{REEXEC_ENV: "1"})
    completed = subprocess.run(  # noqa: S603
        [uv, "run", "--script", str(Path(__file__).resolve()), *argv], env=env, check=False
    )
    return completed.returncode


def _behind_selection(graph, paths: RunnerPaths, targets: list[str], report) -> list:
    """Producers outside the selection, behind it, that are not fresh."""
    from _repro_acceptance import lock_holder
    full = compute_status(graph, paths, targets=targets, upstream=True, live_build=lock_holder(paths))
    return [e for e in full.entries if e.step.name not in report.selected and e.status != "fresh"]


def _explain(args, graph, paths: RunnerPaths, plan_name: str) -> None:
    from _repro_provenance import explain, format_explain, resolve_target, target_ref
    kind, value = resolve_target(graph, args.target, paths.project_root)
    if kind == "step":
        targets = [target_ref(graph.step(value))]
    elif kind == "task":
        targets = [target_ref(graph.step(name)) for name in value[1]]
    else:
        targets = [target_ref(s) for s in ([value["producer"]] if value["producer"] else []) + value["consumers"]]
    from _repro_acceptance import lock_holder
    cache = HashCache(paths.cache_file)
    report = compute_status(graph, paths, targets=targets, cache=cache, upstream=True,
                            live_build=lock_holder(paths))
    result = explain(report, paths, cache, kind, value, full_diff=args.diff, plan_name=plan_name)
    cache.flush()
    if args.as_json:
        if kind == "step":
            step = result.pop("steps")[0]
            result = dict(step, **result)
        print(json.dumps(result, indent=2))
    else:
        print(format_explain(result, report, full_diff=args.diff))
    if result["errors"]:
        sys.exit(1)


def _refuse(errors) -> None:
    """Exit on reproduction errors that touch the build selection."""
    if errors:
        print(f"Error: {len(errors)} reproduction error(s) touch the selected steps; "
              "run `superra task check`.", file=sys.stderr)
        for finding in errors:
            print(f"  {finding.to_text()}", file=sys.stderr)
        sys.exit(1)


def _command_word(argv: list[str]) -> str | None:
    args = iter(argv)
    for arg in args:
        if arg in ("--plan-root", "--root"):
            next(args, None)
        elif not arg.startswith("-"):
            return arg
    return None


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if _command_word(argv) == "tier" or any(a == "--tier" or a.startswith("--tier=") for a in argv):
        build_parser().error(TIER_RETIRED_ERROR)
    args = build_parser().parse_args(argv)
    if args.command in ('build', 'status') and not args.targets:
        build_parser().error(NO_TARGET_ERROR)

    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --root.", file=sys.stderr)
        sys.exit(1)
    if not plan_root.is_dir():
        print(f"Error: task root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)
    project_root = plan_root.resolve().parent
    paths = runner_paths(project_root)
    if args.command in LOCK_READERS and not TOML_AVAILABLE and paths.reads_legacy_lock:
        sys.exit(_reexec(argv, args.command))

    from _repro_acceptance import bind_sources, source_signature
    signature = source_signature(plan_root) if args.command in ("build", "accept") else None
    graph = build_graph(plan_root, project_root=project_root)
    if signature is not None:
        bind_sources(graph, plan_root, signature)

    if args.command == "dag":
        print(render_dag(graph, mermaid=args.mermaid))
        return

    if graph.steps:
        ensure_state_dir(paths)

    if args.command in ("impact", "accept", "revoke"):
        from _repro_acceptance import accept, format_impact, impact, revoke
        try:
            if args.command == "impact":
                result = impact(graph, paths, args.paths, args.scope, config_file=plan_root / "config.yaml")
            elif args.command == "revoke":
                result = revoke(graph, paths, args.targets)
            else:
                reviews = {}
                for item in args.review:
                    node, sep, rationale = item.partition("=")
                    if not sep or not rationale.strip():
                        raise ReproStateError("--review expects NODE=RATIONALE")
                    reviews[node] = rationale
                result = accept(graph, paths, args.targets, args.reason, reviews, dry_run=args.dry_run)
            if args.command == "accept" and not args.as_json:
                print(format_accept(result))
            elif args.command == "impact" and not args.as_json:
                print(format_impact(result))
            else:
                print(json.dumps(result, indent=2))
            return
        except ReproStateError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    if args.command == "build":
        tasks = {"" if t in (".", "./") else t.partition("#")[0].removeprefix("./").rstrip("/")
                 for t in args.targets}
        try:
            names, unknown = select_steps(graph, args.targets, include_ancestors=args.upstream)
        except ReproStateError as exc:
            _refuse(step_errors(graph, [], tasks)[0])
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        errors, notes = step_errors(graph, names, tasks)
        _refuse(errors)
        for note in notes:
            print(f"Warning: {note}", file=sys.stderr)
        if unknown:
            print(
                f"Error: no step or task matches {', '.join(unknown)}", file=sys.stderr
            )
            sys.exit(1)
        if not names:
            print("No steps registered.")
            return
        force_names = names if args.force else []
        try:
            result = run_build(
                graph,
                paths,
                names,
                n_workers=max(1, args.jobs),
                force_names=force_names,
                dry_run=args.dry_run,
            )
        except ReproStateError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        sys.exit(result)

    try:
        if args.command == "explain":
            _explain(args, graph, paths, plan_root.name)
            return
        from _repro_acceptance import lock_holder
        report = compute_status(graph, paths, targets=args.targets, upstream=args.upstream,
                                live_build=lock_holder(paths))
        behind = [] if args.upstream or not report.ok else _behind_selection(graph, paths, args.targets, report)
    except ReproStateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.as_json:
        result = report.to_dict()
        result["behind"] = [{"name": e.step.name, "task": e.step.task_path, "status": e.status} for e in behind]
        print(json.dumps(result, indent=2))
    else:
        print(format_status(report))
        if behind:
            names = ", ".join(f"{e.step.name} ({e.status})" for e in behind)
            print(f"{len(behind)} producer(s) behind the selection not fresh: {names}; "
                  "include them with --upstream")
    sys.exit(1 if not report.ok else 3 if behind else 0)


if __name__ == "__main__":
    main()
