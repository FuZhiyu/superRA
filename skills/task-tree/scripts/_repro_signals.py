"""Advisory reproduction signals: staleness fan-out and unregistered results.

Every function here reads the graph and the task tree; none of them hashes a
file, resolves a ``${VAR}``, or runs a subprocess, so the reminder hook can
call them on the edit hot path. All signals are advisory: a retained file
legitimately has no producer step (a hand-edited ``.tex``, a boundary input),
so every rule here is written to stay silent when in doubt.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from _task_io import _MARKDOWN_LINK_RE, Task
from _task_validate import Finding

CATEGORY = "reproduction"

# What a generated result looks like: data tables and exhibits. Prose and
# source extensions stay out, so a linked `.md`, `.jl`, or `.py` never warns.
GENERATED_SUFFIXES = {
    ".arrow", ".csv", ".dta", ".feather", ".jld2", ".parquet", ".rds", ".tsv",
    ".eps", ".jpeg", ".jpg", ".pdf", ".png", ".svg",
}
# A `.tex` is a table only when it sits in a directory some step already
# writes into; a manuscript `.tex` next to the prose never warns.
OUTPUT_ROOT_SUFFIXES = {".tex"}
# Path segments that mark throwaway work, wherever they appear.
SCRATCH_SEGMENTS = {"cache", "node_modules", "sandbox", "scratch", "temp", "tmp"}

_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_INLINE_CODE_RE = re.compile(r"(`+).*?\1")


# ---------------------------------------------------------------------------
# Staleness fan-out
# ---------------------------------------------------------------------------

def downstream_steps(graph, owners: list[str]) -> list[str]:
    """The steps an edit to `owners` stales: the owners plus their consumers."""
    consumers: dict[str, set[str]] = {}
    for src, dst, _ in graph.step_edges:
        consumers.setdefault(src, set()).add(dst)
    seen = set(owners)
    queue = list(owners)
    while queue:
        for consumer in consumers.get(queue.pop(), ()):
            if consumer not in seen:
                seen.add(consumer)
                queue.append(consumer)
    return sorted(owners) + sorted(seen - set(owners))


def step_durations(project_root: Path, names: list[str]) -> dict[str, float | None]:
    """Each step's last recorded run duration, or None when it never ran."""
    try:
        from _repro_state import read_run_record, runner_paths
    except Exception:
        return {name: None for name in names}
    paths = runner_paths(Path(project_root))
    durations: dict[str, float | None] = {}
    for name in names:
        record = read_run_record(paths, name)
        value = record.get("duration")
        durations[name] = value if isinstance(value, (int, float)) else None
    return durations


def format_fan_out(names: list[str], durations: dict[str, float | None]) -> str:
    """`a (12.4s), b (no recorded duration)` — the rerun cost the edit implies."""
    parts = []
    for name in names:
        seconds = durations.get(name)
        parts.append(
            f"{name} ({seconds:.1f}s)" if seconds else f"{name} (no recorded duration)"
        )
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Results artifacts with no registered producer
# ---------------------------------------------------------------------------

def _literal_tail(declared: str) -> str:
    """The segments after the last `${VAR}` one — `${OUT}/fig/a.png` -> `fig/a.png`."""
    segments = declared.split("/")
    last_var = max((i for i, s in enumerate(segments) if "${" in s), default=-1)
    return "/".join(segments[last_var + 1:])


def _matches(candidate: str, declared: str) -> bool:
    """Does `candidate` name `declared`, or a file inside it?

    A declared path still carrying a `${VAR}` is compared on its literal tail,
    found as a run of whole segments anywhere in the candidate, so a
    variable-rooted directory covers the files under it
    (`${OUT}/estimates` covers `output/estimates/a.csv`). A declaration that is
    nothing but a variable (`${OUT}`) has no tail and covers everything.
    Matching a tail can only suppress a warning — an unresolved variable must
    never make a registered out look unregistered.
    """
    if "${" in declared:
        needle = [s for s in _literal_tail(declared).split("/") if s]
        if not needle:
            return True
        segments = candidate.split("/")
        return any(
            segments[i:i + len(needle)] == needle
            for i in range(len(segments) - len(needle) + 1)
        )
    return candidate == declared or candidate.startswith(declared + "/")


def _declared_paths(graph) -> tuple[list[str], list[str]]:
    """(every out, every dep) an active step declares, as resolved paths."""
    outs = [out.path.resolved for step in graph.steps for out in step.outs]
    deps = [dep.resolved for step in graph.steps for dep in step.deps]
    return outs, deps


def _output_dirs(outs: list[str]) -> list[str]:
    """The directories registered outs are written into."""
    dirs = set()
    for out in outs:
        dirs.add(posixpath.dirname(out) if posixpath.splitext(out)[1] else out)
    return sorted(d for d in dirs if d)


def _is_scratch(rel: str) -> bool:
    return any(
        segment.lower() in SCRATCH_SEGMENTS or segment.startswith(".")
        for segment in rel.split("/")
    )


def iter_links(text: str):
    """Link targets in Markdown `text`, skipping fenced and inline code."""
    fence = None
    for line in text.splitlines():
        marker = _FENCE_RE.match(line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        for match in _MARKDOWN_LINK_RE.finditer(_INLINE_CODE_RE.sub("", line)):
            yield match.group(2).strip("<>")


def uncovered_results_files(graph, task: Task, project_root: Path) -> list[str]:
    """Generated-looking files a task's `## Results` links that no step covers.

    Covered means some active step declares the file as an out (directly or
    inside a directory out) or reads it as a dep, boundary input included. A
    file that is not on disk is left to the link checkers.
    """
    if not task.results.strip():
        return []
    outs, deps = _declared_paths(graph)
    output_dirs = _output_dirs(outs)
    root = Path(project_root).resolve()
    found: list[str] = []
    for target in iter_links(task.results):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        try:
            absolute = (task.dir_path / unquote(parsed.path)).resolve()
            rel = absolute.relative_to(root).as_posix()
        except (OSError, ValueError):
            continue
        suffix = posixpath.splitext(rel)[1].lower()
        if suffix in OUTPUT_ROOT_SUFFIXES:
            parent = posixpath.dirname(rel)
            if not any(_matches(parent, d) for d in output_dirs):
                continue
        elif suffix not in GENERATED_SUFFIXES:
            continue
        if _is_scratch(rel) or rel in found or not absolute.is_file():
            continue
        if any(_matches(rel, d) for d in (*outs, *deps)):
            continue
        found.append(rel)
    return found


def has_reproduction(graph) -> bool:
    """Does this tree configure reproduction at all? Nothing warns when it does not."""
    return bool(
        graph.steps or graph.section_tasks or any(graph.config.to_dict().values())
    )


def check_results_coverage(graph, root: Task, project_root: Path) -> list[Finding]:
    """One `reproduction` warning per results file with no registered producer."""
    if not has_reproduction(graph):
        return []
    from _task_dependencies import archived_paths

    archived = archived_paths(root)
    findings: list[Finding] = []
    pending = [root]
    while pending:
        task = pending.pop()
        pending.extend(task.children)
        if task.path in archived:
            continue
        for rel in uncovered_results_files(graph, task, project_root):
            findings.append(Finding(
                task_path=task.path,
                category=CATEGORY,
                severity="warning",
                message=(
                    f"## Results links {rel}, which no active step declares as an out "
                    f"and no step reads; register its producer step, or leave it if the "
                    f"file has none"
                ),
            ))
    return findings
