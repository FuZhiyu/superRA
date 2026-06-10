---
title: "Assign revision notes cleanup to reviewer"
status: revise
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

**Changes to `skills/task-tree/references/planning.md`:**

5. **Root anatomy (line 73)** — change "Same cleanup lifecycle as review notes — cleaned out when the task is re-implemented and approved" to specify the reviewer as the agent who removes it.

6. **Field notes (line 129)** — same: make the reviewer ownership explicit.

**Not in scope:** Root task.md revision notes. Root tasks don't go through the implementer-reviewer loop, so their revision notes are orchestrator-managed. This is an acceptable edge — root revision notes are rare and the orchestrator can clean them when stale.

## Results

All six edits applied surgically to two files:

**`agents/reviewer.md` (4 edits):**

1. [reviewer.md:82](agents/reviewer.md#L82) — APPROVE verdict now includes "Remove `## Revision Notes` if present."
2. [reviewer.md:86](agents/reviewer.md#L86) — Re-review approval now removes both `## Review Notes` and `## Revision Notes`.
3. [reviewer.md:113](agents/reviewer.md#L113) — Added `## Revision Notes` section to ownership list with constraint: remove-only at APPROVE, content is planner-owned.
4. [reviewer.md:161](agents/reviewer.md#L161) — Added pre-commit self-check: "On APPROVE: I removed `## Revision Notes` if present."

**`skills/task-tree/references/planning.md` (2 edits):**

5. [planning.md:73](skills/task-tree/references/planning.md#L73) — Root anatomy: changed passive "cleaned out when re-implemented and approved" to "The reviewer removes this section when approving the task."
6. [planning.md:129](skills/task-tree/references/planning.md#L129) — Field notes: same change — made reviewer ownership explicit.

## Review Notes

1. **[MAJOR]** [task.md:25](task.md#L25), [task.md:44-47](task.md#L44) — Objective and Results prescribe and cite edits to `skills/task-tree/references/planning.md` (L73/L129), a file that no longer exists; the `## Revision Notes` lifecycle and reviewer-ownership rule now live in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) (Field-by-Field Notes) and [agents/reviewer.md](../../../agents/reviewer.md). The hard-coded reviewer.md line anchors (82/86/113/161) are likewise stale against the current 132-line file. An approved task whose Results point at a deleted file misleads anyone tracing this rule. Fix: replace the dead `planning.md` references with the current owners and drop or refresh the line anchors.
2. **[MINOR]** [task.md:39-47](task.md#L39) — citation links are repo-root-relative (`agents/reviewer.md`, `skills/...`); `report-in-markdown` resolves links relative to the markdown file's directory, so from this task every one needs a `../../../` prefix. Fix the prefixes when applying item 1.
