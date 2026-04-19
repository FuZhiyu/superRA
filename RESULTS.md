# Unified Integration-Workflow Refactor — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-19 (bootstrap)
**Status:** In Progress

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

**Status:** Not started

## Task 4: Update `semantic-merge` caller paths and handoff-doc coherence rule

**Status:** Not started

## Task 5: Minimal `planning-workflow §Changing Plans` extension

**Status:** Not started

## Task 6: Sync peripheral surfaces

**Status:** Not started

## Task 7: End-to-end dry-run verification

**Status:** Not started
