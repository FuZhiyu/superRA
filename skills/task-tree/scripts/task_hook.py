#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""PostToolUse hook: validate task.md and propagate status on edit/write/move.

Fires after Edit/Write/apply_patch and Bash tool calls. The edited files are
the paths the tool call supplies plus those `_edit_detect` finds changed on
disk, so an edit made through a Bash heredoc or `sed -i` is handled like an
Edit (`_process_paths`). A changed task.md gets the best-effort reconcile —
validate the tree and propagate parent status — as does a Bash call that
structurally mutates a task tree (mv, rm, cp, mkdir, ...). It also carries two
advisory reproduction signals, both non-blocking: a reminder, once per file
per session, when a changed file is a registered step's dep/script (or sits in
a declared dependency directory), an unregistered script under a task root, or
a new script of a configured runner's language beside the registered scripts,
naming the steps the edit stales (`_reproduction_reminder`, emitted through
`_repro_emit`); and, once
per transition, a reminder when a leaf reaches `implemented` with results
files no step produces or reads (`_implemented_coverage_reminder`).
It does not write the dashboard; a static dashboard is produced only on
explicit `superra dashboard export`. Always exits 0 — never blocks the agent.
A UserPromptSubmit event only seeds the session's edit baseline, so an edit in
the session's first tool call is still seen. A task.md edit reports validation
warnings for the edited task only. Validation warnings and non-fatal reconcile failures are injected through
PostToolUse JSON on stdout; successful/ignored paths stay silent except in
Codex empty-JSON mode, where no-feedback paths emit `{}` because Codex
requires parseable hook JSON.

PostToolUse stdin format:
  {
    "session_id": "...",
    "tool_name": "Edit" | "Write" | "Bash" | "apply_patch" | ...,
    "tool_input": {"file_path": "/abs/path/to/file", "command": "...", ...},
    "tool_response": {...}
  }
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import warnings
from pathlib import Path


TASK_ROOT_DIRNAME = "superRA"
LEGACY_TASK_ROOT_DIRNAME = ".plan"
TASK_ROOT_DIRNAMES = (TASK_ROOT_DIRNAME, LEGACY_TASK_ROOT_DIRNAME)
CODEX_EMPTY_JSON_ENV = "SUPERRA_TASK_HOOK_EMPTY_JSON"
_CODEX_EMPTY_JSON_MODE = False
# Set once a reconcile ran in this process: it may have rewritten task files.
_RECONCILED = False

# Reproduction reminder: a gitignored state dir, sibling of the task root, that
# holds one empty marker file per (session, resolved producer path) already
# reminded. `02-runner`'s own state directory is expected to reuse this name.
REPRO_STATE_DIRNAME = ".superra-repro"
# Paths the detector found newly created in this call (see `_detected_paths`).
_CREATED: set[str] = set()
REPRO_MARKER_SUBDIR = "hook-markers"
# The `implemented` reminder tracks a status transition rather than a session,
# so its markers live under one fixed key instead of a per-session one.
IMPLEMENTED_MARKER_KEY = "transitions"


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

    The detection logic lives in the sibling communicate skill; this only
    imports and calls it. Resolves the checker relative to this file's own
    location (skills/task-tree/scripts -> skills/communicate/scripts) so
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
        md_scripts = _scripts_dir().parent.parent / "communicate" / "scripts"
        if str(md_scripts) not in sys.path:
            sys.path.insert(0, str(md_scripts))
        import md_integrity
        issues = md_integrity.check(text)
    except Exception:
        return []
    if not issues:
        return []
    feedback = [
        f"Markdown render-integrity issue in {file_path}:{it.line} "
        f"[{it.rule}] {it.message}"
        for it in issues
    ]
    feedback.append(
        "Load the `superRA:communicate` skill and its `references/markdown.md` "
        "for the correct form before fixing these."
    )
    return feedback


def _communicate_reminder(file_paths: list[Path]) -> list[str]:
    """Remind after Markdown edits under a task root without blocking."""
    paths: list[str] = []
    seen: set[Path] = set()
    for file_path in file_paths:
        if not _is_markdown_under_task_root(file_path) or file_path in seen:
            continue
        seen.add(file_path)
        paths.append(str(file_path))
    if not paths:
        return []
    return [
        f"Markdown edited. If these edits are "
        "meant for a user to read, make sure they follow `superRA:communicate` and its "
        "`references/markdown.md`; otherwise continue."
    ]


def _repro_plan_root_for_file(file_path: Path) -> Path | None:
    """Walk up from an edited file to the nearest task tree beside it.

    A producer file (script, helper) usually lives beside the task tree, not
    inside it, so this looks for a `superRA/`/`.plan/` *child* at each
    ancestor level — unlike `_find_plan_root`, which expects the task tree
    itself among the file's own ancestors. Never touches process cwd, so a
    file resolves to the same project regardless of where the hook subprocess
    was launched from.
    """
    current = file_path.parent
    while True:
        for dirname in TASK_ROOT_DIRNAMES:
            candidate = current / dirname
            if candidate.is_dir():
                return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _repro_session_key(data: dict) -> str:
    """One key per session; a payload with no session id dedupes hourly instead.

    Both Claude Code's and Codex's PostToolUse payloads carry `session_id`
    (verified against Codex CLI 0.152.1's hook wire schema), so this is the
    common case; the hourly fallback exists for a harness whose payload omits
    it, so a marker still expires rather than suppressing forever.
    """
    session_id = data.get("session_id")
    if session_id:
        digest = hashlib.sha256(str(session_id).encode("utf-8")).hexdigest()[:16]
        return f"session-{digest}"
    return f"hour-{int(time.time() // 3600)}"


def _repro_marker_path(project_root: Path, session_key: str, resolved_path: str) -> Path:
    digest = hashlib.sha256(resolved_path.encode("utf-8")).hexdigest()[:32]
    return project_root / REPRO_STATE_DIRNAME / REPRO_MARKER_SUBDIR / session_key / digest


def _no_shell(command: str, cwd: Path) -> str:
    """Stand-in for a `shell:` resolver: an inert placeholder no real path matches."""
    return "${shell}"


def _hook_graph(plan_root: Path):
    """The reproduction graph for matching edits: literal and `env:` variables
    resolve; a `shell:` resolver never runs and its paths match nothing."""
    import _repro
    return _repro.build_graph(
        plan_root, project_root=plan_root.parent, shell_runner=_no_shell
    )


def _repro_owning_steps(graph, rel: str) -> list[str]:
    """Names of steps whose deps (declared, script, or Julia closure) reach rel."""
    names = []
    for step in graph.steps:
        for dep in step.deps:
            if rel == dep.resolved or rel.startswith(dep.resolved + "/"):
                names.append(step.name)
                break
    return names


def _repro_is_out(graph, rel: str) -> bool:
    """A step's out is rewritten by a rerun, even when another step reads it."""
    return any(rel == out or rel.startswith(out + "/") for out in graph.producers)


# More reminders than this in one call (a checkout, a merge) collapse to one line.
REPRO_REMINDER_CAP = 5


def _repro_status_targets(graph, owners: list[str]) -> str:
    """`superra repro status` targets for *owners* — the command needs at least
    one, and `.` selects every registered step when no step owns the file."""
    by_name = {step.name: step for step in graph.steps}
    targets = sorted(
        f"{by_name[name].task_path}#{name}" for name in owners if name in by_name
    )
    return " ".join(targets) if targets else "."


def _repro_message(rel: str, owners: list[str], fan_out: str = "", targets: str = ".") -> str:
    owner_text = ", ".join(sorted(owners)) if owners else "none"
    stales = f"Stales {fan_out}. " if fan_out else ""
    return (
        f"Reproduction: {rel} changed (owning step(s): {owner_text}). {stales}Update the "
        f"step's deps/outs or register a new step, then run `superra repro status {targets}`."
    )


def _repro_fan_out(graph, project_root: Path, owners: list[str]) -> str:
    """The steps this edit stales and what rerunning them last cost."""
    if not owners:
        return ""
    try:
        import _repro_signals
        names = _repro_signals.downstream_steps(graph, owners)
        return _repro_signals.format_fan_out(
            names, _repro_signals.step_durations(project_root, names)
        )
    except Exception:
        return ""


def _repro_soft_message(rel: str) -> str:
    return (
        f"Reproduction: new script {rel}. If it produces retained results it may "
        "need a step (`superRA:reproducibility` has the call); many scripts never do."
    )


def _repro_emit(
    data: dict,
    graph,
    project_root: Path,
    rel_paths: list[str],
    soft: frozenset[str] = frozenset(),
) -> list[str]:
    """Message each changed path once per session, with its staleness fan-out.

    Takes project-relative paths from whichever detector found them, so every
    detector draws the identical reminder under one marker per file per
    session. Paths in *soft* are new scripts no step owns: they draw the
    lighter reminder.
    """
    feedback: list[str] = []
    session_key: str | None = None
    for rel in rel_paths:
        if session_key is None:
            session_key = _repro_session_key(data)
        marker = _repro_marker_path(project_root, session_key, rel)
        if marker.exists():
            continue
        owners = _repro_owning_steps(graph, rel)
        if rel in soft:
            feedback.append(_repro_soft_message(rel))
        else:
            feedback.append(
                _repro_message(
                    rel,
                    owners,
                    _repro_fan_out(graph, project_root, owners),
                    _repro_status_targets(graph, owners),
                )
            )
        try:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
        except OSError:
            pass
    return feedback


def _reproduction_reminder(data: dict, file_paths: list[Path]) -> list[str]:
    """Remind once per file per session when an edit touches a producer input.

    Fires when the file is a dep or script of a registered step (including a
    Julia include closure or a file in a declared directory), is a script under
    the task root that no step registers, or is a script newly created beside
    the registered scripts (`.jl` for a `julia` runner). A step's out and a task
    file never trigger. The graph used for matching resolves literal and `env:`
    variables and never runs a `shell:` resolver (`_hook_graph`), so no
    subprocess for *any* edit. Built at most once per distinct plan_root, so a
    multi-file apply_patch does not rebuild per file. Fails open: no task tree
    beside the file, no reproduction config anywhere, or any
    graph-construction problem is silence, never a block.
    """
    candidates = [p for p in file_paths if p.name != "task.md"]
    if not candidates:
        return []

    _ensure_scripts_on_path()

    by_plan_root: dict[Path, list[Path]] = {}
    for file_path in candidates:
        plan_root = _repro_plan_root_for_file(file_path)
        if plan_root is not None:
            by_plan_root.setdefault(plan_root, []).append(file_path)

    feedback: list[str] = []

    for plan_root, paths in by_plan_root.items():
        project_root = plan_root.parent
        try:
            import _edit_detect
            import _repro
            import _repro_signals
            graph = _hook_graph(plan_root)
            if not _repro_signals.has_reproduction(graph):
                continue  # no reproduction config anywhere: nothing to match
            script_suffixes = set(_edit_detect.runner_suffixes(graph.config.runners))
        except Exception:
            continue

        task_root_prefix = plan_root.name + "/"
        relevant: list[str] = []
        soft: set[str] = set()
        for file_path in paths:
            try:
                rel = file_path.resolve().relative_to(project_root.resolve())
            except (ValueError, OSError):
                continue
            rel_str = _repro._norm(rel.as_posix())
            if _repro_is_out(graph, rel_str):
                continue
            unregistered_companion = rel_str.startswith(
                task_root_prefix
            ) and _edit_detect.is_script(file_path)
            owned = bool(_repro_owning_steps(graph, rel_str))
            new_script = (
                not owned
                and not unregistered_companion
                and file_path.suffix.lower() in script_suffixes
                and str(file_path.resolve()) in _CREATED
            )
            if owned or unregistered_companion or new_script:
                relevant.append(rel_str)
                if new_script:
                    soft.add(rel_str)
        feedback.extend(_repro_emit(data, graph, project_root, relevant, frozenset(soft)))

    if len(feedback) > REPRO_REMINDER_CAP:
        return [
            f"Reproduction: {len(feedback)} tracked files changed. Run "
            "`superra repro status .` to see the steps they stale."
        ]
    return feedback


def _clear_repro_markers(project_root: Path, resolved_paths: set[str]) -> None:
    """Remove reminder markers for resolved_paths, across every session key."""
    base = project_root / REPRO_STATE_DIRNAME / REPRO_MARKER_SUBDIR
    if not base.is_dir():
        return
    digests = {
        hashlib.sha256(p.encode("utf-8")).hexdigest()[:32] for p in resolved_paths
    }
    try:
        session_dirs = [d for d in base.iterdir() if d.is_dir()]
    except OSError:
        return
    for session_dir in session_dirs:
        for digest in digests:
            marker = session_dir / digest
            if marker.exists():
                try:
                    marker.unlink()
                except OSError:
                    pass


def _clear_reproduction_markers_for_task(plan_root: Path, task_path: str) -> None:
    """Clear reminder markers for files this task's `## Reproduction` section names.

    Runs only when the just-edited task currently declares the section, so an
    ordinary task.md edit costs nothing extra. It builds the graph the same way
    as `_reproduction_reminder` (`_hook_graph`), so clearing looks up the
    identical resolved path a reminder marked.
    Best-effort: any problem reading the task or building the graph is
    silence, never a block.
    """
    task_dir = plan_root if task_path == "" else plan_root / task_path
    try:
        text = (task_dir / "task.md").read_text(encoding="utf-8")
    except OSError:
        return

    _ensure_scripts_on_path()
    try:
        import _task_io as task_io
        import _repro
        _, body = task_io.parse_frontmatter(text)
        if _repro.REPRO_SECTION not in task_io.parse_body_sections(body):
            return
        graph = _hook_graph(plan_root)
    except Exception:
        return

    resolved_paths = {
        dep.resolved for step in graph.steps_for(task_path) for dep in step.deps
    }
    if not resolved_paths:
        return
    _clear_repro_markers(plan_root.parent, resolved_paths)


def _implemented_coverage_reminder(plan_root: Path, task_path: str) -> list[str]:
    """Remind once per transition when a leaf reaches `implemented` carrying
    results files the reproduction graph does not cover.

    The marker key is the task, not the session, so the reminder follows the
    status transition: it is cleared whenever the task is not `implemented`,
    and set once a reminder is emitted. A task that leaves `implemented` and
    returns reminds again. Cheap gates (status, leaf, a linked results file)
    run before any graph build, so an ordinary task.md edit costs a parse.
    Best-effort: any failure is silence.
    """
    project_root = plan_root.parent
    marker = _repro_marker_path(
        project_root, IMPLEMENTED_MARKER_KEY, f"implemented:{task_path}"
    )
    task_md = (plan_root if task_path == "" else plan_root / task_path) / "task.md"
    _ensure_scripts_on_path()
    try:
        import _task_io as task_io
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # parse_task warns on a bad status
            task = task_io.parse_task(task_md, plan_root)
        is_leaf = not any(task_io.iter_child_task_dirs(task_md.parent))
        if task.status != "implemented" or not is_leaf:
            if marker.exists():
                marker.unlink()
            return []
        if marker.exists() or "](" not in task.results:
            return []
        import _repro
        import _repro_signals
        graph = _hook_graph(plan_root)
        if not _repro_signals.has_reproduction(graph):
            return []
        files = _repro_signals.uncovered_results_files(graph, task, project_root)
    except Exception:
        return []
    if not files:
        return []
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    except OSError:
        pass
    return [
        f"Reproduction: task {task_path or '(root)'} is implemented and its "
        f"## Results links {', '.join(files)}, which no step produces or reads. "
        "Register the producer step, or leave it if the file has none — "
        "`superRA:reproducibility` has the call."
    ]


def _feedback_json(feedback: list[str]) -> str:
    context = (
        "<IMPORTANT>Task-system hook feedback:\n"
        + "\n".join(f"- {line}" for line in feedback)
        + "\n\nThe hook stayed non-blocking; apply any relevant action before proceeding."
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


def _reconcile(
    plan_root: Path, task_path: str | None, scope: list[str] | None = None
) -> list[str]:
    """Validate and propagate parent status for a plan tree.

    Each step is best-effort in its own try/except so a failure in one never
    aborts the others or the process. When task_path is None (a structural move
    whose precise location is unknown), parent status is recomputed across the
    whole tree rather than along a single ancestor chain. `scope` (the edited
    task paths) limits the validation warnings to those tasks; None reports the
    whole tree. The dashboard is not
    regenerated here; it is produced only on explicit `superra dashboard export`.
    """
    global _RECONCILED
    _RECONCILED = True
    _ensure_scripts_on_path()
    import _task_io as task_io
    import _task_validate as task_validate
    feedback: list[str] = []

    # Propagate parent status first so validation below describes the state
    # this run produced, not the pre-rollup tree. Best-effort, never fail.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            propagation_warnings: list[str] = []
            if task_path is None:
                _propagate_whole_tree(task_io, plan_root, propagation_warnings)
            else:
                task_io.propagate_parent_status(
                    plan_root, task_path, feedback=propagation_warnings
                )
        for w in propagation_warnings:
            feedback.append(f"Status propagation warning in {plan_root}: {w}")
    except Exception as exc:
        feedback.append(f"Status propagation failed for {plan_root} (non-fatal): {exc}")

    # Validate — collect warnings for model-visible JSON feedback.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            validation_warnings = task_validate.validate_plan(plan_root)
            from _repro import build_graph
            graph = build_graph(plan_root, resolve_vars=False)
            findings = [f for f in graph.findings
                        if f.severity == "error" or f.category == "dependency"]
            if scope is not None:
                # validate_plan prefixes each warning `<task path>:`, `(root):` for the root.
                wanted = {path or "(root)" for path in scope}
                validation_warnings = [w for w in validation_warnings
                                       if w.split(": ", 1)[0] in wanted]
                findings = [f for f in findings if f.task_path in scope]
            validation_warnings.extend(f.to_text() for f in findings)
        if validation_warnings:
            for w in validation_warnings:
                feedback.append(f"Validation warning in {plan_root}: {w}")
    except Exception as exc:
        feedback.append(f"Validation failed for {plan_root}: {exc}")

    return feedback


def _propagate_whole_tree(
    task_io, plan_root: Path, feedback: list[str] | None = None
) -> int:
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
    seen_warnings: set[str] = set()
    for leaf_path in leaf_paths:
        leaf_warnings: list[str] = []
        updated += task_io.propagate_parent_status(
            plan_root, leaf_path, feedback=leaf_warnings
        )
        for w in leaf_warnings:
            # Ancestor chains overlap across leaves; report each warning once.
            if feedback is not None and w not in seen_warnings:
                seen_warnings.add(w)
                feedback.append(w)
    return updated


# Filesystem-mutating verbs that can restructure a task tree.
_MUTATING_RE = re.compile(
    r"(?:^|[\s;&|(])(?:git\s+mv|mv|rm|rmdir|cp|mkdir)(?:\s|$)"
)
# Path-like tokens that mention a task-root directory.
_PLAN_TOKEN_RE = re.compile(
    r"(?:^|[\s'\"=])((?:[^\s'\"=]*/)?(?:superRA(?=$|/|[\s'\";|&])(?:/[^\s'\";|&]*)?|\.plan[^\s'\";|&]*))"
)


def _command_mentions_task_root(command: str) -> bool:
    return _PLAN_TOKEN_RE.search(command) is not None


# A bare `mv`/`git mv SRC DST` with exactly two task-root path operands — the
# shape of a directory rename. Flags and extra operands fall through to the
# generic reconcile path (no auto-cascade) rather than being mis-parsed.
_MV_RE = re.compile(r"(?:^|[\s;&|(])(?:git\s+mv|mv)(\s+.*)$")


def _detect_same_parent_rename(
    command: str,
    cwd: Path,
    task_io,
) -> tuple[Path, str, str] | None:
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
    plan_root = task_io._find_plan_root(parent)
    if (
        plan_root is None
        or task_io.is_opaque_task_path(parent, plan_root)
        or task_io.has_symlink_task_component(parent, plan_root)
    ):
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


def _bash_structural_feedback(data: dict) -> list[str]:
    """Reconcile any task tree touched by a structural Bash command."""
    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command:
        return []

    # Gate: must reference a task root AND contain a mutating verb. A read-only
    # command that merely mentions a task root (task_query.py, grep, serve) is
    # not a structural change and must early-exit.
    if not _command_mentions_task_root(command):
        return []
    if not _MUTATING_RE.search(command):
        return []

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
    rename = _detect_same_parent_rename(command, cwd, task_io)
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
                task_io.apply_move_link_rewrites(link_root, link_rewrites)
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

    return feedback


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
    if (
        plan_root is None
        or task_io.is_opaque_task_path(file_path.parent, plan_root)
        or task_io.has_symlink_task_component(file_path.parent, plan_root)
    ):
        return None

    task_path = str(file_path.parent.relative_to(plan_root))
    if task_path == ".":
        task_path = ""
    return plan_root, task_path


def _apply_patch_paths(command: str) -> list[str]:
    """Extract file paths from an apply_patch command payload."""
    _ensure_scripts_on_path()
    from _apply_patch import patch_paths

    return patch_paths(command)


def _cwd(data: dict) -> Path:
    cwd = data.get("cwd")
    return Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()


def _tool_paths(data: dict, tool_name: str) -> list[Path]:
    """Files the tool call itself names as edited."""
    tool_input = data.get("tool_input", {}) or {}
    if tool_name in ("Edit", "Write"):
        raw_paths = [tool_input.get("file_path", "")]
    elif tool_name == "apply_patch":
        command = tool_input.get("command", "") or ""
        raw_paths = _apply_patch_paths(command) if command else []
    else:
        raw_paths = []
    cwd = _cwd(data)
    paths: list[Path] = []
    for raw in raw_paths:
        if not isinstance(raw, str) or not raw:
            continue
        path = Path(raw)
        paths.append(path if path.is_absolute() else cwd / path)
    return paths


def _repro_watch(plan_root: Path) -> tuple[list[str], list[list]]:
    """What the baseline watches beyond the task root: (files, dirs).

    `files` are the literal-path deps and scripts of registered steps, minus step
    outs. `dirs` are `[directory, suffixes | None]` scanned on every call: each
    declared directory dependency (every file) and each script's directory (new
    scripts of a configured runner's language), skipping the task root.
    """
    import _edit_detect
    project_root = plan_root.parent
    graph = _hook_graph(plan_root)
    suffixes = _edit_detect.runner_suffixes(graph.config.runners)
    files: list[str] = []
    dirs: dict[str, list[str] | None] = {}
    for step in graph.steps:
        for dep in step.deps:
            if "${" in dep.resolved or _repro_is_out(graph, dep.resolved):
                continue
            path = project_root / dep.resolved
            if path.is_dir():
                dirs[str(path)] = None
            elif path.is_file():
                files.append(str(path))
                parent = path.parent
                if (suffixes and path.suffix.lower() in suffixes
                        and plan_root != parent and plan_root not in parent.parents):
                    dirs.setdefault(str(parent), suffixes)
    return files, [[path, suffix] for path, suffix in dirs.items()]


def _detected_paths(data: dict, tool_name: str, tool_paths: list[Path]) -> list[Path]:
    """Watched files changed on disk since this session's baseline. Fails open."""
    try:
        _ensure_scripts_on_path()
        import _checkout_scope
        import _edit_detect
        tool_input = data.get("tool_input", {}) or {}
        command = tool_input.get("command", "") if tool_name == "Bash" else ""
        session_key = _repro_session_key(data)
        # The session anchor, not the payload cwd: a `cd` into another checkout
        # must not make that checkout the session's own. Same resolution the
        # `guard-foreign-checkout` gate uses.
        anchor = _checkout_scope.session_anchor(data)
        if anchor is None:
            return []
        changed: list[Path] = []
        watch: dict[Path, tuple] = {}

        def watched(root: Path) -> tuple:
            if root not in watch:
                watch[root] = _repro_watch(root)
            return watch[root]

        for plan_root in _edit_detect.plan_roots(
            anchor, tool_paths, command if isinstance(command, str) else ""
        ):
            try:
                changed.extend(
                    _edit_detect.detect(
                        plan_root,
                        session_key,
                        lambda root=plan_root: watched(root)[0],
                        lambda root=plan_root: watched(root)[1],
                        _CREATED,
                    )
                )
            except Exception:
                continue
        return changed
    except Exception:
        return []


def _process_paths(data: dict, file_paths: list[Path]) -> list[str]:
    """Run every edit consumer over the changed files, whichever tool wrote them.

    The task.md-only reconcile (validate + status propagation), the communicate
    reminder and render-integrity check for any .md under a task root, and the
    reproduction reminder — not gated to markdown or the task root, since a
    producer script usually lives beside the task tree, not inside it.
    """
    feedback: list[str] = list(_communicate_reminder(file_paths))
    integrity: list[str] = []
    task_edits: dict[Path, tuple[Path, list[str]]] = {}

    for file_path in file_paths:
        integrity.extend(_markdown_integrity_feedback(file_path))
        match = _task_path_from_file_path(file_path)
        if match is None:
            continue
        plan_root, task_path = match
        task_edits.setdefault(plan_root.resolve(), (plan_root, []))[1].append(task_path)

    for plan_root, task_paths in task_edits.values():
        # One edited task reconciles along its ancestor chain; several recompute
        # the whole tree once.
        feedback.extend(
            _reconcile(
                plan_root,
                task_path=task_paths[0] if len(task_paths) == 1 else None,
                scope=task_paths,
            )
        )
        for task_path in task_paths:
            _clear_reproduction_markers_for_task(plan_root, task_path)
            feedback.extend(_implemented_coverage_reminder(plan_root, task_path))

    feedback.extend(integrity)
    feedback.extend(_reproduction_reminder(data, file_paths))
    return feedback


def _unique_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        try:
            key = path.resolve()
        except OSError:
            key = path
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def main() -> None:
    global _CODEX_EMPTY_JSON_MODE

    # Read tool call info from stdin (Claude Code PostToolUse protocol)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name = data.get("tool_name", "") or data.get("tool", "")
    if data.get("hook_event_name") == "UserPromptSubmit":
        # Seed the session's edit baseline so the first tool call is compared
        # against it; never reports.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _detected_paths(data, "", [])
        _exit_success()
    _CODEX_EMPTY_JSON_MODE = (
        _truthy_env(CODEX_EMPTY_JSON_ENV)
        or tool_name == "apply_patch"
    )

    if tool_name not in ("Bash", "apply_patch", "Edit", "Write"):
        _exit_success()

    feedback: list[str] = []
    tool_paths = _tool_paths(data, tool_name)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # parse_task warns on a bad status
        # Detect before any reconcile runs, so only the tool call's own writes
        # are reported.
        changed = _unique_paths(
            tool_paths + _detected_paths(data, tool_name, tool_paths)
        )
        if tool_name == "Bash":
            feedback.extend(_bash_structural_feedback(data))
        feedback.extend(_process_paths(data, changed))
        if _RECONCILED:
            # Reconcile rewrites ancestor statuses; absorb the hook's own writes
            # so the next call does not report them as an edit.
            _detected_paths(data, tool_name, tool_paths)

    _exit_success(list(dict.fromkeys(feedback)))


if __name__ == "__main__":
    main()
