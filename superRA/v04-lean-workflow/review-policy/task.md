---
title: "Triggered Review Schedule"
status: not-started
depends_on: [role-skills, review-calibration]
---

## Objective

Replace the unconditional per-task implement→review→iterate loop with triggered review plus an INTEGRATE-boundary pass.

- Default per-task path is implementer self-check only; define who sets `approved` when no independent review runs (orchestrator/main-agent verification, with the status-ownership sentence in `task-file-contract.md` updated to match).
- Independent review fires on exactly three triggers: the researcher asks; the planner marked the task high-stakes at planning time; or the implementer returns with concerns/uncertainty — in which case the orchestrator recommends a review rather than silently dispatching one when the researcher is present.
- Define the planner's high-stakes mark (frontmatter is closed — use an objective line or body marker) and when planners should set it: result-bearing, irreversible, or downstream-load-bearing tasks.
- The INTEGRATE boundary keeps a thorough review of accumulated work as the safety net; triggered per-task review chooses tier and focuses per `review-calibration`.
- Update the resume/frontier semantics (`main-agent.md` §Resuming Work: `implemented` no longer universally means "to review") and `superimplement` Steps so no unconditional review step survives.
- Update the statements the policy flip invalidates: the `CLAUDE.md` "Gates are local discipline … enforced" design principle (restate for triggered review — gates still bind when a review runs), and the `docs/site` implement/integrate pages describing the mandatory loop.
- Validation: a trace through `superimplement` for an unmarked task reaches `approved` with zero reviewer dispatches; a marked task dispatches exactly one scoped review pass.

## Planner Guidance

- The current mandate lives at `superimplement/SKILL.md` task-execution steps (unconditional review, iterate-until-APPROVE) — full choreography map with lines: [review-architecture map](../attachments/map-review-architecture.md) §2.
- Scheduling-policy options and their tradeoffs, with sources: [review-prompting research](../attachments/research-review-prompting.md) §C. The chosen design is its options 3+4+6 combined (triggered + boundary + tier/focus scoping).
- Interactive mode's "ask before review: now / defer / skip" (`superplan/references/interactive-mode.md`) is the existing elective-review precedent; the triggered model generalizes it to subagent mode.
- Planning review (`superplan` §Agent Review) is already depth-conditional — leave its entry condition alone; only its severity vocabulary changes (owned by `review-calibration`).

## Results
