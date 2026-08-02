# Integrate

Integrate obtains researcher approval for the protected record and reviewer-authored temporary refactoring task, then executes and reviews that task.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base (`PRE_SYNC_BASE_SHA`) for minimum-net-diff review after Sync.

## Step 1: Run the protection suite

Run every existing protection check plus the mechanisms selected at Protect. A failing drift test or document check blocks Integrate until classified under its owning protection discipline.

## Step 2: Recover the task state

Read the temporary task created by Mature & Consolidate and inspect the git log for an `integrate(mature)` approval commit naming its reviewed SHA. If the task is missing or does not identify the Protect decision commit, protected-record paths, `BASE_HEAD_SHA`, bounded actions, and verification, return to Mature & Consolidate Step 3. If the approval commit is missing, continue to the researcher gate. Otherwise resume from task status:

- `not-started` — execute the approved task;
- `implemented` or `revise` — enter the review or fix loop;
- `approved` — close Integrate.

## Step 3: Run the researcher gate

Present one review surface containing:

1. the completed permanent documentation and result files;
2. the mature task tree and its durable `## Results`; and
3. the temporary task, including automatic pruning items and other refactoring opportunities.

Ask whether to approve the protected record and task. A requested change to the Protect decision returns to Protect; a correction to its materialization returns to Mature & Consolidate Step 2; a task-only change returns to its reviewer at Step 3. Present the surface again after any revision. On every approval, create an `integrate(mature): …` approval commit whose body records the reviewed SHA and decision; use an empty commit when approval changes no files.

## Step 4: Execute the approved task

Assign the `Stage: integration` implementer seat per `agent-orchestration` §Seat Assignment:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: <temporary refactoring task>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
```

The implementer writes the execution outcome and verification evidence to the temporary task’s `## Results` and leaves it `implemented`.

## Step 5: Adjudicate implementation concerns

Resolve concerns inside the approved task through an implementer fix. If execution reveals a materially different protected outcome, return to Mature & Consolidate Step 2; if it reveals a materially different refactoring action, return to its reviewer at Step 3. Repeat the researcher gate before applying the new work.

## Step 6: Assign the reviewer seat

Before review, load `skills/using-superra/references/task-companion-files.md` for every affected task that retains companion files and complete its promotion step.

Assign it per `agent-orchestration` §Seat Assignment:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: <temporary refactoring task>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
```

## Step 7: Refactor loop

Adjudicate any REVISE findings through `agent-orchestration` and iterate implementer fixes plus narrow re-review until the temporary task is `approved` and the `refactor-and-integrate` checklist passes. A fix that expands or materially changes the approved task returns to Mature & Consolidate Step 3 and then the researcher gate; a change to the protected record returns to Mature & Consolidate Step 2.

## Step 8: Close Integrate

Run the protection suite again. After it passes and integration review approves:

- remove the temporary refactoring task, then run `superra task check`;
- remove every temporary task-local `## Sync Impact` section, folding any lasting task assumption into the task’s `## Objective`; and
- commit the closeout edit (`integrate(fit): …`). The approval commit, reviewed execution commit, approved durable tasks, and closeout commit record that Integrate closed.
