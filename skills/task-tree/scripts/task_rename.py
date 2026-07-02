#!/usr/bin/env python3
"""Move or rename a task directory while preserving task-tree invariants."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    cascade_depends_on_rename,
    compute_move_link_rewrites,
    parse_task,
    propagate_parent_status,
    resolve_path,
    resolve_plan_root_arg,
    write_task,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move or rename a task and update safe references.")
    parser.add_argument(
        "--plan-root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument("--from", required=True, dest="from_path", help="Current task path")
    parser.add_argument("--to", required=True, dest="to_path", help="New task path")
    return parser.parse_args(argv)


def _die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def _task_sibling_dirs(parent_dir: Path, *, skip: Path | None = None) -> list[Path]:
    return [
        d for d in parent_dir.iterdir()
        if d != skip and d.is_dir() and (d / "task.md").exists()
    ]


def _precheck_same_parent_rename(from_dir: Path) -> None:
    for sibling_dir in _task_sibling_dirs(from_dir.parent, skip=from_dir):
        try:
            parse_task(sibling_dir / "task.md")
        except Exception as exc:
            _die(f"cannot parse sibling {sibling_dir / 'task.md'}: {exc}")


def _collect_cross_parent_dep_drops(
    from_dir: Path, to_dir: Path
) -> tuple[list[tuple[Path, str]], list[str]]:
    """Identify ``depends_on`` edges a cross-parent move strands.

    ``depends_on`` is sibling-only, so an edge that crosses the move has no
    correct re-pointing: the old siblings are not the new siblings. Rather than
    abort, the caller drops these edges and warns. Parsing every involved task
    here also gives the validate-before-mutate guarantee — a malformed sibling or
    moved task raises before any rename.

    Returns ``(sibling_drops, moved_drops)``: ``sibling_drops`` is a list of
    ``(sibling_dir, slug)`` for old siblings that depend on the source slug;
    ``moved_drops`` is the moved task's own ``depends_on`` entries that no longer
    resolve under the destination parent (including a self-edge on the new slug).
    """
    old_slug = from_dir.name
    new_slug = to_dir.name
    moved_task = parse_task(from_dir / "task.md")

    sibling_drops: list[tuple[Path, str]] = []
    for sibling_dir in _task_sibling_dirs(from_dir.parent, skip=from_dir):
        sibling = parse_task(sibling_dir / "task.md")
        if old_slug in sibling.depends_on:
            sibling_drops.append((sibling_dir, old_slug))

    destination_slugs = {d.name for d in _task_sibling_dirs(to_dir.parent)}
    moved_drops = [
        dep for dep in moved_task.depends_on
        if dep == new_slug or dep not in destination_slugs
    ]
    return sibling_drops, moved_drops


def _apply_dep_drops(
    to_dir: Path, sibling_drops: list[tuple[Path, str]], moved_drops: list[str]
) -> list[str]:
    """Drop the stranded edges identified before the move and report each drop.

    Siblings stay in place, so they are edited at their original paths; the moved
    task is now at ``to_dir``. Returns one human-readable warning line per edge.
    """
    warnings: list[str] = []
    for sibling_dir, slug in sibling_drops:
        sibling = parse_task(sibling_dir / "task.md")
        sibling.depends_on = [d for d in sibling.depends_on if d != slug]
        write_task(sibling)
        warnings.append(
            f"dropped stranded depends_on {slug!r} from sibling {sibling_dir.name}"
        )
    if moved_drops:
        drop_set = set(moved_drops)
        moved_task = parse_task(to_dir / "task.md")
        moved_task.depends_on = [d for d in moved_task.depends_on if d not in drop_set]
        write_task(moved_task)
        for slug in moved_drops:
            warnings.append(
                f"dropped stranded depends_on {slug!r} from moved task {to_dir.name} "
                f"(no such sibling under new parent)"
            )
    return warnings


def rename_task(plan_root: Path, from_path: str, to_path: str) -> None:
    from_dir = resolve_path(plan_root, from_path)
    to_dir = resolve_path(plan_root, to_path)
    plan_root_resolved = plan_root.resolve()
    from_status_path = from_dir.relative_to(plan_root_resolved).as_posix()
    to_status_path = to_dir.relative_to(plan_root_resolved).as_posix()

    if not from_dir.exists():
        _die(f"source not found: {from_dir}")
    if not (from_dir / "task.md").exists():
        _die(f"source is not a task directory: {from_dir}")
    if to_dir.exists():
        _die(f"destination already exists: {to_dir}")
    if not to_dir.parent.exists():
        _die(f"destination parent does not exist: {to_dir.parent}")
    if to_dir.parent != plan_root_resolved and not (to_dir.parent / "task.md").exists():
        _die(f"destination parent is not a task directory: {to_dir.parent}")
    try:
        to_dir.resolve().relative_to(from_dir.resolve())
    except ValueError:
        pass
    else:
        _die("destination cannot be inside the source task subtree")

    from_parent = from_dir.parent
    to_parent = to_dir.parent

    old_slug = from_dir.name
    new_slug = to_dir.name

    sibling_drops: list[tuple[Path, str]] = []
    moved_drops: list[str] = []
    if from_parent == to_parent:
        _precheck_same_parent_rename(from_dir)
    else:
        try:
            sibling_drops, moved_drops = _collect_cross_parent_dep_drops(from_dir, to_dir)
        except Exception as exc:
            _die(f"cannot parse a task involved in the move: {exc}")

    # Computed before the rename, while the moved subtree is readable at from_dir.
    link_rewrites = compute_move_link_rewrites(plan_root, from_dir, to_dir, moved_root=from_dir)
    from_dir.rename(to_dir)
    for path, content in link_rewrites.items():
        path.write_text(content, encoding="utf-8")
    print(f"Moved {from_dir} -> {to_dir}")

    if from_parent == to_parent:
        for sibling_name in cascade_depends_on_rename(to_parent, old_slug, new_slug):
            print(f"  Updated depends_on in {sibling_name}")
    else:
        for warning in _apply_dep_drops(to_dir, sibling_drops, moved_drops):
            print(f"Warning: {warning}", file=sys.stderr)
        updated = propagate_parent_status(plan_root, from_status_path)
        updated += propagate_parent_status(plan_root, to_status_path)
        if updated:
            print(f"  Updated status rollup in {updated} ancestor task(s)")
    if link_rewrites:
        print(f"  Rewrote relative markdown links in {len(link_rewrites)} file(s)")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)
    rename_task(plan_root, args.from_path, args.to_path)


if __name__ == "__main__":
    main()
