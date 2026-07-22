# superRA Release Notes

## [Unreleased]

## [0.3.3] - 2026-07-22

### Changed

- Dashboard hardening from [PR #46](https://github.com/FuZhiyu/superRA/pull/46)
  now keeps live and standalone rendering on explicit per-worktree state, with no
  legacy module-global render state or export snapshot/restore path. The dead
  giant-tree routes and templates are gone, and the children dependency panel
  consumes structured JSON instead of parsing Mermaid source.
- Dashboard CSS and JavaScript are split into cacheable static assets for live
  mode and inlined into standalone exports. Live rendering no longer depends on
  network access for htmx or SSE because those libraries are served from the
  local vendor bundle; Google Fonts retain the existing system-font fallback.

### Fixed

- Dashboard content now crosses one explicit trust boundary: task titles and
  previews display HTML literally, Markdown bodies retain supported HTML only
  through DOMPurify, and dynamic selectors and click targets safely handle
  punctuation in task content.
- Slow dashboard operations run off the event loop, parse failures surface as
  visible error state instead of stale content, slow SSE clients leave accurate
  connection bookkeeping, and watcher teardown remains bounded under repeated
  cancellation and abrupt disconnects.
- Relative Markdown images preserve the selected worktree query parameter, so
  `/files` returns bytes from the active worktree even when worktrees share a
  basename ([issue #47](https://github.com/FuZhiyu/superRA/issues/47)).
- Reconnecting after the last dashboard client disconnects rebuilds that
  worktree's cached task state and sends a worktree-scoped full reload. Offline
  edits appear immediately, while an already-live watcher emits no duplicate
  refresh ([issue #48](https://github.com/FuZhiyu/superRA/issues/48)).

### Release Prep

- Version manifests bumped to `0.3.3` across the maintained Claude,
  marketplace, and Codex plugin metadata via `scripts/bump-version.sh`.

## [0.3.2] - 2026-07-20

### Fixed

- Dashboard launch and reuse URLs retain the canonical URL-encoded worktree
  selector, including collision disambiguation, so a repository-shared server
  opens the worktree that invoked it.

### Removed

- Retired the unmaintained upstream Superpowers package, OpenCode plugin,
  Gemini extension manifest, changelog, and upstream-only documentation and
  tests. Version checks now cover the maintained Claude, marketplace, and
  Codex manifests only.

### Release Prep

- Version manifests bumped to `0.3.2` across the maintained Claude,
  marketplace, and Codex plugin metadata via `scripts/bump-version.sh`.

## [0.3.1] - 2026-07-11

### Fixed

- Dashboard watcher teardown is bounded across cooperative stop, task
  cancellation, and a detached-process fail-safe. Repeated abrupt SSE
  disconnects no longer leave orphaned, CPU-spinning dashboard processes, and
  embedded server threads cannot terminate their host process.

### Release Prep

- Version manifests bumped to `0.3.1` across package, Claude, Codex,
  marketplace, and Gemini extension metadata via `scripts/bump-version.sh`.

## [0.3.0] - 2026-07-01

### Breaking

- **Task tracking model replaced: the `superRA/` task tree supersedes `PLAN.md` / `RESULTS.md`.** A single flat plan/results pair is replaced by a filesystem hierarchy of self-contained `task.md` files, each with a planner-owned `## Objective` and an implementer-owned `## Results` (recursive at every level, including nested subtasks) — `superRA/` task files are now the primary researcher-facing results record, and the old separate `RESULTS.md` / `final-form.md` maturation path is gone. Dependencies are sibling-only; parent status rolls up from children automatically. A live dashboard (`superra dashboard`) — tree, DAG, and kanban views, multi-worktree support, SSE live-updating, exportable offline snapshot — replaces the flat file as the human-facing status view. Top-level tasks are unprivileged: a `superRA/task.md` umbrella is optional, added only when a shared objective genuinely spans every top-level task.

### Migration

- Existing projects on `PLAN.md` / `RESULTS.md` keep working: superRA detects a legacy `PLAN.md` without a `superRA/` tree at session start and offers to migrate it via `superra task migrate from-plan`.
- To stay on the previous model instead, pin the install to the frozen `v0.1.2` tag:
  ```bash
  claude plugin marketplace add FuZhiyu/superRA@v0.1.2
  claude plugin install superRA@superRA
  ```
- See the [superRA docs](http://fuzhiyu.me/superRA/) for full migration details.

### Added

- **`postponed` task status.** New value for `task.md` `status` frontmatter that parks a task off the dispatch frontier without deleting it: a `postponed` leaf never enters the frontier, and a `postponed` task is excluded from the dashboard completion-% denominator — both mirroring `archived`. It differs from `archived` in dependency satisfaction: `archived` lets dependents proceed, while `postponed` **blocks its dependents** until the task is resumed, so `task_check.py` warns when a task depends on a postponed sibling. An all-parked branch rolls up to `postponed` if any child is postponed (else `archived`). The dashboard gains a Postponed kanban column and status badge. Set by the orchestrator / researcher as a scope-deferral decision; resume by setting the status back to `not-started`.

### Release Prep

- Version manifests bumped to `0.3.0` across package, Claude, Codex, marketplace, and Gemini extension metadata via `scripts/bump-version.sh`. The minor bump (rather than a patch) marks this pre-1.0 breaking change.
- The Cursor plugin manifest (`.cursor-plugin/plugin.json`) was removed — Cursor plugin packaging is no longer maintained. Hook scripts keep their Cursor-compatible output branches.

## [0.2.0] - 2026-05-30

### Breaking

- **Workflow phase skills renamed to escape a namespace collision** with Claude Code's new Workflow tool / `/workflows`: `planning-workflow` → `superplan`, `implementation-workflow` → `superimplement`, `integration-workflow` → `superintegrate`. The skill directories, frontmatter `name` fields, and every cross-reference moved to the new ids; the generic PLAN → IMPLEMENT → INTEGRATE phase vocabulary is unchanged.

### Migration

- Any saved or scripted invocation must switch ids: `Skill(superRA:planning-workflow)` → `superRA:superplan`, `superRA:implementation-workflow` → `superRA:superimplement`, `superRA:integration-workflow` → `superRA:superintegrate`.
- Users who installed the named Codex agents globally should refresh them by rerunning the `codex-superra-setup` skill, since the generated agents were regenerated from the renamed sources.

### Release Prep

- Version manifests bumped to `0.2.0` across package, Claude, Cursor, Codex, marketplace, and Gemini extension metadata via `scripts/bump-version.sh`. The minor bump (rather than a patch) marks this pre-1.0 breaking change.

## [0.1.3] - 2026-05-02

### Added

- **Writing skill redesign.** `skills/writing/` reorganized around three working modes (Review / Polish / Draft) instead of superRA workflow phases, replacing the cloned Iron Law / Three Concurrent Disciplines framing with a single principle (Preserve substance, polish prose); load configuration is now the authority grant (light vs deep polish differ only by whether `structure.md` loads), inline directives default to TODO-as-task / DO-NOT-EDIT-as-hands-off, an intent-comment discipline (`% intent: …`) keeps paragraph purpose in-file across sessions, and reviewer-dispatch invariants now live in workflow skills only. Design rationale captured in `skills/writing/CLAUDE.md`.
- **Theory-modeling skill (alpha).** New domain vertical at `skills/theory-modeling/` for rigorous mathematical-modeling work: derivations, equilibrium setup, symbolic manipulation, proofs, comparative statics, and simple numerical verification. Composes with the existing PLAN → IMPLEMENT → INTEGRATE workflow without changes to workflow skills.
  - **Iron Law:** every symbol has a meaning, every assumption has a plain-language interpretation, every non-trivial derivation move has a one-sentence reason.
  - **Four-gate checklist** (Objects & Notation / Assumptions / Derivations / Verification & Rendering) walked at every implementation dispatch as the creation-time correctness floor. Gates 1 and 2 carry per-symbol and per-assumption ledger entries with explicit slot templates; falsification tests (Substitution test, Proof-deletion test) detect generic justifications.
  - **Stage-scoped references:** `references/planning.md` (Model Inventory / Assumption Map hard gate + Verification Plan), `references/integration.md` (readability layer for reader-ready output — objective-first rewriting, half-page mask test for local obviousness, cross-document coherence, refactor-survival), `references/integrate-drift-tests.md` (drift tests for symbolic identities and numerical baselines), `references/objective-first.md` (worked example + identification drills).
  - **Split:** `SKILL.md` is the creation-time correctness floor (load at every implementation dispatch); `references/integration.md` is the readability layer (load when polishing for a human reader).
  - **`skills/theory-modeling/CLAUDE.md`** records the high-level design choices for future contributors.

### Changed

- Routing surfaces (`skills/CATEGORIES.md`, `README.md`, `using-superra` skill inventory) updated to expose the new vertical.

### Release Prep

- Version manifests bumped to `0.1.3` across package, Claude, Cursor, Codex, marketplace, and Gemini extension metadata via `scripts/bump-version.sh`.
- Plan and results archived under `docs/plans/2026-04-22-theory-modeling-vertical-{plan,results}.md`. Design-choice synthesis lives in `skills/theory-modeling/CLAUDE.md`.

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

- Version manifests are bumped to `0.1.2` across the then-supported plugin metadata.
- Plan and results are archived under `docs/plans/2026-04-24-semantic-sync-integration-redesign-{plan,results}.md`.

## [0.1.1] - 2026-04-22

### Added

- **Three autoload hooks** that keep the superRA skill-load state coherent without requiring the user or the agent to remember it manually:
  - **`autoload-superra`** (`UserPromptSubmit`) — soft reminder. Detects "superRA" (and case/spacing variants like `super RA`, `super-ra`, `Super_RA`) in the user's message and, if `superRA:using-superra` has not been invoked this session, injects an `additionalContext` reminder telling Claude to load the master skill before responding.
  - **`ensure-using-superra`** (`PreToolUse:Skill`) — hard enforcement. When Claude invokes any `superRA:*-workflow` skill and `superRA:using-superra` is not yet loaded, blocks the `Skill` call with `permissionDecision: deny` and a reason directing Claude to load the master skill first and retry.
  - **`ensure-agent-orchestration`** (`PreToolUse:Skill`) — same pattern as above, gating independently on `superRA:agent-orchestration`.
- **Hook test suites.** Per-hook stdin-synthesis drivers (16 vectors each, 48 total) under `tests/hooks/test-{autoload-superra,ensure-using-superra,ensure-agent-orchestration}.sh` covering happy path, suppression after companion-load, trigger-boundary cases, JSON-special characters, fail-open on missing transcript, and deny-reason JSON round-trip. A CLI-driven end-to-end driver (`tests/hooks/test-e2e-cli.sh`, 6 scenarios) validates registration + wiring against the live `claude` CLI on Haiku for ~\$0.27 per run.
- **README §Hooks** table extended to list all six registered hooks.

### Fixed

- **Version drift across plugin manifests.** The then-supported plugin metadata, including a leftover upstream Superpowers manifest, was synchronized at 0.1.1 via `scripts/bump-version.sh`.

### Notes

- All three new hooks follow the existing extensionless-bash convention with a three-way platform-output branch (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback) matching `merge-guard` / `exit-plan-mode` / `ask-user-question-logger`. Reminder text and deny reasons are JSON-escaped via `python3 json.dumps` before splicing into the payload, so inner `"` or `\` cannot invalidate the JSON.
- Scenario S4 of the CLI e2e suite passes opportunistically (it relies on Haiku obeying an in-prompt countermand against the autoload reminder); the disposition path if a future model regresses S4 is documented inline in the test's docstring. The deny logic itself is fully covered by the stdin-synthesis unit tests.
- Plan + results for this change: `docs/plans/2026-04-21-superra-autoload-hooks-{plan,results}.md`.
