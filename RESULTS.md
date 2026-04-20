# Unified Integration-Workflow Refactor — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-19 (post-Task 7 — all tasks APPROVED)
**Status:** Execution complete — all 7 tasks APPROVED; integration Phase B Refactored milestone flipped

---

## Task 1: Rebuild `refactor-and-integrate` as a gated checklist

**Status:** IMPLEMENTED

**Summary:** `skills/refactor-and-integrate` restructured with a clean separation between **principle-level body** (SKILL.md) and **how-to + checklist references** — one source of truth per concern. SKILL.md describes what each of the three concurrent disciplines (Drift-Test Integrity, Codebase Integration, Merge Quality) is *for*, names the severity-marker convention (`[BLOCKING]` / `[ADVISORY]`), carries the load-bearing **Minimum net diff to merge base** top item, the two-verdict reviewer protocol (APPROVE / REVISE + dependent-finding prose + narrow re-review), and the pre-commit **Implementer Self-Check** (`git diff <merge-base>..HEAD`). All tuned content lives in the three references, reached via stage-scoped required loads per `superRA:using-superRA` §Skill-Load Manifest.

**Key structural choices:**

- **SKILL.md = principles + cross-cutting gates.** No verbatim Red Flags Never-list, no Tier 3 escalation blockquote, no RA-framing blockquotes. Principle descriptions may *name* concepts ("Tier 3 conflicts", "Red Flags") but the tuned prose lives only in references. Body retained items: load-bearing top item, reviewer verdict protocol, Implementer Self-Check, dispatch convention, integration-pointers.
- **References restructured as §How-To + §Gated Checklist.** Each reference now opens with a how-to section (procedures, worked examples, Red Flags rationale, Tier 3 escalation procedure + Never-list, Project Doc Audit walk-up algorithm, two-commit commit-message templates, integration-map format) and closes with the gated checklist — severity-marked items whose prose points back into §How-To.
  - `drift-test-quality.md` §How-To: tolerance calibration worked examples, red-green cycle, test format conventions, Cross-cutting Red Flags (four-bullet "Never" list, verbatim).
  - `codebase-integration.md` §How-To: handling-inconsistencies decision tree (RA-framing wording preserved verbatim), Project Doc Audit walk-up.
  - `merge-quality.md` §How-To: two-commit templates, Research-Meaningful Escalation (Tier 3) prose + five-conflict-type list + four-bullet "Never" list (verbatim), integration-map format.
- **Tuned wording preserved verbatim.** All Red Flags, rationalization bullets, Tier 3 escalation prose, and RA-framing sentences were relocated with no paraphrasing, per `/CLAUDE.md §Skill Changes`.
- **Shared-flow checklist, one source of truth.** Implementer walks each reference's §Gated Checklist as self-check before commit; reviewer walks the same items as verification. No parallel review-only document exists; no content is duplicated between SKILL.md body and references.
- **Manifest wording tight.** `integration` / `drift-test` / `merge` rows in `using-superRA/SKILL.md` §Skill-Load Manifest already name the specific references as required (`codebase-integration.md`, `drift-test-quality.md`, `merge-quality.md`). No manifest edit needed.

**Scope notes:**

- Caller-side wording in `integration-workflow/SKILL.md`, `merge-workflow/SKILL.md`, and `using-superRA/SKILL.md` still references the filenames directly; those pointers remain valid.
- `[BLOCKING] Handoff-doc coherence` in merge-quality is deferred to Task 4 per plan.

**Step 5 addition (scope-by-Integration-status rule).** SKILL.md body gained one principle-level section, `## Scope by Integration Status`, stating that refactor implementer and verify reviewer operate only on tasks whose `Integration status` is unset or `REVISE`; `APPROVED`-integration tasks are out of scope. The section points at `handoff-doc/references/plan-anatomy.md` (lines 178–179) for the DAG cascade semantics rather than restating them. Minimum-net-diff: only SKILL.md was touched in this step; the three references were not modified.

**Verification:**

- `grep` for "Silently update drift", "Tier 3", and "Never:" in SKILL.md shows the verbatim blockquotes are gone from the body; same strings present verbatim in the references.
- `git diff 92a685b..HEAD` on this task's commit touches exactly four files: SKILL.md and the three references under `skills/refactor-and-integrate/`. No unrelated hunks (Minimum-net-diff self-check passes).



## Task 2: Unify `integration-workflow` — Phases A–D with iterative Phase B

**Status:** IMPLEMENTED

**Summary:** `skills/integration-workflow/SKILL.md` rewritten to cover the full INTEGRATE phase as Phases A–D (drift tests → unified sync+refactor → docs → merge/PR/cleanup). Phase B restructured around **recon-as-reviewer** with two **independent shortcut axes** (Tier from `semantic-merge` trial-merge gates the merge path; annotation count from per-task PLAN.md blockquotes gates the refactor path). Former `merge-workflow` content folded into Phase D with PR template rewritten to remove the dangling `[OR: skipped per Step 2.0 …]` branch from the previous shortcut design.

**Key structural choices:**

- **Recon reviewer replaces read-only recon dispatch.** Step 1 runs a standard reviewer, loaded with `superRA:semantic-merge` via the canonical `Skills:` dispatch field. It follows the standard reviewer protocol (per-task integration review-notes blockquotes with `[BLOCKING]`/`[ADVISORY]` items) and additionally runs a trial `semantic-merge` to produce a Tier classification, logged one-line under §Decisions. No custom return contract — all communication flows through the handoff doc.
- **Two independent shortcut axes.** Tier axis (1 vs 2/3) gates whether follow-up agents load `semantic-merge`; annotation axis (zero vs non-zero) gates whether the unified implementer + verify reviewer run at all. Combined: Tier 1 + zero annotations → `git merge --ff-only` only, Phase B terminates; Tier 1 + annotations → fast-forward + refactor-only (no `semantic-merge` load); Tier 2/3 regardless → full flow with `semantic-merge` on follow-ups. Axes decomposed deliberately to prevent one-axis-clean-other-axis-dirty bugs.
- **Orchestrator post-recon step (Step 2) is explicit and distinct from user-decision batching (Step 2b).** Step 2 is orchestrator-only: read recon's annotations, flip `Integration status: REVISE` on annotated tasks (APPROVED tasks stay APPROVED), evaluate shortcut axes. Step 2b runs only on Tier 2/3 or when decisions need batching.
- **Scope-by-Integration-status wired through dispatches.** The unified implementer and verify reviewer both carry a `Tasks in scope:` dispatch field listing the in-scope task list (tasks with `Integration status: REVISE`); both dispatches explicitly refuse to touch APPROVED-integration tasks. Points at `refactor-and-integrate §Scope by Integration Status` for the rule. Verify reviewer raises out-of-scope hunks as `[BLOCKING]` against Minimum-net-diff.
- **Unified implementer two-commit structure conditional on Tier.** Commit 1 uses `semantic-merge` (delegated) when Tier 2/3; `git merge --ff-only` when Tier 1 + annotations. Commit 2 is always the unified refactor across the in-scope list.
- **Canonical dispatch shape throughout.** Every dispatch block opens with the canonical prefix; required fields (`Stage:`, `Task:`, `Git range:`/`Worktree:`, `Skills:` / `Tasks in scope:` where applicable) appear first; `Additionally:` tail carries only additive steering. No restated PLAN.md content, no duplicated skill-load lines, no drift-test cadence restatements in `Additionally:` (cadence lives in body prose).
- **Phase B opening trimmed to pointer-only.** Two-commit definition now lives exclusively in `refactor-and-integrate/references/merge-quality.md`; Phase B body points there.
- **PR template dangling reference stripped.** `## Pre-Merge Quality` `Integration review:` line in Step 3b PR body now reads `passed pre-merge (Phase B verify reviewer APPROVE)` — no `[OR: skipped per Step 2.0 …]` branch. Reflects actual Phase D behavior under the new shortcut architecture.
- **"When to Lighten" greenfield wording rephrased.** Dropped the confusing "sync commit only" phrase; describes shortcut behavior explicitly (Tier 1 + zero annotations collapses Phase B to fast-forward; true greenfield with no base yet is a Phase B no-op).
- **Red Flags / Always lists reconciled with shortcut architecture.** Core-principle sentence no longer claims "every merge with main uses semantic-merge" (Tier 1 fast-forward is a legitimate shortcut). Always list conditions delegated-mode use on Tier 2/3; drift-test cadence phrased as "when the implementer ran the two-commit structure." Never list updated to reference Step 2b and the scope rule.

**Verification:**

- Canonical shape: every `Agent(subagent_type: …)` block carries required fields first and an `Additionally:` anchor-last; `Skills: superRA:semantic-merge` appears on recon (always) and unified implementer (Tier 2/3 only); `Tasks in scope:` appears on unified implementer + verify reviewer.
- Shortcut matrix consistent: three combinations documented identically in §Internal Structure (Two Shortcut Axes) and in Step 2 (Orchestrator evaluation).
- Four workflow principles: (1) implementer-reviewer pair retained at Phase A drift-test pair, Phase B recon + verify reviewer pair, Phase C doc-writer/doc-reviewer pair. (2) handoff docs as record — recon annotations land in PLAN.md before the shortcut decision; Tier lands under §Decisions; every stop logs per §User Decisions Log before acting. (3) fast early / strict before merge — Phase B is iterative and re-enterable; Phase D Step 1 re-enters Phase B if main advanced; semantic-merge used when non-trivial. (4) autonomous with human in loop — five enumerated stop points unchanged; Step 2 orchestrator logic runs without check-in.
- Deferred items: Task 3 (merge-workflow deletion), Task 4 (semantic-merge caller-path text + `[BLOCKING] Handoff-doc coherence`), Task 5 (planning-workflow bullet + B→B re-entry trigger sentence), Task 6 (peripheral surfaces).

## Task 3: Delete `skills/merge-workflow/`

**Status:** IMPLEMENTED

**Summary:** `skills/merge-workflow/` deleted (one file, `SKILL.md`). Callers outside Task 6's peripheral-surfaces scope repointed to `superRA:integration-workflow` using the Phase A–D vocabulary established in Task 2. `RELEASE-NOTES.md` gained a single deprecation line under a new "Unreleased — unified integration-workflow refactor" heading, naming Phase D as the new home for former merge-workflow choreography.

**Callers repointed (in scope for Task 3):**

- `agents/implementer.md` — description frontmatter dropped `merge-workflow (post-merge refactoring)` and folded its call sites into `integration-workflow (drift test creation, refactoring, and post-merge refactoring across Phases A–D)`. §Stage-specific code deliverables lines for "Refactoring" and "Merge proposer" rewritten to reference `integration-workflow Phase B unified implementer` and `integration-workflow Phase B Commit 1 / Phase D re-sync`.
- `agents/reviewer.md` — description frontmatter dropped `merge-workflow (post-merge drift test + integration review)`; replaced with `integration-workflow (drift test review, Phase B recon + verify review, and Phase D post-merge drift test + integration review)`.
- `skills/refactor-and-integrate/SKILL.md` — "Workflow skills (...)" parenthetical in the body reduced to `superRA:integration-workflow` only. §Integration §Used-by list collapsed from two bullets (integration-workflow + merge-workflow) to one integration-workflow bullet naming Phase A drift tests, Phase B recon/unified-implementer/verify-reviewer, and Phase D post-merge drift-test + integration-review re-runs as the three call sites.
- `skills/refactor-and-integrate/references/drift-test-quality.md` — Cross-cutting Red Flags preamble rewritten: `integration-workflow Stage 1 / Stage 2`, `merge-workflow Step 2`, `semantic-merge` → `integration-workflow Phase A`, `Phase B`, `Phase D post-merge verification`, `semantic-merge`.
- `skills/agent-orchestration/references/agent-teams.md` — Teams-flow diagram collapsed: three cascading boxes (execution → integration → merge) → two boxes (execution → integration), with Phases A–D annotation on the integration team.
- `skills/using-superRA/references/codex-tools.md` — "Finishing a development branch" pointer retargeted from `superRA:merge-workflow` to `superRA:integration-workflow Phase D`.
- `tests/structural-invariants.sh` — `dispatch_files` list pruned (removed `skills/merge-workflow/SKILL.md`); check-10a (canonical-prefix count on dispatch templates) now scans four files instead of five.

**Scope boundary (not touched by Task 3):**

- **Task 6's peripheral surfaces** — `README.md`, `CLAUDE.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md` Skill-Load Manifest + inventory, `skills/execution-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`, and `skills/handoff-doc/references/plan-anatomy.md` Workflow Status block. These are Task 6 Steps 1–5 scope and were left intact so the Task 3 diff stays minimum-net.
- **RELEASE-NOTES.md pre-existing entries** — earlier release notes mention `merge-workflow` by name (it was a live skill at the time); these are historical record and were not rewritten. The new deprecation bullet is the only edit.

**Verification:**

- `grep -rn "merge-workflow" skills/ agents/ hooks/ README.md CLAUDE.md RELEASE-NOTES.md` returns only (a) Task 6 scope files, (b) the new deprecation line in RELEASE-NOTES.md, and (c) pre-existing historical RELEASE-NOTES entries. No hits remain in Task 3's scope files.
- `skills/merge-workflow/` directory no longer exists; `git status` shows `deleted: skills/merge-workflow/SKILL.md`.
- Minimum-net-diff: eight files modified plus one deletion, PLAN.md, and RESULTS.md. No unrelated hunks; each repoint is a 1–3 line edit targeted at a known caller string.

## Task 4: Update `semantic-merge` caller paths and handoff-doc coherence rule

**Status:** IMPLEMENTED

**Summary:** `skills/semantic-merge/SKILL.md` caller-path text re-pointed from the deleted `merge-workflow` onto the unified `integration-workflow` Phase A–D structure (Task 2). `skills/refactor-and-integrate/references/merge-quality.md` gains a new §How-To section ("Handoff-doc coherence through the merge") and a matching `[BLOCKING] Handoff-doc coherence` gated-checklist item carrying the escalation rule for substantive PLAN.md/RESULTS.md restructures.

**Key structural choices:**

- **Two invocation sites named, not one.** The new caller-path text cites both Phase B (recon trial-merge + Tier 2/3 unified implementer) and Phase D re-sync (when the pre-merge freshness check finds main advanced). Keeps the mapping accurate to `integration-workflow` Step 1 (Phase D) where `semantic-merge` is delegated a second time.
- **Dispatch-field mechanism surfaced.** Caller-path prose now states that `integration-workflow` loads `semantic-merge` via the canonical `Skills:` dispatch field on implementer/reviewer subagents — consistent with the §Decisions entry under PLAN.md ("Recon loads `superRA:semantic-merge` via the canonical `Skills:` dispatch field") and with the shortcut-axis rule (Tier 1 follow-ups do NOT load semantic-merge).
- **Delegated-mode verification table updated.** The four "skip" rows now name Phase B verify / Phase D post-merge checks instead of `merge-workflow Step 2a/2b/4`. Tier + incoming-impact return contract repointed at Phase B's two-axis shortcut evaluation and Phase D's re-entry decision.
- **Handoff-doc coherence §How-To is new content.** Scope-defines what counts as a "substantive restructure" (task add/remove/combine, DAG edge flip, APPROVED status invalidation from a cascade) versus routine content conflict (reworded prose, updated numbers inside an unchanged task block, new review-notes blockquote text). Routine conflicts stay mechanical; restructures escalate to `planning-workflow §Changing Plans` **before** the merge proceeds — orchestrator authors the Restructure Proposal, researcher decides, decision logged per `handoff-doc §User Decisions Log`, `PLAN.md` updated atomically, only then does Commit 2 land (reflecting the post-restructure plan).
- **Checklist item is a single `[BLOCKING]` entry.** Points back into the §How-To rather than restating the trigger list — one source of truth. Placed in the "Handoff-doc coherence" checklist group just above "Integration map", so the reviewer hits it between result-integrity checks and the map-format check.
- **Cascade semantics not duplicated.** The DAG cascade rule for `APPROVED` invalidation points at `handoff-doc/references/plan-anatomy.md` (existing owner of the rule) rather than restating the cascade mechanics.

**Verification:**

- `grep -n "merge-workflow" skills/semantic-merge/` returns zero hits — every caller-path reference (description frontmatter, When-to-Use bullet, delegated-mode paragraph, mode-aware verification table, Tier 1 / 2 / 3 Delegated lines, Working-Principles drift-test bullet, What-to-Report header, delegated-return contract, Integration §Called-by + Pairs-with) rewritten.
- `[BLOCKING] Handoff-doc coherence` item present in `merge-quality.md` Gated Checklist; §How-To "Handoff-doc coherence through the merge" section present and cross-referenced.
- Dry-read through a Tier 3 example where incoming PLAN.md restructures a task block: `semantic-merge` → Tier 3 classification → merge-proposer loads `merge-quality.md` → sees `[BLOCKING] Handoff-doc coherence` checklist item → §How-To points at `planning-workflow §Changing Plans` before Commit 2. Escalation path discoverable from `semantic-merge` alone via its required `merge-quality.md` load on the `merge` stage (per `using-superRA` §Skill-Load Manifest).
- Minimum-net-diff: only two files touched in this task (`skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/references/merge-quality.md`) plus PLAN.md / RESULTS.md. No unrelated hunks.

## Task 5: Minimal `planning-workflow §Changing Plans` extension + B→B re-entry trigger

**Status:** IMPLEMENTED

**Summary:** Two minimal additions wire INTEGRATE-phase re-entry into the existing plan-change and cascade machinery without duplicating either. `planning-workflow §Changing Plans` now has one bullet under **Material** acknowledging mid-INTEGRATE restructure findings (Phase B recon, Phase B verify reviewer, Phase C doc-reviewer, Phase D semantic-merge) as valid triggers, with the orchestrator-authors / researcher-decides ownership rule stated inline. `plan-anatomy.md` gains one sentence adjacent to the existing Integration-status cascade rule documenting the **B→B re-entry trigger**: recon's per-task annotations gate the flip — annotated tasks → `Integration status: REVISE`, unannotated tasks stay `APPROVED`.

**Key structural choices:**

- **Pointers, not duplicated protocol.** The `planning-workflow §Changing Plans` bullet names the four Phase-B/C/D call sites that can raise a restructure finding and restates only the ownership rule ("orchestrator authors the Restructure Proposal; the researcher decides"). The protocol body (confirm intent → log decision → inline-edit PLAN.md → update Workflow Status → commit atomically → resume) is unchanged — mid-INTEGRATE restructures ride the existing cascade semantics.
- **Trigger sentence placed at the cascade-rule owner.** The B→B sentence lives in `plan-anatomy.md` next to the Integration-status cascade bullet, not in `integration-workflow`. One source of truth: Phase B recon is the mechanical trigger, but the cascade rule itself (what annotated vs unannotated means for the `Integration status` flip) belongs to the PLAN.md anatomy reference that owns the field's semantics.
- **Wording aligned with Task 2's Phase B recon.** `integration-workflow` Phase B Step 1 already states recon "walks every APPROVED-integration task, appends per-task integration review-notes blockquotes … for any task whose outputs need codebase-fit refactor, drift-test update, handoff-doc coherence, or merge-induced semantic clash." The new sentence uses the same annotation vocabulary without restating the recon procedure.

**Verification:**

- Cross-read with `integration-workflow/SKILL.md` line 91 (Phase-B plan-change pointer) and line 447 (Integration §Called-by entry for `planning-workflow §Changing Plans`): all three pointers use the same "orchestrator authors the Restructure Proposal; researcher decides" framing. No duplication of the cascade semantics — `planning-workflow §Changing Plans` points at `plan-anatomy.md` for the field vocabulary, and `plan-anatomy.md` points at `integration-workflow` Phase B recon as the trigger author.
- Minimum-net-diff: only two skill files touched (`skills/planning-workflow/SKILL.md` + `skills/handoff-doc/references/plan-anatomy.md`) plus PLAN.md / RESULTS.md. One bullet added in the first file, one sentence appended to an existing bullet in the second. No unrelated hunks.

## Task 6: Sync peripheral surfaces

**Status:** IMPLEMENTED

**Files touched:**
- `skills/using-superRA/SKILL.md` — Skill Inventory table: dropped `merge-workflow` row; widened `integration-workflow` one-liner to cover Phases A–D. Skill-Load Manifest: added clarifying paragraph after the table noting the `merge` stage is used for standalone `semantic-merge` delegated-mode dispatches; inside Phase B, the unified implementer runs `Stage: integration` and conditionally loads `superRA:semantic-merge` via the canonical `Skills:` field on Tier 2/3.
- `skills/execution-workflow/SKILL.md` — preamble, top-level-loop Step 4, and §Integration required-workflow-skills list all hand off to `integration-workflow` (Phases A–D) only; no `merge-workflow` reference.
- `skills/handoff-doc/references/plan-anatomy.md` — Workflow Status milestones renamed to Phase A / B / C / D (drift tests / refactor / docs / merge); User Decisions Log cross-task-decision location list updated from Step 1 / Step 3 to Phase A / Phase C.
- `skills/agent-orchestration/SKILL.md` — reviewer-feedback-discipline call-site list updated (line 187): now names `execution-workflow`, `integration-workflow` Phase A/B/C, and standalone `semantic-merge`. Override-pattern language (lines 147–148) confirmed adequate for utility-skill on-demand loading.
- `skills/integration-workflow/SKILL.md` — §Agent Loads row list dropped `merge` (no longer a stage this workflow dispatches); §Red Flags entry on domain-discipline artifacts updated to the conditional `Skills:` pattern.
- `skills/CATEGORIES.md` — dropped `merge-workflow` row; rewrote `integration-workflow` row to Phases A–D; updated `semantic-merge` row to name `integration-workflow` Phase B as caller.
- `README.md` — workflow-map ASCII block replaced (unified `integration-workflow` with Phase A–D bullets); Mermaid diagram MERGE node replaced with Phase D node, added B→B and D→B re-entry arrows; Workflow skill table dropped `merge-workflow` row and widened `integration-workflow` row; Utility skill table `semantic-merge` row cites `integration-workflow` Phase B as caller.
- `CLAUDE.md` — §DRY workflow-skills ownership list updated to drop `merge-workflow` (now names `planning-workflow`, `execution-workflow`, `integration-workflow` Phases A–D).
- `RELEASE-NOTES.md` — Task 3's deprecation bullet augmented with a second bullet listing the peripheral-surface sync (skill inventory, Manifest clarification, Workflow Status milestone rename, README/CATEGORIES/CLAUDE.md updates).

**Validation:**
- `grep merge-workflow` across repo: remaining hits are PLAN.md / RESULTS.md / RELEASE-NOTES.md / `docs/plans/` / `docs/process-issues-2026-04-16.md` — all historical or task-description references. No active skill, agent, or hook file carries a `merge-workflow` reference.
- Dispatch prompts sampled: `integration-workflow` Phase B Steps 1, 3, 4 each follow the canonical shape (required fields first — `Stage:`, `Task:`, `Git range:` / `Worktree:`; optional `Skills: superRA:semantic-merge` between required fields and prefix line on Tier 2/3; canonical prefix verbatim; `Additionally:` anchor last with additive steering only).
- Shared-flow checklist (`refactor-and-integrate` §Three Disciplines) remains single-source — both implementer and reviewer walk the same file per the architectural rule. No review-only parallel document introduced by this task.
- Minimum-net-diff: edits confined to skill inventory / Manifest clarification / milestone rename / caller-list updates. No tuned content (Red Flags tables, rationalization lists, RA-framing language) reworded.

## Task 7: End-to-end dry-run verification

**Status:** IMPLEMENTED

**Summary:** Dry-read simulation of the refactored `integration-workflow` Phases A → D on a hypothetical branch, plus on-paper injection of the four stress scenarios prescribed by the task (B→B main-advance re-entry, mid-Phase-B plan-change, unrelated-hunk injection in Commit 2, D→B main-advance during Phase C). The refactored skill graph carries all four scenarios end-to-end — every dispatch, user stop, and re-entry arrow the dry-run encountered is reachable from the committed skill files without invented protocol. Seven stale-vocabulary hits were found across six skill files (legacy "Step 3" / "Stage 1" / "Stage 2" terminology from the old integration-workflow / merge-workflow split) and fixed as part of this task; all are pointer strings, no tuned content touched.

### Scenarios walked

**(1) Happy path: Phase A → D on a clean branch.**

- Phase A: drift-test creation. Main agent follows `integration-workflow §Phase A` — extracts key results from RESULTS.md, stops at Step 2 for user confirmation via `AskUserQuestion`, dispatches test-creator (Stage `drift-test`) then test-reviewer (Stage `drift-test`), iterates REVISE/APPROVE, runs suite green, commits `tests/`, flips `Drift tests created` milestone. Every dispatch matches canonical shape (required fields first, `Additionally:` anchor last, no restated PLAN.md content).
- Phase B: dispatches recon reviewer with `Skills: superRA:semantic-merge`. Recon commits per-task integration review-notes blockquotes (where warranted) + one-line Tier classification to §Decisions. Orchestrator flips `Integration status: REVISE` on annotated tasks. Evaluates the two shortcut axes; the four combinations (Tier 1 + zero / Tier 1 + annotations / Tier 2 or 3 + zero / Tier 2 or 3 + annotations) all resolve to a single reachable path. Step 2b batched `AskUserQuestion` for research-meaningful items. Unified implementer dispatched with `Tasks in scope:` scoping and conditional `Skills: superRA:semantic-merge`. Two-commit structure (mechanical merge → unified refactor). Drift tests run between commits. Verify reviewer reviews cumulative diff with same `Tasks in scope:` restriction, refuses out-of-scope hunks as `[BLOCKING]` vs Minimum-net-diff.
- Phase C: orchestrator resolves `RESULTS_DIR`; dispatches doc-writer (Stage `documentation`) then doc-reviewer (Stage `documentation`); four-commit maturation lands atomically; flips `Docs finalized`; orchestrator-owned PLAN.md disposition decision.
- Phase D: pre-merge freshness check (`git fetch` + `git log <merge-base>..origin/<base-branch>`); if main not advanced → flip `Merged`, execute Option 1 (local merge) or Option 2 (push + PR); cleanup worktree per `agent-orchestration/references/worktree-harness-fallback.md`.

Result: skill text is internally consistent; all autonomy stop-points enumerated in `Phase Map §Autonomy` are cross-referenced to `using-superRA §Universal Principles (#4)` and to `handoff-doc §User Decisions Log`.

**(2) B→B re-entry: main advances mid-integration.**

Injected scenario: Phase B completes with `Refactored` milestone flipped; before Phase C starts, `origin/main` moves with commits touching two of the five analysis-branch tasks' input files. The researcher triggers another integration pass.

Walked path: re-enter Phase B Step 1 → dispatch recon reviewer with new `<merge-base>..HEAD` git range. Recon annotates the two affected tasks' PLAN.md blockquotes with `[BLOCKING]` merge-induced-semantic-clash items; leaves the other three tasks unannotated; logs new Tier line under §Decisions. Orchestrator Step 2: the two annotated tasks flip to `Integration status: REVISE`; the three unannotated tasks stay `APPROVED`. Unchecks `Refactored` milestone (line 54 of `plan-anatomy.md`) per the DAG-cascade rule.

Consistency check: the B→B trigger sentence in `handoff-doc/references/plan-anatomy.md` line 179 (added by Task 5) reads "*when main advances mid-integration, `integration-workflow` Phase B recon (the reviewer that authors per-task integration review-notes blockquotes) gates the flip — tasks it annotates get `**Integration status:** REVISE`; tasks it does not annotate stay `APPROVED`.*" The dry-run walked this sentence exactly. Scope-by-Integration-status rule in `refactor-and-integrate §Scope by Integration Status` then keeps the three APPROVED-integration tasks out of the unified implementer's diff, preserving minimum-net-diff. **Consistent; no gap.**

**(3) Mid-Phase-B plan-change trigger: substantive restructure surfaces.**

Injected scenario: recon's per-task annotations surface that Task 3's sample construction overlaps with a new main-side helper that subsumes it — the cleanest resolution is to merge Task 3 into the helper and delete Task 3. This is a **substantive restructure** (task remove/combine + DAG edge flip), not a routine conflict.

Walked path: integration-workflow Phase B §Plan-change trigger (lines 91 of the skill) reads "*If the recon reviewer (Step 1) or verify reviewer (Step 4) surfaces a substantive restructure finding — task add/remove/combine, DAG edge flip, prior APPROVED status invalidation — escalate via `planning-workflow §Changing Plans` (orchestrator authors the restructure proposal; researcher decides) before continuing.*" The orchestrator pauses Phase B, authors a Restructure Proposal, stops for the researcher via `AskUserQuestion` per §Changing Plans Step 1, logs the decision per §User Decisions Log Step 2, edits PLAN.md inline per Step 3 (removes Task 3 block, renumbers if needed, updates Depends-on fields), unchecks affected Workflow Status boxes per Step 4, commits atomically per Step 5, then resumes by re-entering Phase B Step 1 per Step 6.

Consistency check: `planning-workflow §Changing Plans` Material-list bullet added by Task 5 (line 155) reads "*Substantive restructure findings surfaced mid-INTEGRATE (by `integration-workflow` Phase B recon, Phase B verify reviewer, Phase C doc-reviewer, or Phase D semantic-merge) — task add/remove/combine, DAG edge flip, prior APPROVED status invalidation. The orchestrator authors the Restructure Proposal; the researcher decides.*" Ownership (orchestrator authors, researcher decides) matches the Phase B pointer and the `integration-workflow §Integration §Escalates to` block (line 447). **Consistent; no duplication of protocol between the two pointers — the protocol body lives only in `planning-workflow §Changing Plans`.**

**(4) Unrelated-hunk injection in Commit 2.**

Injected scenario: the unified implementer, during Commit 2 of Phase B, also re-formats an unrelated module (`utils/dates.py`) that is not in the in-scope task list and not touched by the merge. This is the canonical minimum-net-diff violation.

Walked paths:

- *Implementer self-check* — `refactor-and-integrate §Implementer Self-Check (Before Every Commit)` (lines 80–89 of SKILL.md) runs `git diff <merge-base>..HEAD` before the commit. Procedure Step 2: "*For each hunk, ask: which `[BLOCKING]` or `[ADVISORY]` item justifies this change?*" The `utils/dates.py` reformat has no justification in the three references' checklists (not drift-test preservation, not codebase-convention fit for any in-scope task, not handoff-doc coherence, not documentation currency, not on the integration map). Procedure Step 3: "*Any hunk without a justification is out of scope. Revert it, OR re-justify it by adding the underlying need to the integration map.*" Self-check catches it before commit.
- *Verify-reviewer catch* — if the implementer commits anyway, Phase B Step 4 verify reviewer runs `git diff <merge-base>..HEAD` as evidence per the same Implementer Self-Check section ("*The verify reviewer runs the same `git diff <merge-base>..HEAD` as evidence and walks each hunk through the same reference checklists.*"). The dispatch prompt (integration-workflow line 193–194) reads "*Raise any out-of-scope hunk as a [BLOCKING] finding against Minimum-net-diff.*" The reviewer annotates the `utils/dates.py` hunks as `[BLOCKING]` Minimum-net-diff violations → REVISE → orchestrator adjudicates → implementer reverts the hunks in a follow-up commit → narrow re-review.

**Both nets catch it. Consistent.**

**(5) D→B re-entry: main advances during Phase C.**

Injected scenario: Phase B APPROVED and `Refactored` flipped; during Phase C's doc-writer iteration (say, between the doc-writer's Commit 2 and the doc-reviewer's APPROVE), a colleague lands three commits on main that touch one of the analysis-branch input files. Phase D Step 1 detects the drift.

Walked path: Phase D Step 1 (lines 321–328 of integration-workflow SKILL.md) runs `git fetch origin <base-branch>` + `git log --oneline <merge-base>..origin/<base-branch>`; finds three new commits; re-enters Phase B. Phase B re-opens: new recon dispatch → new Tier classification → new per-task annotations. If only the single task's input file conflicts, recon annotates that one task only; the other tasks stay `Integration status: APPROVED`. Unified implementer + verify reviewer run scoped to the single re-flagged task. After APPROVE, re-check `Refactored`. Then Phase C re-runs per the doc-writer's "always re-runs the whole matured doc" rule (SKILL.md line 244); doc-reviewer reviews the diff from the last APPROVED state. Then Phase D Step 1 re-checks freshness. Eventually clean → Phase D Steps 2–4 execute.

Consistency check: the Phase Map box at lines 18–31 of integration-workflow SKILL.md explicitly draws the D→B arrow ("`D → B` when the semantic-merge in Phase D reveals main moved again"). The Phase D Step 1 text enforces it mechanically. The doc-writer's "re-run the whole matured doc on every integration pass" rule handles the C side (Phase C §Step 2 prose). **Consistent; no gap.**

### Findings

**[BLOCKING]** — none. All five scenarios walked end-to-end on the refactored skill graph with no invented protocol and no unreachable arrows.

**[ADVISORY] — stale-vocabulary hits (fixed in this commit).** Task 6's peripheral-surface sweep missed seven strings that still named the pre-unification vocabulary ("integration-workflow Step 1 / Step 3" or "integration-workflow Stage 1 / Stage 2") on skill files other than the ones Task 6 explicitly enumerated. All are pointer strings — no tuned content (Red Flags, RA-framing, rationalization lists) affected. Fixed in-place:

| File | Line | Before | After |
|---|---|---|---|
| `skills/planning-workflow/SKILL.md` | 123 | `integration-workflow Step 3` | `integration-workflow Phase C` |
| `skills/planning-workflow/SKILL.md` | 175 | `integration-workflow Stage 2` | `integration-workflow Phase B` |
| `skills/using-superRA/SKILL.md` | 58 | `integration-workflow Step 3 doc-writer` | `integration-workflow Phase C doc-writer` |
| `skills/handoff-doc/SKILL.md` | 56 | `integration-workflow Step 3 doc-writer` | `integration-workflow Phase C doc-writer` |
| `skills/handoff-doc/references/results-anatomy.md` | 8 | `integration-workflow Step 3` | `integration-workflow Phase C` |
| `skills/handoff-doc/references/results-anatomy.md` | 106 | `integration-workflow Step 3 … Stage 2 refactor + integration review` | `integration-workflow Phase C … Phase B refactor + integration review` |
| `skills/econ-data-analysis/SKILL.md` | 34 | `integration-workflow Stage 1` | `integration-workflow Phase A` |
| `skills/econ-data-analysis/references/integrate-drift-tests.md` | 3, 40 | `integration-workflow Stage 1 / Stage 1 Step 2` | `integration-workflow Phase A / Phase A Step 2` |
| `skills/refactor-and-integrate/references/codebase-integration.md` | 21, 34 | `Stage 2 refactoring` / `integration-workflow Step 3` | `Phase B refactoring` / `integration-workflow Phase C` |
| `skills/report-in-markdown/SKILL.md` | 14, 34, 35 | `integration-workflow Step 3` | `integration-workflow Phase C` |
| `skills/report-in-markdown/references/final-form.md` | 3, 125, 131 | `integration-workflow Step 3 / Stage 2 / Stage 2` | `integration-workflow Phase C / Phase B / Phase B` |
| `skills/using-superRA/references/main-agent.md` | 67 | `integration-workflow Step 1 / Step 3` | `integration-workflow Phase A / Phase C` |
| `skills/CATEGORIES.md` | 41 | `integration-workflow Step 3 doc-writer` | `integration-workflow Phase C doc-writer` |
| `skills/report-in-markdown/SKILL.md` | 3 | `INTEGRATE Step 3` (frontmatter) | `INTEGRATE Phase C` |
| `skills/report-in-markdown/SKILL.md` | 43 | `INTEGRATE Step 3` | `INTEGRATE Phase C` |
| `skills/report-in-markdown/SKILL.md` | 52 | `INTEGRATE Step 3 caller` | `INTEGRATE Phase C caller` |
| `skills/report-in-markdown/references/baseline-io.md` | 36 | `INTEGRATE Step 3` | `INTEGRATE Phase C` |

**Legitimately retained "Stage 1 / Stage 2" usage.** The RESULTS.md document-lifecycle terminology (Stage 1 dev log → Stage 2 permanent record) is orthogonal to the workflow's old Stage 1 / Stage 2 naming and remains in force across `handoff-doc`, `report-in-markdown`, and their references. Only the workflow-phase label usage was stale.

**Legitimately retained "Step N" usage inside other workflows.** `execution-workflow §Step 4` (the 4-option completion menu) and `integration-workflow §Phase A Step 2`, `§Phase C Step 1` etc. are live, per-phase step labels in the new vocabulary and are not affected.

**RELEASE-NOTES.md historical hits.** `RELEASE-NOTES.md` line 15 and the §"integration-workflow Step 3 consolidation" heading at line 121 are historical record — they document a release made under the old vocabulary and should not be rewritten (same principle as Task 3 Step 4 applied to pre-existing RELEASE-NOTES entries for `merge-workflow`).

### Verification

- **Phase Map reachability**: every re-entry arrow (`B → A`, `B → B`, `C → B`, `D → B`, `Anywhere → planning-workflow §Changing Plans`) in the Phase Map box (integration-workflow SKILL.md lines 18–31) is cited in text elsewhere in the same file (lines 33, 91, 200–203, 262, 321–328).
- **Cross-skill pointer consistency**: planning-workflow §Changing Plans material-list bullet, integration-workflow Phase B plan-change pointer, and integration-workflow §Integration §Escalates-to block all use the same "orchestrator authors, researcher decides" framing — verified by Task 5 and re-verified here.
- **Scope-by-Integration-status invariance**: the rule is stated in `refactor-and-integrate §Scope by Integration Status`, pointed at from the DAG cascade rule in `plan-anatomy.md` line 179, and wired through the unified implementer + verify reviewer dispatch templates (`Tasks in scope:` field; "Refuse to walk APPROVED-integration tasks" in `Additionally:`). No parallel restatement.
- **Minimum-net-diff protection surfaces**: Implementer Self-Check (`refactor-and-integrate/SKILL.md` lines 80–89) + verify-reviewer dispatch `Additionally:` clause (integration-workflow line 193–194) + `[BLOCKING] Handoff-doc coherence` item in `merge-quality.md` compose without overlap.
- **Post-edit stale-vocabulary sweep**: `grep -rn "integration-workflow.*(Stage [12]|Step [1-9])" skills/` post-fixes returns only legitimate per-phase Step N labels and the RESULTS.md Stage 1/Stage 2 lifecycle. No remaining old-vocabulary hits.
- **Minimum-net-diff for this task**: touched eight files (vocabulary fixes) + PLAN.md + RESULTS.md. All hunks are 1-2 line pointer-string replacements. No tuned content edited; no logic edited.

### Conclusion

The refactored `integration-workflow` is internally consistent and externally pointer-correct against `planning-workflow §Changing Plans`, `handoff-doc/references/plan-anatomy.md`, and `refactor-and-integrate`. The five scenarios (happy path, B→B, mid-Phase-B plan-change, unrelated-hunk injection, D→B) all resolve on the committed skill text. Findings were seventeen ADVISORY-level stale-vocabulary strings (thirteen in the initial sweep + four `INTEGRATE Step 3` hits surfaced in review), all fixed. Post-fix broader grep (`INTEGRATE Step\|INTEGRATE Stage\|integration-workflow Step\|integration-workflow Stage`) returns zero hits in skills/, agents/, hooks/. No blocking inconsistency surfaced — the plan's Expected Results (a)–(d) are met.

