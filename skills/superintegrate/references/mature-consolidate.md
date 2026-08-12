# Mature & Consolidate

Runs after Sync, before Integrate. Input: the `integrate(protect)` decision commit — surviving results, durable homes, consolidation dispositions, automated protection. One drafter materializes that record; one reviewer verifies it and derives the temporary refactoring task.

Load `superplan/references/task-tree-design.md`, `superplan/references/consolidation.md`, and `task-tree/references/task-file-contract.md`.

## Step 1: Assemble the maturation input

Read the latest applicable `integrate(protect)` commit body, its recorded protection artifacts, affected-task `## Results`, and the post-Sync governing diff. Missing commit, or a Sync outcome that stales a recorded durable home or disposition → re-enter Protect. Survey retained `attachments/` against the decision per `using-superra/references/task-companion-files.md` §Mature and Consolidate. Invariant: results selected to keep appear in the permanent record; results selected to drop are not preserved indirectly as standalone findings.

## Step 2: Materialize the permanent record and mature the tree

Assign the single drafter — the `Stage: maturation` implementer seat — per `agent-orchestration` §Seat Assignment:

```text
Prompt:
  Load `superRA:implement-task` skill.

  Stage: maturation
  Tasks: <affected task paths>
  Protect decision: <integrate(protect) commit SHA>

  Additionally: apply the recorded Protect decision. Write the selected
    permanent documentation and result files first, then consolidate the task
    structure per `superplan/references/consolidation.md` and mature `## Results`
    per `task-tree/references/task-file-contract.md` §Results Shape. Rewriting
    surviving task files down to terse is part of the job: `implement-task`
    `superRA:communicate` is the bar for every section you touch, not only new writes.
    Land recoverable commits per affected subtree.
```

Structural folds and result maturation happen together, so removed task content lands at its durable home.

## Step 3: Review the record and derive the temporary task

Assign the single reviewer seat per `agent-orchestration` §Seat Assignment:

```text
Prompt:
  Load `superRA:review-task` skill.

  Stage: maturation
  Tasks: <affected durable task paths>
  Focus: correctness, results-writing
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Protect decision: <integrate(protect) commit SHA>

  Additionally: load `superRA:refactor-and-integrate`. Verify that the Protect
    decision is fully and navigably represented at its recorded artifact and
    task paths, and that every support path that must survive refactoring is
    explicit there. Once the record passes, create one recognizably temporary
    refactoring task under the lowest durable ancestor covering the scope.
    Leave it `not-started`; link its `## Objective` to the Protect decision
    commit and protected-record paths; record `BASE_HEAD_SHA`; name every
    pruning or refactoring action by artifact or tightly bounded family; and
    include the verification that must pass.
```

Iterate both seats until the record passes review and the temporary task satisfies the dispatch contract at `not-started`; then enter Integrate with the protected record and that task.
