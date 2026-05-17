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

Swept the rewritten long-form-review pipeline for stale references and confirmed cross-doc coherence.

**Stale-reference sweep (Step 1).** Ran `grep -rn "## Findings\|Sources: F\|F-ID\|per-aspect task block\|Stage-1 task block\|Stage-1 per-aspect\|per-aspect block\|temporary task block" skills/ --include="*.md"`. Eleven hits, classified:

- **One stale hit, fixed:** `skills/writing/CLAUDE.md:48` (the `## Multi-agent review pattern` rename-rule decision item) said "Stage 1 per-aspect blocks live in the workflow's `PLAN.md` as temporary task blocks" — a Task-1-superseded statement. Rewritten in place to the new design: when the long-form review rides an existing workflow with a live `PLAN.md`, the Stage-1 `## Findings` section lives in that PLAN.md and the Stage-2 rewrite rebuilds task blocks inline (accepted findings under `**Findings absorbed:**`; rejected/deferred moved to `## Deferred & Rejected`). The collision-avoidance argument and the "one PLAN.md in play" closer carry over verbatim.
- **All other hits valid:** `CLAUDE.md:63` is the rewritten decision (d) documenting the `## Findings`/F-ID indirection as the rejected alternative — citing the rejected design's vocabulary is correct. `polish.md:25` and `long-form-review.md:13,26,27,33,72,75,79,83` are the new authoritative spec — `## Findings` (Stage-1 section), `**Findings absorbed:**` (Stage-2 inline), and F-ID survival into inlined bodies are all part of the chosen design.

**Lifecycle-ladder clause (Step 2).** Read `skills/writing/SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`, line 40: "in the long-form-review pipeline, the REVIEW.md → PLAN.md promotion is mechanical — a literal `git mv REVIEW.md PLAN.md` at the Stage-2 gate (standalone-only; see `long-form-review.md §Standalone-only rename rule`)." Both clauses are unchanged under the new design — the rename is still the Stage-2 mechanical move; the standalone-only rule still names the same `long-form-review.md` anchor. No edit needed.

**End-to-end walk (Step 3).** Imagined long-form review traced through the rewritten files, checking that every step rides canonical implementer/reviewer protocols without new wiring:

1. **Parallel reviewer dispatch.** `long-form-review.md §Dispatch convention` reuses the canonical reviewer template (`subagent_type: superRA:reviewer`, `Stage: implementation`); writing skill add-on auto-routes via the manifest. One reviewer per dispatched dimension. ✓
2. **Stage-1 findings.** Each reviewer writes into its `### <Dimension>` subsection under `## Findings` using the `consistency/<dim>.md` output format unchanged; assigns next-available global F-IDs. ✓
3. **User feedback.** Main agent writes inline `**User (YYYY-MM-DD):** accept | defer | reject [— reason]` on each finding; "User feedback recorded" Workflow Status box flips. ✓
4. **Stage-2 rewrite (orchestrator).** Four atomic moves: `git mv REVIEW.md PLAN.md`; swap Stage-1 rollup for standard PLAN.md rollup; build task blocks per granularity rule with each absorbed finding inlined under `**Findings absorbed:**`; move rejected/deferred to `## Deferred & Rejected` and delete the now-empty `## Findings`. Flip "Plan approved" in the same commit. ✓
5. **Implementer dispatch (mechanical batch).** Canonical implementer template, `Stage: implementation`. Implementer reads `**Findings absorbed:**` directly from the task block — `polish.md §C` confirms no separate `## Findings` lookup is needed. ✓
6. **Reviewer APPROVE.** Canonical reviewer pass over the implementer's commit range; standard APPROVE / REVISE verdict. ✓
7. **Closeout.** Standard PLAN.md rollup `Finished — PLAN.md archived or deleted per the lifecycle ladder` flips when all polish tasks APPROVED.

**Cross-doc coherence verdict.** The three Task-1/2/3 rewrites and the Task-4 Step-1 fix leave the writing skill describing a single coherent design: Stage 1 collects findings in `## Findings` by dimension with inline user verdicts; Stage 2 rewrites them into self-contained task blocks with `**Findings absorbed:**`; rejected/deferred end up in `## Deferred & Rejected`; the standalone-only rename rule and the riding-a-workflow-PLAN.md handling both spell out the same Stage-1/Stage-2 shapes. No new wiring; no orphaned vocabulary.

**Files touched:** `skills/writing/CLAUDE.md` (line 48 only).
