---
name: integration-workflow
description: Use when an analysis is code-complete and reproducibility-verified and the user has chosen to merge back or open a PR; when you need drift tests to guard key results before they touch main; when the analysis branch needs to be brought up to date with main and refactored to fit codebase conventions (a single unified sync + refactor pass targeting one minimum-net-diff state); when the Stage 1 dev-log RESULTS.md still needs to be matured into its permanent, fact-checked, co-located form; when PLAN.md needs final disposition; when the actual local merge or PR push + worktree cleanup still needs to happen. Triggers include "prepare this for merge", "write drift tests for the key results", "sync with main and refactor", "consolidate RESULTS.md", "mature the results document", "update project docs for this analysis", "get this ready to PR", "merge this back", "open the PR", "finish this analysis", or the transition from `execution-workflow`'s completion menu (options 1 or 2). Sits at the INTEGRATE phase — the final phase of the superRA workflow, covering drift tests through PR/merge.
---

# Integration Workflow

Workflow skill for the **INTEGRATE** phase of the superRA workflow. Owns the full finishing sequence that takes a reproducibility-verified analysis branch to a merged state on main: drift-test creation (Phase A), unified sync-with-main + refactor (Phase B, iterative), documentation maturation + PLAN.md disposition (Phase C), and final local merge or PR push + cleanup (Phase D).

Assumes execution-workflow has already verified reproducibility and the user has chosen Option 1 (merge locally) or Option 2 (push + PR). If you find yourself running reproducibility checks or presenting the 4-option menu, something is wrong: that work belongs in execution-workflow.

**Core principle.** Tests guard results. A single unified diff against the merge base — produced by one two-commit sync+refactor pass per round — carries both the main update and every codebase-fit change; minimum-net-diff is load-bearing (see `superRA:refactor-and-integrate`). Nothing advances without reviewer APPROVE at every gate (drift-test review, verify review, doc review). Non-trivial merges with main use `superRA:semantic-merge` in delegated mode; Tier 1 clean merges take the fast-forward shortcut (Phase B Step 2).

**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

## Phase Map

```
Phase A — Drift Test Creation
   ↓
Phase B — Integrate (sync + refactor, iterative)
   ↓               ↑  (re-enter B when main moves again, or when
Phase C — Docs  ───┘   verify reviewer triggers a new round)
   ↓               ↑
Phase D — Final merge / PR / cleanup
                   ↑
         Anywhere ─┴─→  `planning-workflow §Changing Plans`
                        (substantive restructure: task add/remove/combine,
                         DAG flip, APPROVED invalidation; orchestrator
                         proposes, researcher decides)
```

**Re-entry is the normal case.** `B → A` when a new task is added mid-integration. `B → B` when main advances and needs another sync. `C → B` when doc-reviewer surfaces a code issue. `D → B` when the semantic-merge in Phase D reveals main moved again. Any phase can escalate to `planning-workflow §Changing Plans`.

**Autonomy.** Between stop points, run on your own power — do not check in after each phase, do not re-confirm a reviewer's APPROVE. Legitimate stop points:

- Phase A Step 2 — drift-test candidate confirmation
- Phase B — batched research-meaningful decisions surfaced by the recon reviewer (see Phase B Step 2b)
- Phase B / Phase D — meaningful drift after refactor or post-merge (see `superRA:refactor-and-integrate` `references/drift-test-quality.md`)
- Phase C Step 1 — Stage 2 RESULTS.md relocation target when project guidance is silent
- Phase C Step 4 — PLAN.md disposition

See `superRA:using-superRA` §Universal Principles (#4) for the full autonomy contract, and `superRA:handoff-doc` §User Decisions Log for how every answer must land in PLAN.md before the workflow acts on it.

## Dispatch Convention

Every dispatch in this skill uses the canonical template in `superRA:agent-orchestration` §Dispatch Templates — required fields first, `Additionally:` anchor last (strictly additive steering only). The Skill-Load Manifest in `superRA:using-superRA` is the single source of truth for what each `Stage:` loads — dispatches do not restate skill/reference loads, do not paraphrase PLAN.md, and do not repeat checklist items the agent already reads. REVISE adjudication follows `superRA:agent-orchestration` §Handling Reviewer Feedback.

The checklist discipline for every implementer self-check and every reviewer walk in this workflow lives in `superRA:refactor-and-integrate` (principles in body; `[BLOCKING]` / `[ADVISORY]` items in the stage-scoped references).

## Phase A — Drift Test Creation

Drift tests guard key results from unintended changes during Phase B refactoring, Phase D semantic-merges, and any future modification. They are the safety net that makes everything downstream safe.

**Always run the full drift-test suite on every integration pass**, regardless of re-entry scope. Authoring new drift tests is scoped to tasks with `**Integration status:** ≠ APPROVED` (plus orchestrator-declared related tasks per `planning-workflow §Changing Plans`); running the suite is not.

### Steps

1. **Extract key results from RESULTS.md.** Economic reasoning identifies main findings — not every intermediate number.

2. **Confirm coverage with the researcher.** Legitimate stop point. Use `AskUserQuestion` (plain text if unavailable):
   ```
   These results seem like the key findings to protect with drift tests:
   - [result 1: description and value]
   - [result 2: description and value]

   Which should be protected? Any to add or remove?
   ```
   Log per `superRA:handoff-doc` §User Decisions Log; commit the PLAN.md edit **before** dispatching.

3. **Dispatch test-creator.** Stage `drift-test`, canonical shape.

4. **Dispatch test-reviewer.** Stage `drift-test`, canonical shape. Iterate REVISE → fix → re-review until APPROVE (narrow re-review per reviewer protocol).

5. **Run tests — green baseline.** All drift tests pass on current code. If they fail on existing code, the tests are wrong — fix them.

6. **Commit test files.**
   ```bash
   git add tests/
   git commit -m "add drift tests for key analysis results"
   ```

7. **Flip the `Drift tests created` milestone** in `PLAN.md §Workflow Status` once every task has `**Integration status:** APPROVED` for drift-test coverage. Commit the doc edit before entering Phase B.

## Phase B — Integrate (Sync + Refactor, Iterative)

**Single unified pass targeting one final state.** See `superRA:refactor-and-integrate` `references/merge-quality.md` for the two-commit structure (Commit 1 mechanical merge; Commit 2 unified integration) and why a single cumulative diff is load-bearing.

**Re-enterable.** If main advances again before Phase D, or if a later phase surfaces a code issue, loop back to Phase B Step 1 and run another unified pass.

**Plan-change trigger.** If the recon reviewer (Step 1) or verify reviewer (Step 4) surfaces a substantive restructure finding — task add/remove/combine, DAG edge flip, prior APPROVED status invalidation — escalate via `planning-workflow §Changing Plans` (orchestrator authors the restructure proposal; researcher decides) before continuing.

### Internal Structure — Recon-Driven, Two Shortcut Axes

```
1. Recon reviewer  →  per-task integration review-notes in PLAN.md + Tier classification
2. Orchestrator    →  flip Integration status; evaluate shortcut axes
3. Batched AskUserQuestion  →  collect research-meaningful decisions (when needed)
4. Unified implementer  →  two commits: (1) mechanical merge, (2) unified refactor
5. Verify reviewer  →  cumulative diff across in-scope tasks only
```

Two **independent** shortcut axes govern Phase B path length:

- **Tier axis** (from recon's `semantic-merge` trial-merge) gates the **merge path**. Tier 1 → fast-forward only; follow-ups do NOT load `semantic-merge`. Tier 2/3 → follow-ups load `semantic-merge` via the canonical `Skills:` dispatch field.
- **Annotation axis** (count of tasks carrying new integration review-notes) gates the **refactor path**. Zero annotations → skip Steps 2b/3/4 entirely. Non-zero → dispatch the unified implementer + verify reviewer scoped to the annotated task list.

**Combined shortcuts:**
- Tier 1 + zero annotations → Phase B = `git merge --ff-only` only; terminates.
- Tier 1 + annotations → fast-forward + refactor-only implementer + verify reviewer (no `semantic-merge` load on follow-ups).
- Tier 2/3 regardless of annotations → full flow with `semantic-merge` loaded on follow-ups.

### Step 1: Dispatch the recon reviewer

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Phase B recon — per-task integration review + Tier classification
  Git range: <merge-base>..HEAD   (analysis branch vs target base branch tip)
  Skills: superRA:semantic-merge

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    recon pass — do not refactor. Run a trial `semantic-merge` against
    the base branch to produce a Tier classification (1 / 2 / 3); log
    the Tier as a one-line entry under §Decisions for this integration
    pass. For every APPROVED-integration task whose outputs need
    codebase-fit refactor, drift-test update, handoff-doc coherence
    fix, or merge-induced semantic adaptation, append a per-task
    integration review-notes blockquote with [BLOCKING] / [ADVISORY]
    items. Tasks needing no changes get no annotation.
```

The recon reviewer follows the standard reviewer protocol end-to-end — the distribution of findings into per-task PLAN.md blockquotes is the same mechanism every reviewer uses. The trial-merge happens in a scratch ref that the recon pass does not push; only the Tier classification and the annotations persist.

### Step 2: Orchestrator — flip statuses, evaluate shortcuts

After recon commits, the orchestrator reads PLAN.md:

1. For each task carrying a new integration review-notes blockquote → flip `Integration status: REVISE`. Tasks without annotations stay `APPROVED`. Commit the flips atomically with any §Decisions log additions.
2. Evaluate the two shortcut axes (Tier from §Decisions log; annotation count from the task blocks):
   - **Tier 1 + zero annotations** → execute `git merge --ff-only <base-branch>` on the analysis branch; Phase B terminates; proceed to Phase C.
   - **Tier 1 + annotations** → execute `git merge --ff-only <base-branch>` as Commit 1; skip to Step 3 (refactor-only dispatch, no `Skills: superRA:semantic-merge` on follow-ups).
   - **Tier 2/3** → proceed to Step 2b, then Step 3 with `Skills: superRA:semantic-merge` on the implementer.

### Step 2b: Batched user decisions

Collect every research-meaningful item from recon's per-task blockquotes into a single `AskUserQuestion` call (plain text if unavailable) — one batched stop point rather than interrupting mid-implementation. Include the merge-base target and the Tier classification so the researcher sees the scope at once. Log each answer per `superRA:handoff-doc` §User Decisions Log; commit the PLAN.md edit **before** dispatching the implementer.

**Orchestrator split safety-valve.** If the in-scope task list (tasks flipped to `REVISE`) is large enough that the implementer's projected context exceeds the ~150k threshold in `superRA:agent-orchestration` §Workload Balancing, split into sibling implementers on parallel worktrees per §Concurrent Writers Require Worktree Isolation. Each sibling owns a disjoint slice of the in-scope list; the orchestrator harvests and the verify reviewer walks the combined diff.

### Step 3: Dispatch the unified implementer (two-commit)

```
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: Phase B unified sync + refactor (two-commit)
  Tasks in scope: <list of tasks with Integration status: REVISE>
  Skills: superRA:semantic-merge        # omit when Tier 1

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    two-commit structure — Commit 1 is the mechanical merge
    (`semantic-merge` delegated mode if Tier 2/3; `git merge --ff-only`
    if Tier 1), Commit 2 is the unified refactor across the in-scope
    task list. Refuse to refactor code belonging to any task not listed
    in `Tasks in scope:` — those are APPROVED-integration and out of
    scope per `refactor-and-integrate` §Scope by Integration Status.
    <prior-round adjudication notes if re-dispatching>.
```

**Between the two commits — drift tests.**
- **Pass after Commit 1** → proceed to Commit 2.
- **Fail after Commit 1** → drift from main. Follow `superRA:refactor-and-integrate` `references/drift-test-quality.md` for the adjudication protocol (minor vs meaningful); meaningful drift is a legitimate stop point.

**After Commit 2 — drift tests again.**
- **Pass** → return control for Step 4 review.
- **Fail** → same adjudication protocol.

### Step 4: Dispatch the verify reviewer

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Phase B verify review (unified sync + refactor)
  Git range: <merge-base>..HEAD   (post-implementer cumulative diff)
  Tasks in scope: <same list passed to Step 3>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    walk the cumulative diff restricted to the in-scope task list;
    refuse to walk APPROVED-integration tasks not in scope per
    `refactor-and-integrate` §Scope by Integration Status. Raise any
    out-of-scope hunk as a [BLOCKING] finding against Minimum-net-diff.
    <prior-round adjudication notes if re-dispatching>.
```

Orchestrator split safety-valve applies here too when the in-scope list is large — sibling reviewers on disjoint slices, orchestrator aggregates verdicts.

- **APPROVE** → flip the in-scope tasks' `Integration status: APPROVED`. If every task is now APPROVED, flip the `Refactored` milestone in PLAN.md §Workflow Status and proceed to Phase C.
- **REVISE** → adjudicate per `superRA:agent-orchestration` §Handling Reviewer Feedback. For accepted findings, re-dispatch the implementer (narrow scope — cited fixes plus dependent findings), then re-dispatch this reviewer. Iterate until APPROVE.

If Phase C or D later triggers a new sync+refactor round, uncheck `Refactored` on entry and re-check on the next verify-reviewer APPROVE.

## Phase C — Documentation Finalization + PLAN.md Disposition

After Phase B APPROVES the unified diff, `RESULTS.md` still needs to mature from dev log to permanent record and `PLAN.md` still needs disposition. This phase gates the RESULTS.md maturation behind a **single implementer–reviewer pair** (doc-writer + doc-reviewer); the orchestrator handles the user-facing decisions (relocation target, PLAN.md disposition) on either side of the pair.

Format discipline for sub-part A (maturation) lives entirely in `superRA:report-in-markdown`. This phase orchestrates — it does not duplicate the rules.

### Step 1: Resolve `RESULTS_DIR` (orchestrator preamble)

The matured `RESULTS.md` lands in the analysis's permanent code folder, **per project guidance**. Read `CLAUDE.md`, `AGENTS.md`, or the project README for the convention. If none exists, legitimate stop point — ask via `AskUserQuestion` (plain text if unavailable):

```
Stage 2 RESULTS.md needs a permanent location in this project. The matured
file will be co-located with the analysis code so it travels with it.
Where should it land?

Suggested: <best guess from the analysis code's location, e.g. analyses/<name>/>
```

Log per `superRA:handoff-doc` §User Decisions Log **before** dispatching the doc-writer. Define `RESULTS_DIR` = resolved folder; `RESULTS_ATTACHMENTS_DIR = ${RESULTS_DIR}/attachments`. Pass both as dispatch parameters.

### Step 2: Dispatch the doc-writer

```
Agent(subagent_type: "superRA:implementer"):
  Stage: documentation
  Task: Task N in PLAN.md — Stage 2 RESULTS.md maturation
  RESULTS_DIR: <resolved permanent folder>
  RESULTS_ATTACHMENTS_DIR: ${RESULTS_DIR}/attachments

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    mature RESULTS.md per `final-form.md` §The consolidation pass —
    four ordered commits (fact-check → restructure → materialize
    figures → relocate). Land each commit separately so a session
    interruption is recoverable. In your status return, list which
    sub-commits landed.
    <prior-round doc-reviewer feedback if re-dispatching>.
```

The doc-writer always re-runs the whole matured doc on every integration pass; the doc-reviewer reviews the diff from the last APPROVED state plus any section a newly-reworked task touches. Per-commit validation and recovery rules live in `superRA:report-in-markdown` `final-form.md`.

### Step 3: Dispatch the doc-reviewer

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: documentation
  Task: Task N in PLAN.md — review of matured Stage 2 RESULTS.md
  Git range: <BASE_SHA>..<HEAD_SHA>
  RESULTS_DIR: <resolved permanent folder>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <prior-round adjudication notes if re-dispatching>.
```

Iterate REVISE → fix → narrow re-review until APPROVE. If a reviewer finding traces back to the analysis code (not the doc), that is a Phase B trigger — re-enter Phase B.

**On APPROVE:** flip the `Docs finalized` milestone in `PLAN.md §Workflow Status` (rollup: every task `**Integration status:** APPROVED` and doc-reviewer APPROVED) and commit the doc edit before Step 4. The box flips here, not after disposition — by Step 4 PLAN.md may be moved or removed.

### Step 4: PLAN.md disposition (orchestrator)

Legitimate stop point. Orchestrator-handled directly — not delegated, because disposition is a user-facing decision.

By this point `RESULTS.md` has graduated to `${RESULTS_DIR}` and project docs are in sync (audited during Phase B per `superRA:refactor-and-integrate` `references/codebase-integration.md` §Project Doc Audit). `PLAN.md` and the working `results_attachments/` folder are the last Stage 1 scaffolds at the worktree root.

Ask via `AskUserQuestion` (plain text if unavailable). Default suggestion is Option 1:

```
PLAN.md is still at the worktree root and needs disposition. RESULTS.md
has already been matured and committed at ${RESULTS_DIR}, and project
docs are up to date. Options:

1. Move PLAN.md (and results_attachments/) alongside the matured
   RESULTS.md at ${RESULTS_DIR} — keeps the prescriptive history with
   the analysis code (recommended).
2. Consolidate any plan context into existing project documentation,
   then delete PLAN.md and results_attachments/.
3. Delete PLAN.md and results_attachments/ — git history preserves
   them on this branch.

Which option?
```

Log per `superRA:handoff-doc` §User Decisions Log **before** executing. Include the log entry in the same commit that moves or removes the files.

**Option 1 (Move):**
```bash
git mv PLAN.md ${RESULTS_DIR}/
git mv results_attachments/ ${RESULTS_DIR}/source_attachments/ 2>/dev/null
git commit -m "move analysis plan to ${RESULTS_DIR}"
```
The `results_attachments/` folder is renamed `source_attachments/` to avoid colliding with the matured RESULTS.md's `attachments/` folder. Skip the rename if there are no figures.

**Option 2 (Consolidate):**
- Identify which existing project docs should pick up plan context (data inventory, methodology rationale).
- Merge into existing docs (researcher-guided).
- Remove originals:
```bash
git rm PLAN.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "consolidate analysis plan context into project docs"
```

**Option 3 (Delete):**
```bash
git rm PLAN.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "remove analysis plan (preserved in branch history)"
```

## Phase D — Final Merge / PR / Cleanup

After Phase C completes, execute the user's choice from execution-workflow Step 4. If main has advanced since Phase B, loop back to Phase B first — a fresh sync must precede the merge or push.

### Step 1: Pre-merge check — is another Phase B round needed?

Fetch the target base branch and check whether it has advanced since the last Phase B APPROVE:
```bash
git fetch origin <base-branch>
git log --oneline <merge-base>..origin/<base-branch>
```
If any commits are listed, **re-enter Phase B** for another unified sync+refactor pass. Once Phase B returns APPROVE and main has not advanced again, proceed.

### Step 2: Flip the `Merged` milestone (if PLAN.md still present)

If `PLAN.md` is still at its disposition location (Option 1 from Phase C), check the `Merged` box in §Workflow Status on the analysis branch and commit. The flip records that this workflow has executed its merge action. Skip if PLAN.md was consolidated/deleted (Options 2/3) — the merged commit history is the record.

### Step 3a — Option 1: Merge locally

```bash
git checkout <base-branch>
git pull
git merge <analysis-branch>  # should be fast-forward after Phase B
```

Verify the pipeline still runs on the merged result:
```bash
bash run_all.sh  # or: julia pipeline.jl
```
If it fails, stop and investigate — something moved between Phase B APPROVE and now.

### Step 3b — Option 2: Push and open PR

```bash
git push -u origin <analysis-branch>

gh pr create --title "<title>" --body "$(cat <<'EOF'
## Analysis Summary
<2-3 bullets of what was analyzed and key findings>

## Data
<Key datasets used, sample period, observation counts>

## Reproducibility
- Pipeline file: `run_all.sh` (or equivalent)
- All outputs generated from committed code
- Report: `<path-to-report>`

## Pre-Merge Quality
- Drift tests: included in `tests/` (guard key results); passed on merged state
- Code refactored for codebase integration
- Integration review: passed pre-merge (Phase B verify reviewer APPROVE)

## Review Checklist
- [ ] Pipeline runs end-to-end
- [ ] Drift tests pass on merged state
- [ ] Data descriptions present before all analysis operations
- [ ] Row counts logged for all sample-changing operations
EOF
)"
```

### Step 4: Cleanup worktree

If the analysis was done in a git worktree, remove it per `superRA:agent-orchestration/references/worktree-harness-fallback.md` §Remove (harness tool preferred; `git worktree remove <path>` + `git branch -D <branch>` otherwise). Seeded non-git data inside the worktree disappears with the directory — see `superRA:worktree-data-sync` §Data Teardown. Skip if no worktree.

Report what was merged/pushed and what was cleaned up.

## When to Lighten

**Standalone analysis (no existing codebase to integrate with):**
- Phase A: Always run.
- Phase B: Recon reviewer typically leaves zero annotations and reports Tier 1; the Tier 1 + zero-annotations shortcut then collapses Phase B to a single fast-forward merge (or, on a true greenfield branch with no base yet, Phase B is a no-op until a base exists).

**Small changes (single-file analysis, few results):**
- Phase A: Still run, fewer tests.
- Phase B: Verify reviewer may APPROVE immediately.

## Agent Loads

See `superRA:using-superRA` §Skill-Load Manifest — the single source of truth for what every dispatched implementer / reviewer loads per Stage. This workflow runs the `drift-test`, `integration`, `merge` (inside the Phase B implementer), and `documentation` rows.

Phase C Step 2 (mature RESULTS.md) is performed by the dispatched doc-writer subagent — an implementer-reviewer pair gates RESULTS.md maturation per workflow principle P1. Step 4 (PLAN.md disposition) and Phase D Step 2 (milestone flip) stay with the orchestrator because they are user-facing decisions, not RA-implementable tasks. Project-level doc audit is covered by the Phase B verify reviewer per `codebase-integration.md` §Project Doc Audit — not by Phase C.

## Red Flags

**Never:**
- Skip Phase A — drift tests are the safety net for everything downstream
- Run Phase B as two separate rounds (sync-only, then refactor-only) — that produces two diffs against the merge base and violates minimum-net-diff; always one unified two-commit pass
- Skip the recon reviewer and dispatch the implementer blind — the per-task integration annotations, the Tier classification, and the user-decision batch all come from recon
- Interrupt the implementer mid-run with user questions — batch every research-meaningful decision at Phase B Step 2b
- Invoke semantic-merge in its default (standalone) mode inside Phase B — delegated mode is load-bearing when semantic-merge runs at all (Tier 2/3); Phase B owns the post-merge drift tests and verify review
- Refactor APPROVED-integration tasks not named in `Tasks in scope:` — those are out of scope per `refactor-and-integrate` §Scope by Integration Status
- Strip domain-discipline artifacts during refactoring — see the `integration` / `merge` rows of the Skill-Load Manifest
- Judge the researcher's methodology — challenges to methodology escalate (RA framing, `using-superRA` §Universal Principles)
- Advance to Phase C before the verify reviewer APPROVES the unified diff
- Advance to Phase D without a freshness check on the base branch — if main advanced, re-enter Phase B
- Hand off Phase C Step 4 (PLAN.md disposition) to a subagent — it is a researcher-owned decision
- Inline Phase C's fact-check checklist or frontmatter spec — it lives in `superRA:report-in-markdown`'s `final-form.md` and `baseline-io.md`
- Cleanup the worktree before the merge or push has actually completed

**Always:**
- Confirm key-result coverage with the researcher before creating tests, logged per `superRA:handoff-doc` §User Decisions Log
- Run the recon reviewer first in every Phase B round — per-task annotations + Tier classification drive every downstream decision
- Evaluate the two shortcut axes (Tier + annotation count) before dispatching any follow-up agent; load `semantic-merge` on follow-ups only when Tier 2/3
- Batch user decisions at Phase B Step 2b — one stop, not N interruptions
- Use `superRA:semantic-merge` in delegated mode for the Phase B Commit 1 when Tier 2/3, and for any Phase D re-sync that is itself non-trivial
- Run drift tests between Commit 1 and Commit 2 when the implementer ran the two-commit structure, and again after Commit 2
- Run the Implementer Self-Check (`git diff <merge-base>..HEAD`) before every Phase B commit
- Re-submit to the verify reviewer after every Phase B implementer round
- Keep and re-validate drift tests through refactoring; author new tests only for tasks with `**Integration status:** ≠ APPROVED`, but run the full suite on every integration pass
- Dispatch the Phase C doc-writer with `superRA:report-in-markdown` (full mode); dispatch the doc-reviewer afterward; iterate to APPROVE
- Resolve `RESULTS_DIR` before dispatching the doc-writer — project guidance or `AskUserQuestion`, logged in PLAN.md `## Decisions`
- Commit at each phase boundary and after each Phase C sub-step (Step 2 sub-commits and Step 4 disposition each land separately)
- Re-enter Phase B if main advances between Phase B APPROVE and Phase D merge

**Drift-test integrity** is governed by the cross-cutting rules in `superRA:refactor-and-integrate` `references/drift-test-quality.md` — failing tests must be adjudicated, not silently re-expected; tolerance bumps require justification; test removal during refactoring is forbidden. **Merge quality** is governed by `references/merge-quality.md` — Tier 3 conflicts escalate; mechanical/intent commits stay separate. **Codebase integration + minimum net diff** is governed by `references/codebase-integration.md` and the body of `refactor-and-integrate` (Minimum-net-diff top item + Implementer Self-Check).

## Integration

**Called by:**
- **superRA:execution-workflow** Step 4 — when the user chooses Option 1 (merge) or Option 2 (PR) after reproducibility has been verified

**Invokes:**
- **superRA:semantic-merge** — REQUIRED for the main update in Phase B Commit 1 and any Phase D pre-merge re-sync (delegated mode)
- **superRA:refactor-and-integrate** — loaded by every dispatched implementer and reviewer in Phases A, B, and D; principles in body, `[BLOCKING]` / `[ADVISORY]` items in stage-scoped references
- **superRA:report-in-markdown** — loaded by the Phase C doc-writer (full mode) and doc-reviewer
- **superRA:handoff-doc** — loaded on demand for User Decisions Log format and PLAN.md anatomy

**Escalates to:**
- **superRA:planning-workflow §Changing Plans** — substantive restructure findings (task add/remove/combine, DAG edge flip, APPROVED status invalidation) surfaced in any phase; orchestrator authors the proposal, researcher decides

**Pairs with:**
- **superRA:agent-orchestration** — `references/worktree-harness-fallback.md` §Remove for worktree removal; §Handling Reviewer Feedback for REVISE adjudication; §Concurrent Writers for the Phase B split safety-valve
- **superRA:worktree-data-sync** — §Data Teardown clarifies that seeded non-git data disappears with the worktree directory

**Requires:**
- **RESULTS.md** (Stage 1 dev log) — source of key results for drift tests; matured into Stage 2 form at Phase C
- **Committed analysis code** — must be committed before drift tests are created
- **Reproducibility already verified** by execution-workflow Step 3

**Subagents use:**
- The active domain skill (for data analysis: `superRA:econ-data-analysis`) — domain discipline loaded at dispatch-time per `superRA:using-superRA` §Skill-Load Manifest
