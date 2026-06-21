# Harness Instruction-Following Tests

This suite checks one thing: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting? The scope is the agent-interface contract, not prose quality, so the tests assert structural observables — manifest and role-surface text, generated-agent drift, hook registries, transcript tool events, `superra task read` output, and an artifact whose values can only be produced after reading the required context — never generated prose.

Coverage splits across four layers. The first three run in default CI; the fourth drives a real model and is opt-in.

## Coverage matrix

This matrix maps **every** load-contract entry LC001–LC023 from [load_contract.json](load_contract.json) to its covering test(s) and coverage layer. The layers are *static CI* (parse committed source/JSON, no model), *fixture* (deterministic local CLI/hook/evaluator unit test, no model), *live-claude*, and *live-codex* (real model calls, opt-in, gated on `RUN_LIVE_HARNESS=1`). The machine-readable `covered_by` field on each entry in `load_contract.json` carries the same mapping; this README is the human index and `load_contract.json` is the source of truth — `test_contract.py::test_every_load_contract_entry_carries_covered_by` keeps them from drifting.

**Read the Coverage-strength column literally.** "Live-claude verified" means a real Claude agent run confirmed the behavior during the 08–12 expansion. "Codex built, live-pending" means the Codex test exists and its evaluator is CI-tested on synthetic inputs, but no Codex live run has happened yet (no credentials). "Static/proxy-only" means the layer is the strongest available observable for that contract by harness limitation, not direct by-name evidence — it does not imply live coverage.

| LC | Area | Static CI | Fixture | Live-claude | Live-codex | Coverage strength |
|---|---|---|---|---|---|---|
| **LC001** | always-loaded skills (`using-superra` + `report-in-markdown`) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) + [test_always_loaded_live.py::…static_backbone](test_always_loaded_live.py#L310) (frontmatter contract) | [test_always_loaded_live.py](test_always_loaded_live.py) canary evaluators | [always_loaded_live.py](always_loaded_live.py) introspection canary | [always-loaded-codex-smoke.sh](always-loaded-codex-smoke.sh) body-load canary | **Claude live-verified** via frontmatter autoload — zero `Skill`-tool loads is the expected signal, so this is by-frontmatter + behavioral-introspection evidence, not a by-name `Skill` event. **Codex built, live-pending.** |
| **LC002** | per-stage manifest loads (rollup) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) | per-stage `CanarySpec` (built) | **All 4 non-empty stages Claude live-verified** (see LC007–LC010). **Codex built, live-pending.** |
| **LC003** | per-domain manifest loads (rollup) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) | per-domain `CanarySpec` (built) | **All 4 domains + the multi-domain every-match rule Claude live-verified** (see LC011–LC014). **Codex built, live-pending.** |
| **LC004** | harness-adapter routing (Codex tool map) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | — | — (Codex-only contract) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | Static contract verifies adapter pointer + tool map. **Codex-only live row; built, live-pending.** |
| **LC005** | role + generated surfaces require manifest and `superra task read` | [test_contract.py::…surfaces_require_manifest_and_task_read](test_contract.py#L163) | [test_transcript_assertions.py](test_transcript_assertions.py) ordering parser | [claude-live-smoke.sh](claude-live-smoke.sh) (task-read-before-edit) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Claude live-verified** via the loading-smoke ordering assertion. **Codex built, live-pending.** |
| **LC006** | generated `.codex/agents/*.toml` drift | [test_contract.py::…generated_agent_drift_check](test_contract.py#L193) (runs `sync_codex_agents.py --check`) | — | — | — | **Fully CI-covered; no live row by design.** |
| **LC007** | stage `planning-review` → `planning-review.md` | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_stage_loads_live.py](test_stage_loads_live.py) (Read-channel suffix matcher) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[planning-review]` | planning-review `CanarySpec` (built) | **Claude live-verified** — the reference loads via `Read`, not the `Skill` tool. **Codex built, live-pending.** |
| **LC008** | stage `protection` → `result-protection` | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[protection]` | protection `CanarySpec` (built) | **Claude live-verified.** **Codex built, live-pending.** |
| **LC009** | stage `sync` → `semantic-merge` | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[sync]` | sync `CanarySpec` (built) | **Claude live-verified** that `semantic-merge` loads. The author/reviewer mode-reference sub-selection is **static-only**. **Codex built, live-pending.** |
| **LC010** | stage `integration` → `refactor-and-integrate` | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_stage_loads_live.py](test_stage_loads_live.py) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[integration]` | integration `CanarySpec` (built) | **Claude live-verified.** **Codex built, live-pending.** |
| **LC023** | stage `maturation` → `task-tree` + `superplan` (always; `writing` conditional) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_stage_loads_live.py](test_stage_loads_live.py) (multi-skill stage: both guaranteed skills required, `writing` conditional) | [stage_loads_live.py](stage_loads_live.py) `STAGE_ROWS[maturation]` | maturation `CanarySpec` (built) | **Multi-skill positive stage; fixture-covered, live-pending both harnesses** (added on the better-handoff trunk sync). |
| **LC011** | domain `econ-data-analysis` | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[econ-data-analysis]` | econ `CanarySpec` (built) | **Claude live-verified.** **Codex built, live-pending.** |
| **LC012** | domain `theory-modeling` (+ multi-domain) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_domain_loads_live.py](test_domain_loads_live.py) (multi-domain every-match case) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[theory-modeling]` + multi-domain canary | theory `CanarySpec` + list canary (built) | **Claude live-verified**, including the multi-domain every-match rule (`theory-modeling` + `writing` both load). **Codex built, live-pending.** |
| **LC013** | domain `writing` (+ multi-domain) | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[writing]` + multi-domain canary | writing `CanarySpec` + list canary (built) | **Claude live-verified**, incl. as a multi-domain member. Review/Polish/Draft sub-reference routing is **static-only**. **Codex built, live-pending.** |
| **LC014** | domain `slide-design` | [test_contract.py::…manifest_contract_matches_audit](test_contract.py#L141) | [test_domain_loads_live.py](test_domain_loads_live.py) | [domain_loads_live.py](domain_loads_live.py) `DOMAIN_ROWS[slide-design]` | slide-design `CanarySpec` (built) | **Claude live-verified.** Beamer sub-reference routing is **static-only**. **Codex built, live-pending.** |
| **LC015** | task-read ancestor context | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::…surfaces_context_without_dependency_results](test_contract.py#L275) | [claude-live-smoke.sh](claude-live-smoke.sh) (consumed-before-write proxy) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Fully fixture-covered** (deterministic surfacing). Live *consumption* proxied by the loading-smoke ordering, **Claude-verified**; **Codex built, live-pending.** |
| **LC016** | task-read unresolved comments | — | [test_bundle_fixture.py](test_bundle_fixture.py) | [claude-live-smoke.sh](claude-live-smoke.sh) (surfacing reachable; not an act-on-comment assertion) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Fully fixture-covered.** Whether the agent *acts on* a surfaced comment is **not separately live-asserted** (proxy-only). |
| **LC017** | task-read dependency status | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::…surfaces_context_without_dependency_results](test_contract.py#L275) | — | — | **Fully fixture-covered; no live row by design.** |
| **LC018** | dependency `## Results` non-inheritance | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::…surfaces_context_without_dependency_results](test_contract.py#L275) | [claude-live-smoke.sh](claude-live-smoke.sh) (`dependency_results_excluded` artifact field) | [codex-live-smoke.sh](codex-live-smoke.sh) (built) | **Fully fixture-covered** and additionally checked by the live artifact field. **Claude-verified; Codex built, live-pending.** |
| **LC019** | hook registries (Claude vs Codex events/matchers/commands) | [test_contract.py::…hook_registry_boundaries](test_contract.py#L215) | same test (wired commands) | static-only by design | static-only by design (SF003) | **Registry wiring fully CI-covered.** Live PostToolUse feedback is **not separately asserted** (static-only by design; Codex Bash coverage best-effort per SF003) — not a gap. |
| **LC020** | `superimplement` orchestration default + direct-mode exceptions | [test_contract.py::…workflow_orchestrator_contract_surfaces_are_static](test_contract.py#L251) | [test_transcript_assertions.py](test_transcript_assertions.py), [test_contract.py::…parser_contract_samples](test_contract.py#L296) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) (built) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) `HARNESS=codex` (built) | Static + fixture covered. Orchestrator dispatch smoke is **built; its Claude live run was not part of the 08–12 expansion**, and Codex live is pending. |
| **LC021** | dispatch-template fields + status progression | [test_contract.py::…workflow_orchestrator_contract_surfaces_are_static](test_contract.py#L251) | [test_transcript_assertions.py](test_transcript_assertions.py), [test_contract.py::…parser_contract_samples](test_contract.py#L296) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) (built) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) `HARNESS=codex` (built) | Dispatch-template surfaces **static-covered**; dispatch detection **fixture-covered**. Status-progression assertion is in the orchestrator smoke (**built, live run pending both harnesses**). |
| **LC022** | Codex orchestration adapter (named-agent dispatch) | [test_contract.py::…workflow_orchestrator_contract_surfaces_are_static](test_contract.py#L251) | — | — (Codex-only contract) | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) `HARNESS=codex` + [subagent_start_hook.py](subagent_start_hook.py) dispatch log (built) | Static contract verifies named-agent priority + tool map. The SubagentStart log supersedes JSONL spawn detection (codex emits no `spawn_agent` item). **Codex-only; built, live-pending.** |

**Deferred-import isolation (CI regression guard).** [test_deferred_import_isolation.py](test_deferred_import_isolation.py) locks in that importing any live-harness module (`sdk_load_harness`, `stage_loads_live`, `domain_loads_live`, `always_loaded_live`) pulls neither `claude_agent_sdk` nor a codex-cli client into `sys.modules` and makes no model call — the SDK import stays deferred inside the live entry point. Task 08's reviewer verified this by hand; this test makes it permanent so the deferred-import boundary cannot silently regress onto the default CI path.

### Known coverage gaps and honest caveats

- **No Codex live run yet.** Every Codex live row is *built and CI-tested on synthetic inputs* but has not been executed against a real Codex agent (no credentials). These rows are marked "live-pending," not "verified."
- **The Codex always-loaded canary is a weak standalone proxy.** Its canary token appears in the fixture body, so a Codex agent could in principle echo it without the skill body loading; it is backstopped by the Claude hook evidence and by the SubagentStart dispatch hook, not relied on alone.
- **Loading ≠ rule-compliance.** Every live row evidences that a skill/reference *loaded* (or that its body shaped one observable), not that the agent fully *complied* with the skill's rules. Prose quality and full rule-following are out of scope by design.
- **Sub-reference routing is static-only.** Within a loaded domain/stage skill, which secondary reference the agent picks (Review/Polish/Draft for `writing`, Beamer layout for `slide-design`, author/reviewer mode for `semantic-merge`) is verified statically, not by a live by-name assertion.
- **No LC0xx is uncovered.** All 22 entries carry at least static or fixture coverage; the rows where a layer is static/proxy-only (LC016 act-on-comment, LC019 live hook feedback, sub-reference routing) are marked explicitly above rather than left as silent omissions.

[load_contract.json](load_contract.json) is the compact source-of-truth audit behind this matrix: each entry lists source paths, triggers, expected evidence, `classification` (`ci_safe_static`, `ci_safe_fixture`, `manual_live_*`), and the `covered_by` mapping. Its `static_findings` block records terminology and boundary drift (SF001–SF004) that should become lint or follow-up issues rather than live-agent assertions.

### Layers in detail

**Static CI checks** read committed text and JSON and assert the contract is present — the manifest rows, the role/generated surfaces that must name the manifest and `superra task read`, the hook registries, and the workflow-orchestration surfaces. The generated-agent drift check runs `sync_codex_agents.py --check`, so a hand-edit of a `.codex/agents/*.toml` that diverges from its role spec fails CI.

**Fixture / parser unit tests** exercise the real `task_read.py` against the committed `bundle-two-tasks` fixture and the transcript parser against committed sample transcripts. The fixture tests confirm `superra task read` surfaces ancestor `## Objective` context, unresolved comments, and sibling dependency status, and that a dependency's `## Results` sentinel never leaks into the target's context. The parser tests confirm the ordering, dispatch, fallback, and artifact-diff logic the live smokes depend on, including negative cases (narration without a tool event must fail, a fabricated fallback reason must not skip-pass).

**Hook unit test** asserts the Claude and Codex hook registries wire the expected events, matchers, and commands — Claude has `UserPromptSubmit/PreToolUse/PostToolUse` with a `Skill` PreToolUse matcher and the `ensure-using-superra` / `ensure-agent-orchestration` autoloads; Codex adds a `Stop` hook, drops the Claude-only `Skill` matcher and autoloads, and keeps `autoload-superra` / `merge-guard` / `task-hook`.

**Manual live smokes** drive a real Claude or Codex agent through the bundled fixture and assert structural transcript evidence with the shared parser. See below.

### Claude skill-load-by-name harness (Agent SDK, manual)

Claude's `claude -p` stream does not give skill-load-by-name evidence the shared parser can tie to the manifest, and filesystem `PreToolUse` hooks do not fire under `claude -p` (issue #40506). So on-demand skill loading is verified through the Python `claude-agent-sdk`: the harness **dispatches the real plugin role agent** (`superRA:implementer` / `superRA:reviewer`, present in the SDK init `agents` list) so the manifest-driven loads actually fire, and a `PreToolUse(matcher="Skill")` in-process hook records each on-demand skill by name and event index (including loads inside the dispatched subagent). There is no `InstructionsLoaded` hook — it is not a registrable `claude-agent-sdk` `HookEvent`; the always-loaded skills (`using-superra`, `report-in-markdown`) preload via agent frontmatter `skills: [...]` and are covered by a static frontmatter contract plus a live behavioral canary. The split is deliberate:

- [sdk_load_evidence.py](sdk_load_evidence.py) — CI-safe evidence model + assertions. `SkillLoadEvidence` + `check_skills_loaded_before_first_edit` cover on-demand (Skill-tool) loads; `check_always_loaded_frontmatter` is the static contract asserting both role specs declare both always-loaded skills; `BehavioralCanarySpec` + `check_behavioral_canary` is the reusable live checker (task 10 supplies the fixtures) that proves a preloaded skill's structural rule shaped the output. Never imports `claude-agent-sdk`; never makes a model call.
- [sdk_load_harness.py](sdk_load_harness.py) — the live runner. The **only** module that imports `claude-agent-sdk`, and the import is deferred into `run_skill_load_session`, so the default `pytest` path never touches it. Dispatches the real role agent, gated on `RUN_LIVE_HARNESS=1`, default `CLAUDE_MODEL=haiku`. Supply the SDK on the live path with `uv run --with claude-agent-sdk`.
- [test_sdk_load_evidence.py](test_sdk_load_evidence.py) — CI-safe unit test driving the evidence/assertion/contract/canary layer on synthetic records and the real role specs: on-demand ordering green + two red cases (required skill never loaded; skill loaded only after the first edit); the frontmatter contract green (real specs) + red (missing skill / missing file); the behavioral canary green + red.

The downstream live smokes (always-loaded / per-stage / per-domain skill coverage) call `run_skill_load_session` and assert on the returned evidence — they consume the harness, not raw SDK calls. A required skill that never loads (e.g. `report-in-markdown`) is a real finding in the loading contract to escalate, not a reason to weaken the assertion.

### Always-loaded skill live coverage (LC001, manual)

Both always-loaded skills (`using-superra`, `report-in-markdown`) must be in the dispatched role's context before any task-file or code edit. The two harnesses establish this differently because their loading mechanisms differ:

- **Claude autoloads** both skills via the agents' frontmatter `skills: [...]`, so an autoloaded skill is *invisible* to the `Skill` PreToolUse hook — **zero `Skill`-tool loads is the expected, correct signal, not a failure**. The Claude side evidences the contract two ways: (1) the **static frontmatter contract** ([sdk_load_evidence.py](sdk_load_evidence.py)::`check_always_loaded_frontmatter`, reused via [always_loaded_live.py](always_loaded_live.py)::`check_claude_always_loaded_static`) — the deterministic CI backbone; and (2) a **live discriminating introspection canary** that dispatches the real `superRA:implementer` and asks it to state its markdown file-citation rule *without loading any skill or reading any file*, then checks the answer recites `report-in-markdown`'s anchor-link rule (links *with line anchors*, *not* backtick-wrapped paths) **with zero `Skill` loads of that skill**. The rule is chosen to discriminate against the model default: a bare file-link format would not, so the canary keys off the "line anchors" requirement *and* the explicit "not backticks" contrast, and rejects a `NO_RULE` or backtick-path answer. The introspection prompt, the discriminating `BehavioralCanarySpec`, and the evaluator live in [always_loaded_live.py](always_loaded_live.py).
- **Codex does not autoload**, so a frontmatter-only skill never enters context; the role-spec body instruction is what loads the always-loaded skills. The Codex side uses 09's canary convention ([codex_load_evidence.py](codex_load_evidence.py)): per-skill `CanarySpec` rows whose skill-unique tokens are only producible if the skill body loaded — `report-in-markdown` running its own `check_markdown.py` self-diagnose CLI, and `using-superra`'s `superra task read` wrapper convention — each checked in a `command_execution` or at an artifact field. This exercises the role-spec body-load path that substitutes for Claude's autoload. Fixture: [tests/fixtures/task-trees/always-loaded-canary](../fixtures/task-trees/always-loaded-canary); evaluator: [check_always_loaded_smoke.py](check_always_loaded_smoke.py).

The live SDK dispatch is mildly nondeterministic (it leans on the top-level model to issue the Task dispatch), so the Claude introspection canary defaults to `CLAUDE_MODEL=sonnet` (sonnet dispatched reliably; haiku was flaky) and runs a small pass@k retry window (`attempts`, default 3), passing if any attempt recites the rule. A genuine failure — the rule absent from a reliable dispatch, or a non-zero always-loaded `Skill` load — is a real LC001 loading-contract finding to escalate, not an assertion to relax.

[test_always_loaded_live.py](test_always_loaded_live.py) drives both evaluators (Claude introspection green + the NO_RULE / backtick-default / anchor-without-contrast / autoload-violation red cases; Codex canary green + red) plus the static backbone on synthetic inputs — no model call, no SDK/codex-cli import. Run the live canaries:

```bash
# Claude introspection canary (default sonnet for reliable dispatch; pass@k):
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/always_loaded_live.py

# Codex always-loaded body-load canary (set CODEX_MODEL or use the CLI default):
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

On **Codex** (no skill-load event), each non-empty stage carries a per-stage `CanarySpec` ([stage_loads_live.py](stage_loads_live.py)) whose skill-unique token is a discriminating concept that stage's body prescribes (`drift test`, `intent conflict`, `minimum net diff`, `handoff-readiness`; `frontier` for `maturation`, anchored on the always-loaded `task-tree` body — never on conditional `writing`), recorded at the artifact field `stage_canary` — only producible if the stage skill/reference body loaded. The negative `implementation` stage sets `stage_canary` to `none`.

[test_stage_loads_live.py](test_stage_loads_live.py) drives the stage evaluator and the per-stage canaries on synthetic inputs — green per stage (skill and read channels, including the multi-skill `maturation` stage requiring both guaranteed skills with `writing` left conditional), red (guaranteed stage skill never loaded; reference never read; load after the first edit; a maturation run missing one guaranteed skill), the negative case (no stage skill loaded → green; a stage skill — including a maturation skill — loaded on `implementation` → red over-load), the read-path suffix matcher, and a fixture-sanity check that each committed expected artifact satisfies its canary. No model call, no SDK/codex-cli import. Run the live Claude per-stage canary (default `sonnet`, pass@k; only the orchestrator runs it — no network on the implementer path):

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/stage_loads_live.py
```

A stage that reliably does **not** load its manifest skill/reference is a real LC002/LC007–LC010 finding to record and escalate, not an assertion to relax.

**`--include-hook-events` audit.** Audited against CLI 2.1.183: it is a real, documented flag ("Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)"), not a no-op — it surfaces hook lifecycle events such as the `UserPromptSubmit` autoloads. It does not make filesystem `PreToolUse` hooks fire under `claude -p`, so it gives no skill-load-by-name evidence; that is what the Agent SDK harness above provides. The existing `claude-live-smoke.sh` / `orchestrator-live-smoke.sh` keep the flag for debugging visibility and do not assert on the extra events.

### Per-domain skill-load live coverage (LC003, LC011–LC014, manual)

A domain-worded fixture task must load its domain skill before domain action, and a dispatch whose wording matches more than one domain must load **every** matching domain (the manifest requires loading every matching domain, not just the first). One parametrized `{domain_skill, trigger_wording}` table ([domain_loads_live.py](domain_loads_live.py)::`DOMAIN_ROWS`) is the single source of truth — `econ-data-analysis`, `theory-modeling`, `writing`, `slide-design` — with trigger wording kept close to the manifest Domain-table phrasing, so adding a future domain is a one-row change. One fixture body ([tests/fixtures/task-trees/domain-loads](../fixtures/task-trees/domain-loads)) is reused across every domain; only the dispatch wording differs.

All domain skills load through the `Skill` tool, so 08's `PreToolUse(matcher="Skill")` hook records them by name — the same channel as the per-stage skill rows. There is no Read-channel / reference case here (unlike 11's `planning-review` reference). The evaluator reuses 08's `SkillLoadEvidence` and 11's plugin-prefix-insensitive name matching (live loads are `superRA:`-qualified, e.g. `superRA:econ-data-analysis`; a raw compare against a bare expected name is a false negative — this was live-caught in 11). The **multi-domain** case (`theory-modeling` + `writing`: derive a result *and* write it up) is the load-bearing one — `evaluate_multi_domain_load` requires the **full** matching set, so loading only one of several (first-match instead of every-match) fails, naming each missing domain.

On **Codex** (no skill-load event), each domain carries a per-domain `CanarySpec` ([domain_loads_live.py](domain_loads_live.py)) whose skill-unique token is a discriminating concept that domain's body prescribes (`describe before transform`, `comparative statics`, `audience model`, `live communication`), recorded as an entry of the artifact list field `domain_canaries` — a list (not a scalar) so the multi-domain artifact can carry every matched domain's concept at once. `evaluate_codex_multi_domain` requires every matched domain's token to be present.

[test_domain_loads_live.py](test_domain_loads_live.py) drives the domain evaluator and the per-domain canaries on synthetic inputs — green per domain (including the `superRA:`-qualified live shape), red (domain skill never loaded; loaded after the first edit), the multi-domain cases (all matching skills loaded → green; only one of several loaded → red; none loaded → red), the Codex artifact-list canaries (green/red per domain and multi-domain), and a fixture-sanity check that each committed expected artifact satisfies its canary(s). No model call, no SDK/codex-cli import. Run the live Claude per-domain canary (default `sonnet`, pass@k; only the orchestrator runs it — no network on the implementer path):

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
| Orchestrator | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) | `superimplement` dispatches an implementer then a reviewer subagent for the frontier, or passes-with-skip on a documented direct-mode fallback. `HARNESS=claude` (default) or `HARNESS=codex`. |

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

**When the documented-exception fallback is acceptable.** If a harness cannot expose subagent dispatch events at all, the smoke passes-with-skip only when a single transcript event both names a direct-mode switch with reviewer preservation *and* names one of `superimplement`'s three documented direct-mode exceptions: the harness lacks subagent support, the user explicitly requested direct mode, or the task is documented as trivial enough for direct mode. Bare co-occurrence of "direct mode" and "reviewer" without a documented exception does not qualify — a fabricated or undocumented reason fails the smoke, so a genuinely missing dispatch cannot be masked. A main agent that silently implements inline with neither dispatch events nor a documented fallback fails.

## Intentionally not tested through model prose or live assertions

Some behaviors are subjective or unobservable, so the suite covers them statically or not at all rather than asserting them on a model:

- **Whether a specific skill or reference was loaded into the model's context.** Neither harness emits a structural skill-load event the parser can tie to the manifest by name. The loading smokes therefore assert the strongest available observables — task-read command events, marker read events, and an artifact whose sentinel values can only be produced after reading the required context — and leave manifest / role-surface load expectations to the CI-safe static contract tests. On **Claude**, the SDK harness ([sdk_load_evidence.py](sdk_load_evidence.py)) recovers skill-load-by-name evidence via in-process hooks. On **Codex** (no skill-load event at all), the stage/domain/always-loaded smokes (10–12) use the **canary / side-effect convention** in [codex_load_evidence.py](codex_load_evidence.py): a `CanarySpec` names a skill-unique token the fixture task can only emit if the skill body loaded — either in a prescribed command (a `command_execution` in the JSONL) or at a field of the output artifact — and `evaluate_canary` scans both sources. An absent canary is a real "skill body did not load" finding to escalate.
- **The quality or correctness of generated prose.** Out of scope by design; the contract is the interface, not the writing.
- **Direct-mode policy choices beyond the documented-exception signal.** Direct-mode exceptions are observable only when the agent states the fallback reason and dispatch path (load-contract SF004), so the orchestrator smoke accepts either dispatch evidence or an explicit documented fallback, and never infers a fallback from the absence of spawn events.
- **Terminology drift** such as `Stage: protection` versus older `drift-test` wording (load-contract SF002), and root-level vs `hooks/` registry paths (SF001). These are static lint / follow-up findings, not live-agent behavior assertions.
- **Complete Codex shell-mutation enforcement.** Codex Bash hook coverage is best-effort (SF003), so hook assertions stay at registry-wiring and fixture-invocation level and the live tests do not depend on catching every shell mutation.

## Why live tests are opt-in and excluded from CI

Live smokes make real model calls: they cost money, depend on a logged-in CLI and network access, and are non-deterministic in a way a unit test is not. Putting them in default CI would make every run slow, flaky, and billable, and would fail in any environment without harness credentials. The deterministic value — every contract surface, the parser logic, and the task-read context behavior — already lives in the CI-safe layers, which run with no credentials and no model calls. The live smokes exist to confirm a real agent actually follows the contract on demand, so they gate behind `RUN_LIVE_HARNESS=1` and stay manual.

The default CI command path (`pytest` over `tests/harness-instruction-following`) collects only the Python test modules; it does not invoke the live `*.sh` scripts. A bare invocation of any live script without `RUN_LIVE_HARNESS=1` prints `SKIP` and exits 0, so even if a script were wired into a CI step it would no-op rather than make a model call.

## CI boundary (verified)

The CI/manual boundary holds on four checks, all confirmed in this worktree:

1. **Default `pytest` collects no live `.sh` scripts and imports no `claude-agent-sdk`.** `pytest` collects only `test_*.py` modules; the live `*.sh` smokes are shell scripts and are never collected. None of the collected modules imports `claude_agent_sdk` at top level — the only import lives deferred inside `sdk_load_harness.run_skill_load_session` (reached via `_run_session_async`), and [test_deferred_import_isolation.py](test_deferred_import_isolation.py) asserts importing every live-harness module leaves `claude_agent_sdk` and codex-cli out of `sys.modules`.
2. **Every live script SKIPs without `RUN_LIVE_HARNESS=1`.** [claude-live-smoke.sh](claude-live-smoke.sh), [codex-live-smoke.sh](codex-live-smoke.sh), [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh), and [always-loaded-codex-smoke.sh](always-loaded-codex-smoke.sh) each print `SKIP` and exit 0 when the gate is unset; the orchestrator-run Python live entries ([stage_loads_live.py](stage_loads_live.py), [domain_loads_live.py](domain_loads_live.py), [always_loaded_live.py](always_loaded_live.py)) gate the same way and defer the SDK import behind the gate.
3. **The only committed workflow runs the docs build, not the live suite.** [`.github/workflows/docs-site.yml`](../../.github/workflows/docs-site.yml) runs `docs/build_site.sh`; no workflow runs `RUN_LIVE_HARNESS=1` or invokes the live smokes.
4. **The full CI-safe suite is green.** `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` passes with no model call and no credentials.
