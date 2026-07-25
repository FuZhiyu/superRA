---
title: "Delete Rule-Recitation Canaries"
status: revise
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

## Review Notes

1. **MAJOR — Test documentation still advertises evidence paths deleted by this
   commit.** The detailed stage/domain sections still say fixture artifacts
   satisfy canaries and explicitly claim Codex artifact-list canaries
   ([README.md:100](../../../../tests/harness-instruction-following/README.md#L100),
   [README.md:119](../../../../tests/harness-instruction-following/README.md#L119));
   the evidence-policy section still says `evaluate_canary` scans artifact
   fields ([README.md:175](../../../../tests/harness-instruction-following/README.md#L175));
   and the CI-boundary section still lists `always_loaded_live.py` as a gated
   Python live entry even though that module now ends after its static checker
   ([README.md:191](../../../../tests/harness-instruction-following/README.md#L191),
   [always_loaded_live.py:38-44](../../../../tests/harness-instruction-following/always_loaded_live.py#L38-L44)).
   The supporting research note likewise retains the deleted Claude behavioral
   canary claim
   ([load-testing-research.md:23](../../../../tests/harness-instruction-following/references/load-testing-research.md#L23)).
   Reconcile these test documents with the command-only/schema-only evidence
   that remains; this is also required to make the task's `## Results` claim
   that the documentation stopped making these claims accurate.
