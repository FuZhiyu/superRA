# superRA Release Notes

## [0.1.1] - 2026-04-22

### Added

- **Three autoload hooks** that keep the superRA skill-load state coherent without requiring the user or the agent to remember it manually:
  - **`autoload-superra`** (`UserPromptSubmit`) — soft reminder. Detects "superRA" (and case/spacing variants like `super RA`, `super-ra`, `Super_RA`) in the user's message and, if `superRA:using-superRA` has not been invoked this session, injects an `additionalContext` reminder telling Claude to load the master skill before responding.
  - **`ensure-using-superra`** (`PreToolUse:Skill`) — hard enforcement. When Claude invokes any `superRA:*-workflow` skill and `superRA:using-superRA` is not yet loaded, blocks the `Skill` call with `permissionDecision: deny` and a reason directing Claude to load the master skill first and retry.
  - **`ensure-agent-orchestration`** (`PreToolUse:Skill`) — same pattern as above, gating independently on `superRA:agent-orchestration`.
- **Hook test suites.** Per-hook stdin-synthesis drivers (16 vectors each, 48 total) under `tests/hooks/test-{autoload-superra,ensure-using-superra,ensure-agent-orchestration}.sh` covering happy path, suppression after companion-load, trigger-boundary cases, JSON-special characters, fail-open on missing transcript, and deny-reason JSON round-trip. A CLI-driven end-to-end driver (`tests/hooks/test-e2e-cli.sh`, 6 scenarios) validates registration + wiring against the live `claude` CLI on Haiku for ~$0.27 per run.
- **README §Hooks** table extended to list all six registered hooks.

### Fixed

- **Version drift across plugin manifests.** `package.json` (0.0.5), `.claude-plugin/plugin.json` (0.1.0), `.cursor-plugin/plugin.json` (0.0.3), `.claude-plugin/marketplace.json` (0.1.0), and `gemini-extension.json` (5.0.7 — leftover upstream Superpowers tag) are now all in sync at 0.1.1 via `scripts/bump-version.sh`.

### Notes

- All three new hooks follow the existing extensionless-bash convention with a three-way platform-output branch (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback) matching `merge-guard` / `exit-plan-mode` / `ask-user-question-logger`. Reminder text and deny reasons are JSON-escaped via `python3 json.dumps` before splicing into the payload, so inner `"` or `\` cannot invalidate the JSON.
- Scenario S4 of the CLI e2e suite passes opportunistically (it relies on Haiku obeying an in-prompt countermand against the autoload reminder); the disposition path if a future model regresses S4 is documented inline in the test's docstring. The deny logic itself is fully covered by the stdin-synthesis unit tests.
- Plan + results for this change: `docs/plans/2026-04-21-superra-autoload-hooks-{plan,results}.md`.
