#!/usr/bin/env python3
"""Append findings, figures, or notes to a task's ## Results section."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import parse_task, write_task


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add results to a task.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
    parser.add_argument("--path", required=True, help="Task path relative to plan root")
    parser.add_argument("--finding", help="Key finding to append")
    parser.add_argument("--figure", help="Figure path (relative to task attachments/)")
    parser.add_argument("--figure-caption", default="", help="Caption for the figure")
    parser.add_argument("--note", help="Note to append")
    return parser.parse_args(argv)


def _ensure_section(body: str, section: str) -> tuple[str, int]:
    """Ensure a ## section exists in the body. Returns (body, insert_position)."""
    marker = f"## {section}"
    if marker in body:
        idx = body.index(marker)
        after_header = body.index("\n", idx) + 1
        return body, after_header

    if body and not body.endswith("\n"):
        body += "\n"
    insert_pos = len(body)
    body += f"\n{marker}\n\n"
    return body, len(body)


def add_result(
    plan_root: Path,
    task_path: str,
    finding: str | None = None,
    figure: str | None = None,
    figure_caption: str = "",
    note: str | None = None,
) -> None:
    task_md = plan_root / task_path / "task.md"
    if not task_md.exists():
        print(f"Error: task not found: {task_md}", file=sys.stderr)
        sys.exit(1)

    task = parse_task(task_md)
    body = task.body

    if finding:
        body, pos = _ensure_section(body, "Results")
        subsection = "### Key Findings\n"
        if subsection not in body:
            body = body[:pos] + f"\n{subsection}\n" + body[pos:]
            pos = body.index(subsection) + len(subsection) + 1

        findings_end = pos
        lines = body[pos:].split("\n")
        last_bullet = pos  # track the position just after the last `- ` line
        for i, line in enumerate(lines):
            if line.startswith("## ") or line.startswith("### "):
                break
            line_end = pos + sum(len(l) + 1 for l in lines[: i + 1])
            if line.startswith("- "):
                last_bullet = line_end
            elif line.strip() == "" and last_bullet > pos:
                # blank line after bullet list — stop here
                break
        findings_end = last_bullet

        body = body[:findings_end] + f"- {finding}\n" + body[findings_end:]

    if figure:
        body, pos = _ensure_section(body, "Results")
        caption = figure_caption or figure
        body = body[:pos] + f"\n![{caption}]({figure})\n" + body[pos:]

    if note:
        body, pos = _ensure_section(body, "Results")
        subsection = "### Notes\n"
        if subsection not in body:
            body += f"\n{subsection}\n"
        notes_idx = body.index(subsection) + len(subsection)
        next_section = body.find("\n##", notes_idx)
        if next_section == -1:
            next_section = len(body)
        body = body[:next_section] + f"- {note}\n" + body[next_section:]

    task.body = body
    write_task(task)
    print(f"Updated results in {task_md}")
    try:
        from plan_dashboard import generate_dashboard
        generate_dashboard(plan_root)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    add_result(
        plan_root=Path(args.plan_root),
        task_path=args.path,
        finding=args.finding,
        figure=args.figure,
        figure_caption=args.figure_caption,
        note=args.note,
    )


if __name__ == "__main__":
    main()
