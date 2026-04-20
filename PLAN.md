# Flexible Integration-Workflow + General Semantic-Merge Refactor

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This refactor edits skill files — every implementer and reviewer dispatch MUST additionally load `document-skills:skill-creator` and apply its conciseness, progressive-disclosure, and one-source-of-truth discipline. Preserve carefully-tuned content (Red Flags tables, rationalization lists, RA-framing language) per `/CLAUDE.md §Skill Changes`. Steps use checkbox (`- [ ]`) syntax.

**Objective:** (a) Make `integration-workflow` Phase B a flexible, review-led loop by dropping the Tier 1/2/3 matrix, the shortcut-axis evaluation, the named recon/verify split, and the two-commit implementer contract — replaced by an Integration Intent mechanism in PLAN.md that lets the reviewer drive the fix-review cycle through per-task annotations. (b) Generalize `semantic-merge/SKILL.md` on top of the global `semantic-merge-integration` skill so it reads coherently for any vertical (analysis, writing, modeling) and any caller (agent, orchestrator, human at terminal) — dropping the Standalone/Delegated mode split, the named return-field contract, and in-skill dispatch blocks; stating a 1+N commit shape as *one* possible workflow.

**Methodology:** Skill-design refactor. No code, no data, no pipeline. Everything lives in superRA skill files and cross-cutting docs (`plan-anatomy.md`, `agents/`, `agent-orchestration`, `README.md`, `CATEGORIES.md`, `RELEASE-NOTES.md`, `using-superRA` Skill-Load Manifest). The round-1 `refactor-and-integrate` checklist and the canonical dispatch shape are preserved unchanged.

**DRY audit baseline.** Do not restate content that is already carried by a skill in the integration stage's load set. The following are linked, never restated: APPROVE/REVISE adjudication (`agent-orchestration §Handling Reviewer Feedback`), dispatch shape (`agent-orchestration §Dispatch Templates`), reviewer-owns-verdict-flip + annotation etiquette (`agents/reviewer.md`, `agents/implementer.md`, `plan-anatomy.md`), User Decisions Log (`handoff-doc`), re-entry / Changing Plans (`planning-workflow §Changing Plans`), minimum-net-diff / scope-by-integration-status / drift-test integrity (`refactor-and-integrate` + references), stop-point discipline (`using-superRA §Universal Principles`). **Exception:** `execution-workflow` is NOT in the integration stage's load set; the per-task fix-review inner loop is therefore restated tightly in `integration-workflow` Phase B Step 3 (with the integration-specific twist — REVISE-status scope, APPROVED-integration refusal, mechanical merge first) rather than linked.

**Output:** Modified `skills/integration-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/agent-orchestration/SKILL.md`, `agents/reviewer.md`, `agents/implementer.md`; peripheral surfaces synced (`README.md`, `skills/CATEGORIES.md`, `RELEASE-NOTES.md`, `skills/using-superRA/SKILL.md`). No code or data outputs.

**Expected Results:** (a) `integration-workflow` Phase B is ~half its current length; Tier/shortcut/two-commit/recon-verify vocabulary is fully removed. (b) `semantic-merge/SKILL.md` reads coherently for a human running `git merge` on a non-analysis branch with no hidden orchestrator assumptions. (c) Integration Intent is a first-class PLAN.md section with documented lifecycle. (d) Parallel reviewers are a supported orchestration pattern (extension in `agent-orchestration`, not duplicated in workflow skills).

**Pipeline:** N/A (skill refactor; single entry point is the git history of this branch).

---

## Workflow Status

- [ ] **Plan approved** — researcher signed off on this plan
- [ ] **Execution complete** — all tasks `**Review status:** APPROVED`
- [ ] **Drift tests created** — N/A for skill refactor; Task 6 end-to-end dry-read serves as the substitute (same pattern as round 1)
- [ ] **Refactored** — Phase B verify reviewer APPROVED on cumulative diff
- [ ] **Docs finalized** — matured RESULTS.md + doc-reviewer APPROVED
- [ ] **Merged** — branch merged or PR opened/updated

---

## Decisions

**2026-04-20 — Round 3 extensions (user review of Rounds 1–2 landed skills).** After reading the full set of skills produced by Rounds 1–2, the researcher marked up the files with inline edits and five `<!-- -->` questions. Prose-only edits (grammar, §Concurrent Writers → §Parallelization and Worktree Isolation generalization, background-dispatch preference, §Difficulty and Agent Type) landed in commit `a8c4113`.

Structural changes, mapped to existing tasks per the "prefer modifying existing task blocks" rule:

- **Task 1 (Phase B rewrite)** — reopened. Three new concerns, all inside Phase B: (a) loosen hardcoded `merge-base..origin/<base-branch>` to a researcher-selectable integration base (C1); (b) collapse duplicated implementer template in Step 3b to a pointer at `agent-orchestration §Dispatch Templates` + integration-specific annotation (C2); (c) triage §Red Flags — keep only bullets that warn against a rationalization not already covered by a `[BLOCKING]` item elsewhere (C3). Step set extended with 6–8.
- **Task 4 (§Concurrent Writers extension)** — reopened. The section rename (→ §Parallelization and Worktree Isolation) and the branch-naming flip (`<branch>/parallel/<slug>`) originated here and belong here. Step set extended with 4.
- **Task 5 (peripheral sync)** — reopened. Cross-references to the old section name and old branch-naming convention live across README, RELEASE-NOTES, CATEGORIES, using-superRA, and worktree-harness-fallback; these are the same peripheral surface Task 5 owns. Step set extended with 5.
- **Task 6 (end-to-end dry-read)** — reopened. Adds a Round 3 scenario pass covering the non-main integration base, collapsed Step 3b dispatch, trimmed Red Flags, and relaxed merge-commit structure. Step set extended with 8–11.
- **New Task 7 — refactor-and-integrate extensions (C4 + C5).** Genuinely new: `refactor-and-integrate` was explicitly "preserved unchanged" in Round 2's Project Conventions, so these concerns fall outside every existing task's scope. Bundles §Scope by Integration Status evaluation (C4) and merge-quality two-commit relaxation (C5) because both live in the same skill and share a DRY rationale.
- **New Task 8 — Changing Plans protocol + Stale Content Checklist polish.** Genuinely new: `planning-workflow/SKILL.md` and `handoff-doc/SKILL.md` were preserved in Rounds 1–2 (Task 2 touched only `handoff-doc/references/plan-anatomy.md`, not the parent SKILL.md). Driven by the experience of restructuring Round 3 itself — the "prefer modifying existing task blocks" rule needed operationalization, and a staleness sweep belongs as a discrete protocol step.

DAG cascade. Reopening Tasks 1, 4, 5, 6 clears their per-task `**Review status:**` and `**Integration status:**` because each gets new skill-prose work. No task's objective or output is wholesale-rewritten — Round 3 steps extend the Round 2 steps without invalidating them — so reopened tasks keep their existing step history intact and append Round 3 steps. Downstream audit: Task 5 depended on 1–4 originally; reopening 1 and 4 means 5's sync must re-run; Task 6 depended on 1–5, so it re-runs last. Tasks 7 and 8 have no upstream dependency; Task 6's Round 3 scenarios pick up Task 7 but not Task 8 (Task 8 is protocol polish, not behavior that a dry-read scenario exercises).

Authorization: explicit user request on 2026-04-20 to update the plan with these changes via the Changing Plans protocol.

---

## Project Conventions

Walked at planning time (2026-04-19). Re-walk on-demand only. Round 1 walked the same surfaces 2026-04-19; summaries below are carried forward because the repo state is unchanged except for the round-1 refactor itself (which round 2 partially revises).

### Repo root
- `/CLAUDE.md` (HEAD at f346161): Contributor guide for superRA. Four workflow principles (implementer-reviewer pair, handoff docs as auditable record, fast-early-strict-before-merge with semantic-merges, autonomous with human-in-loop). Architectural pattern: lean agents, rich references, flat skills/ layout. DRY with one source of truth per concern. Skill edits require reading before changing, one problem per commit, testing on at least one harness.
- `/README.md`: superRA skill inventory by Workflow / Domain / Utility / Meta categories. Needs peripheral update in Task 5.

### Module-level docs walked
- `skills/CATEGORIES.md`: Workflow / Domain / Utility / Meta grouping table; stays in sync with README.
- `skills/using-superRA/SKILL.md` §Skill-Load Manifest: authoritative `Stage:` → loads map. `integration` and `merge` rows to be revisited in Task 5.
- `skills/agent-orchestration/SKILL.md` §Dispatch Templates + §Handling Reviewer Feedback + §Concurrent Writers Require Worktree Isolation: canonical dispatch shape and parallel-dispatch pattern; §Concurrent Writers currently frames around implementers (Worktree field is implementer-only per SKILL.md:143) — Task 4 extends with a parallel-reviewer note.
- `skills/handoff-doc/references/plan-anatomy.md`: PLAN.md anatomy. Integration-status lifecycle paragraph (line 179, round-1 Task 8) is symmetric with Review-status and stays. Task 2 adds a new `## Integration Intent` subsection.
- `skills/refactor-and-integrate/SKILL.md` + references: minimum-net-diff, scope-by-integration-status, drift-test integrity. **Preserved unchanged in Rounds 1–2; Round 3 Task 7 revisits §Scope by Integration Status and `merge-quality.md` §Two-commit structure.**
- `skills/planning-workflow/SKILL.md`: re-entry protocol covering B→B, C→B, D→B, mid-workflow scope change. **Mostly preserved in Rounds 1–2; Round 3 Task 8 tightens §User Feedback and Changing Plans (was §Changing Plans) — operationalize the "prefer modifying existing task blocks" rule and add a pre-commit staleness sweep.** The round-1 B→B trigger sentence in `plan-anatomy.md:179` stays.
- `skills/integration-workflow/SKILL.md`: target of the main rewrite. Currently ~450 lines; carries Tier matrix (Phase B Step 2), shortcut-axis evaluation, two-commit implementer contract (Step 3), and recon/verify naming split — all removed by Task 1.
- `skills/semantic-merge/SKILL.md`: target of Task 3. Currently carries Standalone/Delegated mode split, named return-field contract, in-skill dispatch blocks, analysis-only vocabulary — all removed.
- `~/.claude/skills/semantic-merge-integration/SKILL.md` (global): domain-neutral baseline for Task 3's rewrite. Read-only reference.

### Not walked (not reachable from the planned diff)
- `/hooks/` — no hook changes expected.
- `skills/econ-data-analysis/**` — domain vertical unaffected.
- `skills/report-in-markdown/**`, `skills/worktree-data-sync/**`, `skills/zotero-paper-reader/**`, `skills/execution-workflow/**` — unaffected; execution-workflow's inner loop is restated (not linked) in Task 1 output because it is not in the integration stage's load set.

---

### Task 1: Rewrite `integration-workflow` Phase B
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:**

**Script:** N/A
**Input:** current `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/agent-orchestration/SKILL.md` §Dispatch Templates + §Handling Reviewer Feedback + §Parallelization and Worktree Isolation, `skills/refactor-and-integrate/SKILL.md` + references (linked, unchanged).
**Output:** Phase B section in `skills/integration-workflow/SKILL.md` — review-led loop; Tier matrix and shortcut-axis evaluation removed; two-commit implementer contract replaced with a brief "1+N: mechanical merge first, refactors after" note that points at `semantic-merge`; recon/verify naming split collapsed to "integration reviewer"; integration base branch is researcher-selectable (not hardcoded to main); Step 3b dispatch collapsed to a pointer at `agent-orchestration §Dispatch Templates` + integration-specific annotation; §Red Flags trimmed to bullets that warn against a rationalization not already covered by a `[BLOCKING]` item in `refactor-and-integrate` or `using-superRA` §Universal Principles; §Always list, §Phase Map diagram, and metadata block kept in sync.

- [x] **Step 1: Describe — read the current Phase B end-to-end**

  Read `skills/integration-workflow/SKILL.md` lines 85–199 (Phase B proper) plus the Red Flags list (lines ~394–424) and the Integration block (lines ~428–452). Identified all removal targets: Tier 1/2/3 matrix, two-axis shortcut evaluation, recon reviewer, verify reviewer, two-commit structure, delegated mode.

- [x] **Step 2: Draft the four-step Phase B skeleton**

  Written Phase B as four steps: (1) Dispatch integration reviewer — walks branch diff and main-side diff, writes Integration Intent if material changes found, annotates per-task blockquotes, flips REVISE; (2) Orchestrator adjudicate — zero annotations fast-path or batch AskUserQuestion; (3) Fix-review loop — 3a mechanical merge first (semantic-merge when conflicts/material changes), 3b refactor commits scoped to REVISE tasks with dispatch template, 3c re-dispatch reviewer until APPROVE; (4) Flip Refactored milestone when all tasks APPROVED and Intent section empty.

- [x] **Step 3: Update the Phase Map diagram and re-entry arrows**

  Phase Map updated — removed "Recon-Driven, Two Shortcut Axes" sub-heading and "Internal Structure" section. Re-entry arrows (B→B, C→B, D→B) preserved. D→B comment updated to reference Phase D pre-merge check.

- [x] **Step 4: Update Red Flags + Always + metadata blocks**

  Red Flags: removed Tier, recon reviewer, verify reviewer, two-commit structure, shortcut axes, delegated mode bullets. Always list: removed Tier/shortcut/recon-verify wording; updated semantic-merge bullet to describe intent-based resolution trigger (reviewer decides, not Tier gate). Metadata §Invokes updated to drop "REQUIRED on Tier 2/3" qualifier.

- [x] **Step 5: Validate — walk the four workflow principles**

  All four workflow principles preserved. `grep -n "Tier 1\|Tier 2\|Tier 3\|recon reviewer\|verify reviewer\|two-commit\|shortcut ax" skills/integration-workflow/SKILL.md` → empty. Committed.

- [x] **Step 6 (Round 3, C1): Loosen integration base to be researcher-selectable**

  Added an "Integration base" intro paragraph to Phase B establishing that `<base-branch>` is researcher-specified (default `origin/main`, overridable at `execution-workflow` Step 4). Updated the Step 1 dispatch steering to say "base-branch-side" / "integration base" instead of "main"; Step 2 zero-annotation path same; Step 3a "when the base branch has diverged" / "when `<base-branch>` is an ancestor".

- [x] **Step 7 (Round 3, C2): Collapse Phase B Step 3b dispatch block**

  Dispatch block deleted. Replaced with a paragraph pointing at `agent-orchestration §Dispatch Templates` for canonical shape + a four-bullet list of integration-stage additions (`Stage: integration`, `Tasks in scope:` + refusal-to-refactor-APPROVED semantics + IMPLEMENTED flip, mechanical merge must land first, drift tests re-run after affecting refactor). Grep `Agent(subagent_type:` against `integration-workflow/SKILL.md` now shows three hits: one Phase B Step 1 reviewer dispatch (canonical for that stage) + two Phase C doc-writer / doc-reviewer dispatches (out of scope for Step 7). Phase B Step 3b is dispatch-block-free.

- [x] **Step 8 (Round 3, C3): Triage §Red Flags**

  Cut 11 Never bullets → 4; 12 Always bullets → 1. Kept: (a) Never skip the integration reviewer; (b) Never advance to Phase D without a base-branch freshness check; (c) Never hand off Phase C Step 4 to a subagent; (d) Never clean up the worktree before the merge/push completes; (e) Always scope new-drift-test authoring to non-APPROVED tasks but run the full suite. Dropped bullets were either sequencing reminders already stated in the phase prose, or restatements of `refactor-and-integrate` / `using-superRA` universal principles; one pointer block at the end of the section names the cross-cutting owners. Added a lede sentence making the triage criterion explicit.

---

### Task 2: Add `## Integration Intent` anatomy to `plan-anatomy.md`
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:** APPROVED

**Script:** N/A
**Input:** `skills/handoff-doc/references/plan-anatomy.md`, existing `## Decisions` anatomy entry as a structural template.
**Output:** New `## Integration Intent` subsection in `plan-anatomy.md`, placed between the existing `## User Decisions Log` and `## Task Block Anatomy` sections. Documents purpose, ownership (reviewer-only; implementer hands-off), lifecycle (written by reviewer when Phase B scan finds material main-side change → per-item removal on dependent-task APPROVE → section removal when empty), format (one bullet per incoming-change cluster, each bullet names affected task IDs + one-sentence why-it-matters), and placement (directly after `## Decisions` if present, before the first task block).

- [x] **Step 1: Describe — pattern-match against `## Decisions`**

  Read `plan-anatomy.md:99–120` (`## User Decisions Log`) and the existing `## Decisions` placement rule at line 67. The Integration Intent section follows the same placement logic: header context → `## Workflow Status` → `## Decisions` (optional) → `## Integration Intent` (optional) → `---` → task blocks. Confirmed: `## Decisions` placement note updated to include `## Integration Intent` in the order.

- [x] **Step 2: Draft the anatomy entry**

  Added new `## Integration Intent` section between `## User Decisions Log` and `## Task Block Anatomy` in `plan-anatomy.md`. Covers: (a) purpose paragraph bridging Phase B main-side scan to per-task fix-review loop; (b) ownership (integration reviewer only; implementer hands-off; orchestrator `→ orchestrator:` annotations only); (c) lifecycle (write on Phase B Step 1 scan finding material changes → remove items as dependent tasks hit `APPROVED` → remove section when empty); (d) format code block with two-line blockquote cluster (`Main-side change` + `Adaptation needed`) naming affected task IDs explicitly.

- [x] **Step 3: Validate — coherence check against B→B trigger**

  B→B trigger sentence at `plan-anatomy.md §Field-by-Field Notes` confirmed consistent: integration reviewer's annotation gates the flip. Rewrote the `**Integration status:**` paragraph to replace "recon reviewer", "unified implementer", "verify reviewer" with "integration reviewer (annotation pass)", "implementer", "integration reviewer (verify pass)" — reviewer-owns-verdict-flip semantics and B→B trigger sentence preserved. Also updated `Refactored` checkbox in the Workflow Status template from "verify reviewer" to "integration reviewer".

---

### Task 3: Rewrite `semantic-merge/SKILL.md` as general-purpose skill
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:** APPROVED

**Script:** N/A
**Input:** current `skills/semantic-merge/SKILL.md`, global `~/.claude/skills/semantic-merge-integration/SKILL.md` as tone/structure baseline.
**Output:** Rewritten `skills/semantic-merge/SKILL.md` that reads as a skill for thoughtful merging — usable by a human at the terminal, by the orchestrator running it directly, or by a dispatched agent, with the same text. Domain-neutral vocabulary. 1+N commit shape stated as *one possible workflow*, not mandated.

- [x] **Step 1: Describe — read the global baseline + current superRA version**

  Read `~/.claude/skills/semantic-merge-integration/SKILL.md` end-to-end. Read `skills/semantic-merge/SKILL.md` end-to-end. Identified: (a) global skill content to reuse: intent-first framing, diffs for inferring intent, regeneration over hand-edit for derived artifacts, ask-user-when-ambiguous discipline; (b) superRA-specific content to retain: drift-test integrity as safety net, RA framing, handoff-doc coherence with PLAN.md/RESULTS.md conflict escalation to `planning-workflow §Changing Plans`; (c) removal targets: Standalone/Delegated mode split, named return-field contract, in-skill dispatch blocks, Tier 1/2/3 matrix, domain-specific vocabulary (`excess_return`, `variable_construction.py`, `Table 3`, econometric specs, sample filters).

- [x] **Step 2: Draft the rewritten skill**

  Written with structure: frontmatter → Overview → Core principle → The process (6 steps: ground → understand intent → integration map → ask user → resolve/integrate → verify) → Working principles → When to ask the user → What to report → Red Flags → Integration. 1+N commit shape stated explicitly as one possible workflow. Domain-neutral vocabulary throughout; one illustrative example in Step 4 (outcome variable construction) without analysis-specific names.

- [x] **Step 3: Remove dispatch-focused content**

  Deleted: Invocation Pattern section (two-mode split), Mode-aware verification table, in-skill `Agent(subagent_type: ...)` dispatch blocks for Tier 2/3, "What to Report — delegated mode" return-field contract, Tier 1/2/3 classification matrix. Integration block updated to "Called by `integration-workflow` Phase B Step 3 mechanical-merge commit, when conflicts or material main-side changes exist; Phase D re-sync when main has advanced; or standalone by any agent or human."

- [x] **Step 4: Validate — terminal-use dry-read**

  Dry-read passed as a human running `git merge main` on a paper-drafting branch: no dispatching-caller assumptions, no data-analysis vocabulary except the illustrative example (which uses neutral phrasing). Grep for `Standalone\|Delegated\|excess_return\|Table 3\|econometric\|variable_construction\|delegated mode` → empty. Grep for `Tier 1\|Tier 2\|Tier 3\|recon reviewer\|verify reviewer\|two-commit\|Agent(subagent` → empty.

---

### Task 4: Generalize `agent-orchestration §Parallelization and Worktree Isolation`
**Depends on:** *(none)*
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `skills/agent-orchestration/SKILL.md` (section was §Concurrent Writers Require Worktree Isolation in Round 2; renamed to §Parallelization and Worktree Isolation in Round 3 as part of this task's extension).
**Output:** Section now covers any parallel subagent batch (not just implementers). Includes: (a) parallel-reviewer pattern on disjoint diff slices with orchestrator-aggregated verdicts; (b) background-dispatch preference so the orchestrator stays available to the user; (c) new §Difficulty and Agent Type subsection covering model-tier selection (lower-tier for simple tasks / follow-up checks; higher-tier for first-pass adversarial review); (d) new §Worktree lifecycle guidance: orchestrator creates worktree with raw git branching off its current branch, never via `Agent`-tool `isolation: "worktree"` (which branches off main's HEAD). Branch-naming convention flipped to `<branch>/parallel/<slug>` so the `merge-guard` hook can exempt `*/parallel/*` source refs regardless of parent-branch name.

> **Review notes (integration):**
> 1. [MINOR] `skills/agent-orchestration/SKILL.md` line 125 area — the Reviewer Dispatch Template block shows no `Worktree:` optional field line, while the Implementer block (line 115) shows `Worktree: <absolute path>   # optional — parallel-dispatch only`. The `Worktree:` field spec paragraph (line 145) covers both roles in prose, so an orchestrator who reads the full spec will find it. But a reader building a reviewer dispatch from the template block alone won't see the field as an option. Pre-existing gap, not introduced by this commit; low priority since the spec paragraph is just a few lines below. Task 5 or a targeted follow-on could add `Worktree: <absolute path>   # optional — parallel-reviewer pattern only` to the Reviewer template block for symmetry.

- [x] **Step 1: Describe — read the current §Concurrent Writers**

  Read `skills/agent-orchestration/SKILL.md` §Concurrent Writers Require Worktree Isolation plus the `Worktree:` field spec (SKILL.md:143). Identified core pattern (isolated worktree per concurrent writer) and the implementer-specific framing ("Applies to implementers only") that needed generalizing.

- [x] **Step 2: Draft the extension**

  Added one paragraph to §Concurrent Writers (after the implementer-default sentence): parallel reviewers on disjoint worktrees when diff exceeds ~150k threshold; orchestrator splits by task ID / file subtree / commit range; aggregates per-slice verdicts; `Worktree:` field applies to reviewers in this configuration. Updated the `Worktree:` field spec note at SKILL.md:143 to read "parallel-dispatch only; implementers always, reviewers when using the parallel-reviewer pattern in §Concurrent Writers".

- [x] **Step 3: Validate — cross-read with Task 1**

  Grepped: `grep -n "parallel reviewer\|reviewer.*worktree"` returns hits at lines 79 and 145. Task 1's Phase B Step 1 + Step 3 references to "parallel siblings on worktrees" work against this extension.

- [ ] **Step 4 (Round 3): Rename section, generalize scope, add subsections**

  Section rename: `§Concurrent Writers Require Worktree Isolation` → `§Parallelization and Worktree Isolation`. Broaden the opener from "implementers by default" to "any parallel subagent batch". Add: (a) background-dispatch preference paragraph; (b) new `§Difficulty and Agent Type` subsection (tier-matching guidance — lower-tier for simple / follow-up, higher-tier for first-pass review); (c) worktree-lifecycle paragraph covering orchestrator-creates-with-raw-git and the `Agent`-tool `isolation: "worktree"` anti-pattern; (d) `--from "$(pwd)"` seeding guardrail. Branch-naming convention flipped to `<branch>/parallel/<slug>` inside this section (ownership split table, examples, merge-back command). Reviewer-template block at SKILL.md §Dispatch Templates gets the optional `Worktree:` field that Task 4's round-2 review note flagged as missing (R1). Partial work already landed in commit `a8c4113`; this step finalizes. Commit.

---

### Task 5: Sync peripheral surfaces
**Depends on:** Tasks 1, 2, 3, 4
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `README.md`, `skills/CATEGORIES.md`, `RELEASE-NOTES.md`, `skills/using-superRA/SKILL.md` §Skill-Load Manifest, `agents/reviewer.md`, `agents/implementer.md`.
**Output:** Peripheral docs updated to match Round 2's language: no residual "recon/verify reviewer", "Tier 1/2/3", "delegated mode", "Standalone mode" anywhere in the active skills graph; Skill-Load Manifest `integration` / `merge` rows simplified; `agents/reviewer.md` §What You Own + §Editing Etiquette extended to cover Integration Intent ownership; `agents/implementer.md` §What You Own extended with hands-off note for Integration Intent; RELEASE-NOTES.md has a new "Unreleased" entry. Also folded in MINOR advisories R1–R4.

- [x] **Step 1: Update agent files**

  `agents/reviewer.md` §What You Own: replaced stale "recon reviewer / verify reviewer" integration-status flip language with "integration reviewer (annotation pass) / integration reviewer (verify pass)"; added `## Integration Intent` ownership bullet — writes at Phase B Step 1, per-item removes when last named dependent task reaches APPROVED, section-removes when empty; no other role edits it. §Editing Etiquette: added sentence that inline-edit + boundary-preservation rules apply to Integration Intent edits too. Pre-commit self-check: updated to name `## Integration Intent` writes/removes as integration-reviewer-owned.

  `agents/implementer.md` §What You Own: reworded integration-status line to drop "two-commit" and "recon/verify reviewer" vocabulary; added explicit hands-off paragraph for `## Integration Intent`.

- [x] **Step 2: Update Skill-Load Manifest**

  `skills/using-superRA/SKILL.md`: replaced stale paragraph below the manifest table ("delegated mode" / "Tier 2/3" language) with neutral wording describing when `merge` stage is used and how Phase B loads `semantic-merge`.

- [x] **Step 3: Update README, CATEGORIES, RELEASE-NOTES**

  `README.md`: Mermaid INT2 node updated (removed "recon reviewer + unified implementer + verify reviewer" / "Tier 2/3" language); integration-workflow row updated in skill table; semantic-merge row made vertical-neutral; "How It Works" paragraph updated; "invokes semantic-merge internally on Tier 2/3" fixed.
  `skills/CATEGORIES.md`: integration-workflow row simplified; semantic-merge row made vertical-neutral.
  `RELEASE-NOTES.md`: added new `## Unreleased — flexible integration-workflow + general semantic-merge refactor` heading with four bullets.

- [x] **Step 4: Validate — sweep**

  `grep -rn "recon reviewer|verify reviewer|delegated mode|Standalone mode" skills/ agents/ README.md` → empty (active content only; RELEASE-NOTES historical entries excluded). Remaining `two-commit` hits are in `refactor-and-integrate/SKILL.md` merge-quality section (legitimate 1+N merge commit vocabulary, not the removed integration-workflow two-commit contract). R1–R4 advisory fixes applied; see RESULTS.md Task 5 for per-item notes.

- [ ] **Step 5 (Round 3): Cross-surface sweep for renames + branch-naming flip**

  Three renames need sweeping across active surfaces: (a) `§Concurrent Writers Require Worktree Isolation` → `§Parallelization and Worktree Isolation`; (b) `parallel/<analysis-branch>/<slug>` → `<analysis-branch>/parallel/<slug>`; (c) `§Changing Plans` → `§User Feedback and Changing Plans` (renamed in `planning-workflow/SKILL.md` per commit `a8c4113`; active references in at least `semantic-merge`, `handoff-doc`, `execution-workflow`, `integration-workflow`, `refactor-and-integrate/references/merge-quality.md`, `using-superRA`). Run `grep -rn "§Concurrent Writers\|parallel/<branch>/<slug>\|parallel/<analysis-branch>\|parallel/\*\|parallel/\$BR\|§Changing Plans" skills/ agents/ README.md RELEASE-NOTES.md hooks/`. Classify hits as active (update) or historical (leave) — `docs/plans/2026-04-17-*` round-1 artifacts and prior-round `RESULTS.md` log entries are historical. Also add a RELEASE-NOTES.md entry for the Round 3 extensions (flexible integration base, collapsed Step 3b dispatch, Red Flags triage, refactor-and-integrate simplifications, `§Parallelization and Worktree Isolation` rename, `<branch>/parallel/<slug>` naming flip, `§Difficulty and Agent Type`, Changing Plans protocol polish + Stale Content Checklist addition). Re-run the grep; confirm zero active hits remain. Commit.

---

### Task 6: End-to-end dry-read verification
**Depends on:** Tasks 1, 2, 3, 4, 5, 7
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** All round-2 refactored skills + agent files + peripheral docs.
**Output:** Walk-through notes in `RESULTS.md` covering seven scenarios; confirms the refactor is internally coherent and the round-1 invariants still hold; any [ADVISORY] stale-vocabulary hits fixed in-place (no tuned content touched); any [BLOCKING] issue opened as a review-notes entry on the relevant prior task for re-entry.

- [x] **Step 1: Scenario (a) — no-main-movement fast path**

  Hypothetical branch: APPROVED PLAN.md, code-complete, `origin/main` has not advanced since merge-base. Walk Phase A (drift tests authored, all pass) → Phase B Step 1 (integration reviewer walks both diffs; main-side scan finds nothing; no Integration Intent section written; no per-task annotations; Integration status stays APPROVED across all tasks) → Step 2 (orchestrator reads PLAN.md, no adjudication needed) → Step 3 (skipped — no REVISE tasks; mechanical merge is a no-op fast-forward since merge-base is main tip) → Step 4 (Refactored milestone flips) → Phase C → Phase D. Confirm the flow terminates cleanly.

- [x] **Step 2: Scenario (b) — Integration Intent path**

  Hypothetical branch: main has advanced with a cross-cutting refactor of a shared utility; incoming change touches the utility plus a README section that two of this branch's tasks also edit. Walk Phase B Step 1 (reviewer writes Integration Intent section with two bullets + per-task annotations; flips two tasks to REVISE); Step 2 (orchestrator batches a single user-decision on adaptation approach); Step 3 (mechanical merge commit first via `semantic-merge`; then refactor commits scoped to the two REVISE tasks; reviewer re-review APPROVES both, removes review-notes, removes the corresponding Integration Intent bullets, and when both bullets are gone, removes the section). Confirm the ownership contract (reviewer-only for Intent writes + removes) holds.

- [x] **Step 3: Scenario (c) — parallel reviewers on a large diff**

  Hypothetical branch: 20+ tasks; Phase B Step 1 needs to walk a cumulative diff that would exceed one reviewer's context. Walk the orchestrator split: three reviewers dispatched on disjoint worktrees, each walking a ~7-task slice; their verdicts aggregated; per-task annotations land in PLAN.md as if from one reviewer. Confirm the Task 4 extension paragraph covers the mechanics; confirm disjoint-scope invariant holds.

- [x] **Step 4: Scenario (d) — 1+N with parallel refactor implementers**

  Hypothetical continuation of Scenario (b) but with five tasks flipped to REVISE and adaptation work that is independent across them. Walk Step 3's mechanical-merge commit (one implementer, serial, branch-wide) then the N refactor commits dispatched as five parallel sibling implementers on worktrees. Confirm the 1+N shape reads as "one possible workflow" in both `integration-workflow` Phase B and `semantic-merge`, not mandated.

- [x] **Step 5: Scenario (e) — B→B re-entry**

  Hypothetical: Phase B had approved; while Phase C was mid-flight, main advanced again. Walk the C→B re-entry via `planning-workflow §Changing Plans`: `Refactored` unchecks, re-enter Phase B Step 1; reviewer re-walks; new Integration Intent bullet written if material; fix-review loop re-runs. Confirm the existing `plan-anatomy.md:179` B→B trigger sentence (round-1 Task 5) still reads correctly against Task 2's rewritten `**Integration status:**` paragraph.

- [x] **Step 6: Scenarios (f) + (g) — plan-change escalation and standalone semantic-merge**

  (f): Phase B Step 1 reviewer surfaces a finding that is a substantive restructure (a task needs to be removed because main deleted the feature it analyzed). Walk the escalation to `planning-workflow §Changing Plans` — orchestrator authors the proposal, researcher decides, PLAN.md updated inline, re-entry.

  (g): A human runs `git merge` at the terminal on a paper-drafting branch that has no PLAN.md and no drift tests. Walk the rewritten `semantic-merge/SKILL.md` from top to bottom. Confirm nothing in the skill forces the existence of a PLAN.md, drift tests, or a dispatching caller; confirm the handoff-doc coherence and drift-test integrity clauses degrade gracefully to no-ops when those artifacts are absent.

- [x] **Step 7: Write findings to `RESULTS.md`; fix ADVISORY issues in place; commit**

  For each scenario, write a short paragraph in RESULTS.md noting pass/fail and any residual stale vocabulary or coherence gaps. Fix [ADVISORY] items in place (naming-only, prose-only). Open [BLOCKING] items as review-notes entries on the relevant prior task for re-entry. Commit.

- [ ] **Step 8 (Round 3): Scenario — non-main integration base**

  Hypothetical branch integrating into `release/2026-Q2`. Walk Phase B Step 1 dispatch + Integration Intent scan with `<integration-base>=release/2026-Q2`. Confirm no hardcoded main vocabulary remains in Phase B. Covers Task 1 Step 6.

- [ ] **Step 9 (Round 3): Scenario — collapsed Phase B Step 3b dispatch**

  Walk the orchestrator dispatching an implementer via the canonical `agent-orchestration §Dispatch Templates` + integration-specific annotation. Confirm the implementer has every field it needs (scope list, mechanical-merge invariant, drift-test re-run order). Covers Task 1 Step 7.

- [ ] **Step 10 (Round 3): Scenario — §Red Flags regression check + refactor-and-integrate simplifications**

  List the rationalizations that the Round 2 §Red Flags caught in `integration-workflow`. For each, confirm either (i) the bullet survived Task 1 Step 8, or (ii) another surface (checklist, skill body) catches it. Separately, walk Task 7's output: if §Scope by Integration Status was dropped, verify implementer-refusal semantics still live somewhere; walk a trivial one-commit merge and confirm `merge-quality.md` reads as one-commit-allowed without losing the "separate when different intent" discipline. Covers Task 1 Step 8, Task 7.

- [ ] **Step 11 (Round 3): Write findings + commit**

  Append a Round 3 section to `RESULTS.md` covering Steps 8–10 + the Task 4 / Task 5 cross-surface verification. Fix any [ADVISORY] stale-vocabulary hits in place. Surface any [BLOCKING] issues as review-notes on the responsible task for re-entry.

---

### Task 7: Simplify `refactor-and-integrate` — §Scope by Integration Status + merge-quality two-commit mandate (C4 + C5)
**Depends on:** Task 1 (Task 1 Step 7's collapse of the Phase B Step 3b dispatch may already carry the scope-list semantics that §Scope by Integration Status currently codifies)
**Review status:**
**Integration status:**

**Script:** N/A
**Input:** `skills/refactor-and-integrate/SKILL.md` §Scope by Integration Status; `skills/refactor-and-integrate/references/merge-quality.md` §How-To §Two-commit structure + associated gated checklist items; Task 1 Step 7's output (to see what dispatch-level scope info now lives in Phase B Step 3b).
**Output:** (a) §Scope by Integration Status either dropped (if the invariant it guards — implementer refusing to touch APPROVED tasks even when named in a dispatch — is fully expressible in the Implementer Self-Check and Task 1 Step 7 already carries the scope list in Phase B Step 3b) or trimmed to just that invariant. (b) `merge-quality.md` reframed from "two commits required" to "separate commits when intent differs" — mechanical-merge and intent commits MAY be combined when both are trivial. Gated checklist items downgraded from `[BLOCKING]` to `[ADVISORY]` where the blocking rationale no longer holds. `integration-workflow` Phase B and `semantic-merge` 1+N language already read non-mandatorily (Round 2 Tasks 1 + 3); no change there.

Rationale for bundling C4 + C5: both live in the same skill (`refactor-and-integrate`) which Round 2 explicitly left untouched. Both are "relax DRY/mandate" moves driven by the same review pass. Single task preserves atomic-commit discipline for this skill's Round 3 delta.

- [ ] **Step 1: Describe — what each section is load-bearing for**

  §Scope by Integration Status: isolate content that is NOT expressible as a dispatch-time `Tasks in scope:` list (implementer-refusal semantics, reviewer out-of-scope boundary). §Two-commit structure: identify failure modes the discipline prevents (conflated intent, un-reviewable mechanical hunks) and note which survive under a "separate when intent differs" rule.

- [ ] **Step 2: Apply**

  §Scope by Integration Status: drop / trim / keep per Step 1. If dropped, verify the Implementer Self-Check and the reviewer's Pre-Review Scope Check still carry the invariant. §Two-commit structure: rewrite the How-To to frame the two-commit shape as a convention (not a mandate); downgrade severity markers on the gated checklist; keep the templates as examples of the separated case.

- [ ] **Step 3: Validate**

  Grep `skills/ agents/` for `§Scope by Integration Status` cross-references; update any that break. Cross-read against `semantic-merge/SKILL.md` (the 1+N "one possible workflow" language) and `integration-workflow` Phase B to confirm nothing elsewhere now demands two commits in contradiction. Commit.

---

### Task 8: Tighten Changing Plans protocol + Stale Content Checklist
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:**

**Script:** N/A
**Input:** `skills/planning-workflow/SKILL.md` §User Feedback and Changing Plans (renamed from §Changing Plans in Round 3 commit `a8c4113`); `skills/handoff-doc/SKILL.md` §What Counts as Stale.
**Output:** (a) Changing Plans protocol Step 3 operationalizes the "prefer modifying existing task blocks" rule with a task-list walk that names every affected task; the new-task branch only triggers when the change is genuinely independent of every existing task. (b) New protocol Step 5 ("sweep PLAN.md for stale content per `handoff-doc` §Stale Content Checklist") inserted between status-flipping and atomic commit; subsequent steps renumbered to 6 (commit) and 7 (resume). (c) Standalone "DAG cascade on re-entry" paragraph removed — Step 4 already carries the cascade rule. (d) Stale Content Checklist gains one bullet for task-output descriptions superseded by a later task (rewrite the earlier task's **Output:** to the latest shape; keep the "what changed" narrative in the Decisions log only).

Rationale for standalone task: both skills were preserved through Rounds 1–2. Motivated by the lived experience of restructuring Round 3 itself (commit `273de6c`) — the protocol gaps that made that restructure longer than it needed to be are what this task closes.

- [x] **Step 1: Describe — identify the protocol gaps**

  Round 3 restructure surfaced three operational gaps: (a) Step 3 said "prefer modifying existing task blocks" but gave no procedure for finding them; (b) no discrete pre-commit step to sweep PLAN.md for now-stale cross-references; (c) Stale Content Checklist did not name the "earlier task output superseded by later task" pattern that this plan itself exhibits (e.g., Round 2 Task 4's Output: referenced §Concurrent Writers, a section Round 3 Task 4 Step 4 renames). Landed in commit `749c522`.

- [x] **Step 2: Apply**

  planning-workflow: rewrote Step 3 to mandate the task-list walk; inserted new Step 5 (staleness sweep); renumbered commit + resume steps to 6 and 7; removed the redundant "DAG cascade on re-entry" paragraph since Step 4 already carries the rule. handoff-doc: added the superseded-output bullet to the Stale Content Checklist. Landed in commit `749c522`.

- [ ] **Step 3: Validate**

  Reviewer dispatch. Grep the plugin for cross-references to §Changing Plans that now miss the renamed section (`§User Feedback and Changing Plans`); update any that break. Dry-read the polished protocol against the actual Round 3 restructure commit to confirm the new Step 3 wording would have produced the same task-list decisions without the intermediate wrong structure.