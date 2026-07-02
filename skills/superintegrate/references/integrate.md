# Integrate

Integrate is the post-sync quality gate, and it runs do-then-verify: a combined refactor + self-review pass first produces the codebase-fit work and the Final-Diff-Self-Check trail, the orchestrator adjudicates that pass's first-round concerns, and only then does an independent reviewer verify the result. It uses task-local `## Sync Impact` sections plus the sync commit messages (git log) as context for the approved post-sync diff, fits the code to the host project, audits project docs, and verifies the surviving diff against the current base.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base (`PRE_SYNC_BASE_SHA`) for minimum-net-diff review after Sync.

The number of integration implementers and reviewers is discretionary, scaled to the post-sync delta per `agent-orchestration §Workload Balancing`: a small single-subtree delta takes one implementer pass (or an inline sweep) plus one reviewer; a large or multi-subtree delta fans out per subtree.

## Step 1: Run the full drift-test suite

Run the full suite after Sync and before refactor. Failing drift tests block Integrate until classified per `result-protection/references/drift-test-quality.md`.

## Step 2: Integration implementer pass (refactor + self-review)

Dispatch `Stage: integration` implementer(s) to fit the post-sync diff to the host project and run the Final-Diff-Self-Check. A trivial post-sync diff collapses to an orchestrator-inline pruning sweep in Direct mode instead of a dispatch.

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: Post-sync codebase-fit refactor and self-review for <task-path-list>
  Tasks in scope: <task paths touched or Sync-impact-affected>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, fit `git diff <BASE_HEAD_SHA>..HEAD` to the host project, and run the
    Final-Diff-Self-Check; self-review and surface concerns per §What You Own. Commit
    code + task.md atomically. Do not touch tasks outside `Tasks in scope`.
```

## Step 3: Orchestrator adjudication

For each first-pass concern returned in `## Review Notes`:

- **fix** — dispatch an implementer to revert the junk or address the finding; or
- **amend** — fold the justification into the relevant task objective via `superplan §User Feedback and Changing the Task Tree`, dropping the concern.

The resolving commit clears the now-moot first-pass note so the independent reviewer in Step 4 starts from a clean `## Review Notes`. Batch all user-owned questions into one stop point; route substantive task-tree restructures through `superplan §User Feedback and Changing the Task Tree`.

## Step 4: Dispatch the independent integration reviewer

Dispatch fresh `Stage: integration` reviewer(s) for a full first review of the codebase-fit pass against its trail:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Post-sync integration review for <task-path-list>
  Tasks in scope: <task paths touched or Sync-impact-affected>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Sync context: task-local `## Sync Impact` sections plus the sync commit messages (git log)

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, then review `git diff <BASE_HEAD_SHA>..HEAD` against the Final-Diff-Self-Check
    trail. For every in-scope task, either set `status: approved` in its frontmatter or
    write review notes in `## Review Notes` and set `status: revise`. Findings should
    cover minimum surviving branch delta, codebase fit, project-doc audit,
    drift-test implications, and task-file coherence. Do not recreate
    incoming-intent research or re-review semantic coherence already approved
    by sync review.
```

## Step 5: Refactor loop

Dispatch implementer(s) for the accepted `status: revise` findings:

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

## Step 6: Close Integrate

Run the full drift-test suite again. When it passes and integration review is APPROVED:

- remove every temporary task-local `## Sync Impact` section, unless a lasting task assumption still belongs in the task.md — in which case fold that assumption into the task's `## Objective` and remove the section. Then run `superra task check` (warn-only `sync-impact` category) and confirm it flags no surviving `## Sync Impact`.
- commit the closeout edit (`integrate(fit): …`); that commit plus the in-scope tasks' `status: approved` is the record that Integrate closed.
