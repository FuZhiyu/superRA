# Integrate

Integrate derives one temporary refactoring task from the protected record, obtains the researcher’s approval, then executes and independently reviews that task.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base (`PRE_SYNC_BASE_SHA`) for minimum-net-diff review after Sync.

## Step 1: Run the protection suite

Run every existing protection check plus the mechanisms selected at Protect. A failing drift test or document check blocks Integrate until classified under its owning protection discipline.

## Step 2: Derive the temporary refactoring task

The permanent documentation, result files, and mature task results are the protected record. Walk every in-scope change and artifact in the governing diff:

1. A change or artifact is protected when it appears in that record or implements a reproduction, validation, interpretation, or presentation path explicitly documented there.
2. Anything else automatically becomes a pruning item.
3. Protected or supporting work that can better fit the host project becomes a non-removal refactoring item when consolidation, simplification, duplication removal, convention fit, or stale-documentation repair is warranted.

Create one recognizably temporary task under the lowest durable task ancestor covering the scope, or at the task-tree root when no such ancestor exists. Leave it `not-started`. Link its `## Objective` to the protected record, name every proposed action by artifact or tightly bounded family, and include the verification that must pass. Do not copy result prose or create a parallel keep list.

## Step 3: Run the researcher gate

Present one review surface containing:

1. the completed permanent documentation and result files;
2. the mature task tree and its durable `## Results`; and
3. the temporary task, including automatic pruning items and other refactoring opportunities.

Ask whether to approve the protected record and task. A requested change to the protected record returns to Mature & Consolidate; revise a task-only change here and present the surface again. On every approval, create an `integrate(mature): …` approval commit whose body records the reviewed SHA and decision; use an empty commit when approval changes no files.

## Step 4: Execute the approved task

Dispatch a `Stage: integration` implementer:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: <temporary refactoring task>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
```

The implementer writes the execution outcome and verification evidence to the temporary task’s `## Results` and leaves it `implemented`.

## Step 5: Adjudicate implementation concerns

Resolve concerns inside the approved task through an implementer fix. If execution reveals a materially different protected outcome or refactoring action, stop and repeat the appropriate record-maturation or task-proposal step and the researcher gate before applying the new work.

## Step 6: Dispatch the independent reviewer

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: <temporary refactoring task>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
```

## Step 7: Refactor loop

Adjudicate any REVISE findings through `agent-orchestration` and iterate implementer fixes plus narrow re-review until the temporary task is `approved` and the `refactor-and-integrate` checklist passes. A fix that expands or materially changes the approved task returns to Step 3; a change to the protected record returns to Mature & Consolidate.

## Step 8: Close Integrate

Run the protection suite again. After it passes and integration review approves:

- remove the temporary refactoring task, then run `superra task check`;
- remove every temporary task-local `## Sync Impact` section, folding any lasting task assumption into the task’s `## Objective`; and
- commit the closeout edit (`integrate(fit): …`). The approval commit, reviewed execution commit, approved durable tasks, and closeout commit record that Integrate closed.
