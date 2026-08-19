# Planning Discipline for Writing

> Load at the PLAN phase when large writing work enters the superRA workflow: whole-section drafts, whole-paper revisions, R&R passes, or long-form / multi-lane review.

Covers writing work large enough to need durable tasks, reviewer dispatch, or cross-session continuity; most writing work stays standalone.

## Frontier Contributions

Collect enough context before task drafting to populate the header fields below. The writing targets and the build command are facts to find in the project; the rest go to the researcher as frontier questions (`superplan §Grilling`):

- **Mode** — review, polish, or draft.
- **Audience** — journal, working paper, slides, response letter, or replication reader.
- **Review lanes** in scope, or the drafting scope.
- **Disposition of the output** — task-local review notes, an edited manuscript, or a drafted section.

## Writing Plan Header

Add to the `## Objective` of the governing ancestor task — the task whose subtree is the manuscript:

```markdown
**Writing workflow:** <Review-only task tree | Draft / Polish workflow>

**Writing targets:** <files and sections in scope>

**Audience:** <journal / working-paper / slides / response-letter / replication-reader audience>

**Mode:** <Review | Polish | Draft>

**Review lanes:** <style, structure, terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper; omit lanes out of scope>

**Build command:** <latexmk / quarto / project command, or "not applicable" with reason>

**Writing output:** <task-local ## Review Notes | edited manuscript | drafted section>
```

Use only the rows that apply. Review-only trees carry this row exactly, so downstream workflows recognize the path:

```markdown
**Writing workflow:** Review-only task tree
```

## Review Task Trees

Long-form review treats the user's existing draft as the artifact under review. The planner creates a review-only task subtree around that artifact:

- one task per review lane or deep-review perspective;
- each task points at the target file/section and loaded lane reference;
- `status:` starts `not-started`; reviewers set `revise` with task-local review notes, or `approved`.

This path uses superimplement for reviewer dispatch and status handling, not implementer output production — a writing-owned exception that does not modify superimplement. Enter with a task tree carrying the exact review-only row above, and treat task-local `## Review Notes` as the sole durable findings surface: no shared `review.md`, `RESULTS.md`, or equivalent findings file.

## Project Conventions

Populate `## Project Conventions` with the writing-side conventions visible in the target, per the categories and acid tests in `SKILL.md §Project Conventions in the task tree / CLAUDE.md`. Summarize durable project guidance here rather than duplicating it in task blocks.
