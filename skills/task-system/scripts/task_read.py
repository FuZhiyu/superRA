#!/usr/bin/env python3
"""Context-aware task reading: shows ancestor chain, full task content, and sibling dependency status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    Task,
    parse_body_sections,
    parse_frontmatter,
    parse_task,
    resolve_path,
    walk_plan,
)


# ---------------------------------------------------------------------------
# Plan-root auto-detection
# ---------------------------------------------------------------------------

def _autodetect_plan_root(start: Path) -> Path | None:
    """Walk up from *start* looking for the plan root.

    The plan root is the highest directory in the chain that contains a
    task.md whose *parent* does not contain a task.md (i.e. the root task
    has no task.md above it).
    """
    current = start.resolve()
    while True:
        if (current / "task.md").exists():
            parent = current.parent
            if not (parent / "task.md").exists():
                return current
            current = parent
        else:
            # Walk up until we find a task.md
            parent = current.parent
            if parent == current:
                return None
            current = parent


# ---------------------------------------------------------------------------
# Ancestor chain helpers
# ---------------------------------------------------------------------------

def _collect_ancestors(plan_root: Path, target_path: str) -> list[Task]:
    """Return Tasks from root down to (but not including) target_path."""
    if not target_path:
        return []
    parts = target_path.split("/")
    ancestors: list[Task] = []
    current_dir = plan_root
    for i, _part in enumerate(parts[:-1]):  # all segments except the last
        current_dir = current_dir / parts[i]
        task_md = current_dir / "task.md"
        if task_md.exists():
            ancestors.append(parse_task(task_md))
    # Also include root if it exists and target is not root
    root_md = plan_root / "task.md"
    if root_md.exists():
        root_task = parse_task(root_md)
        ancestors.insert(0, root_task)
    # deduplicate (root might have been added twice if parts[0] == plan_root)
    seen: list[str] = []
    unique: list[Task] = []
    for t in ancestors:
        if t.path not in seen:
            seen.append(t.path)
            unique.append(t)
    return unique


def _first_body_excerpt(task: Task, max_lines: int = 10) -> str:
    """Return the first body section content (trimmed), or first paragraph."""
    sections = parse_body_sections(task.body)
    if sections:
        first_content = next(iter(sections.values())).strip()
        if first_content:
            lines = first_content.splitlines()
            if len(lines) > max_lines:
                lines = lines[:max_lines] + ["..."]
            return "\n".join(lines)
    # Fallback: first non-empty paragraph from raw body
    paragraphs = [p.strip() for p in task.body.strip().split("\n\n") if p.strip()]
    if paragraphs:
        lines = paragraphs[0].splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines] + ["..."]
        return "\n".join(lines)
    return ""


# ---------------------------------------------------------------------------
# Sibling dependency helpers
# ---------------------------------------------------------------------------

def _sibling_map(plan_root: Path, target_task: Task) -> dict[str, Task]:
    """Build a map of slug -> Task for all siblings of target_task."""
    if not target_task.path:
        return {}
    parent_path = target_task.path.rsplit("/", 1)[0] if "/" in target_task.path else ""
    parent_dir = plan_root / parent_path if parent_path else plan_root
    siblings: dict[str, Task] = {}
    for subdir in sorted(parent_dir.iterdir()):
        if subdir.is_dir() and (subdir / "task.md").exists():
            slug = subdir.name
            if slug != target_task.slug:
                siblings[slug] = parse_task(subdir / "task.md")
    return siblings


def _dep_tasks(target_task: Task, siblings: dict[str, Task]) -> list[tuple[str, Task | None]]:
    """For each depends_on entry, return (slug, Task or None)."""
    return [(dep, siblings.get(dep)) for dep in target_task.depends_on]


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------

def _render_frontmatter_readable(fm: dict) -> str:
    """Render frontmatter dict as readable key: value lines."""
    lines = []
    field_order = [
        "title", "status", "review_status", "integration_status",
        "depends_on", "tags", "script", "input", "output",
        "created", "updated",
    ]
    seen = set()
    for key in field_order:
        if key not in fm:
            continue
        seen.add(key)
        val = fm[key]
        if isinstance(val, list):
            if not val:
                lines.append(f"{key}: (none)")
            elif len(val) == 1:
                lines.append(f"{key}: {val[0]}")
            else:
                lines.append(f"{key}:")
                for item in val:
                    lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {val}")
    for key, val in fm.items():
        if key in seen:
            continue
        if isinstance(val, list):
            lines.append(f"{key}: {', '.join(val) if val else '(none)'}")
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines)


def render_human(
    ancestors: list[Task],
    target_task: Task,
    dep_pairs: list[tuple[str, Task | None]],
    show_ancestors: bool = True,
) -> str:
    parts: list[str] = []

    if show_ancestors and ancestors:
        parts.append("=== Ancestor Context ===\n")
        for i, anc in enumerate(ancestors):
            depth = i  # root is 0 -> #, next is 1 -> ##, etc.
            prefix = "#" * (depth + 1)
            status_note = f"  (status: {anc.effective_status()})" if not anc.is_root else ""
            parts.append(f"{prefix} {anc.title}{status_note}\n")
            excerpt = _first_body_excerpt(anc)
            if excerpt:
                parts.append(excerpt)
            parts.append("")

    parts.append(f"=== Task: {target_task.title} ===\n")

    # Frontmatter as readable key-value
    fm, _ = parse_frontmatter(
        (target_task.dir_path / "task.md").read_text(encoding="utf-8")
    )
    parts.append(_render_frontmatter_readable(fm))
    parts.append("")

    # All body sections
    sections = parse_body_sections(target_task.body)
    for section_name, content in sections.items():
        parts.append(f"## {section_name}")
        parts.append(content.strip() if content.strip() else "(empty)")
        parts.append("")

    if dep_pairs:
        parts.append("=== Sibling Dependencies ===\n")
        for slug, dep_task in dep_pairs:
            if dep_task is not None:
                eff = dep_task.effective_status()
                title = dep_task.title or slug
                parts.append(f'- {slug} ({eff}) — "{title}"')
            else:
                parts.append(f"- {slug} (NOT FOUND)")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# JSON rendering
# ---------------------------------------------------------------------------

def render_json(
    ancestors: list[Task],
    target_task: Task,
    dep_pairs: list[tuple[str, Task | None]],
    show_ancestors: bool = True,
) -> str:
    fm, _ = parse_frontmatter(
        (target_task.dir_path / "task.md").read_text(encoding="utf-8")
    )
    sections = parse_body_sections(target_task.body)

    anc_data = []
    if show_ancestors:
        for anc in ancestors:
            anc_sections = parse_body_sections(anc.body)
            anc_data.append({
                "path": anc.path,
                "title": anc.title,
                "status": anc.status,
                "effective_status": anc.effective_status(),
                "first_section": _first_body_excerpt(anc),
                "sections": {k: v.strip() for k, v in anc_sections.items()},
            })

    task_data = {
        "path": target_task.path,
        "title": target_task.title,
        "status": target_task.status,
        "effective_status": target_task.effective_status(),
        "review_status": target_task.review_status,
        "integration_status": target_task.integration_status,
        "depends_on": target_task.depends_on,
        "tags": target_task.tags,
        "script": target_task.script,
        "input": target_task.input,
        "output": target_task.output,
        "created": target_task.created,
        "updated": target_task.updated,
        "sections": {k: v.strip() for k, v in sections.items()},
    }

    deps_data = []
    for slug, dep_task in dep_pairs:
        if dep_task is not None:
            deps_data.append({
                "slug": slug,
                "path": dep_task.path,
                "title": dep_task.title,
                "status": dep_task.status,
                "effective_status": dep_task.effective_status(),
            })
        else:
            deps_data.append({"slug": slug, "path": None, "title": None, "status": "NOT FOUND", "effective_status": "NOT FOUND"})

    data = {
        "ancestors": anc_data,
        "task": task_data,
        "dependencies": deps_data,
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a task with ancestor context, full content, and sibling dependency status."
    )
    parser.add_argument(
        "--plan-root",
        default=None,
        help="Path to the plan root directory. Auto-detected from cwd if not given.",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Task path relative to plan root (e.g., data-preparation/merge)",
    )
    parser.add_argument(
        "--no-ancestors",
        action="store_true",
        help="Skip the ancestor context chain; show only the current task.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output as structured JSON with ancestors, task, and dependencies keys.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Resolve plan root
    if args.plan_root:
        plan_root = Path(args.plan_root).resolve()
    else:
        detected = _autodetect_plan_root(Path.cwd())
        if detected is None:
            print(
                "Error: could not auto-detect plan root. Use --plan-root.",
                file=sys.stderr,
            )
            sys.exit(1)
        plan_root = detected

    if not plan_root.exists():
        print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)

    # Resolve target task
    try:
        task_dir = resolve_path(plan_root, args.path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    task_md = task_dir / "task.md"
    if not task_md.exists():
        print(f"Error: task.md not found at {task_md}", file=sys.stderr)
        sys.exit(1)

    target_task = parse_task(task_md)

    # Collect ancestors
    show_ancestors = not args.no_ancestors
    ancestors = _collect_ancestors(plan_root, target_task.path) if show_ancestors else []

    # Collect sibling deps
    siblings = _sibling_map(plan_root, target_task)
    dep_pairs = _dep_tasks(target_task, siblings)

    # Render
    if args.as_json:
        print(render_json(ancestors, target_task, dep_pairs, show_ancestors=show_ancestors))
    else:
        print(render_human(ancestors, target_task, dep_pairs, show_ancestors=show_ancestors))


if __name__ == "__main__":
    main()
