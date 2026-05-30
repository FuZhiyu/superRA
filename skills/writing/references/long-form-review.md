# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Load with `review.md` and the relevant review-lane files.

## Trigger

Load when scope spans more than one review lane, thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass.

Review lanes are:

- **Language/style:** `style.md`
- **Structure:** `structure.md`
- **Consistency:** one lane per relevant `consistency/<dim>.md`

## Task Tree Retrofit

Long-form review treats the user's existing draft as the implementation under review. The orchestrator creates the task tree from the target document, then dispatches reviewers through superimplement.

The root `.plan/task.md` must carry the writing planning rows from `planning.md`, including:

```markdown
**Writing workflow:** Long-form review retrofit (review-only; no ## Results)
```

Task files follow the standard task.md anatomy (see `task-system/references/planning.md`), with one task per review lane or deep-review perspective. Each task names the target file/section and the lane reference to load.

## Task Granularity

- One language/style task covers sentence- and paragraph-level prose.
- One structure task covers section ordering, governing ideas, headings, and first-sentence storyline.
- One consistency task covers exactly one `consistency/<dim>.md` dimension.
- Deep mode may split a lane into 2-3 perspective tasks with distinct stances or reading orders.
- Add a final verification task when the review scope includes build, references, citations, or cross-document checks.

## Dispatch Convention

Dispatch through `agent-orchestration`'s canonical reviewer template. Keep `Stage: implementation`; long-form review changes the artifact under review, not the superRA stage model.

Reviewers do not append to a shared findings section. They write task-local review notes and set `status: revise` or `approved` using the normal reviewer protocol.

Consistency-lane reviewers use the relevant `consistency/<dim>.md` output format inside the review-notes item. Language/style and structure reviewers use `review.md`'s finding format and add `Fix: mechanical | conventional | authorial` using `review.md §Fix tiers`.

Do not dispatch a reviewer-of-reviewer pass over assembled findings. If a summary is needed, the orchestrator writes it from current task-local review notes.

## Workflow Status

Use the task-system status rollup. For review-only long-form review:

- All tasks start with `status: not-started`.
- `status` rolls up to `approved` when every review task is `approved`.
- Integration uses the same `status` field — tasks stay at `approved` unless integration review sets them back to `revise`.

## Review-Time Indices

Use `## Project Conventions` only for durable convention choices covered by `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`. For review-time lookup aids, add a compact task-local note or a sibling section in root `.plan/task.md` when useful. Common indices: key terminology, figures and tables, cross-references, and notation pointers needed for the assigned lanes.
