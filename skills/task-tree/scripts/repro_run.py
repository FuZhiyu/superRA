#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytask>=0.6,<0.7", "pytask-parallel", "pyyaml"]
# ///
"""The `superra repro` command surface: build, status, explain, dag, tier.

`cli.py` routes `repro` here. Only ``build`` imports pytask; when the current
interpreter cannot (``cli.py`` declares pyyaml alone), ``main`` re-execs this
script through ``uv run --script``, which provisions the block above. Every
other subcommand answers from ``_repro_state`` and stays stdlib-only.

Engine bridge: one in-memory pytask task per step, never a ``task_*.py`` in the
project. Nodes are runner-owned so their lock ids are the logical
(``${VAR}``-form) paths while hashing follows the resolved ones.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).parent))

from _repro import TIER_INPUTS, Graph, Out, Step, build_graph, normalize_tier  # noqa: E402
from _repro_state import (  # noqa: E402
    TOML_AVAILABLE,
    HashCache,
    ReproStateError,
    RunnerPaths,
    Node,
    absolute,
    compute_status,
    directory_dep_nodes,
    ensure_state_dir,
    format_explain,
    format_status,
    read_run_record,
    render_dag,
    runner_paths,
    select_steps,
    set_tier,
    output_nodes,
    spec_hash,
    spec_node_id,
    stamp_ref,
    step_nodes,
    write_run_record,
)
from _task_io import TASK_ROOT_DIRNAME, resolve_plan_root_arg  # noqa: E402

REEXEC_ENV = "SUPERRA_REPRO_REEXEC"
TIERS = (*TIER_INPUTS, "all")


# ---------------------------------------------------------------------------
# pytask node and task types
# ---------------------------------------------------------------------------

@dataclass
class FileNode:
    """A file or directory node whose lock id is its logical path.

    Deliberately not a ``PPathNode``: pytask derives a path node's lock id from
    its resolved path, which would embed the author or branch a ``${VAR}``
    expanded to. Keeping the id in ``name`` keeps the committed lock portable.

    ``must_exist`` is the out itself when a sidecar is hashed in its place, so
    a deleted out is missing rather than fresh.
    """

    name: str
    resolved: Path
    cache: HashCache
    must_exist: Path | None = None
    attributes: dict = field(default_factory=dict)

    @property
    def signature(self) -> str:
        return hashlib.sha256(self.name.encode("utf-8")).hexdigest()

    def state(self) -> str | None:
        if self.must_exist is not None and not self.must_exist.exists():
            return None
        return self.cache.path_state(self.resolved)

    def load(self, is_product: bool = False) -> Path:  # noqa: ARG002
        return self.resolved

    def save(self, value: Any) -> None:  # pragma: no cover - never a return target
        raise NotImplementedError("reproduction outs are written by the step command")


@dataclass
class SpecNode:
    """The resolved step definition — cmd, params, deps, outs — as one hash.

    Every generated task shares one function, so pytask's task state cannot
    tell two steps apart. This node supplies that granularity: editing one
    step's definition invalidates that step and nothing else.
    """

    name: str
    value: str
    attributes: dict = field(default_factory=dict)

    @property
    def signature(self) -> str:
        return hashlib.sha256(self.name.encode("utf-8")).hexdigest()

    def state(self) -> str | None:
        return self.value

    def load(self, is_product: bool = False) -> str:  # noqa: ARG002
        return self.value

    def save(self, value: Any) -> None:  # pragma: no cover - never a return target
        raise NotImplementedError


@dataclass(kw_only=True)
class StepTask:
    """One reproduction step as a pytask task.

    The stable state keeps runner upgrades from invalidating project work.
    Forced targets advertise a transient change, cleared after execution so
    the successful lock retains the stable state. Each task owns its flag.
    """

    name: str
    function: Callable[..., Any]
    depends_on: dict = field(default_factory=dict)
    produces: dict = field(default_factory=dict)
    markers: list = field(default_factory=list)
    report_sections: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    force_pending: bool = False

    def __post_init__(self) -> None:
        command = self.function

        # pytask-parallel calls function directly, bypassing execute.
        def execute(**kwargs: Any) -> Any:
            result = command(**kwargs)
            self.force_pending = False
            return result

        self.function = execute

    @property
    def signature(self) -> str:
        return hashlib.sha256(f"step:{self.name}".encode()).hexdigest()

    def state(self) -> str | None:
        return "forced" if self.force_pending else "1"

    def execute(self, **kwargs: Any) -> Any:
        return self.function(**kwargs)


class StepFailed(RuntimeError):
    """A step command exited non-zero."""


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def _run_step(
    step: Step, paths: RunnerPaths, cache: HashCache, *, forced: bool = False,
    graph: Graph | None = None, attributes: dict | None = None
) -> Callable[..., None]:
    """Build the callable pytask executes for *step*."""

    def _execute(deps, spec):  # noqa: ARG001 - pytask injects both by name
        log_path = paths.log_file(step.name)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        for out in step.outs:
            absolute(paths.project_root, out.path.resolved).parent.mkdir(
                parents=True, exist_ok=True
            )
            if out.sidecar is not None:
                absolute(paths.project_root, out.sidecar.resolved).parent.mkdir(
                    parents=True, exist_ok=True
                )
        sidecar_before = {
            out.path.logical: _mtime(absolute(paths.project_root, out.sidecar.resolved))
            for out in step.outs
            if out.sidecar is not None
        }

        from _repro_acceptance import current_state
        if graph is not None and attributes is not None:
            attributes["superra_before"] = current_state(graph, step, paths)
        must_retry = forced or bool((attributes or {}).get("superra_retry_required"))
        started = time.time()
        write_run_record(paths, step.name, {"outcome": "running", "forced": must_retry, "started_at": started})
        with log_path.open("w", encoding="utf-8") as log:
            log.write(f"$ {step.cmd}\n")
            log.flush()
            completed = subprocess.run(  # noqa: S602 - a declared shell step
                step.cmd,
                shell=True,
                cwd=str(paths.project_root),
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        duration = time.time() - started
        record = {
            "outcome": "pending" if completed.returncode == 0 else "failed",
            "forced": must_retry,
            "exit_code": completed.returncode,
            "duration": duration,
            "ended_at": time.time(),
            "log": paths.log_ref(step.name),
        }
        write_run_record(paths, step.name, record)
        if completed.returncode != 0:
            raise StepFailed(
                f"step {step.name!r} exited {completed.returncode}; see "
                f"{paths.log_ref(step.name)}"
            )

        for out in step.outs:
            if out.sidecar is None:
                continue
            sidecar = absolute(paths.project_root, out.sidecar.resolved)
            if _mtime(sidecar) != sidecar_before[out.path.logical]:
                continue  # the step maintains its own sidecar
            _write_sidecar(paths.project_root, out, sidecar, cache)
        if step.kind == "check":
            stamp = paths.project_root / stamp_ref(step.name)
            stamp.parent.mkdir(parents=True, exist_ok=True)
            stamp.write_text(f"{spec_hash(step)}\n", encoding="utf-8")

    return _execute


def _write_sidecar(project_root: Path, out: Out, sidecar: Path, cache: HashCache) -> None:
    """Record the out's content hash so later runs never read the large file."""
    digest = cache.path_state(absolute(project_root, out.path.resolved))
    if digest is None:
        return
    sidecar.write_text(f"{digest}  {out.path.logical}\n", encoding="utf-8")


def _mtime(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return None


def make_tasks(
    graph: Graph, names: list[str], paths: RunnerPaths, cache: HashCache,
    *, force_names: set[str] | None = None,
) -> list[StepTask]:
    """One in-memory pytask task per selected step."""
    outputs = output_nodes(graph)
    tasks = []
    for name in names:
        step = graph.step(name)
        if step is None:  # pragma: no cover - names come from the graph
            continue
        record = read_run_record(paths, name)
        forced = name in (force_names or ()) or (
            record.get("outcome") in ("running", "pending")
            or (record.get("outcome") == "failed" and record.get("forced", False))
        )
        deps, products = step_nodes(step, outputs)
        deps += directory_dep_nodes(graph, step)
        produces: dict[str, Any] = {}
        if products:
            key = "stamp" if step.kind == "check" else "outs"
            produces[key] = [_node(node, paths, cache) for node in products]
        attributes = {"superra": (graph, paths, step), "superra_cache": cache}
        tasks.append(
            StepTask(
                name=step.name,
                function=_run_step(step, paths, cache, forced=forced, graph=graph, attributes=attributes),
                attributes=attributes,
                force_pending=forced,
                depends_on={
                    "deps": [_node(node, paths, cache) for node in deps],
                    "spec": SpecNode(name=spec_node_id(step.name), value=spec_hash(step)),
                },
                produces=produces,
            )
        )
    return tasks


def _node(node: Node, paths: RunnerPaths, cache: HashCache) -> FileNode:
    logical, hashed, must_exist = node
    return FileNode(
        name=logical,
        resolved=absolute(paths.project_root, hashed),
        cache=cache,
        must_exist=(
            absolute(paths.project_root, must_exist) if must_exist else None
        ),
    )


@contextmanager
def _in_directory(target: Path):
    previous = Path.cwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(previous)


def run_build(
    graph: Graph,
    paths: RunnerPaths,
    names: list[str],
    *,
    n_workers: int = 1,
    force_all: bool = False,
    force_names: list[str] | None = None,
    dry_run: bool = False,
) -> int:
    """Hand the selected steps to pytask and return its exit code."""
    import pytask  # noqa: PLC0415 - the one import that needs the PEP 723 block

    # A failed step's actionable line is `StepFailed: … see <log>`; the frames
    # above it are this file's. pytask's own frame-suppression list takes the
    # directory, and `show_traceback=False` would drop the message too.
    scripts_dir = Path(__file__).resolve().parent
    if scripts_dir not in pytask.Traceback.suppress:
        pytask.Traceback.suppress += (scripts_dir,)

    from _repro_acceptance import bind_sources, check_sources
    if not hasattr(graph, "_acceptance_sources") and graph.dependencies:
        bind_sources(graph, graph.dependencies.tasks[""].dir_path)
    check_sources(graph)
    cache = HashCache(paths.cache_file)
    forced = set(names if force_all else (force_names or ()))
    tasks = make_tasks(graph, names, paths, cache, force_names=forced)
    options: dict[str, Any] = {}
    if n_workers > 1:
        # Threads, not processes: steps are subprocesses, so the GIL is free
        # while they run, nothing has to survive pickling, and the workers can
        # share one hash cache.
        options["n_workers"] = n_workers
        options["parallel_backend"] = "threads"
    from _repro_acceptance import mutation_lock
    with mutation_lock(paths), _in_directory(paths.project_root):
        # pytask 0.6's API does not run the hook_module CLI callback.
        from _pytask.pluginmanager import get_plugin_manager, storage
        from _pytask.build import normalize_programmatic_config
        from _pytask.cli import DEFAULTS_FROM_CLI
        import _repro_hooks
        manager = get_plugin_manager()
        manager.register(_repro_hooks)
        storage.store(manager)
        config = normalize_programmatic_config(
            dict(tasks=tasks, paths=[], force=False, dry_run=dry_run,
                 explain=dry_run, **options),
            command="build", defaults_from_cli=DEFAULTS_FROM_CLI,
        )
        session = pytask.build(**config)
    cache.flush()
    root = session.config.get("root")
    if root is not None and Path(root).resolve() != paths.project_root.resolve():
        print(
            f"Warning: pytask rooted at {root}, not {paths.project_root}; "
            f"pytask.lock was written there.",
            file=sys.stderr,
        )
    return int(session.exit_code)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="superra repro", description="Build and inspect the reproduction graph"
    )
    parser.add_argument(
        "--plan-root",
        "--root",
        dest="plan_root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Rebuild stale steps")
    build.add_argument("targets", nargs="*", help="Step names or task paths")
    build.add_argument("--tier", choices=TIERS, default="required")
    build.add_argument("-j", "--jobs", type=int, default=1, dest="jobs")
    force = build.add_mutually_exclusive_group()
    force.add_argument("--force", action="store_true", help="Force direct targets; rebuild ancestors only if stale")
    force.add_argument("--force-all", action="store_true", help="Force targets and all their producer ancestors")
    build.add_argument("--dry-run", action="store_true", help="Report what would run")

    status = sub.add_parser("status", help="Report each step's freshness")
    status.add_argument("targets", nargs="*", help="Step names or task paths, with producer ancestors")
    status.add_argument("--tier", choices=TIERS, default="required")
    status.add_argument("--json", action="store_true", dest="as_json")

    explain = sub.add_parser("explain", help="Explain one step's state")
    explain.add_argument("step")
    explain.add_argument("--json", action="store_true", dest="as_json")

    impact = sub.add_parser("impact", help="Inspect conservative dependency fan-out")
    impact.add_argument("paths", nargs="+")
    impact.add_argument("--scope", action="append", default=[])
    impact.add_argument("--json", action="store_true", dest="as_json")

    accept = sub.add_parser("accept", help="Preview or apply exact-state reviewed acceptance")
    accept.add_argument("targets", nargs="+")
    accept.add_argument("--reason", default="")
    accept.add_argument("--review", action="append", default=[], metavar="NODE=RATIONALE")
    accept.add_argument("--evidence", action="append", default=[], metavar="FILE")
    mode = accept.add_mutually_exclusive_group()
    mode.add_argument("--apply", metavar="PREVIEW_TOKEN")
    mode.add_argument("--dry-run", action="store_true")
    accept.add_argument("--json", action="store_true", dest="as_json")

    revoke = sub.add_parser("revoke", help="Revoke selected step acceptances")
    revoke.add_argument("targets", nargs="+")
    revoke.add_argument("--json", action="store_true", dest="as_json")

    dag = sub.add_parser("dag", help="Render the step graph")
    dag.add_argument("--mermaid", action="store_true")

    tier = sub.add_parser("tier", help="Set a task's reproduction tier")
    tier.add_argument("task_path")
    tier.add_argument("tier", choices=TIER_INPUTS)
    return parser


def _unsupported_here(command: str) -> bool:
    """Whether the running interpreter is short of what this subcommand needs."""
    if command == "build":
        return importlib.util.find_spec("pytask") is None
    return command in ("status", "explain", "accept", "revoke") and not TOML_AVAILABLE


def _missing_piece(command: str) -> str:
    return "pytask" if command == "build" else "Python 3.11+ (tomllib)"


def _reexec(argv: list[str], command: str) -> int:
    """Re-run this script under uv, whose PEP 723 block supplies what is missing."""
    missing = _missing_piece(command)
    if os.environ.get(REEXEC_ENV):
        print(
            f"Error: {missing} is still unavailable after the runner re-execed; "
            f"install it, or make `uv` available on PATH.",
            file=sys.stderr,
        )
        return 1
    uv = shutil.which("uv")
    if uv is None:
        hint = (
            "`pip install 'pytask>=0.6,<0.7' pytask-parallel`"
            if command == "build"
            else "run superRA on Python 3.11 or newer"
        )
        print(
            f"Error: `superra repro {command}` needs {missing}. Install `uv`, which "
            f"lets the runner provision it, or {hint}.",
            file=sys.stderr,
        )
        return 1
    env = dict(os.environ, **{REEXEC_ENV: "1"})
    completed = subprocess.run(  # noqa: S603
        [uv, "run", "--script", str(Path(__file__).resolve()), *argv], env=env, check=False
    )
    return completed.returncode


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(argv)

    if _unsupported_here(args.command):
        sys.exit(_reexec(argv, args.command))

    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --root.", file=sys.stderr)
        sys.exit(1)
    if not plan_root.is_dir():
        print(f"Error: task root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)
    project_root = plan_root.resolve().parent
    paths = runner_paths(project_root)

    if args.command == "tier":
        try:
            print(set_tier(plan_root, args.task_path, args.tier))
        except ReproStateError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        return

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
        from _repro_acceptance import accept, impact, revoke
        try:
            if args.command == "impact":
                result = impact(graph, paths, args.paths, args.scope)
            elif args.command == "revoke":
                result = revoke(graph, paths, args.targets)
            else:
                reviews = {}
                for item in args.review:
                    node, sep, rationale = item.partition("=")
                    if not sep or not rationale.strip():
                        raise ReproStateError("--review expects NODE=RATIONALE")
                    reviews[node] = rationale
                result = accept(graph, paths, args.targets, args.reason, reviews, args.evidence, args.apply)
            print(json.dumps(result, indent=2))
            return
        except ReproStateError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    if args.command == "build":
        errors = [f for f in graph.findings if f.severity == "error"]
        if errors:
            print(
                f"Error: {len(errors)} reproduction error(s); run `superra task check`.",
                file=sys.stderr,
            )
            for finding in errors:
                print(f"  {finding.to_text()}", file=sys.stderr)
            sys.exit(1)
        args.tier = normalize_tier(args.tier)
        names, unknown = select_steps(graph, args.targets, args.tier)
        if unknown:
            print(
                f"Error: no step or task matches {', '.join(unknown)}", file=sys.stderr
            )
            sys.exit(1)
        if not names:
            print(f"No steps registered at tier {args.tier}.")
            return
        force_names = (
            select_steps(graph, args.targets, args.tier, include_ancestors=False)[0]
            if args.force else []
        )
        try:
            result = run_build(
                graph,
                paths,
                names,
                n_workers=max(1, args.jobs),
                force_all=args.force_all,
                force_names=force_names,
                dry_run=args.dry_run,
            )
        except ReproStateError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        sys.exit(result)

    try:
        report = compute_status(
            graph, paths, tier="all" if args.command == "explain" else args.tier,
            targets=args.targets if args.command == "status" else (),
        )
        if args.command == "explain":
            from _repro_acceptance import inspect_baseline
            entry = report.entry(args.step)
            if entry is None:
                raise ReproStateError(f"unknown step {args.step!r}")
            details = inspect_baseline(graph, entry.step, paths)
            if args.as_json:
                print(json.dumps(dict(entry.to_dict(), baseline=details), indent=2))
            else:
                print(format_explain(report, args.step))
                print("  baseline: " + json.dumps(details, indent=2))
            return
    except ReproStateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(format_status(report))
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
