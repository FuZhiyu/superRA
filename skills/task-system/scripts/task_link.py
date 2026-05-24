#!/usr/bin/env python3
"""Add or remove sibling dependency edges on a task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import parse_task, today_str, write_task


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage task dependencies.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
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
        task.updated = today_str()
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
        task.depends_on.append(depends_on)
        task.updated = today_str()
        write_task(task)
        print(f"Added dependency {depends_on} to {task_path}")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    link_task(
        plan_root=Path(args.plan_root),
        task_path=args.path,
        depends_on=args.depends_on,
        remove=args.remove,
    )


if __name__ == "__main__":
    main()
