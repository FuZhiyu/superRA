---
title: "Add Codex Live Smoke"
status: approved
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

Added the opt-in Codex live smoke running the same bundled mock task as the Claude smoke (03) through the cheapest configurable Codex path.

- [tests/harness-instruction-following/codex-live-smoke.sh](../../../../../tests/harness-instruction-following/codex-live-smoke.sh) — gated on `RUN_LIVE_HARNESS=1`; uses `CODEX_MODEL` via `--model` when set and documents in the header that the repo prescribes no canonical cheapest Codex model (defaults to the Codex CLI default). Follows the existing `tests/hooks/test-codex-e2e-cli.sh` pattern: `codex exec --json --ephemeral --skip-git-repo-check -C <workspace>`, a temporary `*.config.toml` Codex profile installing the superRA autoload + task-hook hooks against the in-tree scripts, and a throwaway seeded workspace. Codex-specific profile/hook setup is isolated inside this script.

**Shared reuse (from 03):** the bundled fixture + `transcript_assertions.py` parser (02), `live_smoke_lib.sh::seed_workspace` and `::smoke_task_prompt` (identical prompt text so both harnesses exercise the same scenario), the expected artifact, and `check_loading_smoke.py` (invoked with `--harness codex`). The mock scenario is not re-derived here.

**Harness-evidence limitation (documented in the script header and README):** Codex JSONL exposes `command_execution` and `file_change` items; task reads surface as `command_execution` running `superra task read <path>` and marker reads as read-tool/read-command events — the strongest available observables, which the shared parser keys off. Codex JSONL emits no structural skill-load event tied to the manifest by name, so manifest/role-surface load expectations stay covered by the CI-safe contract tests (06); subagent dispatch is covered by 07. The shared evaluator fails if a required task-read/marker-read is absent or happens after the artifact write.

**Verified without live credentials** (live model calls not run — no spend authorized in this session):
- Gate-off no-op: bare `bash codex-live-smoke.sh` prints SKIP and exits 0.
- `bash -n` syntax-clean.
- The shared evaluator (`check_loading_smoke.py --harness codex`) green/red behavior is verified under 03 (same code path; Codex JSONL parses through the same `parse_codex_jsonl`/`transcript_assertions` used for the orchestrator codex sample).
- `codex` CLI confirmed on PATH (`codex-cli 0.140.0`).

**Not run:** the live `codex exec` turn (requires logged-in CLI + model spend). The script is ready; running it is a manual step.
