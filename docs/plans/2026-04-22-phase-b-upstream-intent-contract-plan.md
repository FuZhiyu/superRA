# Tighten Phase B Upstream-Intent and Minimum-Net-Diff Contract Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all `PLAN.md` / `RESULTS.md` editing. Use `skill-creator` when editing any `skills/*/SKILL.md`. Treat this as behavior-shaping superRA work: preserve one source of truth per concern, keep edits surgical, and validate on at least one harness-visible test surface before claiming done.

**Objective:** Recast Phase B around a frozen-base upstream-intent contract so the base branch is authoritative by default, branch deltas survive only when they serve approved task objectives, and implementers receive task-local upstream-intent instructions without reconstructing git history.

**Methodology:** Update the canonical handoff-doc anatomy and role ownership first, then rewrite `integration-workflow` Phase B around a recorded frozen anchor and `## Upstream Intent`, then tighten the generic integration and merge checklists so minimum-net-diff is enforced against the frozen base snapshot and recorded upstream contract, and finally add narrow structural invariants plus focused verification.

**Data Inventory:** N/A — superRA workflow / skill refactor, no empirical dataset.

**Conventions:** Preserve the repo's current division of concerns: `handoff-doc` owns PLAN anatomy, `integration-workflow` owns choreography, `refactor-and-integrate` owns generic integration gates, `semantic-merge` owns merge behavior, and `agents/` own role-local editing permissions. Archived `docs/plans/` records are historical artifacts, not canonical runtime instructions.

**Output:** Updated canonical instructions in `skills/handoff-doc/references/plan-anatomy.md`, `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/refactor-and-integrate/references/merge-quality.md`, `skills/semantic-merge/SKILL.md`, `agents/reviewer.md`, `agents/implementer.md`, plus a focused structural invariant test and verification notes in `RESULTS.md`.

**Expected Results / Hypotheses:** Canonical Phase B surfaces use `## Upstream Intent` instead of `## Integration Intent`; the section records `Base branch`, `Frozen merge base SHA`, and `Reviewed upstream range`; reviewer task-local notes carry the local upstream-intent contract; minimum-net-diff is evaluated against `git diff <frozen-merge-base>..HEAD`; upstream deletions and relocations are authoritative by default; and narrow structural guards fail fast if the retired section name or stale workflow contract reappears in canonical surfaces.

**Sensitivity Analysis:** Verify four structural shapes: the retired-construct failure shape (`## Universal Principles` restoration rejected), a legitimate shared-file additive adaptation, D->B re-entry that deletes a stale `## Upstream Intent` section when the new round has no material overlap, and the no-material-upstream-change path where no `## Upstream Intent` section is created.

**Pipeline:** `bash tests/check-harness-compatibility.sh && bash tests/test-phase-b-upstream-intent-contract.sh`

---

## Workflow Status

- [x] **Plan approved** — user supplied the target contract and explicitly asked to execute it through superRA workflows on 2026-04-22.
- [x] **Execution complete** — direct-mode fix/re-review loop completed on 2026-04-22 after the reopened Tasks 1-4 issues were resolved and verification passed.
- [ ] **Drift tests created** — not applicable to this workflow/doc task; leave unchecked.
- [x] **Refactored** — Phase B integration reviewer approved the cumulative diff on 2026-04-22 with zero task annotations; `origin/main` still matched the frozen merge base, so the merge step was a no-op.
- [x] **Docs finalized** — the permanent results record landed at `docs/plans/2026-04-22-phase-b-upstream-intent-contract-results.md`, Task 4 returned to `Review status: APPROVED`, and the doc-reviewer approved the matured file on 2026-04-22.
- [x] **Merged** — Phase D freshness check confirmed `origin/main` was still `addc9ca7fe1bdbedb080d92095facb649074c1e4`, the branch was pushed to `origin/tighten-integration-rules`, and draft PR #18 was opened against `main` on 2026-04-22.

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

---

### Task 1: Replace the branch-wide Phase B record with `## Upstream Intent`

**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `skills/handoff-doc/references/plan-anatomy.md`, `agents/reviewer.md`, `agents/implementer.md`

**Input:** The existing `## Integration Intent` anatomy, reviewer ownership rules, and the user-provided upstream-intent contract.

**Output:** Canonical PLAN anatomy and role permissions that define `## Upstream Intent`, its frozen-anchor fields, its lifecycle, and the implementer/reviewer ownership split.

**Steps:**
- [x] Rewrite `skills/handoff-doc/references/plan-anatomy.md` so the header order, section title, purpose, lifecycle, and example all use `## Upstream Intent` rather than `## Integration Intent`.
- [x] In the same anatomy update, define the required anchor lines for the active Phase B round: `Base branch`, `Frozen merge base SHA`, and `Reviewed upstream range`.
- [x] Replace the old two-line cluster format with the new branch-wide cluster contract: `Upstream change cluster (date)`, `Upstream intent`, and `Default merged expectation`, including explicit affected-task references and the rule that the section is rewritten on D->B re-entry and removed only at final closeout / PLAN disposition.
- [x] Update `agents/reviewer.md` so the integration reviewer owns `## Upstream Intent`, writes both the branch-wide section and task-local overlap notes, and includes in each overlap-driven finding the upstream file / commit / change being honored, the upstream intent in plain language, the minimal allowed branch delta, and any stale branch-side content that must not survive.
- [x] Update `agents/implementer.md` so implementers remain hands-off on `## Upstream Intent` but are explicitly required to read the branch-wide section plus task-local upstream-intent notes before editing.
- [x] Verify that canonical runtime surfaces under `skills/` and `agents/` no longer use the retired `## Integration Intent` name once this task is complete.

---

### Task 2: Rewrite `integration-workflow` Phase B around the frozen upstream contract

**Depends on:** 1
**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `skills/integration-workflow/SKILL.md`

**Input:** The current Phase B choreography plus the upstream-intent contract from Task 1.

**Output:** A Phase B workflow that records the frozen base anchor before reviewer dispatch, requires reviewer-written upstream intent plus task-local conflict notes when overlap exists, and judges completion against approved tasks plus a justified surviving diff.

**Steps:**
- [x] Rewrite the Phase B overview to frame the base branch as canonical by default and `## Upstream Intent` as the branch-wide record of what upstream was trying to do in the current integration round.
- [x] Update Phase B Step 0 so the orchestrator fetches the chosen `<base-branch>`, computes `MERGE_BASE_SHA`, and records `Base branch`, `Frozen merge base SHA`, and `Reviewed upstream range` in `PLAN.md` before the reviewer dispatch.
- [x] Update the Phase B Step 1 reviewer dispatch so it explicitly requires the two intent-writing passes whenever overlap is material: branch-wide `## Upstream Intent` plus task-local review notes carrying the local upstream contract.
- [x] Rewrite Phase B Step 2 / Step 3c / Step 4 so completion no longer requires the branch-wide section to become empty mid-round; instead, all in-scope tasks must reach `Integration status: APPROVED`, and the reviewer must confirm the surviving diff is justified by approved task objectives plus the recorded upstream contract.
- [x] Add the D->B re-entry rule: when the base advances after a prior approval, the frozen anchor and `## Upstream Intent` are rewritten in place against the new upstream range before the next review loop starts.
- [x] Sweep the file for stale `Integration Intent` language and any zero-annotation / no-material-change prose that still assumes the old section lifecycle.

---

### Task 3: Tighten generic integration and merge gates to "base-owned by default"

**Depends on:** 1, 2
**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/refactor-and-integrate/references/merge-quality.md`, `skills/semantic-merge/SKILL.md`

**Input:** The current minimum-net-diff top item, integration self-check / reviewer protocol, merge-quality checklist, and semantic-merge process.

**Output:** Canonical generic integration and merge instructions that treat the frozen Phase B base snapshot plus recorded upstream contract as the authority when that contract exists, and otherwise use the task's governing baseline for drift-test and standalone refactor / merge work.

**Steps:**
- [x] Rewrite the top blocking item in `skills/refactor-and-integrate/SKILL.md` so the Phase B / upstream-contract path uses `git diff <frozen-merge-base>..HEAD`, while drift-test and standalone refactor / merge work use the task's governing baseline with the same scope-pruning rule.
- [x] Update `skills/refactor-and-integrate/references/codebase-integration.md` so implementer self-check and reviewer evidence explicitly include base-diff pruning, the "base-owned by default" rule, and the default-authority of upstream deletions / relocations unless the task objective and review notes authorize restoration.
- [x] Update `skills/refactor-and-integrate/references/merge-quality.md` so Phase B semantic merges use the recorded upstream contract as the source of truth for what current-branch deltas are allowed to survive.
- [x] Update `skills/semantic-merge/SKILL.md` so when it is invoked from Phase B it preserves base intent by default, treats the recorded upstream contract as authoritative, and does not preserve stale branch structure merely because it existed before the merge.
- [x] Re-read the touched generic integration surfaces for DRY: the choreography should stay in `integration-workflow`, while the generic blocking rules stay in `refactor-and-integrate` / `semantic-merge` without duplicating design rationale.

---

### Task 4: Add focused structural invariants and verify the new contract

**Depends on:** 1, 2, 3
**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `tests/check-harness-compatibility.sh`, `tests/test-phase-b-upstream-intent-contract.sh`, `RESULTS.md`

**Input:** The completed contract edits from Tasks 1-3 and the user-provided structural test plan.

**Output:** A narrow verification surface that catches stale canonical terminology and missing upstream-intent contract elements, plus recorded test results.

**Steps:**
- [x] Add `tests/test-phase-b-upstream-intent-contract.sh` as a focused structural guard that asserts the canonical runtime surfaces now use `## Upstream Intent`, include the frozen-anchor fields and required cluster language, and no longer expose the retired `## Integration Intent` contract in `skills/` or `agents/`.
- [x] Keep the guard narrow: target canonical runtime files only, and assert only the intentionally retired constructs and required new contract phrases from the user plan. Do not add broad automated diff policing or grep historical `docs/plans/` artifacts.
- [x] Update `tests/check-harness-compatibility.sh` only if needed so the focused contract guard is part of the standard verification entry point without broadening that script beyond structural invariants.
- [x] Run the focused guard and the top-level compatibility check, then record exact pass/fail results and any residual limitations in `RESULTS.md`.
- [x] Perform a direct-mode reviewer pass over the touched files after implementation, using reviewer severity discipline to confirm the new contract is coherent across handoff-doc, workflow, role, and merge surfaces before marking execution complete.
