# Planning Discipline for Writing

> Load at the PLAN phase when large writing work enters the superRA workflow: whole-section drafts, whole-paper revisions, R&R passes, or long-form / multi-lane review.

Most writing work stays standalone. This reference only covers writing work large enough to need durable tasks, reviewer dispatch, or cross-session continuity.

## Hard Gate

Before task drafting, collect enough context to populate the writing header fields below. The gate passes when the researcher has approved the target, mode, review lanes or drafting scope, audience, build command, and disposition.

## Writing Plan Header

Add a writing-specific section to the `## Objective` of the governing ancestor task — the task whose subtree is the manuscript:

```markdown
**Writing workflow:** <Review-only task tree | Draft / Polish workflow>

**Writing targets:** <files and sections in scope>

**Audience:** <journal / working-paper / slides / response-letter / replication-reader audience>

**Mode:** <Review | Polish | Draft>

**Review lanes:** <style, structure, terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper; omit lanes out of scope>

**Build command:** <latexmk / quarto / project command, or "not applicable" with reason>

**Writing output:** <task-local ## Review Notes | edited manuscript | drafted section>
```

Use only the rows that apply. For review-only trees, write this row exactly so downstream workflows can recognize the path:

```markdown
**Writing workflow:** Review-only task tree
```

## Review Task Trees

Long-form review treats the user's existing draft as the artifact under review. The planner creates a review-only task subtree around that artifact:

- one task per review lane or deep-review perspective;
- each task points at the target file/section and loaded lane reference;
- `status:` starts `not-started`, then reviewers set it to `revise` with task-local review notes or `approved`.

This path uses superimplement for reviewer dispatch and status handling, not for implementer output production. It is a writing-owned exception: do not modify superimplement — enter with a task tree carrying the exact review-only row above, and treat task-local `## Review Notes` as the sole durable findings surface. Do not create a shared `review.md`, `RESULTS.md`, or equivalent findings file.

## Project Conventions

Populate `## Project Conventions` with the writing-side conventions visible in the target, using the categories and acid tests in `SKILL.md §Project Conventions in the task tree / CLAUDE.md`. Summarize durable project guidance here rather than duplicating it in task blocks.
