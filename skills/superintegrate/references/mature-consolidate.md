# Mature & Consolidate

Run this stage after Sync and before Integrate. The researcher’s Protect choices determine which results survive, where the permanent documentation belongs, and which automated protection to add. This stage materializes and verifies that protected record; refactoring begins in Integrate.

Load `superplan/references/task-tree-design.md`, `superplan/references/consolidation.md`, and `task-tree/references/task-file-contract.md`.

## Step 1: Assemble the maturation input

Read the researcher’s confirmed Protect choices, any protection artifacts or commit created from them, any affected-task working `## Results`, and the post-Sync governing diff. If a documentation-only decision was interrupted before this stage and is no longer present in the workflow context, re-enter Protect. Survey every affected task and subtree against its selected durable home. Key results selected at Protect must appear in the permanent record; results selected to drop must not be preserved indirectly as standalone findings.

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

## Step 3: Verify the protected record

Dispatch a fresh reviewer over the affected tasks, permanent artifacts, and proposed final tree:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: maturation
  Tasks: <affected durable task paths>
  Git range: <pre-maturation SHA>..HEAD

  Additionally: verify that the permanent documentation and result files
    implement the Protect choices; every kept result appears; every dropped
    result is absent; the task tree and `## Results` are mature and navigable;
    and any reproduction, validation, interpretation, or presentation path that
    must survive later refactoring is explicit in the record.
```

Iterate until the permanent record and tree pass review.

## Step 4: Enter Integrate

The permanent documentation, result files, and mature task results now constitute the protected record. Enter Integrate to derive the temporary refactoring task from that record.
