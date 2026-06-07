#!/usr/bin/env python3
"""Rename a task directory and cascade depends_on updates in siblings."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    cascade_depends_on_rename,
    parse_task,
    resolve_plan_root_arg,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename a task and update sibling references.")
    parser.add_argument(
        "--plan-root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
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

    # Validate every sibling task.md parses before mutating the filesystem, so a
    # malformed sibling aborts here rather than leaving the directory renamed with
    # the cascade half-applied. (cascade_depends_on_rename re-parses these, but
    # that runs after the rename; the pre-check keeps rename + cascade atomic.)
    for sibling_dir in from_parent.iterdir():
        if sibling_dir == from_dir or not sibling_dir.is_dir():
            continue
        sibling_md = sibling_dir / "task.md"
        if not sibling_md.exists():
            continue
        try:
            parse_task(sibling_md)
        except Exception as exc:
            print(f"Error: cannot parse sibling {sibling_md}: {exc}", file=sys.stderr)
            sys.exit(1)

    from_dir.rename(to_dir)
    print(f"Renamed {from_dir} -> {to_dir}")

    for sibling_name in cascade_depends_on_rename(to_parent, old_slug, new_slug):
        print(f"  Updated depends_on in {sibling_name}")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)
    rename_task(plan_root, args.from_path, args.to_path)


if __name__ == "__main__":
    main()
