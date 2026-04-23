# Tighten Phase B Upstream-Intent and Minimum-Net-Diff Contract Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all `PLAN.md` / `RESULTS.md` editing. Use `skill-creator` when editing any `skills/*/SKILL.md`. Treat this as behavior-shaping superRA work: preserve one source of truth per concern, keep edits surgical, and validate on at least one harness-visible test surface before claiming done.

**Objective:** Simplify the Phase B upstream-intent contract into a lightweight reviewer-owned framework: no explicit `B->B` / `D->B` runtime prose, no anchor-vs-cluster ownership split, and no extra lifecycle narration beyond reviewer handling during the active round and orchestrator cleanup at Phase B closeout.

**Methodology:** Re-enter planning, rewrite Tasks 1-4 in place around the simplified contract, then update the handoff, role, workflow, merge, and focused-test surfaces together. Preserve the stable behavioral rules (base-owned-by-default, one-pass reviewer pruning, optional `## Upstream Intent`) while removing overprescriptive re-entry text and moving round-specific base context into the reviewer dispatch.

**Data Inventory:** N/A — superRA workflow / skill refactor, no empirical dataset.

**Conventions:** Preserve the repo's current division of concerns: `handoff-doc` owns PLAN anatomy, `integration-workflow` owns choreography, `refactor-and-integrate` / `semantic-merge` own reusable integration and merge guidance, and `agents/` own role-local editing permissions. Root `PLAN.md` / `RESULTS.md` are the active re-entry handoff docs for this round; archived `docs/plans/` copies remain historical snapshots.

**Output:** Updated canonical instructions in `skills/handoff-doc/references/plan-anatomy.md`, `agents/implementer.md`, `agents/reviewer.md`, `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/references/merge-quality.md`, and `skills/semantic-merge/SKILL.md`; refreshed structural guards in `tests/test-phase-b-upstream-intent-contract.sh`; regenerated project-scoped agent files `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml`; and new verification notes in the restored root `RESULTS.md`.

**Expected Results / Hypotheses:** The implementer role keeps only the read-the-header / do-not-edit-the-header rule; the reviewer owns the active `## Upstream Intent` section during Phase B; the orchestrator passes base branch / frozen merge base / reviewed upstream range in the reviewer dispatch instead of pre-editing `PLAN.md`; Phase B Step 3c still describes one reviewer pass that performs both narrow re-review and branch-wide pruning; Step 4 deletes `## Upstream Intent` at Phase B closeout; standalone merge references stay generic; and the focused guard fails fast if split-ownership or explicit re-entry wording returns.

**Sensitivity Analysis:** Verify six structural shapes: reviewer-owned active `## Upstream Intent`; reviewer dispatch carries base branch / frozen merge base / reviewed upstream range; the single-reviewer Step 3c wording; Phase B closeout deletes `## Upstream Intent`; canonical runtime surfaces no longer spell out explicit `B->B` / `D->B` or split-ownership prose; and the standalone utility-skill path still supports caller-supplied upstream intent.

**Pipeline:** `bash tests/check-harness-compatibility.sh && bash tests/test-phase-b-upstream-intent-contract.sh`

---

## Workflow Status

- [x] **Plan approved** — user explicitly asked on 2026-04-22 to restore the archived handoff pair to the root and update the plan around the new inline follow-up comments.
- [x] **Execution complete** — re-checked on 2026-04-22 after Tasks 1-4 were implemented in direct mode for the simplified contract, the first Phase B reviewer dispatch was tightened to load `handoff-doc/references/plan-anatomy.md` §Upstream Intent explicitly, `bash tests/test-phase-b-upstream-intent-contract.sh` passed with 40 assertions and 0 failures, `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` regenerated the stale reviewer agent artifact, `bash tests/check-harness-compatibility.sh` then passed, and an in-session review sweep found no remaining blocking drift in the touched runtime surfaces.
- [ ] **Drift tests created** — not applicable to this workflow/doc task; leave unchecked.
- [ ] **Refactored** — cleared on 2026-04-22 re-entry because the current scope changes the canonical Phase B / merge contract and needs a fresh integration review round.
- [ ] **Docs finalized** — cleared on 2026-04-22 re-entry because the restored root `RESULTS.md` is now the active handoff artifact for a new round.
- [ ] **Merged** — cleared on 2026-04-22 re-entry because the current comment-driven scope has not yet been integrated and published.

## Project Conventions

Walked at planning time (2026-04-22). Re-walk on-demand only.

### Repo root

- `/CLAUDE.md` (HEAD at `addc9ca`): contributor-facing superRA rules are load-bearing. Skill edits are treated as skill-creation work, tuned content should only change for observed failures, one source of truth per concern must be preserved, and README / inventory surfaces must stay in sync when shared behavior changes.
- `/AGENTS.md`: symlink alias to `/CLAUDE.md`; Codex-facing contributor guidance stays canonical in one file.
- `/AGENT.md`: second symlink alias to `/CLAUDE.md`; same guidance, exposed for harness compatibility.
- `/README.md` (HEAD at `addc9ca`): public workflow description must stay coherent with the canonical skill surface, especially around the integration phase, semantic merges, and the stated workflow principles.

### Not walked (not needed for this task)

- `docs/plans/`, `docs/superpowers/`, and harness-specific test fixtures under `tests/` — historical records and fixtures, not canonical runtime instructions for this contract change.

## Decisions

> **User decision (2026-04-22):** Treat the previously drafted "Tighten Phase B Upstream-Intent and Minimum-Net-Diff Contract" plan as the source of intent, bootstrap a root `PLAN.md` / `RESULTS.md`, and execute the work through the superRA workflow conventions in this worktree.
> **Question asked:** Should this contract change be implemented directly from the supplied plan, or should a new plan be authored first?
> **Rationale (if given):** "following superRA workflows to implement. start by writing down the plan.md"

> **User decision (2026-04-22):** Use `origin/main` as the integration base for Phase B.
> **Question asked:** Is `origin/main` the correct integration base for this branch?

> **Orchestrator decision (2026-04-22):** Phase B integration review against `origin/main` returned APPROVE with zero task annotations. `origin/main` still resolved to the frozen merge base `addc9ca7fe1bdbedb080d92095facb649074c1e4`, so there was no `## Upstream Intent` section to create and the Phase B merge step was a no-op.
> **Reviewer evidence:** `2652d81` made the zero-annotation approval state explicit by flipping Tasks 1-4 to `Integration status: APPROVED`; the reviewer also confirmed `bash tests/test-phase-b-upstream-intent-contract.sh` and `bash tests/check-harness-compatibility.sh` passed on the approved diff.

> **Convention applied (2026-04-22, no user prompt):** `RESULTS_DIR` = `docs/plans/`, target filename `2026-04-22-phase-b-upstream-intent-contract-results.md`, following the established `docs/plans/<YYYY-MM-DD>-<slug>-results.md` convention already used for superRA workflow refactors in this repo.
> **Rationale:** `docs/plans/` is the permanent archive for refactor plans and results in this repo, and this branch's deliverable is workflow/plugin documentation rather than analysis code co-located elsewhere. There are no figures in the current Stage 1 `RESULTS.md`, so the attachments step is expected to be a no-op unless the doc-writer materializes new assets.

> **Convention applied (2026-04-22, no user prompt):** Phase C Step 4 disposition = Option 1. Move `PLAN.md` alongside the matured results record as `docs/plans/2026-04-22-phase-b-upstream-intent-contract-plan.md`.
> **Rationale:** This repo already archives superRA workflow refactor handoff pairs under `docs/plans/<YYYY-MM-DD>-<slug>-{plan,results}.md`, and this branch follows the same permanent-record convention. There is no `results_attachments/` directory to move.

> **User decision (2026-04-22):** Phase D disposition — push `tighten-integration-rules` to `origin` and open a draft PR against `main`; do not perform a local merge in this worktree.
> **Question asked:** After Phase C, should this branch be merged locally, left as-is, or published as a PR?

> **Orchestrator decision (2026-04-22):** Phase D freshness check found `origin/main` unchanged since the approved Phase B round (`addc9ca7fe1bdbedb080d92095facb649074c1e4`), so no D->B re-entry was needed. The branch was pushed to `origin/tighten-integration-rules` and draft PR [#18](https://github.com/FuZhiyu/superRA/pull/18) was opened against `main`.
> **Rationale:** Publishing through a draft PR preserves the integrated state without changing local `main`, matches the user's requested execution mode, and keeps the archived handoff pair attached to the review branch.

> **Orchestrator re-entry (2026-04-22):** Independent reviewer agents audited commit `4036130` and found four MAJOR issues plus one MINOR that require a normal fix / re-review loop. Re-open Task 1 for the no-material-overlap re-entry lifecycle gap in `plan-anatomy.md` / `agents/implementer.md` and the reviewer-protocol side of the whole-diff confirmation mismatch. Re-open Task 2 for the same no-overlap lifecycle gap in `integration-workflow` plus the unresolved interaction between branch-wide hunk confirmation and narrow re-review. Re-open Task 3 because `refactor-and-integrate` applies the frozen-anchor rule to non-Phase-B uses. Re-open Task 4 because the structural guard encodes that over-broad rule and the handoff write-up overstates no-material-overlap coverage.
> **Boxes unchecked:** `Execution complete` only. `Plan approved` still stands, and no later workflow milestone had been checked.

> **User decision (2026-04-22):** Restore the archived handoff pair from `docs/plans/2026-04-22-phase-b-upstream-intent-contract-{plan,results}.md` back to root `PLAN.md` / `RESULTS.md`, then re-enter planning to incorporate the new inline follow-up comments before further implementation.
> **Question asked:** None — direct instruction to restore the archived pair and update the plan from the inline comments.

> **Orchestrator re-entry (2026-04-22):** Inline comments in `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/references/merge-quality.md`, and `skills/semantic-merge/SKILL.md`, plus a related unstaged role-surface edit in `agents/implementer.md`, materially change Tasks 1-4. Restored the archived handoff pair to the root, rewrote those task blocks in place, and unchecked `Execution complete`, `Refactored`, `Docs finalized`, and `Merged` so the current scope matches the active work.
> **Boxes unchecked:** `Execution complete`, `Refactored`, `Docs finalized`, `Merged`. `Plan approved` still stands because the user explicitly requested this follow-up round.

> **User decision (2026-04-22):** Prefer concise local instructions. When a role or workflow surface can rely on a canonical source, point to that source instead of restating the mechanics locally; explanatory duplication is a bug unless the local instruction truly needs the detail to execute correctly.
> **Question asked:** How should the inline-comment follow-up edits balance clarity against repetition?
> **Rationale (if given):** Reading the header plus a no-edit ownership rule is enough in the implementer agent; intent handling can stay in the canonical skill / handoff sources.

> **Orchestrator decision (2026-04-22):** Parallel reviewer sweep over the concise re-entry diff returned two accepted MAJOR issues and one rejected MINOR. Accepted: generalize the `semantic-merge` deletion / relocation guard so it matches the standalone upstream-intent contract, and restore a focused structural assertion for the semantic-merge base-owned-by-default clause. Rejected: removing the final-closeout guard check, because that lifecycle path is part of Tasks 2 and 4's stated scope.
> **Rationale:** The accepted findings were real contract drift; the rejected finding would have weakened a lifecycle invariant this round explicitly intended to preserve.

> **User decision (2026-04-22):** Simplify the current design further. Drop explicit `B->B` / `D->B` runtime wording, avoid overprescribing ownership splits, and keep `## Upstream Intent` as a lightweight framework rather than a fully narrated subprotocol.
> **Question asked:** How should the current Phase B upstream-intent handling be simplified?
> **Rationale (if given):** "the idea is that we do not want to overprescribe but simply provide a framework to keep the flexibility."

> **User decision (2026-04-22):** During Phase B, the reviewer handles the active `## Upstream Intent` section. The orchestrator passes the relevant base context in the reviewer prompt and removes the section once the Phase B merge / refactor round is done because it is stale.
> **Question asked:** Which ownership model should the simplified plan lock in for the active `## Upstream Intent` section during Phase B?
> **Rationale (if given):** "the orchestrator can pass through the relevant information to it in the prompt"

> **Orchestrator re-entry (2026-04-22):** The new simplification materially changes Tasks 1-4. Rewrite them around reviewer-owned active `## Upstream Intent`, prompt-passed round context, Phase B closeout deletion, and focused absence checks for explicit re-entry / split-ownership prose.
> **Boxes unchecked:** `Execution complete`, `Refactored`, `Docs finalized`, `Merged`. `Plan approved` still stands because the user explicitly requested implementation of the simplified design.

---

### Task 1: Simplify role and handoff ownership for `## Upstream Intent`

**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(pending next integration round)*

**Files affected:** `skills/handoff-doc/references/plan-anatomy.md`, `agents/implementer.md`, `agents/reviewer.md`

**Input:** The current role / handoff wording plus the user direction to keep local instructions terse, drop the split-ownership narration, and let the reviewer own the active Phase B section while the orchestrator passes round context in the prompt.

**Output:** Canonical role / handoff instructions where the implementer only reads relevant header context and treats the header as read-only, while the reviewer owns the active `## Upstream Intent` section during Phase B and the handoff anatomy records the simpler lifecycle.

**Steps:**
- [x] Confirmed the existing `agents/implementer.md` simplification already matched the target: read the task block, read the relevant header context, and do not edit the header.
- [x] Rewrote `agents/reviewer.md` so the reviewer owns the active `## Upstream Intent` section during Phase B, with the orchestrator supplying round context in the dispatch rather than pre-authoring part of the section.
- [x] Rewrote `skills/handoff-doc/references/plan-anatomy.md` so `## Upstream Intent` records the simpler contract: reviewer-owned while active, optional, and removed by the orchestrator at Phase B closeout.
- [x] Removed explicit `B->B` / `D->B` and anchor-vs-cluster ownership narration from these canonical runtime surfaces.

---

### Task 2: Simplify Phase B workflow around reviewer-owned prompt-fed context

**Depends on:** 1
**Review status:** APPROVED
**Integration status:** *(pending next integration round)*

**Files affected:** `skills/integration-workflow/SKILL.md`

**Input:** The current Phase B choreography plus the user direction to keep the framework flexible: Step 0 should compute the round context, Step 1 should pass it to the reviewer, and `## Upstream Intent` should be cleaned up at Phase B closeout instead of being narrated across later phases.

**Output:** A shorter Phase B workflow where the reviewer prompt carries the round context, Step 3c remains a single-pass verify-and-prune loop, and Step 4 removes `## Upstream Intent` immediately after Phase B APPROVE.

**Steps:**
- [x] Rewrote Phase B Step 0 so it resolves `<base-branch>` and `MERGE_BASE_SHA`, but does not pre-edit `PLAN.md`; instead it passes the relevant round context into the reviewer dispatch.
- [x] Rewrote Phase B Step 1 so the reviewer creates or updates `## Upstream Intent` only when needed, using the prompt-passed base context plus the base-side scan.
- [x] Tightened the first Phase B reviewer dispatch so it explicitly loads `superRA:handoff-doc` `references/plan-anatomy.md` §Upstream Intent for the section's format and placement, closing the remaining load-path gap.
- [x] Kept Step 3c short and stable: one reviewer pass verifies cited fixes on in-scope tasks and prunes unjustified surviving hunks from `git diff <MERGE_BASE_SHA>..HEAD`.
- [x] Rewrote Step 4 and later references so `## Upstream Intent` is deleted at Phase B closeout rather than carried into PLAN disposition.

---

### Task 3: Keep merge references generic and lightweight

**Depends on:** 1, 2
**Review status:** APPROVED
**Integration status:** *(pending next integration round)*

**Files affected:** `skills/refactor-and-integrate/references/merge-quality.md`, `skills/semantic-merge/SKILL.md`

**Input:** The current merge-quality / semantic-merge wording plus the simplified design: in Phase B, use the active reviewer-recorded section when present; otherwise rely on the caller-supplied round context or the default base-owned-by-default rule without extra lifecycle narration.

**Output:** Reusable merge references that stay generic, preserve base-owned-by-default semantics, and avoid overexplaining Phase B-specific lifecycle cases.

**Steps:**
- [x] Rewrote `skills/refactor-and-integrate/references/merge-quality.md` so Phase B uses `## Upstream Intent` when the reviewer recorded an active section for the round, and otherwise falls back to caller-supplied context without narrating no-overlap subcases.
- [x] Rewrote `skills/semantic-merge/SKILL.md` with the same light contract: use the active Phase B section when present, otherwise use caller-supplied context and preserve base intent by default.
- [x] Kept the base-owned-by-default and no-silent-restoration rules intact across both files.
- [x] Re-read the utility surfaces for DRY and concision so workflow-owned details stay in `integration-workflow`.

---

### Task 4: Refresh structural guards and verification for the simplified contract

**Depends on:** 1, 2, 3
**Review status:** APPROVED
**Integration status:** *(pending next integration round)*

**Files affected:** `tests/test-phase-b-upstream-intent-contract.sh`, `RESULTS.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`

**Input:** The simplified contract from Tasks 1-3 plus the existing focused guard and generated Codex agent surfaces.

**Output:** A narrow verification surface that catches drift in the reviewer-owned active section, prompt-passed round context, closeout deletion, and removal of explicit re-entry / split-ownership prose, plus updated verification notes in the restored root `RESULTS.md`.

**Steps:**
- [x] Updated `tests/test-phase-b-upstream-intent-contract.sh` so it asserts reviewer-owned active `## Upstream Intent`, prompt-passed base context, one-pass Step 3c pruning, Phase B closeout deletion, and concise standalone caller-supplied upstream intent.
- [x] Added focused assertions that the first Phase B reviewer dispatch explicitly loads the `plan-anatomy` upstream-intent reference and tells the reviewer to use it for section format / placement.
- [x] Added absence checks for explicit `B->B` / `D->B` runtime wording and the split-ownership narration across canonical runtime surfaces.
- [x] Kept the guard narrow: it targets only canonical runtime surfaces under `skills/`, `agents/`, and the standard compatibility entry point.
- [x] Ran the focused guard and `bash tests/check-harness-compatibility.sh`, regenerated the project-scoped Codex agent artifacts, and rewrote the restored root `RESULTS.md` back into a Stage 1 task-indexed handoff doc for this round.
- [x] Performed a fresh in-session review sweep over the touched surfaces before re-checking the execution milestone.
