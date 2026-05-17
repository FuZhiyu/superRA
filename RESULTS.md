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

Edited the single "When polish rides the long-form-review pipeline" paragraph in `skills/writing/references/polish.md §C`. The paragraph now states that the Stage-2 task block carries each absorbed finding's body inline under a `**Findings absorbed:**` subheading (preserving the `consistency/<dim>.md`-format entry and the F-ID), and that the implementer reads findings directly from the task block — no separate `## Findings` lookup. The surrounding §C content is unchanged: shape-C definition sentence, standalone-shape-C paragraph, per-tier apply rules (`mechanical` / `conventional` / `authorial`), and the deferred-authorial note all stand verbatim.

**DRY/Necessity pass:** the rewritten paragraph names a non-default location (the `**Findings absorbed:**` subheading) the implementer needs to find the findings in, and explicitly negates the prior lookup behavior the old wording established. The one-line echo of the absorbed-finding contents (dimension format + F-ID) avoids forcing implementers in shape C to load `long-form-review.md` just to know what is in that subheading.

**Files touched:** `skills/writing/references/polish.md`.

## Task 3: Rewrite `writing/CLAUDE.md §Two-stage REVIEW.md → PLAN.md lifecycle`

Rewrote the five-decision block (a)–(e) in `skills/writing/CLAUDE.md §Two-stage REVIEW.md → PLAN.md lifecycle` in place per the inline-edit rule. Decisions (a), (c), (e) carry over with light vocabulary touch-ups; (b) updates its recorder-mechanism phrasing; (d) is reversed.

**(a) Two-stage over one-stage** — unchanged argument; vocabulary updated: the orchestrator now "writes the single set of Stage-2 task blocks once, drawing on every accepted finding" (was "writes Stage-2 task blocks once"). The "two-stage over one-stage" framing and the assembled-view rationale stand.

**(b) Per-finding user-feedback granularity** — substituted "per-dimension or per-tier directives" for "per-task tier directives" (the prior example was a per-Stage-1-task directive that no longer exists). Recorder mechanism rewritten from "`**User feedback:**` field on each Stage-1 task block" to "inline `**User (YYYY-MM-DD):** accept | defer | reject` line at the end of each Stage-1 finding" to match the new Stage-1 shape.

**(c) Stage-2 task granularity** — verbatim; no edits needed (the rule and rationale are independent of the `## Findings` header decision).

**(d) Reversed.** New choice: inline accepted findings in each Stage-2 task under `**Findings absorbed:**`; consolidate rejected and deferred findings in `## Deferred & Rejected` at the bottom. Rejected alternative: `## Findings` header with `**Sources:** F-ID` indirection in Stage-2 tasks. Why rejected: the header indirection adds a lookup hop; the duplication concern that motivated it does not occur in practice — issue-class batching (decision (c)) means each accepted finding is absorbed by exactly one task. Rejected/deferred-visibility concern handled by `## Deferred & Rejected`. F-IDs survive into the inlined finding bodies for commit-message audit even though Stage-2 no longer indexes by them.

**(e) Rename rule (standalone-only)** — verbatim; no edits.

**DRY/Necessity pass:** every line in the rewritten (d) shapes behavior — names the chosen mechanism and its location markers (`**Findings absorbed:**`, `## Deferred & Rejected`), names the rejected alternative and the loss it incurs, dismisses the duplication concern by reference to decision (c), notes F-ID survival. No wrapper instructions, no default reminders, no Skill-Load Manifest restatement, no "here is what you will receive" descriptions.

**Files touched:** `skills/writing/CLAUDE.md`.

## Task 4: Verification sweep

*(pending)*
