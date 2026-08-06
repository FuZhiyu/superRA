---
title: "Reporting Contract: Concise Writing and the Conversation Boundary"
status: approved
depends_on:
  - role-skills
---

## Objective

Maintain **Communicate**, superRA's human-facing communication contract across conversation, task files, reports, and workflow handoffs. A cold reader should reach the outcome, evidence, caveats, and next action without duplicated facts or avoidable decoding work.

- `superRA:communicate` is standalone and available to planners, implementers, reviewers, integrators, and direct user invocations.
- Brevity comes from selection and structure; clarity wins when compression would obscure meaning.
- The contract governs information choice, order, rewriting, distillation, and review. Academic `writing` owns manuscript discipline; technical Markdown guidance owns rendering mechanics.
- Each fact has one durable home. Other surfaces point to it.
- Learn from `avoid-ai-writing` only where a pattern lowers information density or raises communication friction. Authorship detection and “sound human” are outside scope.

## Planner Guidance

- The approved Results below document the v0.4 baseline. The child task owns the expanded architecture.
- Evidence: [writing-surfaces map](../attachments/map-writing-surfaces.md) and [concise-writing research](../attachments/research-concise-writing.md).
- Showcase/task-file hygiene remains out of scope; update user-facing docs invalidated by the skill replacement.

## Revision Notes

Substantive expansion: replace the implementer-centered reporting contract with the cross-role standalone **Communicate** skill. Remove this section once the child implementation lands and the parent Results reflect the new owner.

## Results

The contract is [`implement-task/SKILL.md` §Reporting](../../../skills/implement-task/SKILL.md#L37-L60): reporting is half the task and gets a real share of the thinking budget; pyramid structure, pointing at its owner [`writing/references/structure.md`](../../../skills/writing/references/structure.md); the finding bar; each-fact-once, with the cross-file failure mode named (a number copied into a second file survives wrong in every copy once the result changes); extras wait to be asked for; concise-by-selection as the anti-compression guardrail; current-not-a-log editing; and a before/after merge-task example. `review-task` `results-writing` focus, [`interactive-mode.md`](../../../skills/superplan/references/interactive-mode.md), `superimplement` Step 3, `report-in-markdown`, and `changing-the-tree.md` all point here.

`using-superra` slims to the all-agent survival kit — [§Communication, §Commits, §Task Interface, §Skill-Load Manifest](../../../skills/using-superra/SKILL.md). Work Defaults moved into [`implement-task`](../../../skills/implement-task/SKILL.md#L10); the workflow map and Execution Modes moved to [`main-agent.md`](../../../skills/using-superra/references/main-agent.md); `report-in-markdown` is load-on-demand, with the render-integrity hook in [`task_hook.py`](../../../skills/task-tree/scripts/task_hook.py) naming it when it fires (verified on a seeded bad file and a clean file).

The house citation/figure conventions live in [`using-superra` §Task Interface](../../../skills/using-superra/SKILL.md#L38), not in the contract — every agent hits them on nearly every write, and only `using-superra` is always loaded. `report-in-markdown` stays the authority on the full form; the duplication is deliberate, prevention beating post-hoc correction.

Supporting edits: inclusion test, omit-by-default subsection menu, and dated-decision-ledger stale class in [`task-file-contract.md`](../../../skills/task-tree/references/task-file-contract.md); the `<summarize the results>` placeholder replaced in [`superimplement`](../../../skills/superimplement/SKILL.md); the final-diff self-check trail moved to the commit body ([`refactor-and-integrate`](../../../skills/refactor-and-integrate/SKILL.md), [`protect.md`](../../../skills/superintegrate/references/protect.md)); the objective-rewrite trim counterpart in [`task-tree-design.md`](../../../skills/superplan/references/task-tree-design.md); the canonical `task.md` example in [`task-tree/SKILL.md`](../../../skills/task-tree/SKILL.md) rewritten to plain lines. Downstream surfaces repointed for the relocations: [`CLAUDE.md`](../../../CLAUDE.md#L81-L88) ownership rows for Execution modes, the read/edit interface, and the reporting contract, plus its Agent Load Surface row; [`RELEASE-NOTES.md`](../../../RELEASE-NOTES.md#L20) for §Work Defaults.

The extras rule keeps the §Communication "no closing offers" line intact: the agent *states* the extra it left out as a delta in its return, and it enters `## Results` only if the researcher or orchestrator says so — a statement, not an offer.

Tests: harness suite 126 passed; task-tree suite 797 passed, 0 skipped.

Not swept: this repo's own task files and the `docs/site` exemplars, out of v0.4 scope per the parent.
