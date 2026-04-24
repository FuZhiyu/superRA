---
name: integration-workflow
description: Requires `superRA:using-superra` loaded first. Use when a plan is code-complete and reproducibility-verified and the user has chosen to merge back or open a PR; when you need drift tests to guard key results before they touch main; when the branch needs to be brought up to date with main and refactored to fit codebase conventions (review-led iterative sync + refactor targeting minimum-net-diff); when the working RESULTS.md still needs to be matured into its permanent, fact-checked, co-located form (Phase C); when PLAN.md needs final disposition; when the actual local merge or PR push + worktree cleanup still needs to happen. Triggers include "integrate", "prepare this for merge", "write drift tests for the key results", "sync with main and refactor", "consolidate RESULTS.md", "mature the results document", "update project docs for this analysis", "get this ready to PR", "merge this back", "open the PR", "finish this analysis", or the transition from `implementation-workflow`'s completion menu.
---

# Integration Workflow

**First, load `superRA:using-superra` if not already loaded.**

Workflow skill for the **INTEGRATE** phase of the superRA workflow. Owns the full finishing sequence that takes a reproducibility-verified analysis branch to a merged state on main: drift-test creation (Phase A), unified sync-with-main + refactor (Phase B, iterative), documentation maturation + PLAN.md disposition (Phase C), and final local merge or PR push + cleanup (Phase D).


**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

## Phase Map

```
Phase A — Drift Test Creation
   ↓
Phase B — Integrate (sync + refactor, iterative)
   ↓
Phase C — Docs
   ↓
Phase D — Final merge / PR / cleanup
```

The main agent's Workflow Frontier Resolver chooses where to enter this map. Once this skill is entered, run the selected phase's local gates exactly; do not redo task-local approvals outside the affected frontier simply because a rollup milestone was unchecked.

**Autonomy** — full contract: `superRA:using-superra/references/main-agent.md`. Legitimate stop points in this workflow:

- Phase A Step 2 — drift-test candidate confirmation
- Phase B Step 0 — integration-base confirmation (skippable when a prior §Decisions entry already records it)
- Phase B Step 2 — batched research-meaningful decisions surfaced by the integration reviewer
- Phase B / Phase D — meaningful drift after refactor or post-merge (see `superRA:refactor-and-integrate` `references/drift-test-quality.md`)
- Phase C Step 1 — Phase C RESULTS.md relocation target when project guidance is silent
- Phase C Step 4 — PLAN.md disposition

Every stop: log the answer per `superRA:handoff-doc` §User Decisions Log **before** acting.

## Dispatch Convention

**Load `superRA:agent-orchestration` before writing any dispatch prompt.** Checklist discipline for this phase comes from `superRA:refactor-and-integrate`.

## Phase A — Drift Test Creation

Drift tests guard key results from unintended changes during Phase B refactoring, Phase D semantic-merges, and any future modification. They are the safety net that makes everything downstream safe.

**Always run the full drift-test suite on every integration pass**, regardless of re-entry scope. Authoring new drift tests is scoped to tasks with `**Integration status:** ≠ APPROVED` (plus orchestrator-declared related tasks per `planning-workflow §User Feedback and Changing Plans`); running the suite is not.

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

**Integration base.** Phase B integrates the analysis branch against a researcher-specified base — `<base-branch>` in every reference below. `origin/main` is the typical default; override is expected when the analysis branched off a release, a co-authored track, or another analysis's sibling branch.

The base branch is authoritative by default. Phase B freezes one merge-base snapshot for the active round, passes that round context to the integration reviewer, and records `## Upstream Intent` in `PLAN.md` only when the reviewer needs a branch-wide upstream contract for material overlap. Every surviving branch delta must justify against approved task objectives plus that recorded contract when present. The integration reviewer drives the loop: it walks both the branch diff and the base-branch-side changes, writes branch-wide upstream-intent context when needed, and writes task-local annotations so implementers do not have to reconstruct upstream intent from git history. The orchestrator adjudicates findings, batches user decisions, then dispatches implementer(s) to fix, and re-dispatches the reviewer. Repeat until every in-scope task is APPROVED and the reviewer confirms the surviving diff is justified.

### Step 0: Resolve and confirm the integration base

Resolve a candidate base from git and any prior §Decisions entry:
```bash
git merge-base HEAD origin/main 2>/dev/null \
  || git merge-base HEAD origin/master 2>/dev/null
```

Legitimate stop point — ask via `AskUserQuestion` (plain text if unavailable):

```
Phase B will integrate this analysis branch against <resolved-base>.
Is that correct, or did this branch split from a different base
(release branch, co-authored track, sibling analysis)?
```

If a prior `## Decisions` entry on this branch already records the integration base and it matches the git-resolved candidate, skip the prompt — the researcher has already answered. Otherwise log the confirmed answer per `superRA:handoff-doc` §User Decisions Log as `<base-branch>` **before** fetching or dispatching. Fetch fresh so base-branch-side scans walk current upstream state:
```bash
git fetch origin <base-branch>
MERGE_BASE_SHA=$(git merge-base HEAD origin/<base-branch>)
```

Use this `MERGE_BASE_SHA` as the frozen anchor for the active Phase B round. Do not pre-edit `PLAN.md` in Step 0. Instead pass the reviewer the round context it needs:

```text
Base branch: origin/<base-branch>
Frozen merge base SHA: <MERGE_BASE_SHA>
Reviewed upstream range: <MERGE_BASE_SHA>..origin/<base-branch>
```

### Step 1: Dispatch the integration reviewer

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Phase B integration review
  Git range: <MERGE_BASE_SHA>..HEAD
  References: `superRA:handoff-doc` `references/plan-anatomy.md` §Upstream Intent

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    walk (a) <MERGE_BASE_SHA>..HEAD for integration fit per
    `refactor-and-integrate`; (b) <MERGE_BASE_SHA>..origin/<base-branch>
    for material incoming changes on the integration base. Use this round
    context while doing (b): base branch `origin/<base-branch>`, frozen
    merge base `<MERGE_BASE_SHA>`, reviewed upstream range
    `<MERGE_BASE_SHA>..origin/<base-branch>`. Treat the base branch as
    canonical by default. Use the cited handoff reference for the section's
    format and placement. If (b) surfaces material overlap, create or
    update `## Upstream Intent` in PLAN.md for the active round using that
    context, and for each affected task append a task-local integration review-notes
    item that names the upstream file / commit / change being honored,
    the upstream intent in plain language, the minimal allowed branch
    delta, and any stale branch-side content that must not survive.
    If (b) finds no material overlap, leave `## Upstream Intent` absent
    for this round.
    For every in-scope task needing codebase-fit refactor, drift-test
    update, handoff-doc coherence fix, or merge-induced semantic
    adaptation, append a per-task integration review-notes blockquote
    with [BLOCKING] / [ADVISORY] items. Tasks needing no changes get
    no annotation; flip each annotated task to
    `Integration status: REVISE` in the same review commit. When
    the diff to walk is large (see `agent-orchestration`
    §Workload Balancing)
    <prior-round adjudication notes if re-dispatching>.
```

### Step 2: Orchestrator — adjudicate and batch user decisions

Read PLAN.md (`## Upstream Intent` when present + per-task annotations). Two branching points:

- **Zero annotated tasks** — no refactor needed. If the base-branch-side scan also found nothing material, Phase B terminates: execute `git merge --ff-only <base-branch>` (or skip if `git merge-base --is-ancestor origin/<base-branch> HEAD`), note in §Decisions, proceed to Phase C.
- **Annotated tasks exist** — collect every research-meaningful item from the per-task blockquotes. Batch into a single `AskUserQuestion` (plain text if unavailable) — one stop point, not N interruptions. If findings imply a substantive restructure (task add/remove/combine, DAG flip), escalate to `planning-workflow §User Feedback and Changing Plans` instead. Otherwise log each answer per `superRA:handoff-doc` §User Decisions Log; commit the PLAN.md edit **before** dispatching implementer(s).

### Step 3: Fix-review loop

**3a — Mechanical merge first (when the base branch has diverged).** Before any refactor, land the merge commit on its own. Orchestrator executes directly or dispatches one implementer — no parallelization for this commit. Use `superRA:semantic-merge` when there are conflicts or material base-branch-side changes that need intent-based resolution; `git merge --ff-only` when `<base-branch>` is an ancestor. Run drift tests on the merged tree; meaningful drift is a legitimate stop point per `superRA:refactor-and-integrate` `references/drift-test-quality.md`. If merge is a no-op (branch already ahead of `<base-branch>`), skip.

**3b — Refactor commits (one per logical change, scoped to REVISE tasks).** Dispatch implementer(s) to address accepted findings using the canonical implementer template in `agent-orchestration §Dispatch Templates`. Integration-stage additions to the template:

- `Stage: integration`.
- `Tasks in scope: <list of tasks with Integration status: REVISE>` — the implementer refuses to refactor any task not in this list; flips each in-scope task to `Integration status: IMPLEMENTED` on commit.
- Mechanical merge (3a) must land before any refactor commit.
- Drift tests are re-run after any refactor that could affect them.

Commit granularity is the implementer's judgment; minimum-net-diff self-check before every commit. When the REVISE task list is large enough to exceed the ~150k context threshold (`agent-orchestration` §Workload Balancing), split into sibling implementers on parallel worktrees per `agent-orchestration §Parallelization and Worktree Isolation` — each owns a disjoint task slice.

**3c — Re-dispatch integration reviewer.** Do one reviewer pass over the cumulative diff. Verify the cited fixes and dependent findings on in-scope tasks, then sweep `git diff <MERGE_BASE_SHA>..HEAD` for unjustified surviving hunks. Treat that branch-wide pass as pruning, not a fresh checklist walk: previously `APPROVED` tasks stay out of scope unless the sweep finds a new unjustified hunk and annotates them back into scope. On APPROVE: the reviewer has flipped in-scope tasks to `Integration status: APPROVED`, removed the in-scope per-task review-notes blockquotes, and confirmed that every surviving hunk in `git diff <MERGE_BASE_SHA>..HEAD` is justified by approved task objectives plus the recorded upstream contract. On REVISE: adjudicate per `superRA:agent-orchestration` §Handling Reviewer Feedback; iterate from 3b.

### Step 4: Flip `Refactored` milestone
When every in-scope task is `Integration status: APPROVED` and the reviewer has confirmed the surviving diff is justified against approved task objectives plus the recorded upstream contract, the orchestrator flips the `Refactored` box in PLAN.md §Workflow Status and, if `## Upstream Intent` is present, deletes it in the same closeout commit before proceeding to Phase C.

## Phase C — Documentation Finalization + PLAN.md Disposition

Gates `RESULTS.md` maturation (dev log → permanent record) behind a doc-writer + doc-reviewer pair; orchestrator handles user-facing decisions (relocation target, PLAN.md disposition). Format discipline lives in `superRA:report-in-markdown`.

### Step 1: Resolve `RESULTS_DIR` (orchestrator preamble)

The matured `RESULTS.md` lands in the analysis's permanent code folder, **per project guidance**. Read `CLAUDE.md`, `AGENTS.md`, or the project README for the convention. If none exists, legitimate stop point — ask via `AskUserQuestion` (plain text if unavailable):

```
Phase C RESULTS.md needs a permanent location in this project. The matured
file will be co-located with the analysis code so it travels with it.
Where should it land?

Suggested: <best guess from the analysis code's location, e.g. analyses/<name>/>
```

Log per `superRA:handoff-doc` §User Decisions Log **before** dispatching the doc-writer. Define `RESULTS_DIR` = resolved folder; `RESULTS_ATTACHMENTS_DIR = ${RESULTS_DIR}/attachments`. Pass both as dispatch parameters.

### Step 2: Dispatch the doc-writer

```
Agent(subagent_type: "superRA:implementer"):
  Stage: documentation
  Task: Task N in PLAN.md — Phase C RESULTS.md maturation
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

When the frontier reaches Phase C, the doc-writer re-runs the whole matured doc; the doc-reviewer reviews the diff from the last APPROVED state plus any section a newly-reworked task touches. Per-commit validation and recovery rules live in `superRA:report-in-markdown` `final-form.md`.

### Step 3: Dispatch the doc-reviewer

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: documentation
  Task: Task N in PLAN.md — review of matured Phase C RESULTS.md
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

By this point `RESULTS.md` has graduated to `${RESULTS_DIR}` and project docs are in sync (audited during Phase B per `superRA:refactor-and-integrate` `references/codebase-integration.md` §Project Doc Audit). `PLAN.md` and the working `results_attachments/` folder are the last in-progress scaffolds at the worktree root.


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

After Phase C completes, execute the user's choice from implementation-workflow Step 4. The final freshness check below may route back to Phase B before merge or push.

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
- Integration review: passed pre-merge (Phase B integration reviewer APPROVE)

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

## Agent Loads

This workflow runs the `drift-test`, `integration`, and `documentation` Stages (see `superRA:using-superra` §Skill-Load Manifest).

## Red Flags

**Never:**
- Skip the integration reviewer and dispatch the implementer blind — per-task annotations, branch-wide upstream-intent clusters, and the user-decision batch all come from the reviewer
- Advance to Phase D without a freshness check on the integration base — if the base branch advanced, re-enter Phase B
- Hand off Phase C Step 4 (PLAN.md disposition) to a subagent — it is a researcher-owned decision
- Clean up the worktree before the merge or push has actually completed

**Always:**
- Author new drift tests only for tasks with `**Integration status:** ≠ APPROVED`, but run the **full** drift-test suite on every integration pass (scope is for authoring; running is not scoped)
