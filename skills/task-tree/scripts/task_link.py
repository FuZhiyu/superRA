#!/usr/bin/env python3
"""Add or remove sibling dependency edges on a task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import TASK_ROOT_DIRNAME, parse_task, resolve_plan_root_arg, write_task


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


def _has_transitive_dep(parent_dir: Path, from_slug: str, to_slug: str) -> bool:
    """Check if *from_slug* transitively depends on *to_slug* via depends_on chains.

    Returns True when adding ``to_slug -> from_slug`` would create a cycle
    (i.e. *to_slug* already reaches *from_slug*).
    """
    visited: set[str] = set()
    stack = [from_slug]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        task_md = parent_dir / current / "task.md"
        if not task_md.exists():
            continue
        task = parse_task(task_md)
        for dep in task.depends_on:
            if dep == to_slug:
                return True
            stack.append(dep)
    return False


def link_task(
    plan_root: Path,
    task_path: str,
    depends_on: str,
    remove: bool = False,
) -> None:
    task_md = plan_root / task_path / "task.md"
    if not task_md.exists():
        print(f"Error: task not found: {task_md}", file=sys.stderr)
        sys.exit(1)

    task = parse_task(task_md)

    if remove:
        if depends_on not in task.depends_on:
            print(f"Warning: {depends_on} is not in depends_on for {task_path}", file=sys.stderr)
            return
        task.depends_on.remove(depends_on)
        write_task(task)
        print(f"Removed dependency {depends_on} from {task_path}")
    else:
        parent_dir = (plan_root / task_path).parent
        dep_dir = parent_dir / depends_on
        if not dep_dir.exists() or not (dep_dir / "task.md").exists():
            print(f"Error: sibling dependency not found: {dep_dir}/task.md", file=sys.stderr)
            sys.exit(1)

        if depends_on in task.depends_on:
            print(f"Already depends on {depends_on}")
            return

        source_slug = (plan_root / task_path).name
        if _has_transitive_dep(parent_dir, depends_on, source_slug):
            print(
                f"Error: adding {depends_on} as dependency of {task_path} "
                f"would create a cycle ({depends_on} already depends on {source_slug})",
                file=sys.stderr,
            )
            sys.exit(1)

        task.depends_on.append(depends_on)
        write_task(task)
        print(f"Added dependency {depends_on} to {task_path}")


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
