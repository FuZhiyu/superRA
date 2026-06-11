#!/usr/bin/env python3
"""Move or rename a task directory while preserving task-tree invariants."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    cascade_depends_on_rename,
    parse_task,
    propagate_parent_status,
    resolve_path,
    resolve_plan_root_arg,
)

MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^)\s\n]+)(\))")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


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


def _is_local_markdown_target(target: str) -> bool:
    if not target or target.startswith(("#", "/")):
        return False
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return False
    return True


def _split_target(target: str) -> tuple[str, str, bool]:
    angle_wrapped = target.startswith("<") and target.endswith(">")
    inner = target[1:-1] if angle_wrapped else target
    split_at = len(inner)
    for marker in ("#", "?"):
        pos = inner.find(marker)
        if pos != -1:
            split_at = min(split_at, pos)
    return inner[:split_at], inner[split_at:], angle_wrapped


def _rewrite_markdown_links(text: str, old_md: Path, new_md: Path, from_dir: Path, to_dir: Path) -> str:
    in_fence = False

    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        path_part, suffix, angle_wrapped = _split_target(target)
        if not _is_local_markdown_target(path_part):
            return match.group(0)

        old_target = (old_md.parent / path_part).resolve()
        try:
            target_after_move = to_dir / old_target.relative_to(from_dir.resolve())
        except ValueError:
            target_after_move = old_target

        rel = os.path.relpath(target_after_move, new_md.parent)
        rel = Path(rel).as_posix()
        if rel == ".":
            rel = ""
        new_target = f"{rel}{suffix}"
        if angle_wrapped:
            new_target = f"<{new_target}>"
        return f"{match.group(1)}{new_target}{match.group(3)}"

    rewritten_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            rewritten_lines.append(line)
        elif in_fence:
            rewritten_lines.append(line)
        else:
            rewritten_lines.append(MARKDOWN_LINK_RE.sub(replace, line))
    return "".join(rewritten_lines)


def _collect_markdown_rewrites(from_dir: Path, to_dir: Path) -> dict[Path, str]:
    rewrites: dict[Path, str] = {}
    for old_md in from_dir.rglob("*.md"):
        relative = old_md.relative_to(from_dir)
        new_md = to_dir / relative
        original = old_md.read_text(encoding="utf-8")
        rewritten = _rewrite_markdown_links(original, old_md, new_md, from_dir, to_dir)
        if rewritten != original:
            rewrites[new_md] = rewritten
    return rewrites


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


def _precheck_cross_parent_move(from_dir: Path, to_dir: Path) -> None:
    old_slug = from_dir.name
    new_slug = to_dir.name
    moved_task = parse_task(from_dir / "task.md")

    for sibling_dir in _task_sibling_dirs(from_dir.parent, skip=from_dir):
        sibling = parse_task(sibling_dir / "task.md")
        if old_slug in sibling.depends_on:
            _die(
                f"cross-parent move would strand dependency: {sibling.path} "
                f"depends on source slug {old_slug!r}; remove or rewire it first"
            )

    destination_slugs = {d.name for d in _task_sibling_dirs(to_dir.parent)}
    for dep in moved_task.depends_on:
        if dep == new_slug:
            _die(f"moved task cannot depend on its destination slug {new_slug!r}")
        if dep not in destination_slugs:
            _die(
                f"cross-parent move would strand dependency on {dep!r}; "
                f"no such sibling exists under {to_dir.parent}"
            )


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

    if from_parent == to_parent:
        _precheck_same_parent_rename(from_dir)
    else:
        _precheck_cross_parent_move(from_dir, to_dir)

    markdown_rewrites = _collect_markdown_rewrites(from_dir, to_dir)
    from_dir.rename(to_dir)
    for path, content in markdown_rewrites.items():
        path.write_text(content, encoding="utf-8")
    print(f"Moved {from_dir} -> {to_dir}")

    if from_parent == to_parent:
        for sibling_name in cascade_depends_on_rename(to_parent, old_slug, new_slug):
            print(f"  Updated depends_on in {sibling_name}")
    else:
        updated = propagate_parent_status(plan_root, from_status_path)
        updated += propagate_parent_status(plan_root, to_status_path)
        if updated:
            print(f"  Updated status rollup in {updated} ancestor task(s)")
    if markdown_rewrites:
        print(f"  Rewrote relative markdown links in {len(markdown_rewrites)} file(s)")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)
    rename_task(plan_root, args.from_path, args.to_path)


if __name__ == "__main__":
    main()
