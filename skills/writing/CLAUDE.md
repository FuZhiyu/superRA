# writing - Contributor Notes

Read the repo root `CLAUDE.md` for the DRY/Necessity gate, ownership boundaries, generated-artifact rules, and general skill-authoring discipline. This file records only the current design constraints specific to the writing vertical.

## Current architecture

`writing` is a domain add-on under the existing superRA workflows. It does not define a new workflow stage, reviewer protocol, handoff format, or orchestration mechanism.

The top-level axis is **mode**, not workflow phase:

- **Review** reports issues in prose, structure, citations, consistency, or paper-code alignment.
- **Polish** edits existing prose inside the requested scope.
- **Draft** creates new prose from notes, tables, outlines, or surrounding sections.

Mode determines the loaded references and therefore the authority grant. Do not add conditional prose where a load decision should carry the distinction.

## Governing principle

`SKILL.md` owns the unconditional writing principle:

- Preserve substance: argument, logic, structure, technical claims, author intent, and tone.
- Polish prose: wording, sentence shape, clarity, parallelism, hedging, flow, and mechanical correctness.
- Ask before changing substance or restructuring unless the request explicitly authorizes that scope.

Writing rules are additive to baseline writing competence. Add only constraints that redirect behavior a strong general editor would otherwise get wrong on shared academic drafts.

## Current conventions

- Inline TODOs, placeholders, crude draft phrasing, `??`, and `XXX` are work assigned to the agent inside scope.
- Explicit `DO NOT EDIT` or equivalent hands-off markers are off-limits.
- Intent comments live in source files (`% intent: ...` or `<!-- intent: ... -->`): Draft writes them from the user's brief; Polish preserves existing comments and does not invent new author intent; Review can use them as a yardstick.
- Audience discipline is unconditional: document prose is written for the document's reader, not for the editing conversation or repository context.
- Writing-side project conventions live in the active `## Project Conventions` surface: `PLAN.md` for workflow-scoped work and project `CLAUDE.md` for durable project rules.

## Reference ownership

- `SKILL.md` owns unconditional principles, mode routing, before-start discipline, project-convention categories, and workflow coupling.
- `references/review.md` owns review-mode workflow and fix tiers.
- `references/polish.md` owns polish-mode input shapes, triage, edit/propose/ask behavior, and intent-comment handling.
- `references/draft.md` owns draft-mode input gathering, structure-first drafting, and draft intent comments.
- `references/style.md` owns sentence- and paragraph-level style heuristics.
- `references/structure.md` owns structure-level heuristics and is loaded only when drafting or authorized restructuring is in scope.
- `references/consistency/*.md` owns dimension-specific review checks and output details.
- `references/long-form-review.md` owns multi-lane review orchestration, PLAN-only review retrofit, and review-time indices.
- `references/refactor-and-compile.md` owns document-wide prose refactors and build/compile discipline.
- `references/integration.md` owns behavior specific to writing work riding `integration-workflow`.

If a rule is already carried by one of these references, point to it instead of restating it.

## Workflow boundary

Standalone writing invocations terminate at edit plus commit, or findings plus commit. Full superRA workflows own reviewer dispatch, task status transitions, integration gates, and final closeout. Keep those invariants out of the writing skill unless the behavior is specific to writing mode execution.

Multi-lane review may dispatch one reviewer per lane, but the dispatch mechanics belong to `agent-orchestration`; `writing` supplies the lane files and the long-form-review reference.

## Extension rules

- Add sentence-level rules to `references/style.md`.
- Add structure-level rules to `references/structure.md`.
- Add dimension-specific checks to the relevant `references/consistency/*.md`.
- Add build or document-wide refactor rules to `references/refactor-and-compile.md`.
- Add integration-only writing behavior to `references/integration.md`.
- Add a new knowledge file only when it has a distinct load condition that existing references cannot cover.
- Add a new mode only when Review, Polish, and Draft cannot describe the request shape and the new mode needs a distinct workflow plus a distinct loaded reference set.
- When changing writing-side project conventions, keep math notation owned by `theory-modeling`; writing owns prose typography, terminology, citation, numerical, cross-reference, voice, tense, and abbreviation choices.

Before merging changes under `skills/writing`, walk the root `CLAUDE.md` DRY/Necessity tests line by line.
