---
title: "Document Matrix And CI Boundary"
status: implemented
depends_on:
  - 03-claude-live-smoke
  - 04-codex-live-smoke
  - 06-ci-safe-contract-tests
  - 07-orchestrator-behavior-smoke
tags: []
created: 2026-06-19
---

## Objective

Document the final instruction-following test matrix and make the CI/manual boundary hard to miss.

The documentation should state:

- Which requirements are covered by static CI checks, fixture/parser unit tests, hook unit tests, and manual live harness tests.
- How to run the Claude smoke on Haiku and how to override the model.
- How to run the Codex smoke with `CODEX_MODEL`.
- How to run the orchestrator-behavior smoke for `superimplement`, what dispatch evidence is expected in each harness, and when a harness-supported fallback is acceptable.
- Which behaviors are intentionally not tested through model prose or live assertions because they are subjective or unobservable.
- Why live tests are opt-in and excluded from CI.

## Planner Guidance

Prefer a README in `tests/harness-instruction-following/`. If a top-level test README already exists and is more discoverable, add a short pointer there rather than duplicating the full matrix.

Before closing this task, verify the default CI command path does not invoke the live scripts.

## Results

Elaborated the seeded index at [tests/harness-instruction-following/README.md](../../../../../tests/harness-instruction-following/README.md) into the full instruction-following test matrix, rather than creating a second doc — there is no more-discoverable top-level test README to point at (the only other test README is the unrelated `tests/claude-code/README.md`), so the single README here is the discoverable home per the planner guidance.

**What the README now documents:**

- **Four-layer coverage matrix** mapping each agent-interface requirement to its static CI check, fixture/parser unit test, hook unit test, and manual live smoke, with file-line citations to the specific test functions. The layers were grounded in the actual files: static checks in [test_contract.py](../../../../../tests/harness-instruction-following/test_contract.py), fixture/parser unit tests in [test_bundle_fixture.py](../../../../../tests/harness-instruction-following/test_bundle_fixture.py) and [test_transcript_assertions.py](../../../../../tests/harness-instruction-following/test_transcript_assertions.py), the hook-registry assertion inside `test_contract.py`, and the three live smokes.
- **How to run each smoke** including the model controls: Claude defaults to `CLAUDE_MODEL=haiku` with a `CLAUDE_MODEL` override example; Codex uses `CODEX_MODEL` (no canonical cheapest model, falls back to the Codex CLI default); orchestrator smoke per harness via `HARNESS=claude|codex`.
- **Expected orchestrator dispatch evidence per harness** (Claude `Task`/`Agent` event with `subagent_type`; Codex `spawn_agent(agent_type=...)`) and exactly when the documented-exception fallback is acceptable — a single event must name a direct-mode switch with reviewer preservation AND one of the three documented exceptions (no harness subagent support, explicit user override, documented triviality); a fabricated reason fails.
- **Intentionally-not-tested behaviors** with reasons, grounded in the `load_contract.json` static findings: per-skill load into context (no structural skill-load event — SF-style limitation), generated prose quality (out of scope), direct-mode policy beyond the documented signal (SF004), terminology drift (SF002/SF001), and complete Codex shell-mutation enforcement (SF003).
- **Why live tests are opt-in and CI-excluded** — cost, credential dependency, and non-determinism, with the deterministic value already covered by the CI-safe layers.

**CI-boundary verification (required before closing):**

- `pytest tests/harness-instruction-following --collect-only` collects 24 Python test functions and **0** `.sh` entries — the live shell smokes are never collected or invoked by the default pytest path.
- Full default run is green: `24 passed`.
- Each live script, invoked bare without `RUN_LIVE_HARNESS=1`, prints `SKIP` and exits **0** (confirmed for all three: claude, codex, orchestrator), so even an accidental CI wiring would no-op rather than make a model call.
- The only committed CI workflow is [.github/workflows/docs-site.yml](../../../../../.github/workflows/docs-site.yml) (docs-site build/deploy); it runs `docs/build_site.sh`, not pytest or the live scripts, so it cannot invoke the smokes either.

`check_markdown.py` reports the README clean (no broken math/operator patterns).
