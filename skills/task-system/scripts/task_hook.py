#!/usr/bin/env python3
"""PostToolUse hook: validate task.md and rebuild dashboard on edit/write/move.

Fires after Edit/Write tool calls (targeting a task.md) and after Bash tool
calls that structurally mutate a .plan/ task tree (mv, rm, cp, mkdir, ...).
In both cases it runs the same best-effort reconcile — validate the tree,
propagate parent status, rebuild the dashboard. Always exits 0 — never blocks
the agent.

Claude Code PostToolUse stdin format:
  {
    "tool_name": "Edit" | "Write" | "Bash" | ...,
    "tool_input": {"file_path": "/abs/path/to/file", "command": "...", ...},
    "tool_response": {...}
  }
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _scripts_dir() -> Path:
    return Path(__file__).parent


def _ensure_scripts_on_path() -> None:
    """Add the scripts directory to sys.path so _task_io and plan_dashboard are importable."""
    scripts = str(_scripts_dir())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def _reconcile(plan_root: Path, task_path: str | None) -> None:
    """Validate, propagate parent status, and rebuild the dashboard for a plan tree.

    Each step is best-effort in its own try/except so a failure in one never
    aborts the others or the process. When task_path is None (a structural move
    whose precise location is unknown), parent status is recomputed across the
    whole tree rather than along a single ancestor chain.
    """
    _ensure_scripts_on_path()
    import _task_io as task_io

    # Validate — print warnings to stderr so the agent sees them.
    try:
        warnings = task_io.validate_plan(plan_root)
        if warnings:
            print(f"[task-hook] Validation warnings for {plan_root}:", file=sys.stderr)
            for w in warnings:
                print(f"  WARNING: {w}", file=sys.stderr)
    except Exception as exc:
        print(f"[task-hook] Validation error: {exc}", file=sys.stderr)

    # Propagate parent status up the tree — best-effort, never fail.
    try:
        if task_path is None:
            updated = _propagate_whole_tree(task_io, plan_root)
        else:
            updated = task_io.propagate_parent_status(plan_root, task_path)
        if updated:
            print(f"[task-hook] Propagated status to {updated} ancestor(s).", file=sys.stderr)
    except Exception as exc:
        print(f"[task-hook] Status propagation failed (non-fatal): {exc}", file=sys.stderr)

    # Regenerate dashboard — best-effort, never fail.
    try:
        import plan_dashboard
        plan_dashboard.generate_dashboard(plan_root)
    except Exception as exc:
        print(f"[task-hook] Dashboard rebuild failed (non-fatal): {exc}", file=sys.stderr)


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


# Filesystem-mutating verbs that can restructure a .plan/ task tree.
_MUTATING_RE = re.compile(
    r"(?:^|[\s;&|(])(?:git\s+mv|mv|rm|rmdir|cp|mkdir)(?:\s|$)"
)
# Path-like tokens that mention a .plan directory.
_PLAN_TOKEN_RE = re.compile(r"(?:^|[\s'\"=])((?:[^\s'\"=]*/)?\.plan[^\s'\";|&]*)")


def _find_plan_root_for_token(task_io, token: str, cwd: Path) -> Path | None:
    """Resolve a .plan-containing command token to its plan root directory.

    The token may be a source that no longer exists (post-move) or a
    destination that does not exist yet, so this does not rely on the path
    existing. It splits on the first '.plan' segment and returns the directory
    up to and including it, resolved against cwd when relative.
    """
    raw = Path(token)
    base = raw if raw.is_absolute() else (cwd / raw)
    parts = base.parts
    plan_idx = None
    for i, part in enumerate(parts):
        if part == ".plan" or part.startswith(".plan"):
            plan_idx = i
            break
    if plan_idx is None:
        return None
    plan_root = Path(*parts[: plan_idx + 1])
    if (plan_root / "task.md").exists() or plan_root.is_dir():
        return plan_root
    # The .plan dir itself may have been moved/removed; walk up to an existing one.
    return plan_root if plan_root.exists() else None


def _handle_bash(data: dict) -> None:
    """Reconcile any .plan tree touched by a structural Bash command."""
    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command:
        sys.exit(0)

    # Gate: must reference .plan AND contain a mutating verb. A read-only
    # command that merely mentions .plan (task_query.py, grep .plan, ...) is
    # not a structural change and must early-exit.
    if ".plan" not in command:
        sys.exit(0)
    if not _MUTATING_RE.search(command):
        sys.exit(0)

    _ensure_scripts_on_path()
    import _task_io as task_io

    cwd = Path.cwd()
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

    # Fallback: no resolvable token but the command still touched .plan — try
    # the .plan/ under the process working directory.
    if not plan_roots:
        candidate = cwd / ".plan"
        if candidate.is_dir():
            plan_roots.append(candidate)

    for plan_root in plan_roots:
        if not (plan_root / "task.md").exists() and not plan_root.is_dir():
            continue
        _reconcile(plan_root, task_path=None)

    sys.exit(0)


_COMPLETED_STATES = ("approved", "implemented")

# A `## Revision Notes` section: its header through (but not including) the next
# `## ` header, or end of file.
_REVNOTE_SECTION_RE = re.compile(
    r"(?ms)^[ \t]*##[ \t]+Revision Notes[ \t]*$.*?(?=^[ \t]*##[ \t]+|\Z)"
)


def _body_has_revision_notes(body: str) -> bool:
    """True if the body contains a ``## Revision Notes`` header."""
    return bool(re.search(r"(?m)^[ \t]*##[ \t]+Revision Notes[ \t]*$", body))


def _strip_revision_notes(body: str) -> str:
    """Remove the entire ``## Revision Notes`` section from a task body."""
    return _REVNOTE_SECTION_RE.sub("", body)


def _recover_prior_status(task_io, file_path: Path) -> str | None:
    """Recover the last committed status of a task.md, best-effort.

    Tries the staged (index) version first, then HEAD. Returns the parsed
    ``status`` frontmatter value, or None when the prior state cannot be
    recovered (file not committed/staged, not in a git tree, git unavailable,
    or unparseable). A None result must map to the safe no-op fallback —
    never a destructive guess.
    """
    work_dir = file_path.parent
    try:
        toplevel = subprocess.run(
            ["git", "-C", str(work_dir), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return None
    if toplevel.returncode != 0:
        return None
    repo_root = Path(toplevel.stdout.strip())
    try:
        rel = file_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return None

    for ref in (f":{rel}", f"HEAD:{rel}"):
        try:
            shown = subprocess.run(
                ["git", "-C", str(repo_root), "show", ref],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            continue
        if shown.returncode != 0:
            continue
        try:
            fm, _ = task_io.parse_frontmatter(shown.stdout)
        except Exception:
            continue
        status = fm.get("status")
        if isinstance(status, str) and status:
            return status
    return None


def _reconcile_revision_notes(task_io, file_path: Path) -> None:
    """Run the revision-note ↔ status automation on an edited leaf task.md.

    Behavior A — a revision note added to a completed task (approved/implemented)
    that did NOT just transition to approved → flip status to ``revise``.
    Behavior B — a task flipped TO approved that still carries a revision note →
    remove the section.

    Both intents share the identical ``{approved + revnote}`` end-state; the
    discriminator is whether status changed to ``approved`` in this edit,
    recovered from the last committed version. When the prior status cannot be
    recovered the automation is a no-op (the safe fallback), since a wrong guess
    could delete a planner's revision note.

    Only leaf tasks are touched — a branch's status is rolled up from its
    children, so its authored frontmatter status is not a target for this flip.
    """
    # Leaf check: a task directory with any child task.md is a branch.
    task_dir = file_path.parent
    for child in task_dir.iterdir():
        if child.is_dir() and (child / "task.md").exists():
            return

    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return

    fm, body = task_io.parse_frontmatter(text)
    status = fm.get("status")
    if not isinstance(status, str) or not status:
        return

    has_revnote = _body_has_revision_notes(body)

    # Behavior A and B only act on completed states carrying a revision note.
    if status not in _COMPLETED_STATES or not has_revnote:
        return

    prior_status = _recover_prior_status(task_io, file_path)
    if prior_status is None:
        # Safe fallback: cannot tell A from B, so leave the note untouched.
        return

    new_text: str | None = None
    if status == "approved" and prior_status != "approved":
        # Behavior B — approval transition: the rework is done, clean the note.
        stripped = _strip_revision_notes(body)
        new_text = f"---\n{task_io.serialize_frontmatter(fm)}---\n{stripped}"
    elif status == prior_status:
        # Behavior A — note added to a still-completed task: route back to revise.
        fm["status"] = "revise"
        new_text = f"---\n{task_io.serialize_frontmatter(fm)}---\n{body}"

    if new_text is not None:
        try:
            file_path.write_text(new_text, encoding="utf-8")
            print(
                f"[task-hook] Revision-note lifecycle applied to {file_path}.",
                file=sys.stderr,
            )
        except Exception as exc:
            print(
                f"[task-hook] Revision-note reconcile failed (non-fatal): {exc}",
                file=sys.stderr,
            )


def _handle_edit_write(data: dict) -> None:
    """Reconcile the plan tree for an Edit/Write of a task.md."""
    tool_input = data.get("tool_input", {}) or {}
    file_path_str = tool_input.get("file_path", "")
    if not file_path_str:
        sys.exit(0)

    file_path = Path(file_path_str)

    # Must be named task.md
    if file_path.name != "task.md":
        sys.exit(0)

    # Must be inside a .plan/ directory somewhere in the path
    parts = file_path.parts
    if not any(p.startswith(".plan") for p in parts):
        sys.exit(0)

    _ensure_scripts_on_path()
    import _task_io as task_io
    plan_root = task_io._find_plan_root(file_path.parent)
    if plan_root is None:
        sys.exit(0)

    task_path = str(file_path.parent.relative_to(plan_root))
    if task_path == ".":
        task_path = ""

    # Run the revision-note ↔ status automation first so a status flip is
    # reflected before parent rollup. Best-effort, never blocks.
    try:
        _reconcile_revision_notes(task_io, file_path)
    except Exception as exc:
        print(
            f"[task-hook] Revision-note reconcile failed (non-fatal): {exc}",
            file=sys.stderr,
        )

    _reconcile(plan_root, task_path=task_path)
    sys.exit(0)


def main() -> None:
    # Read tool call info from stdin (Claude Code PostToolUse protocol)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name = data.get("tool_name", "") or data.get("tool", "")

    if tool_name == "Bash":
        _handle_bash(data)
    elif tool_name in ("Edit", "Write"):
        _handle_edit_write(data)

    sys.exit(0)


if __name__ == "__main__":
    main()
