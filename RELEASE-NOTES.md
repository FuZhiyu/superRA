# superRA Release Notes

## [0.1.3] - 2026-05-02

### Added

- **Theory-modeling skill (alpha).** New domain vertical at `skills/theory-modeling/` for rigorous mathematical-modeling work: derivations, equilibrium setup, symbolic manipulation, proofs, comparative statics, and simple numerical verification. Composes with the existing PLAN → IMPLEMENT → INTEGRATE workflow without changes to workflow skills.
  - **Iron Law:** every symbol has a meaning, every assumption has a plain-language interpretation, every non-trivial derivation move has a one-sentence reason.
  - **Four-gate checklist** (Objects & Notation / Assumptions / Derivations / Verification & Rendering) walked at every implementation dispatch as the creation-time correctness floor. Gates 1 and 2 carry per-symbol and per-assumption ledger entries with explicit slot templates; falsification tests (Substitution test, Proof-deletion test) detect generic justifications.
  - **Stage-scoped references:** `references/planning.md` (Model Inventory / Assumption Map hard gate + Verification Plan), `references/integration.md` (readability layer for reader-ready output — objective-first rewriting, half-page mask test for local obviousness, cross-document coherence, refactor-survival), `references/integrate-drift-tests.md` (drift tests for symbolic identities and numerical baselines), `references/objective-first.md` (worked example + identification drills).
  - **Split:** `SKILL.md` is the creation-time correctness floor (load at every implementation dispatch); `references/integration.md` is the readability layer (load when polishing for a human reader).
  - **`skills/theory-modeling/CLAUDE.md`** records the high-level design choices for future contributors.

### Changed

- Routing surfaces (`skills/CATEGORIES.md`, `README.md`, `using-superra` skill inventory) updated to expose the new vertical.

## [0.1.2] - 2026-04-24

Includes merged PRs since `0.1.1`: #18 `[codex] tighten Phase B upstream-intent contract`, #19 `[codex] clarify Codex superRA orchestration instructions`, #20 `[codex] generate direct-mode role refs from canonical agents`, #21 `Teach-the-protocol: resolver redesign + over-prescription audit + gated principle`, #22 `planning-workflow: include header fields in change-plan protocol`, plus this release branch.

### Added

- **Result protection utility.** Protect now routes `Stage: protection` to `result-protection`; drift tests remain the current/default protection mechanism.
- **Explicit Sync stage label.** Sync now has `Stage: sync` for generic sync author/reviewer agents using semantic-merge workflow mode references.
- **Generated direct-mode role references.** Codex direct mode now reads skill-owned role references generated from canonical agent specs.

### Changed

- **Integration workflow split:** Protect -> Sync -> Integrate -> Document -> Finish now separates key-result protection, semantic sync, and codebase-coherence refactor/review.
- **Refactor discipline:** `refactor-and-integrate` now focuses on minimum net diff, convention fit, utility reuse, Project Doc Audit walk-up, and caller-supplied Sync impact as context.
- **Teach-the-protocol gate:** Contributor guidance, workflow resolver behavior, role specs, and skill prose now enforce DRY / Necessity discipline for instruction-bearing changes.
- **Codex orchestration:** Codex guidance now makes named-agent dispatch and warm-agent lifecycle behavior explicit while keeping generated role artifacts in sync.
- **Planning changes:** The plan-change protocol now sweeps header fields after task-block edits so scope, output, and methodology stay current.
- **Docs and harnesses:** README, Mermaid workflow diagram, Codex adapter guidance, generated artifacts, and contract tests now align with Protection / Sync / Integrate terminology.

### Fixed

- Tightened the Phase B upstream-intent contract and retired legacy Phase B / Upstream Intent / merge-quality / refactor-owned drift-test surfaces in favor of semantic-merge, result-protection, and refactor-and-integrate ownership boundaries.
- Reduced duplicated dispatch and direct-mode instructions by keeping generated artifacts tied to canonical agent sources.

### Release Prep

- Version manifests are bumped to `0.1.2` across package, Claude, Cursor, Codex, marketplace, and Gemini extension metadata.
- Plan and results are archived under `docs/plans/2026-04-24-semantic-sync-integration-redesign-{plan,results}.md`.

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
