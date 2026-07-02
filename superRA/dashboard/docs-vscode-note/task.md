---
title: "Quickstart Note: Dashboard VS Code Deep Links (Optional)"
status: approved
depends_on:
  - worktree-open-button
---

## Objective

Add a short note to the **Prerequisite** section of the quickstart (`docs/site/02-quickstart/task.md`, the `### Prerequisite` block ~line 13-21) that the dashboard supports VS Code deep links — clicking a task can open its `task.md`, and (per task `01`) open the task's worktree — if the researcher uses VS Code, framed as a convenience that is **not required**.

**Constraints:**

- Keep it to one or two sentences. This is an adopter-facing convenience note, not a mechanics explanation — describe what the researcher gets, not how the deep link is wired (no `vscode://`, no `RESOLVED_ROOT`, no internal function names).
- Fit the existing prose voice; no AI-flavored phrasing. Load the `writing` skill (Polish mode) before drafting.
- Since it is optional, phrase it as such (like the existing "recommended but not required" branch-and-PR line).
- Verify the docs site still builds/renders (this page is itself a doc-mode task-tree page).

## Planner Guidance

Natural home is right after the git/worktree prerequisite discussion or near the existing `uv` / dashboard line (line 21), since VS Code deep links are a dashboard convenience. Depends on `01` so the note can accurately describe the worktree-open capability.

## Results

Added a two-sentence optional note to the quickstart Prerequisite section, immediately after the `uv` / dashboard line ([docs/site/02-quickstart/task.md:23](../../../docs/site/02-quickstart/task.md#L23)):

> If you use VS Code, the dashboard doubles as a launcher: clicking a task opens its `task.md`, and a header button opens the active worktree in a VS Code window. Convenient, but not required.

- Describes both capabilities the researcher gets (task-file open + worktree open per task `01`), no wiring mechanics (`vscode://`, `RESOLVED_ROOT`, function names all avoided).
- Optional framing (`Convenient, but not required.`) mirrors the existing `recommended but not required` branch-and-PR line; fits the direct second-person voice of the surrounding prose.
- **Verification.** Markdown check clean (`check_markdown.py`). Doc-mode static build succeeds (`plan_dashboard.py generate --plan-root docs/site --doc-mode`) and the rendered page contains the new note.
