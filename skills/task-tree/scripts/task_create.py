#!/usr/bin/env python3
"""Create a new task directory with a task.md file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    iter_child_task_dirs,
    propagate_parent_status,
    resolve_path,
    strip_root_prefix,
)


TASK_TEMPLATE = """\
---
title: "{title}"
status: not-started
depends_on: {depends_on}
---

## Objective

{objective}

{guidance_section}\
## Results

"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new task.")
    parser.add_argument(
        "--plan-root",
        default=TASK_ROOT_DIRNAME,
        help=f"Path to the task root directory (default: {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument("--path", required=True, help="Task path relative to plan root (e.g., 01-data-prep/01-load)")
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--objective", default="", help="Task objective (one-line description)")
    parser.add_argument("--guidance", default="", help="Optional advisory Planner Guidance section")
    parser.add_argument("--depends-on", nargs="*", default=[], help="Sibling dependency names")
    return parser.parse_args(argv)


def create_task(
    plan_root: Path,
    task_path: str,
    title: str,
    objective: str = "",
    guidance: str = "",
    depends_on: list[str] | None = None,
) -> Path:
    depends_on = depends_on or []

    # Tolerate a redundant leading task-root segment regardless of entry surface.
    task_path = strip_root_prefix(plan_root, task_path)
    try:
        task_dir = resolve_path(plan_root, task_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if task_dir.exists():
        print(f"Error: directory already exists: {task_dir}", file=sys.stderr)
        sys.exit(1)

    parent_dir = task_dir.parent
    if not parent_dir.exists():
        print(f"Error: parent directory does not exist: {parent_dir}", file=sys.stderr)
        sys.exit(1)

    sibling_names = {directory.name for directory in iter_child_task_dirs(parent_dir)}
    for dep in depends_on:
        if dep not in sibling_names:
            dep_dir = parent_dir / dep
            print(f"Error: dependency not found: {dep} (expected {dep_dir}/task.md)", file=sys.stderr)
            sys.exit(1)

    if depends_on:
        deps_yaml = "\n" + "".join(f"  - {d}\n" for d in depends_on)
    else:
        deps_yaml = " []"

    safe_title = title.replace('"', '\\"')
    content = TASK_TEMPLATE.format(
        title=safe_title,
        objective=objective,
        guidance_section=f"## Planner Guidance\n\n{guidance}\n\n" if guidance else "",
        depends_on=deps_yaml,
    )

    task_dir.mkdir(parents=False)
    task_md = task_dir / "task.md"
    task_md.write_text(content, encoding="utf-8")

    print(f"Created {task_md}")

    # Propagate parent chain status now that a new not-started child exists.
    # This mirrors the same call in task_update.py and task_hook.py.
    propagate_parent_status(plan_root, task_path)

    return task_dir


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    create_task(
        plan_root=Path(args.plan_root),
        task_path=args.path,
        title=args.title,
        objective=args.objective,
        guidance=args.guidance,
        depends_on=args.depends_on,
    )


if __name__ == "__main__":
    main()
