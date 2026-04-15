# superRA Plugin Restructure Plan

> **For agentic workers:** this is a PLUGIN META-REFACTOR — the "analysis" is the superRA plugin itself, not a data analysis. The domain skill `superRA:econ-data-analysis` applies only when tasks touch data-analysis content; most tasks here are skill-file rewrites. Use `superRA:execution-workflow` to coordinate. Steps use checkbox (`- [ ]`) syntax.

**Objective:** Make `execution-workflow` domain-agnostic; share the gating/review checklist between implementer (self-check) and reviewer (verification) by keeping it inline in `econ-data-analysis/SKILL.md` main body; standardize dispatch-prompt language across all workflow skills so the prompt carries only steering on top of the agent's standard protocol.

**Methodology:** Phased commits on `refactor/workflow-domain-split`. Each commit leaves repo in a working state (structural-invariants green). PR #1 updates on push.

**Data Inventory:** N/A — plugin meta-refactor. No datasets.

**Output:** Rewritten skill / agent / workflow files. Updated `tests/structural-invariants.sh`. New `RELEASE-NOTES.md` entry.

**Pipeline:** `bash tests/structural-invariants.sh`.

**Background plan document:** `/Users/zhiyufu/.claude/plans/agile-orbiting-star.md` carries the full design rationale. This PLAN.md is the task-tracker.

---

## Decisions

> **User decision (2026-04-15):** default to one comprehensive review pass per task; reviewer walks the full checklist even on gating failure and returns `CONDITIONAL APPROVE` (gating items must be fixed; downstream verified and contingent on gating fix not invalidating). Rationale: reviewer dispatches are costly; re-review on gating fix becomes narrow (verify the fix + downstream still holds).

> **User decision (2026-04-15):** shared gating lives in `econ-data-analysis/SKILL.md` main body, NOT as separate `implementation-review.md` / `integration-review.md` references. Single source of truth; no possibility of divergence between what implementer self-checks and what reviewer verifies.

> **User decision (2026-04-15):** dispatch prompts use the prefix "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …" so agents always treat the standard workflow (from agent files) as in effect, and the dispatch prompt is ADDITIONAL steering on top. Same protocol applies across every workflow skill that dispatches agents.

---

## Task 1: Standardize Dispatch-Prompt Protocol Across All Workflow Skills

**Review status:** APPROVED

**Objective:** Rewrite every dispatch template in the plugin so it opens with the language

> "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, ..."

The `Additionally, ...` tail carries only steering — focus areas, prior-round adjudication, warnings, non-default skill/reference overrides. The dispatch prompt NEVER repeats (a) the standard protocol that lives in `agents/implementer.md` / `agents/reviewer.md`, (b) PLAN.md task content (the agent reads it), or (c) domain-skill checklist content (the agent walks it per their Before-You-Start).

**Files the dispatcher touches:**

- `skills/execution-workflow/SKILL.md` — per-task implementer + reviewer dispatch templates (currently in §"Dispatch Templates" around L150-L200).
- `skills/integration-workflow/SKILL.md` — Stage 1 drift-test-creator + drift-test-reviewer dispatches; Stage 2 integration-reviewer + refactorer dispatches; Step 3 doc-writer + doc-reviewer dispatches.
- `skills/merge-workflow/SKILL.md` — any dispatch templates.
- `skills/semantic-merge/SKILL.md` — Tier 2 merge-proposer + merge-reviewer dispatches; Tier 3 same.
- `skills/agent-orchestration/SKILL.md` — team-recipe dispatch patterns.

**Steps:**

- [x] **Step 1: Describe — audit every dispatch template in the plugin.** Grepped `Agent(subagent_type:` across `skills/`. Found 16 dispatch templates across 5 files: `execution-workflow/SKILL.md` (3), `integration-workflow/SKILL.md` (6), `merge-workflow/SKILL.md` (2), `semantic-merge/SKILL.md` (3), `refactor-and-integrate/SKILL.md` (2 illustrative). Legacy over-specification observed: `Work from:` + `Counterpart:` in `execution-workflow`'s three primary templates; free-form `Note:` fields in `merge-workflow` post-merge reviewer + post-merge refactorer and in `semantic-merge` Tier 3. `using-superRA/references/codex-tools.md` contains one mention inside a harness-mapping table (prose context, not a dispatch template) — left alone.

- [x] **Step 2: Analyze — rewrite each template to the new canonical shape.** Template form:

  ```
  Agent(subagent_type: "superRA:<implementer|reviewer>"):
    # --- REQUIRED FIELDS FIRST (dispatch cannot function without them) ---
    Stage: <stage-name>
    Task: <PLAN.md pointer or git range>
    [Git range: <BASE>..<HEAD>]     # for review stages
    [Skills: <extras>]              # only if non-default
    [References: <extras>]          # only if non-default
    # --- THEN the standard-workflow anchor + optional steering ---
    Additionally: Follow the standard stage-relevant workflow and load
      relevant skills and documents to proceed. Additionally,
      <optional one-or-two-sentence steering — focus area, prior-round
      adjudication, warning, anything non-default>.
  ```

  **Ordering rule (non-negotiable):** required identifying information (Stage, Task, Git range, Skills/References overrides) comes **first** — the agent needs it to load the right context. The `Additionally:` block comes **last** — it anchors "standard workflow is in effect" plus any free-form steering on top. Do NOT invert the order (Additionally-block on top, required fields below) — that buries required information after prose and invites the agent to miss it.

  - Drop `Work from:` lines (subagent runs in cwd by default).
  - Drop `Counterpart:` lines outside explicit Agent Teams subsections.
  - Drop any preamble that restates standard protocol, PLAN.md content, or checklist items the agent already reads.
  - The prefix "Follow the standard stage-relevant workflow..." is literal and common across every template. This is the anchor that tells the agent: your standard Before-You-Start + stage-reference-auto-load is in effect; what follows is additions on top.

- [x] **Step 3: Validate — verify and commit.**
  - Grep: no dispatch template in `skills/` is missing the "Follow the standard stage-relevant workflow..." prefix.
  - Grep: no dispatch template retains `Work from:` (outside explicit worktree-setup prose) or `Counterpart:` (outside Agent Teams subsections).
  - `bash tests/structural-invariants.sh` passes.
  - Add one new assertion to `structural-invariants.sh`: every dispatch template in the live surface contains "Follow the standard stage-relevant workflow" (use a grep count >= N where N = number of templates).
  - Update RELEASE-NOTES.md top entry to note the dispatch-protocol standardization.
  - Atomic commit: `refactor(dispatch): standardize dispatch-prompt prefix across all workflow skills`.

**Out of scope for this task (handled in follow-on tasks 2–6 below).**

---

## Task 2: Integrate §Review & Self-Check Discipline into `econ-data-analysis/SKILL.md`

**Review status:** APPROVED

**Objective:** Add a new top-level section `## Review & Self-Check Discipline — shared gating for implementer and reviewer` to the main body of `skills/econ-data-analysis/SKILL.md`. Content uses `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers so implementer self-check and reviewer verification walk the exact same list. Encode the CONDITIONAL APPROVE verdict protocol (reviewer walks the entire checklist even on gating failure; returns APPROVE / REVISE / CONDITIONAL APPROVE). Single source of truth — no new reference files.

**Files touched:**

- `skills/econ-data-analysis/SKILL.md` — add `## Review & Self-Check Discipline` after the three concurrent disciplines (after Validate §Sensitivity analysis, before Pitfalls). Convert the existing `## Verification Checklist` into a one-line pointer to the new section.

**Steps:**

- [x] **Step 1: Describe — locate insertion point and audit existing content.** Read SKILL.md end-to-end; identify where the new section lands (after Validate, before Pitfalls). Catalog the items already present elsewhere in the file that should be cross-referenced (not duplicated) from the new section: Iron Law, Describe panel structure / variable diagnostics / merge-key inspection, Analyze row-count logging, Validate sanity checks / multi-source / sensitivity, Pitfalls §Merges, the `script-to-notebook` pointer, `integrate-drift-tests.md`, `data-robustness-checklist.md`. Confirm the existing `## Verification Checklist` content is fully subsumed by the new section.

- [x] **Step 2: Analyze — write the new section.** Drafted with this shape (preamble + verdict protocol + six sub-sections):

  - **Preamble.** Single source of truth. Implementer walks as pre-handoff self-check; reviewer walks as verification criteria. Markers: `[GATING]` = load-bearing non-negotiables (failure blocks unconditional APPROVE); `[STANDARD]` = required, becomes a REVISE finding if missing; `[ADVISORY]` = best-practice, reviewer MAY flag as MINOR.

  - **Reviewer verdict protocol (CONDITIONAL APPROVE).** Walk the entire section top to bottom — do NOT halt on gating failure (reviewer dispatches are costly). Three verdicts: `APPROVE` (no findings), `REVISE` (only `[STANDARD]` items failed), `CONDITIONAL APPROVE` (one or more `[GATING]` items failed; reviewer walked downstream anyway and those look correct *conditional on the gating fix not invalidating them*). On CONDITIONAL, the re-dispatched reviewer's second pass is narrow: verify the gating fix + verify cited downstream items still hold; if both, CONDITIONAL → unconditional APPROVE.

  - **§ Gating: the Iron Law applied per step**
    - `[GATING]` Every input described before first transformation (panel structure, variable diagnostics, missing values). See §Describe.
    - `[GATING]` Every sample-changing operation logs before/after row counts. See §Analyze.
    - `[GATING]` Every merge describes join keys on both sides before execution. See §Pitfalls §Merges.

  - **§ Implementation standards**
    - `[STANDARD]` Each step matches PLAN.md spec.
    - `[STANDARD]` Analysis scripts follow notebook-compatible format per `superRA:script-to-notebook`.
    - `[STANDARD]` Major decisions (filter threshold, join type, variable definition) carry a markdown-cell justification; minor decisions carry an inline comment.
    - `[STANDARD]` Outputs (tables, figures) generated from committed code, not ad-hoc REPL.

  - **§ Validation completeness**
    - `[STANDARD]` Distribution re-check after each major transformation; compare pre/post.
    - `[STANDARD]` Economic sense: magnitudes plausible, signs as expected, published benchmarks where applicable.
    - `[STANDARD]` When PLAN.md header has Expected Results / Hypotheses, compare findings and flag divergences.
    - `[ADVISORY]` Sensitivity analysis on robustness-sensitive tasks per `references/data-robustness-checklist.md`.

  - **§ Documentation and handoff**
    - `[GATING]` RESULTS.md updated in place for the task's section per `superRA:handoff-doc`.
    - `[STANDARD]` Markdown cells explain what/why.
    - `[STANDARD]` Figures saved under `results_attachments/` and embedded via relative paths.
    - `[STANDARD]` No dangling TODO / placeholder strings.

  - **§ Refactor integrity (applies during `refactoring` and `integration review` stages)**
    - `[GATING]` All describe steps preserved (or explicitly replaced by upstream-validated diagnostics).
    - `[GATING]` All row-count prints preserved at sample-changing operations.
    - `[GATING]` All validation checks preserved.
    - `[GATING]` Drift tests (where they exist) pass post-refactor; failures adjudicated per `references/integrate-drift-tests.md`, never silently re-expected.
    - `[STANDARD]` Variable definitions unchanged, or the change is documented and justified.
    - `[STANDARD]` Sample construction unchanged, or documented.
    - `[STANDARD]` Naming follows nearest module-level `CLAUDE.md` / `AGENTS.md` / `README.md` conventions.
    - `[STANDARD]` Utility functions reused; no reinvented helpers.

  - **§ Completion verification (applies at `execution-workflow` Step 3)**
    - `[GATING]` All code committed.
    - `[GATING]` Multi-script pipeline runs end-to-end if the plan declares one.
    - `[GATING]` Outputs exist and were generated from committed code (not ad-hoc REPL).
    - `[STANDARD]` PLAN.md and RESULTS.md current.
    - `[STANDARD]` Deferred MINORs resolved or documented in RESULTS.md as accepted limitations.

- [x] **Step 3: Validate — consolidate, test, commit.**
  - Replace `## Verification Checklist` section (L311-L337 current) with a one-liner: "For pre-handoff self-check and reviewer verification, see §Review & Self-Check Discipline above."
  - Add one sentence under `## Stage-Scoped References` noting: "The §Review & Self-Check Discipline section below loads with the main body at every stage — it is the shared gating both implementer and reviewer walk."
  - Run `bash tests/structural-invariants.sh` — must stay green.
  - Add new assertions in `tests/structural-invariants.sh`:
    - `## Review & Self-Check Discipline` heading exists in `econ-data-analysis/SKILL.md`.
    - `[GATING]` marker count ≥ 8 in that file.
    - `CONDITIONAL APPROVE` string appears in that file (verdict protocol encoded).
    - No file `implementation-review.md` or `integration-review.md` under `skills/econ-data-analysis/references/` (sanity check on shared-gating decision).
  - Update RELEASE-NOTES.md top (Unreleased) entry to note the §Review integration.
  - Atomic commit: `feat(econ-data-analysis): add §Review & Self-Check Discipline with shared gating markers`.

---

## Task 3: Rewrite `execution-workflow/SKILL.md` for Domain Agnosticism

**Review status:** REVISE

> **Review notes:**
> 1. [MINOR] Residual data-flavored examples in `## Handling Implementer Status` (`skills/execution-workflow/SKILL.md:326,328,331-332`). `DONE_WITH_CONCERNS` cites "data quality or unexpected findings"; `NEEDS_CONTEXT` says "Provide missing data documentation, upstream results, or methodology details"; `BLOCKED` enumerates "Data not available" and "Data quality too poor". Task 3's stated Objective is "speak only in domain-neutral terms" and the dispatch brief asks to flag residual data-flavored phrasing. This section was not in the Task 3 Files-touched list, so it is out of spec scope, but the examples here are the most domain-neutralizable residuals in the file. Suggest rewriting the `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` lines in domain-neutral terms and converting `BLOCKED` items 1 and 2 to "Required input not available" / "Input quality too poor" (or similar). Alternatively, leave with an "(for data analysis: ...)" gloss consistent with the rest of the file.
> 2. [MINOR] `## Autonomy and Stop Points` (`skills/execution-workflow/SKILL.md:352-353`) carries heavily data-flavored illustrative examples: "Data description reveals unexpected issues (wrong magnitudes, high missingness), merge produces an unexpected row count change, validation fails against economic intuition, ... required data source unavailable" and "sensitivity failure of unclear economic significance, sample/variable definition call". Not in spec's Files-touched list, but same domain-neutrality objective applies. Either generalize (e.g., "unexpected input-quality issues, unexpected scope change in a transformation, validation fails against domain expectation") or wrap in an "(data-analysis example: ...)" gloss.
> 3. [MINOR] Red Flags list (`skills/execution-workflow/SKILL.md:379,382`): "Dispatch multiple implementers in parallel on the same data (conflicts)" and "Ignore implementer data quality or methodology concerns". Spec explicitly lists Red Flags (L404–L424 in old file) as a Files-touched block with instruction "scrub remaining 'data integrity' / 'implementation review' references" — the scrub was done but "data" examples in bullet text remain. Suggest "on the same files" / "on the same working tree" for L379 and "input-quality or methodology concerns" for L382 to match the domain-neutral framing used elsewhere.
> 4. [MINOR] Step 1 orchestrator load (`skills/execution-workflow/SKILL.md:146`) contains the inline auto-load hardcoded at orchestrator level: "For data-analysis plans (importing, cleaning, merging, constructing variables, regressions, figures), load `superRA:econ-data-analysis` and `superRA:script-to-notebook`." This is the orchestrator-side counterpart to the dispatch-template preamble that Task 3 Step 2 removed from subagents. The brief item (e) specifically called for removing the hardcoded auto-load preamble from dispatch templates; the orchestrator-side load is not in scope of (e) strictly, but it is the same smell in a different location and reads in tension with "domain-agnostic". Flagging for orchestrator adjudication — the step's intent (orchestrator needs the domain skill loaded for adjudication) is sound, so perhaps the right fix is reframing as "Load the active domain skill(s) PLAN.md identifies. For data analysis, this is `superRA:econ-data-analysis` + `superRA:script-to-notebook`." Low confidence this is worth changing.

**Objective:** Make `execution-workflow` speak only in domain-neutral terms. Collapse two-stage review into one comprehensive pass; rewrite Step 3 as a domain-parametric skeleton that points at the active domain skill's §Completion verification; rewrite the completion menu and Step 4 language; delete the data-flavored "Sensitivity Analysis Tasks" and hard-coded auto-loads; update dispatch templates to the new canonical form with renamed stages (`implementation`, `implementation review`).

**Depends on:** Task 2 must APPROVE first so the workflow can cite `econ-data-analysis/SKILL.md §Review & Self-Check Discipline`.

**Files touched:**

- `skills/execution-workflow/SKILL.md` — review protocol (L8-L14, L46-L56, L82-L103), Step 2 sub-steps (L157-L167), dispatch templates (L169-L210), Step 3 (L247-L271), Step 4 (L273-L306), Review Status table (L308-L331), Sensitivity Analysis + Model Selection sections (L333-L351), Red Flags (L404-L424), Integration table (L425-L435).

**Steps:**

- [x] **Step 1: Describe — grep existing terminology.** Audited the live file: `data integrity` / `two-stage review` / `REVISE (data integrity)` / `REVISE (implementation)` appeared throughout the intro (L8–L14), Step 2 sub-steps (L157–L167), three dispatch templates (L169–L210), Review Status table (L308–L319), Red Flags (L404–L424), and the `Note: Data integrity` interim-checkpoint clause at L331. `analysis task` appeared in the implementer dispatch template. `## Sensitivity Analysis Tasks` at L333–L341 and `## Model Selection` at L343–L351 were data-flavored. Dispatch-template preamble at L171 hardcoded the `superRA:econ-data-analysis` + `superRA:script-to-notebook` auto-loads that belong in the agent Stage tables per Task 4.

- [x] **Step 2: Analyze — rewrite.**
  - **Review protocol (one pass):** replace the "two-stage review (data integrity then implementation correctness)" narrative with "one comprehensive review pass per task. The reviewer walks the active domain skill's §Review & Self-Check Discipline top to bottom and returns APPROVE / REVISE / CONDITIONAL APPROVE." Orchestrator MAY dispatch a second reviewer via steering when the CONDITIONAL's gating fix is substantial enough to cast doubt on downstream items — document this as documented flexibility, not default.
  - **Process flowchart:** replace the two-node data-integrity → implementation dispatch chain with one "Dispatch reviewer (implementation review)" node whose verdict branch includes the CONDITIONAL APPROVE path (narrow re-review).
  - **Review Status table:** collapse `REVISE (data integrity)` + `REVISE (implementation)` into `REVISE`; add `CONDITIONAL APPROVE` row. Actions re-pointed to the domain skill's §Review.
  - **Per-task execution steps (L157-L167):** rewrite sub-steps 3+4 into a single "Dispatch reviewer" step with REVISE / CONDITIONAL APPROVE / APPROVE branches.
  - **Dispatch templates (L169-L210):** rename stages per D-Stage-1 (`analysis task` → `implementation`, collapse `data integrity` + `implementation` reviewers → `implementation review`). Keep the canonical prefix from Task 1 (Additionally-anchor last; Stage/Task/Git range first). Drop the hardcoded "For every analysis-touching stage … auto-loads `superRA:econ-data-analysis` and `superRA:script-to-notebook`" preamble — agent files handle stage-based auto-load per Task 4's Stage table.
  - **Step 3 (Verify Pipeline and Reproducibility):** replace specific pipeline-runs / outputs-exist checks with a short orchestrator skeleton: (1) All code committed, (2) PLAN.md current, (3) RESULTS.md current, (4) Domain completion verification — "walk the active domain skill's §Completion Verification `[GATING]` items; for data analysis: `econ-data-analysis/SKILL.md` §Review §Completion verification," (5) Deferred MINORs resolved.
  - **Step 4 / completion menu:** "Analysis complete and reproducible" → "Work complete and verified." Option descriptions stay domain-neutral.
  - **Delete `## Sensitivity Analysis Tasks`** (L333-L341) — content is already in `econ-data-analysis/SKILL.md` §Validate §Sensitivity analysis and in `references/data-robustness-checklist.md`.
  - **Replace `## Model Selection`** (L343-L351) with one paragraph: "Use the least capable model that handles the task; reviewers use the most capable available model. Domain-specific complexity examples live in the domain skill, not here."
  - **Red Flags + Integration table:** scrub remaining "data integrity" / "implementation review" references. Keep the list as Red Flags for the one-pass flow.
  - **Integration table L425-L435:** "`superRA:econ-data-analysis` — REQUIRED: Data discipline all agents must follow" → "the active domain skill (for data analysis: `superRA:econ-data-analysis`) — REQUIRED: domain discipline all agents follow at dispatch-time auto-load per `agents/implementer.md` / `agents/reviewer.md` Stage tables."

- [x] **Step 3: Validate — grep checks + commit.**
  - Greps confirmed: `data integrity|two-stage review|REVISE \(data integrity\)|REVISE \(implementation\)` absent; `^## Sensitivity Analysis Tasks` absent; `CONDITIONAL APPROVE` present (3+ hits). `## Model Selection` retained as a one-paragraph section per task spec (the old data-flavored body is gone; the heading stays).
  - `tests/structural-invariants.sh` gains assertion block #12 with three new checks: two-stage-review phrasing absent, `## Sensitivity Analysis Tasks` heading absent, `CONDITIONAL APPROVE` present. Old block #12 (README Why-superRA?) renumbered to #13. Full run: 29 PASS, 2 known WARN, 0 FAIL.
  - Atomic commit to follow: `refactor(execution-workflow): one-pass review, domain-parametric Step 3, generic completion menu`.

---

## Task 4: Agent-File Stage Tables + Dispatch-Prompt Contract + Self-Review Walk

**Review status:** (not started)

**Objective:** Add an authoritative Stage → reference-loads table in both `agents/implementer.md` and `agents/reviewer.md`. Add a "What the dispatch prompt carries — and doesn't" contract section near the top. Extend the implementer's Self-Review to walk the domain skill's §Review & Self-Check Discipline before returning DONE. Extend the reviewer's Review Protocol with the CONDITIONAL APPROVE verdict.

**Depends on:** Tasks 2 and 3 must APPROVE first.

**Files touched:**

- `agents/implementer.md` — add Stage table; add dispatch-prompt contract section; extend §Self-Review Before Reporting with §Review walk.
- `agents/reviewer.md` — add Stage table; add dispatch-prompt contract section; extend §Verdict with CONDITIONAL APPROVE; extend §How You Write a Review with CONDITIONAL APPROVE mechanics (state gating item(s) that failed + "downstream reviewed, contingent on gating fix").

**Steps:**

- [ ] **Step 1: Describe — audit current stage references in agent files.** Both files currently carry prose under "Before You Start" step 2 describing stage-scoped loading. Identify the prose lines to replace with the table.

- [ ] **Step 2: Analyze — write the Stage table and dispatch contract.**

  Stage table (same in both agent files, adapted for implementer vs reviewer wording):

  | `Stage:` value | Domain skill (auto-loaded) | Stage-scoped reference(s) |
  |---|---|---|
  | `implementation` | `econ-data-analysis` + `script-to-notebook` | main body §Review & Self-Check Discipline |
  | `implementation review` | same | same |
  | `refactoring` | same | main body §Refactor integrity; plus `integrate-drift-tests.md` if drift tests exist |
  | `integration review` | same | same |
  | `drift test creation` | same + `refactor-and-integrate` | `integrate-drift-tests.md` + `drift-test-quality.md` |
  | `drift test review` | same + `refactor-and-integrate` | same |
  | `merge proposer` | same + `refactor-and-integrate` | `merge-quality.md` |
  | `merge review` | same + `refactor-and-integrate` | `merge-quality.md` |
  | `doc writer` | `report-in-markdown` | `baseline-io.md` + `rich-content.md` + `final-form.md` |
  | `doc reviewer` | `report-in-markdown` | `final-form.md` |
  | planning-phase reviewer | `econ-data-analysis` | `planning.md` |

  Dispatch-prompt contract section (both agents):

  > **What the dispatch prompt carries — and doesn't.** The dispatcher uses the Stage table above to choose which references auto-load. Task content lives in `PLAN.md` / `RESULTS.md`, which you read directly (see Before You Start). Standard protocol — how you load handoff docs, walk module-level guidance, self-review, annotate review items, report — lives in this file and is always in effect.
  >
  > The dispatch prompt carries only the Stage, a task pointer, a git range (if reviewing), and an optional `Additionally:` steering line. If the dispatch paraphrases `PLAN.md`, passes a review checklist, or repeats standard protocol, treat that as over-specification and use your standard protocol + the authoritative sources it points at.

  Implementer §Self-Review extension: "Before returning DONE, walk the domain skill's §Review & Self-Check Discipline yourself. Every `[GATING]` item must pass — a gating failure is a fix-first, not a handoff. Every `[STANDARD]` item should pass; if not, document the exception in RESULTS.md so the reviewer is not surprised."

  Reviewer §Verdict extension (CONDITIONAL APPROVE): three-verdict protocol. On CONDITIONAL APPROVE, review-notes blockquote lists the failed `[GATING]` item(s) first, then notes "downstream items reviewed and currently correct; approval contingent on the gating fix not changing downstream results." Set `**Review status:** CONDITIONAL APPROVE`. On re-review after gating fix: verify (a) the gating fix is correct, (b) cited downstream items still hold; if both, delete the blockquote and set `**Review status:** APPROVED`.

- [ ] **Step 3: Validate — structural invariants + commit.**
  - New invariants: both agent files contain a Stage table (markdown table with "Stage" header row + rows for `implementation`, `implementation review`, `refactoring`, `integration review`). Both files contain the dispatch-prompt contract phrase ("What the dispatch prompt carries — and doesn't"). `agents/reviewer.md` contains `CONDITIONAL APPROVE`.
  - Atomic commit: `feat(agents): Stage tables + dispatch-prompt contract + CONDITIONAL APPROVE verdict`.

---

## Task 5: Companion Workflow Skills — Light Audit

**Review status:** (not started)

**Objective:** Update `integration-workflow/SKILL.md` Stage 2 to cite the domain skill's §Refactor integrity. Light grep-audit of `merge-workflow`, `semantic-merge`, `planning-workflow` for residual "data integrity" / "two-stage review" phrasing. Add a top-of-file pointer in `refactor-and-integrate/references/codebase-integration.md` naming the domain skill's §Refactor integrity as primary for data-analysis work.

**Depends on:** Tasks 2–4 APPROVE.

**Files touched:**

- `skills/integration-workflow/SKILL.md` — Stage 2 domain-reference pointer.
- `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/planning-workflow/SKILL.md` — scrub data-flavored residuals.
- `skills/refactor-and-integrate/references/codebase-integration.md` — top-of-file pointer.

**Steps:**

- [ ] **Step 1:** Grep `data integrity|two-stage review|data-integrity reviewer` across those four workflow skill files. Catalog hits.
- [ ] **Step 2:** Rewrite each hit into domain-parametric language. Update integration-workflow Stage 2 reference. Add the codebase-integration.md preamble pointer.
- [ ] **Step 3:** Grep proves no residuals. Atomic commit: `refactor(workflows): domain-parametric references and residual cleanup`.

---

## Task 6: Structural Invariants + RELEASE-NOTES Finalization

**Review status:** (not started)

**Objective:** Consolidate all new invariants added across Tasks 2–5 into a coherent section of `tests/structural-invariants.sh`; expand the top (Unreleased) entry of `RELEASE-NOTES.md` to describe the full restructure (DAV rename + dispatch standardization + §Review integration + execution-workflow domain agnosticism + Stage tables + CONDITIONAL APPROVE + companion-workflow audit).

**Depends on:** Tasks 2–5 APPROVE.

**Files touched:**

- `tests/structural-invariants.sh` — verify all new assertions from Tasks 2–4 are present; add any missing one.
- `RELEASE-NOTES.md` — expand Unreleased.

**Steps:**

- [ ] **Step 1:** Audit structural-invariants.sh for completeness; add missing assertions.
- [ ] **Step 2:** Rewrite the top RELEASE-NOTES entry to cover all restructure pieces.
- [ ] **Step 3:** Run the test suite — must exit 0 with the existing ≤2 WARN. Atomic commit: `test+docs: finalize invariants and release notes for workflow-domain-split restructure`.
