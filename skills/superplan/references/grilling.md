# Grilling

Load when planning needs decisions from the researcher: a scoping round at §Entry Assessment, the main round at Phase 3 entry, and again on any tree change that reopens scope.

## The design tree

**Map the work as a tree of decisions** — every decision branches into the decisions that hang off it.

The **frontier** is every decision whose prerequisites are already settled: askable now, without guessing at an answer you have not heard.

## Facts are yours

**A fact the environment holds is your job.** Read it, or dispatch exploration per `agent-orchestration/references/parallel-dispatch.md`. A running exploration is an unsettled prerequisite — it defers the questions downstream of it, not the round.

**A fact only the researcher holds is a question:** venue, research intent, what an output is for.

**A fact only work can produce is a task boundary.** Needs a data build, a derivation, a rendered artifact: split there per `task-tree-design.md` §Splitting Tasks, queue the dependents with `depends_on`, mark them open-ended, and re-enter grilling when the evidence lands.

## The round

- **Channel: `AskUserQuestion`**, batched call after call until the frontier is empty.
- **Recommended answer first**, labeled `(Recommended)`, on every question.
- **A decision with no discrete alternatives** rides the same round as plain numbered text: `❓ **Q1** — **<title>**: <body>`, then `➡️ <recommended answer>`.
- **Carry the evidence.** Name the survey finding or exploration result that raises the question.

Recompute the frontier and ask the next round.

## Landing

**Every settled decision reaches the tree** as contract, per `task-tree-design.md` §Writing Objectives and Details.

**An empty frontier ends the round**, returning to the step that entered it — the Phase 3 round to decomposition, a scoping round to §Entry Assessment, a re-entry round to the change that reopened scope. No confirmation round.
