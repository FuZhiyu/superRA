---
title: "Document Matrix And CI Boundary"
status: not-started
depends_on:
  - 03-claude-live-smoke
  - 04-codex-live-smoke
  - 06-ci-safe-contract-tests
tags: []
created: 2026-06-19
---

## Objective

Document the final instruction-following test matrix and make the CI/manual boundary hard to miss.

The documentation should state:

- Which requirements are covered by static CI checks, fixture/parser unit tests, hook unit tests, and manual live harness tests.
- How to run the Claude smoke on Haiku and how to override the model.
- How to run the Codex smoke with `CODEX_MODEL`.
- Which behaviors are intentionally not tested through model prose or live assertions because they are subjective or unobservable.
- Why live tests are opt-in and excluded from CI.

## Planner Guidance

Prefer a README in `tests/harness-instruction-following/`. If a top-level test README already exists and is more discoverable, add a short pointer there rather than duplicating the full matrix.

Before closing this task, verify the default CI command path does not invoke the live scripts.

## Results
