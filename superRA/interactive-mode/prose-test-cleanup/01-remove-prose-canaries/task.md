---
title: "Remove Prose Canaries from Live Load Harnesses"
status: approved
depends_on:  []
---

## Objective

Remove authored instruction phrases as expected outputs from always-loaded, stage-load, and domain-load live/fixture harnesses. Preserve behaviorally meaningful evidence: actual skill-load/dispatch/tool events, command execution, file mutations, schemas, and structured identities. Update affected fixtures, expected JSON, harness documentation, and tests. Success: no expected artifact or assertion recites a skill rule; replacement structural/behavioral checks pass with red-green evidence.

## Planner Guidance

Audit inventory: always_loaded_live and its tests/fixture; stage_loads_live and protection/sync/integration/planning-review/maturation fixtures; domain_loads_live and econ/theory/writing/slide/multi-domain fixtures. Delete artifact-token paths that exist only to recite skill concepts; strengthen actual command/tool evidence where available.

## Results

Removed rule-recitation outputs and grading paths from the always-loaded,
stage-load, and domain-load harness families:

- Always-loaded coverage combines role-frontmatter declarations, an observed
  role mutation, exact schema/task/path identity, and zero on-demand loads on
  Claude. The retired assistant-answer capture and regex prose grader have no
  remaining caller or storage field
  ([sdk_load_evidence.py:95](../../../../tests/harness-instruction-following/sdk_load_evidence.py#L95),
  [sdk_load_harness.py:238](../../../../tests/harness-instruction-following/sdk_load_harness.py#L238)).
- Codex command evidence now parses `command_execution` records, matches the
  exact executable and ordered non-path arguments, and requires a completed
  zero-exit outcome. Only explicitly identified path arguments use suffix
  normalization. Mentions through `printf` or `rg` do not satisfy the predicate
  ([codex_load_evidence.py:62](../../../../tests/harness-instruction-following/codex_load_evidence.py#L62),
  [always_loaded_live.py:116](../../../../tests/harness-instruction-following/always_loaded_live.py#L116)).
- Stage fixtures preserve ordered load kinds, skill IDs, and the
  planning-review reference path. Domain fixtures preserve only the schema and
  ordered matched skill IDs, including every multi-domain match
  ([stage_loads_live.py:62](../../../../tests/harness-instruction-following/stage_loads_live.py#L62),
  [domain_loads_live.py:57](../../../../tests/harness-instruction-following/domain_loads_live.py#L57)).
- LC001 now lists only the channels the harness actually observes: source and
  frontmatter structure, Claude mutation with zero on-demand loads, successful
  Codex command executions, and exact artifact identities
  ([load_contract.json:21](../../../../tests/harness-instruction-following/load_contract.json#L21)).

Verification:

- Red: the new command-evidence tests failed during collection because the old
  layer exposed no `CommandSpec`, `CommandEvidenceReport`, structured extractor,
  or predicate evaluator (`2 errors`).
- Green: the focused Codex, always-loaded, SDK, and contract suite passed
  (`66 passed`).
- Second-round red: focused start-only and path-suffixed non-path argument tests
  both failed under the prior matcher (`2 failed`).
- Second-round green: the focused Codex and always-loaded suite passed
  (`34 passed`).
- Broader verification: the complete harness suite passed (`139 passed`) with
  `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with
  'uvicorn[standard]' --with watchfiles --with httpx python -m pytest
  tests/harness-instruction-following`.
- A repository-wide API audit found no remaining `BehavioralCanarySpec`,
  `check_behavioral_canary`, assistant-answer capture path, `CanarySpec`,
  artifact-field evaluator route, flattened-command extractor, or associated
  finding codes outside these historical review notes.
