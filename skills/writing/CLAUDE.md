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

`SKILL.md` owns the unconditional writing principle (preserve substance, polish prose, ask before changing substance or restructuring). Writing rules are additive to baseline competence: add only constraints that redirect behavior a strong general editor would otherwise get wrong on shared academic drafts.

## Reference ownership

- `SKILL.md` owns unconditional principles, mode routing, before-start discipline, project-convention categories, and workflow coupling.
- `references/review.md` owns review-mode workflow and fix tiers.
- `references/polish.md` owns polish-mode input shapes, triage, edit/propose/ask behavior, and intent-comment handling.
- `references/draft.md` owns draft-mode input gathering, structure-first drafting, and draft intent comments.
- `references/style.md` owns sentence- and paragraph-level style heuristics.
- `references/structure.md` owns structure-level heuristics and is loaded only when drafting or authorized restructuring is in scope.
- `references/consistency/*.md` owns dimension-specific review checks and output details.
- `references/long-form-review.md` owns multi-lane review orchestration, review-only task trees, and review-time indices.
- `references/refactor-and-compile.md` owns document-wide prose refactors and build/compile discipline.
- `references/integration.md` owns behavior specific to writing work riding `superintegrate`.

If a rule is already carried by one of these references, point to it instead of restating it.

## Workflow boundary

Standalone writing invocations terminate at edit plus commit, or findings plus commit. Full superRA workflows own reviewer dispatch, task status transitions, integration gates, and final closeout. Keep those invariants out of the writing skill unless the behavior is specific to writing mode execution.

Multi-lane review may dispatch one reviewer per lane, but the dispatch mechanics belong to `agent-orchestration`; `writing` supplies the lane files and the long-form-review reference.

The review-only task-tree path (`references/long-form-review.md` + `references/planning.md`) is writing-owned: `superplan` routes large writing work to the writing planning reference, and `superimplement` carries no writing-specific exception prose.

## Extension rules

- Add a rule to the reference that owns its concern (see Reference ownership above).
- Add a new knowledge file only when it has a distinct load condition that existing references cannot cover.
- Add a new mode only when Review, Polish, and Draft cannot describe the request shape and the new mode needs a distinct workflow plus a distinct loaded reference set.
- When changing writing-side project conventions, keep math notation owned by `theory-modeling`; writing owns prose typography, terminology, citation, numerical, cross-reference, voice, tense, and abbreviation choices.

Before merging changes under `skills/writing`, walk the root `CLAUDE.md` DRY/Necessity tests line by line.
