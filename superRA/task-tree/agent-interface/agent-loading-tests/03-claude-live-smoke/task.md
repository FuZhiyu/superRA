---
title: "Add Claude Live Smoke"
status: not-started
depends_on:
  - 06-ci-safe-contract-tests
tags: []
created: 2026-06-19
---

## Objective

Add an opt-in Claude live smoke test that runs the bundled fixture through the cheapest/dumbest Claude agent path and verifies structural evidence of required loading.

The script should:

- Be manual-only and disabled unless an explicit environment gate such as `RUN_LIVE_HARNESS=1` is set.
- Default to `CLAUDE_MODEL=haiku`, with an override.
- Use the existing `claude -p` style from `tests/hooks/test-e2e-cli.sh`: plugin dir, stream JSON, hook events, verbose output, and a temporary workspace.
- Ask the agent to perform one compact bundled mock task that requires multiple `superra task read <path>` calls, reading a sentinel marker file, preserving dependency-result exclusion, and writing the evidence JSON artifact.
- Keep the mock task intentionally shallow: no real code implementation, no dependency installation, and no project test run.
- Parse the transcript with the shared bundled assertions and fail if required load/read events occur after an edit/write or never occur.
- Record cost/model metadata when available without asserting exact values.

## Planner Guidance

Keep the prompt short and operational. Do not ask the model to explain its compliance; ask it to produce the fixture artifact for the bundled scenario. Tell it the expected work is only sentinel collection plus one JSON write. If Claude exposes tool events for skill loading, assert them; if not, assert the strongest available observable evidence and document the limitation.

## Results
