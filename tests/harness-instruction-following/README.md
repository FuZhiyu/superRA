# Harness Instruction-Following Tests

This suite checks one thing: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting? The scope is the agent-interface contract, not prose quality, so the tests assert structural observables — manifest and role-surface text, generated-agent drift, hook registries, transcript tool events, `superra task read` output, and an artifact whose values can only be produced after reading the required context — never generated prose.

Coverage splits across four layers. The first three run in default CI; the fourth drives a real model and is opt-in.

## Coverage matrix

| Requirement | Static CI check | Fixture / parser unit test | Hook unit test | Manual live smoke |
|---|---|---|---|---|
| Skill-Load Manifest always-loaded + stage + domain rows | [test_contract.py::test_skill_load_manifest_contract_matches_audit](test_contract.py#L106) | — | — | loading smokes (indirect; see limitation below) |
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

The evaluator keys off the harness's own dispatch event shape, never a prose claim:

- **Claude** exposes a subagent dispatch as a `Task` / `Agent` tool event carrying a `subagent_type` of `superRA:implementer` or `superRA:reviewer`.
- **Codex** exposes it as `spawn_agent(agent_type="superra_implementer" / "superra_reviewer")`.

The smoke passes when both an implementer and a reviewer dispatch event are present.

**When the documented-exception fallback is acceptable.** If a harness cannot expose subagent dispatch events at all, the smoke passes-with-skip only when a single transcript event both names a direct-mode switch with reviewer preservation *and* names one of `superimplement`'s three documented direct-mode exceptions: the harness lacks subagent support, the user explicitly requested direct mode, or the task is documented as trivial enough for direct mode. Bare co-occurrence of "direct mode" and "reviewer" without a documented exception does not qualify — a fabricated or undocumented reason fails the smoke, so a genuinely missing dispatch cannot be masked. A main agent that silently implements inline with neither dispatch events nor a documented fallback fails.

## Intentionally not tested through model prose or live assertions

Some behaviors are subjective or unobservable, so the suite covers them statically or not at all rather than asserting them on a model:

- **Whether a specific skill or reference was loaded into the model's context.** Neither harness emits a structural skill-load event the parser can tie to the manifest by name. The loading smokes therefore assert the strongest available observables — task-read command events, marker read events, and an artifact whose sentinel values can only be produced after reading the required context — and leave manifest / role-surface load expectations to the CI-safe static contract tests.
- **The quality or correctness of generated prose.** Out of scope by design; the contract is the interface, not the writing.
- **Direct-mode policy choices beyond the documented-exception signal.** Direct-mode exceptions are observable only when the agent states the fallback reason and dispatch path (load-contract SF004), so the orchestrator smoke accepts either dispatch evidence or an explicit documented fallback, and never infers a fallback from the absence of spawn events.
- **Terminology drift** such as `Stage: protection` versus older `drift-test` wording (load-contract SF002), and root-level vs `hooks/` registry paths (SF001). These are static lint / follow-up findings, not live-agent behavior assertions.
- **Complete Codex shell-mutation enforcement.** Codex Bash hook coverage is best-effort (SF003), so hook assertions stay at registry-wiring and fixture-invocation level and the live tests do not depend on catching every shell mutation.

## Why live tests are opt-in and excluded from CI

Live smokes make real model calls: they cost money, depend on a logged-in CLI and network access, and are non-deterministic in a way a unit test is not. Putting them in default CI would make every run slow, flaky, and billable, and would fail in any environment without harness credentials. The deterministic value — every contract surface, the parser logic, and the task-read context behavior — already lives in the CI-safe layers, which run with no credentials and no model calls. The live smokes exist to confirm a real agent actually follows the contract on demand, so they gate behind `RUN_LIVE_HARNESS=1` and stay manual.

The default CI command path (`pytest` over `tests/harness-instruction-following`) collects only the Python test modules; it does not invoke the live `*.sh` scripts. A bare invocation of any live script without `RUN_LIVE_HARNESS=1` prints `SKIP` and exits 0, so even if a script were wired into a CI step it would no-op rather than make a model call.
