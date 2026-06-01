#!/usr/bin/env python3
"""Update frontmatter fields of an existing task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    VALID_STATUSES,
    collect_all_tasks,
    compute_status,
    parse_task,
    propagate_parent_status,
    resolve_plan_root_arg,
    walk_plan,
    write_task,
)

# Statuses with clear recursive semantics, allowed with --cascade.
_CASCADE_ALLOWED = ("approved", "not-started", "archived")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update task frontmatter fields.")
    parser.add_argument(
        "--plan-root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument("--path", help="Task path relative to task root")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Set task status")
    parser.add_argument("--cascade", action="store_true",
                        help="When setting status on a branch task, cascade to all descendant leaves. "
                             "Only valid for: approved, not-started, archived.")
    parser.add_argument("--title", help="Set task title")
    parser.add_argument("--add-tag", action="append", default=[], help="Add a tag")
    parser.add_argument("--remove-tag", action="append", default=[], help="Remove a tag")
    parser.add_argument("--script", help="Set script path")
    parser.add_argument("--fix", action="store_true",
                        help="Scan the tree and fix status consistency mismatches "
                             "(corrects parent status fields to match rolled-up children)")
    parser.add_argument("--propagate-all", action="store_true",
                        help="Walk the entire tree and propagate all parent statuses "
                             "from their children")
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
        write_task(task)
        print(f"Updated {task_md}")
        # Propagate status to ancestors
        propagated = propagate_parent_status(plan_root, task_path)
        if propagated:
            print(f"Propagated status to {propagated} ancestor(s).")
        try:
            from plan_dashboard import generate_dashboard
            generate_dashboard(plan_root)
        except Exception:
            pass
    else:
        print("No changes.")


def fix_status_consistency(plan_root: Path) -> int:
    """Scan the tree and fix status mismatches.

    For branch (non-leaf) tasks, sets the frontmatter `status` field to
    match the rolled-up status from children.

    Returns the number of tasks fixed.
    """
    root = walk_plan(plan_root)
    all_tasks = collect_all_tasks(root)
    fixed_count = 0

    for task in all_tasks:
        changed = False

        # For branch tasks: align frontmatter status with rollup
        if not task.is_leaf:
            rolled_up = compute_status(task)
            if task.status != rolled_up:
                print(f"  fix: {task.path}: status {task.status!r} -> {rolled_up!r} (rolled up from children)")
                task.status = rolled_up
                changed = True

        if changed:
            write_task(task)
            fixed_count += 1

    return fixed_count


def propagate_all(plan_root: Path) -> int:
    """Walk the entire tree bottom-up, recomputing all parent statuses.

    Processes branch tasks deepest-first so that by the time a parent is
    processed, all its children already have correct statuses.

    Returns the number of tasks updated.
    """
    from _task_io import _walk_children

    root = walk_plan(plan_root)
    all_tasks = collect_all_tasks(root)
    # Include root if it has children
    if not root.is_leaf:
        all_tasks.append(root)

    # Only branch tasks need propagation
    branches = [t for t in all_tasks if not t.is_leaf]
    # Sort deepest first so children are correct before parents
    branches.sort(key=lambda t: t.path.count("/"), reverse=True)

    total_updated = 0

    for task in branches:
        # Re-read from disk (children may have been updated in earlier iterations)
        task_md = task.dir_path / "task.md"
        fresh = parse_task(task_md)
        fresh.children = _walk_children(task.dir_path, plan_root)

        if fresh.is_leaf:
            continue

        changed = False
        rolled_status = compute_status(fresh)

        if fresh.status != rolled_status:
            fresh.status = rolled_status
            changed = True

        if changed:
            write_task(fresh)
            total_updated += 1

    return total_updated


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)

    if args.fix:
        print(f"Scanning {plan_root} for status consistency issues...")
        fixed = fix_status_consistency(plan_root)
        if fixed:
            print(f"Fixed {fixed} task(s).")
            try:
                from plan_dashboard import generate_dashboard
                generate_dashboard(plan_root)
            except Exception:
                pass
        else:
            print("No inconsistencies found.")
        return

    if getattr(args, "propagate_all", False):
        print(f"Propagating parent statuses in {plan_root}...")
        updated = propagate_all(plan_root)
        if updated:
            print(f"Updated {updated} parent task(s).")
            try:
                from plan_dashboard import generate_dashboard
                generate_dashboard(plan_root)
            except Exception:
                pass
        else:
            print("All parent statuses already consistent.")
        return

    if not args.path:
        print("Error: --path is required (unless using --fix or --propagate-all)", file=sys.stderr)
        sys.exit(1)

    update_task(
        plan_root=plan_root,
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
