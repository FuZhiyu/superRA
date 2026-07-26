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

Before permanent documentation is written, superRA surveys the provisional findings and proposes concrete choices: which results to keep or drop, what the final documentation and result files should look like, where they should live, and how each kept result should be protected. You choose among those options while the work is still easy to reshape.

Permanent results documentation can be sufficient protection. For a headline coefficient or another result where automated drift detection is valuable, you can also request a drift test: a small check that fails when a later sync or refactor moves the saved value. Existing protection checks continue to run throughout integration.

### Sync — fold the base branch in by what the changes mean

The **base branch** is the shared branch your work will eventually land on — usually `main` or your repo's trunk. While you were working on your branch, other people kept advancing the base, so by the time you integrate, the base has changes your branch never saw. Sync brings those incoming changes into your branch before anything else.

It does this **by intent, not by line**. A plain `git merge` resolves conflicts textually — it compares the two versions of each clashing region and you pick a side, with no understanding of why either side changed. Sync instead reads what the incoming changes *mean* and reconciles your work with that intent, so the merged result reflects both sides' purpose rather than whichever hunk happened to win the textual collision. If folding in the incoming intent would actually change the meaning of your work, it stops and asks rather than resolving silently.

### Mature & Consolidate — write the permanent record and prepare the refactoring proposal

After Sync, agents create the agreed user-facing documentation and result files, then consolidate the task tree and mature its `## Results` against those artifacts. A task whose output is a document points to that document instead of duplicating it; finished update scaffolding folds into its durable owner.

Agents then create one temporary refactoring task. It lists proposed pruning and other opportunities—consolidation, simplification, duplication removal, convention fit, and stale-documentation cleanup—against the permanent record and its documented support paths. You review the completed record, mature task tree, and this task together once. If you want a different outcome, the agents revise or undo the maturation and present it again.

### Integrate — execute the approved refactoring mechanically

After approval, agents execute the temporary task. Work that does not support the permanent record or its reproduction, validation, interpretation, and presentation paths is removed; the survivors are fitted to your codebase under a minimum-net-diff principle.

A fresh reviewer checks the final diff against the approved task and protected record. If execution would require a materially different result or refactoring action, the workflow returns to the previous stage and asks again rather than expanding the proposal silently.

### Finish — re-check the base, then ship

Integration takes time, and the base branch may have advanced again while you worked through the earlier stages. Finish re-checks that the base hasn't moved underneath you — if it has, it loops back to Sync before publishing. Once the base is current, it ships: opening a pull request, or fast-forwarding the work into the base for a local merge, and then cleaning up the worktree the work ran in.

### What stays with you

superRA asks for your input twice: first for the results, permanent documentation, and protection choices; later for the completed record and temporary refactoring task. It also stops for a missing base decision or an intent-changing conflict it will not resolve silently. The full phase is owned by [superintegrate](skills/superintegrate/SKILL.md).
