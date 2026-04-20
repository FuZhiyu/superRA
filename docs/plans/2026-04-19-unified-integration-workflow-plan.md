# Unified Integration-Workflow Refactor

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This refactor edits skill files — every implementer and reviewer dispatch MUST additionally load `document-skills:skill-creator` and apply its conciseness, progressive-disclosure, and one-source-of-truth discipline. Preserve carefully-tuned content (Red Flags tables, rationalization lists, RA-framing language) per `/CLAUDE.md §Skill Changes`. Steps use checkbox (`- [ ]`) syntax.

**Objective:** Unify `integration-workflow` + `merge-workflow` into a single iterative INTEGRATE phase (Phases A–D); rebuild `refactor-and-integrate` as a gated checklist shared by implementer + reviewer (`[BLOCKING]` / `[ADVISORY]` markers, minimum-net-diff-to-merge-base as the top blocking item); refactor all dispatch prompts to the canonical `agent-orchestration §Dispatch Templates` shape; delete `merge-workflow`; retain `semantic-merge` as standalone utility.

**Methodology:** This is a skill-design refactor. No data, no pipeline. Work is in superRA skill files and cross-cutting docs (README, CATEGORIES, RELEASE-NOTES, CLAUDE.md). Each task block defines one coherent sub-change to the skill graph. Verification is a skill-graph consistency sweep + an end-to-end dry-run on a throwaway worktree.

**Conventions:** (to be populated as the refactor progresses — emergent naming / section titles / stage-label conventions land here)

**Output:** Modified skills under `/skills/`, deleted `skills/merge-workflow/`, updated top-level docs (`README.md`, `RELEASE-NOTES.md`, `CLAUDE.md`), updated `skills/CATEGORIES.md`. No code artifacts, no data outputs.

**Expected Results:** (a) boundary confusion between integration, merge, and semantic-merge eliminated; (b) minimum-net-diff principle is load-bearing in refactor checklist and verified by implementer self-check + reviewer walk; (c) dispatch prompts carry no content duplicated from loaded skills; (d) mid-integration task restructuring flows through existing `planning-workflow §Changing Plans` with only minimal additions.

**Pipeline:** N/A (skill refactor, not analysis).

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on this plan (2026-04-19; re-approved after §Changing Plans protocol on 2026-04-19 for recon-as-reviewer architecture and shortcut axes)
- [x] **Execution complete** — Task 8 reviewer APPROVED (2026-04-19); all 8 tasks `**Review status:** APPROVED`
- [x] **Drift tests created** — N/A for skill refactor; substitute satisfied by Task 7 end-to-end dry-run + skill-graph consistency sweep (2026-04-19)
- [x] **Refactored** — Phase B re-entry verify reviewer APPROVED (2026-04-19) cumulative diff post-semantic-merge (Tier 2 absorption of origin/main 9831255..6d4a0ea into merge commit `712602e`); all 8 tasks `**Integration status:** APPROVED`
- [ ] **Docs finalized** — rolled back 2026-04-19 by §Changing Plans; matured RESULTS.md needs a Task 8 section + fresh doc-review pass
- [ ] **Merged** — rolled back 2026-04-19 by §Changing Plans; PR #5 description and branch both require the Task 8 changes before merge

---

## Decisions

> **User decision (2026-04-19):** Delete `skills/merge-workflow/` entirely and note the deprecation in `RELEASE-NOTES.md`. No redirect stub.
> **Question asked:** How should the ex-merge-workflow content be retired?

> **User decision (2026-04-19):** Use the existing `planning-workflow §Changing Plans` protocol as-is for mid-integration plan changes. Only minimal additions — one pointer bullet acknowledging the INTEGRATE-phase trigger and the orchestrator-authors / researcher-decides ownership rule.
> **Question asked:** Where should the mid-integration plan-change trigger live structurally?
> **Rationale:** Existing protocol already covers it; one source of truth; minimize churn.

> **User decision (2026-04-19):** Phase B (Integrate — sync + refactor) is re-enterable multiple times within a single integration pass. Supports the explicitly iterative design.
> **Question asked:** Phase B cadence — once per pass or iterative?

> **User decision (2026-04-19):** Collapse the former Phase B (sync) and Phase C (refactor) into a single unified Phase B ("Integrate — sync + refactor"). Minimum-net-diff principle demands merge and refactor target the same final state in one two-commit structure. Internal structure: recon reviewer → batched user decisions → unified implementer (two-commit merge) → verify reviewer. Orchestrator split safety-valve when integration map is large.
> **Question asked:** Should B (sync) and C (refactor) be separate stages or collapsed?
> **Rationale:** Two separate diffs against merge-base violate minimum-net-diff; collapsed flow produces one coherent diff.

> **User decision (2026-04-19):** Add an implementer self-check step before every commit: run `git diff <merge-base>..HEAD` and review the cumulative diff against the minimum-net-diff rule; revert or re-justify any hunk not tied to the integration map or gated-checklist items. Walked by the verify reviewer as part of `refactor-and-integrate`.
> **Question asked:** Should there be an explicit self-check for minimum-change discipline?

> **User decision (2026-04-19):** In `refactor-and-integrate`, SKILL.md body highlights principles only — tuned content (Red Flags, Tier 3 escalation, rationalization lists, RA-framing) lives **only** in references, which are required loads. Restructure references as how-tos + checklists. No duplication between body and references.
> **Question asked:** How to de-duplicate tuned content between SKILL.md body and references?
> **Rationale:** DRY / one-source-of-truth; mirrored content in Task 1's first pass would drift on future edits.

> **User decision (2026-04-19):** Phase B recon is a reviewer following the standard reviewer protocol. Its specialty is also running `semantic-merge` to produce a Tier classification. Recon output is distributed across PLAN.md task blocks as per-task integration review-notes blockquotes with `[BLOCKING]` / `[ADVISORY]` items — not a monolithic return payload. Orchestrator reads PLAN.md: any task with a new integration review-notes blockquote gets its `Integration status:` flipped to `REVISE`; tasks without annotations stay `APPROVED`. Tier classification is logged as a one-line entry under §Decisions for the integration pass.
> **Question asked:** How does recon communicate the integration map?
> **Rationale:** All important communication goes through handoff doc, not return text. Recon is already a reviewer; following the standard reviewer annotation protocol means one source of truth and no custom return contract.

> **User decision (2026-04-19):** Tier-1 / refactor-path shortcut axes are independent.
> - **Tier classification** (from recon's `semantic-merge` run) gates the **merge path**. Tier 1 → fast-forward merge only (Commit 1 = `git merge --ff-only`); follow-up agents do not load `semantic-merge`. Tier 2/3 → `semantic-merge` loaded by follow-up agents for proper merge resolution.
> - **Per-task integration annotations** gate the **refactor path**. Zero annotations across all APPROVED-integration tasks → skip unified implementer + verify reviewer entirely. Non-zero → dispatch them, scoped to the annotated task list.
> - Combined: Tier 1 + zero annotations → Phase B = fast-forward only, terminates. Tier 1 + annotations → fast-forward + refactor-only implementer + verify reviewer (no semantic-merge load). Tier 2/3 regardless of annotations → full flow.
> **Question asked:** How do Tier and annotation-count gates combine into shortcuts?
> **Rationale:** Decomposing the single "Tier-1 shortcut" into two independent axes prevents the class of bugs where one axis is clean but the other isn't.

> **User decision (2026-04-19):** Refactor implementer and verify reviewer operate only on tasks whose `Integration status` is unset or `REVISE`. `APPROVED`-integration tasks are out of scope — do not walk their code, do not touch their output files except through legitimate merge resolution. Mirrors the existing Review-status DAG cascade rule in `handoff-doc/references/plan-anatomy.md`. The dispatch `Task:` or `Tasks in scope:` field names the explicit list.
> **Question asked:** Do refactorer / verify-reviewer know to skip already-integrated tasks?
> **Rationale:** Without scoping, a second integration pass either redoes work or silently lets reviewer flag already-APPROVED tasks — violates minimum-net-diff.

> **User decision (2026-04-19):** Recon loads `superRA:semantic-merge` via the canonical `Skills:` dispatch field (per `agent-orchestration §Dispatch Templates`) on top of its Stage-default loads. No new Manifest stage required.
> **Question asked:** How does recon get the `semantic-merge` load without adding a new stage?
> **Rationale:** The `Skills:` field is the canonical extra-load mechanism; introducing a new stage for one use case is heavier than needed.

> **User decision (2026-04-19):** Push `refactor/unified-integration` to origin and create a PR against main for review.
> **Question asked:** All 7 tasks APPROVED — merge locally, push+PR, keep as-is, or discard?

> **Integration recon (2026-04-19):** Tier 1 — trivial fast-forward; `origin/main` has not advanced since merge-base `92a685b` (0 commits behind), `git merge-tree` reports no conflicts, branch is 31 commits ahead. Phase B merge path = `git merge --ff-only`; follow-ups do NOT load `semantic-merge`.

> **Integration recon re-entry (2026-04-19, post-Task-8):** Tier 2 — `origin/main` has advanced by 4 commits (session-start hook drop, PR #6) since merge-base `92a685b`; `git merge-tree` reports a real textual conflict in `RELEASE-NOTES.md` (competing "Unreleased" entries — this branch's unified-integration-workflow refactor vs main's session-start hook drop) plus autoresolving `changed in both` hunks on `README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md`, `skills/using-superRA/references/main-agent.md`, `skills/agent-orchestration/references/agent-teams.md`, and a `removed in remote` on `hooks/session-start`. Phase B merge path = `semantic-merge` delegated mode; follow-ups load `superRA:semantic-merge`. Supersedes the prior Tier 1 classification (main had not advanced at the prior pass).

> **Orchestrator decision (2026-04-19):** `RESULTS_DIR` = `docs/plans/`; target filename `2026-04-19-unified-integration-workflow-results.md` per existing repo convention (date-prefixed plan/results pairs alongside historical refactors). No researcher stop needed — convention is unambiguous from `docs/plans/` contents.
> **Question asked:** Where should the matured RESULTS.md land?
> **Rationale:** `docs/plans/` is the established archive for refactor plans and results; filename mirrors sibling entries like `2026-04-16-design-coherence-refactor-results.md`. No figures in this refactor → attachments step is a no-op.

> **Orchestrator decision (2026-04-19):** PLAN.md disposition = Option 1 (relocate alongside matured RESULTS.md at `docs/plans/2026-04-19-unified-integration-workflow-plan.md`). No `results_attachments/` rename needed (no figures). Sibling precedent: `docs/plans/2026-04-16-design-coherence-refactor.md` + `-results.md` pair.
> **Question asked:** How to dispose of PLAN.md?
> **Rationale:** Option 1 is the established repo convention for refactor plan/results pairs; preserves prescriptive history alongside the permanent archive.

> **User decision (2026-04-19, §Changing Plans — post-integration retrospective):** Add Task 8 covering three retrospective refinements surfaced during the end-to-end Phase A–D dogfooding run. All three are documentation-only fixes to skills altered by Tasks 1, 2, 5; none affect Tasks 1–7's code content. Tasks 1–7 retain `**Review status:** APPROVED` + `**Integration status:** APPROVED` per the "untouched tasks retain APPROVED" rule. Workflow Status boxes unchecked: `Execution complete`, `Refactored`, `Docs finalized`, `Merged` (Task 8 unstarted; its output will produce new diff hunks requiring a fresh Phase B recon + verify pass, a matured-doc update, and a PR-body update before re-flipping). `Drift tests created` stays checked (N/A substitute unchanged). Task 8 combines three small edits into one task for proportionality: (a) `plan-anatomy.md:179` state-setter clause + `integration-workflow` Phase B `IMPLEMENTED` beat; (b) `agents/reviewer.md` + `agents/implementer.md` annotation etiquette (preserve task-block boundaries); (c) `integration-workflow` Phase B Step 2 Tier-1 + unchanged-main no-op case.
> **Question asked:** The integration dogfooding surfaced three small documentation-fix items — add as one new Task 8, or close PR #5 and handle in a follow-up?
> **Rationale:** Proportional. The three items are all small doc fixes informed by the very integration run that produced the PR; bundling into PR #5 keeps the retrospective fixes alongside the refactor that motivated them. Separate tasks would multiply Phase B / Phase C re-runs for trivial doc edits.

---

## Project Conventions

Walked at planning time (2026-04-19). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 92a685b): Contributor guide for superRA fork. Four workflow principles (implementer-reviewer pair, handoff docs as auditable record, fast-early-strict-before-merge with semantic-merges, autonomous with human-in-loop). Architectural pattern: lean agents, rich references, flat skills/ layout. DRY with one source of truth per concern — duplication is a code smell. Domain skills own domain discipline; workflow skills own choreography; `agent-orchestration` owns cross-stage orchestration; `refactor-and-integrate` owns generic integration discipline; `handoff-doc` owns handoff-doc mechanics. Extensibility path is adding a new domain skill, not forking workflow skills. Skill edits require reading before changing (tuned content), one problem per commit, commit messages describe the problem not the change, and testing on at least one harness.
- `/AGENTS.md`: (not present at repo root — only subagent role docs under `/agents/`)
- `/README.md`: superRA skill inventory organized by Workflow / Domain / Utility / Meta categories; skill triggers and what-to-load guidance.

### Module-level docs walked
- `/skills/CATEGORIES.md`: Workflow / Domain / Utility / Meta grouping table; must stay in sync with README when skills are added, renamed, or removed.
- `/skills/using-superRA/SKILL.md` §Skill-Load Manifest: authoritative map from `Stage:` value to required skills + stage-scoped references. `Additionally:` dispatch line is the on-demand override pattern for utility skills like `document-skills:skill-creator`.
- `/skills/agent-orchestration/SKILL.md` §Dispatch Templates: canonical dispatch shape (required fields first, `Additionally:` anchor-last with additive signal only, canonical prefix `"Follow the standard stage-relevant workflow and load relevant skills and documents to proceed."`). Banned in dispatch: `Work from:`, restated PLAN.md content, duplicated checklist items.
- `/skills/handoff-doc/references/plan-anatomy.md`: PLAN.md anatomy — Header → `## Workflow Status` → `## Decisions` (when present) → `## Project Conventions` → task blocks. Task-block fields `**Review status:**` / `**Integration status:**` with DAG cascade on re-entry.
- `/skills/econ-data-analysis/SKILL.md` §Three Concurrent Disciplines: reference pattern for gated checklists. `[BLOCKING]` / `[ADVISORY]` markers. Shared by implementer (self-check before handoff) and reviewer (verification). Narrow re-review after REVISE.
- `/skills/planning-workflow/SKILL.md` §Changing Plans: re-entry protocol — confirm intent, log User Decision, inline-edit PLAN.md (prefer modifying existing blocks), update `## Workflow Status` rollup by orchestrator judgment, commit atomically, resume with full drift-test re-run.

### Not walked (not reachable from the planned diff)
- `/hooks/` — no hook changes expected.
- `/skills/econ-data-analysis/**` — domain vertical unaffected by this refactor.
- `/skills/report-in-markdown/**`, `/skills/worktree-data-sync/**`, `/skills/zotero-paper-reader/**` — unaffected utility skills.

---

### Task 1: Rebuild `refactor-and-integrate` as a gated checklist
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A (skill file refactor)
**Input:** `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/drift-test-quality.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/refactor-and-integrate/references/merge-quality.md`, `skills/econ-data-analysis/SKILL.md` §Three Concurrent Disciplines (pattern reference)
**Output:** Rewritten `skills/refactor-and-integrate/SKILL.md` with §Three Concurrent Disciplines-style gated checklist; references preserved only where load-bearing (long-form operational procedures); body walked by both implementer (self-check before commit) and reviewer (verification).

- [x] **Step 1: Describe — read tuned content carefully before touching**

  Read all three references in full. Identify Red Flags tables, rationalization lists, and severity-marked items. Per `/CLAUDE.md §Skill Changes`, this content is tuned through real sessions — paraphrasing is forbidden; relocation must preserve wording.

- [x] **Step 2: Design the gated checklist structure**

  Three disciplines (Drift-Test Integrity, Codebase Integration, Merge Quality) as top-level sections. Each item marked `[BLOCKING]` or `[ADVISORY]`. Top-level item:

  > `[BLOCKING] Minimum net diff to merge base.` Cumulative refactor across all integration rounds touches only what drift-test preservation, convention fit, handoff-doc coherence, and documentation demand. No unrelated cleanup, no speculative abstractions, no "while I'm here" edits. Implementer runs `git diff <merge-base>..HEAD` before each commit and reviews the cumulative diff; reviewer computes the same diff as evidence.

  Include an explicit **Implementer self-check** subsection at the end of the checklist restating the pre-commit `git diff` procedure and what to do when a hunk fails justification (revert or re-justify in the integration map + commit message).

- [x] **Step 3: Fold references into body where load-bearing**

  Long-form operational content stays in references (e.g., Project Doc Audit walk-up algorithm, two-commit merge mechanics). Short checklist items fold into SKILL.md body per `skill-creator §Progressive Disclosure`.

- [x] **Step 4: Validate — confirm implementer + reviewer walk the same file**

  Cross-read with `/agents/implementer.md` and `/agents/reviewer.md`. Both must point at the single gated-checklist section. No parallel review-only document. Commit.

- [x] **Step 5: Add scope-by-Integration-status rule** *(added 2026-04-19 via §Changing Plans)*

  In `skills/refactor-and-integrate/SKILL.md` body, add an explicit principle: *"Refactor implementer and verify reviewer operate only on tasks whose `Integration status` is unset or `REVISE`. `APPROVED`-integration tasks are out of scope — do not walk their code, do not touch their output files except through legitimate merge resolution."* Point at `handoff-doc/references/plan-anatomy.md` for the DAG cascade semantics. Commit.

> **Integration review notes (recon, 2026-04-19):**
> 1. **[ADVISORY]** `skills/refactor-and-integrate/SKILL.md:104` — `§Integration → Used by workflow skills → superRA:integration-workflow` bullet says the workflow dispatches "Phase D post-merge drift-test + integration-review re-runs (`references/codebase-integration.md`) when main advanced." Phase D as authored in `skills/integration-workflow/SKILL.md` does not itself dispatch a drift-test run or integration review; when main advances it re-enters Phase B (line 319), and Phase D Step 3a only verifies the pipeline. The "re-runs when main advanced" phrasing conflates the Phase D→B re-entry with a Phase D dispatch. Minor prose clarity; no `[BLOCKING]` impact on the checklist's load-bearing content. Fix: reword to "Phase D pipeline verification; the Phase D→B re-entry trigger on main advancement then runs the Phase B drift-test + verify-review dispatches again."
>    → implemented: reworded line 104 to name Phase D as pipeline verification and the Phase D→B re-entry trigger as the dispatcher of the re-run (`skills/refactor-and-integrate/SKILL.md:104`)

---

### Task 2: Unify `integration-workflow` — Phases A–D with iterative Phase B
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A
**Input:** current `skills/integration-workflow/SKILL.md`, current `skills/merge-workflow/SKILL.md`, Task 1's rewritten `refactor-and-integrate`, `agent-orchestration §Dispatch Templates`
**Output:** Rewritten `skills/integration-workflow/SKILL.md` covering Phases A (drift-test creation, unchanged), B (Integrate — sync + refactor, three-dispatch internal structure, iterative), C (docs maturation + disposition, unchanged), D (final merge / PR / cleanup, folded in from merge-workflow); all dispatches use canonical shape with no content duplicated from loaded skills; re-entry arrows explicit.

- [x] **Step 1: Draft phase skeleton** — Phases A–D with explicit re-entry arrows (B→A, B→B, C→B, D→B, Anywhere→`planning-workflow §Changing Plans`).

- [x] **Step 2: Write Phase B internal structure** *(rewritten 2026-04-19 via §Changing Plans — see §Decisions, 4 new decisions)*

  Phase B uses standard reviewer/implementer dispatches with two shortcut axes.
  - **Recon reviewer** (Stage: `integration`; **Skills: superRA:semantic-merge** via canonical `Skills:` dispatch field). Follows the standard reviewer protocol: walks every APPROVED-integration task, appends per-task integration review-notes blockquotes with `[BLOCKING]`/`[ADVISORY]` items for any task whose outputs need codebase-fit refactor, drift-test update, handoff-doc coherence, or merge-induced semantic clash. Additionally, runs `semantic-merge` trial-merge + drift tests to produce a **Tier classification**, logged as a one-line User Decision entry in §Decisions for this integration pass.
  - **Orchestrator post-recon actions** (reads PLAN.md after recon commits):
    - For each task carrying a new integration review-notes blockquote → flip `Integration status: REVISE`. Tasks without annotations stay `APPROVED`. Commit the flips atomically.
    - Evaluate the two independent shortcut axes:
      - **Tier 1 + zero annotations** → fast-forward merge only (Commit 1 = `git merge --ff-only`). Phase B terminates. Skip Steps 2b/3/4.
      - **Tier 1 + annotations** → fast-forward merge (Commit 1); dispatch unified implementer + verify reviewer scoped to the flagged task list; follow-ups do NOT load `semantic-merge`.
      - **Tier 2/3** (regardless of annotations) → full flow; follow-ups load `semantic-merge` via the `Skills:` field for proper merge resolution.
  - **Step 2b — Batched user decisions**: collect research-meaningful items from recon's blockquotes into a single `AskUserQuestion` call (merge-base target + user-decision items). Log each per `handoff-doc §User Decisions Log`. Commit PLAN.md before dispatching the implementer.
  - **Step 3 — Unified implementer** (Stage: `integration`; `Skills: superRA:semantic-merge` IF Tier 2/3; `Tasks in scope:` field names flagged task list). Two-commit structure: Commit 1 = mechanical merge (semantic-merge if Tier 2/3; `git merge --ff-only` if Tier 1); Commit 2 = unified refactor across flagged tasks. Pre-commit self-check per `refactor-and-integrate`.
  - **Step 4 — Verify reviewer** (Stage: `integration`; walks cumulative diff; refuses to walk APPROVED-integration tasks not in scope). Orchestrator split safety-valve applies when the in-scope task list is large enough to exceed context threshold.

- [x] **Step 3: Refactor every dispatch prompt** to canonical shape. Required-fields-first (`Stage:`, `Task:`, `Worktree:` / `Git range:`; `Skills:` / `References:` where override needed); `Additionally:` anchor-last with additive signal only. Canonical prefix verbatim. No restated PLAN.md content or checklist items.

- [x] **Step 4: Fold Phase D (merge/PR/cleanup)** from former `merge-workflow`. Drift tests run once on final state. PR body template preserved verbatim — strip or rewrite any branch whose condition no longer exists in unified Phase D (e.g., any `[OR: skipped per Step 2.0 …]` referencing the old Tier-1 branch if the new shortcut architecture removes it).

- [x] **Step 5: Add plan-change trigger pointer** — one bullet in Phase B acknowledging that substantive restructure findings escalate to `planning-workflow §Changing Plans` (orchestrator proposes, researcher decides). Not a duplicated protocol — a pointer.

- [x] **Step 6: Validate — walk the four workflow principles** against the draft. Confirm each principle preserved or strengthened. Commit.

> **Integration review notes (recon, 2026-04-19):**
> 1. **[ADVISORY]** `skills/integration-workflow/SKILL.md:441` — `§Integration → Invokes` says `superRA:semantic-merge` is "REQUIRED for the main update in Phase B Commit 1 and any Phase D pre-merge re-sync (delegated mode)." This contradicts Step 2's two-shortcut-axes logic: Tier 1 uses `git merge --ff-only` (line 142–143) and the Red Flags list at line 408 explicitly says "delegated mode is load-bearing when semantic-merge runs at all (Tier 2/3)." The word "REQUIRED" overstates — semantic-merge is Tier-conditional, not unconditional. Minor doc coherence; does not mis-operate because Step 2 is authoritative on control flow. Fix: change "REQUIRED for the main update in Phase B Commit 1" → "REQUIRED for Phase B Commit 1 on Tier 2/3 (Tier 1 uses `git merge --ff-only`; see Phase B Step 2)".
>    → implemented: softened line 441 to Tier-conditional wording per recon's suggested fix (`skills/integration-workflow/SKILL.md:441`)

---

### Task 3: Delete `skills/merge-workflow/`
**Depends on:** Task 2
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A
**Input:** `skills/merge-workflow/SKILL.md` + references; every caller of `superRA:merge-workflow` across the repo (grep).
**Output:** Directory deleted; callers outside Task 6's peripheral-surfaces scope repointed at `integration-workflow`; `RELEASE-NOTES.md` carries one deprecation line pointing at `integration-workflow`. Task 6 owns the remaining inventory / Workflow Status / CLAUDE.md / README / CATEGORIES / Skill-Load Manifest sync; Task 3 does not pre-empt those files.

- [x] **Step 1: Audit callers** — `grep -rn "merge-workflow" skills/ agents/ hooks/ README.md CLAUDE.md RELEASE-NOTES.md`. Hits outside Task 6's scope (the ones Task 3 owns): `agents/implementer.md` (×3), `agents/reviewer.md` (×1), `skills/refactor-and-integrate/SKILL.md` (×2), `skills/refactor-and-integrate/references/drift-test-quality.md` (×1), `skills/agent-orchestration/references/agent-teams.md` (×1), `skills/using-superRA/references/codex-tools.md` (×1), `tests/structural-invariants.sh` (×1). Task 6's scope (deferred): `README.md`, `CLAUDE.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`. RELEASE-NOTES pre-existing entries remain as historical record.
- [x] **Step 2: Update each in-scope caller** to point at `integration-workflow` (Phase A–D vocabulary). Done: agents/implementer.md + agents/reviewer.md stage listings + agents/implementer.md §Stage-specific code deliverables; refactor-and-integrate/SKILL.md §Workflow-skills line folded into a single integration-workflow bullet citing Phase A / Phase B / Phase D call sites and the residual "Workflow skills (...)" parenthetical trimmed to `superRA:integration-workflow` only; drift-test-quality.md cross-cutting Red Flags preamble; agent-teams.md diagram; codex-tools.md finishing-branch pointer; tests/structural-invariants.sh dispatch_files list.
- [x] **Step 3: Delete the directory** — `git rm -r skills/merge-workflow/` (one file: SKILL.md).
- [x] **Step 4: Add deprecation line to `RELEASE-NOTES.md`** — single bullet under a new "Unreleased — unified integration-workflow refactor" heading, naming Phase D as the new home and listing the caller-file classes that were repointed.
- [x] **Step 5: Validate — re-grep** remaining hits confirmed to be either Task 6's scope or pre-existing historical RELEASE-NOTES entries. Commit.

---

### Task 4: Update `semantic-merge` caller paths and handoff-doc coherence rule
**Depends on:** Task 2
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A
**Input:** `skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/references/merge-quality.md` (or its successor location post-Task 1).
**Output:** `semantic-merge` caller-path text updated (`merge-workflow Step 1` → `integration-workflow Phase B`); `[BLOCKING] Handoff-doc coherence` item added to merge-quality; escalation rule stated: substantive handoff-doc restructures (task add/remove/combine, DAG edge flip, APPROVED status invalidation) escalate to `planning-workflow §Changing Plans` before the merge proceeds.

- [x] **Step 1: Update caller-path references** in `semantic-merge/SKILL.md` (delegated-mode invocation section, return contract section, standalone-invocation section).
- [x] **Step 2: Add `[BLOCKING] Handoff-doc coherence`** item to merge-quality checklist (Task 1's successor location). Include the escalation-to-Change-Plans rule.
- [x] **Step 3: Validate** — dry-read through a Tier 3 example where PLAN.md is in the conflict set. Confirm the escalation path is discoverable from semantic-merge alone. Commit.

---

### Task 5: Minimal `planning-workflow §Changing Plans` extension + B→B re-entry trigger
**Depends on:** Task 2
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A
**Input:** `skills/planning-workflow/SKILL.md` §Changing Plans; `skills/handoff-doc/references/plan-anatomy.md` (DAG cascade rule for Integration status).
**Output:** (a) One bullet in `planning-workflow §Changing Plans` acknowledging INTEGRATE-phase findings can trigger the protocol; one line stating orchestrator authors the Restructure Proposal and researcher decides. (b) In `plan-anatomy.md`, alongside the existing Integration-status cascade rule (lines 178–179), add one sentence documenting the **B→B re-entry trigger**: when main advances mid-integration, the recon reviewer's per-task annotations gate the flip — tasks it annotates get `Integration status: REVISE`; tasks it does not annotate stay `APPROVED`. No duplication of the cascade semantics elsewhere.

- [x] **Step 1: Add the pointer bullet and authorship rule** to `planning-workflow §Changing Plans`. No other changes — existing cascade semantics already cover mid-INTEGRATE rollback.
- [x] **Step 2: Add B→B re-entry trigger sentence** to `plan-anatomy.md` adjacent to the Integration-status cascade rule. Format: one sentence; references `integration-workflow` Phase B recon as the trigger author.
- [x] **Step 3: Validate** — cross-read with Task 2's Phase B plan-change pointer and recon protocol; confirm the two pointers + the trigger sentence are consistent and not duplicative. Commit.

---

### Task 6: Sync peripheral surfaces
**Depends on:** Tasks 2, 3, 4, 5
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A
**Input:** `skills/using-superRA/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/agent-orchestration/SKILL.md`, `README.md`, `RELEASE-NOTES.md`, `skills/CATEGORIES.md`, `/CLAUDE.md`.
**Output:** All skill inventories, the Skill-Load Manifest, the execution-workflow hand-off, the PLAN.md template's Workflow Status milestones, the agent-orchestration override-pattern language, and the contributor CLAUDE.md reflect the unified `integration-workflow` and the deletion of `merge-workflow`.

- [x] **Step 1: Skill-Load Manifest** — Skill Inventory `merge-workflow` row removed; `integration-workflow` row rewritten to "INTEGRATE (Phases A–D): drift tests, iterative sync + refactor, doc finalization, final merge / PR / cleanup." `merge` stage row in the Manifest retained but clarified in a follow-up paragraph: used only for standalone `semantic-merge` delegated-mode dispatches; inside Phase B the unified implementer runs `Stage: integration` and conditionally loads `superRA:semantic-merge` via the canonical `Skills:` field on Tier 2/3. The existing `Skills:` + `References:` override-pattern language in `agent-orchestration §Dispatch Templates` (lines 147–148) already supports on-demand utility-skill loading (e.g., `document-skills:skill-creator`) — no edit needed.
- [x] **Step 2: `execution-workflow` Step 4 completion menu** — confirmed Option 1 and Option 2 already dispatch `integration-workflow` only (line 186 unchanged). SKILL.md preamble, top-level process loop Step 4, and §Integration "Required workflow skills" list updated to cite `integration-workflow` Phases A–D only (removed the `merge-workflow` bullet).
- [x] **Step 3: `plan-anatomy.md` Workflow Status** — milestone list rewritten: `Drift tests created` → Phase A; `Refactored` → Phase B verify reviewer APPROVED; `Docs finalized` → Phase C; `Merged` → Phase D (kept as a standalone milestone for visibility into the final merge action). §Field-by-Field §User Decisions Log location list updated from `integration-workflow` Step 1 / Step 3 to Phase A / Phase C.
- [x] **Step 4: `agent-orchestration`** — override-pattern language (lines 147–148) confirmed adequate for utility-skill on-demand loading via `Skills:` / `References:` fields; no edit. Removed the `merge-workflow` citation from the reviewer-feedback-discipline call-site list (now names `execution-workflow`, `integration-workflow` Phase A/B/C, and standalone `semantic-merge`).
- [x] **Step 5: README / RELEASE-NOTES / CATEGORIES / CLAUDE.md** — README workflow-map ASCII + Mermaid diagram retooled to Phases A–D with B→B re-entry and D→B re-entry arrows; skill-inventory table dropped `merge-workflow` row and widened `integration-workflow` to Phases A–D; `semantic-merge` row updated to cite `integration-workflow` Phase B as caller. CATEGORIES.md same pattern. CLAUDE.md §DRY workflow-skills list updated to drop `merge-workflow`. RELEASE-NOTES Task 3 bullet augmented with Task 6's peripheral-surface summary.
- [x] **Step 6: Validate** — post-edit `grep merge-workflow` sweep: only PLAN.md / RESULTS.md / RELEASE-NOTES.md / `docs/` (historical plan archive) remain — all expected. Dispatch prompts in `integration-workflow` Phase B already use canonical `Skills:` / `Task:` / `Git range:` fields (Steps 1, 3, 4 — inspected). Commit.

---

### Task 7: End-to-end dry-run verification
**Depends on:** Tasks 1–6
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A (on-paper dry-read / simulation)
**Input:** All refactored skills; a hypothetical dummy branch with APPROVED PLAN.md and code-complete state.
**Output:** Walk-through notes in RESULTS.md showing Phases A → D exercised on paper, with B → B re-entry (main advances mid-integration), a mid-Phase-B plan-change restructure triggering `planning-workflow §Changing Plans`, an unrelated-hunk injection caught by the Implementer Self-Check + verify reviewer, and D → B re-entry (main advances during Phase C). Confirms per-task `Integration status` flip logic, Workflow Status rollback, minimum-net-diff protection via self-check + reviewer walk, and B→B trigger-sentence consistency with Task 5's addition.

- [x] **Step 1: Dry-read Phase A → D** on the refactored `integration-workflow` SKILL.md with a hypothetical dummy branch in mind; log every dispatch, user stop-point, and re-entry arrow encountered.
- [x] **Step 2: B→B re-entry scenario** — inject main advancing mid-integration on paper; walk recon-reviewer flip logic; confirm consistency with the B→B trigger sentence in `plan-anatomy.md` line 179 (added by Task 5).
- [x] **Step 3: Mid-Phase-B plan-change scenario** — inject a substantive restructure need surfaced by recon; walk `planning-workflow §Changing Plans` with the INTEGRATE-trigger bullet (added by Task 5); confirm orchestrator-authors / researcher-decides ownership is unambiguous.
- [x] **Step 4: Unrelated-hunk injection scenario** — on paper, inject an out-of-scope hunk in the implementer's Commit 2; walk the Implementer Self-Check (`git diff <merge-base>..HEAD`) and the verify reviewer's minimum-net-diff catch; confirm both independently catch it.
- [x] **Step 5: D→B re-entry scenario** + write findings to RESULTS.md. Fix any ADVISORY stale-vocabulary hits found during the sweep in-place (no tuned content touched). Any `[BLOCKING]` issues would have been opened as new review-notes entries on the relevant prior task; none found.

---

### Task 8: Retrospective refinements from Phase A–D dogfooding
**Depends on:** Tasks 1, 2, 5 *(edits files those tasks touched; added post-integration 2026-04-19 via §Changing Plans)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** N/A (skill + agent file edits)
**Input:** `skills/handoff-doc/references/plan-anatomy.md`, `skills/integration-workflow/SKILL.md`, `agents/reviewer.md`, `agents/implementer.md`.
**Output:** Three documentation clarifications in the skills / agents graph, all small edits, all motivated by concrete ambiguities the PR #5 integration run itself exposed. No code content of Tasks 1–7 touched.

- [x] **Step 1: Clarify Integration-status lifecycle** — in `skills/handoff-doc/references/plan-anatomy.md`, rewrite the `**Integration status:**` bullet's state-setter clause (line 179). The current wording ("set by the integration reviewer…") predates the recon-as-reviewer architecture added in Task 2 and hides the three-actor choreography. New wording must name: orchestrator flips to `REVISE` post-recon (on annotated tasks) and to `APPROVED` post-verify-reviewer APPROVE; implementer flips to `IMPLEMENTED` post-commit. Preserve the existing DAG cascade paragraph and the B→B re-entry trigger sentence (Task 5's addition) unchanged. Then, in `skills/integration-workflow/SKILL.md` Phase B, add one sentence between Step 3 and Step 4 naming the implementer's `IMPLEMENTED` flip as part of the two-commit handoff (so the lifecycle is discoverable from the workflow skill without having to cross-read `plan-anatomy.md`).

- [x] **Step 2: Annotation etiquette — preserve task-block boundaries** — add a rule to the annotation-etiquette sections of `agents/reviewer.md` and `agents/implementer.md`: when appending a review-notes blockquote (reviewer) or a `→ implemented:` reply (implementer), the edit must stay strictly within the task block — never disturb the preceding `---` separator, the `### Task N:` heading, or the trailing separator before the next task. Motivation: during PR #5 Phase B recon, the annotation insertion on Task 1 elided the separator + Task 2 heading between blocks (commit `7a12e34`), forcing the implementer to restore them in commit `b58c3fc` as a coherence fix. Find the existing inline-edit etiquette section in each agent file and add the boundary rule alongside it.

- [x] **Step 3: Phase B Tier 1 + unchanged-main degenerate case** — in `skills/integration-workflow/SKILL.md` Phase B Step 2, add one sentence to the Tier 1 bullets handling the case where `origin/<base-branch>` has not advanced since merge-base. Wording: *"Degenerate case: if `git merge-base --is-ancestor origin/<base-branch> HEAD`, the fast-forward merge is a true no-op — skip Commit 1 and note the skip in the implementer's status return. The two-commit structure collapses to one commit (Commit 2 = unified refactor)."* Motivation: PR #5 implementer had to improvise this handling on the fly.

- [x] **Step 4: Validate** — re-read the edited files end-to-end; confirm (a) state-setter clause now matches the recon-as-reviewer architecture in Task 2's Phase B, (b) annotation-etiquette rule sits alongside the existing inline-edit discipline in each agent file without duplicating it, (c) Tier 1 no-op sentence reads correctly against Phase B Step 2's existing bullets. Run `grep -n "integration reviewer\|set by the" skills/handoff-doc/references/plan-anatomy.md` to confirm no stale pre-architecture phrasing remains. Commit.

  → implemented: (a) `plan-anatomy.md:179` state-setter clause rewritten to name orchestrator (REVISE/APPROVED flips) + implementer (IMPLEMENTED flip); (b) boundary-preservation rule added as a new bullet between inline-edit and remove-superseded in both `agents/implementer.md` §Editing Etiquette and `agents/reviewer.md` §Editing Etiquette; (c) Tier 1 no-op sentence added to both Tier-1 bullets in `integration-workflow` Phase B Step 2; (d) `integration-workflow` Phase B gained an `IMPLEMENTED` flip sentence between Step 3 and Step 4; grep confirmed no stale pre-architecture phrasing remains.
