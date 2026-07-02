#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""PostToolUse hook: validate task.md and propagate status on edit/write/move.

Fires after Edit/Write tool calls (targeting a task.md) and after Bash tool
calls that structurally mutate a task tree (mv, rm, cp, mkdir, ...).
In both cases it runs the same best-effort reconcile — validate the tree and
propagate parent status. It does not write the dashboard; a static dashboard is
produced only on explicit `superra dashboard export`. Always exits 0 — never
blocks the agent. Validation warnings and non-fatal reconcile failures are
injected through PostToolUse JSON on stdout; successful/ignored paths stay silent
except in Codex empty-JSON mode, where no-feedback paths emit `{}` because
Codex requires parseable hook JSON.

PostToolUse stdin format:
  {
    "tool_name": "Edit" | "Write" | "Bash" | "apply_patch" | ...,
    "tool_input": {"file_path": "/abs/path/to/file", "command": "...", ...},
    "tool_response": {...}
  }
"""

from __future__ import annotations

import json
import os
import re
import sys
import warnings
from pathlib import Path


TASK_ROOT_DIRNAME = "superRA"
LEGACY_TASK_ROOT_DIRNAME = ".plan"
TASK_ROOT_DIRNAMES = (TASK_ROOT_DIRNAME, LEGACY_TASK_ROOT_DIRNAME)
CODEX_EMPTY_JSON_ENV = "SUPERRA_TASK_HOOK_EMPTY_JSON"
_CODEX_EMPTY_JSON_MODE = False


def _scripts_dir() -> Path:
    return Path(__file__).parent


def _ensure_scripts_on_path() -> None:
    """Add the scripts directory to sys.path so _task_io is importable."""
    scripts = str(_scripts_dir())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def _is_markdown_under_task_root(file_path: Path) -> bool:
    """True when file_path is a `.md` file somewhere inside a task root.

    Cheap gate for the hot path: a suffix check plus a path-parts scan, no file
    read. The common non-markdown edit short-circuits here before anything else.
    """
    if file_path.suffix.lower() != ".md":
        return False
    return any(
        p == TASK_ROOT_DIRNAME
        or p == LEGACY_TASK_ROOT_DIRNAME
        or p.startswith(f"{LEGACY_TASK_ROOT_DIRNAME}.")
        for p in file_path.parts
    )


def _markdown_integrity_feedback(file_path: Path) -> list[str]:
    """Run the render-integrity checker on a `.md` under a task root.

    The detection logic lives in the sibling report-in-markdown skill; this only
    imports and calls it. Resolves the checker relative to this file's own
    location (skills/task-tree/scripts -> skills/report-in-markdown/scripts) so
    it works across local checkout, plugin cache, and GitHub-clone installs where
    the whole skills/ tree ships together. Best-effort: any failure (gate miss,
    unreadable file, import or check error) returns no feedback rather than
    breaking the hook.
    """
    if not _is_markdown_under_task_root(file_path):
        return []
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        md_scripts = _scripts_dir().parent.parent / "report-in-markdown" / "scripts"
        if str(md_scripts) not in sys.path:
            sys.path.insert(0, str(md_scripts))
        import md_integrity
        issues = md_integrity.check(text)
    except Exception:
        return []
    return [
        f"Markdown render-integrity issue in {file_path}:{it.line} "
        f"[{it.rule}] {it.message}"
        for it in issues
    ]


def _feedback_json(feedback: list[str]) -> str:
    context = (
        "<IMPORTANT>Task-system hook feedback:\n"
        + "\n".join(f"- {line}" for line in feedback)
        + "\n\nThe hook stayed non-blocking; fix the task tree before proceeding."
        + "</IMPORTANT>"
    )
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            },
        },
        separators=(",", ":"),
    )


def _truthy_env(name: str) -> bool:
    value = os.environ.get(name, "")
    return value.lower() not in ("", "0", "false", "no", "off")


def _emit_empty_json_if_needed() -> None:
    if _CODEX_EMPTY_JSON_MODE or _truthy_env(CODEX_EMPTY_JSON_ENV):
        print("{}")


def _exit_success(feedback: list[str] | None = None) -> None:
    feedback = feedback or []
    if feedback:
        print(_feedback_json(feedback))
    else:
        _emit_empty_json_if_needed()
    sys.exit(0)


def _reconcile(plan_root: Path, task_path: str | None) -> list[str]:
    """Validate and propagate parent status for a plan tree.

    Each step is best-effort in its own try/except so a failure in one never
    aborts the others or the process. When task_path is None (a structural move
    whose precise location is unknown), parent status is recomputed across the
    whole tree rather than along a single ancestor chain. The dashboard is not
    regenerated here; it is produced only on explicit `superra dashboard export`.
    """
    _ensure_scripts_on_path()
    import _task_io as task_io
    import _task_validate as task_validate
    feedback: list[str] = []

    # Validate — collect warnings for model-visible JSON feedback.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            validation_warnings = task_validate.validate_plan(plan_root)
        if validation_warnings:
            for w in validation_warnings:
                feedback.append(f"Validation warning in {plan_root}: {w}")
    except Exception as exc:
        feedback.append(f"Validation failed for {plan_root}: {exc}")

    # Propagate parent status up the tree — best-effort, never fail.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if task_path is None:
                _propagate_whole_tree(task_io, plan_root)
            else:
                task_io.propagate_parent_status(plan_root, task_path)
    except Exception as exc:
        feedback.append(f"Status propagation failed for {plan_root} (non-fatal): {exc}")

    return feedback


def _propagate_whole_tree(task_io, plan_root: Path) -> int:
    """Recompute parent status across every branch in the tree.

    propagate_parent_status only walks the ancestors of one task_path, so a
    structural move (which can change several branches at once) needs every
    leaf's ancestor chain recomputed. Propagating from each leaf covers all
    intermediate parents; counts are summed for the stderr note.
    """
    root = task_io.walk_plan(plan_root)
    leaf_paths: list[str] = []

    def _collect(task) -> None:
        if task.is_leaf:
            if task.path:
                leaf_paths.append(task.path)
        else:
            for child in task.children:
                _collect(child)

    _collect(root)

    updated = 0
    for leaf_path in leaf_paths:
        updated += task_io.propagate_parent_status(plan_root, leaf_path)
    return updated


# Filesystem-mutating verbs that can restructure a task tree.
_MUTATING_RE = re.compile(
    r"(?:^|[\s;&|(])(?:git\s+mv|mv|rm|rmdir|cp|mkdir)(?:\s|$)"
)
# Path-like tokens that mention a task-root directory.
_PLAN_TOKEN_RE = re.compile(
    r"(?:^|[\s'\"=])((?:[^\s'\"=]*/)?(?:superRA(?=$|/|[\s'\";|&])(?:/[^\s'\";|&]*)?|\.plan[^\s'\";|&]*))"
)
_APPLY_PATCH_FILE_RE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File: (?P<path>.+)$|^\*\*\* Move to: (?P<move_to>.+)$"
)


def _command_mentions_task_root(command: str) -> bool:
    return _PLAN_TOKEN_RE.search(command) is not None


# A bare `mv`/`git mv SRC DST` with exactly two task-root path operands — the
# shape of a directory rename. Flags and extra operands fall through to the
# generic reconcile path (no auto-cascade) rather than being mis-parsed.
_MV_RE = re.compile(r"(?:^|[\s;&|(])(?:git\s+mv|mv)(\s+.*)$")


def _detect_same_parent_rename(command: str, cwd: Path) -> tuple[Path, str, str] | None:
    """Return (parent_dir, old_slug, new_slug) for a same-parent task rename.

    Detects the lossless case `mv superRA/a/x superRA/a/y` (or `git mv`): a
    two-operand move whose source and destination share a parent and differ only
    in the final slug, with both inside a task root. Returns None for anything
    else (flags, >2 operands, cross-parent move, non-task-root paths) so those
    fall through to the warn-only reconcile path. Slugs are resolved from the
    command text (the hook fires post-move, so the source no longer exists), but
    the move-into-dir vs. rename disambiguation reads post-move filesystem state:
    after a clean rename `dst/<src basename>` does not exist, whereas after a
    move-into-existing-dir the moved task is sitting at `dst/<src basename>/task.md`.
    """
    match = _MV_RE.search(command)
    if match is None:
        return None
    operands = match.group(1).split()
    # A flag (e.g. -f, --verbose) means we cannot trust the two-operand shape.
    if any(op.startswith("-") for op in operands):
        return None
    if len(operands) != 2:
        return None

    src_raw, dst_raw = (op.strip("'\"") for op in operands)
    src = Path(src_raw)
    dst = Path(dst_raw)
    src_abs = src if src.is_absolute() else (cwd / src)
    dst_abs = dst if dst.is_absolute() else (cwd / dst)

    # `mv x y/` (trailing slash) means "move into the directory y", i.e. a
    # re-parent whose result is y/x — not a rename. This is the explicit
    # move-into-dir spelling; reject it from the command text up front.
    if dst_raw.endswith("/"):
        return None

    if src_abs.parent != dst_abs.parent:
        return None
    if src_abs.name == dst_abs.name:
        return None

    parent = dst_abs.parent
    # Both operands must sit inside a task root for this to be a task rename.
    parts = parent.parts
    if not any(p in TASK_ROOT_DIRNAMES or p.startswith(f"{LEGACY_TASK_ROOT_DIRNAME}.")
               for p in parts):
        return None
    # The renamed directory must itself be a task (have a task.md post-move).
    if not (dst_abs / "task.md").exists():
        return None
    # A bare `mv x existing-task` where the destination is a pre-existing task
    # directory is a move-INTO-dir, not a rename: `mv` lands the source at
    # `existing-task/x`, so `dst/<src basename>/task.md` exists post-move. That is
    # a cross-parent re-parent (warn-only), and reading it as a rename would
    # silently re-point dependents to the wrong task. A clean rename never leaves
    # `dst/<src basename>/task.md` behind, so this rejects only the re-parent.
    if (dst_abs / src_abs.name / "task.md").exists():
        return None

    return parent, src_abs.name, dst_abs.name


def _find_plan_root_for_token(task_io, token: str, cwd: Path) -> Path | None:
    """Resolve a task-root-containing command token to its plan root directory.

    The token may be a source that no longer exists (post-move) or a
    destination that does not exist yet, so this does not rely on the path
    existing. It splits on the first task-root segment and returns the
    directory up to and including it, resolved against cwd when relative.
    """
    raw = Path(token)
    base = raw if raw.is_absolute() else (cwd / raw)
    parts = base.parts
    plan_idx = None
    for i, part in enumerate(parts):
        if part == TASK_ROOT_DIRNAME or part == LEGACY_TASK_ROOT_DIRNAME or part.startswith(f"{LEGACY_TASK_ROOT_DIRNAME}."):
            plan_idx = i
            break
    if plan_idx is None:
        return None
    plan_root = Path(*parts[: plan_idx + 1])
    if (plan_root / "task.md").exists() or plan_root.is_dir():
        return plan_root
    # The task root itself may have been moved/removed; walk up to an existing one.
    return plan_root if plan_root.exists() else None


def _handle_bash(data: dict) -> None:
    """Reconcile any task tree touched by a structural Bash command."""
    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command:
        _exit_success()

    # Gate: must reference a task root AND contain a mutating verb. A read-only
    # command that merely mentions a task root (task_query.py, grep, serve) is
    # not a structural change and must early-exit.
    if not _command_mentions_task_root(command):
        _exit_success()
    if not _MUTATING_RE.search(command):
        _exit_success()

    _ensure_scripts_on_path()
    import _task_io as task_io

    cwd = Path.cwd()

    # Lossless same-parent rename: auto-cascade sibling depends_on before
    # reconcile, the same class of YAML-metadata maintenance the hook already
    # does for status rollups. Runs first so validate_plan sees the rewired
    # edges and emits no spurious dangling-dependency warning. Cross-parent
    # moves, deletes, and merges are deliberately left to warn (handled below in
    # the generic reconcile) — those need a human decision, never a silent guess.
    rewire_feedback: list[str] = []
    rename = _detect_same_parent_rename(command, cwd)
    if rename is not None:
        parent_dir, old_slug, new_slug = rename
        try:
            updated = task_io.cascade_depends_on_rename(parent_dir, old_slug, new_slug)
            if updated:
                rewire_feedback.append(
                    f"Auto-rewired depends_on '{old_slug}' -> '{new_slug}' in "
                    f"sibling task(s): {', '.join(sorted(updated))}."
                )
        except Exception as exc:
            rewire_feedback.append(
                f"depends_on rewire failed for rename {old_slug} -> {new_slug} "
                f"(non-fatal): {exc}"
            )
        # Same maintenance class as the depends_on cascade: a rename can break
        # relative Markdown links pointing into or out of the renamed task.
        # Computed post-move (the subtree now lives at parent_dir/new_slug), so
        # moved_root is the destination.
        try:
            link_root = task_io._find_plan_root(parent_dir)
            if link_root is not None:
                link_rewrites = task_io.compute_move_link_rewrites(
                    link_root,
                    parent_dir / old_slug,
                    parent_dir / new_slug,
                    moved_root=parent_dir / new_slug,
                )
                for path, content in link_rewrites.items():
                    path.write_text(content, encoding="utf-8")
                if link_rewrites:
                    rewire_feedback.append(
                        f"Auto-rewrote relative markdown links in "
                        f"{len(link_rewrites)} file(s) after rename "
                        f"'{old_slug}' -> '{new_slug}'."
                    )
        except Exception as exc:
            rewire_feedback.append(
                f"link rewrite failed for rename {old_slug} -> {new_slug} "
                f"(non-fatal): {exc}"
            )

    plan_roots: list[Path] = []
    seen: set[Path] = set()

    for match in _PLAN_TOKEN_RE.finditer(command):
        token = match.group(1)
        root = _find_plan_root_for_token(task_io, token, cwd)
        if root is None:
            continue
        resolved = root.resolve() if root.exists() else root
        if resolved in seen:
            continue
        seen.add(resolved)
        plan_roots.append(root)

    # Fallback: no resolvable token but the command still touched a task root —
    # try the standard roots under the process working directory.
    if not plan_roots:
        for dirname in TASK_ROOT_DIRNAMES:
            candidate = cwd / dirname
            if candidate.is_dir():
                plan_roots.append(candidate)
                break

    feedback: list[str] = list(rewire_feedback)
    for plan_root in plan_roots:
        if not (plan_root / "task.md").exists() and not plan_root.is_dir():
            continue
        feedback.extend(_reconcile(plan_root, task_path=None))

    _exit_success(feedback)


def _handle_edit_write(data: dict) -> None:
    """Handle an Edit/Write: reconcile task.md edits and render-integrity-check
    any .md edited under a task root.

    Two branches that merge into one feedback emission: the task.md-only
    reconcile (validate + status propagation) and the broader render-integrity
    check that runs on any .md under a task root (including task.md). The cheap
    .md-under-task-root gate short-circuits the common non-markdown edit before
    any file read.
    """
    tool_input = data.get("tool_input", {}) or {}
    file_path_str = tool_input.get("file_path", "")
    if not file_path_str:
        _exit_success()

    file_path = Path(file_path_str)

    # Cheap gate: only a .md under a task root is of interest to either branch.
    if not _is_markdown_under_task_root(file_path):
        _exit_success()

    feedback: list[str] = []

    # task.md-only branch: validate the tree and propagate parent status.
    if file_path.name == "task.md":
        _ensure_scripts_on_path()
        import _task_io as task_io
        plan_root = task_io._find_plan_root(file_path.parent)
        if plan_root is not None:
            task_path = str(file_path.parent.relative_to(plan_root))
            if task_path == ".":
                task_path = ""
            feedback.extend(_reconcile(plan_root, task_path=task_path))

    # Broader branch: render-integrity-check any .md under a task root.
    feedback.extend(_markdown_integrity_feedback(file_path))

    _exit_success(feedback)


def _task_path_from_file_path(file_path: Path) -> tuple[Path, str] | None:
    """Return (plan_root, task_path) when file_path names a task.md in a task tree."""
    if file_path.name != "task.md":
        return None

    parts = file_path.parts
    if not any(p == TASK_ROOT_DIRNAME or p == LEGACY_TASK_ROOT_DIRNAME or p.startswith(f"{LEGACY_TASK_ROOT_DIRNAME}.") for p in parts):
        return None

    _ensure_scripts_on_path()
    import _task_io as task_io

    plan_root = task_io._find_plan_root(file_path.parent)
    if plan_root is None:
        return None

    task_path = str(file_path.parent.relative_to(plan_root))
    if task_path == ".":
        task_path = ""
    return plan_root, task_path


def _apply_patch_paths(command: str) -> list[str]:
    """Extract file paths from an apply_patch command payload."""
    paths: list[str] = []
    for line in command.splitlines():
        match = _APPLY_PATCH_FILE_RE.match(line)
        if not match:
            continue
        path = match.group("path") or match.group("move_to") or ""
        path = path.strip()
        if path:
            paths.append(path)
    return paths


def _handle_apply_patch(data: dict) -> None:
    """Reconcile task trees touched by Codex apply_patch file edits."""
    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command:
        _exit_success()

    cwd = Path.cwd()
    roots: list[Path] = []
    seen: set[Path] = set()
    feedback: list[str] = []

    for raw_path in _apply_patch_paths(command):
        path = Path(raw_path)
        file_path = path if path.is_absolute() else cwd / path

        # Render-integrity-check any .md under a task root (including task.md);
        # the cheap gate inside short-circuits everything else.
        feedback.extend(_markdown_integrity_feedback(file_path))

        # task.md-only branch: reconcile the touched plan tree once.
        match = _task_path_from_file_path(file_path)
        if match is None:
            continue
        plan_root, _task_path = match
        resolved = plan_root.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append(plan_root)

    for plan_root in roots:
        feedback.extend(_reconcile(plan_root, task_path=None))

    _exit_success(feedback)


def main() -> None:
    global _CODEX_EMPTY_JSON_MODE

    # Read tool call info from stdin (Claude Code PostToolUse protocol)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name = data.get("tool_name", "") or data.get("tool", "")
    _CODEX_EMPTY_JSON_MODE = (
        _truthy_env(CODEX_EMPTY_JSON_ENV)
        or tool_name == "apply_patch"
    )

    if tool_name == "Bash":
        _handle_bash(data)
    elif tool_name == "apply_patch":
        _handle_apply_patch(data)
    elif tool_name in ("Edit", "Write"):
        _handle_edit_write(data)

    _exit_success()


if __name__ == "__main__":
    main()
