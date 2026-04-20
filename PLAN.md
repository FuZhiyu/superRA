# Flexible Integration-Workflow + General Semantic-Merge Refactor (Round 2)

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

*(to be populated as user decisions arrive during execution)*

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
- `skills/refactor-and-integrate/SKILL.md` + references: minimum-net-diff, scope-by-integration-status, drift-test integrity. **Preserved unchanged.**
- `skills/planning-workflow/SKILL.md` §Changing Plans: re-entry protocol covering B→B, C→B, D→B, mid-workflow scope change. **Preserved unchanged** — the round-1 B→B trigger sentence in `plan-anatomy.md:179` stays.
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
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A
**Input:** current `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md` (Integration Intent anatomy produced by Task 2 — cross-referenced only after Task 2 lands; Task 1 names the section and describes purpose/ownership inline), `skills/agent-orchestration/SKILL.md` §Dispatch Templates + §Handling Reviewer Feedback + §Concurrent Writers (parallel-reviewer extension produced by Task 4 — cross-referenced only after Task 4 lands), `skills/refactor-and-integrate/SKILL.md` + references (linked, unchanged)
**Output:** Rewritten Phase B section in `skills/integration-workflow/SKILL.md` — review-led loop with four steps; Tier matrix and shortcut-axis evaluation removed; two-commit implementer contract replaced with a brief "1+N: mechanical merge first, refactors after" note that points at `semantic-merge` for the shape; recon/verify naming split collapsed to "integration reviewer"; Red Flags + Always lists updated; metadata block (Called by / Invokes / Escalates to / Pairs with / Requires) updated.

- [ ] **Step 1: Describe — read the current Phase B end-to-end**

  Read `skills/integration-workflow/SKILL.md` lines 85–199 (Phase B proper) plus the Red Flags list (lines ~394–424) and the Integration block (lines ~428–452). Identify every sentence that names Tier 1/2/3, the two-axis shortcut, the recon reviewer, the verify reviewer, the two-commit structure, or delegated-mode semantic-merge semantics. These are the removal targets.

- [ ] **Step 2: Draft the four-step Phase B skeleton**

  Write Phase B as:
  - **Step 1 — Dispatch integration reviewer(s).** One reviewer by default; parallel siblings on worktrees per `agent-orchestration §Concurrent Writers` (Task 4 extension) when the in-scope surface is large. Reviewer walks (a) `merge-base..HEAD` for integration fit per `refactor-and-integrate`, (b) `merge-base..origin/<base>` for what has moved on main. If (b) reveals meaningful incoming changes that could affect this branch, reviewer writes/updates a `## Integration Intent` section in PLAN.md per `plan-anatomy.md` (added by Task 2) and annotates per-task review-notes blockquotes on affected tasks. Reviewer flips `Integration status: REVISE` on annotated tasks in its own review commit (round-1 Task 8 rule).
  - **Step 2 — Orchestrator adjudicate.** Read PLAN.md (Integration Intent section + per-task annotations). Batch research-meaningful items into one `AskUserQuestion` per `handoff-doc §User Decisions Log`. If findings are a substantive restructure → escalate to `planning-workflow §Changing Plans` (orchestrator authors proposal, researcher decides). Otherwise → Step 3.
  - **Step 3 — Fix-review loop** (restated inline — do not link to `execution-workflow`). Tight restatement: (a) mechanical merge lands first, branch-wide, alone — orchestrator executes directly or dispatches one implementer (no parallelization for this commit); drift tests run on the merged tree; meaningful drift is a stop point per `refactor-and-integrate/references/drift-test-quality.md`. (b) Follow-up refactor commits scoped to REVISE-status tasks (implementer refuses APPROVED-integration tasks per `refactor-and-integrate §Scope by Integration Status`); one serial implementer by default, or parallel siblings on worktrees when the surface is large (same §Concurrent Writers pattern). Commit granularity is the implementer's judgment; minimum-net-diff self-check before every commit; drift tests after any refactor that could affect them. (c) Dispatch reviewer; on APPROVE the reviewer removes its per-task review-notes, flips `Integration status: APPROVED`, and when the last task tied to an Integration Intent item is APPROVED removes that item (and the section when empty). On REVISE: adjudicate per `agent-orchestration §Handling Reviewer Feedback`, iterate. State the 1+N shape as one possible workflow — orchestrator may collapse to a single commit when refactor is trivial.
  - **Step 4 — Flip `Refactored` milestone.** Orchestrator flips the box when every in-scope task is APPROVED and the Integration Intent section is empty/absent; proceed to Phase C.

- [ ] **Step 3: Update the Phase Map diagram and re-entry arrows**

  Replace the current Phase Map ASCII diagram (lines ~18–31) with the same four-phase topology but drop the "Recon-Driven, Two Shortcut Axes" sub-heading. B→B re-entry stays: "main advances mid-integration → re-enter Phase B Step 1". C→B, D→B, B→A, Anywhere→Changing Plans are unchanged. Drop the sub-section "Internal Structure — Recon-Driven, Two Shortcut Axes".

- [ ] **Step 4: Update Red Flags + Always + metadata blocks**

  Red Flags: remove bullets mentioning Tier, recon reviewer, verify reviewer, two-commit structure, shortcut axes, delegated mode. Keep: no skipping Phase A, no refactoring APPROVED-integration tasks, no judging methodology, no advancing to C before reviewer APPROVES, no advancing to D without a freshness check, no PLAN.md disposition by subagent, no worktree cleanup before merge. Always list: keep coverage confirmation with researcher, running the full drift-test suite on every integration pass, re-entering Phase B if main advances. Remove any Tier/shortcut/recon-verify wording. Metadata: §Invokes — drop the "REQUIRED on Tier 2/3" qualifier on `semantic-merge`; it is "invoked by Phase B Step 3's mechanical-merge commit when conflicts or material main-side changes exist" (the reviewer decides; no Tier gate).

- [ ] **Step 5: Validate — walk the four workflow principles**

  Cross-read the rewritten Phase B against `/CLAUDE.md` §Workflow Principles 1–4. Confirm implementer-reviewer pair, handoff-doc auditability, fast-early-strict-before-merge with semantic-merges, and autonomous-with-human-in-loop are all preserved. Grep for residual Tier/shortcut/recon-verify/two-commit language: `grep -n "Tier 1\|Tier 2\|Tier 3\|recon reviewer\|verify reviewer\|two-commit\|shortcut ax" skills/integration-workflow/SKILL.md` → expect empty. Commit.

---

### Task 2: Add `## Integration Intent` anatomy to `plan-anatomy.md`
**Depends on:** *(none)*
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A
**Input:** `skills/handoff-doc/references/plan-anatomy.md`, existing `## Decisions` anatomy entry as a structural template.
**Output:** New `## Integration Intent` subsection in `plan-anatomy.md`, placed between the existing `## User Decisions Log` and `## Task Block Anatomy` sections. Documents purpose, ownership (reviewer-only; implementer hands-off), lifecycle (written by reviewer when Phase B scan finds material main-side change → per-item removal on dependent-task APPROVE → section removal when empty), format (one bullet per incoming-change cluster, each bullet names affected task IDs + one-sentence why-it-matters), and placement (directly after `## Decisions` if present, before the first task block).

- [ ] **Step 1: Describe — pattern-match against `## Decisions`**

  Read `plan-anatomy.md:99–120` (`## User Decisions Log`) and the existing `## Decisions` placement rule at line 67. The Integration Intent section follows the same placement logic: header context → `## Workflow Status` → `## Decisions` (optional) → `## Integration Intent` (optional) → `---` → task blocks.

- [ ] **Step 2: Draft the anatomy entry**

  Write the new subsection with: (a) purpose paragraph (one paragraph: why the section exists — bridge between a material main-side change and the per-task annotations that drive the fix-review loop); (b) ownership rule (reviewer-only; implementer does not edit; orchestrator overrules only via `→ orchestrator:` annotations); (c) lifecycle (written/updated by reviewer at `integration-workflow` Phase B Step 1 when the main-side scan surfaces material incoming intent; per-item removed by reviewer when the last task tied to that item reaches `Integration status: APPROVED`; section removed when empty); (d) format — a markdown code block showing:
  ```markdown
  ## Integration Intent

  > **Main-side change (2026-04-19):** origin/main added a session-start hook that drops a banner into every new session; touches no analysis files but adds a new `hooks/session-start` script and updates `README.md §Hooks`. Affects Tasks 5, 7 (README edit conflicts).
  > **Adaptation needed:** Tasks 5 and 7's README edits must be re-based on top of the new §Hooks language.
  ```
  Three-line bullet per cluster; `Main-side change (YYYY-MM-DD)` + `Adaptation needed`; affected task IDs named explicitly.

- [ ] **Step 3: Validate — coherence check against B→B trigger**

  Read `plan-anatomy.md:179` (B→B trigger sentence, round-1 Task 5). Confirm its language is still consistent: the reviewer's annotation gates the flip, unchanged. Read the `**Integration status:**` paragraph (same line, round-1 Task 8): the three-actor choreography (recon reviewer → implementer → verify reviewer) is now just "integration reviewer → implementer → integration reviewer" in round 2; rewrite the paragraph's naming to drop "recon" and "verify" while preserving the reviewer-owns-verdict-flip semantics. Commit.

---

### Task 3: Rewrite `semantic-merge/SKILL.md` as general-purpose skill
**Depends on:** *(none)*
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A
**Input:** current `skills/semantic-merge/SKILL.md`, global `~/.claude/skills/semantic-merge-integration/SKILL.md` as tone/structure baseline.
**Output:** Rewritten `skills/semantic-merge/SKILL.md` that reads as a skill for thoughtful merging — usable by a human at the terminal, by the orchestrator running it directly, or by a dispatched agent, with the same text. Domain-neutral vocabulary. 1+N commit shape stated as *one possible workflow*, not mandated.

- [ ] **Step 1: Describe — read the global baseline + current superRA version**

  Read `~/.claude/skills/semantic-merge-integration/SKILL.md` end-to-end. Read `skills/semantic-merge/SKILL.md` end-to-end. Identify: (a) what the global skill carries that superRA should reuse as-is (intent-first framing, commit messages + diffs for inferring intent, regeneration over hand-edit for derived artifacts, ask-user-when-ambiguous discipline); (b) what is superRA-specific and must be retained (drift-test integrity as safety net where tests exist, RA framing on research-meaningful decisions, handoff-doc coherence — PLAN.md / RESULTS.md are themselves conflictable files, escalation to `planning-workflow §Changing Plans` if a PLAN.md conflict implies a substantive restructure); (c) what must be removed (Standalone vs Delegated mode split, named return-field contract, in-skill `Agent(subagent_type: ...)` dispatch blocks, domain-specific examples naming `excess_return` / `variable_construction.py` / `Table 3` / econometric specs / sample filters).

- [ ] **Step 2: Draft the rewritten skill**

  Structure: Overview → Core principle (intent first, preserve both sides' purpose) → The process (ground in repo state → understand incoming intent → build integration map → resolve conflicts by intent with user input on ambiguity → verify) → Working principles → When to ask the user (research-meaningful decisions; domain-neutral phrasing) → Commit structure (1+N: mechanical-merge commit first, alone, branch-wide; then N refactor commits, in principle independent and parallelizable when the surface is large; stated as one possible workflow — caller may collapse to a single commit when adaptation is trivial, or to two commits per the global skill's default) → Drift-test / domain-discipline integrity (loads `refactor-and-integrate/references/drift-test-quality.md` on demand when the branch has drift tests) → Red Flags → Integration.

  Replace all domain-specific examples with vertical-neutral phrasing: "results-bearing files", "domain discipline artifacts", "adaptation to integrated intent". Keep one short illustrative example that can be from any vertical (e.g., a paper-drafting branch merging upstream changes that rename a section heading referenced in multiple chapters).

- [ ] **Step 3: Remove dispatch-focused content**

  Delete: "Invocation Pattern" section with the two-mode split; "Mode-aware verification" table; in-skill `Agent(subagent_type: ...)` blocks for Tier 2/3 merge-proposer/merge-reviewer dispatches; the "What to Report — delegated mode" return-field contract; the Tier 1/2/3 classification matrix (the skill's core act is "merge thoughtfully by intent"; classification is an internal concern of whoever is running the skill, not a load-bearing output for a dispatching caller). Replace the `## Integration` block's "Invoked internally by `integration-workflow` Phase B ... via delegated mode" with a neutral "Called by `integration-workflow` Phase B Step 3 mechanical-merge, or standalone by any agent or human doing a research-aware merge".

- [ ] **Step 4: Validate — terminal-use dry-read**

  Read the rewritten skill from top to bottom as if a human were running `git merge main` at the terminal on a paper-drafting branch (no orchestrator, no PLAN.md, no dispatch). Confirm nothing assumes a dispatching caller; confirm no data-analysis vocabulary leaks in except as an explicitly-illustrative example. Grep: `grep -n "Standalone\|Delegated\|excess_return\|Table 3\|econometric\|variable_construction\|delegated mode" skills/semantic-merge/SKILL.md` → expect empty. Commit.

---

### Task 4: Extend `agent-orchestration §Concurrent Writers` with parallel-reviewer note
**Depends on:** *(none)*
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A
**Input:** `skills/agent-orchestration/SKILL.md` §Concurrent Writers Require Worktree Isolation (existing section, implementer-framed).
**Output:** One additional short paragraph in `agent-orchestration §Concurrent Writers` generalizing the pattern to parallel reviewers walking disjoint slices of a large diff — same worktree isolation, same split-by-disjoint-scope, same orchestrator-aggregates-verdicts pattern. One-sentence note that the `Worktree:` dispatch field applies to reviewers in this configuration too.

- [ ] **Step 1: Describe — read the current §Concurrent Writers**

  Read `skills/agent-orchestration/SKILL.md` §Concurrent Writers Require Worktree Isolation plus the `Worktree:` field spec (SKILL.md:143). Identify the core pattern (isolated worktree per concurrent writer to avoid index contention) and the implementer-specific framing that needs generalizing.

- [ ] **Step 2: Draft the extension**

  Append one paragraph to §Concurrent Writers: *"The same pattern generalizes to parallel reviewers when the diff to be walked is large enough that a single reviewer's context would exceed the ~150k threshold (see §Workload Balancing). The orchestrator splits the diff into disjoint slices (by task ID, by file subtree, or by commit range), dispatches one reviewer per slice on its own worktree, and aggregates the per-slice verdicts into a single overall verdict. The `Worktree:` dispatch field applies to reviewers in this configuration as well. Disjoint scoping is the invariant — two reviewers must not walk the same hunk, and their union must cover the whole diff."* Keep the paragraph inside §Concurrent Writers, not a new top-level section — the pattern is the same.

- [ ] **Step 3: Validate — cross-read with Task 1**

  Confirm Task 1's Phase B Step 1 + Step 3 references to "parallel siblings on worktrees" work against this extension. Grep: `grep -n "parallel reviewer\|reviewer.*worktree" skills/agent-orchestration/SKILL.md` → expect at least one hit in the extension paragraph. Commit.

---

### Task 5: Sync peripheral surfaces
**Depends on:** Tasks 1, 2, 3, 4
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A
**Input:** `README.md`, `skills/CATEGORIES.md`, `RELEASE-NOTES.md`, `skills/using-superRA/SKILL.md` §Skill-Load Manifest, `agents/reviewer.md`, `agents/implementer.md`.
**Output:** Peripheral docs updated to match Round 2's language: no residual "recon/verify reviewer", "Tier 1/2/3", "delegated mode", "Standalone mode", "two-commit" anywhere in the skills graph; Skill-Load Manifest `integration` / `merge` rows simplified; `agents/reviewer.md` §What You Own + §Editing Etiquette extended to cover Integration Intent ownership; `agents/implementer.md` §What You Own extended with hands-off note for Integration Intent; RELEASE-NOTES.md has a new "Unreleased" entry.

- [ ] **Step 1: Update agent files**

  `agents/reviewer.md` §What You Own: add a bullet that the integration reviewer owns the `## Integration Intent` section — writes it at Phase B Step 1 when main-side scan surfaces material changes, per-item removes bullets when the last dependent task APPROVES, section-removes when empty. §Editing Etiquette: one sentence confirming the inline-edit + boundary-preservation rules (round 1 Task 8) apply to Integration Intent edits too.

  `agents/implementer.md` §What You Own: add one sentence that the implementer does not edit the `## Integration Intent` section — only the integration reviewer writes it, and only the orchestrator can overrule via `→ orchestrator:` annotations.

- [ ] **Step 2: Update Skill-Load Manifest**

  `skills/using-superRA/SKILL.md` §Skill-Load Manifest: the `integration` row's descriptor rewritten to drop "recon/verify" language if present. The `merge` row stays (semantic-merge standalone is still a thing) but any "delegated mode" phrasing in the descriptor is replaced with a neutral "general-purpose research-aware merge".

- [ ] **Step 3: Update README, CATEGORIES, RELEASE-NOTES**

  `README.md`: workflow-map diagram and skill-inventory table — check for residual Tier / recon-verify / two-commit language in the integration-workflow row and the semantic-merge row; fix.
  `skills/CATEGORIES.md`: integration-workflow row's short description simplified; semantic-merge row's description made vertical-neutral.
  `RELEASE-NOTES.md`: new `## Unreleased — flexible integration-workflow + general semantic-merge refactor` heading with bullets listing (a) Phase B flattened to review-led loop; Tier matrix removed; (b) semantic-merge generalized on top of global skill; mode split removed; (c) Integration Intent section added to plan-anatomy; (d) parallel-reviewers note added to agent-orchestration.

- [ ] **Step 4: Validate — sweep**

  Grep: `grep -rn "Tier 1\|Tier 2\|Tier 3\|recon reviewer\|verify reviewer\|two-commit\|delegated mode\|Standalone mode" skills/ agents/ README.md RELEASE-NOTES.md` → expect only pre-existing historical RELEASE-NOTES entries and `docs/plans/` archive hits (the round-1 plan/results are historical record, not touched by round 2). Commit.

---

### Task 6: End-to-end dry-read verification
**Depends on:** Tasks 1, 2, 3, 4, 5
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A
**Input:** All round-2 refactored skills + agent files + peripheral docs.
**Output:** Walk-through notes in `RESULTS.md` covering seven scenarios; confirms the refactor is internally coherent and the round-1 invariants still hold; any [ADVISORY] stale-vocabulary hits fixed in-place (no tuned content touched); any [BLOCKING] issue opened as a review-notes entry on the relevant prior task for re-entry.

- [ ] **Step 1: Scenario (a) — no-main-movement fast path**

  Hypothetical branch: APPROVED PLAN.md, code-complete, `origin/main` has not advanced since merge-base. Walk Phase A (drift tests authored, all pass) → Phase B Step 1 (integration reviewer walks both diffs; main-side scan finds nothing; no Integration Intent section written; no per-task annotations; Integration status stays APPROVED across all tasks) → Step 2 (orchestrator reads PLAN.md, no adjudication needed) → Step 3 (skipped — no REVISE tasks; mechanical merge is a no-op fast-forward since merge-base is main tip) → Step 4 (Refactored milestone flips) → Phase C → Phase D. Confirm the flow terminates cleanly.

- [ ] **Step 2: Scenario (b) — Integration Intent path**

  Hypothetical branch: main has advanced with a cross-cutting refactor of a shared utility; incoming change touches the utility plus a README section that two of this branch's tasks also edit. Walk Phase B Step 1 (reviewer writes Integration Intent section with two bullets + per-task annotations; flips two tasks to REVISE); Step 2 (orchestrator batches a single user-decision on adaptation approach); Step 3 (mechanical merge commit first via `semantic-merge`; then refactor commits scoped to the two REVISE tasks; reviewer re-review APPROVES both, removes review-notes, removes the corresponding Integration Intent bullets, and when both bullets are gone, removes the section). Confirm the ownership contract (reviewer-only for Intent writes + removes) holds.

- [ ] **Step 3: Scenario (c) — parallel reviewers on a large diff**

  Hypothetical branch: 20+ tasks; Phase B Step 1 needs to walk a cumulative diff that would exceed one reviewer's context. Walk the orchestrator split: three reviewers dispatched on disjoint worktrees, each walking a ~7-task slice; their verdicts aggregated; per-task annotations land in PLAN.md as if from one reviewer. Confirm the Task 4 extension paragraph covers the mechanics; confirm disjoint-scope invariant holds.

- [ ] **Step 4: Scenario (d) — 1+N with parallel refactor implementers**

  Hypothetical continuation of Scenario (b) but with five tasks flipped to REVISE and adaptation work that is independent across them. Walk Step 3's mechanical-merge commit (one implementer, serial, branch-wide) then the N refactor commits dispatched as five parallel sibling implementers on worktrees. Confirm the 1+N shape reads as "one possible workflow" in both `integration-workflow` Phase B and `semantic-merge`, not mandated.

- [ ] **Step 5: Scenario (e) — B→B re-entry**

  Hypothetical: Phase B had approved; while Phase C was mid-flight, main advanced again. Walk the C→B re-entry via `planning-workflow §Changing Plans`: `Refactored` unchecks, re-enter Phase B Step 1; reviewer re-walks; new Integration Intent bullet written if material; fix-review loop re-runs. Confirm the existing `plan-anatomy.md:179` B→B trigger sentence (round-1 Task 5) still reads correctly against Task 2's rewritten `**Integration status:**` paragraph.

- [ ] **Step 6: Scenarios (f) + (g) — plan-change escalation and standalone semantic-merge**

  (f): Phase B Step 1 reviewer surfaces a finding that is a substantive restructure (a task needs to be removed because main deleted the feature it analyzed). Walk the escalation to `planning-workflow §Changing Plans` — orchestrator authors the proposal, researcher decides, PLAN.md updated inline, re-entry.

  (g): A human runs `git merge` at the terminal on a paper-drafting branch that has no PLAN.md and no drift tests. Walk the rewritten `semantic-merge/SKILL.md` from top to bottom. Confirm nothing in the skill forces the existence of a PLAN.md, drift tests, or a dispatching caller; confirm the handoff-doc coherence and drift-test integrity clauses degrade gracefully to no-ops when those artifacts are absent.

- [ ] **Step 7: Write findings to `RESULTS.md`; fix ADVISORY issues in place; commit**

  For each scenario, write a short paragraph in RESULTS.md noting pass/fail and any residual stale vocabulary or coherence gaps. Fix [ADVISORY] items in place (naming-only, prose-only). Open [BLOCKING] items as review-notes entries on the relevant prior task for re-entry. Commit.
