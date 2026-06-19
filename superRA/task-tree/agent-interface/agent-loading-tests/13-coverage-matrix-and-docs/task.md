---
title: "Coverage Matrix + Contract Annotation"
status: not-started
depends_on:
  - 10-always-loaded-live
  - 11-stage-loads-live
  - 12-domain-loads-live
tags: []
created: 2026-06-19
---

## Objective

Close out the expansion by making coverage legible and confirming the CI/manual boundary still holds.

Deliverables:

- Extend the test-matrix README (the file [05-docs-ci-boundary](../05-docs-ci-boundary/task.md) created at `tests/harness-instruction-following/README.md`, not a new doc) to map **every** `LC001`–`LC022` contract from [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json) to its covering test(s) and coverage layer (static CI / fixture / live-claude / live-codex), including the new live rows for tasks 08–12 and the always-loaded/stage/domain mechanism.
- Annotate `load_contract.json`: add a `covered_by` field per entry naming the test(s)/scripts that now exercise it, so the audit and the suite stay in sync.
- Verify and record the CI boundary is unchanged: default `pytest` over the repo collects no live `.sh` scripts and does not import `claude-agent-sdk`; all live scripts SKIP without `RUN_LIVE_HARNESS=1`; the only committed workflow runs the docs build, not the live suite.

Success criteria: the README matrix accounts for LC001–LC022 with accurate layer/coverage per row; `load_contract.json` entries carry `covered_by`; the recorded CI-boundary checks pass.

### Constraints

- Reader-facing technical prose — load the `writing` domain skill.
- Do not duplicate the matrix across files; the README is the single index, `load_contract.json` carries the machine-readable `covered_by`.

## Planner Guidance

Where a contract remains static-only or proxy-only by harness limitation (e.g. codex skill-load), say so explicitly in the matrix rather than implying live-by-name coverage. If any LC0xx is still uncovered after 08–12, list it as a known gap, not a silent omission.
