# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Loaded **in addition to** `review.md` and the relevant `consistency/<dim>.md` files; everything those references already teach is assumed and not restated here.

## Trigger

Load when scope is multi-dimensional (>1 `consistency/<dim>.md`), thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass. Quick single-dimension reviews stay in `review.md` and do not load this file.

## Doc convention

The shared review document is **`REVIEW.md` at the worktree root** — never `PLAN.md`, which collides with a workflow's own plan when one is in play. Lifecycle: born for one review, dies after closeout (delete or archive). Anatomy follows `superRA:handoff-doc references/plan-anatomy.md` (header + task blocks); inline-edit + atomic-commit discipline carries over from `superRA:handoff-doc` SKILL.md.

Three adaptations of that anatomy:

- **Header indices live under `## Project Conventions`** — notation index (key symbols → meaning + first-use location), terminology index (key terms → definition + first-use), figures-and-tables index, cross-reference index. The orchestrator builds these once before dispatch so each parallel reviewer reads the indices instead of cold-reading the manuscript. Promote to a sibling `## Document Map` section when the indices outgrow Conventions.
- **Per-aspect blocks ARE task blocks** per `plan-anatomy.md §Task Block Anatomy` — one block per dimension (or, in deep mode, per perspective), all `**Depends on:** *(none)*`. Reviewer findings land in the existing review-notes blockquote of the task block, each finding in its loaded `consistency/<dim>.md` output format including the `Fix:` tier line per `review.md §Fix tiers`.
- **Final summary block at the top** of REVIEW.md: severity × fix-tier counts table, top-3 priorities, pointer to each per-aspect block, and a per-tier batch table (mechanical / judgment / decision) sized for polish-mode shape C handoff. Built by the orchestrator, optionally with one final-summary reviewer pass over the assembled doc.

`## Workflow Status` is **omitted** for standalone review-as-data; when this protocol rides a workflow, that workflow's PLAN.md owns the rollup.

## Dispatch convention

Use the canonical reviewer template in `superRA:agent-orchestration §Dispatch Templates` — `subagent_type: "superRA:reviewer"`, `Stage: implementation` (no new Stage value; the writing skill add-on already routes via the manifest). Two adaptations specific to review-as-data:

- The manuscript is the implicit "implementer output" being audited; reviewers append findings to their assigned per-aspect block in `REVIEW.md` instead of returning APPROVE / REVISE on a commit range.
- **No reviewer-of-reviewer pass.** The assembled `REVIEW.md` *is* the artifact; chaining adversarial review over the findings is recursion. An optional final-summary reviewer pass over the assembled doc is allowed if the orchestrator wants a sanity check, and is the only second pass permitted.

Parallel-dispatch + worktree-isolation steering carries over verbatim from `agent-orchestration`; one reviewer per per-aspect block.

## Multi-perspective deep mode

When thoroughness is `deep`, dispatch 2–3 reviewers per dimension with diverse stances ("skeptical referee" / "constructive mentor" / "domain expert") and ordering ("forward" / "backward from conclusions" / "most complex first"). Each reviewer writes findings into its **own** per-perspective task block under that dimension. Closeout merges findings across perspectives and weights multi-agent-confirmed findings higher in the final summary.
