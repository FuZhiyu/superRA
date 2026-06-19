---
title: "Add Codex Live Smoke"
status: not-started
depends_on:
  - 06-ci-safe-contract-tests
tags: []
created: 2026-06-19
---

## Objective

Add an opt-in Codex live smoke test that runs the same bundled fixture through the cheapest/dumbest configurable Codex path and verifies structural evidence of required loading.

The script should:

- Be manual-only and disabled unless an explicit environment gate such as `RUN_LIVE_HARNESS=1` is set.
- Use `CODEX_MODEL` when provided and document that the repo has no current canonical cheapest Codex model.
- Follow the existing temporary-profile pattern in `tests/hooks/test-codex-e2e-cli.sh`: `codex exec --json --ephemeral --skip-git-repo-check`, temporary hook config, and temporary workspace.
- Ask the agent to perform the same bundled sentinel-backed mock task used by the Claude smoke.
- Keep the mock task intentionally shallow: no real code implementation, no dependency installation, and no project test run.
- Parse Codex JSONL with the shared parser and fail if `superra task read <path>` or required file-read evidence is absent or happens after a file-change event.
- Keep any Codex-specific hook or profile setup isolated in the live script.

## Planner Guidance

Prefer the single bundled scenario shared with the Claude script before adding a broader matrix. If Codex JSONL does not expose enough file-read evidence for a particular requirement, make that limitation explicit and assert the available command/file-change ordering instead.

## Results
