---
title: "Add Claude Live Smoke"
status: approved
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

Added the opt-in Claude live smoke plus the shared infrastructure the Codex (04) and orchestrator (07) smokes reuse.

- [tests/harness-instruction-following/claude-live-smoke.sh](../../../../../tests/harness-instruction-following/claude-live-smoke.sh) — gated on `RUN_LIVE_HARNESS=1`; defaults to `CLAUDE_MODEL=haiku` with override; runs `claude -p` with the in-tree plugin dir, `--output-format=stream-json --include-hook-events --verbose`, a throwaway workspace, and `--no-session-persistence`. Records `total_cost_usd` (printed, never asserted).
- [tests/harness-instruction-following/live_smoke_lib.sh](../../../../../tests/harness-instruction-following/live_smoke_lib.sh) — shared setup: `require_live_gate` (documented no-op when the gate is unset), `seed_workspace` (copies the committed `bundle-two-tasks` `superRA/` + `markers/` into a temp workspace and writes a `superRA/superra` wrapper forwarding to the live task-tree CLI — does **not** copy `expected/` so the agent cannot crib the answer), and `smoke_task_prompt` (the single bundled mock task: two `superra task read` calls, three marker reads, dependency-result exclusion, one JSON write — no code, installs, or test runs).
- [tests/harness-instruction-following/check_loading_smoke.py](../../../../../tests/harness-instruction-following/check_loading_smoke.py) — shared evaluator reusing `transcript_assertions.py`: requires both task reads and all three marker reads before the `loading-evidence.json` write, then compares the artifact to the committed `expected/loading-evidence.expected.json`.

**Mock scenario reuse:** the bundled fixture and `transcript_assertions.py` parser from 02, and the expected artifact, are reused — the scenario is not re-derived per script.

**Harness-evidence limitation (documented in the script header and README):** Claude stream-json exposes Bash/Read/Write tool events but no structural `Skill(...)` skill-load event the parser can tie to the manifest by name. Rather than assert something vacuous, the smoke asserts the strongest observables — task-read command events and marker Read events ordered before the artifact write, plus an artifact whose sentinel values can only be produced after reading the required context. Manifest/role-surface load expectations stay covered by the CI-safe contract tests (06); subagent dispatch is covered by 07.

**Verified without live credentials** (live model calls not run — no spend authorized in this session):
- Gate-off no-op: bare `bash claude-live-smoke.sh` prints SKIP and exits 0.
- `seed_workspace` wrapper resolves and runs `./superRA/superra task read` in the temp workspace, surfacing root/parent/primary/comment/dependency sentinels; the dependency `## Results` sentinel does not leak (0 matches).
- Evaluator green case: passes against the committed `samples/claude-stream.bundle.jsonl` with the expected artifact.
- Evaluator red cases all exit 1: task read after write, artifact never written, artifact with `dependency_results_excluded=false`.
- `bash -n` syntax-clean; `--harness` arg validation rejects bad input (exit 2).
- Full CI-safe suite still green: `pytest tests/harness-instruction-following` → 23 passed.

**Not run:** the live `claude -p` turn (requires logged-in CLI + API spend). The script is ready; running it is a manual step.
