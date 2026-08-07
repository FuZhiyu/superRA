# Grilling

Load when planning needs decisions from the researcher: a scoping round at §Entry Assessment, the main round at Phase 3 entry, and again on any tree change that reopens scope.

## The design tree

**Map the work as a tree of decisions** — every decision branches into the decisions that hang off it.

The **frontier** is every decision whose prerequisites are already settled: askable now, without guessing at an answer you have not heard. A question depending on one still open belongs to a later round.

## Facts are yours

**A fact the environment holds is your job.** Read it, or dispatch exploration per `agent-orchestration/references/parallel-dispatch.md`. A running exploration is an unsettled prerequisite — it defers the questions downstream of it, not the round.

**A fact only the researcher holds is a question:** venue, research intent, what an output is for.

**A fact only work can produce is a task boundary.** Needs a data build, a derivation, a rendered artifact: split there per `task-tree-design.md` §Splitting Tasks, queue the dependents with `depends_on`, mark them open-ended, and re-enter grilling when the evidence lands.

## The round

Ask the whole frontier in one round.

- **Channel: `AskUserQuestion`**, batched call after call until the frontier is empty. Never hold a question back for want of slots in a call.
- **Recommended answer first**, labeled `(Recommended)`, on every question.
- **A decision with no discrete alternatives** rides the same round as plain numbered text: `❓ **Q1** — **<title>**: <body>`, then `➡️ <recommended answer>`.
- **Carry the evidence.** Name the survey finding or exploration result that raises the question.

Answers settle decisions and push the frontier outward. Recompute it and ask the next round.

## Landing

**Every settled decision reaches the tree** — a binding objective bullet, a scoped `### Context` / `### Constraints`, or `## Planner Guidance`, per `task-tree-design.md` §Writing Objectives and Planner Guidance. State it as the current contract; git carries the date.

**Frontier empty ends the session.** Go to Phase 3 decomposition.
