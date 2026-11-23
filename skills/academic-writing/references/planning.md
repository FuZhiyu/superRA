# Planning Discipline for Writing

> Load at the PLAN phase when large writing work enters the superRA workflow: whole-section drafts, whole-paper revisions, R&R passes, or long-form / multi-lane review.

## Frontier Contributions

Find the writing targets and build command in the project. Use [Mode routing](../SKILL.md#mode-routing). Surface unresolved audience, scope, and output decisions during `superplan §Grilling`.

## Writing Plan Header

Add to the `## Objective` of the governing ancestor task — the task whose subtree is the manuscript:

```markdown
**Writing workflow:** <Review-only task tree | Editing workflow>

**Writing targets:** <files and sections in scope>

**Audience:** <journal / working-paper / slides / response-letter / replication-reader audience>

**Mode:** <Review | Proofread | Polish | Draft>

**Review lanes:** <style, structure, terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper; omit lanes out of scope>

**Build command:** <latexmk / quarto / project command, or "not applicable" with reason>

**Writing output:** <task-local ## Review Notes | edited manuscript | drafted section>
```

Use only the rows that apply. Name the mode in every task that edits manuscript text, including tasks that also run analysis. Review-only trees carry this row exactly, so downstream workflows recognize the path:

```markdown
**Writing workflow:** Review-only task tree
```

## Review Task Trees

Long-form review treats the user's existing draft as the artifact under review. The planner creates a review-only task subtree around that artifact:

- one task per review lane or deep-review perspective;
- each task points at the target file/section and loaded lane reference;
- `status:` starts `not-started`; reviewers set `revise` with task-local review notes, or `approved`.

This path uses superimplement for reviewer dispatch and status handling, not implementer output production — a writing-owned exception that does not modify superimplement. Enter with a task tree carrying the exact review-only row above, and treat task-local `## Review Notes` as the sole durable findings surface: no shared `review.md`, `RESULTS.md`, or equivalent findings file.

## Manuscript Writing Conventions

Use the paper-folder instruction file described in [conventions.md](conventions.md).
