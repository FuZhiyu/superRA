---
title: "Assign revision notes cleanup to reviewer"
status: implemented
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

The `## Revision Notes` lifecycle trigger is stated in `planning.md` (lines 73, 129): "cleaned out when the task is re-implemented and approved — same lifecycle as `## Review Notes`." But **no agent is explicitly told to do the cleanup.** `reviewer.md` never mentions `## Revision Notes`. This means revision notes accumulate on approved tasks.

Assign cleanup to the reviewer — the natural owner, since the reviewer already removes `## Review Notes` at approval time.

**Changes to `agents/reviewer.md`:**

1. **§Verdict APPROVE (line 82)** — currently: "No `[BLOCKING]` findings. No review notes needed; set `review_status: approved` in frontmatter." Add: remove `## Revision Notes` if present.

2. **§Verdict re-review (line 86)** — currently says "remove the `## Review Notes` section entirely." Extend to include `## Revision Notes`.

3. **§What You Own (lines 108-112)** — add `## Revision Notes` section removal at approval to the ownership list. Reviewer may NOT edit revision notes content (that's planner-owned) — only remove the entire section when approving.

4. **§Pre-Commit Self-Check (line 158 area)** — add a check: "On APPROVE: I removed `## Revision Notes` if present."

**Changes to `skills/task-tree/references/task-file-contract.md`** (the current owner of the `## Revision Notes` lifecycle; `planning.md` no longer exists):

5. **Field-by-Field Notes** — specify the reviewer as the agent who removes `## Revision Notes` at approval.

6. **Body Sections** — same: make reviewer ownership explicit.

**Not in scope:** Root task.md revision notes. Root tasks don't go through the implementer-reviewer loop, so their revision notes are orchestrator-managed. This is an acceptable edge — root revision notes are rare and the orchestrator can clean them when stale.

## Results

All six edits applied surgically to two files:

**`agents/reviewer.md` (4 edits):**

1. [reviewer.md:63](../../../agents/reviewer.md#L63) — APPROVE verdict now includes "Remove `## Revision Notes` if present."
2. [reviewer.md:70](../../../agents/reviewer.md#L70) — Pre-commit self-check: "I only edited ... and (at APPROVE) removed `## Revision Notes` of assigned tasks."
3. [reviewer.md:85](../../../agents/reviewer.md#L85) — Added `## Revision Notes` section to ownership list with constraint: remove-only at APPROVE, content is planner-owned.
4. [reviewer.md:111](../../../agents/reviewer.md#L111) — Re-review approval now removes both `## Review Notes` and `## Revision Notes`.

**`skills/task-tree/references/task-file-contract.md` (2 edits):**

5. [task-file-contract.md:13](../../../skills/task-tree/references/task-file-contract.md#L13) — Body Sections: specified reviewer removes `## Revision Notes` at approval.
6. [task-file-contract.md:25](../../../skills/task-tree/references/task-file-contract.md#L25) — Field-by-Field Notes: made reviewer ownership explicit with `validate_plan` warning note.

## Review Notes

1. **[MAJOR]** [task.md:25](task.md#L25), [task.md:44-47](task.md#L44) — Objective and Results prescribe and cite edits to `skills/task-tree/references/planning.md` (L73/L129), a file that no longer exists; the `## Revision Notes` lifecycle and reviewer-ownership rule now live in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) (Field-by-Field Notes) and [agents/reviewer.md](../../../agents/reviewer.md). The hard-coded reviewer.md line anchors (82/86/113/161) are likewise stale against the current 132-line file. An approved task whose Results point at a deleted file misleads anyone tracing this rule. Fix: replace the dead `planning.md` references with the current owners and drop or refresh the line anchors.
   → implemented: replaced `planning.md` references in Objective and Results with current owners (`task-file-contract.md` and `agents/reviewer.md`); refreshed line anchors to match live 132-line reviewer.md ([task.md](task.md))
2. **[MINOR]** [task.md:39-47](task.md#L39) — citation links are repo-root-relative (`agents/reviewer.md`, `skills/...`); `report-in-markdown` resolves links relative to the markdown file's directory, so from this task every one needs a `../../../` prefix. Fix the prefixes when applying item 1.
   → implemented: updated all citation links in Results to use `../../../` prefix ([task.md:39-47](task.md#L39))
