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

**Status:** Not started

## Task 3: One-line read instructions in draft.md and polish.md

**Status:** Not started

## Task 4: Contributor entry in skills/writing/CLAUDE.md

**Status:** Not started
