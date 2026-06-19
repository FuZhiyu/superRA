---
title: "Per-Stage Skill Loads Live Coverage"
status: approved
depends_on:
  - 08-claude-sdk-load-harness
  - 09-codex-canary-and-dispatch-hook
tags: []
created: 2026-06-19
---

## Objective

Verify live, in both harnesses, that each non-empty workflow stage loads the skill/reference the Skill-Load Manifest assigns it before stage action (contracts LC002, LC007–LC010):

- `planning-review` → `skills/superplan/references/planning-review.md`
- `protection` → `result-protection`
- `sync` → `semantic-merge`
- `integration` → `refactor-and-integrate`

Also assert the negative: `implementation` and `documentation` carry **no** extra stage-skill expectation.

Deliverables:

- A parametrized set of stage fixtures (a minimal dispatch per stage carrying `Stage: <name>`), each with an assertion that the stage's required skill/reference is evidenced loaded — Claude via the 08 SDK skill-load hook, Codex via the 09 canary — before the stage's first action.
- The two negative cases (implementation/documentation) asserting no stage-skill load is required.

Success criteria: each of the four stages evidences its manifest skill/reference loaded on its triggering dispatch in both harnesses; the negative cases hold; a red case (stage skill not loaded) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses.
- Keep each stage fixture minimal — the test target is the stage→skill load, not stage work quality. Per the audit's SF002, assert `protection` from the manifest, not older `drift-test` wording.

## Planner Guidance

Parametrize over a `{stage, expected_skill}` table so adding a future stage is a one-row change. `planning-review` loads a reference *file*, the others load *skills* — the assertion helper should accept either a skill name or a reference path as the expected evidence. Reuse one fixture body across stages where only the dispatch `Stage:` line differs.

Two distinct evidence channels (this is load-bearing for the harness work):

- **Stage skills** (`result-protection`, `semantic-merge`, `refactor-and-integrate`) load via the `Skill` tool → caught by 08's `PreToolUse(matcher="Skill")` hook, tagged `subagent_skill_tool` (orchestrator-confirmed live that the hook fires for loads inside the dispatched subagent). Reuse it; do not re-implement.
- **The `planning-review` reference** is a file loaded via `Read`, not the `Skill` tool, so the `Skill` hook will NOT see it. Extend 08's harness additively with a `PreToolUse(matcher="Read")` hook that records read paths (default-off / opt-in so existing callers are unaffected, SDK import stays off the CI path), and assert the manifest reference path was read inside the dispatched agent. Confirm the exact `Read` tool_input path key on the first live run; the orchestrator runs the live path.

The live SDK dispatch is mildly nondeterministic — default `CLAUDE_MODEL=sonnet` (haiku was flaky at issuing the Task dispatch) and assert across a small pass@k window, not a single shot. A stage that reliably does **not** load its manifest skill/reference is a real LC002/LC007–LC010 finding to record and escalate, not an assertion to relax — this is the heart of what the task verifies.

## Results

CI-safe layer green (full harness suite: 110 passed). The live path is built and gated; the orchestrator runs it (no network on the implementer path). Exact live commands handed back below.

### Live-run outcome and the false-negative fix

The orchestrator ran the live path against the subscription. **The loading contract is healthy: every stage actually loads its manifest skill/reference** — `planning-review` read its reference, and `protection`/`sync`/`integration` each loaded their skill. This is **not** an LC002/LC007–LC010 loading-contract gap.

The live run exposed a **test bug (false negative)** instead. The `Skill` tool records a load plugin-qualified (`superRA:result-protection`), while the manifest table (`STAGE_ROWS`) names skills bare (`result-protection`), so `evaluate_stage_load`'s `skill not in evidence.loaded_skill_names` missed the real load:

```
FAIL: protection: required skill 'result-protection' never loaded (observed: ['superRA:result-protection', 'superRA:using-superra'])
```

Fix (correctness, not assertion-relaxing): skill-name matching now normalizes the leading `<plugin>:` prefix on **both** sides, so either spelling matches. `normalize_skill_name` in [sdk_load_evidence.py](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L170) strips one leading `<plugin>:` segment; `SkillLoadEvidence.loaded_skill_names`, `first_load_index`, and (via it) `loaded_before_first_edit` are now prefix-insensitive, and `check_skills_loaded_before_first_edit` normalizes the queried name. `loaded_skill_names_raw` preserves the unqualified-as-recorded set for diagnostics. `STAGE_ROWS` was **not** hardcoded to qualified names — normalizing is robust to how the manifest vs the `Skill` tool spell names. The negative direction is unchanged: a genuinely-absent skill is still reported missing.

### What was built

- **Single source of truth: the parametrized stage table** in [stage_loads_live.py](../../../../../tests/harness-instruction-following/stage_loads_live.py) (`STAGE_ROWS`). One row per stage with `{stage, expected_skill_or_refpath, channel, codex_canary}`; adding a future stage is a one-row change. Rows: `planning-review → skills/superplan/references/planning-review.md` (read channel), `protection → result-protection`, `sync → semantic-merge`, `integration → refactor-and-integrate` (skill channel), and the two negatives `implementation` / `documentation` (`channel=none`). Verified against [skills/using-superra/SKILL.md](../../../../../skills/using-superra/SKILL.md) manifest rows 71/73–75.

- **Two evidence channels (load-bearing).** Stage *skills* load via the `Skill` tool → caught by 08's existing `PreToolUse(matcher="Skill")` hook (reused, not re-implemented). The `planning-review` *reference* loads via `Read`, not `Skill`, so the `Skill` hook cannot see it. I extended 08's harness additively: a new opt-in `PreToolUse(matcher="Read")` hook recorded into a new `read_loads` channel on `SkillLoadEvidence`.
  - [sdk_load_evidence.py](../../../../../tests/harness-instruction-following/sdk_load_evidence.py): added `ReadLoadRecord`, `SkillLoadEvidence.read_loads` / `read_paths` / `first_read_index` / `read_before_first_edit`, a `_read_path_matches` path-segment-suffix matcher (absolute/plugin-install path matches the manifest-relative ref without substring false positives), and a `read_tool_events` param on `evidence_from_hook_records`.
  - [sdk_load_harness.py](../../../../../tests/harness-instruction-following/sdk_load_harness.py): `run_skill_load_session(..., capture_reads=True)` registers the Read hook. **Default-off** so every existing caller (the ordering smoke, the task-10 introspection canary) is unaffected; `claude-agent-sdk` import stays deferred and off the CI path. The Read tool_input path key is read defensively (`file_path` → `path` → `filename`), to be confirmed `file_path` on the first live run.

- **Claude evaluator** `evaluate_stage_load` (+ `evaluate_all_stage_loads`): skill channel = manifest skill loaded before first edit; read channel = manifest reference read before first edit; negative channel = **no** stage skill loaded (a stage-skill load on `implementation`/`documentation` is a real over-load finding). A non-stage skill (e.g. a domain skill) on a negative stage does not trip it.

- **Manual-only live entry** `run_claude_stage_canary` / `_main`: consumes 08's `run_skill_load_session` (with `capture_reads=True`), gated on `RUN_LIVE_HARNESS=1`, default `CLAUDE_MODEL=sonnet`, pass@k window (`attempts=3`). Bare run prints `SKIP` and exits 0 (confirmed).

- **Codex side: per-stage canaries** following the 09 convention — each stage's `CanarySpec` keys on a skill-unique discriminating concept its body prescribes (`drift test`, `intent conflict`, `minimum net diff`, `handoff-readiness`) recorded at artifact field `stage_canary`; negatives use `none`.

- **Fixtures** under [tests/fixtures/task-trees/stage-loads](../../../../../tests/fixtures/task-trees/stage-loads): one shared root + one shared leaf body (`stage-loads-task`) reused across stages (only the dispatch `Stage:` line differs), plus per-stage `expected/<stage>.expected.json` for fixture-sanity. The leaf task is superficial (read context, write one tiny JSON). Verified the wrapper `superra task read stage-loads-task` resolves from the workspace root.

- **CI-safe unit tests** [test_stage_loads_live.py](../../../../../tests/harness-instruction-following/test_stage_loads_live.py): table integrity vs the manifest; dispatch prompt carries the `Stage:` line; green per stage (both channels); red (skill never loaded, reference never read, load after first edit); negatives (green when no stage skill; red over-load); read-path suffix matcher (absolute matches, sibling/non-segment do not); per-stage Codex canary green/red; committed-artifact fixture sanity; CI-path imports no SDK/codex. **Plugin-qualified-vs-bare equivalence cases** (the live-run false-negative regression): a `superRA:`-qualified load satisfies a bare stage expectation across all four skill stages, the over-load check fires on a qualified negative-stage load, and a genuinely-absent skill is still rejected amid qualified observations. Read-channel and prefix-normalization evidence-model tests added to [test_sdk_load_evidence.py](../../../../../tests/harness-instruction-following/test_sdk_load_evidence.py) (`normalize_skill_name`, qualified↔bare symmetry, negative still rejects).

- **Docs**: [README.md](../../../../../tests/harness-instruction-following/README.md) coverage-matrix row + a per-stage detail section (two channels, the opt-in Read hook, the suffix matcher, the live command). README passes the markdown self-diagnose.

### Verification

- `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following/` → **110 passed**.
- `python3 tests/harness-instruction-following/stage_loads_live.py` (no gate) → `SKIP … opt-in`, exit 0.
- `python3 -c "import stage_loads_live"` → no `claude_agent_sdk` in `sys.modules` (CI-safe import boundary).

### Handoff: exact live commands (orchestrator runs; no network on implementer path)

```bash
# Claude per-stage skill-load canary (default sonnet, pass@k):
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/stage_loads_live.py
```

The first live run already confirmed: (a) the `Skill` hook fires for stage-skill loads inside the dispatched subagent (loads observed plugin-qualified, e.g. `superRA:result-protection`); (b) the new `Read` hook fires for the `planning-review` reference read. All four stages load their manifest skill/reference. The false-negative match bug (qualified-vs-bare) is fixed above, so the re-run should now PASS all four stages. The Codex per-stage canary runs through the 09 dispatch convention. A stage that reliably does not load its manifest skill/reference would be a real LC002/LC007–LC010 finding to escalate, not an assertion to relax.
