---
title: "Workflow Defaults: Interactive Main Agent, On-the-Fly Review"
status: not-started
depends_on: [role-skills, review-skill]
---

## Objective

Make interactive main-agent execution the default workflow and independent review an execution-time decision, re-scoping `superimplement` as the explicitly-entered autonomous mode.

- Interactive default: on a built tree the main agent executes tasks itself (the canvas loop) without loading `superimplement`. `superimplement` becomes the autonomous subagent workflow, loaded only when the researcher requests it or accepts the agent's recommendation — recommend with a one-line rationale when the frontier is broad, parallelizable, or context-heavy; never silently switch.
- Review is decided on the fly by whoever orchestrates, with researcher input — not scheduled at planning. After a task completes, judge from the result's stakes and plausibility (and any implementer concern return) whether an independent pass is worth it and at which tier/focuses; when the researcher is present, recommend and ask rather than dispatch. Planners may suggest a review in `## Planner Guidance`; the suggestion does not bind.
- Define the approval transition when no review runs — the orchestrating agent sets `approved` after its own verification — and update the status-ownership sentence in `task-file-contract.md`, the resume semantics in `main-agent.md` §Resuming Work (`implemented` no longer universally means "to review"), and every unconditional review step in `superimplement`.
- Record what review an approved task actually got. At APPROVE the reviewer's tier/focus header goes away with `## Review Notes`, so an approved task carries no record of the depth and focus it was reviewed under — or of whether an independent pass ran at all. Under triggered review that record is load-bearing for the next reader; give it a durable home (the approving agent's commit body is the cheapest candidate).
- The INTEGRATE boundary keeps one thorough review of accumulated work as the safety net.
- Re-scope or verify `hooks/ensure-agent-orchestration` — it gates the `agent-orchestration` load for `superimplement`, which misfires when the default path dispatches nothing.
- Task-sizing instruction fixes live in the `planning-sizing` sibling (different edit surface: superplan references).
- Update the statements the flip invalidates: the `CLAUDE.md` "Gates are local discipline … enforced" principle (gates still bind when a review runs), and execution-mode/implement descriptions in `CLAUDE.md`, `README.md`, and `docs/site`.
- Validation: a fresh-session trace on a small tree runs interactive with zero dispatches and zero `superimplement` loads; a broad-frontier trace produces a subagent-mode recommendation; a completed high-stakes task produces a review recommendation naming tier and focuses.

## Planner Guidance

- Motivation: subagent-heavy execution is slow and implements/reviews things the researcher never wanted; high human cadence catches misdirection early.
- Choreography map with the unconditional-review lines: [review-architecture map](../attachments/map-review-architecture.md) §2; scheduling options and evidence: [review-prompting research](../attachments/research-review-prompting.md) §C.
- Interactive mode's "ask before review: now / defer / skip" (`superplan/references/interactive-mode.md`) is the precedent; the canvas loop likely moves out of superplan's references to a home both PLAN and IMPLEMENT enter.
- Seat assignment in `agent-orchestration` stays useful for the autonomous mode — re-scope it, don't delete it.

## Results
