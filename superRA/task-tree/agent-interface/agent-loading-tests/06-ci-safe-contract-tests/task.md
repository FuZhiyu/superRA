---
title: "Add CI-Safe Contract Tests"
status: not-started
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
- `superra task read` fixture behavior: ancestor sentinels, target body, unresolved comment sentinel, and dependency status/title are visible; dependency `## Results` sentinel is not inherited.
- Parser sample tests: synthetic or committed sample Claude/Codex transcript events prove the bundled parser catches missing, late, and correctly ordered `superra task read` evidence across multiple required reads in one run.
- Fixture cheapness: the bundled live fixture's assigned task is a mock sentinel-collection task that writes one small JSON artifact and does not request package installation, real code implementation, project tests, or broad repository exploration.

## Planner Guidance

Prefer `tests/harness-instruction-following/test_contract.py` plus fixture data over extending large shell scripts. Test the bundled scenario as the primary contract case, then add smaller parser/unit cases only where they make failures easier to diagnose. If existing hook tests already cover one requirement, add a small assertion or README pointer rather than duplicating the whole hook payload.

Do not add live harness commands to CI. These tests should run under the same local pytest path used for other repository tests, or be easy to include there later without credentials.

## Results
