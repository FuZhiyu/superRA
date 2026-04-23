---
name: integration-workflow
description: Requires `superRA:using-superra` loaded first. Use when a plan is code-complete and reproducibility-verified and the user has chosen to finish, PR, or land the work; when key results need drift tests before they touch the base branch; when the branch must be synced with the current base and then refactored for codebase fit; when RESULTS.md needs to mature into its permanent record; when PLAN.md needs final disposition; or when final PR/publish/cleanup still needs to happen. Triggers include "integrate", "prepare this for PR", "finish this analysis", "write drift tests for the key results", "sync with main and refactor", "consolidate RESULTS.md", "mature the results document", "update project docs for this analysis", "open the PR", or the transition from `implementation-workflow`'s completion menu.
---

# Integration Workflow

**First, load `superRA:using-superra` if not already loaded.** It carries the Skill-Load Manifest, handoff-doc pointer, code-change defaults, and commit hygiene this workflow assumes.

Workflow skill for the **INTEGRATE** phase of the superRA workflow. It takes a reproducibility-verified analysis branch through five steps:

```
Protect   -> create or refresh drift tests for key results
Sync      -> bring the branch onto the current base via semantic-merge
Integrate -> refactor, propagate sync obligations, and pass integration review
Document  -> mature RESULTS.md and dispose of PLAN.md
Finish    -> final freshness check, PR or fast-forward, and cleanup

Any step -> planning-workflow §User Feedback and Changing Plans
           when scope, methodology, task structure, or APPROVED status changes materially
```

**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

## Stop Points

Use `AskUserQuestion` (plain text if unavailable) only for legitimate stop points. Log every answer per `superRA:handoff-doc` §User Decisions Log before acting.

- **Protect:** key result / drift-test coverage confirmation.
- **Sync:** target base confirmation when no prior decision records it; research-meaningful conflicts surfaced by `semantic-merge`.
- **Integrate:** meaningful drift after sync or refactor; research-owned choices surfaced by the integration reviewer.
- **Document:** RESULTS.md permanent location when project guidance is silent; PLAN.md disposition.
- **Finish:** hard blockers only, such as target base advancing again after Integrate.

## Dispatch Convention

Load `superRA:agent-orchestration` before writing any dispatch prompt. Dispatch shape lives there; skill loads live in `superRA:using-superra` §Skill-Load Manifest.

Role boundaries:

- `Stage: drift-test` agents use `refactor-and-integrate` drift-test quality.
- `Stage: sync` agent uses `semantic-merge`, lands the semantic sync commit, and writes `## Sync Map` when needed.
- `Stage: integration` agents use `refactor-and-integrate` for post-sync quality and consume `## Sync Map`.
- `Stage: documentation` agents use `handoff-doc` and `report-in-markdown`.

## Protect

Drift tests guard key results during Sync, Integrate, Finish, and future work.

**Always run the full drift-test suite on every integration pass.** Authoring new drift tests is scoped to tasks with `**Integration status:**` unset or not `APPROVED` plus orchestrator-declared related tasks from `planning-workflow §User Feedback and Changing Plans`; running the suite is not scoped.

### Steps

1. **Extract key results from RESULTS.md.** Protect main findings, not every intermediate number.
2. **Confirm coverage with the researcher.** Stop point:
   ```text
   These results seem like the key findings to protect with drift tests:
   - [result 1: description and value]
   - [result 2: description and value]

   Which should be protected? Any to add or remove?
   ```
3. **Dispatch test-creator.** `Stage: drift-test`, canonical implementer template.
4. **Dispatch test-reviewer.** `Stage: drift-test`, canonical reviewer template. Iterate REVISE -> fix -> narrow re-review until APPROVE.
5. **Run tests on the current branch.** If new tests fail on existing code, fix the tests.
6. **Commit tests and handoff docs.**
7. **Flip `Drift tests created`** in PLAN.md §Workflow Status once all confirmed key results are protected and the full drift-test suite passes.

## Sync

Sync brings the analysis branch onto the current base before refactor starts. It is serialized: one sync agent, no parallelization.

### Step 1: Resolve the target base

Resolve a candidate base from prior `## Decisions` or git:

```bash
git merge-base HEAD origin/main 2>/dev/null \
  || git merge-base HEAD origin/master 2>/dev/null
```

If no prior decision records the base, ask:

```text
This integration will sync the analysis branch against <resolved-base>.
Is that correct, or did it split from a release branch, co-authored track,
or sibling analysis branch?
```

Log the confirmed base before fetching or dispatching.

### Step 2: Compute sync anchors

Fetch the confirmed base and record two anchors:

```bash
git fetch origin <base-branch>
PRE_SYNC_BASE_SHA=$(git merge-base HEAD origin/<base-branch>)
BASE_HEAD_SHA=$(git rev-parse origin/<base-branch>)
```

- `PRE_SYNC_BASE_SHA` is evidence for incoming intent: `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.
- `BASE_HEAD_SHA` is the post-sync governing baseline for Integrate: `BASE_HEAD_SHA..HEAD`.

### Step 3: Dispatch the sync agent when needed

If `git merge-base --is-ancestor "$BASE_HEAD_SHA" HEAD` succeeds, the branch is already synced. Record a no-op in the workflow notes if useful and proceed to Integrate.

Otherwise dispatch one implementer:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: sync
  Task: Sync this analysis branch with origin/<base-branch>
  Base branch: origin/<base-branch>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    use semantic-merge to land exactly one semantic sync commit.
    Write or update PLAN.md `## Sync Map` only when there is material
    overlap, a conflict, a user decision, or a post-sync obligation.
    Do not perform codebase refactor, generated-output refresh, drift-test
    expectation updates, or project-doc audit. Return the sync commit SHA,
    Sync Map status, checks run, and post-sync obligations.
```

If the sync agent returns `NEEDS_USER_DECISION`, the orchestrator asks the researcher, logs the decision, commits the log entry, and re-dispatches the sync agent with the decision context.

## Integrate

Integrate is the post-sync quality gate. It consumes `## Sync Map`, performs semantic propagation into non-conflicted files, fits the code to the host project, audits project docs, and verifies the surviving diff against the current base.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base for minimum-net-diff review after Sync.

### Step 1: Run the full drift-test suite

Run the full suite after Sync and before refactor. Failing drift tests block Integrate until classified per `refactor-and-integrate/references/drift-test-quality.md`.

### Step 2: Dispatch the integration reviewer

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Post-sync integration review
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Sync Map: PLAN.md ## Sync Map, if present

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    consume the Sync Map and review `git diff <BASE_HEAD_SHA>..HEAD`.
    For every touched or Sync-Map-affected task, either set
    `Integration status: APPROVED` or write task-local review notes and
    set `Integration status: REVISE`. Findings should cover minimum
    surviving branch delta, Sync Map obligations, semantic propagation,
    codebase fit, project-doc audit, drift-test implications, and handoff-doc
    coherence. Do not recreate the incoming-intent research owned by Sync.
```

### Step 3: Orchestrator adjudication

Read the task-local integration notes. Classify reviewer findings per `superRA:agent-orchestration` §Handling Reviewer Feedback.

- Batch all research-owned questions into one stop point.
- Route substantive plan restructures through `planning-workflow §User Feedback and Changing Plans`.
- Log user decisions before dispatching fixes.

### Step 4: Refactor loop

Dispatch implementer(s) for accepted `Integration status: REVISE` items:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: Fix integration review items for <task list>
  Tasks in scope: <tasks with Integration status: REVISE>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    consume PLAN.md `## Sync Map` if present, address accepted review
    findings, and run the minimum-net-diff self-check against
    `git diff <BASE_HEAD_SHA>..HEAD` before each commit. Do not touch
    tasks outside `Tasks in scope` except where required by a Sync Map
    obligation or accepted reviewer finding.
```

Re-dispatch the reviewer for narrow re-review plus the branch-wide pruning sweep over `BASE_HEAD_SHA..HEAD`. Iterate until all in-scope tasks are `Integration status: APPROVED` and every surviving hunk is justified by approved objectives, Sync Map obligations, logged user decisions, or project convention fit.

### Step 5: Close Integrate

Run the full drift-test suite again. When it passes and integration review is APPROVED:

- remove temporary `## Sync Map` from PLAN.md, if present
- flip `Integrated` in PLAN.md §Workflow Status
- commit the closeout doc edit

## Document

Document matures RESULTS.md from live dev log to permanent record and resolves PLAN.md disposition.

### Step 1: Resolve RESULTS_DIR

The matured RESULTS.md lands in the analysis's permanent code folder per project guidance. Read CLAUDE.md, AGENTS.md, and README.md. If guidance is silent, ask:

```text
RESULTS.md needs a permanent location in this project. The matured file
will be co-located with the analysis code so it travels with it.
Where should it land?

Suggested: <best guess from the analysis code's location>
```

Log the answer before dispatching the doc-writer.

### Step 2: Dispatch doc-writer

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: documentation
  Task: Mature RESULTS.md into permanent record
  RESULTS_DIR: <resolved permanent folder>
  RESULTS_ATTACHMENTS_DIR: ${RESULTS_DIR}/attachments

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    mature RESULTS.md per `report-in-markdown/references/final-form.md`:
    fact-check, restructure, materialize figures, and relocate. Land
    recoverable commits and report which sub-commits landed.
```

### Step 3: Dispatch doc-reviewer

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: documentation
  Task: Review matured RESULTS.md
  Git range: <BASE_SHA>..<HEAD_SHA>
  RESULTS_DIR: <resolved permanent folder>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <prior-round adjudication notes if re-dispatching>.
```

Iterate REVISE -> fix -> narrow re-review until APPROVE. If a documentation finding traces to analysis code, re-enter Integrate.

On APPROVE, flip `Docs finalized` in PLAN.md §Workflow Status and commit before PLAN.md disposition.

### Step 4: PLAN.md disposition

Ask the researcher:

```text
PLAN.md is still at the worktree root and needs disposition. RESULTS.md
has already been matured and committed at ${RESULTS_DIR}, and project
docs are up to date. Options:

1. Move PLAN.md (and results_attachments/) alongside the matured
   RESULTS.md at ${RESULTS_DIR}.
2. Consolidate any plan context into existing project documentation,
   then delete PLAN.md and results_attachments/.
3. Delete PLAN.md and results_attachments/; git history preserves them
   on this branch.

Which option?
```

Log the answer before moving or removing files. Include the log in the same commit as the disposition.

## Finish

Finish executes the user's completion choice from `implementation-workflow`.

### Step 1: Freshness check

Fetch the target base and check whether it advanced since Integrate:

```bash
git fetch origin <base-branch>
git rev-parse origin/<base-branch>
```

If `origin/<base-branch>` differs from the recorded `BASE_HEAD_SHA`, re-enter Sync before publishing or landing the work.

### Step 2: Mark final action in PLAN.md if present

If PLAN.md still exists after disposition, flip the final workflow checkbox in the same commit that performs the final action. Skip if PLAN.md was consolidated or removed.

### Step 3: Publish or land

For a PR:

```bash
git push -u origin <analysis-branch>
gh pr create --title "<title>" --body "<summary, data, reproducibility, quality gates>"
```

For a local fast-forward into the base:

```bash
git checkout <base-branch>
git pull
git merge --ff-only <analysis-branch>
```

Run the project pipeline or targeted verification on the final tree. If it fails, investigate before cleanup.

### Step 4: Cleanup

If the analysis used a worktree, remove it per `superRA:agent-orchestration/references/worktree-harness-fallback.md`. Seeded non-git data disappears with the worktree; see `superRA:worktree-data-sync` for data teardown.

Report what was published or landed and what was cleaned up.

## When to Lighten

- **Standalone analysis:** Protect still runs. Sync may be a no-op. Integrate often collapses to a short reviewer pass.
- **Small changes:** Keep the same five steps, but dispatch fewer agents and keep Sync Map absent when there are no obligations.

## Red Flags

**Never:**
- Refactor before Sync when the base has advanced.
- Use `PRE_SYNC_BASE_SHA` as the post-sync minimum-net-diff baseline.
- Skip the integration reviewer after Sync.
- Leave `## Sync Map` in PLAN.md after Integrate closes.
- Enter Finish without checking whether the base advanced again.

**Always:**
- Run the full drift-test suite on every integration pass.
- Use semantic-merge for research-aware branch syncs.
- Keep Sync serialized and refactor parallelizable only after Sync lands.
- Log user decisions before acting.
