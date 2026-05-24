#!/usr/bin/env python3
"""Rename a task directory and cascade depends_on updates in siblings."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import parse_task, today_str, write_task


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename a task and update sibling references.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
    parser.add_argument("--from", required=True, dest="from_path", help="Current task path")
    parser.add_argument("--to", required=True, dest="to_path", help="New task path")
    return parser.parse_args(argv)


def rename_task(plan_root: Path, from_path: str, to_path: str) -> None:
    from_dir = plan_root / from_path
    to_dir = plan_root / to_path

    if not from_dir.exists():
        print(f"Error: source not found: {from_dir}", file=sys.stderr)
        sys.exit(1)
    if to_dir.exists():
        print(f"Error: destination already exists: {to_dir}", file=sys.stderr)
        sys.exit(1)

    from_parent = from_dir.parent
    to_parent = to_dir.parent
    if from_parent != to_parent:
        print("Error: rename must stay within the same parent directory", file=sys.stderr)
        sys.exit(1)

    old_slug = from_dir.name
    new_slug = to_dir.name

    # Parse and validate all sibling files BEFORE renaming, so a parse
    # failure does not leave the directory renamed with stale references.
    siblings = [
        d for d in from_parent.iterdir()
        if d.is_dir() and (d / "task.md").exists() and d != from_dir
    ]
    sibling_updates: list[tuple[Path, "Task"]] = []  # type: ignore[name-defined]
    for sibling_dir in siblings:
        task = parse_task(sibling_dir / "task.md")
        if old_slug in task.depends_on:
            task.depends_on = [new_slug if d == old_slug else d for d in task.depends_on]
            task.updated = today_str()
            sibling_updates.append((sibling_dir, task))

    # All parsing succeeded — now perform the rename and writes.
    from_dir.rename(to_dir)
    print(f"Renamed {from_dir} -> {to_dir}")

    for sibling_dir, task in sibling_updates:
        write_task(task)
        print(f"  Updated depends_on in {sibling_dir.name}")

    try:
        from plan_dashboard import generate_dashboard
        generate_dashboard(plan_root)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    rename_task(Path(args.plan_root), args.from_path, args.to_path)


if __name__ == "__main__":
    main()
