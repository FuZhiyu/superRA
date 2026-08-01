---
title: "Conversation/Task-File Boundary"
status: not-started
depends_on: [writing-contract, review-policy]
---

## Objective

Define the orchestrator→researcher reporting contract: conversation carries deltas and pointers; task files remain the single home of recorded results.

- `main-agent.md` gains a reporting section: after work lands, tell the researcher what changed at a high level and point to the task file/dashboard; content already recorded in a task file is referenced, never reproduced in conversation.
- Extras path: information possibly relevant to the researcher that the agent chose not to record goes to conversation with an offer — add to `## Results` only if the researcher wants it.
- Replace the unbounded `<summarize the results>` placeholder in `superimplement` with the bounded pointer-first form; parent rollups link to child findings instead of restating their numbers.
- Validation: no surviving workflow instruction invites reproducing `## Results` content in conversation; the reporting contract appears once (`main-agent.md`) with pointers from `superimplement`/`agent-orchestration`.

## Planner Guidance

- The orchestrator→user leg is currently specified nowhere except the `<summarize the results>` placeholder — evidence and lines: [writing-surfaces map](../attachments/map-writing-surfaces.md) §5.
- The subagent→orchestrator boundary (status enum + SHA only) is the model to extend one hop; the dashboard URL retained at session start is the ready-made pointer.
- Matches the standing reporting model: commit = summary, return = status + SHA, files = state — this task adds the missing conversation = delta + pointer leg.

## Results
