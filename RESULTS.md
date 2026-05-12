# Writing-Side Conventions in the Handoff-Doc Header — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-12 (planning)
**Status:** In Progress

---

## Task 1: Author the new SKILL.md section

**Status:** Implemented

### Outcome

New section "Project Conventions in the handoff doc / CLAUDE.md" inserted in `skills/writing/SKILL.md` between §Audience ("Write to the reader, not the conversation") and §Before you start, sibling to §Audience. Section is ~30 lines and contains: one-paragraph opener with the acid-test framing; lifecycle ladder (REVIEW.md → PLAN.md → CLAUDE.md) with the theory-modeling promotion pointer; 7-row contribution table (Convention | What's recorded | Acid test); excluded-categories line; soft-trigger line; scanning-is-unspecified closer.

### Notes

**DRY / Necessity audit (Step 2 outcome).** Walked the new section line-by-line against repo `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action`. All lines kept; no deletions. Justifications: the opener carries the acid-test framing that shapes every row's "What's recorded" choice; the lifecycle ladder is the load-bearing routing decision and the promotion pointer is one line, not a restatement; the table rows are the contribution itself; the excluded-categories line prevents duplicate recording against theory-modeling's table; the soft-trigger line shapes behavior agents wouldn't produce on their own (default would be either always-scan or never-scan); the scanning-is-unspecified line is a deliberate non-prescription that prevents agents inventing a procedure. One refactor inside the table: rows 4 and 7 originally cited consistency advisories (`consistency/numerical.md:97`, `consistency/notation.md:62`) as the acid test; replaced with the generic "Fresh agent would guess between conventions" because the line cites would drift and the consistent acid-test framing makes the column readable.

**Cross-file consistency (Step 3 outcome).** Math-notation boundary phrasing ("symbol → meaning, equation numbering") matches `theory-modeling/SKILL.md:215` and `theory-modeling/CLAUDE.md` (symbol → meaning, math notation table). Promotion pointer cites `theory-modeling/SKILL.md §Documentation and handoff` (the correct §, lines 210+). Soft trigger composes with §Mode routing without introducing a new mode — it conditions on "first long-form review or first draft pass" within existing Review and Draft modes. No discrepancies found; no edits to other files required.

## Task 2: Rework long-form-review.md §Doc convention

**Status:** Implemented

### Outcome

`skills/writing/references/long-form-review.md §Doc convention` reworded in place. The opening sentence now qualifies REVIEW.md as the shared doc "for the standalone case" rather than the only home. The first of the three adaptation bullets is generalized: header indices live in the relevant handoff doc's `## Project Conventions` header per the lifecycle ladder in `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`, with a one-line decoder naming REVIEW.md (standalone), PLAN.md (workflow), CLAUDE.md (project-permanent). The four long-form-review-specific indices (notation, terminology, figures-and-tables, cross-reference) are kept and reframed as additive to the writing-side rows; the SKILL.md 7-row writing-side table is named as the master list. The orchestrator-builds-once-before-dispatch invariant and the promote-to-Document-Map sentence are preserved verbatim. §Dispatch convention and §Multi-perspective deep mode untouched.

### Notes

**DRY / Necessity audit (Step 2 outcome).** All lines in the new bullet kept; no deletions. Pointer-not-restate verified for both the SKILL.md 7-row table and the SKILL.md lifecycle ladder. The one-line parenthetical decoding the ladder (REVIEW.md / PLAN.md / CLAUDE.md) is the tolerable one-line echo per repo `CLAUDE.md §Teach the Protocol` — it spares an agent already loaded into long-form review from a redundant SKILL.md load to interpret the pointer. The four review-time indices (notation, terminology, figures-and-tables, cross-reference) are long-form-review's own orchestrator-built artifact and not duplicated in SKILL.md's writing-side 7-row table; they remain owned here. The orchestrator-builds-once invariant is behavior-shaping (its absence would yield N redundant index builds across parallel reviewers).

## Task 3: One-line read instructions in draft.md and polish.md

**Status:** Not started

## Task 4: Contributor entry in skills/writing/CLAUDE.md

**Status:** Not started
