# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Load with `review.md` and the relevant review-lane files.

## Trigger

Load when scope spans more than one review lane, thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass.

Review lanes are:

- **Language/style:** `style.md`
- **Structure:** `structure.md`
- **Consistency:** one lane per relevant `consistency/<dim>.md`

## Review Task Tree

Long-form review treats the user's existing draft as the artifact under review. The orchestrator enters through the review-only task tree defined in `planning.md §Review Task Trees`, then dispatches reviewers through superimplement. One task per review lane or deep-review perspective; each task names the target file/section and the lane reference to load.

## Task Granularity

- One language/style task covers sentence- and paragraph-level prose.
- One structure task covers section ordering, governing ideas, headings, and first-sentence storyline.
- One consistency task covers exactly one `consistency/<dim>.md` dimension.
- Deep mode may split a lane into 2-3 perspective tasks with distinct stances or reading orders.
- Add a final verification task when the review scope includes build, references, citations, or cross-document checks.

## Dispatch Convention

Dispatch through `agent-orchestration`'s canonical reviewer template. Keep `Stage: implementation`; long-form review changes the artifact under review, not the superRA stage model.

Reviewers write task-local review notes (not a shared findings section) and set `status: revise` or `approved`. Consistency-lane reviewers use the relevant `consistency/<dim>.md` output format; language/style and structure reviewers use `review.md`'s finding format with `Fix:` per `review.md §Fix tiers`.

Do not create a shared `review.md` or reviewer-of-reviewer pass over assembled findings. If a summary is needed, the orchestrator writes it from current task-local review notes on the manuscript-governing task.

## Review-Time Indices

Use `## Project Conventions` only for durable convention choices covered by `SKILL.md §Project Conventions in the task tree / CLAUDE.md`. For review-time lookup aids, add a compact task-local note or a sibling section on the manuscript-governing task when useful. Common indices: key terminology, figures and tables, cross-references, and notation pointers needed for the assigned lanes.
