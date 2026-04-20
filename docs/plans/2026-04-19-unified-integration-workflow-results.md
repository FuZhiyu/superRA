---
author: "[[Julie Zhiyu Fu]]"
date: 2026-04-19
timestamp: "2026-04-19T00:00:00"
session_id: "session-20260419-integration-phaseC"
git_commit: "b015b8e71cb2152032deb5d47990903ffa3b4ecf"
git_message: "results: fact-check Stage 2 RESULTS.md"
git_dirty: false
branch: "refactor/unified-integration"
merge_base: "92a685ba67970f00f3009fa51acd67292ce64715"
tags: ["report", "results", "superRA", "skill-refactor", "integration-workflow"]
project: "[[superRA]]"
permalink: "docs/plans/2026-04-19-unified-integration-workflow-results"
---

# Unified Integration-Workflow Refactor — Results

**Status:** Complete — all 7 tasks APPROVED; Phase A (`Drift tests created`) and Phase B (`Refactored`) milestones flipped; Phase C docs finalization in progress (this document).
**Branch:** `refactor/unified-integration`
**Merge base:** `92a685b` (`origin/main`, 0 commits behind at integration recon)
**Companion plan:** `docs/plans/2026-04-19-unified-integration-workflow-plan.md` (to be relocated alongside this file on final disposition).

---

## Context and Objective

Prior to this refactor, superRA's INTEGRATE phase was split across two workflow skills (`integration-workflow` for drift tests + refactor + docs; `merge-workflow` for main update + merge/PR + cleanup) and the boundary produced recurring confusion:

- Two separate diffs against the merge base (one from the sync step, one from the refactor step) violated the minimum-net-diff principle — the shape of what ends up on `main` should come from a single coherent change set, not two stacked ones.
- The drift-test / integration-review / refactor discipline was duplicated in body prose across `integration-workflow`, `merge-workflow`, `refactor-and-integrate`, and the dispatched-agent protocol, with wording drifting between copies.
- Dispatch prompts carried content that belonged to loaded skills (checklist items, PLAN.md restated, skill-load enumerations), working against the agent-orchestration principle that dispatch prompts carry only required identifying fields plus additive steering.
- Mid-integration plan changes (task add/remove/combine, DAG edge flips) had no explicit protocol — the existing `planning-workflow §Changing Plans` covered the mechanics but nothing routed INTEGRATE-phase findings into it.

The refactor unifies the INTEGRATE phase into a single iterative skill with four phases (A–D), rebuilds the integration discipline as a severity-marked gated checklist shared by implementer and reviewer, deletes `merge-workflow`, retains `semantic-merge` as a standalone utility, and wires INTEGRATE-phase restructure findings into the existing `planning-workflow §Changing Plans` protocol via minimal additions.

## What Changed

### Skill graph diff

**`skills/integration-workflow/SKILL.md`** — rewritten end-to-end. Phases A–D replace the prior Stage 1 / Stage 2 / Step 3 / hand-off-to-merge-workflow structure:

- **Phase A** — drift-test creation (unchanged in intent; dispatch prompts re-shaped to canonical form).
- **Phase B** — *unified* sync + refactor. Internal structure: recon reviewer → orchestrator-owned flag pass (Integration status flips per annotation) → optional batched user decisions → unified implementer (two-commit structure) → verify reviewer. Iterative: re-entrant on itself (`B → B`) when main advances again before Phase D.
- **Phase C** — docs maturation + disposition (the stage producing this document).
- **Phase D** — pre-merge freshness check, final merge or PR, cleanup. Folded in from the deleted `merge-workflow`. Re-enters Phase B (`D → B`) when the freshness check finds main advanced since Phase B APPROVED.
- **Cross-phase** — any phase that surfaces a substantive restructure finding (task add/remove/combine, DAG edge flip, prior APPROVED invalidation) escalates to `planning-workflow §Changing Plans`.

Two independent shortcut axes in Phase B: **Tier classification** (from recon's `semantic-merge` trial-merge) gates the merge path (Tier 1 → `git merge --ff-only`; Tier 2/3 → delegated `semantic-merge` on follow-ups); **annotation count** (from recon's per-task blockquotes) gates the refactor path (zero annotations → skip unified implementer + verify reviewer; non-zero → dispatch them scoped to the annotated task list). Combined, they cover four shortcut combinations, all documented identically in `§Internal Structure` and in the orchestrator's post-recon step.

**`skills/merge-workflow/`** — **deleted** (one file, `SKILL.md`). All callers outside peripheral-surface scope were repointed at `integration-workflow` Phase A–D vocabulary; `RELEASE-NOTES.md` carries the deprecation line.

**`skills/refactor-and-integrate/`** — restructured. The SKILL.md body is principle-level only (cross-cutting gates: the load-bearing `[BLOCKING] Minimum net diff to merge base` top item, the reviewer verdict protocol, the Implementer Self-Check, the `§Scope by Integration Status` rule). All tuned content (Red Flags, Tier 3 escalation prose, RA-framing, rationalization lists) lives in the three references (`drift-test-quality.md`, `codebase-integration.md`, `merge-quality.md`), each organized as §How-To followed by a §Gated Checklist with `[BLOCKING]` / `[ADVISORY]` severity markers. The same checklist is walked by the implementer as pre-handoff self-check and by the reviewer as verification criteria — one source of truth, two perspectives.

**`skills/semantic-merge/`** — caller-path text updated from the deleted `merge-workflow` to `integration-workflow` Phase B + Phase D. A new `[BLOCKING] Handoff-doc coherence` item was added to `merge-quality.md` with a matching §How-To section that carves out substantive handoff-doc restructures (task add/remove/combine, DAG edge flip, APPROVED status invalidation) from routine content conflicts — restructures escalate to `planning-workflow §Changing Plans` *before* the merge proceeds. `semantic-merge` itself remains a standalone utility.

**`skills/planning-workflow/SKILL.md`** — `§Changing Plans` gained one bullet acknowledging INTEGRATE-phase restructure findings (Phase B recon, Phase B verify reviewer, Phase C doc-reviewer, Phase D semantic-merge) as valid triggers, naming the orchestrator-authors / researcher-decides ownership rule. No duplication of protocol — the bullet is a pointer.

**`skills/handoff-doc/references/plan-anatomy.md`** — one sentence appended to the existing Integration-status cascade rule documenting the **B→B re-entry trigger**: recon's per-task annotations gate the flip (annotated tasks → `REVISE`; unannotated stay `APPROVED`). The Workflow Status milestone list was renamed to Phase A / B / C / D.

**Dispatch-prompt normalization.** Every `Agent(subagent_type: …)` block in `integration-workflow` now follows the canonical shape from `agent-orchestration §Dispatch Templates`: required identifying fields first (`Stage:`, `Task:`, `Git range:` / `Worktree:`, `Skills:` / `Tasks in scope:` where applicable), canonical prefix verbatim, `Additionally:` anchor-last with additive steering only. No restated PLAN.md content; no duplicated checklist items; no skill-load enumerations (the Skill-Load Manifest handles those).

**Peripheral surfaces** — skill inventories (`using-superRA §Skill Inventory`, `CATEGORIES.md`, `README.md`), the PLAN.md template's Workflow Status block, `execution-workflow` Step 4 completion menu, `agent-orchestration` reviewer-feedback call-site list, `CLAUDE.md §DRY workflow-skills ownership list`, and `RELEASE-NOTES.md` were all swept to drop `merge-workflow` and widen `integration-workflow` to Phases A–D. README's workflow-map ASCII diagram and Mermaid diagram gained B→B and D→B re-entry arrows.

### Follow-Up Refinements (Task 8)

Three documentation clarifications surfaced by the end-to-end Phase A–D dogfooding run itself; added post-integration via `planning-workflow §Changing Plans` and applied without touching Tasks 1–7's code content.

- **Integration-status lifecycle named explicitly.** `handoff-doc/references/plan-anatomy.md` state-setter clause (line 179) now names the three-actor choreography — orchestrator flips to `REVISE` post-recon and to `APPROVED` post-verify, unified implementer flips to `IMPLEMENTED` on Commit 2. `integration-workflow` Phase B gained a one-sentence cross-reference between Step 3 and Step 4 so the lifecycle is discoverable from the workflow skill. Replaces the prior "set by the integration reviewer" phrasing that predated Task 2's recon-as-reviewer architecture.
- **Annotation etiquette — task-block boundary preservation.** `agents/reviewer.md` and `agents/implementer.md` Editing Etiquette sections gained a boundary-preservation bullet alongside the existing inline-edit rule: never disturb `---` separators or `### Task N:` headings when writing review-notes blockquotes or `→ implemented:` replies. Motivated by the PR #5 Phase B recon elision that commit `b58c3fc` had to restore.
- **Phase B Tier 1 + unchanged-main degenerate case documented.** `integration-workflow` Phase B Step 2 Tier-1 bullets gained explicit handling for the case where `origin/<base-branch>` has not advanced since merge-base: the fast-forward merge is a true no-op (skip Commit 1, collapse the two-commit structure to one). The PR #5 implementer had to improvise this on the fly.

### Load-bearing design decisions

- **Minimum-net-diff as the top gated-checklist item.** Stated as `[BLOCKING] Minimum net diff to merge base` in the Gated Checklist of all three `refactor-and-integrate` references. Enforced by two independent nets: the Implementer Self-Check (`git diff <merge-base>..HEAD` before every commit; any hunk without a checklist justification is reverted or re-justified in the integration map) and the verify reviewer (runs the same diff as evidence; raises out-of-scope hunks as `[BLOCKING]` findings).
- **Shared-flow gated checklist.** The implementer walks each reference's §Gated Checklist as pre-handoff self-check; the reviewer walks the same items as verification. No review-only parallel document, no content duplicated between SKILL.md body and references. `[BLOCKING]` items block APPROVE; `[ADVISORY]` items may be flagged as MINOR.
- **Recon is a standard reviewer.** Phase B Step 1 dispatches a reviewer (`Stage: integration`) with `Skills: superRA:semantic-merge` via the canonical dispatch field. Recon's output flows through the standard reviewer protocol — per-task integration review-notes blockquotes on PLAN.md — rather than a custom return payload. Tier classification is logged as a one-line entry under `## Decisions`. All communication flows through the handoff doc; no return-text contract.
- **Scope by Integration status.** Unified implementer and verify reviewer operate only on tasks whose `Integration status` is unset or `REVISE`. APPROVED-integration tasks are out of scope (mirrors the existing Review-status DAG cascade rule in `plan-anatomy.md`). Dispatches carry a `Tasks in scope:` field naming the in-scope list; the verify reviewer raises out-of-scope hunks as `[BLOCKING]` Minimum-net-diff violations.
- **Tier-conditional `semantic-merge` load.** Tier 1 (clean fast-forward) → follow-ups do NOT load `semantic-merge`. Tier 2/3 → follow-ups load `semantic-merge` via the canonical `Skills:` dispatch field. The two-axis decomposition (Tier × annotations) prevents the class of bugs where one axis is clean and the other isn't.
- **Mid-INTEGRATE restructures ride the existing `planning-workflow §Changing Plans`.** Not a new protocol — a pointer bullet in `§Changing Plans` and a trigger sentence in `plan-anatomy.md`. Ownership: orchestrator authors the Restructure Proposal; researcher decides. Existing cascade semantics apply.
- **Tuned wording preserved verbatim.** All Red Flags tables, rationalization bullets, Tier 3 escalation prose, and RA-framing sentences were relocated without paraphrasing, per the plugin's `/CLAUDE.md §Skill Changes` contract.

For the full deliberation log, see the companion plan's `## Decisions` section.

## Validation

### End-to-end dry-run (Task 7)

Five scenarios walked on paper against the refactored skill graph, confirming that every dispatch, stop-point, and re-entry arrow is reachable from the committed skill text without invented protocol:

1. **Happy path Phase A → D** on a clean branch. Every dispatch matches the canonical shape; every autonomy stop-point in the `Phase Map §Autonomy` box cross-references back to `using-superRA §Universal Principles (#4)` and to `handoff-doc §User Decisions Log`.
2. **B→B re-entry** — main advances after `Refactored` flips but before Phase C. Recon's per-task annotations gate the `Integration status` flip (annotated → `REVISE`; unannotated stay `APPROVED`); the three APPROVED tasks stay out of the unified implementer's diff under `§Scope by Integration Status`. Consistent with the B→B trigger sentence in `plan-anatomy.md`.
3. **Mid-Phase-B substantive restructure** — recon surfaces that one task's sample construction overlaps with a new main-side helper; cleanest resolution is to merge and delete the task. Walks `planning-workflow §Changing Plans` with the INTEGRATE-trigger bullet: orchestrator authors the Restructure Proposal, researcher decides via `AskUserQuestion`, decision logged per `§User Decisions Log`, PLAN.md inline-edited atomically, Phase B re-entered at Step 1 per `§Changing Plans` Step 6.
4. **Unrelated-hunk injection in Commit 2** — implementer reformats an out-of-scope module during the unified refactor commit. Caught twice, independently: (a) the Implementer Self-Check (`git diff <merge-base>..HEAD`) rejects hunks with no `[BLOCKING]`/`[ADVISORY]` justification; (b) the verify reviewer raises them as `[BLOCKING]` Minimum-net-diff findings on the same cumulative diff.
5. **D→B re-entry** — main advances during Phase C. Phase D Step 1's pre-merge freshness check (`git fetch` + `git log <merge-base>..origin/<base-branch>`) detects the drift and re-enters Phase B scoped to the newly affected task. After Phase B re-APPROVE, Phase C re-runs under the doc-writer's "re-run the whole matured doc on every integration pass" rule; Phase D Step 1 re-checks freshness.

All five scenarios resolved on the committed skill text with no gaps. Seventeen ADVISORY-level stale-vocabulary strings (legacy `integration-workflow Step 1 / Step 3` / `Stage 1 / Stage 2` pointers across 11 skill files) surfaced during the dry-run and were fixed in the same task — all pointer strings, no tuned content touched.

### Integration Phase B recon

Recon (`Stage: integration`, loaded with `superRA:semantic-merge`) classified the branch as **Tier 1** — trivial fast-forward; `origin/main` 0 commits ahead of merge-base `92a685b`, `git merge-tree` clean, branch 31 commits ahead. Two `[ADVISORY]` pointer issues were annotated on Task 1 and Task 2 PLAN.md blockquotes; both fixed in the unified Phase B refactor commit and verified by the Phase B verify reviewer. Per the two-axis shortcut rule: Tier 1 + non-zero annotations → fast-forward merge + refactor-only pass; follow-ups did not load `semantic-merge`.

### Skill-graph consistency sweeps

- `grep -rn "merge-workflow"` across `skills/`, `agents/`, `hooks/`, `README.md`, `CLAUDE.md`, `RELEASE-NOTES.md` after all tasks: remaining hits are (a) the RELEASE-NOTES deprecation bullet, (b) pre-existing RELEASE-NOTES entries from prior releases (historical record), and (c) `docs/plans/` archive. No active skill, agent, or hook carries a `merge-workflow` reference.
- `grep -rn "integration-workflow.*(Stage [12]|Step [1-9])"` across `skills/` post-Task-7 fixes: only legitimate per-phase Step N labels and the orthogonal RESULTS.md Stage 1 / Stage 2 document-lifecycle terminology remain.
- Minimum-net-diff invariant: Implementer Self-Check, verify-reviewer dispatch `Additionally:` clause, and the `[BLOCKING] Handoff-doc coherence` item in `merge-quality.md` compose without overlap.
- Shared-flow checklist invariant: the three `refactor-and-integrate` references each carry a single §Gated Checklist section walked by both implementer (as self-check) and reviewer (as verification). No parallel review-only document was introduced.
- Canonical dispatch shape: sampled dispatches in `integration-workflow` Phase B Steps 1, 3, 4 and Phase D Step 3b PR-creation block — all open with required fields first (`Stage:`, `Task:`, `Git range:` / `Worktree:`; optional `Skills:` / `Tasks in scope:` between required fields and the canonical prefix), canonical prefix verbatim, `Additionally:` anchor-last with additive signal only.

### Four workflow principles

Each principle preserved or strengthened:

1. **Implementer–reviewer pair at every step.** Phase A drift-test pair; Phase B recon + verify reviewer pair; Phase C doc-writer + doc-reviewer pair. No step ships without review.
2. **Handoff docs as record.** Recon annotations land in PLAN.md before the shortcut decision; Tier classification lands in `## Decisions`; every stop-point logs per `§User Decisions Log` before acting.
3. **Fast early, strict before merge. Semantic merges always.** Phase B iterative and re-enterable; Phase D Step 1 re-enters Phase B on main advancement; `semantic-merge` used on Tier 2/3 and on Phase D re-sync.
4. **Autonomous with human in the loop.** The five enumerated stop-points (recon user-decision batch, Phase A user confirmation, Phase C doc disposition, Phase D merge/PR choice, mid-phase restructure triggers) all route through `AskUserQuestion`, with each decision logged per `§User Decisions Log` before acting.

## Residual Risks and Follow-Ups

- **Pre-commit hook coverage for minimum-net-diff.** The Implementer Self-Check is prose-only; enforcement relies on the implementer running `git diff <merge-base>..HEAD` and the verify reviewer doing the same. A future lightweight hook could surface out-of-scope hunks automatically at commit time.
- **Mermaid / ASCII diagram maintenance cost.** The README workflow map now carries two views (ASCII block + Mermaid) of the same Phase A–D graph with re-entry arrows. Drift between the two is a future risk; a single source of truth (one diagram format) would be cleaner.
- **Historical RELEASE-NOTES entries mention `merge-workflow`.** Left as historical record per the deletion-task's scope decision. Future readers of release notes see `merge-workflow` in entries from before this refactor and should read the current "Unreleased — unified integration-workflow refactor" entry for the retirement context.
- **Stage 2 RESULTS.md co-location.** After this document's relocation to `docs/plans/`, a follow-up session should decide whether to retain the companion `PLAN.md` at the worktree root or also move it to `docs/plans/` alongside the sibling entries' convention of paired `*-plan.md` / `*-results.md` files.

## Reproducibility

This refactor is a skill-design change; there is no analysis pipeline to regenerate. To reconstruct the full edit history: `git log --follow docs/plans/2026-04-19-unified-integration-workflow-results.md` after the relocation commit, or `git log 92a685b..HEAD -- skills/ agents/ README.md CLAUDE.md RELEASE-NOTES.md CATEGORIES.md` for the full diff against merge base.
