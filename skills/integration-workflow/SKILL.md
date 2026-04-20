---
name: integration-workflow
description: Use when a plan is code-complete and reproducibility-verified and the user has chosen to merge or open a PR. Covers drift-test creation, review-led sync + refactor against main, RESULTS.md maturation + PLAN.md disposition, and final local merge or PR push + cleanup. Triggers include "integrate", "prepare this for merge", "sync with main", "mature the results document", or the transition from `execution-workflow`'s completion menu.
---

# Integration Workflow

Workflow skill for the **INTEGRATE** phase of the superRA workflow. Owns the full finishing sequence that takes a reproducibility-verified analysis branch to a merged state on main: drift-test creation (Phase A), unified sync-with-main + refactor (Phase B, iterative), documentation maturation + PLAN.md disposition (Phase C), and final local merge or PR push + cleanup (Phase D).

Assumes execution-workflow has already verified reproducibility and the user has chosen Option 1 (merge locally) or Option 2 (push + PR). If you find yourself running reproducibility checks or presenting the 4-option menu, something is wrong: that work belongs in execution-workflow.

**Core principle.** Tests guard results. Minimum net diff relative to integration base. Nothing advances without reviewer APPROVE at every gate (drift-test review, integration review, doc review). Non-trivial merges with main use `superRA:semantic-merge`; the integration reviewer decides whether one is needed.

**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

## Phase Map

```
Phase A — Drift Test Creation
   ↓
Phase B — Integrate (sync + refactor, iterative)
   ↓               ↑  (re-enter B when main moves again, or when
Phase C — Docs  ───┘   integration reviewer triggers a new round)
   ↓               ↑
Phase D — Final merge / PR / cleanup
                   ↑
         Anywhere ─┴─→  `planning-workflow §User Feedback and Changing Plans`
                        (substantive restructure: task add/remove/combine,
                         DAG flip, APPROVED invalidation; orchestrator
                         proposes, researcher decides)
```

**Autonomy.** Between stop points, run on your own power — do not check in after each phase, do not re-confirm a reviewer's APPROVE. Legitimate stop points:

- Phase A Step 2 — drift-test candidate confirmation
- Phase B — batched research-meaningful decisions surfaced by the integration reviewer (see Phase B Step 2)
- Phase B / Phase D — meaningful drift after refactor or post-merge (see `superRA:refactor-and-integrate` `references/drift-test-quality.md`)
- Phase C Step 1 — Phase C RESULTS.md relocation target when project guidance is silent
- Phase C Step 4 — PLAN.md disposition

See `superRA:using-superRA` §Universal Principles (#4) for the full autonomy contract, and `superRA:handoff-doc` §User Decisions Log for how every answer must land in PLAN.md before the workflow acts on it.

## Dispatch Convention

Every dispatch in this skill uses the canonical template in `superRA:agent-orchestration` §Dispatch Templates — required fields first, `Additionally:` anchor last (strictly additive steering only). The Skill-Load Manifest in `superRA:using-superRA` is the single source of truth for what each `Stage:` loads — dispatches do not restate skill/reference loads, do not paraphrase PLAN.md, and do not repeat checklist items the agent already reads. REVISE adjudication follows `superRA:agent-orchestration` §Handling Reviewer Feedback.

The checklist discipline for every implementer self-check and every reviewer walk in this workflow lives in `superRA:refactor-and-integrate` (principles in body; `[BLOCKING]` / `[ADVISORY]` items in the stage-scoped references).

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

**Integration base.** Phase B integrates the analysis branch against a researcher-specified base — `<base-branch>` in every reference below. `origin/main` is the typical default, but confirm with the researcher; override is expected when the analysis branched off a release, a co-authored track, or another analysis's sibling branch. The ref is fetched fresh (`git fetch origin <base-branch>`) at the start of Phase B so base-branch-side scans walk current upstream state.

The integration reviewer drives the loop. It walks both the branch diff and the base-branch-side changes, writes per-task annotations in PLAN.md, and writes or updates a `## Integration Intent` section when material incoming changes need adaptation (see `superRA:handoff-doc` `references/plan-anatomy.md` §Integration Intent for the section's anatomy and ownership rules). The orchestrator adjudicates findings, batches user decisions, then dispatches implementer(s) to fix, and re-dispatches the reviewer. Repeat until every in-scope task is APPROVED.

### Step 1: Dispatch the integration reviewer

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Phase B integration review
  Git range: <merge-base>..HEAD

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    walk (a) <merge-base>..HEAD for integration fit per
    `refactor-and-integrate`; (b) <merge-base>..origin/<base-branch>
    for material incoming changes on the integration base. For (b):
    if incoming changes could affect this branch's code or docs,
    write or update a `## Integration Intent` section in PLAN.md
    per `plan-anatomy.md` and annotate affected tasks. For every
    in-scope task needing codebase-fit refactor, drift-test update,
    handoff-doc coherence fix, or merge-induced semantic adaptation,
    append a per-task integration review-notes blockquote with
    [BLOCKING] / [ADVISORY] items. Tasks needing no changes get
    no annotation; flip each annotated task to
    `Integration status: REVISE` in the same review commit. When
    the diff to walk is large (see `agent-orchestration`
    §Workload Balancing), the orchestrator may dispatch parallel
    sibling reviewers on disjoint worktrees per
    §Parallelization and Worktree Isolation — each walks a
    disjoint slice.
    <prior-round adjudication notes if re-dispatching>.
```

### Step 2: Orchestrator — adjudicate and batch user decisions

Read PLAN.md (Integration Intent section + per-task annotations). Two branching points:

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

**3c — Re-dispatch integration reviewer.** Walk the cumulative diff; refuse to walk APPROVED-integration tasks not in scope. On APPROVE: the reviewer has flipped in-scope tasks to `Integration status: APPROVED`, removed its per-task review-notes blockquotes, and updated the Integration Intent section (removing resolved items; removing the section when empty). On REVISE: adjudicate per `superRA:agent-orchestration` §Handling Reviewer Feedback; iterate from 3b.

### Step 4: Flip `Refactored` milestone

When every in-scope task is `Integration status: APPROVED` and the Integration Intent section is empty or absent, the orchestrator flips the `Refactored` box in PLAN.md §Workflow Status and proceeds to Phase C. If Phase C or D later triggers a new sync+refactor round, uncheck `Refactored` on re-entry and re-check on the next reviewer APPROVE.

## Phase C — Documentation Finalization + PLAN.md Disposition

After Phase B APPROVES the unified diff, `RESULTS.md` still needs to mature from dev log to permanent record and `PLAN.md` still needs disposition. This phase gates the RESULTS.md maturation behind a **single implementer–reviewer pair** (doc-writer + doc-reviewer); the orchestrator handles the user-facing decisions (relocation target, PLAN.md disposition) on either side of the pair.

Format discipline for sub-part A (maturation) lives entirely in `superRA:report-in-markdown`. This phase orchestrates — it does not duplicate the rules.

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

The doc-writer always re-runs the whole matured doc on every integration pass; the doc-reviewer reviews the diff from the last APPROVED state plus any section a newly-reworked task touches. Per-commit validation and recovery rules live in `superRA:report-in-markdown` `final-form.md`.

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

## When to Lighten

**Standalone analysis (no existing codebase to integrate with):**
- Phase A: Always run.
- Phase B: Integration reviewer typically leaves zero annotations and finds no material main-side changes; Phase B then collapses to a single fast-forward merge (or is a no-op on a true greenfield branch).

**Small changes (single-file analysis, few results):**
- Phase A: Still run, fewer tests.
- Phase B: Integration reviewer may APPROVE immediately with no annotations.

## Agent Loads

See `superRA:using-superRA` §Skill-Load Manifest — the single source of truth for what every dispatched implementer / reviewer loads per Stage. This workflow runs the `drift-test`, `integration`, and `documentation` rows. The Phase B implementer runs `Stage: integration`; `superRA:semantic-merge` is loaded when the mechanical merge needs intent-based resolution (the integration reviewer's annotation drives that call, not a Tier gate).

Phase C Step 2 (mature RESULTS.md) is performed by the dispatched doc-writer subagent — an implementer-reviewer pair gates RESULTS.md maturation per workflow principle P1. Step 4 (PLAN.md disposition) and Phase D Step 2 (milestone flip) stay with the orchestrator because they are user-facing decisions, not RA-implementable tasks. Project-level doc audit is covered by the Phase B integration reviewer per `codebase-integration.md` §Project Doc Audit — not by Phase C.

## Red Flags

Each bullet below catches a rationalization the RA is plausibly going to make *in this phase*. Sequencing reminders and cross-skill principles (integration discipline, merge quality, drift-test integrity, RA framing) live where they are owned and are not restated here. See the cross-cutting references at the end of this section.

**Never:**
- Skip the integration reviewer and dispatch the implementer blind — per-task annotations, Integration Intent updates, and the user-decision batch all come from the reviewer
- Advance to Phase D without a freshness check on the integration base — if the base branch advanced, re-enter Phase B
- Hand off Phase C Step 4 (PLAN.md disposition) to a subagent — it is a researcher-owned decision
- Clean up the worktree before the merge or push has actually completed

**Always:**
- Author new drift tests only for tasks with `**Integration status:** ≠ APPROVED`, but run the **full** drift-test suite on every integration pass (scope is for authoring; running is not scoped)

**Drift-test integrity** is governed by the cross-cutting rules in `superRA:refactor-and-integrate` `references/drift-test-quality.md`. **Merge quality** is governed by `references/merge-quality.md`. **Codebase integration + minimum net diff** is governed by `references/codebase-integration.md` and the body of `refactor-and-integrate` (Minimum-net-diff top item + Implementer Self-Check). **RA framing** (no unilateral methodology judgments; escalate via `AskUserQuestion`) is governed by `superRA:using-superRA` §Universal Principles.
