#!/usr/bin/env python3
"""Read-only diagnostic tool for task tree integrity.

Checks:
1. Status validity — all status values in valid enum, flags stale
   review_status / integration_status fields still in frontmatter.
2. Dependency integrity — all depends_on resolve to existing siblings,
   no cycles, flags dependencies on archived tasks.
3. Rollup consistency — stored parent status matches compute_status()
   from children.
4. Sync-impact leak — advisory warning for any task still carrying a
   temporary ## Sync Impact section past Integrate closeout.

Exit code 0 if clean, 1 if issues found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    VALID_STATUSES,
    Task,
    compute_status,
    parse_frontmatter,
    resolve_plan_root_arg,
    walk_plan,
)
from _task_validate import detect_cycles, invalid_status_message


# ---------------------------------------------------------------------------
# Finding data model
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """A single diagnostic finding."""

    task_path: str
    category: str  # "status" | "dependency" | "rollup" | "sync-impact"
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

def check_dependency_integrity(root: Task) -> list[Finding]:
    """Check dependency resolution, cycles, and archived dependencies."""
    findings: list[Finding] = []
    _check_deps_recursive(root, findings)
    return findings


def _check_deps_recursive(task: Task, findings: list[Finding]) -> None:
    if not task.children:
        return

    sibling_map = {c.slug: c for c in task.children}

    # Check each child's depends_on references
    for child in task.children:
        for dep in child.depends_on:
            if dep not in sibling_map:
                findings.append(Finding(
                    task_path=child.path,
                    category="dependency",
                    severity="error",
                    message=f"depends_on '{dep}' does not resolve to any sibling task",
                ))
            else:
                dep_task = sibling_map[dep]
                if dep_task.effective_status() == "archived":
                    findings.append(Finding(
                        task_path=child.path,
                        category="dependency",
                        severity="warning",
                        message=f"depends on archived task '{dep}'",
                    ))
                elif dep_task.effective_status() == "postponed":
                    findings.append(Finding(
                        task_path=child.path,
                        category="dependency",
                        severity="warning",
                        message=f"depends on postponed task '{dep}' (blocked until resumed)",
                    ))

    # Cycle detection at this sibling level
    cycle_warnings = detect_cycles(task.children)
    for warning in cycle_warnings:
        findings.append(Finding(
            task_path=task.path,
            category="dependency",
            severity="error",
            message=warning,
        ))

    # Recurse into children that have their own children
    for child in task.children:
        _check_deps_recursive(child, findings)


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
        choices=["status", "dependency", "rollup", "sync-impact"],
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
    if category is None or category == "dependency":
        findings.extend(check_dependency_integrity(root))
    if category is None or category == "rollup":
        findings.extend(check_rollup_consistency(root))
    if category is None or category == "sync-impact":
        findings.extend(check_sync_impact(root))

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
