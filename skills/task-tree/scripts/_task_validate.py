#!/usr/bin/env python3
"""Validation suite for the task-tree skill.

Owns every task-tree validity rule and its message text. ``parse_task``'s
lenient warning and ``task_check``'s strict findings both consume
``invalid_status_message`` so the status-validity rule has exactly one
message source.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from _task_io import (
    VALID_STATUSES,
    Task,
    _has_nonempty_section,
    iter_child_task_dirs,
    parse_body_sections,
    parse_frontmatter,
    parse_task,
)


# Default agent-facing output lists at most this many findings per group; the
# rest collapse to a count and the command that lists them, so output size
# stays fixed however messy the tree.
OUTPUT_CAP = 10


@dataclass
class Finding:
    """A single diagnostic finding.

    Lives here rather than in ``task_check`` so every validator that reports
    severities — ``task_check``'s own checks and ``_repro``'s reproduction
    checks — emits one shape without importing the CLI module.
    """

    task_path: str
    category: str  # "status" | "dependency" | "rollup" | "sync-impact" | "reproduction"
    severity: str  # "error" | "warning"
    message: str

    def to_text(self) -> str:
        prefix = self.task_path or "(root)"
        return f"[{self.severity.upper()}] [{self.category}] {prefix}: {self.message}"

    def to_dict(self) -> dict:
        return {
            "task_path": self.task_path,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
        }


def invalid_status_message(status: str) -> str:
    """The single message source for the status-validity rule."""
    return f"invalid status {status!r}; expected one of {list(VALID_STATUSES)}"


def validate_frontmatter(task: Task) -> list[str]:
    """Validate frontmatter fields of a Task.

    Returns a list of warning strings for any violations.
    """
    warnings_out: list[str] = []

    if task.status not in VALID_STATUSES:
        warnings_out.append(invalid_status_message(task.status))
    if not isinstance(task.depends_on, list) or not all(
        isinstance(v, str) for v in task.depends_on
    ):
        warnings_out.append("depends_on must be a list of strings")
    if not task.title or not task.title.strip():
        warnings_out.append("title must be a non-empty string")

    return warnings_out


def validate_revision_notes(task: Task) -> list[str]:
    """Warn when a task past ``implemented`` still carries a ``## Revision Notes`` section.

    The implementer consumes and removes the note in the same commit that sets
    ``status: implemented`` (see ``implement-task`` SKILL.md Execution), whether
    or not review follows. A note is legitimate before that point —
    ``not-started``, ``in-progress``, or ``revise``, where a fresh note is the
    prescribed planner-to-implementer handoff. Detection is fence-aware so a
    header quoted inside a code block does not trigger it.
    """
    if task.status in ("not-started", "in-progress", "revise"):
        return []
    if not _has_nonempty_section(task.body, "Revision Notes"):
        return []
    return [
        f"{task.status} task still carries a ## Revision Notes section; "
        "the implementer should have removed it once implemented"
    ]


def approved_with_blocking_review_notes(text: str) -> bool:
    """Return whether task Markdown violates the approval-review invariant."""
    fm, body = parse_frontmatter(text)
    review_notes = parse_body_sections(body).get("Review Notes", "")
    return _review_notes_block_approval(
        str(fm.get("status", "not-started")), review_notes
    )


def _review_notes_block_approval(status: str, review_notes: str) -> bool:
    return status == "approved" and bool(
        re.search(r"\[BLOCKING\]", review_notes, re.IGNORECASE)
    )


def validate_review_notes(task: Task) -> list[str]:
    """Warn when an approved task retains blocking review findings."""
    if not _review_notes_block_approval(task.status, task.review_notes):
        return []
    return [
        "approved task still carries a [BLOCKING] item in ## Review Notes; "
        "run narrow re-review or keep the task in revision"
    ]


def validate_plan(plan_root: Path) -> list[str]:
    """Walk the entire plan tree and run all validations at each level.

    Returns aggregated list of warning strings, each prefixed with the task path.
    """
    warnings_out: list[str] = []

    def _validate_level(directory: Path) -> None:
        subdirs = iter_child_task_dirs(directory)

        tasks_at_level: list[Task] = []
        for subdir in subdirs:
            try:
                task = parse_task(subdir / "task.md", plan_root)
            except Exception as exc:
                warnings_out.append(f"{subdir.name}: parse error: {exc}")
                continue
            tasks_at_level.append(task)

        for task in tasks_at_level:
            prefix = task.path if task.path else task.slug

            for w in validate_frontmatter(task):
                warnings_out.append(f"{prefix}: {w}")

            for w in validate_revision_notes(task):
                warnings_out.append(f"{prefix}: {w}")

            for w in validate_review_notes(task):
                warnings_out.append(f"{prefix}: {w}")

        for subdir in subdirs:
            _validate_level(subdir)

    # Validate root task if present
    root_task_md = plan_root / "task.md"
    if root_task_md.exists():
        try:
            root_task = parse_task(root_task_md, plan_root)
            for w in validate_frontmatter(root_task):
                warnings_out.append(f"(root): {w}")
            for w in validate_revision_notes(root_task):
                warnings_out.append(f"(root): {w}")
            for w in validate_review_notes(root_task):
                warnings_out.append(f"(root): {w}")
        except Exception as exc:
            warnings_out.append(f"(root): parse error: {exc}")

    _validate_level(plan_root)
    return warnings_out
