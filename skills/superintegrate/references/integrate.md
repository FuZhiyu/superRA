# Integrate

Integrate obtains researcher approval for the protected record and reviewer-authored temporary refactoring task, then executes and reviews that task.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD` — never the old merge base (`PRE_SYNC_BASE_SHA`) for minimum-net-diff review after Sync.

## Step 1: Run the protection suite

Every existing check plus the mechanisms selected at Protect. A failing drift test or document check blocks Integrate until classified under its owning protection discipline.

## Step 2: Recover the task state

Read the temporary task from Mature & Consolidate; check the git log for an `integrate(mature)` approval commit naming its reviewed SHA.

- Task missing, or not identifying the Protect decision commit, protected-record paths, `BASE_HEAD_SHA`, bounded actions, and verification: return to Mature & Consolidate Step 3.
- Approval commit missing: continue to the researcher gate.
- Otherwise resume from task status: `not-started` — execute; `implemented` or `revise` — enter the review or fix loop; `approved` — close Integrate.

## Step 3: Run the researcher gate

Present one review surface:

1. the completed permanent documentation and result files;
2. the mature task tree and its durable `## Results`;
3. the temporary task, with automatic pruning items and other refactoring opportunities.

Ask whether to approve the protected record and task. A change to the Protect decision returns to Protect; a correction to its materialization to Mature & Consolidate Step 2; a task-only change to its reviewer at Step 3. Re-present the surface after any revision. Every approval creates an `integrate(mature): …` commit recording the reviewed SHA and decision — empty when approval changes no files.

## Step 4: Execute the approved task

Assign the `Stage: integration` implementer seat per `agent-orchestration` §Seat Assignment:

```text
Prompt:
  Load `superRA:implement-task` skill.

  Stage: integration
  Task: <temporary refactoring task>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
```

The implementer writes the execution outcome and verification evidence to the temporary task's `## Results` and leaves it `implemented`.

## Step 5: Adjudicate implementation concerns

Resolve concerns inside the approved task through an implementer fix. Execution revealing a materially different protected outcome returns to Mature & Consolidate Step 2; a materially different refactoring action, to its reviewer at Step 3. Repeat the researcher gate before applying the new work.

## Step 6: Assign the reviewer seat

This pass always runs: it is the one independent review of the accumulated work, whatever review individual tasks got.

First complete `skills/using-superra/references/task-companion-files.md` §Promote for each affected task retaining companions. Then assign per `agent-orchestration` §Seat Assignment:

```text
Prompt:
  Load `superRA:review-task` skill.

  Stage: integration
  Task: <temporary refactoring task>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Tier: thorough
```

## Step 7: Refactor loop

Adjudicate REVISE findings through `agent-orchestration`; iterate implementer fixes plus narrow re-review until the task is `approved` and the `refactor-and-integrate` checklist passes. A fix expanding or materially changing the approved task returns to Mature & Consolidate Step 3 and then the researcher gate; a change to the protected record, to Step 2.

## Step 8: Close Integrate

Run the protection suite again. Once it passes and integration review approves:

- remove the temporary refactoring task, then run `superra task check`;
- remove every temporary task-local `## Sync Impact` section, folding any lasting task assumption into the task's `## Objective`;
- commit the closeout edit (`integrate(fit): …`). The approval commit, reviewed execution commit, approved durable tasks, and closeout commit record that Integrate closed.
