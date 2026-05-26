#!/usr/bin/env python3
"""Update frontmatter fields of an existing task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    VALID_STATUSES,
    parse_task,
    today_str,
    walk_plan,
    write_task,
)

# Statuses with clear recursive semantics, allowed with --cascade.
_CASCADE_ALLOWED = ("approved", "not-started", "archived")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update task frontmatter fields.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
    parser.add_argument("--path", required=True, help="Task path relative to plan root")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Set task status")
    parser.add_argument("--cascade", action="store_true",
                        help="When setting status on a branch task, cascade to all descendant leaves. "
                             "Only valid for: approved, not-started, archived.")
    parser.add_argument("--title", help="Set task title")
    parser.add_argument("--add-tag", action="append", default=[], help="Add a tag")
    parser.add_argument("--remove-tag", action="append", default=[], help="Remove a tag")
    parser.add_argument("--script", help="Set script path")
    return parser.parse_args(argv)


def _collect_descendant_leaves(task_dir: Path, plan_root: Path) -> list[Path]:
    """Walk subdirectories of *task_dir* and return task.md paths for all descendant leaves."""
    root = walk_plan(task_dir)
    leaves: list[Path] = []

    def _walk(t) -> None:
        if t.is_leaf:
            task_md = t.dir_path / "task.md"
            # Skip the root node if it is the task_dir itself (handled separately)
            if task_md.exists():
                leaves.append(task_md)
        else:
            for child in t.children:
                _walk(child)

    # The root returned by walk_plan is task_dir itself.  We want its
    # descendant leaves, not the branch task itself.
    for child in root.children:
        _walk(child)
    return leaves


def update_task(
    plan_root: Path,
    task_path: str,
    status: str | None = None,
    cascade: bool = False,
    title: str | None = None,
    add_tags: list[str] | None = None,
    remove_tags: list[str] | None = None,
    script: str | None = None,
) -> None:
    task_dir = plan_root / task_path
    task_md = task_dir / "task.md"
    if not task_md.exists():
        print(f"Error: task not found: {task_md}", file=sys.stderr)
        sys.exit(1)

    task = parse_task(task_md)

    # --- Cascade validation --------------------------------------------------
    is_branch = any(
        d.is_dir() and (d / "task.md").exists()
        for d in task_dir.iterdir()
    )

    if cascade and status is None:
        print("Error: --cascade requires --status.", file=sys.stderr)
        sys.exit(1)

    if cascade and not is_branch:
        print("Warning: --cascade ignored; this is a leaf task.", file=sys.stderr)
        cascade = False

    if cascade and status not in _CASCADE_ALLOWED:
        print(
            f"Error: --cascade is only valid for {', '.join(_CASCADE_ALLOWED)}; "
            f"got {status!r}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if status is not None and is_branch and not cascade:
        print(
            "Warning: This task has children; stored status is overridden by "
            "computed rollup.",
            file=sys.stderr,
        )

    # --- Cascade application -------------------------------------------------
    if cascade and status is not None:
        leaves = _collect_descendant_leaves(task_dir, plan_root)
        n_updated = 0
        for leaf_md in leaves:
            leaf = parse_task(leaf_md)
            # Skip archived descendants unless cascading 'archived' itself.
            if leaf.status == "archived" and status != "archived":
                continue
            if leaf.status != status:
                leaf.status = status
                leaf.updated = today_str()
                write_task(leaf)
                n_updated += 1
        print(f"Cascaded status={status!r} to {n_updated} descendant leaf(s).")
        try:
            from plan_dashboard import generate_dashboard
            generate_dashboard(plan_root)
        except Exception:
            pass
        return

    # --- Normal (non-cascade) update -----------------------------------------
    changed = False

    if status is not None and status != task.status:
        task.status = status
        changed = True
    if title is not None and title != task.title:
        task.title = title
        changed = True
    if script is not None and script != task.script:
        task.script = script
        changed = True

    for tag in (add_tags or []):
        if tag not in task.tags:
            task.tags.append(tag)
            changed = True
    for tag in (remove_tags or []):
        if tag in task.tags:
            task.tags.remove(tag)
            changed = True

    if changed:
        task.updated = today_str()
        write_task(task)
        print(f"Updated {task_md}")
        try:
            from plan_dashboard import generate_dashboard
            generate_dashboard(plan_root)
        except Exception:
            pass
    else:
        print("No changes.")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    update_task(
        plan_root=Path(args.plan_root),
        task_path=args.path,
        status=args.status,
        cascade=args.cascade,
        title=args.title,
        add_tags=args.add_tag,
        remove_tags=args.remove_tag,
        script=args.script,
    )


if __name__ == "__main__":
    main()
