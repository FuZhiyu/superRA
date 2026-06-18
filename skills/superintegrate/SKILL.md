---
name: superintegrate
description: "Integrate code-complete superRA work. Requires superRA:using-superra. Use for result protection, base sync, codebase-fit refactors, permanent records, cleanup, or PR preparation."
---

# superintegrate — the INTEGRATE phase

Workflow skill for the **INTEGRATE** phase. It takes a reproducibility-verified branch through five steps:

```
Protect   -> protect key results (default: drift tests)
Sync      -> bring the branch onto the current base via semantic-merge
Integrate -> refactor with Sync context and pass integration review
           -> [consolidation gate] judge the tree clean-enough vs needs-a-pass before Document
Document  -> mature task.md ## Results sections for reader-facing clarity
Finish    -> final freshness check, PR or fast-forward, and cleanup

Any step -> superplan §User Feedback and Changing the Task Tree
           when scope, methodology, task structure, or APPROVED status changes materially
```

**Announce at start:** "I'm using the superintegrate skill to prepare this work for integration."

## Stop Points

The Workflow Frontier Resolver chooses where to enter. Once entered, run the selected step's local gates; do not redo task-local approvals outside the affected frontier just because a rollup milestone was unchecked.

Legitimate stop points (fold every answer into the relevant task objective **before** acting):

- **Protect:** key-result protection confirmation.
- **Sync:** target base confirmation when no prior decision records it; intent-changing conflicts surfaced by `semantic-merge`.
- **Integrate:** meaningful drift after sync or refactor; user-owned choices surfaced by the integration reviewer.
- **Document:** maturation scope when project guidance is silent.
- **Finish:** hard blockers only, such as target base advancing again after Integrate.

## Dispatch Convention

**Load `superRA:agent-orchestration` before writing any dispatch prompt.** Task-scoped dispatches use the Stage values in `superRA:using-superra` §Skill-Load Manifest; do not restate load lists in prompts.

Sync uses `Stage: sync` with generic sync author / sync reviewer agents and the relevant `semantic-merge` mode reference.

## Protect

Drift tests are the default protection mechanism, guarding key results through Sync, Integrate, Finish, and future work. For the writing vertical, "key results" are the manuscript artifacts; protection is satisfied by document-build success plus outline stability across the merged state — see `skills/writing/references/integration.md`.

**Always run the full drift-test suite on every integration pass.** Authoring new drift tests is scoped to tasks with `status:` not `approved` plus orchestrator-declared related tasks from `superplan §User Feedback and Changing the Task Tree`; running the suite is not scoped.

### Steps

1. **Extract key results from task.md `## Results` sections.** Walk the `superRA/` tree (`superra task tree`) and identify main findings across tasks. Protect main findings, not every intermediate number. Reference tasks by path (e.g., `data-preparation/merge`).
2. **Confirm coverage with the researcher.** Stop point:
   ```text
   These results seem like the key findings to protect:
   - [result 1: description and value] (from task-path/subtask)
   - [result 2: description and value] (from task-path/subtask)

   Which should be protected? Any to add or remove?
   ```
3. **Dispatch protection-creator.** `Stage: protection`, canonical implementer template. Drift tests reference task paths, not task numbers.
4. **Dispatch protection-reviewer.** `Stage: protection`, canonical reviewer template. On REVISE, adjudicate and fix per `agent-orchestration` §Handling Reviewer Feedback until APPROVE.
5. **Run tests on the current branch.** If new tests fail on existing code, fix the tests.
6. **Commit tests and task.md updates.**
7. **Flip `Drift tests created`** in root task.md §Workflow Status once all confirmed key results are protected and the full drift-test suite passes.

## Sync

Sync brings the branch onto the current base before refactor starts. It is serialized: one generic sync author followed by one generic sync reviewer, no parallelization.

### Step 1: Resolve the target base

Resolve and record a candidate base ref from prior task context or git. This is a branch/ref name, not a merge-base SHA:

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
This integration will sync the branch against <base-ref>.
Is that correct, or did it split from a release branch, co-authored track,
or sibling branch?
```

Record the confirmed `BASE_REF` in root task.md before fetching, computing anchors, or dispatching.

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
  Stage: sync
  Role: sync author
  References:
    - semantic-merge/references/workflow-sync-author.md

  Task: Sync this branch with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>

  Use semantic-merge workflow sync author mode. Land the merge commit plus
  any propagation commits needed to reach semantic coherence — `SKILL.md
  §Semantic Coherence Checklist §Scope boundary` is the stopping rule. The
  branch-level sync narrative is the commit messages; add a task-local
  `## Sync Impact` section to each affected task.md whose post-sync diff needs
  task-specific context. Defer codebase coherence — convention fit, utility
  reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff — to
  `refactor-and-integrate` via Integrate.
```

If the sync author returns `NEEDS_CONTEXT` or `BLOCKED` because a user decision is required, the orchestrator asks the user, folds the decision into the relevant task objective, commits, and re-dispatches the sync author with the decision context.

### Step 4: Dispatch the sync reviewer

Before Integrate begins, dispatch one generic sync reviewer:

```text
Agent(generic):
  Stage: sync
  Role: sync reviewer
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
  task-local `## Sync Impact` coverage, and scope boundary. Record any
  sync-review finding via the standard mechanism (affected task's
  `## Review Notes`, or the REVISE return for a branch-level finding with no
  task home). Return APPROVE or REVISE.
```

On REVISE, adjudicate sync-review findings per `superRA:agent-orchestration` §Handling Reviewer Feedback, re-dispatch the sync author for accepted items, then re-dispatch the sync reviewer. Integrate starts only after sync review APPROVES.

## Integrate

Integrate is the post-sync quality gate. It uses task-local `## Sync Impact` sections plus the sync commit messages (git log) as context for the approved post-sync diff, fits the code to the host project, audits project docs, and verifies the surviving diff against the current base.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base for minimum-net-diff review after Sync.

### Step 1: Run the full drift-test suite

Run the full suite after Sync and before refactor. Failing drift tests block Integrate until classified per `result-protection/references/drift-test-quality.md`.

### Step 2: Dispatch the integration reviewer

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Post-sync integration review
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Sync context: task-local `## Sync Impact` sections plus the sync commit messages (git log)

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, then review `git diff <BASE_HEAD_SHA>..HEAD`.
    For every touched or Sync-impact-affected task, either set
    `status: approved` in its frontmatter or write review notes in
    `## Review Notes` and set `status: revise`. Findings should
    cover minimum surviving branch delta, codebase fit, project-doc audit,
    drift-test implications, and task-file coherence. Do not recreate
    incoming-intent research or re-review semantic coherence already approved
    by sync review.
```

### Step 3: Orchestrator adjudication

Read the task-local `## Review Notes` sections for tasks with `status: revise`. Classify reviewer findings per `superRA:agent-orchestration` §Handling Reviewer Feedback.

- Batch all user-owned questions into one stop point.
- Route substantive task-tree restructures through `superplan §User Feedback and Changing the Task Tree`.
- Fold user decisions into the relevant task objectives before dispatching fixes.

### Step 4: Refactor loop

Dispatch implementer(s) for accepted `status: revise` items:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: Fix integration review items for <task-path-list>
  Tasks in scope: <task paths with status: revise>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, address accepted review findings, and run the minimum-net-diff
    self-check against `git diff <BASE_HEAD_SHA>..HEAD` before each commit. Commit code + task.md
    atomically. Do not touch tasks outside `Tasks in scope` except where required by an accepted
    reviewer finding.
```

For non-minor fixes that require reviewer re-dispatch per `agent-orchestration` §Handling Reviewer Feedback, include narrow re-review plus the branch-wide pruning sweep over `BASE_HEAD_SHA..HEAD`. Iterate until all in-scope tasks have `status: approved` and every surviving hunk is justified by approved objectives, approved semantic-sync context, logged user decisions, or project convention fit.

### Step 5: Close Integrate

Run the full drift-test suite again. When it passes and integration review is APPROVED:

- remove every temporary task-local `## Sync Impact` section, unless a lasting task assumption still belongs in the task.md — in which case fold that assumption into the task's `## Objective` and remove the section. Then run `superra task check` (warn-only `sync-impact` category) and confirm it flags no surviving `## Sync Impact`.
- flip `Integrated` in root task.md §Workflow Status
- commit the closeout doc edit

## Consolidation Gate

Once per integration, between closing Integrate and entering Document, the orchestrator surveys the tree and decides whether it is clean enough to mature or needs a consolidation pass first. This is orchestrator inline work, not a dispatched stage.

1. Load `superplan/references/task-tree-design.md` and apply its durable-home and update-task lifecycle rules to the affected tree before Document. The check is **whole-tree within the affected tree**, not frontier-internal: compare every task and subtree, including approved and in-flight update tasks, against its parent and other candidate durable owners. Run `superra task tree`, `superra task dag`, and `superra task check --category placement`; use the placement warnings as advisory evidence alongside the manual survey.
2. Record the verdict — clean-enough or needs-a-pass, one line — in the durable integration record in root task.md §Workflow Status so a later session sees the judgment was made.
3. A clean-enough verdict is invalid while a temporary update task survives as a misplaced durable subtree, or while an action-verb parent that should mature into a stable concern remains framed as the update episode. On needs-a-pass, load `superplan/references/consolidation.md` and run its survey → classify → propose → approve → execute protocol (atomic commit), then enter Document on the consolidated tree. Material merge, prune, restructure, mature/rename, and status-invalidating scope expansion still route through `superplan §User Feedback and Changing the Task Tree` — the gate triggers the assessment, it does not grant authority to restructure approved work unilaterally.

## Document

Document matures selected task.md `## Results` sections from live dev log to reader-facing permanent record (Stage 2 maturation per `task-tree/references/task-file-contract.md` §Results Shape).

### Step 1: Identify maturation scope

Walk the `superRA/` tree and identify the highest-level task this integration touched per affected subtree — those are the homes that carry the matured narrative — plus any leaf tasks whose `## Results` still need light evidence cleanup. Trivial results (e.g., "renamed variable, no findings") need no maturation. The default home for each affected subtree is its highest touched task; ask only when project guidance is silent on whether to confirm a different home:

```text
This integration touched these subtrees; the matured narrative defaults
to each subtree's highest touched task:
- [highest-touched-task-1: one-line summary]
- [highest-touched-task-2: one-line summary]

Confirm these as the maturation homes, or name a different home per subtree?
```

Fold the answer into the relevant highest-touched task's `## Results` / `## Revision Notes` before dispatching.

### Step 2: Dispatch doc-writer

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: documentation
  Task: Mature results for reader-facing clarity
  Tasks in scope: <task paths whose results need maturation>

  Additionally: mature each in-scope task's `## Results` section per
    `task-tree/references/task-file-contract.md` §Results Shape: fact-check against
    code outputs, restructure for reader clarity, materialize figures when
    needed using `report-in-markdown`, and ensure notation consistency across
    tasks. Edit task.md files in place. Land recoverable commits (one per
    task or logical group) and report which sub-commits landed.
```

### Step 3: Dispatch doc-reviewer

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: documentation
  Task: Review matured results
  Git range: <BASE_SHA>..<HEAD_SHA>
  Tasks in scope: <same task paths>

  Additionally: Review each in-scope task's `## Results` section per
    `task-tree/references/task-file-contract.md` §Results Shape, including Stage 2
    maturation at the highest-touched-task narrative homes, retained leaf
    evidence, and task-local figure attachments.
    <prior-round adjudication notes if re-dispatching>
```

On REVISE, adjudicate and fix per `agent-orchestration` §Handling Reviewer Feedback until APPROVE. If a documentation finding traces to the code, re-enter Integrate.

On APPROVE, flip `Docs finalized` in root task.md §Workflow Status and commit.

## Finish

Finish executes the user's completion choice from `superimplement`. The `superRA/` directory is committed as-is — it is part of the permanent branch record.

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

### Step 2: Mark final action

Flip the final workflow checkbox in root task.md §Workflow Status in the same commit that performs the final action.

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

If the work used a worktree, remove it per `superRA:agent-orchestration/references/worktree-harness-fallback.md`. Seeded non-git data disappears with the worktree; see `superRA:worktree-data-sync` for data teardown.

Report what was published or landed and what was cleaned up.

## When to Lighten

- **Standalone analysis:** Protect still runs. Sync may be a no-op. Integrate often collapses to a short reviewer pass.
- **Small changes:** Keep the same five steps, but dispatch fewer agents and add no `## Sync Impact` sections when there is no material sync context.
- **Writing-vertical tasks:** Most writing work runs as standalone Review / Polish / Draft per `skills/writing/SKILL.md` and does not enter this workflow. Only large work (whole-section drafts, whole-paper revisions, R&R passes) reaches Integrate; for those, Protect substitutes build + outline-stability for drift tests, and the Integrate reviewer additionally walks `skills/writing/references/integration.md`.
- **Task tree consolidation:** The assessment gate always runs, but a clean-enough tree skips the consolidation pass entirely — see §Consolidation Gate.

## Red Flags

- Refactoring before Sync when the base has advanced, or using `PRE_SYNC_BASE_SHA` (not `BASE_HEAD_SHA`) as the post-sync minimum-net-diff baseline.
- Parallelizing Sync, or parallelizing refactor before Sync lands.
- Entering Finish without re-checking whether the base advanced since Integrate.
