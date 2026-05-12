# Writing-Side Conventions in the Handoff-Doc Header Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This plan edits skill content (no implemented domain vertical) — apply contributor discipline from the repo-root `CLAUDE.md` line-by-line, especially the DRY / Necessity gate and the "Teach the Protocol, Don't Prescribe Each Action" anti-patterns.

**Objective:** Add a writing-side contribution to the generic `## Project Conventions` slot in handoff docs, so draft / polish / long-form-review modes record and read a paper's writing-side conventions (terminology, abbreviations, citation format, numerical formatting, cross-reference phrasing, voice/tense, prose typography around notation) once instead of re-inferring them every session.

**Methodology:** Authoring task. Add one new short section to `skills/writing/SKILL.md` after the Audience section, declaring the 7-row writing-side conventions list, the lifecycle ladder (REVIEW.md → PLAN.md → CLAUDE.md), and a soft trigger on first long-form review / first draft pass. Coordinate the other writing references (`long-form-review.md`, `draft.md`, `polish.md`) to point at the new section. Record the design rationale in `skills/writing/CLAUDE.md` so future contributors don't re-litigate the decisions. No changes to `handoff-doc`, `theory-modeling`, or `planning-workflow` (the slot is generic and already accepts vertical contributions).

**Domain vertical:** None implemented for skill-content authoring on superRA itself. Flagged per `planning-workflow` Phase 1; the work uses the contributor discipline in repo-root `CLAUDE.md` in place of a domain skill.

**Conventions:** One paragraph per line in skill / handoff prose (no hard wrap inside paragraphs) per the memory rule `feedback_one_paragraph_per_line`. Apply audience-awareness upstream when writing prose per `skills/writing/SKILL.md §Write to the reader, not the conversation`. Walk the DRY / Necessity tests line-by-line on every new instruction line in skill files per repo `CLAUDE.md §Teach the Protocol`.

**Output:** Five edits.
- `skills/writing/SKILL.md` — new section "Project Conventions in the handoff doc / CLAUDE.md" (~30 lines).
- `skills/writing/references/long-form-review.md` — rework §Doc convention to point at the lifecycle ladder (~5 line diff).
- `skills/writing/references/draft.md` — one-line read-conventions-before-drafting instruction.
- `skills/writing/references/polish.md` — one-line read-conventions-during-triage instruction.
- `skills/writing/CLAUDE.md` — contributor entry (~15 lines) recording lifecycle-ladder, no-fourth-mode, and soft-trigger decisions.

**Expected Results / Hypotheses:** After this plan lands, a fresh agent dispatched into a long-form review or a draft pass against a paper with an existing PLAN.md will find writing-side conventions in `## Project Conventions` and read from them; if the section is empty on first long-form / first draft, the agent will inventory and populate it before substantive editing. Routine polish does not auto-scan. Standalone long-form review writes to its own REVIEW.md `## Project Conventions` header (REVIEW.md is itself a handoff doc per `long-form-review.md:11`).

**Sensitivity Analysis:** N/A — authoring task, no quantitative output.

**Pipeline:** N/A — single-edit task across five files, no script to run.

---

## Workflow Status

- [x] **Plan approved** — user approved the plan in plan mode on 2026-05-12; researcher decisions logged below
- [x] **Execution complete** — all tasks `APPROVED`, no reproducibility pipeline (skill-content work)
- [x] **Drift tests created** — N/A; no quantitative result to protect (Protect decision logged 2026-05-12)
- [ ] **Integrated** — integration reviewer `APPROVED` on `BASE_HEAD_SHA..HEAD` after Sync
- [ ] **Docs finalized** — RESULTS.md matured (or consolidated to CLAUDE.md per branch pattern), project docs audited, doc-reviewer `APPROVED`
- [ ] **Finished** — branch landed locally or PR opened

---

## Project Conventions

Walked at planning time (2026-05-12). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 322588d): contributor guidelines for superRA itself. Authoritative on: skill-creation discipline (load `skill-creator` before editing `skills/*/SKILL.md`); the DRY / Necessity gate (`§Teach the Protocol, Don't Prescribe Each Action`) is a **blocking** self-check on every line added to `skills/*` or `agents/*`; ownership boundaries table assigns one owner per concern; lean-agents / rich-references architectural pattern. Codex / harness design rules cover generator-driven artifacts (`sync_codex_agents.py`) that this plan does NOT touch.
- `/AGENTS.md`, `/AGENT.md`: aliases for `/CLAUDE.md`.
- `/README.md` (HEAD at 322588d): user-facing product overview. Not load-bearing for this plan.

### Module-level docs walked
- `skills/writing/CLAUDE.md` (HEAD at 322588d): records prior design choices for the writing vertical — the Preserve-substance-polish-prose principle replacing the Iron Law, mode-based routing (Review / Polish / Draft) replacing per-phase routing, load-as-authority-grant rule for light-vs-deep polish, TODO-as-task / DO-NOT-EDIT-as-hands-off default, intent-comment discipline, audience-awareness upstream protocol. New contributor entry from Task 4 must compose with these without restating them.
- `skills/writing/SKILL.md` (HEAD at 322588d): three modes (Review / Polish / Draft), unconditional principles (Preserve substance / Audience awareness), mode-routing table, knowledge-files table, coupling-to-superRA-workflows section. The new section lands after §Audience.
- `skills/handoff-doc/SKILL.md` and `references/plan-anatomy.md` (HEAD at 322588d): the generic `## Project Conventions` slot exists and is already populated by `econ-data-analysis` (Data Inventory) and `theory-modeling` (Model Inventory / Notation Conventions table); writing has no contribution yet. The slot is authored by the orchestrator at planning time, refreshed at `implementation-workflow` Step 1 on new doc discovery; subagents read it as read-only.
- `skills/theory-modeling/SKILL.md` (HEAD at 322588d): canonical Notation Conventions table in PLAN.md owned by theory-modeling — symbol → meaning, user-gated promotion from per-task ledger. **Boundary line for this plan:** theory-modeling owns math notation (symbol → meaning, equation numbering); writing owns prose typography of notation (bold/italic/hat conventions when symbols appear in text). Orthogonal — they occupy different rows in the same `## Project Conventions` section.
- `skills/writing/references/long-form-review.md` (HEAD at 322588d): currently asserts REVIEW.md as the home for `## Project Conventions` indices, built by the orchestrator before parallel-reviewer dispatch. Task 2 generalizes this — REVIEW.md is itself a handoff doc, so the rule becomes "the relevant handoff doc's `## Project Conventions` header," with the lifecycle ladder in `SKILL.md` deciding which.

### Not walked (not reachable from the planned diff)
- `.codex/`, generator scripts (`scripts/sync_codex_agents.py`), and `skills/using-superRA/references/direct-mode-*.md` — not touched by this plan.
- Other domain skills (`econ-data-analysis`, `theory-modeling`) — read as boundary references above; not modified.
- Other workflow skills (`planning-workflow`, `implementation-workflow`, `integration-workflow`, `agent-orchestration`, `semantic-merge`, `result-protection`, `refactor-and-integrate`) — not modified.

---

## Decisions

> **User decision (2026-05-12):** Drop hedging register from the writing-side conventions list. Keep voice/tense and prose typography around notation.
> **Question asked:** Which of the three borderline convention categories (hedging register, voice/tense, prose typography around notation) survive into the list?

> **User decision (2026-05-12):** REVIEW.md is itself a handoff doc — don't carve a separate case for it. Conventions live in *whichever* handoff doc is in play.
> **Question asked:** Should `long-form-review.md` defer to PLAN.md when one exists, or keep REVIEW.md's own indices?
> **Rationale (user):** REVIEW.md follows `handoff-doc` anatomy (`long-form-review.md:11`) — it IS a handoff doc.

> **User decision (2026-05-12):** Conventions can also live in the relevant `CLAUDE.md`. The homes form a lifecycle ladder — REVIEW.md (single review) → PLAN.md (analysis-scoped) → CLAUDE.md (project-permanent) — ordered by permanence. Promote up the chain when the user signals durability (mirrors theory-modeling per-task-ledger → PLAN.md Notation Conventions promotion).
> **Question asked:** *(volunteered by user)* CLAUDE.md as an additional home.

> **User decision (2026-05-12):** Soft trigger — scan on first long-form review or first draft pass against a paper with no recorded conventions. No auto-scan on routine polish or single-dimension review.
> **Question asked:** Fully adaptive (no trigger) or soft trigger?

> **User decision (2026-05-12):** Proceed with integration.
> **Question asked:** Step 4 completion menu — proceed with integration, change the plan, keep the branch as-is, or discard?

> **User decision (2026-05-12):** Skip drift tests — no quantitative result to protect for skill-content edits; reviewer dispatch (per-task review + integration review) is the protection.
> **Question asked:** Protect step — skip drift tests, add build/outline-stability check, or define some other protection?

---

### Task 1: Author the new SKILL.md section
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**File:** `skills/writing/SKILL.md`
**Input:** Current SKILL.md, the 7-row convention list in `/Users/zhiyufu/.claude/plans/i-think-that-s-a-curious-charm.md`, the lifecycle ladder and soft trigger from §Decisions above.
**Output:** New section "Project Conventions in the handoff doc / CLAUDE.md" inserted after the §Audience section ("Write to the reader, not the conversation") and before §Before you start. The section is sibling to §Audience.

- [x] **Step 1: Author the new section.** Write the section. Required content, with no narrative filler:
  - One-paragraph opener: writing-side conventions are paper-specific choices among defensible alternatives (cite the acid test: would a fresh agent get it wrong if not written down?). Recording once prevents re-inference.
  - **Lifecycle ladder:** REVIEW.md (single review) → PLAN.md (analysis-scoped) → CLAUDE.md (project-permanent). Conventions live in *whichever* handoff doc is in play for the current task. When no handoff doc is in play, standalone invocations return the inventory as a conversation reply. Promote up the ladder when the user signals durability — same pattern as theory-modeling's per-task-ledger → PLAN.md Notation Conventions promotion at `theory-modeling/SKILL.md` §Documentation and handoff.
  - **7-row table** with columns "Convention | What's recorded | Acid test" — terminology, abbreviations, citation format, numerical formatting, cross-reference phrasing, voice and tense conventions, prose typography around notation. Use the row contents from the approved plan at `/Users/zhiyufu/.claude/plans/i-think-that-s-a-curious-charm.md §Updated convention list (7 rows)`.
  - **Excluded (one line):** math notation (owned by `theory-modeling` Notation Conventions table); section/caption capitalization and page-layout macros (venue / template territory).
  - **Soft trigger (one line):** "On the first long-form review or first draft pass against a paper with no recorded conventions, inventory the writing-side conventions and record them in the relevant handoff doc / CLAUDE.md before substantive editing. Routine polish and single-dimension review do not auto-scan."
  - **Closer (one line):** "Scanning is unspecified — agents inventory using `references/consistency/*.md` and `references/style.md`; there is no separate scan procedure."
- [x] **Step 2: DRY / Necessity self-check.** Walk the new section line by line against repo `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action`. For every line, ask: (a) is the information already carried by another skill, reference, or handoff doc the agent reads? (DRY) — if yes, point, don't restate; (b) without this line, would the agent's behavior be unstable? (Necessity) — if no, delete. Delete or rewrite any line that fails either test. Record the audit outcome (lines kept, lines deleted, why) in RESULTS.md Task 1 §Notes.
- [x] **Step 3: Cross-file consistency.** Check the boundary line about math notation matches the phrasing used in `theory-modeling/SKILL.md §Documentation and handoff` and the `## Project Conventions` Notation Conventions row owned by theory-modeling. Verify the lifecycle ladder mention of "promotion up the chain" matches the theory-modeling per-task-ledger → PLAN.md promotion semantics. Verify the soft trigger condition aligns with the existing §Mode routing table (no mode change). Update SKILL.md or note discrepancies in RESULTS.md.
- [x] **Step 4: Commit.** Stage only `skills/writing/SKILL.md` plus PLAN.md / RESULTS.md updates. `git diff --cached` to confirm. Atomic commit titled `skills: add Project Conventions section to writing SKILL.md`.

### Task 2: Rework long-form-review.md §Doc convention
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** APPROVED

**File:** `skills/writing/references/long-form-review.md`
**Input:** Current `long-form-review.md` (especially lines 9–17), the new SKILL.md §Project Conventions section (SKILL.md lines 36-58).
**Output:** §Doc convention reworded so that the `## Project Conventions` header is the relevant *handoff doc's* header — REVIEW.md, PLAN.md, or CLAUDE.md per the ladder in `SKILL.md`. No "REVIEW.md only" framing.

- [x] **Step 1: Rework §Doc convention.** Edit the first bullet of "Three adaptations" in place per the inline-edit rule. Concrete changes landed:
  - Opening sentence qualified to "for the standalone case" — REVIEW.md remains the standalone shared doc and the lifecycle (born for one review, dies at closeout) is preserved.
  - First bullet generalized: indices now live in "the relevant handoff doc's `## Project Conventions` header" with a one-line decoder for the lifecycle ladder (REVIEW.md / PLAN.md / CLAUDE.md) pointing at `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`. The four long-form-review-specific indices (notation, terminology, figures-and-tables, cross-reference) are kept and described as additive to the writing-side rows; the SKILL.md 7-row table is named as the master list.
  - Orchestrator-builds-indices-once-before-dispatch invariant preserved verbatim (now scoped to "the four review-time indices").
  - Promote-to-Document-Map line preserved verbatim.
  - §Dispatch convention and §Multi-perspective deep mode untouched.
- [x] **Step 2: DRY / Necessity self-check on the diff.** Walked the new bullet line by line. Confirmed: the bullet points at the SKILL.md 7-row table, does not restate it; points at the SKILL.md lifecycle ladder with a one-line decoder, does not restate the promotion semantics or the soft trigger. The four review-time indices are long-form-review's own contribution (orchestrator-built, manuscript-derived) and not duplicated in SKILL.md. The orchestrator-builds-once invariant is behavior-shaping — without it parallel reviewers would re-build indices N times. All lines kept.
- [x] **Step 3: Commit.** Stage only `long-form-review.md` plus PLAN.md / RESULTS.md updates. Atomic commit titled `skills: generalize long-form-review §Doc convention to handoff-doc ladder`.

### Task 3: One-line read instructions in draft.md and polish.md
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/writing/references/draft.md`, `skills/writing/references/polish.md`
**Input:** Current draft.md and polish.md, the new SKILL.md section from Task 1.
**Output:** One short addition in each file pointing at the conventions section.

- [x] **Step 1: Add the draft.md instruction.** Folded into the existing Workflow Step 1 ("Gather inputs") rather than inserted as a new step — the convention read is an input to drafting, and folding avoids renumbering Steps 2-5. Added sentence: *"If a handoff doc carrying `## Project Conventions` is in play, read its writing-side rows and align to them; if those rows are empty on the first draft pass against the paper, populate them before drafting (per `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`)."* — pointer to SKILL.md replaces enumerating the 7 dimensions (DRY).
- [x] **Step 2: Add the polish.md instruction.** Inserted as a one-paragraph framing right under the `## Input shapes` header so it applies to shapes A, B, and C uniformly: *"Across all three shapes: if `## Project Conventions` is in play in a handoff doc, treat its writing-side rows as the established choice during triage — divergences from them are findings to fix or surface, not free authorial calls (per `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`)."* — pointer-style; no row enumeration; reuses `writing-side rows` framing from SKILL.md.
- [x] **Step 3: DRY / Necessity check.** Walked both lines. Both pass Necessity: the draft.md line is what makes draft-mode read `## Project Conventions` (without it agents re-infer terminology/citation style every session) and operationalizes the soft trigger at the draft call site; the polish.md line redirects triage to treat convention divergences as findings rather than authorial choices (without it polish would either ignore the rows or surface them inconsistently). Both pass DRY: no enumeration of the 7-row table, no restatement of the lifecycle ladder or scanning protocol — the SKILL.md pointer carries those. No lines deleted.
- [x] **Step 4: Commit.** Stage only `draft.md`, `polish.md`, plus PLAN.md / RESULTS.md updates. Atomic commit titled `skills: wire draft + polish to read Project Conventions header`.

### Task 4: Contributor entry in skills/writing/CLAUDE.md
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** REVISE

> **Integration review notes (2026-05-12):**
>
> 1. **[BLOCKING] Missing Final Diff Self-Check trail** — `refactor-and-integrate §Final Diff Self-Check` requires a `**Final diff self-check:** <command/range>; <surviving-change classes>; <suspicious hunk justifications or none>` line in the assigned PLAN.md task block before commit, including when no code changed. None of the four tasks in this cycle carry this trail; `grep "Final diff self-check" PLAN.md RESULTS.md` returns nothing. One consolidated trail under Task 4 covering the full `git diff 322588d..HEAD` is sufficient — the cycle's surviving hunks split cleanly across the four tasks with no overlap, so a single line naming the four hunk classes (SKILL.md §Project Conventions section / long-form-review §Doc convention bullet rework / draft.md Step 1 sentence + polish.md `## Input shapes` framing / writing/CLAUDE.md new dated entry) plus a no-suspicious-hunks note covers all four. Fix: add the trail line at the end of this task block, then re-dispatch.

**File:** `skills/writing/CLAUDE.md`
**Input:** Current `skills/writing/CLAUDE.md`, the four §Decisions entries above, the SKILL.md section from Task 1.
**Output:** One new contributor entry (~15 lines) documenting the design choices behind the new conventions section so future contributors don't re-litigate them.

- [x] **Step 1: Author the contributor entry.** Appended a new dated section "Writing-side contribution to the `## Project Conventions` slot" after §Audience-awareness, matching the existing one-paragraph-per-line dated-entry convention. Five paragraphs cover: (a) the parallel to `econ-data-analysis`'s Data Inventory and `theory-modeling`'s Notation Conventions plus the math-notation-vs-prose-typography boundary as orthogonal contributions; (b) the no-fourth-mode decision with its load-bearing reason — mode routing IS the authority grant (cites §Load configuration), and convention inventory has no mode-distinctive workflow; (c) the soft-trigger decision with the cost-asymmetry rationale (un-recorded session costs one pass; auto-scan costs every polish a surprise); (d) the permanence-ordered lifecycle ladder and its parallel to theory-modeling's per-task ledger → PLAN.md promotion (cites `theory-modeling/SKILL.md §Documentation and handoff`); (e) the deliberate exclusions (detection logic, scanning procedure, math notation, capitalization, page-layout macros). Does not restate the Preserve-substance-polish-prose principle, mode-routing rationale, or audience-awareness entry.
- [x] **Step 2: Trail to deleted feedback memory.** Omitted — no `skills/writing/feedback_*` file exists and `git log --diff-filter=D` shows no deletion of one related to this work. The four §Decisions entries were elicited inline during planning, not via a feedback note. PLAN.md Step 2 explicitly permits omission in this case.
- [x] **Step 3: DRY / Necessity check on the new entry.** Walked all five paragraphs against repo `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action`. All kept; no deletions. Each paragraph carries design rationale (parallel-to-other-domains, no-mode-distinctive-workflow, cost-asymmetry, parallel promotion pattern, gap-vs-baseline-competence) rather than restating SKILL.md content. The boundary line and lifecycle ladder appear in both SKILL.md and the contributor entry — same SKILL.md / CLAUDE.md rule-vs-why split established by the Audience-awareness and Preserve-substance-polish-prose entries, not a DRY violation. Pointer style is used everywhere a rule is named; the contributor entry adds the load-bearing reason against re-litigation.
- [x] **Step 4: Commit.** Stage only `skills/writing/CLAUDE.md` plus PLAN.md / RESULTS.md updates. Atomic commit titled `skills: record Project Conventions design decisions in writing CLAUDE.md`.
