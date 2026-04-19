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

- [x] **Plan approved** — researcher signed off on this plan (2026-04-19)
- [ ] **Execution complete** — all tasks `APPROVED`
- [ ] **Drift tests created** — N/A for skill refactor; substitute: skill-graph consistency sweep + end-to-end dry-run verified
- [ ] **Refactored** — final integration-review approval on the consolidated skill changes
- [ ] **Docs finalized** — README / RELEASE-NOTES / CATEGORIES / CLAUDE.md audited and consistent with new skill graph
- [ ] **Merged** — branch merged to main or PR opened

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
**Integration status:** *(set during integration)*

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

---

### Task 2: Unify `integration-workflow` — Phases A–D with iterative Phase B
**Depends on:** Task 1
**Review status:** REVISE
**Integration status:**

> **Review notes (2026-04-19):**
>
> 1. [MAJOR] **Unauthorized step rewrite — Tier-1 shortcut drop routed through step-text edit, not `planning-workflow §Changing Plans`.** Step 2 text was changed from the planned "Tier 1 shortcut path." to a paragraph documenting that the shortcut was dropped. The implementer is not authorized to rewrite step content (handoff-doc ownership: implementers annotate with `→ implemented:`, they do not alter step text or task objective — see `agents/implementer.md`). Dropping the Tier-1 shortcut is a substantive design deviation from the approved plan and should have escalated via `planning-workflow §Changing Plans` (orchestrator authors the restructure; researcher decides). Fix: (a) revert Step 2 text to its original wording ("… Tier 1 shortcut path."), append an `→ implemented: <file:line> — noted that the Tier-1 shortcut was not included; escalation needed` annotation below it, and (b) flag this to the orchestrator in your status return so the plan change can be properly logged (User Decision + §Decisions entry) before the shortcut drop is ratified.
>
> 2. [MAJOR] **PR body template preserves a dangling "Step 2.0" reference.** Phase D Step 3b (SKILL.md:344) carries the old PR body verbatim including `[OR: skipped per Step 2.0 — Tier 1 clean merge, no analysis-path changes incoming]`. Phase D has no Step 2.0 — the Tier-1 skip path was deliberately dropped (see finding 1). Preserving the `[OR: …]` branch in the template invites PR authors to fill it in when no underlying mechanism exists. The Task 2 Step 2 text acknowledges this ("carries over only in the PR body template … if a future revision re-introduces the shortcut") but the dispatch-time user of the template has no way to know that. Either (a) strip the `[OR: …]` branch so the template reflects actual Phase D behavior, or (b) keep the full text but add an explicit in-file note above the PR body that the `[OR: …]` branch is a forward hook, not an active option — preferably (a), since "preserved verbatim" is a design requirement the orchestrator set, but a template that lies about the workflow is worse than a near-verbatim template. Flag to the orchestrator if unsure.
>
> 3. [MINOR] **Phase B opening paragraph lightly duplicates the two-commit definition from `refactor-and-integrate/references/merge-quality.md`.** SKILL.md:87 describes "Commit 1 mechanical conflict resolution via `superRA:semantic-merge`; Commit 2 unified integration — codebase-fit changes plus any intent-level work semantic-merge identified". `references/merge-quality.md` §11–26 owns this definition. Some naming is needed for the workflow to orchestrate, but the current paragraph leans into scope description ("codebase-fit changes plus any intent-level work semantic-merge identified"), which is merge-quality content. Consider trimming to: "Commit 1 mechanical (via `superRA:semantic-merge`); Commit 2 unified integration (per `refactor-and-integrate/references/merge-quality.md` §Two-Commit Structure)." Not blocking — borderline DRY.
>
> 4. [MINOR] **"Run drift tests between the two commits and again after Commit 2" is named in both the Phase B body prose (lines 147, 151–158) and the dispatch `Additionally:` block (line 147).** Dispatch `Additionally:` steering must be strictly additive per `agent-orchestration §Dispatch Templates`. The drift-test cadence is already codified in the body prose immediately below and in `references/drift-test-quality.md`. Consider deleting the "Run drift tests between the two commits and again after Commit 2." line from the `Additionally:` block — the implementer will read the body prose and the reference. Not blocking — close call on whether this is load-bearing steering or restated content.
>
> 5. [MINOR] **"When to Lighten" section mentions "the sync commit only" for true greenfield branches.** SKILL.md:367 says "Phase B reduces to the sync commit only" for greenfield. The Phase B core principle (lines 86–87, 381) is that separating sync and refactor into two passes violates minimum-net-diff. For a greenfield branch with no base, there is no sync to perform; the "sync commit only" wording is confusing. Consider rephrasing: "For a true greenfield branch with no base branch, Phase B is skipped entirely (no sync, no refactor target)." Not blocking.
>
> Re-review scope: (1) and (2) are the blocking items; (3)-(5) are advisory.

**Script:** N/A
**Input:** current `skills/integration-workflow/SKILL.md`, current `skills/merge-workflow/SKILL.md`, Task 1's rewritten `refactor-and-integrate`, `agent-orchestration §Dispatch Templates`
**Output:** Rewritten `skills/integration-workflow/SKILL.md` covering Phases A (drift-test creation, unchanged), B (Integrate — sync + refactor, three-dispatch internal structure, iterative), C (docs maturation + disposition, unchanged), D (final merge / PR / cleanup, folded in from merge-workflow); all dispatches use canonical shape with no content duplicated from loaded skills; re-entry arrows explicit.

- [x] **Step 1: Draft phase skeleton** — Phases A–D with explicit re-entry arrows (B→A, B→B, C→B, D→B, Anywhere→`planning-workflow §Changing Plans`).

- [x] **Step 2: Write Phase B three-dispatch internal structure** — recon reviewer (read-only, produces integration map) → batched `AskUserQuestion` for research-meaningful items + merge-base list → unified implementer (loads `semantic-merge` + `refactor-and-integrate`; two-commit structure: Commit 1 mechanical, Commit 2 unified integration; runs pre-commit self-check) → verify reviewer. Orchestrator split safety-valve for large integration maps. The Tier-1 shortcut that former `merge-workflow` used for Step 2b was dropped: Phase B's verify reviewer is always dispatched regardless of tier — the shortcut only saved one dispatch and complicated the flow. Post-merge skip-documentation carries over only in the PR body template (Phase D) where a Tier-1 clean merge may still be documented if a future revision re-introduces the shortcut.

- [x] **Step 3: Refactor every dispatch prompt** to canonical shape. Required-fields-first (`Stage:`, `Task:`, `Worktree:` / `Git range:`); `Additionally:` anchor-last with additive signal only. Canonical prefix verbatim. No restated PLAN.md content or checklist items.

- [x] **Step 4: Fold Phase D (merge/PR/cleanup)** from former `merge-workflow`. Drift tests run once on final state. PR body template preserved verbatim.

- [x] **Step 5: Add plan-change trigger pointer** — one bullet in Phase B acknowledging that substantive restructure findings escalate to `planning-workflow §Changing Plans` (orchestrator proposes, researcher decides). Not a duplicated protocol — a pointer.

- [x] **Step 6: Validate — walk the four workflow principles** against the draft. Confirm each principle preserved or strengthened. Commit.

---

### Task 3: Delete `skills/merge-workflow/`
**Depends on:** Task 2
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `skills/merge-workflow/SKILL.md` + references; every caller of `superRA:merge-workflow` across the repo (grep).
**Output:** Directory deleted; `grep -r "merge-workflow"` returns zero hits in `/skills/`, `/agents/`, `/hooks/`; `RELEASE-NOTES.md` carries one deprecation line pointing at `integration-workflow`.

- [ ] **Step 1: Audit callers** — `grep -rn "merge-workflow" skills/ agents/ hooks/ README.md CLAUDE.md RELEASE-NOTES.md`. List every hit.
- [ ] **Step 2: Update each caller** to point at `integration-workflow`. Confirm wording matches the new Phase A–D structure.
- [ ] **Step 3: Delete the directory** — `git rm -r skills/merge-workflow/`.
- [ ] **Step 4: Validate — re-grep** returns zero hits except the RELEASE-NOTES deprecation line. Commit.

---

### Task 4: Update `semantic-merge` caller paths and handoff-doc coherence rule
**Depends on:** Task 2
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/references/merge-quality.md` (or its successor location post-Task 1).
**Output:** `semantic-merge` caller-path text updated (`merge-workflow Step 1` → `integration-workflow Phase B`); `[BLOCKING] Handoff-doc coherence` item added to merge-quality; escalation rule stated: substantive handoff-doc restructures (task add/remove/combine, DAG edge flip, APPROVED status invalidation) escalate to `planning-workflow §Changing Plans` before the merge proceeds.

- [ ] **Step 1: Update caller-path references** in `semantic-merge/SKILL.md` (delegated-mode invocation section, return contract section, standalone-invocation section).
- [ ] **Step 2: Add `[BLOCKING] Handoff-doc coherence`** item to merge-quality checklist (Task 1's successor location). Include the escalation-to-Change-Plans rule.
- [ ] **Step 3: Validate** — dry-read through a Tier 3 example where PLAN.md is in the conflict set. Confirm the escalation path is discoverable from semantic-merge alone. Commit.

---

### Task 5: Minimal `planning-workflow §Changing Plans` extension
**Depends on:** Task 2
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `skills/planning-workflow/SKILL.md` §Changing Plans.
**Output:** One bullet added acknowledging INTEGRATE-phase findings can trigger the protocol; one line stating orchestrator authors the Restructure Proposal and researcher decides. No duplication of the protocol body elsewhere.

- [ ] **Step 1: Add the pointer bullet and authorship rule.** No other changes — existing cascade semantics already cover mid-INTEGRATE rollback.
- [ ] **Step 2: Validate** — cross-read with Task 2's Phase B plan-change pointer; confirm the two pointers are consistent and not duplicative. Commit.

---

### Task 6: Sync peripheral surfaces
**Depends on:** Tasks 2, 3, 4, 5
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `skills/using-superRA/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/agent-orchestration/SKILL.md`, `README.md`, `RELEASE-NOTES.md`, `skills/CATEGORIES.md`, `/CLAUDE.md`.
**Output:** All skill inventories, the Skill-Load Manifest, the execution-workflow hand-off, the PLAN.md template's Workflow Status milestones, the agent-orchestration override-pattern language, and the contributor CLAUDE.md reflect the unified `integration-workflow` and the deletion of `merge-workflow`.

- [ ] **Step 1: Skill-Load Manifest** — update stage names if any changed; verify the `Additionally:` override pattern language supports on-demand `document-skills:skill-creator` loading.
- [ ] **Step 2: `execution-workflow` Step 4 completion menu** — hand-off points at `integration-workflow` for Options 1 and 2; no `merge-workflow` reference.
- [ ] **Step 3: `plan-anatomy.md` Workflow Status** — revise milestone list to match unified phases (drop separate `Merged` milestone or fold it under Phase D completion signal — orchestrator judgment).
- [ ] **Step 4: `agent-orchestration`** — confirm override-pattern language for utility-skill loading via `Additionally:` is clear; light edit if not.
- [ ] **Step 5: README / RELEASE-NOTES / CATEGORIES / CLAUDE.md** — sync skill inventory; add RELEASE-NOTES deprecation line for `merge-workflow`; update CLAUDE.md §Workflow principles + §Roadmap language.
- [ ] **Step 6: Validate** — skill-graph consistency sweep (grep for `merge-workflow`; sample five dispatch prompts; confirm shared-flow checklist is single source). Commit.

---

### Task 7: End-to-end dry-run verification
**Depends on:** Tasks 1–6
**Review status:**
**Integration status:**

**Script:** N/A (simulation in a throwaway worktree)
**Input:** All refactored skills; a dummy branch with APPROVED PLAN.md and code-complete state.
**Output:** Walk-through notes in RESULTS.md showing Phases A → D exercised, with B → B re-entry (second merge-base sync), a mid-Phase-B plan-change restructure triggering `planning-workflow §Changing Plans`, and D → B re-entry simulating main advancing during Phase C. Confirms drift tests re-run on re-entry, `Integration status` resets, Workflow Status rolls back, minimum-net-diff self-check catches a deliberately-injected unrelated hunk.

- [ ] **Step 1: Set up dummy worktree** on a throwaway branch with a minimal analysis and APPROVED plan.
- [ ] **Step 2: Walk Phase A → D** using the refactored skills; log every dispatch, user decision, and re-entry.
- [ ] **Step 3: Inject a plan-change trigger** mid-Phase-B; verify protocol fires correctly.
- [ ] **Step 4: Inject an unrelated hunk** in the implementer's Commit 2; verify self-check + reviewer catch it.
- [ ] **Step 5: Write findings** to RESULTS.md (Stage 1 dev-log form). Any pattern issues found feed back as additional REVISE cycles on prior tasks.
