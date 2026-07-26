---
title: "INTEGRATE: Protect, Sync, and Ship"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

The tasks are approved, so the work is correct, but correct work can still break when it lands on a shared base. INTEGRATE folds the work into your codebase so the results stay reproducible and coherent over time, then ships it. Say `superintegrate` to enter the phase. It runs as five stages, each described below.

### Protect — choose the permanent record and how to guard it

Before permanent documentation is written, superRA surveys the provisional findings and proposes concrete choices: which results to keep or drop, what the final documentation and result files should look like, where they should live, how the affected task tree should consolidate, and how each kept result should be protected. You choose among those options while the work is still easy to reshape. The approved choices are recorded in a decision commit so later agents and resumed sessions share the same specification.

Permanent results documentation can be sufficient protection. For a headline coefficient or another result where automated drift detection is valuable, you can also request a drift test: a small check that fails when a later sync or refactor moves the saved value. Existing protection checks continue to run throughout integration.

### Sync — fold the base branch in by what the changes mean

The **base branch** is the shared branch your work will eventually land on — usually `main` or your repo's trunk. While you were working on your branch, other people kept advancing the base, so by the time you integrate, the base has changes your branch never saw. Sync brings those incoming changes into your branch before anything else.

It does this **by intent, not by line**. A plain `git merge` resolves conflicts textually — it compares the two versions of each clashing region and you pick a side, with no understanding of why either side changed. Sync instead reads what the incoming changes *mean* and reconciles your work with that intent, so the merged result reflects both sides' purpose rather than whichever hunk happened to win the textual collision. If folding in the incoming intent would actually change the meaning of your work, it stops and asks rather than resolving silently.

### Mature & Consolidate — write the protected record and derive the refactoring task

After Sync, one drafter creates the agreed user-facing documentation and result files, then consolidates the task tree and matures its `## Results` against those artifacts. A task whose output is a document points to that document instead of duplicating it; finished update scaffolding folds into its durable owner.

Together, the permanent documentation, result files, and mature task results are the protected record. One reviewer checks those paths against the recorded Protect decision, compares every in-scope change against that record, and writes one temporary task containing the automatic pruning list and other worthwhile consolidation or refactoring.

### Integrate — approve and execute the refactoring task

You review the completed record, mature task tree, and temporary task together once. After approval, agents execute it mechanically and the reviewer checks the final diff. A materially different protected result returns to maturation; a materially different refactoring action returns to the proposal gate.

### Finish — re-check the base, then ship

Integration takes time, and the base branch may have advanced again while you worked through the earlier stages. Finish re-checks that the base hasn't moved underneath you — if it has, it loops back to Sync before publishing. Once the base is current, it ships: opening a pull request, or fast-forwarding the work into the base for a local merge, and then cleaning up the worktree the work ran in.

### What stays with you

superRA asks for your input twice: first for the results, permanent documentation, and protection choices; later for the completed record and temporary refactoring task. It also stops for a missing base decision or an intent-changing conflict it will not resolve silently. The full phase is owned by [superintegrate](skills/superintegrate/SKILL.md).
