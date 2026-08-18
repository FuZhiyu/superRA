# superRA Release Notes

## [Unreleased]

## [0.4.0] - 2026-08-18

The lean-workflow release. Roles become skills, review becomes a decision rather
than a schedule, interactive execution becomes the default, planning settles
decisions by grilling the researcher instead of collecting sign-offs, and
everything agents write is governed by one reporting contract.

### Changed

- **Interactive execution is now the default mode.** On a built tree the main agent works the frontier itself through the canvas loop — no `superimplement` load, no dispatch (`using-superra/references/interactive-mode.md`, `main-agent.md` §Execution Modes). `superimplement` is re-scoped as the explicitly-entered **autonomous** mode, loaded on researcher request or an accepted one-line recommendation; the agent recommends it when the frontier is broad, parallelizable, or context-heavy, and never switches silently.
- **Independent review is triggered, not scheduled.** Whoever orchestrates decides after a task completes, from the result's stakes and plausibility (`main-agent.md` §Deciding on Review): review on a researcher request, a planner high-stakes mark, an implementer concern, or a load-bearing result the evidence cannot settle; recommend-and-ask when the researcher is present. With no review, the orchestrating agent verifies the work itself and sets `approved`. `implemented` now means "approval decision still open," not "waiting for a reviewer." One thorough review of accumulated work at the INTEGRATE boundary remains the safety net. A commit landing `status: approved` records the tier and focuses the task was reviewed under, or that no independent pass ran.
- Implementer and reviewer are now **skills**, not dedicated agents. A dispatch prompt names `superRA:implement-task` or `superRA:review-task`; that skill pulls in `using-superra` and the manifest's stage and domain skills. A seat the main agent fills itself loads the same skill. One dispatch mechanism now serves Claude Code and Codex.
- **A review is an explicitly scoped pass.** Dispatch names a `Tier:` (`quick`, the default, or `thorough`) and a `Focus:` (`correctness` by default, plus `scope-fidelity` and `results-writing`); the reviewer records both. Verification is evidence-first — the committed diff, outputs, logs, and figures — and re-executing the work's code path is a bounded exception, not routine. Every finding carries a `file:line`, artifact path, or quoted line; findings are reported rather than pre-filtered, with severity adjudicated downstream. Re-review rounds report blocking findings only.
- **One severity vocabulary repo-wide.** CRITICAL/MAJOR/MINOR is retired in favor of `[BLOCKING]` / `[ADVISORY]` across task findings, every gated checklist, and planning review. The checklists were recalibrated in the same pass (294 → 259 blocking, 76 → 68 advisory), cutting duplication and verification scaffolding while keeping the domain-substantive gates — merge validation, look-ahead bias, proof verification — intact.
- The always-loaded **`communicate` skill** now governs human-facing writing, rewriting, distillation, and review. It leads with the answer or honest current state, reveals evidence and caveats before implementation details, and defaults to short nested pyramids. On-demand references cover sentence style, structural rewrites, friction audits, Markdown mechanics, figures, and standalone-report IO; academic manuscripts compose it with `academic-writing`.
- The academic-prose skill is now **`academic-writing`** (`superRA:academic-writing`); its protocol is unchanged.
- `report-in-markdown` is retired. Its render checker and Markdown references moved under `communicate` without changing checker behavior, and active callers now point to the new owner.
- Agents also carry a scope contract (`implement-task` §Work Defaults): deliver what was asked at the scope intended, and when the request seems mistaken, say so in a sentence and continue as asked rather than quietly narrowing or widening the work. Planners mark deliberately open-ended tasks in the objective; otherwise the artifacts the objective names are the scope.
- **Planners cut tasks by edit surface.** Children editing the same files or reloading the same context are one task, however many concerns it serves; the granularity self-review item now prescribes merging as well as splitting, and a shared edit surface is a merge finding rather than a `depends_on` finding. A task's fixed cost is its contract, results record, verdict, and researcher reading time — paid in every execution mode, not just when it is dispatched. Three or more tasks modifying one critical file is a re-cut signal. No numeric task-count caps.
- **The frontier no longer stalls behind deferred work.** A dependency counts as satisfied once its work product exists — `approved`, `archived`, `implemented`, or `revise`; only `not-started`, `in-progress`, and `postponed` block. A subtree whose children are all implemented or approved rolls up as `implemented`, so a branch dependency unlocks its dependents like a leaf does. Open `revise` tasks in the tree are the durable deferral record.
- **Skill prose is terse across the repo.** Every skill and reference was restyled to the register of the role skills — bolded imperative plus short elaboration, definition bullets, no rationale clauses — and `CLAUDE.md` now carries the style spec and the "Teach the Protocol, Don't Prescribe Each Action" gate that keeps new instruction lines from re-inflating it.
- **Planning grills; the domain approval gates are gone.** `superplan` puts every unsettled decision to the researcher in frontier-ordered rounds, each question carrying its recommended answer as the first option (`superplan/references/grilling.md`). Facts the environment holds are the agent's to read or explore; a fact only work can produce is a task boundary, split with `depends_on` and re-grilled when the evidence lands. The four domain planning sign-offs — econ-data-analysis's inventory presentation, theory-modeling's approval step, academic-writing's hard gate, slide-design's pre-decomposition recording — are replaced by a §Frontier Contributions list in each domain's planning reference. Grilling runs by default at standard and thorough depth, and on any request to grill, stress-test, or interrogate an idea.
- **`## Planner Guidance` is now `## Details`, and one test sorts the two body sections.** Binding content — what a reviewer rejects work against — goes in `## Objective`; everything else is information and goes in `## Details` (`task-tree/references/task-file-contract.md` §Task Anatomy). Because a task read injects an ancestor's objective and nothing else, that test also decides what a subtree inherits, and each skill classifies its own artifacts against it. Existing trees keep working: the old heading parses as `Details` indefinitely, with no warning and no file rewrite, and `superra task create` takes `--details` with `--guidance` as an alias.
- **Generic agent dispatches must state their model.** `agent-orchestration` owns one default call shape, `Agent(model: …, prompt: …)`, and `codex-instructions.md` maps it to Codex's `model` plus `reasoning_effort`; inheritance is not a choice. A shared `PreToolUse(Agent)` hook (`hooks/agent-model-guard`) denies a generic dispatch that omits those controls and tells the caller which argument to supply, passing named and specialized agents through untouched. It carries no model allowlist — each harness validates its own values. Claude Code enforcement is verified end to end; Codex CLI 0.147.0 starts `spawn_agent` without emitting `PreToolUse`, so the wiring follows the documented contract but that runtime bypasses it (`tests/hooks/codex-agent-model-live.sh`).
- **Hooks enforce the writing contract and the approval gate.** Markdown mutations through `Edit`, `Write`, Codex `apply_patch`, and supported Bash forms require `superRA:communicate` first (`hooks/ensure-communicate`), and every Markdown edit under a task tree gets one non-blocking reminder to apply it when the text is user-facing. Setting `status: approved` on a task whose `## Review Notes` still holds a `[BLOCKING]` finding is denied (`hooks/guard-task-approval`). The two Skill companion gates merged into one table-driven `hooks/ensure-companion`. All of them fail open on unreadable input.
- **Worktree data seeding is fast, precise, and loud.** `--mode seed` routes each managed root through a stat-only preflight: a clean fresh root is one wholesale `cp -c -R` instead of a subprocess per file (~0.3s vs ~15.5s on 2,000 files), directories holding cloud-placeholder files are rebuilt with per-file symlinks, and a mostly-placeholder root seeds per file and suggests annotating it `# data-sync:symlink` rather than switching behavior. Failures are listed per path on stderr and exit nonzero, replacing a swallowed `errors=N` counter that exited 0. Discovery gained a built-in denylist (venvs, caches, build dirs, harness-local state) that an explicit annotation overrides, and stops re-collecting symlinks git already tracks. `--from` now defaults to the worktree containing the caller, so the old "always pass `--from`" workaround is retired from the orchestration references.

### Removed

- The prototype agent files (`agents/implementer.md`, `agents/reviewer.md`), the generated Codex named agents (`.codex/agents/superra_*.toml`), the `codex-superra-setup` skill and its generator, and the canonical-role resolver (`using-superra/scripts/resolve_role.py`, `references/canonical-role.md`, `references/claude-instructions.md`).
- **Codex users who installed the named agents globally:** a session that finds the now-stale files (`~/.codex/agents/superra_*.toml`) deletes them with your confirmation (or remove them by hand: `rm -f ~/.codex/agents/superra_implementer.toml ~/.codex/agents/superra_reviewer.toml`). Nothing replaces them; the skills bundle carries the roles.

### Release Prep

- Version manifests bumped to `0.4.0` across the maintained Claude,
  marketplace, and Codex plugin metadata via `scripts/bump-version.sh`.

## [0.3.6] - 2026-08-02

### Changed

- Dashboard file links, task attachments (both their links and the reading
  pane's `Open` button), the task card's `Open` button, and the header `VS Code`
  button now open the file on the machine running the dashboard, in whatever
  application that machine already uses for the file type; the header button
  opens the active task's file in the VS Code window already holding that
  worktree, and `SUPERRA_EDITOR` points it at a fork. Opening is served by a
  loopback-only route, so an off-loopback `--host` bind, doc-mode, and
  standalone exports keep the previous `vscode://` links, as do modifier and
  middle clicks anywhere.
- The browser tab now names the page it is showing — the active task, or the
  attachment being read — followed by the worktree branch it lives in, so tabs
  of several worktrees of one repo are no longer identical. Doc-mode and
  standalone exports name the site or export in place of a worktree, which gives
  the published documentation site per-page titles.

### Release Prep

- Version manifests bumped to `0.3.6` across the maintained Claude,
  marketplace, and Codex plugin metadata via `scripts/bump-version.sh`.

## [0.3.5] - 2026-07-26

### Changed

- Tasks now keep retained task-local companion files in `attachments/`, with a
  documented lifecycle for reproduction, promotion, maturation, and
  consolidation.
- Live and standalone task-tree dashboards expose those attachments as a
  navigable, full-width reading surface for supported text, code, notebook,
  image, and PDF files.

### Release Prep

- Version manifests bumped to `0.3.5` across the maintained Claude,
  marketplace, and Codex plugin metadata via `scripts/bump-version.sh`.

## [0.3.4] - 2026-07-23

### Changed

- Execution modes are now two coherent modes instead of three mismatched
  presets ([PR #50](https://github.com/FuZhiyu/superRA/pull/50)). **subagent**
  (default, autonomous) routes through `agent-orchestration`, which owns the
  three seat structures; when the main agent fills a seat it runs that seat's
  role spec. **interactive** (the `direct` alias) has the main agent execute the
  task itself at high human cadence and ask before dispatching a reviewer. The
  `manual` preset is retired — main-fills-both is served by interactive with
  review deferred.
- The interactive canvas loop is self-contained (it loads no role specs) and now
  makes *keep the task updated* and *ask before review with a tool* required
  steps. Retroactive capture is reframed around its real trigger — writing up
  work already done — routed through the same loop. The generated direct-mode
  role mirrors are retired; the named Codex agents remain generated from the
  canonical role specs.
- The `superplan` SKILL.md spine was tightened (Depth Tiers rendered as a table);
  phase choreography and review gates remain owned by the spine.
- Economic-data work now assesses committed diagnostics and outputs first,
  re-executes when a discrepancy is suspected, limits fix iterations to the
  changed step and its downstream dependents, and presents headline findings
  visually unless a figure would not clarify them.
- Prose-specific test oracles were removed conservatively: authored instruction
  wording, labels, and layout are no longer regression contracts, while cheap
  mutation, status, schema, identity, ordering, and secret-exposure checks
  remain. The cleanup adds no live harness, network, or production testability
  infrastructure.

### Release Prep

- Version manifests bumped to `0.3.4` across the maintained Claude, marketplace,
  and Codex plugin metadata via `scripts/bump-version.sh`.

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
- Frontend refreshes do less redundant work: sidebar filtering is debounced and
  runs in a single pass, children-panel caches invalidate when task titles
  change, and opening the worktree selector refreshes discovery without
  rebuilding unchanged options or causing visible flicker.

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
