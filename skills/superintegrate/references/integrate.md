# Integrate

Integrate executes the researcher-approved temporary refactoring task against the protected permanent record. It runs do-then-verify: the implementer applies the approved pruning and refactoring, the orchestrator adjudicates concerns, and an independent reviewer verifies the final state.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base (`PRE_SYNC_BASE_SHA`) for minimum-net-diff review after Sync.

## Step 1: Run the protection suite

Run every existing protection check plus the mechanisms selected at Protect. A failing drift test or document check blocks Integrate until classified under its owning protection discipline.

## Step 2: Execute the temporary refactoring task

Dispatch a `Stage: integration` implementer with the temporary task and the protected record:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: <temporary refactoring task>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Additionally: execute the researcher-approved objective mechanically. Use the
    linked permanent documentation, result files, and mature task results as the
    protected record; apply the proposed pruning and other refactoring; fit the
    survivors to the host project; and run the Final-Diff-Self-Check against
    `git diff <BASE_HEAD_SHA>..HEAD`.
```

The implementer writes the execution outcome and verification evidence to the temporary task’s `## Results` and leaves it `implemented`.

## Step 3: Adjudicate implementation concerns

Resolve concerns inside the approved proposal through an implementer fix. If execution reveals a materially different protected outcome or refactoring action, stop, return to Mature & Consolidate, update the permanent record or temporary task, and repeat its reviewer and researcher gates before applying the new work.

## Step 4: Dispatch the independent integration reviewer

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: <temporary refactoring task>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
```

## Step 5: Refactor loop

Adjudicate any REVISE findings through `agent-orchestration` and iterate implementer fixes plus narrow re-review until the temporary task is `approved` and the `refactor-and-integrate` checklist passes. A fix that expands or materially changes the approved proposal returns to Mature & Consolidate instead.

## Step 6: Close Integrate

Run the protection suite again. After it passes and integration review approves:

- remove the temporary refactoring task, then run `superra task check`;
- remove every temporary task-local `## Sync Impact` section, folding any lasting task assumption into the task’s `## Objective`; and
- commit the closeout edit (`integrate(fit): …`). The reviewed execution commit, the approved durable tasks, and the closeout commit record that Integrate closed.
