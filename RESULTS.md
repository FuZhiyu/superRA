# RESULTS — Simplify long-form review

Pre-allocated task stubs for parallel implementer dispatch.

## Task 1: Rewrite `long-form-review.md` for the simpler design

Rewrote `## Doc convention` in `skills/writing/references/long-form-review.md` for the simpler single-set-of-tasks design.

**Stage 1 shape (changed):** dropped per-dimension/per-aspect task blocks; findings now live in a flat `## Findings` section with one subsection per dispatched dimension (or per perspective in deep mode). Reviewers write into their assigned subsection in the existing `consistency/<dim>.md` output format. Per-finding verdict moved from a per-aspect `**User feedback:**` field to an inline `**User (YYYY-MM-DD):** accept | defer | reject [— reason]` line at the end of each finding. F-IDs preserved at write time and through the Stage-2 rewrite for commit-message audit. Workflow Status now has one `… reviewer done` checkbox per dispatched dimension plus `User feedback recorded`.

**Stage 1 → Stage 2 rewrite (changed):** four moves are now (1) `git mv REVIEW.md PLAN.md`, (2) replace the Stage-1 rollup with the standard PLAN.md rollup, (3) build Stage-2 task blocks per the granularity rule with each absorbed finding inlined under a `**Findings absorbed:**` subheading (preserving the dimension-format entry and F-ID), (4) move rejected and deferred findings to a single `## Deferred & Rejected` section at the bottom and delete the now-empty `## Findings`. Stage-2 tasks are self-contained — no `**Sources:** F2, F5, F9` indirection and no `## Findings` header lookup.

**Carried over verbatim or with light wording updates:** standalone-only rename rule, Stage-2 task granularity (1 authorial = 1 task; mechanical/conventional batched by issue class; final Verify task), review-time indices in `## Project Conventions`, dispatch convention, multi-perspective deep mode, final summary block.

**DRY/Necessity pass:** dropped a single orienting sentence ("The shared review document lives through two stages that share one file.") that named no behavior. Every remaining line either defines a non-default format (verdict line, rewrite moves, Workflow Status blocks), an ordering constraint (four moves), a load-bearing exception (standalone-only rename, no reviewer-of-reviewer), or a pointer to an authoritative spec. Walked the repo CLAUDE.md anti-patterns list: no wrapper instructions, no "here is what you will receive" descriptions, no default reminders, no Skill-Load Manifest restatement.

**Files touched:** `skills/writing/references/long-form-review.md`.

## Task 2: Update `polish.md §C` to drop F-ID lookup

*(pending)*

## Task 3: Rewrite `writing/CLAUDE.md §Two-stage REVIEW.md → PLAN.md lifecycle`

*(pending)*

## Task 4: Verification sweep

*(pending)*
