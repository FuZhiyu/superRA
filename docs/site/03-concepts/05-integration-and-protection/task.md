---
title: "Integration and Protection"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Getting a correct result is not the same as landing it safely. Once the analysis is in hand, superRA shifts from "fast and exploratory" to "strict and protective": the integration phase folds the work into your codebase in a way that keeps the results reproducible and coherent for the long haul. This is the job of [superintegrate](skills/superintegrate/SKILL.md), and it is a phase of its own — not a final `git commit` — because each of its steps guards against a different way that good work quietly goes wrong after it is done.

## Protecting results against drift

The first risk is that a result silently changes later — a refactor, a dependency bump, or a downstream edit shifts a headline number and nobody notices. superRA guards the key results before they touch your base branch by writing **drift tests**: small automated checks that pin the results you care about, so any future change that moves them fails loudly instead of slipping through. Drift and regression tests are the default protection mechanism; the [result-protection](skills/result-protection/SKILL.md) skill covers selecting which results to protect and writing the tests that hold them. The [How-To › Integrate and Ship](#/04-how-to/05-integrate-and-ship) guide walks the protection step in practice.

## Syncing by intent, not by reflex

The second risk shows up when your branch has to catch up with a base branch that moved while you were working. A blind `git merge` resolves conflicts mechanically — by line — and will happily produce code that compiles but no longer means what either side intended. superRA uses **semantic merge** instead: it investigates the intent behind each incoming change, resolves conflicts to preserve that intent, escalates to you when a change would alter what your work means, and leaves the existing result protection passing on every commit. The mechanism is owned by the [semantic-merge](skills/semantic-merge/SKILL.md) skill, and intent-aware syncs never fall back to a bare merge.

## Refactor, document, ship

With results protected and the branch synced, the remaining steps make the work fit to live in the codebase. The post-sync changes are refactored for convention fit and a minimal, reviewable diff — the discipline in [refactor-and-integrate](skills/refactor-and-integrate/SKILL.md) — and the task-level findings are matured into documentation a future reader can follow, rather than left as a scattered dev log. Only then does the work ship, by PR or merge. The result is that what lands on your base branch is coherent, reproducible, and protected, instead of a pile of single-shot outputs that no one can later reconstruct.
