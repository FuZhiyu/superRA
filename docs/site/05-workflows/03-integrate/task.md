---
title: "INTEGRATE: Protect, Sync, and Ship"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

The tasks are approved, so the work is correct, but correct work can still break when it lands on a shared base. INTEGRATE folds the work into your codebase so the results stay reproducible and coherent over time, then ships it. Say `superintegrate` to enter the phase. It runs as five stages, each described below.

### Protect — pin the key results so a later change can't move them silently

Before anything else moves, superRA guards the results you care about with **drift tests**. A drift test is a small automated check that records a result's current value and fails the moment a later step changes it — the way a unit test fails when behavior breaks, except here the thing being protected is a finding, not a function. A coefficient of 0.42, a long-short spread of 1.8% a month, a sample of 12,840 firm-months: each becomes a check that turns red the instant a sync or refactor shifts it.

This matters because the dangerous regressions are the quiet ones. A later refactor that silently rounds a number differently, or a merge that drops a filter, would otherwise reach the final paper unnoticed. With the result pinned, that same change trips a red test instead. You choose which results are key — superRA proposes a list and asks before pinning — and it then writes the tests and re-runs the full suite at every later stage, so the protection holds through the rest of the phase.

### Sync — fold the base branch in by what the changes mean

The **base branch** is the shared branch your work will eventually land on — usually `main` or your repo's trunk. While you were working on your branch, other people kept advancing the base, so by the time you integrate, the base has changes your branch never saw. Sync brings those incoming changes into your branch before anything else.

It does this **by intent, not by line**. A plain `git merge` resolves conflicts textually — it compares the two versions of each clashing region and you pick a side, with no understanding of why either side changed. Sync instead reads what the incoming changes *mean* and reconciles your work with that intent, so the merged result reflects both sides' purpose rather than whichever hunk happened to win the textual collision. If folding in the incoming intent would actually change the meaning of your work, it stops and asks rather than resolving silently.

### Refactor — shrink to the smallest diff that does the job

Agent-built code tends to accrete: a one-shot script here, a near-duplicate helper there, names that don't match the surrounding code. Refactor fits the work to your codebase under a **minimum-net-diff** principle — the change that survives should be the smallest reviewable diff that does the job, measured against the freshly synced base. That means following the conventions already in the project, reusing utilities that already exist instead of re-implementing them, and dropping scaffolding that was useful while building but adds nothing to the final result.

A tight, convention-matching change is one a reviewer can actually judge. A reviewer wading through a pile of single-use scripts and stray reformatting cannot, and waves through bugs as a result.

### Mature & Consolidate — settle the tree's shape and turn the working notes into a record a stranger can read

Once the code has landed, superRA settles the task tree itself. Over a project, a tree accumulates scaffolding — a small update task spun out to track a fix, a parent named for an action that is now done — and through PLAN and IMPLEMENT each `task.md`'s `## Results` accumulates as a working dev log, terse and written for whoever had the full context in the moment. This stage does both jobs at once, because they are one decision: for each task the integration touched, it decides what survives and where it lands. A finished update task folds into the task that owns its concern; an action-named parent matures into the durable home for its results; a task whose own output is a document shrinks to a pointer to that document; a minor fix not worth surfacing is dropped. The findings that remain are matured into durable documentation a future reader — or you in six months — can follow without the original context in their head.

superRA always asks you to confirm this shape before it executes, even when the tree is already clean, and the work folding two tasks together or pruning a result a reader would expect is surfaced for your explicit approval. The findings are edited for a reader who wasn't there; the analysis itself is not re-run.

### Finish — re-check the base, then ship

Integration takes time, and the base branch may have advanced again while you worked through the earlier stages. Finish re-checks that the base hasn't moved underneath you — if it has, it loops back to Sync before publishing. Once the base is current, it ships: opening a pull request, or fast-forwarding the work into the base for a local merge, and then cleaning up the worktree the work ran in.

### What stays with you

superRA runs the stages and surfaces the choices that are yours to make: which results are the key ones to protect, which branch to sync against, an intent-changing conflict it will not resolve silently, and meaningful drift it sees after a sync or refactor. It stops and asks at those points rather than guessing. The full phase is owned by [superintegrate](skills/superintegrate/SKILL.md).
