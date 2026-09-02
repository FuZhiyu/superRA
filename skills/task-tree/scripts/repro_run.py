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

from _repro import Graph, Out, Step, build_graph  # noqa: E402
from _repro_state import (  # noqa: E402
    TOML_AVAILABLE,
    HashCache,
    ReproStateError,
    RunnerPaths,
    absolute,
    compute_status,
    ensure_state_dir,
    format_explain,
    format_status,
    render_dag,
    runner_paths,
    select_steps,
    set_tier,
    sidecar_targets,
    spec_hash,
    spec_node_id,
    stamp_ref,
    step_nodes,
    write_run_record,
)
from _task_io import TASK_ROOT_DIRNAME, resolve_plan_root_arg  # noqa: E402

REEXEC_ENV = "SUPERRA_REPRO_REEXEC"
TIERS = ("canon", "local", "all")


# ---------------------------------------------------------------------------
# pytask node and task types
# ---------------------------------------------------------------------------

@dataclass
class FileNode:
    """A file or directory node whose lock id is its logical path.

    Deliberately not a ``PPathNode``: pytask derives a path node's lock id from
    its resolved path, which would embed the author or branch a ``${VAR}``
    expanded to. Keeping the id in ``name`` keeps the committed lock portable.
    """

    name: str
    resolved: Path
    cache: HashCache
    attributes: dict = field(default_factory=dict)

    @property
    def signature(self) -> str:
        return hashlib.sha256(self.name.encode("utf-8")).hexdigest()

    def state(self) -> str | None:
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

    ``state`` is a constant: upgrading the runner must not invalidate a
    project's whole graph, and ``SpecNode`` already carries what changed.
    """

    name: str
    function: Callable[..., Any]
    depends_on: dict = field(default_factory=dict)
    produces: dict = field(default_factory=dict)
    markers: list = field(default_factory=list)
    report_sections: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)

    @property
    def signature(self) -> str:
        return hashlib.sha256(f"step:{self.name}".encode()).hexdigest()

    def state(self) -> str | None:
        return "1"

    def execute(self, **kwargs: Any) -> Any:
        return self.function(**kwargs)


class StepFailed(RuntimeError):
    """A step command exited non-zero."""


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def _run_step(step: Step, paths: RunnerPaths, cache: HashCache) -> Callable[..., None]:
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

        started = time.time()
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
            "outcome": "success" if completed.returncode == 0 else "failed",
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
    graph: Graph, names: list[str], paths: RunnerPaths, cache: HashCache
) -> list[StepTask]:
    """One in-memory pytask task per selected step."""
    tracked = sidecar_targets(graph)
    tasks = []
    for name in names:
        step = graph.step(name)
        if step is None:  # pragma: no cover - names come from the graph
            continue
        deps, products = step_nodes(step, tracked)
        produces: dict[str, Any] = {}
        if products:
            key = "stamp" if step.kind == "check" else "outs"
            produces[key] = [_node(logical, resolved, paths, cache) for logical, resolved in products]
        tasks.append(
            StepTask(
                name=step.name,
                function=_run_step(step, paths, cache),
                depends_on={
                    "deps": [
                        _node(logical, resolved, paths, cache) for logical, resolved in deps
                    ],
                    "spec": SpecNode(name=spec_node_id(step.name), value=spec_hash(step)),
                },
                produces=produces,
            )
        )
    return tasks


def _node(logical: str, resolved: str, paths: RunnerPaths, cache: HashCache) -> FileNode:
    return FileNode(
        name=logical,
        resolved=absolute(paths.project_root, resolved),
        cache=cache,
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
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Hand the selected steps to pytask and return its exit code."""
    import pytask  # noqa: PLC0415 - the one import that needs the PEP 723 block

    cache = HashCache(paths.cache_file)
    tasks = make_tasks(graph, names, paths, cache)
    options: dict[str, Any] = {}
    if n_workers > 1:
        # Threads, not processes: steps are subprocesses, so the GIL is free
        # while they run, nothing has to survive pickling, and the workers can
        # share one hash cache.
        options["n_workers"] = n_workers
        options["parallel_backend"] = "threads"
    with _in_directory(paths.project_root):
        session = pytask.build(
            tasks=tasks,
            paths=[],
            force=force,
            dry_run=dry_run,
            explain=dry_run,
            **options,
        )
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
    build.add_argument("--tier", choices=TIERS, default="canon")
    build.add_argument("-j", "--jobs", type=int, default=1, dest="jobs")
    build.add_argument("--force", action="store_true", help="Run even when nothing changed")
    build.add_argument("--dry-run", action="store_true", help="Report what would run")

    status = sub.add_parser("status", help="Report each step's freshness")
    status.add_argument("--tier", choices=TIERS, default="canon")
    status.add_argument("--json", action="store_true", dest="as_json")

    explain = sub.add_parser("explain", help="Explain one step's state")
    explain.add_argument("step")

    dag = sub.add_parser("dag", help="Render the step graph")
    dag.add_argument("--mermaid", action="store_true")

    tier = sub.add_parser("tier", help="Set a task's reproduction tier")
    tier.add_argument("task_path")
    tier.add_argument("tier", choices=("canon", "local"))
    return parser


def _unsupported_here(command: str) -> bool:
    """Whether the running interpreter is short of what this subcommand needs."""
    if command == "build":
        return importlib.util.find_spec("pytask") is None
    return command in ("status", "explain") and not TOML_AVAILABLE


def _reexec(argv: list[str]) -> int:
    """Re-run this script under uv so its PEP 723 block supplies pytask."""
    if os.environ.get(REEXEC_ENV):
        print(
            "Error: pytask is unavailable and the runner already re-execed; "
            "install pytask>=0.6,<0.7 or make `uv` available on PATH.",
            file=sys.stderr,
        )
        return 1
    uv = shutil.which("uv")
    if uv is None:
        print(
            "Error: `superra repro build` needs pytask. Install `uv` (the runner "
            "provisions pytask itself) or `pip install 'pytask>=0.6,<0.7' "
            "pytask-parallel`.",
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
        sys.exit(_reexec(argv))

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

    graph = build_graph(plan_root, project_root=project_root)

    if args.command == "dag":
        print(render_dag(graph, mermaid=args.mermaid))
        return

    if graph.steps:
        ensure_state_dir(paths)

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
        names, unknown = select_steps(graph, args.targets, args.tier)
        if unknown:
            print(
                f"Error: no step or task matches {', '.join(unknown)}", file=sys.stderr
            )
            sys.exit(1)
        if not names:
            print(f"No steps registered at tier {args.tier}.")
            return
        sys.exit(
            run_build(
                graph,
                paths,
                names,
                n_workers=max(1, args.jobs),
                force=args.force,
                dry_run=args.dry_run,
            )
        )

    try:
        report = compute_status(
            graph, paths, tier="all" if args.command == "explain" else args.tier
        )
        if args.command == "explain":
            print(format_explain(report, args.step))
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
