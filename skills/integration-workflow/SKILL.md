---
name: integration-workflow
description: Requires `superRA:using-superra` loaded first. Use when a plan is code-complete and reproducibility-verified and the user has chosen to finish, PR, or land the work; when key results need drift tests before they touch the base branch; when the branch must be synced with the current base and then refactored for codebase fit; when RESULTS.md needs to mature into its permanent record; when PLAN.md needs final disposition; or when final PR/publish/cleanup still needs to happen. Triggers include "integrate", "prepare this for PR", "finish this analysis", "write drift tests for the key results", "sync with main and refactor", "consolidate RESULTS.md", "mature the results document", "update project docs for this analysis", "open the PR", or the transition from `implementation-workflow`'s completion menu.
---

# Integration Workflow

**First, load `superRA:using-superra` if not already loaded.**

Workflow skill for the **INTEGRATE** phase of the superRA workflow. It takes a reproducibility-verified analysis branch through five steps:

```
Protect   -> create or refresh drift tests for key results
Sync      -> bring the branch onto the current base via semantic-merge
Integrate -> refactor with Sync context and pass integration review
Document  -> mature RESULTS.md and dispose of PLAN.md
Finish    -> final freshness check, PR or fast-forward, and cleanup

Any step -> planning-workflow §User Feedback and Changing Plans
           when scope, methodology, task structure, or APPROVED status changes materially
```

**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

## Stop Points

The main agent's Workflow Frontier Resolver chooses where to enter this workflow. Once entered, run the selected step's local gates exactly; do not redo task-local approvals outside the affected frontier simply because a rollup milestone was unchecked.

Legitimate stop points (log every answer per `superRA:handoff-doc` §User Decisions Log **before** acting):

- **Protect:** key result / drift-test coverage confirmation.
- **Sync:** target base confirmation when no prior decision records it; intent-changing conflicts surfaced by `semantic-merge`.
- **Integrate:** meaningful drift after sync or refactor; user-owned choices surfaced by the integration reviewer.
- **Document:** RESULTS.md permanent location when project guidance is silent; PLAN.md disposition.
- **Finish:** hard blockers only, such as target base advancing again after Integrate.

## Dispatch Convention

**Load `superRA:agent-orchestration` before writing any dispatch prompt.** Checklist discipline for the drift-test and integration stages comes from `superRA:refactor-and-integrate`.

- `Stage: drift-test` agents use `refactor-and-integrate` drift-test quality.
- Sync uses generic sync author / sync reviewer agents that explicitly load `semantic-merge` mode references. Sync is branch-level and is not a normal task-scoped manifest stage.
- `Stage: integration` agents use `refactor-and-integrate` for post-sync quality and read task-local `**Sync impact:**` plus referenced `## Sync Map` clusters as context.
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

Sync brings the analysis branch onto the current base before refactor starts. It is serialized: one generic sync author followed by one generic sync reviewer, no parallelization.

### Step 1: Resolve the target base

Resolve and record a candidate base ref from prior `## Decisions` or git. This is a branch/ref name, not a merge-base SHA:

```bash
if git rev-parse --verify --quiet origin/main >/dev/null; then
  BASE_REF=origin/main
elif git rev-parse --verify --quiet origin/master >/dev/null; then
  BASE_REF=origin/master
else
  BASE_REF=
fi
```

If no prior decision records the base, ask:

```text
This integration will sync the analysis branch against <base-ref>.
Is that correct, or did it split from a release branch, co-authored track,
or sibling analysis branch?
```

Log the confirmed `BASE_REF` before fetching, computing anchors, or dispatching.

### Step 2: Compute sync anchors

Fetch the confirmed base when it is a remote-tracking ref and record two anchors from that same ref:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
PRE_SYNC_BASE_SHA=$(git merge-base HEAD "$BASE_REF")
BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

- `PRE_SYNC_BASE_SHA` is evidence for incoming intent: `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.
- `BASE_HEAD_SHA` is the post-sync governing baseline for Integrate: `BASE_HEAD_SHA..HEAD`.

### Step 3: Dispatch the sync author when needed

If `git merge-base --is-ancestor "$BASE_HEAD_SHA" HEAD` succeeds, the branch is already synced. Record a no-op in the workflow notes if useful and proceed to Integrate.

Otherwise dispatch one generic sync author:

```text
Agent(generic):
  Role: sync author
  Skills: semantic-merge
  References:
    - semantic-merge/references/workflow-sync-author.md

  Task: Sync this analysis branch with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>

  Use semantic-merge workflow sync author mode. Land the merge commit plus
  any propagation commits needed to reach semantic coherence — `SKILL.md
  §Semantic Coherence Checklist §Scope boundary` is the stopping rule. Write branch-level PLAN.md `## Sync
  Map` only when there is material overlap, a conflict, a user decision,
  sync-review carryover, or post-sync context. Add compact task-local
  `**Sync impact:**` annotations to affected task blocks. Defer codebase
  coherence — convention fit, utility reuse, PR-friendly diffs, Project Doc
  Audit walk-up, minimum net diff — to `refactor-and-integrate` via Integrate.
  Return the full sync commit chain, Sync Map status, task-local Sync impact
  annotations, checks run, and codebase-review context recorded.
```

If the sync author returns `NEEDS_CONTEXT` or `BLOCKED` because a user decision is required, the orchestrator asks the user, logs the decision, commits the log entry, and re-dispatches the sync author with the decision context.

### Step 4: Dispatch the sync reviewer

Before Integrate begins, dispatch one generic sync reviewer:

```text
Agent(generic):
  Role: sync reviewer
  Skills: semantic-merge
  References:
    - semantic-merge/references/workflow-sync-reviewer.md

  Task: Review the semantic sync with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>
  Sync commits: <MERGE_COMMIT_SHA>[, <PROPAGATION_OR_DOC_SHAS>...]

  Use semantic-merge workflow sync reviewer mode. Verify anchors, incoming
  intent, current-branch intent, conflict resolution, user-decision logging,
  Sync Map completeness, task-local Sync impact coverage, and scope boundary.
  Record sync-review status and notes in PLAN.md `## Sync Map` when a map
  exists or when review finds a material issue. Return APPROVE or REVISE.
```

On REVISE, adjudicate sync-review findings per `superRA:agent-orchestration` §Handling Reviewer Feedback, re-dispatch the sync author for accepted items, then re-dispatch the sync reviewer. Integrate starts only after sync review APPROVES.

## Integrate

Integrate is the post-sync quality gate. It uses task-local `**Sync impact:**` annotations and referenced `## Sync Map` clusters as context for the approved post-sync diff, fits the code to the host project, audits project docs, and verifies the surviving diff against the current base.

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
  Sync context: task-local `**Sync impact:**` fields plus PLAN.md ## Sync Map, if present

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    read task-local Sync impact annotations and referenced Sync Map clusters as context,
    then review `git diff <BASE_HEAD_SHA>..HEAD`.
    For every touched or Sync-impact-affected task, either set
    `Integration status: APPROVED` or write task-local review notes and
    set `Integration status: REVISE`. Findings should cover minimum
    surviving branch delta, codebase fit, project-doc audit, drift-test
    implications, and handoff-doc coherence. Do not recreate incoming-intent
    research or re-review semantic coherence already approved by sync review.
```

### Step 3: Orchestrator adjudication

Read the task-local integration notes. Classify reviewer findings per `superRA:agent-orchestration` §Handling Reviewer Feedback.

- Batch all user-owned questions into one stop point.
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
    read task-local `**Sync impact:**` and referenced Sync Map clusters as context,
    address accepted review findings, and run the minimum-net-diff self-check against
    `git diff <BASE_HEAD_SHA>..HEAD` before each commit. Do not touch
    tasks outside `Tasks in scope` except where required by an accepted reviewer finding.
```

Re-dispatch the reviewer for narrow re-review plus the branch-wide pruning sweep over `BASE_HEAD_SHA..HEAD`. Iterate until all in-scope tasks are `Integration status: APPROVED` and every surviving hunk is justified by approved objectives, approved semantic-sync context, logged user decisions, or project convention fit.

### Step 5: Close Integrate

Run the full drift-test suite again. When it passes and integration review is APPROVED:

- remove temporary `## Sync Map` from PLAN.md, if present
- remove temporary task-local `**Sync impact:**` fields unless a lasting task assumption still belongs in the task block
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

Fetch the recorded `BASE_REF` when it is a remote-tracking ref and check whether it advanced since Integrate:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
CURRENT_BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

If `CURRENT_BASE_HEAD_SHA` differs from the recorded `BASE_HEAD_SHA`, re-enter Sync before publishing or landing the work.

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
- **Small changes:** Keep the same five steps, but dispatch fewer agents and keep Sync Map absent when there is no material sync context.

## Red Flags

**Never:**
- Refactor before Sync when the base has advanced.
- Use `PRE_SYNC_BASE_SHA` as the post-sync minimum-net-diff baseline.
- Skip the integration reviewer after Sync.
- Leave `## Sync Map` in PLAN.md after Integrate closes.
- Enter Finish without checking whether the base advanced again.

**Always:**
- Run the full drift-test suite on every integration pass (new drift tests scoped to tasks not yet `Integration status: APPROVED`; running the suite is not scoped).
- Use semantic-merge for intent-aware branch syncs.
- Keep Sync serialized and refactor parallelizable only after Sync lands.
- Log user decisions before acting.
