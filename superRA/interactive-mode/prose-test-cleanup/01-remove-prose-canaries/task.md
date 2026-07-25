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

Removed rule-recitation outputs from the always-loaded, stage-load, and
domain-load harness families:

- Always-loaded coverage now combines role-frontmatter declarations, an observed
  role mutation, exact schema/task/path identity, zero on-demand loads on Claude,
  and actual task-read/markdown-check command executions on Codex
  ([always_loaded_live.py:34-129](../../../../tests/harness-instruction-following/always_loaded_live.py#L34-L129),
  [test_always_loaded_live.py:42-136](../../../../tests/harness-instruction-following/test_always_loaded_live.py#L42-L136)).
- Stage fixtures now encode ordered load kinds, skill IDs, and the
  planning-review reference path; Claude still requires every `Skill`/`Read`
  event before the first mutation
  ([stage_loads_live.py:62-176](../../../../tests/harness-instruction-following/stage_loads_live.py#L62-L176),
  [test_stage_loads_live.py:448-483](../../../../tests/harness-instruction-following/test_stage_loads_live.py#L448-L483)).
- Domain fixtures now encode only the schema and ordered matched skill IDs,
  including every multi-domain match; Claude still requires all matching
  `Skill` events before mutation
  ([domain_loads_live.py:57-133](../../../../tests/harness-instruction-following/domain_loads_live.py#L57-L133),
  [test_domain_loads_live.py:237-270](../../../../tests/harness-instruction-following/test_domain_loads_live.py#L237-L270)).
- Harness documentation and `load_contract.json` now state the Codex limitation
  honestly: Codex emits no stage/domain load-by-name event, so those artifacts
  preserve schemas, IDs, kinds, and paths without claiming that authored prose
  proves a body load
  ([README.md](../../../../tests/harness-instruction-following/README.md),
  [load_contract.json](../../../../tests/harness-instruction-following/load_contract.json)).

Red-green verification:

- Red: the three replacement structural tests failed against the old fixtures
  (`3 failed`) because the artifacts still contained rule-recitation fields.
- Green: the targeted always/stage/domain suite passed (`59 passed`).
- Broader verification: the complete harness suite passed (`138 passed`) with
  `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with
  'uvicorn[standard]' --with watchfiles --with httpx python -m pytest
  tests/harness-instruction-following`.
- A scoped audit found none of the removed instruction phrases or old artifact
  fields in the live modules, their tests/docs, or the three fixture families.

## Review Notes

1. **MAJOR** — The old always-loaded exact-prose oracle still exists in the shared live-harness layer, so the stated “no expected artifact or assertion recites a skill rule” success condition and scoped-audit result are false. `BehavioralCanarySpec` still stores a human rule plus a regex and `check_behavioral_canary` still grades assistant prose against it ([sdk_load_evidence.py:513-570](../../../../tests/harness-instruction-following/sdk_load_evidence.py#L513-L570)); its unit tests still recite and assert the `report-in-markdown` line-anchor rule verbatim ([test_sdk_load_evidence.py:310-350](../../../../tests/harness-instruction-following/test_sdk_load_evidence.py#L310-L350)). The live runner also retains answer-capture plumbing documented as existing solely for that removed task-10 introspection canary ([sdk_load_harness.py:240-253](../../../../tests/harness-instruction-following/sdk_load_harness.py#L240-L253), [sdk_load_harness.py:283-291](../../../../tests/harness-instruction-following/sdk_load_harness.py#L283-L291)). Remove the prose-grading API, its exact-rule tests, and now-unused capture path/documentation (or replace them with structured evidence if another real caller requires it), then repeat the repository audit rather than limiting it to the three renamed live modules.

2. **MAJOR** — The Codex support layer retains the artifact-token route that Planner Guidance explicitly requires deleting, and the replacement “actual command” evidence is only substring matching. `CanarySpec.in_artifact_field` and `evaluate_canary` still accept a sentinel artifact value as proof that a skill body loaded ([codex_load_evidence.py:67-89](../../../../tests/harness-instruction-following/codex_load_evidence.py#L67-L89), [codex_load_evidence.py:126-184](../../../../tests/harness-instruction-following/codex_load_evidence.py#L126-L184)), with tests preserving that obsolete path ([test_codex_load_evidence.py:66-129](../../../../tests/harness-instruction-following/test_codex_load_evidence.py#L66-L129)). Meanwhile the always-loaded smoke flattens events to strings and passes them to that same substring checker ([check_always_loaded_smoke.py:41-50](../../../../tests/harness-instruction-following/check_always_loaded_smoke.py#L41-L50)); commands such as `printf './superRA/superra task read always-loaded-task'` and `rg check_markdown.py ...` therefore pass without executing either required tool, and exit status is discarded. Remove the unused artifact-field branch and replace the command canaries with structured command-execution predicates that identify the intended executable/arguments (and successful outcome where available), with red tests for echo/search mentions and failed executions.

3. **MAJOR** — `load_contract.json` still overstates LC001’s live evidence: it says the live transcript “shows the role loads/reads both” always-loaded skills before edits, while the recorded Claude evidence is frontmatter plus a mutation/zero on-demand loads and the Codex evidence is two command events ([load_contract.json:21-44](../../../../tests/harness-instruction-following/load_contract.json#L21-L44)). Neither harness exposes the claimed load/read event, as the updated README correctly explains. Rewrite `expected_evidence` to name only the structural and observable channels actually asserted, so the compact contract agrees with `covered_by` and does not preserve an unsupported body-load claim.
