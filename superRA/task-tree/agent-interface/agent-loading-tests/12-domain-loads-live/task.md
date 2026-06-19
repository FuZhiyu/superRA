---
title: "Per-Domain Skill Loads Live Coverage"
status: implemented
depends_on:
  - 08-claude-sdk-load-harness
  - 09-codex-canary-and-dispatch-hook
tags: []
created: 2026-06-19
---

## Objective

Verify live, in both harnesses, that a domain-worded fixture task loads its domain skill (contracts LC003, LC011–LC014):

- `econ-data-analysis` — task wording about importing/cleaning/merging/regressing data
- `theory-modeling` — task wording about deriving/solving/proving
- `writing` — task wording about drafting/polishing reader-facing prose
- `slide-design` — task wording about creating/revising slides/Beamer

Include a **multi-domain** fixture whose wording matches more than one domain (e.g. derive a result *and* write it up) and assert **all** matching domain skills load, since the manifest requires loading every matching domain.

Deliverables:

- A parametrized set of domain fixtures (a minimal task whose objective text unambiguously triggers one domain) plus the multi-domain fixture, each with an assertion that the expected domain skill(s) are evidenced loaded — Claude via the 08 SDK skill-load hook, Codex via the 09 canary.

Success criteria: each domain skill is evidenced loaded on its triggering fixture in both harnesses; the multi-domain case loads all matching skills; a red case (domain skill not loaded on triggering wording) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses.
- Keep fixture tasks shallow — domain-triggering *wording* without requiring real domain work (no actual regression, proof, or deck). The target is the load, not the output.

## Planner Guidance

Parametrize over a `{domain_skill, trigger_wording}` table. The multi-domain case is the load-bearing one — it proves the "load every matching domain" rule, not just first-match. Keep trigger wording close to the manifest's own trigger phrasing so the test reflects the documented contract.

All domain skills load via the `Skill` tool → caught by 08's `PreToolUse(matcher="Skill")` hook, tagged `subagent_skill_tool` (orchestrator-confirmed live that the hook fires for loads inside the dispatched subagent). Reuse it; no Read-hook/reference case here (unlike task 11's `planning-review`).

Match skill names with the plugin-prefix normalization task 11 established: live loads are `superRA:`-qualified (e.g. `superRA:econ-data-analysis`), so a bare expected name like `econ-data-analysis` must still match — reuse 11's normalized matcher rather than a raw string compare, or every assertion is a false negative (this was a live-caught bug in 11). The live SDK dispatch is mildly nondeterministic — default `CLAUDE_MODEL=sonnet`, assert across a small pass@k window, not a single shot. A domain whose triggering wording reliably does **not** load its skill (or the multi-domain case loading only one of several matching skills) is a real LC003/LC011–LC014 finding to record and escalate, not an assertion to relax.

## Results

Per-domain skill-load live coverage built as a CI-safe core + manual live entry, consuming the 08 (Claude SDK) and 09 (Codex canary) harnesses and reusing task 11's machinery (the `STAGE_ROWS` table pattern, 08's `SkillLoadEvidence`, and `normalize_skill_name`).

**Module — [domain_loads_live.py](../../../../../tests/harness-instruction-following/domain_loads_live.py).** One parametrized `{domain_skill, trigger_wording}` table (`DOMAIN_ROWS`) is the single source of truth for the four domains; trigger wording is kept close to the manifest Domain-table phrasing (e.g. "import, clean, merge, and run a regression on a panel of economic data" for `econ-data-analysis`). All domain skills load through the `Skill` tool, so the evaluator reuses 08's `Skill`-hook evidence — no Read-channel case here (unlike 11's `planning-review` reference). Skill-name comparison goes through 11's `normalize_skill_name`, so a `superRA:`-qualified live load satisfies a bare expected name (the live-caught false-negative class from 11).

The **multi-domain** case is load-bearing: `MULTI_DOMAIN_SKILLS = ("theory-modeling", "writing")` with wording matching both (derive a result *and* write it up). `evaluate_multi_domain_load` requires the **full** matching set — loading only one of several (first-match instead of every-match) fails and names each missing domain. The single-domain `evaluate_domain_load` is a one-element delegate of the same checker.

**Codex side.** Per-domain `CanarySpec` rows (tokens `describe before transform`, `comparative statics`, `audience model`, `live communication` — each a discriminating concept from that domain's body). Because a multi-domain dispatch must emit several tokens at once, the canary is recorded in a **list** field `domain_canaries` (not a scalar). `domain_canary_in_artifact` / `evaluate_codex_multi_domain` check list membership; the scalar-field `evaluate_canary` in `codex_load_evidence.py` cannot express a multi-token artifact, hence the list helper. The Codex live dispatch is orchestrator-run per the 09 convention against the committed fixture + expected artifacts (same approach as 11 — no separate shell script).

**Fixtures — [tests/fixtures/task-trees/domain-loads](../../../../../tests/fixtures/task-trees/domain-loads).** One shared shallow leaf task ([domain-loads-task/task.md](../../../../../tests/fixtures/task-trees/domain-loads/superRA/domain-loads-task/task.md)) carries no domain of its own; only the dispatch wording differs across shots. The task asks only to read context and write a tiny `domain-loads-evidence.json` — no real domain work. Five committed expected artifacts (one per domain + multi-domain) under `expected/`.

**CI-safe tests — [test_domain_loads_live.py](../../../../../tests/harness-instruction-following/test_domain_loads_live.py)** (22 tests): green per domain (including `superRA:`-qualified shape); red (never loaded; loaded after first edit); multi-domain all-loaded → green, loaded-only-one → red, none-loaded → red; Codex artifact-list canaries green/red per domain and multi-domain; and a fixture-sanity check that every committed expected artifact satisfies its canary(s). No model call, no SDK/codex-cli import (asserted by `test_default_ci_path_never_imports_sdk_or_codex`).

**Verification.**
- New module: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following/test_domain_loads_live.py -q` → **22 passed**.
- Full harness suite: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following -q` → **132 passed** (no regression).
- Live entry no-op without the gate: `python3 tests/harness-instruction-following/domain_loads_live.py` → prints `SKIP`, exit 0, never imports the SDK.
- README self-check: `python3 skills/report-in-markdown/scripts/check_markdown.py tests/harness-instruction-following/README.md` → clean.

**Docs.** [README.md](../../../../../tests/harness-instruction-following/README.md) gains a coverage-matrix row and a "Per-domain skill-load live coverage (LC003, LC011–LC014, manual)" section describing the table, the multi-domain rule, the Codex list-canary, and the live command.

**Live handoff (orchestrator runs; no network on the implementer path).** I could not run the live dispatches. The exact Claude live command:

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/domain_loads_live.py
```

This dispatches one `superRA:implementer` per domain plus the multi-domain shot (default `CLAUDE_MODEL=sonnet`, pass@k=3) and asserts each domain's skill loads on its triggering wording and that the multi-domain wording loads **both** matching skills. A reliable non-load, or a multi-domain shot that loads only one matching skill, is a real LC003/LC011–LC014 loading-contract finding to escalate, not an assertion to relax. The Codex side is run by the orchestrator per the 09 canary convention against the committed `domain-loads` fixture and expected artifacts.
