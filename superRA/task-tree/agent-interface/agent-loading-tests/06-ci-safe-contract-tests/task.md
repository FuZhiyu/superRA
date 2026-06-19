---
title: "Add CI-Safe Contract Tests"
status: approved
depends_on:
  - 01-load-contract-audit
  - 02-fixtures-and-parser
tags: []
created: 2026-06-19
---

## Objective

Implement the deterministic contract tests that do not call Claude, Codex, or any live model. These tests should make the load-contract audit executable and protect the file-loading rules that can be verified without agent behavior.

At minimum, add CI-safe assertions for:

- The Skill-Load Manifest in `skills/using-superra/SKILL.md`: always-loaded skills, stage rows, domain rows, and harness adapter pointers expected by the audit.
- Canonical and generated role surfaces: `agents/implementer.md`, `agents/reviewer.md`, direct-mode references, and `.codex/agents/*.toml` contain the required manifest-load and `superra task read` instructions.
- Generated Codex-agent drift: the checked-in generated surfaces match the generator output or the existing generator check remains covered.
- Hook registry boundaries: Claude hook config includes the hard loading gates expected for Claude; Codex hook config omits Claude-only gates and includes Codex-compatible autoload/task hooks.
- Workflow-orchestrator contract: `skills/superimplement/SKILL.md` states subagent mode as the default, requires `agent-orchestration` before dispatch, and preserves reviewer dispatch in direct mode; `skills/agent-orchestration/SKILL.md` contains canonical implementer/reviewer templates; Codex adapter text maps those dispatches to `superra_implementer` / `superra_reviewer`.
- `superra task read` fixture behavior: ancestor sentinels, target body, unresolved comment sentinel, and dependency status/title are visible; dependency `## Results` sentinel is not inherited.
- Parser sample tests: synthetic or committed sample Claude/Codex transcript events prove the bundled parser catches missing, late, and correctly ordered `superra task read` evidence across multiple required reads in one run.
- Fixture cheapness: the bundled live fixture's assigned task is a mock sentinel-collection task that writes one small JSON artifact and does not request package installation, real code implementation, project tests, or broad repository exploration.

## Planner Guidance

Prefer `tests/harness-instruction-following/test_contract.py` plus fixture data over extending large shell scripts. Test the bundled scenario as the primary contract case, then add smaller parser/unit cases only where they make failures easier to diagnose. If existing hook tests already cover one requirement, add a small assertion or README pointer rather than duplicating the whole hook payload.

Do not add live harness commands to CI. These tests should run under the same local pytest path used for other repository tests, or be easy to include there later without credentials.

## Results

Implemented deterministic CI-safe contract coverage in [test_contract.py](../../../../../tests/harness-instruction-following/test_contract.py#L81-L378). The tests do not call Claude, Codex, or live models; they parse committed source, run local fixture CLIs, and use the existing transcript parser helpers.

Coverage added:

- Load-contract audit indexing, Skill-Load Manifest stage/domain rows, always-loaded skills, and the generic harness-adapter reference pointer are asserted from committed files ([test_contract.py:81](../../../../../tests/harness-instruction-following/test_contract.py#L81)).
- Canonical role specs, direct-mode references, and checked-in Codex agent TOMLs are checked for Skill-Load Manifest and `superra task read <path>` instructions, plus generated-source headers ([test_contract.py:128](../../../../../tests/harness-instruction-following/test_contract.py#L128)).
- Codex generated-agent drift is protected by invoking the existing generator `--check` path from the contract suite ([test_contract.py:158](../../../../../tests/harness-instruction-following/test_contract.py#L158)).
- Claude and Codex hook registry boundaries are parsed statically: Claude retains hard loading gates, while Codex omits Claude-only gates and wires autoload, merge guard, task hook, and plan Stop hooks ([test_contract.py:180](../../../../../tests/harness-instruction-following/test_contract.py#L180)).
- Workflow-orchestrator dispatch contracts are asserted across `superimplement`, `agent-orchestration`, and the Codex adapter mapping to `superra_implementer` / `superra_reviewer` ([test_contract.py:216](../../../../../tests/harness-instruction-following/test_contract.py#L216)).
- The fixture `superra task read` behavior, parser ordering behavior, Codex orchestrator sample dispatches, and live-fixture cheapness constraints are covered in the same deterministic test module ([test_contract.py:240](../../../../../tests/harness-instruction-following/test_contract.py#L240)).

Verification:

- `uv run --with pytest python -m pytest tests/harness-instruction-following` passed: 23 tests.
- `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` passed: 7 tests.
- `bash tests/hooks/test-ensure-using-superra.sh` passed: 16 cases.
- `bash tests/hooks/test-ensure-agent-orchestration.sh` passed: 16 cases.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 cases.
