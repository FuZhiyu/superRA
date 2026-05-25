#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Agent CLI for reading and resolving task comments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _comments import load_comments, resolve_anchors, resolve_comment
from _task_io import collect_all_tasks, resolve_path, walk_plan


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="task-comment",
        description="Read and resolve task comments.",
    )
    parser.add_argument(
        "--plan-root",
        default=".plan",
        help="Path to the plan root directory (default: .plan)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # --- list ---
    p_list = sub.add_parser("list", help="List comments for a task")
    p_list.add_argument("task_path", help="Task path (relative to plan root)")
    p_list.add_argument("--all", action="store_true", dest="show_all",
                        help="Show resolved comments too")
    p_list.add_argument("--json", action="store_true", dest="as_json",
                        help="Output as JSON")

    # --- resolve ---
    p_resolve = sub.add_parser("resolve", help="Toggle resolved status")
    p_resolve.add_argument("task_path", help="Task path")
    p_resolve.add_argument("comment_id", type=int, help="Comment ID")

    # --- list-tree ---
    p_tree = sub.add_parser("list-tree",
                            help="Show unresolved comment counts across the plan")
    p_tree.add_argument("--json", action="store_true", dest="as_json",
                        help="Output as JSON")

    return parser.parse_args(argv)


def _comment_to_json(c) -> dict:
    return {
        "id": c.id,
        "author": c.author,
        "timestamp": c.timestamp,
        "resolved": c.resolved,
        "orphaned": c.orphaned,
        "anchor": {
            "section": c.anchor.section,
            "block_index": c.anchor.block_index,
            "text_preview": c.anchor.text_preview,
        },
        "body": c.body,
    }


def cmd_list(args: argparse.Namespace) -> None:
    plan_root = Path(args.plan_root)
    try:
        task_dir = resolve_path(plan_root, args.task_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not task_dir.exists():
        print(f"Error: task directory not found: {task_dir}", file=sys.stderr)
        sys.exit(1)

    comments = load_comments(task_dir)

    # Re-anchor against current body
    task_md = task_dir / "task.md"
    if task_md.exists():
        body_text = task_md.read_text(encoding="utf-8")
        # Strip frontmatter to get body
        import re
        fm_match = re.match(r"\A---\n.*?\n---\n(.*)", body_text, re.DOTALL)
        body = fm_match.group(1) if fm_match else body_text
        comments = resolve_anchors(comments, body)

    if not args.show_all:
        comments = [c for c in comments if not c.resolved]

    if args.as_json:
        print(json.dumps([_comment_to_json(c) for c in comments], indent=2))
        return

    if not comments:
        print("No comments.")
        return

    for c in comments:
        status = "resolved" if c.resolved else "unresolved"
        orphan_tag = " [ORPHANED]" if c.orphaned else ""
        preview = c.anchor.text_preview
        if len(preview) > 60:
            preview = preview[:57] + "..."
        print(
            f'[#{c.id}] ({status}) {c.anchor.section}, '
            f'block {c.anchor.block_index}: "{preview}..."{orphan_tag}'
        )
        # Indent body lines under the header
        for line in c.body.split("\n"):
            print(f"  > {line}")
        print()


def cmd_resolve(args: argparse.Namespace) -> None:
    plan_root = Path(args.plan_root)
    try:
        task_dir = resolve_path(plan_root, args.task_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    result = resolve_comment(task_dir, args.comment_id)
    if result is None:
        print(f"Error: comment #{args.comment_id} not found.", file=sys.stderr)
        sys.exit(1)

    if result.resolved:
        print(f"Resolved comment #{result.id}")
    else:
        print(f"Unresolved comment #{result.id}")


def cmd_list_tree(args: argparse.Namespace) -> None:
    plan_root = Path(args.plan_root)
    if not plan_root.exists():
        print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)

    root = walk_plan(plan_root)
    all_tasks = collect_all_tasks(root)

    entries: list[dict] = []
    for task in all_tasks:
        comments = load_comments(task.dir_path)
        unresolved = [c for c in comments if not c.resolved]
        if unresolved:
            entries.append({
                "task_path": task.path,
                "unresolved_count": len(unresolved),
            })

    if args.as_json:
        print(json.dumps(entries, indent=2))
        return

    if not entries:
        print("No unresolved comments in the plan tree.")
        return

    for entry in entries:
        print(f"{entry['task_path']}: {entry['unresolved_count']} unresolved comments")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.command == "list":
        cmd_list(args)
    elif args.command == "resolve":
        cmd_resolve(args)
    elif args.command == "list-tree":
        cmd_list_tree(args)


if __name__ == "__main__":
    main()
