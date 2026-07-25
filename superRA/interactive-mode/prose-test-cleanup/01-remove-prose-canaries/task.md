---
title: "Delete Rule-Recitation Canaries"
status: not-started
depends_on:  []
---

## Objective

Delete authored instruction phrases and model rule recitation as expected outputs from always-loaded, stage-load, and domain-load harnesses. Retain existing schema, skill/path identity, event-order, dispatch, and mutation checks. Do not add replacement execution, parsing, or evidence machinery. Success: the live suites perform no additional work, the affected test code shrinks, and no expected artifact asks the model to repeat a skill rule.

## Planner Guidance

Audit inventory: always-loaded, stage-load, and domain-load live modules, tests, fixtures, and expected JSON. Delete only recitation/artifact-token paths that exist to prove wording. Existing behavioral evidence stays; missing evidence does not justify a new harness.

## Results
