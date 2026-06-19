# Harness Instruction-Following Audit

`load_contract.json` is the compact source-of-truth audit for planned harness instruction-following tests. It lists source paths, triggers, expected evidence, and whether each check is CI-safe or requires manual live Claude/Codex evidence.

| Area | Entries | Primary check class |
|---|---:|---|
| Manifest, roles, generated agents | LC001-LC006 | static plus live transcript |
| Stage loads | LC007-LC010 | static plus live transcript |
| Domain loads | LC011-LC014 | static plus live transcript |
| `superra task read` behavior | LC015-LC018 | fixture, with selected live transcript checks |
| Hook registries | LC019 | static and fixture |
| Workflow orchestration | LC020-LC022 | static plus manual live transcript |

Static findings are included in the JSON under `static_findings`. They should become lint or follow-up issues, not live-agent behavior assertions.

## Live smokes (manual-only, gated)

These drive a real Claude or Codex agent through the bundled `bundle-two-tasks` fixture and assert structural transcript evidence with the shared parser. They never run in default CI: each gates on `RUN_LIVE_HARNESS=1` and is a documented no-op otherwise. Shared setup (workspace seeding, the bundled mock-task prompt, the orchestrator prompt) lives in `live_smoke_lib.sh`; the Python evaluators (`check_loading_smoke.py`, `check_orchestrator_smoke.py`) reuse `transcript_assertions.py` and the committed expected artifact.

| Smoke | Entry | What it asserts |
|---|---|---|
| Claude loading | `claude-live-smoke.sh` | Both `superra task read` calls and all three marker reads occur before the `loading-evidence.json` write; artifact matches the expected sentinels. Defaults to `CLAUDE_MODEL=haiku`. |
| Codex loading | `codex-live-smoke.sh` | Same contract through `codex exec --json --ephemeral`. Uses `CODEX_MODEL` when set; the repo prescribes no canonical cheapest Codex model. |
| Orchestrator | `orchestrator-live-smoke.sh` | `superimplement` dispatches implementer then reviewer subagents for the frontier; passes-with-skip if the harness exposes no dispatch events but the agent records a documented direct-mode fallback. `HARNESS=claude` (default) or `HARNESS=codex`. |

```bash
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/claude-live-smoke.sh
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/codex-live-smoke.sh
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/orchestrator-live-smoke.sh
RUN_LIVE_HARNESS=1 HARNESS=codex bash tests/harness-instruction-following/orchestrator-live-smoke.sh
```

Harness-evidence limitation: neither harness emits a structural skill-load event the parser can tie to the manifest by name, so manifest/role-surface load expectations stay covered by the CI-safe contract tests in `test_contract.py`; the loading smokes assert the strongest available observables (task-read command events, marker read events, and an artifact whose sentinel values can only be produced after reading the required context).
