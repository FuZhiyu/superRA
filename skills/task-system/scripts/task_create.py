#!/usr/bin/env python3
"""Create a new task directory with a task.md file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import today_str


TASK_TEMPLATE = """\
---
title: "{title}"
status: not-started
depends_on: {depends_on}
tags: []
{script_line}{input_line}{output_line}created: {today}
updated: {today}
---

## Objective

{objective}

## Results

"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new task.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
    parser.add_argument("--path", required=True, help="Task path relative to plan root (e.g., 01-data-prep/01-load)")
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--objective", default="", help="Task objective (one-line description)")
    parser.add_argument("--depends-on", nargs="*", default=[], help="Sibling dependency names")
    parser.add_argument("--script", default="", help="Script path")
    parser.add_argument("--input", nargs="*", default=[], help="Input file paths")
    parser.add_argument("--output", nargs="*", default=[], help="Output file paths")
    return parser.parse_args(argv)


def create_task(
    plan_root: Path,
    task_path: str,
    title: str,
    objective: str = "",
    depends_on: list[str] | None = None,
    script: str = "",
    input_files: list[str] | None = None,
    output_files: list[str] | None = None,
) -> Path:
    depends_on = depends_on or []
    input_files = input_files or []
    output_files = output_files or []

    task_dir = plan_root / task_path
    if task_dir.exists():
        print(f"Error: directory already exists: {task_dir}", file=sys.stderr)
        sys.exit(1)

    parent_dir = task_dir.parent
    if not parent_dir.exists():
        print(f"Error: parent directory does not exist: {parent_dir}", file=sys.stderr)
        sys.exit(1)

    for dep in depends_on:
        dep_dir = parent_dir / dep
        if not dep_dir.exists() or not (dep_dir / "task.md").exists():
            print(f"Error: dependency not found: {dep} (expected {dep_dir}/task.md)", file=sys.stderr)
            sys.exit(1)

    if depends_on:
        deps_yaml = "\n" + "".join(f"  - {d}\n" for d in depends_on)
    else:
        deps_yaml = " []"

    script_line = f"script: {script}\n" if script else ""
    input_line = ""
    if input_files:
        input_line = "input:\n" + "".join(f"  - {f}\n" for f in input_files)
    output_line = ""
    if output_files:
        output_line = "output:\n" + "".join(f"  - {f}\n" for f in output_files)

    safe_title = title.replace('"', '\\"')
    content = TASK_TEMPLATE.format(
        title=safe_title,
        objective=objective,
        depends_on=deps_yaml,
        script_line=script_line,
        input_line=input_line,
        output_line=output_line,
        today=today_str(),
    )

    task_dir.mkdir(parents=False)
    task_md = task_dir / "task.md"
    task_md.write_text(content, encoding="utf-8")

    print(f"Created {task_md}")
    try:
        from plan_dashboard import generate_dashboard
        generate_dashboard(plan_root)
    except Exception:
        pass
    return task_dir


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    create_task(
        plan_root=Path(args.plan_root),
        task_path=args.path,
        title=args.title,
        objective=args.objective,
        depends_on=args.depends_on,
        script=args.script,
        input_files=args.input,
        output_files=args.output,
    )


if __name__ == "__main__":
    main()
