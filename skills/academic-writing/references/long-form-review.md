# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Load with `review.md` and the relevant review-lane files.

## Trigger

Load when scope spans more than one review lane, thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass.

Review lanes are:

- **Language/style:** `style.md`
- **Structure:** `structure.md`
- **Consistency:** one lane per relevant `consistency/<dim>.md`

## Review Task Tree

Enter through the review-only task tree defined in `planning.md §Review Task Trees`, then dispatch reviewers through superimplement.

## Task Granularity

- One language/style task covers sentence- and paragraph-level prose.
- One structure task covers section ordering, governing ideas, headings, and first-sentence storyline.
- One consistency task covers exactly one `consistency/<dim>.md` dimension.
- Deep mode may split a lane into 2-3 perspective tasks with distinct stances or reading orders.
- Add a final verification task when the review scope includes build, references, citations, or cross-document checks.

## Dispatch Convention

Dispatch through `agent-orchestration`'s canonical reviewer template. Keep `Stage: implementation`; long-form review changes the artifact under review, not the superRA stage model.

Reviewers write task-local review notes and set `status: revise` or `approved`. Consistency-lane reviewers use the relevant `consistency/<dim>.md` output format; language/style and structure reviewers use `review.md`'s finding format with `Fix:` per `review.md §Fix tiers`.

No shared `review.md`, no reviewer-of-reviewer pass over assembled findings. A needed summary is written by the orchestrator from current task-local review notes on the manuscript-governing task.

## Review-Time Indices

`## Project Conventions` holds only durable convention choices covered by `SKILL.md §Project Conventions in the task tree / CLAUDE.md`. Review-time lookup aids go in a compact task-local note or a sibling section on the manuscript-governing task. Common indices: key terminology, figures and tables, cross-references, and notation pointers for the assigned lanes.
