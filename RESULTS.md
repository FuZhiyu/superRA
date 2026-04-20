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
**Status:** Not started
