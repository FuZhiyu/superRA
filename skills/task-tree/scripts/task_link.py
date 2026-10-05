#!/usr/bin/env python3
"""Add or remove sibling dependency edges on a task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _repro import build_graph
from _task_dependencies import within
from _task_snapshot import preflight, print_edit_notes
from _task_io import (
    ATTACHMENTS_DIRNAME,
    TASK_ROOT_DIRNAME,
    iter_child_task_dirs,
    parse_task,
    resolve_path,
    resolve_plan_root_arg,
    strip_root_prefix,
    write_task,
)


def _is_sibling_slug(slug: str) -> bool:
    """True if *slug* names a sibling (a bare directory name), not a path or escape."""
    return (
        bool(slug)
        and slug not in {".", "..", ATTACHMENTS_DIRNAME}
        and "/" not in slug
        and "\\" not in slug
    )


def _files_from(graph, consumer: str, producer: str) -> str:
    return ", ".join(sorted({e["via"] for e in graph.dependencies.inputs(consumer)
                             if within(e["from"], producer)}))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage task dependencies.")
    parser.add_argument(
        "--plan-root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument("--path", required=True, help="Task path (the task to modify)")
    parser.add_argument("--depends-on", required=True, help="Sibling dependency name to add or remove")
    parser.add_argument("--remove", action="store_true", help="Remove the dependency instead of adding it")
    return parser.parse_args(argv)


def link_task(
    plan_root: Path,
    task_path: str,
    depends_on: str,
    remove: bool = False,
) -> None:
    # Single enforcement point (see task_update): containment + prefix tolerance
    # on the task path, and sibling-only validation on the dependency slug — so a
    # literal ``../outside`` edge cannot be written through any entry surface.
    if not _is_sibling_slug(depends_on):
        print(f"Error: dependency must be a sibling slug: {depends_on!r}", file=sys.stderr)
        sys.exit(1)
    try:
        task_dir = resolve_path(plan_root, task_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    task_path = strip_root_prefix(plan_root, task_path)
    task_md = task_dir / "task.md"
    if not task_md.exists():
        print(f"Error: task not found: {task_md}", file=sys.stderr)
        sys.exit(1)

    task = parse_task(task_md)

    if remove:
        parent = task_path.rsplit("/", 1)[0] + "/" if "/" in task_path else ""
        if depends_on not in task.depends_on:
            files = _files_from(build_graph(plan_root, resolve_vars=False), task_path, parent + depends_on)
            detail = (f"; {task_path} reads {files} from {depends_on}, a file edge that orders builds "
                      "but never gates starting work") if files else ""
            print(f"Warning: {depends_on} is not in depends_on for {task_path}{detail}", file=sys.stderr)
            return
        task.depends_on.remove(depends_on)
        try:
            graph = preflight(plan_root, lambda root, tasks: setattr(tasks[task_path], "depends_on", task.depends_on))
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        write_task(task)
        print(f"Removed dependency {depends_on} from {task_path}")
        files = _files_from(graph, task_path, parent + depends_on)
        if files:
            print(f"File edge remains: {task_path} reads {files} from {depends_on}.")
        print_edit_notes(graph)
    else:
        parent_dir = task_dir.parent
        sibling_dirs = {
            directory.name: directory
            for directory in iter_child_task_dirs(parent_dir)
        }
        dep_dir = sibling_dirs.get(depends_on)
        if dep_dir is None:
            dep_dir = parent_dir / depends_on
            print(f"Error: sibling dependency not found: {dep_dir}/task.md", file=sys.stderr)
            sys.exit(1)

        if depends_on in task.depends_on:
            print(f"Already depends on {depends_on}")
            return

        task.depends_on.append(depends_on)
        try:
            graph = preflight(plan_root, lambda root, tasks: setattr(tasks[task_path], "depends_on", task.depends_on))
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        write_task(task)
        print(f"Added dependency {depends_on} to {task_path}")
        print_edit_notes(graph)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)
    link_task(
        plan_root=plan_root,
        task_path=args.path,
        depends_on=args.depends_on,
        remove=args.remove,
    )


if __name__ == "__main__":
    main()
