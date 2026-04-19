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

**Summary:** `skills/integration-workflow/SKILL.md` rewritten to cover the full INTEGRATE phase from drift tests through PR/merge as Phases A–D. Former `merge-workflow` content folded in as Phase D (PR body template preserved verbatim). Former Stage 1 / Stage 2 / Step 3 collapsed into A / B / C; B now carries the unified two-commit sync+refactor pass with an explicit three-dispatch internal structure (recon reviewer → batched user decisions → unified implementer → verify reviewer). The skill is the only workflow owner of INTEGRATE — `merge-workflow` will be deleted in Task 3.

**Key structural choices:**

- **Phase map up front.** ASCII diagram at the top of the file names all four phases and every re-entry arrow (B→A, B→B, C→B, D→B, Anywhere→`planning-workflow §Changing Plans`). Re-entry is framed as the normal case, not an exception.
- **Phase B three-dispatch structure explicit.** Step 1 recon reviewer produces the integration map + tier preview + user-decision list; Step 2 is a single batched `AskUserQuestion` (no mid-implementation interruptions); Step 3 is the unified implementer with Commit 1 (mechanical semantic-merge, delegated mode) and Commit 2 (unified integration); Step 4 verify reviewer walks `git diff <merge-base>..HEAD`. Drift tests run between Commit 1 and Commit 2 and again after Commit 2.
- **Orchestrator split safety-valve** documented at Phase B Step 2 — when the integration map exceeds the ~150k context threshold, siblings run on parallel worktrees per `agent-orchestration §Concurrent Writers`.
- **Minimum-net-diff enforcement.** The body points at `superRA:refactor-and-integrate` for the top item and the Implementer Self-Check (`git diff <merge-base>..HEAD`); the verify-reviewer dispatch explicitly tells the reviewer to compute the same diff and walk every hunk.
- **Plan-change pointer.** One bullet in Phase B body names the escalation path to `planning-workflow §Changing Plans` (orchestrator authors the restructure proposal; researcher decides). No protocol duplication — just the pointer.
- **Phase D folds in merge-workflow verbatim.** Step 1 (pre-merge freshness check — re-enter Phase B if main advanced), Step 2 (`Merged` milestone flip), Step 3a/3b (local merge vs PR push, full PR body template copied without paraphrasing), Step 4 (worktree cleanup) — all preserved. The skill-calls-skill mechanics (semantic-merge in delegated mode, `worktree-harness-fallback.md` for cleanup) remain identical.
- **Dispatches use canonical shape only.** Every dispatch block in the file opens with the canonical prefix "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …" and carries only strictly additive steering in the `Additionally:` tail — no restated PLAN.md content, no duplicated skill-load lines, no repeated checklist items. Required fields appear first; `Additionally:` is anchor-last.
- **Legitimate stop points enumerated.** Five stops total (Phase A drift-test confirmation, Phase B batched decisions, Phase B/D meaningful-drift stop, Phase C RESULTS_DIR when guidance is silent, Phase C PLAN.md disposition). Every one is logged per `superRA:handoff-doc §User Decisions Log` before the workflow acts.
- **Red Flags body stays principle-level.** No Tier 3 blockquote, no Red Flags Never-list verbatim from merge-workflow — pointers to `refactor-and-integrate/references/` instead (Task 1 owns those). RA-framing reference preserved via a one-line pointer to `using-superRA §Universal Principles`.
- **Hand-off targets updated.** Phase D is the terminal phase; no reference to `superRA:merge-workflow` remains. Task 3 can delete the merge-workflow directory without breaking a caller.

**Verification:**

- Canonical shape: every `Agent(subagent_type: …)` block in the new file carries `Stage:` and `Task:` first, `Git range:` where reviewer-only, and an `Additionally:` tail with only additive content.
- Four workflow principles: (1) implementer-reviewer pair at every gate — retained at drift-test pair, verify-reviewer pair for Phase B, doc-writer / doc-reviewer pair for Phase C, post-merge safety-check via re-entry into Phase B. (2) handoff docs as record — every stop point logs into PLAN.md before the work runs. (3) fast early / strict before merge / semantic merges — Phase B's Commit 1 is always semantic-merge (delegated), and Phase D Step 1 re-enters Phase B if main advanced. (4) autonomous with human in loop — five enumerated stop points, explicit "between stops, run on own power" language.
- Deferred items: manifest / plan-anatomy / execution-workflow hand-off wording update is Task 6; semantic-merge caller-path text + `[BLOCKING] Handoff-doc coherence` is Task 4; planning-workflow bullet is Task 5; merge-workflow directory deletion is Task 3.

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
