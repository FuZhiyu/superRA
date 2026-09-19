#!/usr/bin/env python3
"""Read-only diagnostic tool for task tree integrity.

Checks:
1. Status validity — all status values in valid enum, no approved task retains
   blocking review findings, flags stale review_status / integration_status fields.
2. Dependency integrity — all depends_on resolve to existing siblings,
   no cycles, flags dependencies on archived tasks.
3. Rollup consistency — stored parent status matches compute_status()
   from children.
4. Sync-impact leak — advisory warning for any task still carrying a
   temporary ## Sync Impact section past Integrate closeout.
5. Reproduction — the ## Reproduction section and config.yaml build-graph
   contract (schema errors, duplicate outs, unknown ${VAR} refs); see
   _repro.check_reproduction. Never-built steps are runner state, not a
   finding, so a fresh clone still checks clean.

Exit code 0 if clean, 1 if issues found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _repro import build_graph
from _task_io import (
    TASK_ROOT_DIRNAME,
    VALID_STATUSES,
    Task,
    compute_status,
    parse_frontmatter,
    resolve_plan_root_arg,
    walk_plan,
)
from _task_validate import (
    Finding,
    invalid_status_message,
    validate_review_notes,
)


# ---------------------------------------------------------------------------
# Check 1: Status validity
# ---------------------------------------------------------------------------

def check_status_validity(root: Task, plan_root: Path) -> list[Finding]:
    """Check all tasks have valid status values and no stale fields."""
    findings: list[Finding] = []
    _check_status_recursive(root, plan_root, findings)
    return findings


def _check_status_recursive(
    task: Task, plan_root: Path, findings: list[Finding]
) -> None:
    # Check the status value itself
    if task.status not in VALID_STATUSES:
        findings.append(Finding(
            task_path=task.path,
            category="status",
            severity="error",
            message=invalid_status_message(task.status),
        ))

    for message in validate_review_notes(task):
        findings.append(Finding(
            task_path=task.path,
            category="status",
            severity="error",
            message=message,
        ))

    # Check for stale review_status / integration_status in raw frontmatter
    task_md = task.dir_path / "task.md"
    if task_md.exists():
        text = task_md.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        stale_fields = {"review_status", "integration_status"}
        for field_name in sorted(stale_fields & fm.keys()):
            value = fm[field_name]
            if value and value != "~":
                findings.append(Finding(
                    task_path=task.path,
                    category="status",
                    severity="warning",
                    message=(
                        f"stale field '{field_name}' still present "
                        f"with value {value!r}; should be removed"
                    ),
                ))
            else:
                findings.append(Finding(
                    task_path=task.path,
                    category="status",
                    severity="warning",
                    message=(
                        f"stale field '{field_name}' still present "
                        f"in frontmatter (value: {value!r}); should be removed"
                    ),
                ))

    for child in task.children:
        _check_status_recursive(child, plan_root, findings)


# ---------------------------------------------------------------------------
# Check 2: Dependency integrity
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Check 3: Rollup consistency
# ---------------------------------------------------------------------------

def check_rollup_consistency(root: Task) -> list[Finding]:
    """Check that stored parent status matches computed rollup."""
    findings: list[Finding] = []
    _check_rollup_recursive(root, findings)
    return findings


def _check_rollup_recursive(task: Task, findings: list[Finding]) -> None:
    if not task.children:
        return

    computed = compute_status(task)
    stored = task.status

    if stored != computed:
        findings.append(Finding(
            task_path=task.path,
            category="rollup",
            severity="warning",
            message=(
                f"stored status is '{stored}' but computed rollup "
                f"from children is '{computed}'"
            ),
        ))

    for child in task.children:
        _check_rollup_recursive(child, findings)


# ---------------------------------------------------------------------------
# Check 4: Lingering ## Sync Impact (advisory)
# ---------------------------------------------------------------------------

# Matches the canonical ``## Sync Impact`` heading (owned by
# semantic-merge/references/workflow-sync-author.md) as a standalone heading line,
# tolerating trailing whitespace but no other variation, so the leak-detector
# neither misses the canonical form nor over-matches near-misses.
_SYNC_IMPACT_HEADING = re.compile(r"^##\s+Sync Impact\s*$", re.MULTILINE)


def check_sync_impact(root: Task) -> list[Finding]:
    """Flag any task carrying a temporary ``## Sync Impact`` section.

    ``## Sync Impact`` is scaffolding the sync author adds during Integrate and
    must remove at Integrate closeout (or fold a lasting assumption into
    ``## Objective``). A surviving section is a leak. All findings are advisory
    ``warning`` severity — a ``## Sync Impact`` section is legitimate mid-Integrate,
    so this is a leak-detector, never a hard gate, and the check never mutates.
    """
    findings: list[Finding] = []
    _check_sync_impact_recursive(root, findings)
    return findings


def _check_sync_impact_recursive(task: Task, findings: list[Finding]) -> None:
    task_md = task.dir_path / "task.md"
    if task_md.exists():
        text = task_md.read_text(encoding="utf-8")
        if _SYNC_IMPACT_HEADING.search(text):
            findings.append(Finding(
                task_path=task.path,
                category="sync-impact",
                severity="warning",
                message=(
                    "carries a temporary '## Sync Impact' section; remove it at "
                    "Integrate closeout, or fold any lasting task assumption into "
                    "'## Objective' and drop the section"
                ),
            ))

    for child in task.children:
        _check_sync_impact_recursive(child, findings)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnostic tool for task tree integrity (read-only)."
    )
    parser.add_argument(
        "--plan-root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output findings as JSON",
    )
    parser.add_argument(
        "--category",
        choices=["status", "dependency", "rollup", "sync-impact", "reproduction"],
        help="Only run a specific check category",
    )
    return parser.parse_args(argv)


def run_checks(
    plan_root: Path,
    category: str | None = None,
) -> list[Finding]:
    """Run all (or filtered) checks and return findings."""
    root = walk_plan(plan_root)
    findings: list[Finding] = []

    if category is None or category == "status":
        findings.extend(check_status_validity(root, plan_root))

    if category is None or category == "rollup":
        findings.extend(check_rollup_consistency(root))
    if category is None or category == "sync-impact":
        findings.extend(check_sync_impact(root))
    if category is None or category in {"dependency", "reproduction"}:
        findings.extend(build_graph(plan_root, root=root).findings)

    return findings


def format_text(findings: list[Finding]) -> str:
    """Format findings as human-readable text."""
    if not findings:
        return "All checks passed. No issues found."

    lines: list[str] = []
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines.append(f"Found {len(findings)} issue(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    lines.append("")

    for finding in findings:
        lines.append(finding.to_text())

    return "\n".join(lines)


def format_json(findings: list[Finding]) -> str:
    """Format findings as JSON."""
    return json.dumps(
        {
            "ok": len(findings) == 0,
            "total": len(findings),
            "errors": sum(1 for f in findings if f.severity == "error"),
            "warnings": sum(1 for f in findings if f.severity == "warning"),
            "findings": [f.to_dict() for f in findings],
        },
        indent=2,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)

    if not plan_root.exists():
        print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)

    findings = run_checks(plan_root, category=args.category)

    if args.as_json:
        print(format_json(findings))
    else:
        print(format_text(findings))

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
