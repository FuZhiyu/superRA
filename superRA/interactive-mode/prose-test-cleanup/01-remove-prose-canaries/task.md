---
title: "Remove Prose Canaries from Live Load Harnesses"
status: revise
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
  executable and ordered arguments, and rejects explicit nonzero outcomes.
  Mentions through `printf` or `rg` do not satisfy the predicate
  ([codex_load_evidence.py:62](../../../../tests/harness-instruction-following/codex_load_evidence.py#L62),
  [test_codex_load_evidence.py:49](../../../../tests/harness-instruction-following/test_codex_load_evidence.py#L49)).
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
- Broader verification: the complete harness suite passed (`137 passed`) with
  `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with
  'uvicorn[standard]' --with watchfiles --with httpx python -m pytest
  tests/harness-instruction-following`.
- A repository-wide API audit found no remaining `BehavioralCanarySpec`,
  `check_behavioral_canary`, assistant-answer capture path, `CanarySpec`,
  artifact-field evaluator route, flattened-command extractor, or associated
  finding codes outside these historical review notes.

## Review Notes

1. **MAJOR** — The structured Codex predicate still accepts evidence that does not establish a successful execution of the intended command. A matching start-only record with `exit_code=None` is classified as successful ([codex_load_evidence.py:138-157](../../../../tests/harness-instruction-following/codex_load_evidence.py#L138-L157)), so a truncated transcript can satisfy LC001 before the command completes; the new paired-event test covers a later explicit failure but not the start-only red case ([test_codex_load_evidence.py:126-149](../../../../tests/harness-instruction-following/test_codex_load_evidence.py#L126-L149)). Separately, `_path_arg_matches` applies suffix matching to every argument ([codex_load_evidence.py:98-122](../../../../tests/harness-instruction-following/codex_load_evidence.py#L98-L122)), so `./superRA/superra /tmp/task /tmp/read /tmp/always-loaded-task` incorrectly matches the required `task read always-loaded-task` vector. Require completed zero-exit evidence and exact matching for non-path arguments (with any intentional path normalization represented explicitly), then add red coverage for start-only records and path-suffixed non-path arguments.
   → implemented: replaced token/artifact and flattened-string routes with structured executable/argument/outcome predicates, including red coverage for `printf`, `rg`, nonzero completion, and start/completion event pairs ([codex_load_evidence.py:62](../../../../tests/harness-instruction-following/codex_load_evidence.py#L62), [test_codex_load_evidence.py:70](../../../../tests/harness-instruction-following/test_codex_load_evidence.py#L70)).
