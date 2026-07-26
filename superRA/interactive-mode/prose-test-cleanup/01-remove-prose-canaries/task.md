---
title: "Delete Rule-Recitation Canaries"
status: approved
depends_on:  []
---

## Objective

Delete authored instruction phrases and model rule recitation as expected outputs from always-loaded, stage-load, and domain-load harnesses. Retain existing schema, skill/path identity, event-order, dispatch, and mutation checks. Do not add replacement execution, parsing, or evidence machinery. Success: the live suites perform no additional work, the affected test code shrinks, and no expected artifact asks the model to repeat a skill rule.

## Planner Guidance

Audit inventory: always-loaded, stage-load, and domain-load live modules, tests, fixtures, and expected JSON. Delete only recitation/artifact-token paths that exist to prove wording. Existing behavioral evidence stays; missing evidence does not justify a new harness.

## Results

Removed rule-recitation oracles from the always-loaded, per-stage, and
per-domain harness families without adding any execution:

- The always-loaded coverage now retains role-frontmatter declarations, the
  existing Codex task-read and markdown-check command events, and the exact
  schema-only artifact
  ([always_loaded_live.py:2-44](../../../../tests/harness-instruction-following/always_loaded_live.py#L2-L44),
  [check_always_loaded_smoke.py:35-58](../../../../tests/harness-instruction-following/check_always_loaded_smoke.py#L35-L58)).
- Deleted the Claude prose-introspection prompt, answer capture, rule-regex
  evaluator, and their tests. The shared SDK harness still records the existing
  `Skill`, `Read`, and edit ordering evidence used by stage/domain coverage
  ([sdk_load_evidence.py](../../../../tests/harness-instruction-following/sdk_load_evidence.py),
  [sdk_load_harness.py](../../../../tests/harness-instruction-following/sdk_load_harness.py)).
- Stage and domain fixtures now emit only stable schema and identity fields;
  existing Claude load-by-name, reference-path, multi-domain completeness, and
  before-edit ordering checks remain
  ([stage_loads_live.py:61-130](../../../../tests/harness-instruction-following/stage_loads_live.py#L61-L130),
  [domain_loads_live.py:57-130](../../../../tests/harness-instruction-following/domain_loads_live.py#L57-L130),
  [test_stage_loads_live.py:429-436](../../../../tests/harness-instruction-following/test_stage_loads_live.py#L429-L436),
  [test_domain_loads_live.py:227-238](../../../../tests/harness-instruction-following/test_domain_loads_live.py#L227-L238)).
- Updated the harness contract and documentation to stop claiming Codex
  stage/domain load-by-name evidence or Claude prose-introspection evidence
  ([load_contract.json](../../../../tests/harness-instruction-following/load_contract.json),
  [README.md](../../../../tests/harness-instruction-following/README.md)).

Verification:

- Focused always-loaded/stage/domain evidence suite: `103 passed` in `1.12s`.
- Python compile and JSON parse checks passed.
- Scoped search found no remaining behavioral-canary API, answer-capture path,
  artifact-field canary, stage/domain recitation field, or introspection prompt.
- Test/fixture/documentation diff before this task-file update: 175 insertions,
  1,424 deletions; no production file changed.

Revision:

- Reconciled the harness README and research note with the surviving Claude
  `Skill`/`Read` evidence, Codex command evidence, and static schema/frontmatter
  checks; removed stale artifact-canary and Python live-gate claims
  ([README.md:98](../../../../tests/harness-instruction-following/README.md#L98),
  [README.md:175](../../../../tests/harness-instruction-following/README.md#L175),
  [load-testing-research.md:23](../../../../tests/harness-instruction-following/references/load-testing-research.md#L23)).
- The scoped stale-claim search is clean; the focused revision tests passed
  `15/15`, and the full suite passed `899` tests with four expected warnings.
- Final revision: corrected the stage-load test module's docstring to describe
  only the surviving Claude evaluator, read-path matching, and Codex
  schema/stage-identity fixture check
  ([test_stage_loads_live.py:2](../../../../tests/harness-instruction-following/test_stage_loads_live.py#L2)).
  The scoped stage-canary search and Python compilation passed; the module's
  test suite passed `24` tests in `0.05s`.
