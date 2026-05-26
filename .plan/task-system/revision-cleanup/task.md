---
title: "Assign revision notes cleanup to reviewer"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

The `## Revision Notes` lifecycle trigger is stated in `planning.md` (lines 73, 129): "cleaned out when the task is re-implemented and approved — same lifecycle as `## Review Notes`." But **no agent is explicitly told to do the cleanup.** `reviewer.md` never mentions `## Revision Notes`. This means revision notes accumulate on approved tasks.

Assign cleanup to the reviewer — the natural owner, since the reviewer already removes `## Review Notes` at approval time.

**Changes to `agents/reviewer.md`:**

1. **§Verdict APPROVE (line 82)** — currently: "No `[BLOCKING]` findings. No review notes needed; set `review_status: approved` in frontmatter." Add: remove `## Revision Notes` if present.

2. **§Verdict re-review (line 86)** — currently says "remove the `## Review Notes` section entirely." Extend to include `## Revision Notes`.

3. **§What You Own (lines 108-112)** — add `## Revision Notes` section removal at approval to the ownership list. Reviewer may NOT edit revision notes content (that's planner-owned) — only remove the entire section when approving.

4. **§Pre-Commit Self-Check (line 158 area)** — add a check: "On APPROVE: I removed `## Revision Notes` if present."

**Changes to `skills/task-system/references/planning.md`:**

5. **Root anatomy (line 73)** — change "Same cleanup lifecycle as review notes — cleaned out when the task is re-implemented and approved" to specify the reviewer as the agent who removes it.

6. **Field notes (line 129)** — same: make the reviewer ownership explicit.

**Not in scope:** Root task.md revision notes. Root tasks don't go through the implementer-reviewer loop, so their revision notes are orchestrator-managed. This is an acceptable edge — root revision notes are rare and the orchestrator can clean them when stale.

## Results

