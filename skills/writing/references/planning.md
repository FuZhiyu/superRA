# Planning Discipline for Writing

> Load at the PLAN phase when large writing work enters the superRA workflow: whole-section drafts, whole-paper revisions, R&R passes, or long-form / multi-lane review.

Most writing work stays standalone. This reference only covers writing work large enough to need durable task blocks, reviewer dispatch, or cross-session handoff.

## Hard Gate

Before task drafting, collect enough context to populate the writing header fields below. The gate passes when the researcher has approved the target, mode, review lanes or drafting scope, audience, build command, and disposition.

## Writing Plan Header

Add a writing-specific section to the PLAN.md header:

```markdown
**Writing workflow:** <Long-form review retrofit (PLAN-only; no RESULTS.md) | Draft / Polish workflow>

**Writing targets:** <files and sections in scope>

**Audience:** <journal / working-paper / slides / response-letter / replication-reader audience>

**Mode:** <Review | Polish | Draft>

**Review lanes:** <style, structure, terminology, notation, citations, numerical, math, argument-logic, code-paper; omit lanes out of scope>

**Build command:** <latexmk / quarto / project command, or "not applicable" with reason>

**Writing output:** <review notes in PLAN.md | edited manuscript | drafted section>

**RESULTS.md:** <required | intentionally absent; review findings live in PLAN.md review notes>
```

Use only the rows that apply. For long-form review retrofit, write these rows exactly so downstream workflows can recognize the PLAN-only path:

```markdown
**Writing workflow:** Long-form review retrofit (PLAN-only; no RESULTS.md)

**RESULTS.md:** intentionally absent; review findings live in PLAN.md review notes
```

## Retrofitting a Review Plan

Long-form review treats the user's existing draft as the implementation under review. The planner retroactively creates PLAN.md around that artifact:

- one task per review lane or deep-review perspective;
- each task points at the target file/section and loaded lane reference;
- `**Review status:**` starts unset, then reviewers set `REVISE` with task-local review notes or `APPROVED`;
- no RESULTS.md is created; findings belong in PLAN.md review notes.

This path uses superimplement for reviewer dispatch and status handling, but not for implementer output production.

Because superimplement's generic entry check expects RESULTS.md, the writing orchestrator handles this retrofit as a writing-owned exception: do not modify superimplement; instead, enter with the PLAN.md that carries the exact PLAN-only rows above and treat PLAN.md review notes as the sole durable findings surface for this writing mode.

## Project Conventions

Populate `## Project Conventions` with writing-side conventions already visible in the target: terminology, abbreviations, citation style, numerical formatting, cross-reference phrasing, voice/tense, and prose typography around notation. Record only choices a fresh agent would otherwise re-infer.

When durable project guidance exists, summarize it in `## Project Conventions` rather than duplicating it in task blocks.
