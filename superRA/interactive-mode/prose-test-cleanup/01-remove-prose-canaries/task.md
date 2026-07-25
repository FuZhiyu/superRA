---
title: "Remove Prose Canaries from Live Load Harnesses"
status: implemented
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
