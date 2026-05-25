#!/usr/bin/env python3
"""Query the task tree: print tree, compute frontier, render DAG."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import Task, collect_all_tasks, compute_frontier, parse_body_sections, walk_plan


STATUS_ICONS = {
    "not-started": "○",
    "in-progress": "◐",
    "implemented": "◑",
    "revise": "✗",
    "approved": "●",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the task tree.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tree", action="store_true", help="Print the task tree")
    group.add_argument("--frontier", action="store_true", help="List dispatchable leaf tasks")
    group.add_argument("--dag", nargs="?", const="", metavar="SUBTREE", help="Render dependency DAG (Mermaid format)")

    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")
    return parser.parse_args(argv)


def print_tree(task: Task, indent: int = 0, status_filter: str | None = None, tag_filter: str | None = None) -> None:
    """Print an indented tree with status icons."""
    effective = task.effective_status()
    icon = STATUS_ICONS.get(effective, "?")

    if status_filter and effective != status_filter:
        pass_filter = False
    elif tag_filter and tag_filter not in task.tags:
        pass_filter = False
    else:
        pass_filter = True

    if task.is_root:
        label = task.title or "(root)"
        if pass_filter:
            print(f"{icon} {label}")
    else:
        prefix = "  " * indent
        label = task.title or task.slug
        if not task.is_leaf:
            child_statuses = [c.effective_status() for c in task.children]
            approved_count = sum(1 for s in child_statuses if s == "approved")
            total = len(child_statuses)
            progress = f" ({approved_count}/{total})"
        else:
            progress = ""
        if pass_filter:
            print(f"{prefix}{icon} {task.slug}: {label}{progress}")

    for child in task.children:
        print_tree(child, indent + 1, status_filter, tag_filter)


def print_frontier(frontier: list[Task], as_json: bool = False) -> None:
    """Print the dispatch frontier."""
    if as_json:
        data = [{"path": t.path, "title": t.title, "status": t.status} for t in frontier]
        print(json.dumps(data, indent=2))
        return

    if not frontier:
        print("No tasks on the frontier (all blocked or completed).")
        return

    for task in frontier:
        icon = STATUS_ICONS.get(task.status, "?")
        deps = f" [depends: {', '.join(task.depends_on)}]" if task.depends_on else ""
        print(f"  {icon} {task.path}: {task.title}{deps}")


def _sanitize_mermaid_id(slug: str) -> str:
    """Replace non-alphanumeric characters (except hyphens) with underscores."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", slug)


def render_dag(task: Task, subtree_path: str = "") -> str:
    """Render a Mermaid DAG of sibling dependencies within a subtree."""
    if subtree_path:
        target = _find_subtask(task, subtree_path)
        if target is None:
            print(f"Error: subtree not found: {subtree_path}", file=sys.stderr)
            sys.exit(1)
    else:
        target = task

    if not target.children:
        return "graph LR\n    %% no children"

    status_colors = {
        "not-started": ":::notstarted",
        "in-progress": ":::inprogress",
        "implemented": ":::implemented",
        "revise": ":::revise",
        "approved": ":::approved",
    }

    lines = ["graph LR"]
    for child in target.children:
        effective = child.effective_status()
        style = status_colors.get(effective, "")
        node_id = _sanitize_mermaid_id(child.slug)
        label = child.title or child.slug
        lines.append(f'    {node_id}["{label}"]{style}')

    for child in target.children:
        child_id = _sanitize_mermaid_id(child.slug)
        for dep in child.depends_on:
            dep_id = _sanitize_mermaid_id(dep)
            lines.append(f"    {dep_id} --> {child_id}")

    lines.append("")
    lines.append("    classDef notstarted fill:#e0e0e0,stroke:#999,color:#333")
    lines.append("    classDef inprogress fill:#bbdefb,stroke:#1976d2,color:#0d47a1")
    lines.append("    classDef implemented fill:#fff9c4,stroke:#f9a825,color:#e65100")
    lines.append("    classDef revise fill:#ffcdd2,stroke:#e53935,color:#b71c1c")
    lines.append("    classDef approved fill:#c8e6c9,stroke:#43a047,color:#1b5e20")

    return "\n".join(lines)


def _find_subtask(task: Task, path: str) -> Task | None:
    """Find a subtask by its path."""
    if task.path == path:
        return task
    for child in task.children:
        result = _find_subtask(child, path)
        if result:
            return result
    return None


def tree_to_json(task: Task) -> dict:
    """Serialize the task tree to a JSON-compatible dict."""
    sections = parse_body_sections(task.body)
    return {
        "path": task.path,
        "title": task.title,
        "status": task.status,
        "effective_status": task.effective_status(),
        "review_status": task.review_status,
        "integration_status": task.integration_status,
        "depends_on": task.depends_on,
        "tags": task.tags,
        "script": task.script,
        "input": task.input,
        "output": task.output,
        "created": task.created,
        "updated": task.updated,
        "is_leaf": task.is_leaf,
        "body": task.body,
        "objective": sections.get("Objective", ""),
        "results": sections.get("Results", ""),
        "decisions": sections.get("Decisions", ""),
        "revision_notes": sections.get("Revision Notes", ""),
        "review_notes": sections.get("Review Notes", ""),
        "children": [tree_to_json(c) for c in task.children],
    }


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = Path(args.plan_root)

    if not plan_root.exists():
        print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)

    root = walk_plan(plan_root)

    if args.tree:
        if args.as_json:
            print(json.dumps(tree_to_json(root), indent=2))
        else:
            print_tree(root, status_filter=args.status, tag_filter=args.tag)

    elif args.frontier:
        frontier = compute_frontier(root)
        if args.status:
            frontier = [t for t in frontier if t.status == args.status]
        if args.tag:
            frontier = [t for t in frontier if args.tag in t.tags]
        print_frontier(frontier, as_json=args.as_json)

    elif args.dag is not None:
        mermaid = render_dag(root, args.dag)
        print(mermaid)


if __name__ == "__main__":
    main()
