# Harness Instruction-Following Tests

This suite checks one thing: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting? The scope is the agent-interface contract, not prose quality, so the tests assert structural observables — manifest and role-surface text, generated-agent drift, hook registries, transcript tool events, `superra task read` output, and an artifact whose values can only be produced after reading the required context — never generated prose.

Coverage splits across four layers. The first three run in default CI; the fourth drives a real model and is opt-in.

## Coverage matrix

| Requirement | Static CI check | Fixture / parser unit test | Hook unit test | Manual live smoke |
|---|---|---|---|---|
| Skill-Load Manifest always-loaded + stage + domain rows | [test_contract.py::test_skill_load_manifest_contract_matches_audit](test_contract.py#L106) | — | — | loading smokes (indirect; see limitation below) |
| Both always-loaded skills (`using-superra` + `report-in-markdown`, LC001) in the dispatched role's context | [test_always_loaded_live.py::test_green_static_backbone_real_role_specs](test_always_loaded_live.py#L209) (static frontmatter contract — the deterministic backbone) + [test_always_loaded_live.py](test_always_loaded_live.py) canary-evaluator green/red | — | — | Claude introspection canary ([always_loaded_live.py](always_loaded_live.py)); Codex body-load canary ([always-loaded-codex-smoke.sh](always-loaded-codex-smoke.sh)) |
| Each non-empty stage loads its manifest skill/reference; `implementation`/`documentation` load none (LC002, LC007–LC010) | [test_stage_loads_live.py](test_stage_loads_live.py) stage-evaluator green/red per stage + negative cases | — | — | Claude per-stage canary ([stage_loads_live.py](stage_loads_live.py)); Codex per-stage body-load canary (orchestrator-run per [09](../../superRA/task-tree/agent-interface/agent-loading-tests/09-codex-canary-and-dispatch-hook/task.md) convention) |
| Role + generated surfaces require manifest and `superra task read` | [test_contract.py::test_role_and_generated_surfaces_require_manifest_and_task_read](test_contract.py#L128) | — | — | loading smokes (indirect) |
| Generated `.codex/agents/*.toml` stay aligned with role specs | [test_contract.py::test_codex_generated_agent_drift_check_is_ci_safe](test_contract.py#L158) | — | — | — |
| Hook registries: Claude vs Codex event sets, matchers, commands | [test_contract.py::test_hook_registry_boundaries_for_claude_and_codex](test_contract.py#L180) | — | same test | — |
| `superra task read` surfaces ancestor context, comments, dependency status; excludes dependency `## Results` | — | [test_bundle_fixture.py](test_bundle_fixture.py), [test_contract.py::test_task_read_fixture_contract_surfaces_context_without_dependency_results](test_contract.py#L240) | — | both loading smokes assert `dependency_results_excluded` in the artifact |
| `superimplement` orchestration + dispatch-template surfaces are documented | [test_contract.py::test_workflow_orchestrator_contract_surfaces_are_static](test_contract.py#L216) | — | — | orchestrator smoke |
| Transcript parser: task-read / marker-read ordering, dispatch detection, fallback gating, artifact diffing | — | [test_transcript_assertions.py](test_transcript_assertions.py), [test_contract.py::test_parser_contract_samples_and_negative_ordering_cases](test_contract.py#L261) | — | feeds every live smoke |
| Load-contract audit indexes every CI-safe area | [test_contract.py::test_load_contract_indexes_every_ci_safe_contract_area](test_contract.py#L81) | — | — | — |
| Live fixture stays cheap and mock-only | [test_contract.py::test_live_fixture_stays_cheap_and_mock_only](test_contract.py#L346) | — | — | — |
| Agent runs both task reads + three marker reads before writing the evidence artifact | — | parser samples in the two tests above | — | [claude-live-smoke.sh](claude-live-smoke.sh), [codex-live-smoke.sh](codex-live-smoke.sh) |
| `superimplement` dispatches an implementer then a reviewer subagent (not silent inline work) | — | dispatch-detection samples | — | [orchestrator-live-smoke.sh](orchestrator-live-smoke.sh) |

[load_contract.json](load_contract.json) is the compact source-of-truth audit behind this matrix: it lists each requirement's source paths, triggers, expected evidence, and classification (`ci_safe_static`, `ci_safe_fixture`, `manual_live_*`). Its `static_findings` block records terminology and boundary drift (SF001–SF004) that should become lint or follow-up issues rather than live-agent assertions.

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

### Per-stage skill-load live coverage (LC002, LC007–LC010, manual)

Each non-empty workflow stage must load the skill or reference the Skill-Load Manifest assigns it before stage action; the two negative stages (`implementation`, `documentation`) must load no extra stage skill. One parametrized table ([stage_loads_live.py](stage_loads_live.py)::`STAGE_ROWS`) is the single source of truth — `planning-review → skills/superplan/references/planning-review.md`, `protection → result-protection`, `sync → semantic-merge`, `integration → refactor-and-integrate` — so adding a future stage is a one-row change. One fixture body ([tests/fixtures/task-trees/stage-loads](../fixtures/task-trees/stage-loads)) is reused across every stage; only the dispatch `Stage:` line differs.

Two evidence channels, because the stage manifest entries load through different tools:

- **Stage skills** (`result-protection`, `semantic-merge`, `refactor-and-integrate`) load via the `Skill` tool, so 08's `PreToolUse(matcher="Skill")` hook records them by name — the same channel as the ordering smoke. The evaluator reuses 08's `SkillLoadEvidence`.
- **The `planning-review` reference** is a file loaded via `Read`, not the `Skill` tool, so the `Skill` hook cannot see it. Task 11 extends 08's harness additively with an opt-in `PreToolUse(matcher="Read")` hook (`run_skill_load_session(..., capture_reads=True)`) that records read paths into `SkillLoadEvidence.read_loads`; the evaluator matches the manifest reference path against the captured reads by path-segment suffix (the SDK payload carries the plugin-install absolute path, not the manifest-relative one). The hook is default-off so existing callers are unaffected, and `claude-agent-sdk` stays off the CI import path. The exact `Read` tool_input path key (expected `file_path`) is confirmed on the first live run.

On **Codex** (no skill-load event), each stage carries a per-stage `CanarySpec` ([stage_loads_live.py](stage_loads_live.py)) whose skill-unique token is a discriminating concept that stage's body prescribes (`drift test`, `intent conflict`, `minimum net diff`, `handoff-readiness`), recorded at the artifact field `stage_canary` — only producible if the stage skill/reference body loaded. The negative stages set `stage_canary` to `none`.

[test_stage_loads_live.py](test_stage_loads_live.py) drives the stage evaluator and the per-stage canaries on synthetic inputs — green per stage (skill and read channels), red (stage skill never loaded; reference never read; load after the first edit), the negative cases (no stage skill loaded → green; a stage skill loaded on `implementation`/`documentation` → red over-load), the read-path suffix matcher, and a fixture-sanity check that each committed expected artifact satisfies its canary. No model call, no SDK/codex-cli import. Run the live Claude per-stage canary (default `sonnet`, pass@k; only the orchestrator runs it — no network on the implementer path):

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/stage_loads_live.py
```

A stage that reliably does **not** load its manifest skill/reference is a real LC002/LC007–LC010 finding to record and escalate, not an assertion to relax.

**`--include-hook-events` audit.** Audited against CLI 2.1.183: it is a real, documented flag ("Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)"), not a no-op — it surfaces hook lifecycle events such as the `UserPromptSubmit` autoloads. It does not make filesystem `PreToolUse` hooks fire under `claude -p`, so it gives no skill-load-by-name evidence; that is what the Agent SDK harness above provides. The existing `claude-live-smoke.sh` / `orchestrator-live-smoke.sh` keep the flag for debugging visibility and do not assert on the extra events.

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
