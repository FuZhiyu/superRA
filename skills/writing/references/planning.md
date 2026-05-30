# Planning Discipline for Writing

> Load at the PLAN phase when large writing work enters the superRA workflow: whole-section drafts, whole-paper revisions, R&R passes, or long-form / multi-lane review.

Most writing work stays standalone. This reference only covers writing work large enough to need durable task blocks, reviewer dispatch, or cross-session handoff.

## Hard Gate

Before task drafting, collect enough context to populate the writing header fields below. The gate passes when the researcher has approved the target, mode, review lanes or drafting scope, audience, build command, and disposition.

## Writing Plan Header

Add a writing-specific section to root `.plan/task.md`:

```markdown
**Writing workflow:** <Long-form review retrofit (review-only; no ## Results) | Draft / Polish workflow>

**Writing targets:** <files and sections in scope>

**Audience:** <journal / working-paper / slides / response-letter / replication-reader audience>

**Mode:** <Review | Polish | Draft>

**Review lanes:** <style, structure, terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper; omit lanes out of scope>

**Build command:** <latexmk / quarto / project command, or "not applicable" with reason>

**Writing output:** <review notes in task ## Review Notes | edited manuscript | drafted section>
```

Use only the rows that apply. For long-form review retrofit, write this row exactly so downstream workflows can recognize the review-only path:

```markdown
**Writing workflow:** Long-form review retrofit (review-only; no ## Results)
```

## Retrofitting a Review Plan

Long-form review treats the user's existing draft as the implementation under review. The planner retroactively creates the task tree around that artifact:

- one task per review lane or deep-review perspective;
- each task points at the target file/section and loaded lane reference;
- `status:` starts `not-started`, then reviewers set it to `revise` with task-local review notes or `approved`;
- no `## Results` sections are created; findings belong in task-local `## Review Notes`.

This path uses superimplement for reviewer dispatch and status handling, but not for implementer output production.

Because superimplement's generic entry check expects `## Results`, the writing orchestrator handles this retrofit as a writing-owned exception: do not modify superimplement; instead, enter with the task tree that carries the exact review-only rows above and treat task-local `## Review Notes` as the sole durable findings surface for this writing mode.

## Project Conventions

Populate `## Project Conventions` with writing-side conventions already visible in the target: terminology, abbreviations, citation style, numerical formatting, cross-reference phrasing, voice/tense, and prose typography around notation. Record only choices a fresh agent would otherwise re-infer.

When durable project guidance exists, summarize it in `## Project Conventions` rather than duplicating it in task blocks.
