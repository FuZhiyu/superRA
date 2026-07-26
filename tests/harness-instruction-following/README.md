# Harness Instruction-Following Tests

This suite checks one thing: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting? The scope is the agent-interface contract, not prose quality, so the tests assert structural observables — parsed manifest and tool-map tables, generated-agent drift, hook registries, transcript tool events, `superra task read` output, and an artifact whose values can only be produced after reading the required context — never generated prose.

Coverage splits across four layers. Static and fixture checks run in default CI;
the Claude and Codex live-harness layers drive real models and are opt-in.

## Coverage matrix

This matrix maps **every** load-contract entry LC001–LC023 from [load_contract.json](load_contract.json) to its covering test(s) and coverage layer. The layers are *static CI* (parse committed source/JSON, no model), *fixture* (deterministic local CLI/hook/evaluator unit test, no model), *live-claude*, and *live-codex* (real model calls, opt-in, gated on `RUN_LIVE_HARNESS=1`). The machine-readable `covered_by` field on each entry in `load_contract.json` carries the same mapping; this README is the human index and `load_contract.json` is the source of truth — `test_contract.py::test_every_load_contract_entry_carries_covered_by` keeps them from drifting.

**Read the Coverage-strength column literally.** "Live-claude verified" means a real Claude agent run confirmed the behavior during the 08–12 expansion. "Codex built, live-pending" means the Codex test exists and its evaluator is CI-tested on synthetic inputs, but no Codex live run has happened yet (no credentials). "Static/proxy-only" means the layer is the strongest available observable for that contract by harness limitation, not direct by-name evidence — it does not imply live coverage.

| LC | Area | Static CI | Fixture | Live-claude | Live-codex | Coverage strength |
|---|---|---|---|---|---|---|
| **LC001** | always-loaded skills (`using-superra` + `report-in-markdown`) | [test_always_loaded_live.py](test_always_loaded_live.py) (frontmatter contract) | [test_always_loaded_live.py](test_always_loaded_live.py) (command checks + artifact schema) | — | [always-loaded-codex-smoke.sh](always-loaded-codex-smoke.sh) | Static frontmatter coverage; Codex command-event smoke built, live-pending. |
| **LC002** | per-stage manifest loads (rollup) | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_stage_loads_live.py](test_stage_loads_live.py) (schema + stage IDs) | [stage_loads_live.py](stage_loads_live.py) | unavailable by name | **All 4 non-empty stages Claude live-verified** (see LC007–LC010). |
| **LC003** | per-domain manifest loads (rollup) | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_domain_loads_live.py](test_domain_loads_live.py) (schema + domain IDs) | [domain_loads_live.py](domain_loads_live.py) | unavailable by name | **All 4 domains + the multi-domain every-match rule Claude live-verified** (see LC011–LC014). |
| **LC004** | harness-adapter routing (Codex tool map) | [test_contract.py::…codex_tool_map_matches_contract](test_contract.py#L189) | — | — (Codex-only contract) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | Structured CI coverage parses the tool map. **Codex-only live row; built, live-pending.** |
| **LC005** | role sessions perform `superra task read` before edits | — | [test_transcript_assertions.py](test_transcript_assertions.py) ordering parser | [claude-live-smoke.sh](claude-live-smoke.sh) (task-read-before-edit) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Claude live-verified** via the loading-smoke ordering assertion. **Codex built, live-pending.** |
| **LC006** | generated `.codex/agents/*.toml` drift | [test_contract.py::…generated_agent_drift_check](test_contract.py#L209) (runs `sync_codex_agents.py --check`) | — | — | — | **Fully CI-covered; no live row by design.** |
| **LC007** | stage `planning-review` → `planning-review.md` | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_stage_loads_live.py](test_stage_loads_live.py) (Read-channel suffix matcher) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[planning-review]` | unavailable by name | **Claude live-verified** — the reference loads via `Read`. |
| **LC008** | stage `protection` → `result-protection` | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[protection]` | unavailable by name | **Claude live-verified.** |
| **LC009** | stage `sync` → `semantic-merge` | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[sync]` | unavailable by name | **Claude live-verified.** Author/reviewer reference selection is static-only. |
| **LC010** | stage `integration` → `refactor-and-integrate` | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[integration]` | unavailable by name | **Claude live-verified.** |
| **LC023** | stage `maturation` → `task-tree` + `superplan` (always; `writing` conditional) | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[maturation]` | unavailable by name | **Fixture-covered; Claude live-pending.** |
| **LC011** | domain `econ-data-analysis` | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[econ-data-analysis]` | unavailable by name | **Claude live-verified.** |
| **LC012** | domain `theory-modeling` (+ multi-domain) | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[theory-modeling]` + multi-domain events | unavailable by name | **Claude live-verified**, including both matching skill loads. |
| **LC013** | domain `writing` (+ multi-domain) | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[writing]` + multi-domain events | unavailable by name | **Claude live-verified**, including multi-domain membership. |
| **LC014** | domain `slide-design` | [test_contract.py::…manifest_tables_match_contract](test_contract.py#L164) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[slide-design]` | unavailable by name | **Claude live-verified.** |
| **LC015** | task-read ancestor context | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::…surfaces_context_without_dependency_results](test_contract.py#L267) | [claude-live-smoke.sh](claude-live-smoke.sh) (consumed-before-write proxy) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Fully fixture-covered** (deterministic surfacing). Live *consumption* proxied by the loading-smoke ordering, **Claude-verified**; **Codex built, live-pending.** |
| **LC016** | task-read unresolved comments | — | [test_bundle_fixture.py](test_bundle_fixture.py) | [claude-live-smoke.sh](claude-live-smoke.sh) (surfacing reachable; not an act-on-comment assertion) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Fully fixture-covered.** Whether the agent *acts on* a surfaced comment is **not separately live-asserted** (proxy-only). |
| **LC017** | task-read dependency status | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::…surfaces_context_without_dependency_results](test_contract.py#L267) | — | — | **Fully fixture-covered; no live row by design.** |
| **LC018** | dependency `## Results` non-inheritance | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::…surfaces_context_without_dependency_results](test_contract.py#L267) | [claude-live-smoke.sh](claude-live-smoke.sh) (`dependency_results_excluded` artifact field) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Fully fixture-covered** and additionally checked by the live artifact field. **Claude-verified; Codex built, live-pending.** |
| **LC019** | hook registries (Claude vs Codex events/matchers/commands) | [test_contract.py::…hook_registry_boundaries](test_contract.py#L231) | same test (wired commands) | static-only by design | static-only by design (SF003) | **Registry wiring fully CI-covered.** Live PostToolUse feedback is **not separately asserted** (static-only by design; Codex Bash coverage best-effort per SF003) — not a gap. |
| **LC020** | execution-mode contract + `superimplement` default | [test_contract.py](test_contract.py) (structured availability/disposition/seat execution and shared-resolver routing) | [test_resolve_role.py](../../skills/using-superra/scripts/test_resolve_role.py) (packaged discovery from a foreign project), [test_transcript_assertions.py](test_transcript_assertions.py) (interactive ordering + canonical-role resolution for both main-seat routes), [test_contract.py::…codex_orchestrator_sample](test_contract.py) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) (built) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) `HARNESS=codex` (built) | Availability, durable review disposition, seat execution, and both adapter routes are **static-covered**; packaged role discovery, interactive ordering, main-seat behavior, and default dispatch are **fixture-covered**. Orchestrator dispatch smoke is **built; its Claude live run was not part of the 08–12 expansion**, and Codex live is pending. |
| **LC021** | dispatch fields + status progression | — | [test_transcript_assertions.py](test_transcript_assertions.py), [test_contract.py::…parser_contract_samples](test_contract.py#L288) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) (built) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) `HARNESS=codex` (built) | Dispatch detection is **fixture-covered**. Dispatch fields and status progression are asserted by the orchestrator smoke (**built, live run pending both harnesses**). |
| **LC022** | Codex orchestration adapter (named-agent dispatch) | [test_contract.py::…codex_tool_map_matches_contract](test_contract.py#L189) | — | — (Codex-only contract) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) `HARNESS=codex` + [subagent_start_hook.py](subagent_start_hook.py) dispatch log (built) | Structured CI coverage parses the named-agent mappings. The SubagentStart log supersedes JSONL spawn detection (codex emits no `spawn_agent` item). **Codex-only; built, live-pending.** |

**Deferred-import isolation (CI regression guard).** [test_deferred_import_isolation.py](test_deferred_import_isolation.py) locks in that importing any live-harness module (`sdk_load_harness`, `stage_loads_live`, `domain_loads_live`, `always_loaded_live`) pulls neither `claude_agent_sdk` nor a codex-cli client into `sys.modules` and makes no model call — the SDK import stays deferred inside the live entry point. Task 08's reviewer verified this by hand; this test makes it permanent so the deferred-import boundary cannot silently regress onto the default CI path.

### Known coverage gaps and honest caveats

- **No Codex live run yet.** Every Codex live row is *built and CI-tested on synthetic inputs* but has not been executed against a real Codex agent (no credentials). These rows are marked "live-pending," not "verified."
- **Codex cannot report stage/domain loads by name.** Those rows retain structured manifest and artifact identity coverage but make no live Codex body-load claim.
- **Loading ≠ rule-compliance.** The suite checks load events and other structural evidence, not generated prose or full rule-following.
- **Sub-reference routing is static-only.** Within a loaded domain/stage skill, which secondary reference the agent picks (Review/Polish/Draft for `writing`, Beamer layout for `slide-design`, author/reviewer mode for `semantic-merge`) is verified statically, not by a live by-name assertion.
- **No LC0xx is uncovered.** All 23 entries carry at least static or fixture coverage; the rows where a layer is static/proxy-only (LC016 act-on-comment, LC019 live hook feedback, sub-reference routing) are marked explicitly above rather than left as silent omissions.

[load_contract.json](load_contract.json) is the compact source-of-truth audit behind this matrix: each entry lists source paths, triggers, expected evidence, `classification` (`ci_safe_static`, `ci_safe_fixture`, `manual_live_*`), and the `covered_by` mapping. Its `static_findings` block records terminology and boundary drift (SF001–SF004) that should become lint or follow-up issues rather than live-agent assertions.

### Layers in detail

**Static CI checks** parse committed structured surfaces — manifest, tool-map, availability-routing, and seat-assignment tables; role frontmatter; hook registries; generated-agent equality; and routed reference paths/headings. The generated-agent drift check runs `sync_codex_agents.py --check`, so a hand-edit of a `.codex/agents/*.toml` that diverges from its role spec fails CI. Authored instruction sentences and labels are not test oracles.

**Fixture / parser unit tests** exercise the real `task_read.py` against the committed `bundle-two-tasks` fixture, packaged canonical-role discovery from a foreign project, and the transcript parser against committed sample transcripts. The fixture tests confirm `superra task read` surfaces ancestor `## Objective` context, unresolved comments, and sibling dependency status, and that a dependency's `## Results` sentinel never leaks into the target's context. The parser tests confirm interactive task-update → question-tool → reviewer-dispatch ordering, canonical-role resolution → role load → opposite-seat dispatch for both main-seat routes, default orchestration dispatch, and artifact-diff behavior. Negative fixtures prove missing or reordered structural events fail without relying on generated prose.

**Hook unit test** asserts the Claude and Codex hook registries wire the expected events, matchers, and commands — Claude has `UserPromptSubmit/PreToolUse/PostToolUse` with a `Skill` PreToolUse matcher and the `ensure-using-superra` / `ensure-agent-orchestration` autoloads; Codex adds a `Stop` hook, drops the Claude-only `Skill` matcher and autoloads, and keeps `autoload-superra` / `merge-guard` / `task-hook`.

**Manual live smokes** drive a real Claude or Codex agent through the bundled fixture and assert structural transcript evidence with the shared parser. See below.

### Claude skill-load-by-name harness (Agent SDK, manual)

Claude's `claude -p` stream does not give skill-load-by-name evidence the shared parser can tie to the manifest, and filesystem `PreToolUse` hooks do not fire under `claude -p` (issue #40506). So on-demand skill loading is verified through the Python `claude-agent-sdk`: the harness **dispatches the real plugin role agent** (`superRA:implementer` / `superRA:reviewer`, present in the SDK init `agents` list) so the manifest-driven loads actually fire, and a `PreToolUse(matcher="Skill")` in-process hook records each on-demand skill by name and event index (including loads inside the dispatched subagent). There is no `InstructionsLoaded` hook; always-loaded skills are covered by the role-frontmatter contract.

- [sdk_load_evidence.py](sdk_load_evidence.py) — CI-safe evidence model + assertions. `SkillLoadEvidence` + `check_skills_loaded_before_first_edit` cover on-demand (`Skill`-tool) loads; `check_always_loaded_frontmatter` asserts both role specs declare both always-loaded skills. Never imports `claude-agent-sdk`; never makes a model call.
- [sdk_load_harness.py](sdk_load_harness.py) — the live runner. The **only** module that imports `claude-agent-sdk`, and the import is deferred into `run_skill_load_session`, so the default `pytest` path never touches it. Dispatches the real role agent, gated on `RUN_LIVE_HARNESS=1`, default `CLAUDE_MODEL=haiku`. Supply the SDK on the live path with `uv run --with claude-agent-sdk`.
- [test_sdk_load_evidence.py](test_sdk_load_evidence.py) — CI-safe unit tests for event capture, ordering, and the frontmatter contract.

The per-stage and per-domain live smokes call `run_skill_load_session` and assert on the returned evidence — they consume the harness, not raw SDK calls.

### Always-loaded skill live coverage (LC001, manual)

Both always-loaded skills (`using-superra`, `report-in-markdown`) are declared in each role's frontmatter. The deterministic test parses those declarations. Codex has no skill-load event, so its opt-in smoke retains the existing task-read and markdown-check command events plus the exact schema-only artifact.

[test_always_loaded_live.py](test_always_loaded_live.py) covers the frontmatter declarations, command evidence, and artifact schema. Run the Codex smoke:

```bash
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/always-loaded-codex-smoke.sh
```

Smoke-check the live path standalone:

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/sdk_load_harness.py
```

### Per-stage skill-load live coverage (LC002, LC007–LC010, LC023, manual)

Each non-empty workflow stage must load the skill(s) or reference the Skill-Load Manifest assigns it before stage action; the sole negative stage (`implementation`) must load no extra stage skill. One parametrized table ([stage_loads_live.py](stage_loads_live.py)::`STAGE_ROWS`) is the single source of truth — `planning-review → skills/superplan/references/planning-review.md`, `protection → result-protection`, `sync → semantic-merge`, `integration → refactor-and-integrate`, `maturation → task-tree + superplan` (always; `writing` conditional for prose-heavy maturation, not a guaranteed load) — so adding a future stage is a one-row change. `maturation` is the one positive stage that loads multiple skills, so its row carries a tuple of guaranteed skill names (`expected_skills`); the single-skill rows and the read-channel row are unchanged. One fixture body ([tests/fixtures/task-trees/stage-loads](../fixtures/task-trees/stage-loads)) is reused across every stage; only the dispatch `Stage:` line differs.

Two evidence channels, because the stage manifest entries load through different tools:

- **Stage skills** (`result-protection`, `semantic-merge`, `refactor-and-integrate`) load via the `Skill` tool, so 08's `PreToolUse(matcher="Skill")` hook records them by name — the same channel as the ordering smoke. The evaluator reuses 08's `SkillLoadEvidence`.
- **The `planning-review` reference** is a file loaded via `Read`, not the `Skill` tool, so the `Skill` hook cannot see it. Task 11 extends 08's harness additively with an opt-in `PreToolUse(matcher="Read")` hook (`run_skill_load_session(..., capture_reads=True)`) that records read paths into `SkillLoadEvidence.read_loads`; the evaluator matches the manifest reference path against the captured reads by path-segment suffix (the SDK payload carries the plugin-install absolute path, not the manifest-relative one). The hook is default-off so existing callers are unaffected, and `claude-agent-sdk` stays off the CI import path. The exact `Read` tool_input path key (expected `file_path`) is confirmed on the first live run.

Codex exposes no stage skill/reference load event. The committed artifacts retain only the schema and stage identity.

[test_stage_loads_live.py](test_stage_loads_live.py) drives the stage evaluator on synthetic inputs — green per stage (skill and read channels, including the multi-skill `maturation` stage requiring both guaranteed skills with `writing` left conditional), red (guaranteed stage skill never loaded; reference never read; load after the first edit; a maturation run missing one guaranteed skill), the negative case (no stage skill loaded → green; a stage skill — including a maturation skill — loaded on `implementation` → red over-load), and the read-path suffix matcher. The committed Codex artifacts retain schema and stage identity only. No model call, no SDK/codex-cli import. Run the live Claude per-stage load check (default `sonnet`, pass@k; only the orchestrator runs it — no network on the implementer path):

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/stage_loads_live.py
```

A stage that reliably does **not** load its manifest skill/reference is a real LC002/LC007–LC010 finding to record and escalate, not an assertion to relax.

**`--include-hook-events` audit.** Audited against CLI 2.1.183: it is a real, documented flag ("Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)"), not a no-op — it surfaces hook lifecycle events such as the `UserPromptSubmit` autoloads. It does not make filesystem `PreToolUse` hooks fire under `claude -p`, so it gives no skill-load-by-name evidence; that is what the Agent SDK harness above provides. The existing `claude-live-smoke.sh` / `orchestrator-live-smoke.sh` keep the flag for debugging visibility and do not assert on the extra events.

### Per-domain skill-load live coverage (LC003, LC011–LC014, manual)

A domain-worded fixture task must load its domain skill before domain action, and a dispatch whose wording matches more than one domain must load **every** matching domain (the manifest requires loading every matching domain, not just the first). One parametrized `{domain_skill, trigger_wording}` table ([domain_loads_live.py](domain_loads_live.py)::`DOMAIN_ROWS`) is the single source of truth — `econ-data-analysis`, `theory-modeling`, `writing`, `slide-design` — with trigger wording kept close to the manifest Domain-table phrasing, so adding a future domain is a one-row change. One fixture body ([tests/fixtures/task-trees/domain-loads](../fixtures/task-trees/domain-loads)) is reused across every domain; only the dispatch wording differs.

All domain skills load through the `Skill` tool, so 08's `PreToolUse(matcher="Skill")` hook records them by name — the same channel as the per-stage skill rows. There is no Read-channel / reference case here (unlike 11's `planning-review` reference). The evaluator reuses 08's `SkillLoadEvidence` and 11's plugin-prefix-insensitive name matching (live loads are `superRA:`-qualified, e.g. `superRA:econ-data-analysis`; a raw compare against a bare expected name is a false negative — this was live-caught in 11). The **multi-domain** case (`theory-modeling` + `writing`: derive a result *and* write it up) is the load-bearing one — `evaluate_multi_domain_load` requires the **full** matching set, so loading only one of several (first-match instead of every-match) fails, naming each missing domain.

Codex exposes no domain skill-load event. The committed artifacts retain only the schema and ordered matched domain IDs.

[test_domain_loads_live.py](test_domain_loads_live.py) drives the domain evaluator on synthetic inputs — green per domain (including the `superRA:`-qualified live shape), red (domain skill never loaded; loaded after the first edit), and the multi-domain cases (all matching skills loaded → green; only one of several loaded → red; none loaded → red). The committed Codex artifacts retain schema and ordered matched-domain identities only. No model call, no SDK/codex-cli import. Run the live Claude per-domain load check (default `sonnet`, pass@k; only the orchestrator runs it — no network on the implementer path):

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/domain_loads_live.py
```

A domain that reliably does **not** load its skill — or the multi-domain case loading only one of several matching skills — is a real LC003/LC011–LC014 finding to record and escalate, not an assertion to relax.

## Running the CI-safe layers

```bash
uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following
```

This collects only the Python test modules; the live `*.sh` smokes are shell scripts and are not collected or invoked by pytest.

## Live smokes (manual-only, gated)

Each smoke gates on `RUN_LIVE_HARNESS=1` and is a documented no-op otherwise — a bare invocation prints `SKIP` and exits 0. Shared setup (workspace seeding, the bundled mock-task prompt, the orchestrator prompt) lives in [live_smoke_lib.sh](live_smoke_lib.sh); the Python evaluators ([check_loading_smoke.py](check_loading_smoke.py), [check_orchestrator_smoke.py](check_orchestrator_smoke.py)) reuse [transcript_assertions.py](transcript_assertions.py) and the committed expected artifact.

| Smoke | Entry | What it asserts |
|---|---|---|
| Claude loading | [claude-live-smoke.sh](claude-live-smoke.sh) | Both `superra task read` calls and all three marker reads occur before the `loading-evidence.json` write; the artifact matches the expected sentinels. Defaults to `CLAUDE_MODEL=haiku`. |
| Codex loading | [codex-live-smoke.sh](codex-live-smoke.sh) | Same contract through `codex exec --json --ephemeral`. Uses `CODEX_MODEL` when set; the repo prescribes no canonical cheapest Codex model. |
| Orchestrator | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) | `superimplement` dispatches an implementer then a reviewer subagent for the default-mode frontier. `HARNESS=claude` (default) or `HARNESS=codex`. |

```bash
# Claude loading smoke on the cheapest model (default haiku); override the model:
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/claude-live-smoke.sh
RUN_LIVE_HARNESS=1 CLAUDE_MODEL=sonnet bash tests/harness-instruction-following/claude-live-smoke.sh

# Codex loading smoke; set the model with CODEX_MODEL (no override = Codex CLI default):
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/codex-live-smoke.sh
RUN_LIVE_HARNESS=1 CODEX_MODEL=gpt-5-codex bash tests/harness-instruction-following/codex-live-smoke.sh

# Orchestrator smoke, per harness:
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/orchestrator-live-smoke.sh
RUN_LIVE_HARNESS=1 HARNESS=codex bash tests/harness-instruction-following/orchestrator-live-smoke.sh
```

The Claude smokes need a logged-in `claude` CLI; the Codex smokes need a logged-in `codex` CLI. Both run against a throwaway workspace and require a small API turn budget. The loading smokes record token cost as metadata but never assert on it.

### Expected orchestrator dispatch evidence per harness

The evaluator keys off the harness's own dispatch signal, never a prose claim:

- **Claude** exposes a subagent dispatch as a `Task` / `Agent` tool event carrying a `subagent_type` of `superRA:implementer` or `superRA:reviewer`. The smoke keys off these events.
- **Codex** exposes neither a `spawn_agent` item in the JSONL nor any skill-load event, so dispatch is observed out-of-band: a `SubagentStart` hook (one entry per agent type as the matcher) appends each dispatched agent type to a dispatch log via [subagent_start_hook.py](subagent_start_hook.py). The codex orchestrator smoke passes the log to the evaluator with `--dispatch-log` and asserts both `superra_implementer` and `superra_reviewer` appear in it. This supersedes JSONL-based dispatch detection for the codex path; the claude path is unchanged. The hook disambiguates by the agent-type payload field, not `session_id`.

The smoke passes when both an implementer and a reviewer dispatch are observed (claude: dispatch events; codex: SubagentStart log sentinels).

## Intentionally not tested through model prose or live assertions

Some behaviors are subjective or unobservable, so the suite covers them statically or not at all rather than asserting them on a model:

- **Whether a specific skill or reference was loaded into the model's context.** The loading smokes assert the strongest available structural observables — task-read and marker-read command events — while CI parses manifest mappings, role frontmatter, and artifact schemas. On **Claude**, the SDK harness ([sdk_load_evidence.py](sdk_load_evidence.py)) recovers on-demand skill and reference loads via in-process `Skill` and `Read` hooks. Codex exposes no skill-load event: its always-loaded smoke retains command evidence, while committed stage/domain artifacts establish only schema and identity.
- **The quality or correctness of generated prose.** Out of scope by design; the contract is the interface, not the writing.
- **Terminology drift** such as `Stage: protection` versus older `drift-test` wording (load-contract SF002), and root-level vs `hooks/` registry paths (SF001). These are static lint / follow-up findings, not live-agent behavior assertions.
- **Complete Codex shell-mutation enforcement.** Codex Bash hook coverage is best-effort (SF003), so hook assertions stay at registry-wiring and fixture-invocation level and the live tests do not depend on catching every shell mutation.

## Why live tests are opt-in and excluded from CI

Live smokes make real model calls: they cost money, depend on a logged-in CLI and network access, and are non-deterministic in a way a unit test is not. Putting them in default CI would make every run slow, flaky, and billable, and would fail in any environment without harness credentials. The deterministic value — every contract surface, the parser logic, and the task-read context behavior — already lives in the CI-safe layers, which run with no credentials and no model calls. The live smokes exist to confirm a real agent actually follows the contract on demand, so they gate behind `RUN_LIVE_HARNESS=1` and stay manual.

The default CI command path (`pytest` over `tests/harness-instruction-following`) collects only the Python test modules; it does not invoke the live `*.sh` scripts. A bare invocation of any live script without `RUN_LIVE_HARNESS=1` prints `SKIP` and exits 0, so even if a script were wired into a CI step it would no-op rather than make a model call.

## CI boundary (verified)

The CI/manual boundary holds on four checks, all confirmed in this worktree:

1. **Default `pytest` collects no live `.sh` scripts and imports no `claude-agent-sdk`.** `pytest` collects only `test_*.py` modules; the live `*.sh` smokes are shell scripts and are never collected. None of the collected modules imports `claude_agent_sdk` at top level — the only import lives deferred inside `sdk_load_harness.run_skill_load_session` (reached via `_run_session_async`), and [test_deferred_import_isolation.py](test_deferred_import_isolation.py) asserts importing every live-harness module leaves `claude_agent_sdk` and codex-cli out of `sys.modules`.
2. **Every live script SKIPs without `RUN_LIVE_HARNESS=1`.** [claude-live-smoke.sh](claude-live-smoke.sh), [codex-live-smoke.sh](codex-live-smoke.sh), [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh), and [always-loaded-codex-smoke.sh](always-loaded-codex-smoke.sh) each print `SKIP` and exit 0 when the gate is unset; the orchestrator-run Python live entries ([stage_loads_live.py](stage_loads_live.py), [domain_loads_live.py](domain_loads_live.py)) gate the same way and defer the SDK import behind the gate.
3. **The only committed workflow runs the docs build, not the live suite.** [`.github/workflows/docs-site.yml`](../../.github/workflows/docs-site.yml) runs `docs/build_site.sh`; no workflow runs `RUN_LIVE_HARNESS=1` or invokes the live smokes.
4. **The full CI-safe suite is green.** `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` passes with no model call and no credentials.
