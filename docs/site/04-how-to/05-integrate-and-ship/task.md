---
title: "Integrate and Ship"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

<!-- intent: frame integration as a distinct phase with a specific purpose -->
You have a branch of analysis code that works, the reviewer approved the tasks, and now you want to land it on `main` without breaking existing results or making the codebase incoherent.
The INTEGRATE phase handles this: it protects key results with drift tests, syncs the branch against the current base using intent-aware merging, refactors for codebase fit, matures the documentation, and opens the PR.

Trigger integration by saying:

> "Integrate this with main."
> "superintegrate: prepare this for PR."

The `superintegrate` skill is the authority for the full protocol; this guide explains what each step does and when you are asked to make decisions.

## Protect

<!-- intent: explain drift tests and the researcher decision point -->
The first step asks you to confirm which results are "key results" worth protecting.
The agent proposes a list drawn from the `## Results` sections in your task tree.

You review the list and say which to protect, add, or remove.
The agent then writes drift tests — lightweight scripts that re-run the computation and assert the result has not changed — and commits them.

These tests run on every future integration pass.
They are the safety net that lets the agent refactor and sync without silently changing your findings.

The full drift-test mechanism is explained in [Concepts › Integration & Protection](#/03-concepts/05-integration-and-protection).

## Sync

<!-- intent: explain semantic merge and why it is not a bare git merge -->
Sync brings your branch onto the current `main` without a bare `git merge`.
Instead, the agent uses the `semantic-merge` skill: it investigates the intent of every conflict, classifies each changed file (behavior, data, docs, generated output, tests, config), resolves conflicts intent-first, and escalates to you only when a conflict would change what the code *means*.

You are asked to confirm the target base if it was not already recorded in the task tree.
You may also be asked to adjudicate intent-changing conflicts — cases where two edits are logically incompatible and only you can decide which intent wins.

Do not run `git merge` manually on an analysis branch; the `merge-guard` hook will remind you to use `semantic-merge` instead.

## Integrate

<!-- intent: explain the refactor step -->
After sync, the agent refactors the post-sync diff for codebase fit: removing dead code the sync exposed, making the new analysis follow existing project conventions, and ensuring the diff is the minimum needed to land the work.
A reviewer agent then checks the integrated state.

You are asked only when the reviewer surfaces something that requires a methodology or scope decision.

The integration checklist is in the [`refactor-and-integrate` skill](skills/refactor-and-integrate/SKILL.md).

## Document

<!-- intent: explain results maturation step -->
The agent matures the `## Results` sections in the affected task files from terse agent notes into reader-facing permanent records.
Findings stay in the task files; a synthesized summary is written up into the highest task the integration touched, with links down to the leaf tasks holding per-task evidence.

## Finish

<!-- intent: explain the final PR step -->
The agent does a final freshness check — runs the drift tests, confirms the base has not advanced again — then opens the PR.
You review and merge.

After the PR merges, the agent cleans up the branch and closes the integration workflow.
