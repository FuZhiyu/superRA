# Mature & Consolidate

Run this stage after Sync and before Integrate. The researcher’s Protect choices determine which results survive, where the permanent documentation belongs, and which automated protection to add. One drafter materializes that protected record; one reviewer verifies it and derives the temporary refactoring task. Refactoring begins after the researcher gate in Integrate.

Load `superplan/references/task-tree-design.md`, `superplan/references/consolidation.md`, and `task-tree/references/task-file-contract.md`.

## Step 1: Assemble the maturation input

Read the researcher’s confirmed Protect choices, any protection artifacts or commit created from them, any affected-task working `## Results`, and the post-Sync governing diff. If a documentation-only decision was interrupted before this stage and is no longer present in the workflow context, re-enter Protect. Survey every affected task and subtree against its selected durable home. Key results selected at Protect must appear in the permanent record; results selected to drop must not be preserved indirectly as standalone findings.

## Step 2: Materialize the permanent record and mature the tree

Fill one `Stage: maturation` implementer seat for the affected tasks. Create or revise the agreed user-facing documentation and result files first. Then consolidate the task structure and distil each affected task’s `## Results` against those permanent artifacts:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: maturation
  Tasks: <affected task paths>

  Additionally: apply the researcher’s Protect choices. Write the selected
    permanent documentation and result files first, then consolidate the task
    structure per `superplan/references/consolidation.md` and mature `## Results`
    per `task-tree/references/task-file-contract.md` §Results Shape. Land
    recoverable commits per affected subtree.
```

The task record points to a permanent document when that document is the source of truth; it does not duplicate it. Structural folds and result maturation still happen together so removed task content lands at its durable home.

## Step 3: Review the record and derive the temporary task

Fill one reviewer seat over the affected tasks, permanent artifacts, proposed final tree, and `BASE_HEAD_SHA..HEAD`:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: maturation
  Tasks: <affected durable task paths>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Additionally: load `superRA:refactor-and-integrate`. Verify that the Protect
    choices are fully and navigably represented and every support path that
    must survive refactoring is explicit. Once the record passes, create one
    recognizably temporary refactoring task under the lowest durable ancestor
    covering the scope. Leave it `not-started`; link its `## Objective` to the
    protected record; record `BASE_HEAD_SHA`; name every pruning or refactoring
    action by artifact or tightly bounded family; and include the verification
    that must pass.
```

Iterate the same drafter and reviewer seats until the protected record passes review and the temporary task is complete. Mature & Consolidate is complete when that task is `not-started` and satisfies the dispatch contract above; otherwise resume at this step.

## Step 4: Enter Integrate

Enter Integrate with the protected record and reviewer-authored temporary task.
