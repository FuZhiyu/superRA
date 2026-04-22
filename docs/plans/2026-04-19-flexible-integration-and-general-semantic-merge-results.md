# Flexible Integration-Workflow + General Semantic-Merge Refactor — Results

Stage 1 dev log. Per `superRA:handoff-doc` / `references/results-anatomy.md`, the file is matured to its permanent location at `integration-workflow` Phase C.

---

### Task 1: Rewrite `integration-workflow` Phase B
**Status:** IMPLEMENTED

Phase B in `skills/integration-workflow/SKILL.md` rewritten as a four-step review-led loop. The Tier 1/2/3 matrix, two shortcut axes, "Internal Structure — Recon-Driven" sub-section, two-commit implementer contract, and recon/verify reviewer naming split are fully removed.

**New structure:**
- **Step 1** — Single integration reviewer dispatched; walks `merge-base..HEAD` and `merge-base..origin/<base>` (main-side scan); writes/updates `## Integration Intent` in PLAN.md when material incoming changes found; annotates per-task blockquotes and flips REVISE. Parallel sibling reviewers supported for large diffs (forward-reference to Task 4 §Concurrent Writers).
- **Step 2** — Orchestrator adjudicates: zero annotations fast-paths to `git merge --ff-only` (or no-op) and proceeds to Phase C; annotated tasks batch into one `AskUserQuestion`; substantive restructure escalates to `planning-workflow §Changing Plans`.
- **Step 3** — Fix-review loop (three sub-steps): 3a mechanical merge first (semantic-merge when conflicts or material main-side changes; reviewer's finding drives the call, not a Tier gate); 3b refactor commits scoped to REVISE tasks with dispatch template; 3c re-dispatch reviewer until APPROVE (reviewer removes resolved blockquotes and Integration Intent items on APPROVE).
- **Step 4** — Orchestrator flips `Refactored` milestone when all tasks APPROVED and Integration Intent empty/absent.

**Other changes:** Red Flags and Always lists updated to remove Tier/shortcut/recon-verify language. §Invokes metadata updated: semantic-merge qualifier changed from "REQUIRED on Tier 2/3" to reviewer-driven. Phase Map re-entry comments cleaned. Autonomy stop-point list, When to Lighten, and Agent Loads updated.

**Validation:** `grep "Tier 1\|Tier 2\|Tier 3\|recon reviewer\|verify reviewer\|two-commit\|shortcut ax\|delegated mode\|Standalone mode"` on SKILL.md → empty.

Follow-up: R1 advisory — fixed stale "Verify reviewer" → "integration reviewer" in §When to Lighten Small changes; softened frontmatter "single unified pass" to "review-led iterative sync + refactor targeting minimum-net-diff".

---

### Task 2: Add `## Integration Intent` anatomy to `plan-anatomy.md`
**Status:** Implemented

**What changed:** `skills/handoff-doc/references/plan-anatomy.md` received three edits:

1. **New `## Integration Intent` section** inserted between `## User Decisions Log` and `## Task Block Anatomy`. Covers purpose (bridges Phase B main-side scan to per-task fix-review loop), ownership (integration reviewer only; implementer hands-off; orchestrator overrules via `→ orchestrator:` annotations), lifecycle (write on scan → remove items as dependent tasks hit `APPROVED` → remove section when empty), and format (two-line blockquote cluster: `Main-side change (YYYY-MM-DD)` naming affected task IDs + `Adaptation needed` describing required work).

2. **`## Decisions` placement note updated** (line 67) to include `## Integration Intent` in the header order: `## Workflow Status` → `## Decisions` (when present) → `## Integration Intent` (when present) → `---` → task blocks.

3. **`**Integration status:**` paragraph rewritten** (§Field-by-Field Notes): "recon reviewer", "unified implementer", "verify reviewer" replaced with "integration reviewer (annotation pass)", "implementer", "integration reviewer (verify pass)". Reviewer-owns-verdict-flip semantics and B→B trigger sentence fully preserved. Also updated the `Refactored` Workflow Status checkbox template from "verify reviewer" to "integration reviewer".

Follow-up: R2 advisory — Integration Intent lifecycle Step 2 trigger tightened: "As each cluster of affected tasks reaches APPROVED" → "When the last task named in a cluster reaches APPROVED".

---

### Task 3: Rewrite `semantic-merge/SKILL.md` as general-purpose skill
**Status:** Implemented

**What changed:** `skills/semantic-merge/SKILL.md` rewritten from ~338 lines to ~170 lines. All dispatch-focused machinery removed: Standalone/Delegated mode split, Mode-aware verification table, in-skill `Agent(subagent_type: ...)` dispatch blocks (Tier 2/3 merge-proposer/reviewer), named return-field contract ("What to Report — delegated mode"), and the Tier 1/2/3 classification matrix. The skill now reads coherently for a human at the terminal, an orchestrator running it directly, or a dispatched agent — same text, no caller assumptions.

**Retained superRA-specific content:** Drift-test integrity clause (run after merge, load `drift-test-quality.md`, adjudicate don't silence meaningful failures); RA framing on research-meaningful decisions; PLAN.md/RESULTS.md as conflictable handoff docs with escalation to `planning-workflow §Changing Plans` when a PLAN.md conflict implies substantive restructure; `handoff-doc §User Decisions Log` logging requirement.

**1+N commit shape:** Stated in Step 5 as "one possible workflow" with explicit note that callers may collapse to a single commit or split integration work across parallel commits.

**Vocabulary:** All analysis-specific names removed (`excess_return`, `variable_construction.py`, `Table 3`, econometric specs, sample filters). Replaced with vertical-neutral phrasing: "results-bearing files", "domain-discipline artifacts". Illustrative example in Step 4 uses generic "outcome variable construction" without analysis-specific names.

**Validation grep results:** `Standalone\|Delegated\|excess_return\|Table 3\|econometric\|variable_construction\|delegated mode` → empty; `Tier 1\|Tier 2\|Tier 3\|recon reviewer\|verify reviewer\|two-commit` → empty.

Follow-up: R3 advisory — generalized remaining analysis-idiom vocabulary: Step 2 "describe steps, row-count logs" → explicit "(e.g. for data analysis: ...)" qualifier; Step 4 parenthetical example list → vertical-neutral "scope-defining variables, key model specifications"; §Working Principles domain-discipline bullet → added explicit data-analysis qualifier. General criteria text is now vertical-neutral throughout.

---

### Task 4: Extend `agent-orchestration §Concurrent Writers` with parallel-reviewer note
**Status:** Implemented

**Changes made to `skills/agent-orchestration/SKILL.md`:**

1. Softened the "Applies to implementers only" sentence to "Applies to implementers by default. Reviewers typically run post-merge on the analysis branch..." to set up the generalization.

2. Added one paragraph extending the pattern to parallel reviewers (lines 79–79): orchestrator splits large diffs into disjoint slices, dispatches one reviewer per slice on its own worktree, aggregates per-slice verdicts. `Worktree:` dispatch field applies to reviewers in this configuration. Disjoint-scope invariant stated explicitly.

3. Updated the `Worktree:` field spec note (was "implementer-only, parallel-dispatch only"; now "parallel-dispatch only; implementers always, reviewers when using the parallel-reviewer pattern in §Concurrent Writers").

**Validation:** `grep -n "parallel reviewer\|reviewer.*worktree"` returns hits at lines 79 and 145. Task 1's Phase B Step 1 + Step 3 references to "parallel siblings on worktrees" reference this extension correctly. No new top-level section created — extension stays inside §Concurrent Writers.

Follow-up: R4 advisory — added `Worktree: <absolute path>   # optional — parallel-reviewer pattern only` line to the Reviewer Dispatch Template block, symmetric with the Implementer block which already showed the field.

---

### Task 5: Sync peripheral surfaces
**Status:** Implemented

**Agent file updates:**
- `agents/reviewer.md` §What You Own: replaced "recon reviewer / verify reviewer" integration-status language with "integration reviewer (annotation pass) / integration reviewer (verify pass)"; added `## Integration Intent` ownership bullet with full lifecycle (write at Phase B Step 1 → per-item remove when last named task APPROVED → section-remove when empty). §Editing Etiquette: added sentence confirming inline-edit rules apply to Integration Intent. Pre-commit self-check: updated to mention `## Integration Intent`.
- `agents/implementer.md` §What You Own: reworded integration-status line (dropped "two-commit", "recon reviewer", "verify reviewer"); added explicit hands-off paragraph — implementer never edits `## Integration Intent`.

**Skill-Load Manifest:** Stale paragraph below the manifest table in `skills/using-superRA/SKILL.md` (which said "delegated mode" and "Tier 2/3 only") replaced with neutral explanation of when `merge` stage is used vs when Phase B loads `semantic-merge`.

**Peripheral surfaces:** README.md Mermaid INT2 node and skill-table rows updated (removed Tier/recon-verify vocabulary); semantic-merge row made vertical-neutral in both README.md and CATEGORIES.md; "invokes semantic-merge internally on Tier 2/3" fixed in the "How It Works" diagram header. RELEASE-NOTES.md: new `## Unreleased — flexible integration-workflow + general semantic-merge refactor` section added with four bullets covering Phase B flattening, semantic-merge generalization, Integration Intent anatomy, and parallel-reviewer pattern.

**Validation sweep:** `grep -rn "recon reviewer|verify reviewer|delegated mode|Standalone mode"` on active skill/agent files → empty. Remaining `two-commit` hits are legitimate merge-quality vocabulary in `refactor-and-integrate/SKILL.md`, not the removed integration-workflow contract.

**Advisory fixes folded in (R1–R4):**

**R1 (integration-workflow SKILL.md):** "Verify reviewer may APPROVE immediately" → "Integration reviewer may APPROVE immediately with no annotations" (`§When to Lighten → Small changes`). Frontmatter description softened: "a single unified sync + refactor pass" → "review-led iterative sync + refactor".

**R2 (plan-anatomy.md):** Integration Intent lifecycle Step 2 trigger tightened: "As each cluster of affected tasks reaches APPROVED" → "When the last task named in a cluster reaches APPROVED".

**R3 (semantic-merge SKILL.md):** Three analysis-idiom generalizations: (a) Step 2 "Domain-discipline artifacts" bullet — "describe steps, row-count logs, validation checks, drift tests" → "validation artifacts the domain skill requires (e.g. for data analysis: describe steps, row-count logs, validation checks); drift tests"; (b) Step 4 parenthetical — "variable definitions, sample construction, model specifications, data sources" → "scope-defining variables, key model specifications, data sources"; (c) §Working Principles "Domain-discipline artifacts" bullet — added explicit "(for data analysis: ...)" qualifier. All general criteria text is now vertical-neutral; one illustrative example per location.

**R4 (agent-orchestration SKILL.md):** Added `Worktree: <absolute path>   # optional — parallel-reviewer pattern only` to the Reviewer Dispatch Template block, symmetric with the Implementer template.

---

### Task 6: End-to-end dry-read verification
**Status:** Implemented

Seven scenarios simulated on paper against the round-2 refactored skills (`integration-workflow`, `semantic-merge`, `plan-anatomy`, `agent-orchestration`) plus agent files and peripheral surfaces. All seven pass. No BLOCKING issues found.

**Scenario (a) — No-main-movement fast path:** PASS. Phase B Step 2's "zero annotated tasks" branch routes cleanly to a fast-forward merge and then Phase C. The `When to Lighten §Standalone analysis` entry confirms the same shortcut in prose. Lifecycle terminates correctly without stale vocabulary.

**Scenario (b) — Integration Intent path:** PASS. Reviewer writes `## Integration Intent` (two bullets); implementer hands off (confirmed in `implementer.md §What You Don't Own`); reviewer removes bullets as tasks reach APPROVED and removes section when empty. Ownership contract is three-way consistent across `plan-anatomy.md §Integration Intent`, `reviewer.md §What You Own`, and `implementer.md §What You Don't Own`. The lifecycle trigger (remove bullet when the last named task reaches APPROVED, remove section when empty) matches across all three sources.

**Scenario (c) — Parallel reviewers on a large diff:** PASS. `agent-orchestration §Concurrent Writers` paragraph (Task 4 extension) covers mechanics; `integration-workflow` Phase B Step 1 dispatch template forward-references it. `Worktree:` field appears in the Reviewer Dispatch Template block (R4 fix). Disjoint-scope invariant stated explicitly. One ADVISORY: the `§Concurrent Writers` ownership table rows ("Inside worktree", "Harvest-out") name implementers but not reviewers; the prose covers it but the table is implementer-framed. This is pre-existing and low-priority; no change made.

**Scenario (d) — 1+N with parallel refactor implementers:** PASS. The mechanical merge commit is correctly serialized ("no parallelization for this commit"). N parallel refactor implementers on disjoint worktrees are supported per §Concurrent Writers. The 1+N commit shape is consistently non-mandating in both `integration-workflow` Phase B Step 3 and `semantic-merge §Step 5` ("one possible workflow, not mandatory").

**Scenario (e) — B→B re-entry:** PASS. `plan-anatomy.md §Field-by-Field Notes` B→B trigger sentence is coherent with Task 2's rewritten `**Integration status:**` paragraph and Task 1's Phase B structure. Non-annotated tasks stay APPROVED; annotated tasks flip to REVISE — consistent across `plan-anatomy.md`, `integration-workflow`, and `reviewer.md §What You Own`. `planning-workflow §Changing Plans` Step 4 covers the C→B rollback ("If the change rolled back `Refactored`, re-enter `integration-workflow` Phase B").

**Scenario (f) — Plan-change escalation:** PASS. Substantive restructure findings escalate to `planning-workflow §Changing Plans` cleanly. The trigger is named in `integration-workflow §Phase B Step 2` (task add/remove/combine, DAG flip), in `semantic-merge §Step 3` (PLAN.md conflict implying structural reorganization), and in `planning-workflow §Changing Plans §Material`. All three sources are consistent. Protocol covers task removal without leaving stale review-notes or integration-status artifacts.

**Scenario (g) — Standalone semantic-merge:** PASS. `semantic-merge/SKILL.md` degrades gracefully when PLAN.md, drift tests, and a dispatching caller are all absent. Drift-test checks are conditional ("if the branch has them"). Domain-discipline artifacts use explicit "(for data analysis: ...)" qualifiers. Step 4 provides a fallback for logging user decisions without PLAN.md ("record the decision in the merge commit message instead"). No caller-assumption vocabulary remains. Skill reads coherently for a human running `git merge` on a paper-drafting branch.

**Overall verdict:** All seven scenarios pass. The round-2 refactor is internally coherent; round-1 invariants hold. No BLOCKING issues. Two ADVISORY observations noted in scenarios (c) and the commit-hygiene reading of Phase C Option 2/3's `git add -A results_attachments/` — both are pre-existing, in-bounds, or low-priority; no edits required.

### Task 6 — Round 3 scenarios

Four additional scenarios walked on paper against the Round 3 refactored skills (`integration-workflow` Phase B with flex base + collapsed Step 3b + trimmed Red Flags; `refactor-and-integrate` with §Scope by Integration Status lifted into Implementer Self-Check; `merge-quality.md` with intent-separation framing; `planning-workflow §User Feedback and Changing Plans` with new staleness-sweep step). All four pass.

**Scenario (h) — Non-main integration base:** PASS. Hypothetical analysis branch integrating into `release/2026-Q2`. Phase B opener's new "Integration base" paragraph establishes `<base-branch>` as researcher-selectable (default `origin/main`). Step 1 dispatch steering reads "material incoming changes on the integration base" — no "main" hardcoding. Step 2 zero-annotation fast path: `git merge --ff-only <base-branch>`. Step 3a: "when the base branch has diverged" / "when `<base-branch>` is an ancestor". Phase D pre-merge freshness block (line 269-273) already used the `<base-branch>` placeholder from Round 2 and reads correctly against the release branch. Red Flag bullet 2 ("advance to Phase D without a freshness check on the integration base") catches the failure mode. No residual main-only vocabulary in the Phase B path.

**Scenario (i) — Collapsed Phase B Step 3b dispatch:** PASS. Orchestrator with three REVISE tasks (Tasks 2, 5, 7) now consults `agent-orchestration §Dispatch Templates` for shape and applies the four Step 3b additions listed in the new prose: `Stage: integration`, `Tasks in scope: 2, 5, 7` + refusal + IMPLEMENTED flip, mechanical merge must land first, drift tests re-run. Every field the old embedded block carried is reconstructible from template + additions. The scope-list refusal semantics are now also guarded at commit time by Implementer Self-Check step 4 ("Respect the dispatch's scope list — APPROVED tasks not named in scope are out of scope; a hunk touching one fails step 3"), so the contract is enforced at both dispatch and self-check boundaries. `grep -n "Agent(subagent_type:" skills/integration-workflow/SKILL.md` returns three hits: Phase B Step 1 reviewer (canonical for that stage), Phase C doc-writer, Phase C doc-reviewer. Phase B Step 3b is dispatch-block-free — target met.

**Scenario (j) — Red Flags regression check + refactor-and-integrate simplifications:** PASS. Walked each dropped Red Flags bullet against where the underlying rationalization is now caught: (1) Skip Phase A → §Three Concurrent Disciplines + Phase A choreography prose. (2) Skip integration reviewer → KEPT. (3) Interrupt implementer mid-run → Phase B Step 2 prose ("batch every research-meaningful decision… one stop point, not N interruptions"). (4) Refactor APPROVED tasks not in scope → Implementer Self-Check step 4 (moved from §Scope by Integration Status) + Phase B Step 3b's refusal bullet. (5) Strip domain artifacts → §Three Concurrent Disciplines (drift-test integrity + codebase integration `[BLOCKING]` items). (6) Judge methodology → cross-cutting pointer block at end of §Red Flags names `using-superRA §Universal Principles`. (7) Advance Phase C without all APPROVE → Phase B Step 4 prose. (8) No Phase D freshness check → KEPT. (9) Delegate Phase C Step 4 → KEPT. (10) Inline Phase C fact-check → Phase C Step 2 prose ("Format discipline… lives entirely in `superRA:report-in-markdown`"). (11) Cleanup before merge completes → KEPT. All prior rationalizations either retained or covered elsewhere. §Scope by Integration Status removal: `grep -rn "§Scope by Integration Status" skills/ agents/` → empty; no dangling cross-references. merge-quality intent-separation: trivial fast-forward merge + near-empty adaptation now legitimately lands as one commit; non-trivial merge lands as two (canonical template) or N (when intent decomposes); the `[BLOCKING]` "intent separation" item catches the real failure mode (conflating mechanical + intent) without mandating count.

**Scenario (k) — Changing Plans protocol tightened:** PASS. The Round 3 protocol-restructure commit (`273de6c`) is itself the natural test case — walked backwards against the new `planning-workflow §User Feedback and Changing Plans`. Step 3's task-list walk would have produced the same fan-out directly (Tasks 1, 4, 5, 6 reopened; 7 + 8 genuinely new) rather than the original Task 7–13 structure that had to be undone. Step 5's staleness sweep would have caught the "Preserved unchanged" Project Conventions entry for `planning-workflow` in the same pass it was invalidated, rather than leaving the stale claim in PLAN.md across commits. `handoff-doc` §What Counts as Stale's new bullet (task-output superseded by a later task) catches the exact pattern Task 4's Round 2 Output: exhibited after Task 4 Step 4 renamed its subject section. Grep sweep confirmed in Task 5 Step 5: zero active `§Changing Plans` or `§Concurrent Writers` references remain outside historical RELEASE-NOTES entries.

**Round 3 overall verdict:** All four scenarios pass. The Round 3 refactor is internally coherent; Round 2 invariants hold. Task 6 Step 8 (non-main base), Step 9 (collapsed dispatch), Step 10 (Red Flags + refactor-and-integrate), Step 11 (protocol tightening) all clear with no BLOCKING issues.

### Round 3 integration review (Phase B)

Independent integration review dispatched against `50a224a..HEAD` per `integration-workflow` Phase B Step 1. Verdict: **APPROVE** (commit `632a188`). `origin/main` had not advanced — no Integration Intent needed. All six dispatch-specified checks passed; one `[ADVISORY]` surfaced — pre-existing miss from Round 2 Task 5's sweep where hyphenated forms of "Phase B recon, unified-implementer, verify-reviewer dispatches" and semantic-merge "tier classification" in `refactor-and-integrate/SKILL.md:90-91` slipped the grep. Rewritten to current Round 2+3 vocabulary in commit `3e68327` (same commit that flipped the `Refactored` milestone).

Tasks 1, 4, 5, 6, 7, 8 all carry `**Integration status:** APPROVED` post-review. All Round 3 task-output descriptions in PLAN.md reflect the latest shipped state per `handoff-doc` §Stale Content Checklist.
