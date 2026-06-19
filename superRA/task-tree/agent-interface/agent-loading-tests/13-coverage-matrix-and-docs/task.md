---
title: "Coverage Matrix + Contract Annotation"
status: implemented
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

When recording the CI boundary, add a CI-safe regression test that locks in the deferred-import isolation — assert that importing `sdk_load_harness` (and the 09 codex harness) does not pull `claude_agent_sdk` / codex-cli into `sys.modules` and makes no model call. Task 08's reviewer verified this isolation manually; without a test it can silently regress.

## Results

All four deliverables landed and the full CI-safe suite is green: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → **136 passed** (was 132; +3 deferred-import isolation, +1 covered-by completeness). [README.md](../../../../../tests/harness-instruction-following/README.md) passes the markdown self-diagnose clean.

### 1. Coverage matrix — every LC001–LC022

Replaced the old behavior-grouped matrix in [tests/harness-instruction-following/README.md](../../../../../tests/harness-instruction-following/README.md) with a one-row-per-LC table mapping each contract to its static-CI / fixture / live-claude / live-codex covering test(s), plus a Coverage-strength column. A preamble states the README is the human index and `load_contract.json` is the source of truth (no duplicated matrix — per the no-duplication constraint).

Live facts recorded exactly as the orchestrator established them, no re-run:

- **Claude live-verified:** always-loaded (`using-superra` + `report-in-markdown`, by frontmatter autoload — zero `Skill`-tool loads is the expected signal); all 4 non-empty stages (planning-review via the `Read` channel; protection/sync/integration via the `Skill` tool); all 4 domains + the multi-domain every-match rule.
- **Codex:** every Codex row marked **"built, live-pending"** (no credentials yet) — not "verified."

A "Known coverage gaps and honest caveats" subsection records the required caveats: no Codex live run yet; the Codex always-loaded canary token appears in the fixture body (weak standalone proxy, backstopped by the Claude hook); loading ≠ rule-compliance; sub-reference routing (Review/Polish/Draft, Beamer layout, semantic-merge mode) is static-only; and that **no LC0xx is uncovered** — the proxy-only/static-only rows (LC016 act-on-comment, LC019 live hook feedback, sub-reference routing) are marked explicitly rather than omitted.

### 2. `load_contract.json` `covered_by` annotation

Added a `covered_by` block to all 22 LC entries in [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json), keyed by layer (`ci_safe_static`, `fixture_unit`/`ci_safe_fixture`, `manual_live_claude`, `manual_live_codex`) plus a `notes` line carrying the same honesty markers as the README. New CI-safe test [test_contract.py::test_every_load_contract_entry_carries_covered_by](../../../../../tests/harness-instruction-following/test_contract.py#L106) asserts every entry carries a populated `covered_by` consistent with its `classification` (so a `manual_live_both` entry must populate both single-harness layers), keeping the audit and suite in sync.

### 3. Deferred-import isolation regression test

[tests/harness-instruction-following/test_deferred_import_isolation.py](../../../../../tests/harness-instruction-following/test_deferred_import_isolation.py) (3 tests) locks in the isolation task 08's reviewer verified by hand: importing each live-harness module (`sdk_load_harness`, `stage_loads_live`, `domain_loads_live`, `always_loaded_live`) in a fresh subprocess pulls **neither** `claude_agent_sdk` **nor** a codex-cli client into `sys.modules`, and a structural check confirms the lone `claude_agent_sdk` import is indented inside a function body (deferred into `_run_session_async`, reached via `run_skill_load_session`), not at module top level. Empirically verified the leak set is empty before writing the test.

### 4. CI boundary — verified and recorded

Added a "CI boundary (verified)" section to the README with the four confirmed checks:

1. Default `pytest` collects only `test_*.py` (no `.sh` smokes) and imports no `claude_agent_sdk` — confirmed empirically (`sys.modules` leak set empty) and now guarded by the deferred-import test.
2. All live scripts SKIP without `RUN_LIVE_HARNESS=1` — confirmed: `claude-live-smoke.sh`, `codex-live-smoke.sh`, `orchestrator-live-smoke.sh`, `always-loaded-codex-smoke.sh` each print `SKIP` and exit 0.
3. The only committed workflow ([.github/workflows/docs-site.yml](../../../../../.github/workflows/docs-site.yml)) runs `docs/build_site.sh`, not the live suite — confirmed; no workflow sets `RUN_LIVE_HARNESS=1`.
4. The full CI-safe suite is green (136 passed, no model call, no credentials).
