# Mature & Consolidate

Run this stage after Sync and before Integrate. The researcher’s Protect choices determine which results survive, where the permanent documentation belongs, and which automated protection to add. This stage materializes that record, matures the task tree, and prepares the refactoring work the researcher will review.

Load `superplan/references/task-tree-design.md`, `superplan/references/consolidation.md`, and `task-tree/references/task-file-contract.md`.

## Step 1: Assemble the maturation input

Read the researcher’s confirmed Protect choices, any protection artifacts or commit created from them, the affected tasks’ working `## Results`, and the post-Sync governing diff. Survey every affected task and subtree against its selected durable home. Key results selected at Protect must appear in the permanent record; results selected to drop must not be preserved indirectly as standalone findings.

## Step 2: Materialize the permanent record and mature the tree

Dispatch `Stage: maturation` implementers per affected subtree. Create or revise the agreed user-facing documentation and result files first. Then consolidate the task structure and distil each affected task’s `## Results` against those permanent artifacts:

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

## Step 3: Prepare the temporary refactoring task

Create one recognizably temporary task under the lowest durable task ancestor that covers the affected scope, or at the task-tree root when no such ancestor exists. Leave it `not-started`; Integrate executes it.

Its `## Objective` links to the permanent documentation, result files, and mature task results, then states the proposed work:

- pruning of tasks, code, outputs, diagnostics, and documentation not justified by the protected record or its documented reproduction, validation, interpretation, and presentation paths;
- consolidation, simplification, duplication removal, host-project convention fit, and stale-documentation repair; and
- verification that must pass after those changes.

Name the affected artifacts or tightly bounded families. Do not copy the protected result prose into the task or create another keep list.

## Step 4: Review the completed record and proposal

Dispatch a fresh reviewer over the affected tasks, permanent artifacts, proposed final tree, and temporary refactoring task:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: maturation
  Tasks: <affected durable task paths>
  Git range: <pre-maturation SHA>..HEAD

  Additionally: verify that the permanent documentation and result files
    implement the Protect choices; the task tree and `## Results` are mature and
    navigable; and every in-scope change is justified by the protected record or
    appears as an actionable item in the temporary refactoring task. Review that
    task as an artifact; leave it `not-started` for Integrate.
```

Iterate until the permanent record, tree, and proposal pass review.

## Step 5: Run the researcher gate

Present one review surface containing:

1. the completed user-facing documentation and result files;
2. the mature task tree and its durable `## Results`; and
3. the temporary refactoring task, including proposed pruning and other refactoring.

Ask whether to approve this record and proposal. If the researcher requests changes, revise or undo the recoverable maturation commits, rebuild the refactoring task, repeat Step 4, and present the updated surface. On every approval, create an `integrate(mature): …` approval commit whose body records the reviewed SHA and decision; use an empty commit when approval changes no files. Then enter Integrate.
