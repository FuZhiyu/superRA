---
title: "result-protection"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

`result-protection` keeps your key results from moving unnoticed when later work refactors, merges, or reruns the code behind them. A refactor can pass every test while a headline coefficient slides from 0.42 to 0.31.

## Choose a guard per key result

- **Permanent documentation** — the result recorded in its permanent home. Often enough on its own.
- **Plus a drift test** — a check that reads the saved output and fails when the value leaves a tolerance. Worth it for a headline number.
  - Tolerances follow the quantity: a basis-point spread and a t-statistic get different bands, each with a stated reason.
  - Each test is proven to fail when the protected value is perturbed.

## Where you meet it

- **In INTEGRATE:** the [Protect stage](#/05-workflows/03-integrate) proposes what to keep and how to guard it; you choose.
- **Standalone:**
  - "pin the spread in `analysis/term-structure` and guard it, tolerance 1 bp"
  - "review the drift tests in `test/` against the current key results"

## A failing drift test waits for you

Later integration runs the drift tests, and a failure blocks until resolved. If the result really moved, that is a research decision; the agent updates the expectation only after you make it.

Drift tests register as check steps in the [reproduction graph](#/04-utility-skills/09-reproducibility). Details live in [result-protection](skills/result-protection/SKILL.md).
