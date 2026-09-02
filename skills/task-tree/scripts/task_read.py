#!/usr/bin/env python3
"""Context-aware task reading: shows a focused tree + ancestor objectives, full task content, and sibling dependency status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _comments import LegacyCommentFormatError, anchored_block, load_comments
from _repro import DEFAULT_TIER, REPRO_SECTION, build_graph
from _repro_state import ReproStateError, compute_status, runner_paths
from _task_io import (
    Task,
    autodetect_plan_root,
    iter_child_task_dirs,
    parse_body_sections,
    parse_frontmatter,
    parse_task,
    resolve_path,
    walk_plan,
)
from task_query import format_focused_tree


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
            ancestors.append(parse_task(task_md, plan_root))
    # Also include root if it exists and target is not root
    root_md = plan_root / "task.md"
    if root_md.exists():
        root_task = parse_task(root_md, plan_root)
        ancestors.insert(0, root_task)
    # deduplicate (root might have been added twice if parts[0] == plan_root)
    seen: list[str] = []
    unique: list[Task] = []
    for t in ancestors:
        if t.path not in seen:
            seen.append(t.path)
            unique.append(t)
    return unique


def _ancestor_objective(task: Task) -> str:
    """Return an ancestor's full ``## Objective`` content, nested ``###`` and all.

    Ancestor objectives carry the binding context an agent inherits — scoped
    ``### Context`` / ``### Conventions`` / ``### Constraints`` subsections that
    change what implementation or review does. Rendering the whole section keeps
    that context intact instead of truncating it. Falls back to the first body
    section, then the first paragraph, for tasks that predate the objective
    convention.
    """
    sections = parse_body_sections(task.body)
    objective = sections.get("Objective", "").strip()
    if objective:
        return objective
    if sections:
        first_content = next(iter(sections.values())).strip()
        if first_content:
            return first_content
    paragraphs = [p.strip() for p in task.body.strip().split("\n\n") if p.strip()]
    if paragraphs:
        return paragraphs[0]
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
    for subdir in iter_child_task_dirs(parent_dir):
        slug = subdir.name
        if slug != target_task.slug:
            siblings[slug] = parse_task(subdir / "task.md", plan_root)
    return siblings


def _dep_tasks(target_task: Task, siblings: dict[str, Task]) -> list[tuple[str, Task | None]]:
    """For each depends_on entry, return (slug, Task or None)."""
    return [(dep, siblings.get(dep)) for dep in target_task.depends_on]


# ---------------------------------------------------------------------------
# Reproduction helpers
# ---------------------------------------------------------------------------

def _reproduction_view(
    plan_root: Path, target_task: Task, root: Task | None
) -> dict | None:
    """Return the task's owned-step states and derived task edges, or ``None``.

    ``None`` means the task carries no ``## Reproduction`` section: such a task
    owns no steps and cannot appear in any task-level edge (an edge needs a
    producing and a consuming step), so there is nothing to compute and the
    graph is never built — this is what keeps a read cheap on a tree with no
    Reproduction sections at all.
    """
    if REPRO_SECTION not in parse_body_sections(target_task.body):
        return None

    project_root = plan_root.resolve().parent
    tree = root if root is not None else walk_plan(plan_root)
    graph = build_graph(plan_root, project_root=project_root, root=tree)

    steps = sorted(graph.steps_for(target_task.path), key=lambda s: s.name)
    states: dict[str, tuple[str, str]] = {}
    unavailable: str | None = None
    if steps:
        try:
            report = compute_status(graph, runner_paths(project_root), tier="all")
        except ReproStateError as exc:
            unavailable = str(exc)
        else:
            states = {e.step.name: (e.status, e.reason) for e in report.entries}

    step_rows = []
    for step in steps:
        outs = [o.path.logical for o in step.outs]
        if unavailable is not None:
            status, reason = "unknown", f"runner unavailable: {unavailable}"
        else:
            status, reason = states[step.name]
        step_rows.append({"name": step.name, "status": status, "reason": reason, "outs": outs})

    return {
        "tier": graph.tiers.get(target_task.path, DEFAULT_TIER),
        "steps": step_rows,
        "feeds_on": sorted({a for a, b in graph.task_edges if b == target_task.path}),
        "feeds": sorted({b for a, b in graph.task_edges if a == target_task.path}),
    }


# ---------------------------------------------------------------------------
# Open-comment helpers
# ---------------------------------------------------------------------------

def _open_comments(target_task: Task) -> list[dict]:
    """Return unresolved comments for *target_task*, each with its full block.

    Each entry is ``{author, section, block, preview, body, orphaned, degraded}``.
    ``block`` is the full anchored block text (no length cap), or ``None`` for an
    orphaned comment (its anchored block moved/was edited away); orphaned entries
    carry the stored ``text_preview`` under ``preview`` instead. Resolved comments
    are excluded.

    Comment loading never crashes the read: if the sidecar is a legacy block-YAML
    file and ``pyyaml`` is unavailable (bare ``python3``), this returns a single
    ``degraded`` sentinel entry carrying a visible note instead of raising, so the
    rest of the read (frontmatter, sections, sibling deps) still emits with exit 0.
    """
    try:
        loaded = load_comments(target_task.dir_path)
    except LegacyCommentFormatError:
        return [{
            "author": None,
            "section": None,
            "block": None,
            "preview": None,
            "body": None,
            "orphaned": False,
            "degraded": "open comments unavailable: legacy sidecar format — "
                        "re-run under uv or re-save to migrate",
        }]
    comments = [c for c in loaded if not c.resolved]
    if not comments:
        return []
    entries: list[dict] = []
    for c in comments:
        block = anchored_block(c, target_task.body)
        entries.append({
            "author": c.author,
            "section": c.anchor.section,
            "block": block,
            "preview": c.anchor.text_preview,
            "body": c.body,
            "orphaned": block is None,
            "degraded": None,
        })
    return entries


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------

def _render_frontmatter_readable(fm: dict) -> str:
    """Render frontmatter dict as readable key: value lines."""
    lines = []
    field_order = ["title", "status", "depends_on"]
    # Stale fields removed from the data model — suppress in output even if
    # still present in old task files.
    _STALE_FIELDS = {
        "review_status", "integration_status", "updated",
        "tags", "script", "input", "output", "created",
    }
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
        if key in seen or key in _STALE_FIELDS:
            continue
        if isinstance(val, list):
            lines.append(f"{key}: {', '.join(val) if val else '(none)'}")
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines)


def _render_reproduction_human(repro: dict) -> list[str]:
    """Render the ``=== Reproduction ===`` block from a `_reproduction_view` dict."""
    lines = ["=== Reproduction ===\n", f"tier: {repro['tier']}"]
    if repro["steps"]:
        lines.append("steps:")
        for row in repro["steps"]:
            outs = ", ".join(row["outs"]) if row["outs"] else "(none)"
            lines.append(
                f"  - {row['name']}: {row['status']} — {row['reason']} [outs: {outs}]"
            )
    else:
        lines.append("steps: (none)")
    for task_path in repro["feeds_on"]:
        lines.append(f"feeds on: {task_path}")
    for task_path in repro["feeds"]:
        lines.append(f"feeds: {task_path}")
    return lines


def render_human(
    ancestors: list[Task],
    target_task: Task,
    dep_pairs: list[tuple[str, Task | None]],
    show_ancestors: bool = True,
    focused_tree: str = "",
    repro: dict | None = None,
) -> str:
    parts: list[str] = []

    if show_ancestors and ancestors:
        parts.append("=== Context ===\n")
        if focused_tree:
            parts.append(focused_tree)
            parts.append("")
        for i, anc in enumerate(ancestors):
            depth = i  # root is 0 -> #, next is 1 -> ##, etc.
            prefix = "#" * (depth + 1)
            status_note = f"  (status: {anc.effective_status()})" if not anc.is_root else ""
            parts.append(f"{prefix} {anc.title}{status_note}\n")
            objective = _ancestor_objective(anc)
            if objective:
                parts.append(objective)
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

    # Unresolved comments anchored to this task, with their full blocks.
    open_comments = _open_comments(target_task)
    if open_comments:
        parts.append("=== Open Comments ===\n")
        for c in open_comments:
            if c.get("degraded"):
                parts.append(f"  [{c['degraded']}]")
                parts.append("")
                continue
            parts.append(f"[{c['author']}] on ## {c['section']}")
            if c["orphaned"]:
                parts.append(f'  block: "{c["preview"]}"')
                parts.append("  [ORPHANED — block moved/edited away]")
            else:
                parts.append("  block:")
                for line in c["block"].split("\n"):
                    parts.append(f"    {line}")
            parts.append("  comment:")
            for line in c["body"].split("\n"):
                parts.append(f"    {line}")
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

    if repro is not None:
        parts.append("")
        parts.extend(_render_reproduction_human(repro))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# JSON rendering
# ---------------------------------------------------------------------------

def render_json(
    ancestors: list[Task],
    target_task: Task,
    dep_pairs: list[tuple[str, Task | None]],
    show_ancestors: bool = True,
    focused_tree: str = "",
    repro: dict | None = None,
) -> str:
    fm, _ = parse_frontmatter(
        (target_task.dir_path / "task.md").read_text(encoding="utf-8")
    )
    sections = parse_body_sections(target_task.body)

    anc_data = []
    if show_ancestors:
        for anc in ancestors:
            anc_sections = {k: v.strip() for k, v in parse_body_sections(anc.body).items()}
            objective = _ancestor_objective(anc)
            anc_data.append({
                "path": anc.path,
                "title": anc.title,
                "status": anc.status,
                "effective_status": anc.effective_status(),
                # `objective` is the explicit full ancestor ## Objective (nested
                # ### subsections included); `first_section` is retained for
                # backward compatibility and mirrors it.
                "objective": objective,
                "first_section": objective,
                "sections": anc_sections,
            })

    task_data = {
        "path": target_task.path,
        "title": target_task.title,
        "status": target_task.status,
        "effective_status": target_task.effective_status(),
        "depends_on": target_task.depends_on,
        "sections": {k: v.strip() for k, v in sections.items()},
        "reproduction": repro,
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

    # Unresolved comments with full block text (parity with human output).
    open_comments = [
        {
            "author": c["author"],
            "section": c["section"],
            "block": c["block"],          # full block text, or null if orphaned
            "preview": c["preview"],      # stored anchor preview (retained for orphans)
            "body": c["body"],
            "orphaned": c["orphaned"],
            "degraded": c.get("degraded"),  # set only when a legacy sidecar could
                                            # not be read under bare python3
        }
        for c in _open_comments(target_task)
    ]

    data = {
        # `tree` is the focused root→target spine (siblings + direct children,
        # current node marked); a new key added alongside the prior ones so
        # existing consumers of `ancestors`/`task`/`dependencies` are unaffected.
        "tree": focused_tree if show_ancestors else "",
        "ancestors": anc_data,
        "task": task_data,
        "open_comments": open_comments,
        "dependencies": deps_data,
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a task with its context (focused tree + ancestor objectives), full content, and sibling dependency status."
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
        help="Skip the Context block (focused tree + ancestor spine); show only the current task.",
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
        detected = autodetect_plan_root(Path.cwd())
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

    target_task = parse_task(task_md, plan_root)

    # Collect ancestors
    show_ancestors = not args.no_ancestors
    ancestors = _collect_ancestors(plan_root, target_task.path) if show_ancestors else []

    # Collect sibling deps
    siblings = _sibling_map(plan_root, target_task)
    dep_pairs = _dep_tasks(target_task, siblings)

    # Build the focused tree (root → target spine, siblings, direct children).
    focused_tree = ""
    root = None
    if show_ancestors:
        root = walk_plan(plan_root)
        focused_tree = format_focused_tree(root, target_task.path)

    repro = _reproduction_view(plan_root, target_task, root)

    # Render
    if args.as_json:
        print(render_json(ancestors, target_task, dep_pairs, show_ancestors=show_ancestors, focused_tree=focused_tree, repro=repro))
    else:
        print(render_human(ancestors, target_task, dep_pairs, show_ancestors=show_ancestors, focused_tree=focused_tree, repro=repro))


if __name__ == "__main__":
    main()
