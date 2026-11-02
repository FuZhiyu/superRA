#!/usr/bin/env python3
"""Move or rename a task directory while preserving task-tree invariants."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _repro_state import is_online_only
from _task_snapshot import preflight, print_edit_notes
from _task_dependencies import task_index
from _task_io import (
    TASK_ROOT_DIRNAME,
    _contained_regular_relative,
    _read_contained_bytes,
    apply_move_link_rewrites,
    cascade_depends_on_rename,
    compute_move_link_rewrites,
    iter_child_task_dirs,
    parse_task,
    propagate_parent_status,
    resolve_path,
    resolve_plan_root_arg,
    task_path_rewriter,
    write_task,
)
from _task_validate import OUTPUT_CAP

# Authored text a task path can be hard-coded in. Logs, manifests, and data keep
# the path they recorded, and the lock's evidence stays as written.
SOURCE_SUFFIXES = frozenset({
    ".ado", ".bash", ".c", ".cc", ".cfg", ".cpp", ".do", ".go", ".h", ".hpp",
    ".ini", ".ipynb", ".java", ".jl", ".js", ".lua", ".m", ".md", ".pl", ".ps1",
    ".py", ".qmd", ".r", ".rb", ".rmd", ".rs", ".rst", ".sas", ".scala", ".sh",
    ".sql", ".tex", ".toml", ".ts", ".yaml", ".yml", ".zsh",
})
SOURCE_NAMES = frozenset({
    ".gitattributes", ".gitignore", "Dockerfile", "GNUmakefile", "Justfile",
    "Makefile", "Snakefile", "justfile", "makefile",
})


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
        directory
        for directory in iter_child_task_dirs(parent_dir)
        if directory != skip
    ]


def _precheck_same_parent_rename(from_dir: Path) -> None:
    for sibling_dir in _task_sibling_dirs(from_dir.parent, skip=from_dir):
        try:
            parse_task(sibling_dir / "task.md")
        except Exception as exc:
            _die(f"cannot parse sibling {sibling_dir / 'task.md'}: {exc}")


def _precheck_status_ancestors(
    plan_root: Path, start_dir: Path, *, side: str
) -> None:
    """Validate each structural ancestor that status propagation will parse."""
    root = plan_root.resolve()
    current = start_dir
    while True:
        task_md = current / "task.md"
        if task_md.is_symlink():
            _die(f"{side} ancestor task.md is a symlink: {task_md}")
        if not task_md.exists():
            if current == root:  # rootless forests have no structural root task
                return
            _die(f"{side} ancestor is not a task directory: {current}")
        if not task_md.is_file():
            _die(f"{side} ancestor task.md is not a regular file: {task_md}")
        try:
            parse_task(task_md, root)
        except Exception as exc:
            _die(f"cannot parse {side} ancestor {task_md}: {exc}")
        if current == root:
            return
        current = current.parent


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


def _tracked_sources(plan_root: Path) -> tuple[Path, list[Path]] | None:
    """The git worktree holding *plan_root* and its tracked source files, if any."""
    def git(*args: str, cwd: Path) -> bytes | None:
        try:
            done = subprocess.run(
                ["git", "-C", str(cwd), *args], capture_output=True, check=False
            )
        except OSError:
            return None
        return done.stdout if done.returncode == 0 else None

    root = plan_root.resolve()
    top_line = git("rev-parse", "--show-toplevel", cwd=root)
    if top_line is None:
        return None
    top = Path(os.fsdecode(top_line).rstrip("\n")).resolve()
    listed = git("ls-files", "-z", cwd=top)
    if listed is None or not root.is_relative_to(top):
        return None
    paths = {top / os.fsdecode(name) for name in listed.split(b"\0") if name}
    return top, sorted(
        path for path in paths
        if path.suffix.lower() in SOURCE_SUFFIXES or path.name in SOURCE_NAMES
    )


def _project_path_rewrites(
    plan_root: Path, from_dir: Path, to_dir: Path
) -> tuple[Path, dict[Path, str]] | None:
    """Tracked sources hard-coding the moved task's path, as ``{post_move_path: text}``.

    Task-tree Markdown is `compute_move_link_rewrites`' scope; `comments.yaml` is
    review history. An online-only file is skipped rather than downloaded. Returns
    the git worktree with the rewrites, or None outside git.
    """
    tracked = _tracked_sources(plan_root)
    if tracked is None:
        return None
    top, sources = tracked
    root = plan_root.resolve()
    rewrite = task_path_rewriter(plan_root, from_dir, to_dir)
    rewrites: dict[Path, str] = {}
    for path in sources:
        if path.is_relative_to(root) and (
            path.suffix.lower() == ".md" or path.name == "comments.yaml"
        ):
            continue
        try:
            _contained_regular_relative(path, top)
            if is_online_only(path, path.stat()):
                continue
            original = _read_contained_bytes(path, top).decode("utf-8")
        except (OSError, ValueError):  # unreadable, symlinked, or not UTF-8 text
            continue
        rewritten = rewrite(original)
        if rewritten != original:
            moved = path.is_relative_to(from_dir)
            rewrites[to_dir / path.relative_to(from_dir) if moved else path] = rewritten
    return top, rewrites


def _capped(names: list[str], listing_command: str) -> str:
    listed = ", ".join(names[:OUTPUT_CAP])
    if len(names) > OUTPUT_CAP:
        listed += f", and {len(names) - OUTPUT_CAP} more (`{listing_command}` lists them)"
    return listed


def _steps_touched(graph, rewrite, rewritten_files: set[Path], project_root: Path) -> list[str]:
    """Steps the move changes: a declared path, or the bytes of a file they read."""
    touched = []
    for step in graph.steps:
        declared = [step.cmd_logical, *(dep.logical for dep in step.deps)]
        declared += [ref.logical for out in step.outs for ref in (out.path, out.sidecar) if ref]
        if any(rewrite(text) != text for text in declared) or any(
            project_root / dep.resolved in rewritten_files for dep in step.deps
        ):
            touched.append(step.name)
    return sorted(touched)


def rename_task(plan_root: Path, from_path: str, to_path: str) -> None:
    try:
        from_dir = resolve_path(plan_root, from_path)
        to_dir = resolve_path(plan_root, to_path)
    except ValueError as exc:
        _die(str(exc))
    plan_root_resolved = plan_root.resolve()
    from_status_path = from_dir.relative_to(plan_root_resolved).as_posix()
    to_status_path = to_dir.relative_to(plan_root_resolved).as_posix()

    if not from_dir.exists():
        _die(f"source not found: {from_dir}")
    source_task_md = from_dir / "task.md"
    if source_task_md.is_symlink():
        _die(f"source task.md is a symlink: {source_task_md}")
    if not source_task_md.is_file():
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
        _precheck_status_ancestors(plan_root_resolved, from_parent, side="source")
        _precheck_status_ancestors(
            plan_root_resolved, to_parent, side="destination"
        )
        try:
            sibling_drops, moved_drops = _collect_cross_parent_dep_drops(from_dir, to_dir)
        except Exception as exc:
            _die(f"cannot parse a task involved in the move: {exc}")

    def proposed(root, tasks):
        old_parent = from_status_path.rsplit("/", 1)[0] if "/" in from_status_path else ""
        new_parent = to_status_path.rsplit("/", 1)[0] if "/" in to_status_path else ""
        moving = tasks[from_status_path]
        tasks[old_parent].children.remove(moving)
        tasks[new_parent].children.append(moving)
        if old_parent == new_parent:
            for sibling in tasks[new_parent].children:
                sibling.depends_on = [new_slug if d == old_slug else d for d in sibling.depends_on]
        else:
            for sibling in tasks[old_parent].children:
                sibling.depends_on = [d for d in sibling.depends_on if d != old_slug]
            moving.depends_on = [d for d in moving.depends_on if d not in moved_drops]
        for old_path, node in task_index(moving).items():
            node.path = to_status_path + old_path[len(from_status_path):]
            node.dir_path = plan_root / node.path
    try:
        graph = preflight(plan_root, proposed, moved=(from_status_path, to_status_path))
    except ValueError as exc:
        _die(str(exc))

    # Computed before the rename, while the moved subtree is readable at from_dir.
    link_rewrites = compute_move_link_rewrites(plan_root, from_dir, to_dir, moved_root=from_dir)
    project_sweep = _project_path_rewrites(plan_root, from_dir, to_dir)
    project_top, project_rewrites = project_sweep or (None, {})
    from_dir.rename(to_dir)
    try:
        apply_move_link_rewrites(
            project_top if project_rewrites else plan_root,
            {**link_rewrites, **project_rewrites},
        )
    except (OSError, ValueError) as exc:
        try:
            to_dir.rename(from_dir)
        except OSError as rollback_exc:
            _die(
                f"unsafe path rewrite after move ({exc}); "
                f"rollback also failed: {rollback_exc}"
            )
        _die(f"unsafe path rewrite after move; move rolled back: {exc}")
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
        print(f"  Rewrote links and task paths in {len(link_rewrites)} Markdown file(s)")
    if project_rewrites:
        names = sorted(path.relative_to(project_top).as_posix() for path in project_rewrites)
        print(
            f"  Rewrote hard-coded task paths in {len(names)} project file(s): "
            f"{_capped(names, 'git diff --name-only')}"
        )
    if project_sweep is None:
        print(
            f"  Not a git worktree, so project files were not searched for "
            f"{plan_root_resolved.name}/{from_status_path}"
        )
    touched = _steps_touched(
        graph,
        task_path_rewriter(plan_root, from_dir, to_dir),
        set(project_rewrites),
        plan_root_resolved.parent,
    )
    if touched:
        print(
            f"  Rewritten paths leave {len(touched)} step(s) stale until rebuilt or "
            f"accepted: {_capped(touched, 'superra repro status .')}"
        )
    print_edit_notes(graph)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)
    rename_task(plan_root, args.from_path, args.to_path)


if __name__ == "__main__":
    main()
