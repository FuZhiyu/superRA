#!/usr/bin/env python3
"""Update frontmatter fields of an existing task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    VALID_INTEGRATION_STATUSES,
    VALID_REVIEW_STATUSES,
    VALID_STATUSES,
    collect_all_tasks,
    compute_review_status,
    compute_status,
    parse_task,
    propagate_parent_status,
    today_str,
    validate_status_consistency,
    walk_plan,
    write_task,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update task frontmatter fields.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
    parser.add_argument("--path", help="Task path relative to plan root")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Set task status")
    parser.add_argument("--review-status", choices=VALID_REVIEW_STATUSES, help="Set review status")
    parser.add_argument("--integration-status", choices=VALID_INTEGRATION_STATUSES, help="Set integration status")
    parser.add_argument("--title", help="Set task title")
    parser.add_argument("--add-tag", action="append", default=[], help="Add a tag")
    parser.add_argument("--remove-tag", action="append", default=[], help="Remove a tag")
    parser.add_argument("--script", help="Set script path")
    parser.add_argument("--fix", action="store_true",
                        help="Scan the tree and fix status consistency mismatches "
                             "(corrects parent status fields to match rolled-up children)")
    parser.add_argument("--propagate-all", action="store_true",
                        help="Walk the entire tree and propagate all parent statuses "
                             "from their children (status + review_status + cascade)")
    return parser.parse_args(argv)


def update_task(
    plan_root: Path,
    task_path: str,
    status: str | None = None,
    review_status: str | None = None,
    integration_status: str | None = None,
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
    changed = False

    if status is not None and status != task.status:
        task.status = status
        changed = True
    if review_status is not None and review_status != task.review_status:
        task.review_status = review_status
        changed = True
    if integration_status is not None and integration_status != task.integration_status:
        task.integration_status = integration_status
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
    """Scan the tree and fix status/review_status mismatches.

    For branch (non-leaf) tasks, sets the frontmatter `status` field to
    match the rolled-up status from children. Also flags leaf tasks with
    review_status or integration_status inconsistencies.

    Returns the number of tasks fixed.
    """
    root = walk_plan(plan_root)
    all_tasks = collect_all_tasks(root)
    fixed_count = 0

    for task in all_tasks:
        changed = False

        # For branch tasks: align frontmatter status and review_status with rollup
        if not task.is_leaf:
            rolled_up = compute_status(task)
            if task.status != rolled_up:
                print(f"  fix: {task.path}: status {task.status!r} -> {rolled_up!r} (rolled up from children)")
                task.status = rolled_up
                changed = True

            rolled_review = compute_review_status(task)
            if task.review_status != rolled_review:
                print(f"  fix: {task.path}: review_status {task.review_status!r} -> {rolled_review!r} (rolled up from children)")
                task.review_status = rolled_review
                changed = True

            # integration_status cannot advance past ~ unless review_status == approved
            if task.review_status != "approved" and task.integration_status != "~":
                print(f"  fix: {task.path}: integration_status {task.integration_status!r} -> '~' (review_status not 'approved')")
                task.integration_status = "~"
                changed = True

        # For all tasks: check review/integration consistency
        warnings = validate_status_consistency(task)
        if warnings:
            for w in warnings:
                print(f"  warn: {task.path}: {w}")

        if changed:
            task.updated = today_str()
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
        rolled_review = compute_review_status(fresh)

        if fresh.status != rolled_status:
            fresh.status = rolled_status
            changed = True

        # For branch tasks, review_status is purely rolled up from children.
        if fresh.review_status != rolled_review:
            fresh.review_status = rolled_review
            changed = True

        # Cascade: reset integration_status if review_status is not 'approved'
        if fresh.review_status != "approved" and fresh.integration_status != "~":
            fresh.integration_status = "~"
            changed = True

        if changed:
            fresh.updated = today_str()
            write_task(fresh)
            total_updated += 1

    return total_updated


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.fix:
        plan_root = Path(args.plan_root)
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
        plan_root = Path(args.plan_root)
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
        plan_root=Path(args.plan_root),
        task_path=args.path,
        status=args.status,
        review_status=args.review_status,
        integration_status=args.integration_status,
        title=args.title,
        add_tags=args.add_tag,
        remove_tags=args.remove_tag,
        script=args.script,
    )


if __name__ == "__main__":
    main()
