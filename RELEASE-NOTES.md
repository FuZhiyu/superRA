# superRA Release Notes

## [0.5.0] - Unreleased

The reproduction upgrade: task-declared build steps that superRA runs itself, content-based reruns, reviewed acceptance, and a dashboard for inspecting how research outputs are produced.

### Upgrading a project that used the reproduction pre-release

**Every coauthor upgrades superRA before the first commit from steps 3 or 4 lands.** An older superRA reads neither `repro-lock.json` nor `repro-acceptance/`, so for a coauthor who has not upgraded, every step reads stale or missing and no accepted step reads fresh.

1. Upgrade superRA on every machine that works on the project.
2. Run `superra task check`.
   - A leftover `tier:` key, in a section or a step, is a warning and is ignored. Tier never entered a step's hash, so existing builds stay fresh.
   - A leftover `env_probe` or `code_roots` key under `reproduction:` in `superRA/config.yaml` is also a warning and is ignored. Delete these keys when convenient.
3. Run a build. It writes `repro-lock.json` and prints the `git rm` that retires `pytask.lock` and `repro-builds.json`, which are read until then. Commit the lock and the removal, and delete the `.pytask/` directory.
4. The first `superra repro accept` converts `repro-acceptance.json` into one file per step under `repro-acceptance/` and deletes it. Commit both changes.

`--tier` and `repro tier` stop with an error naming task targets as the replacement.

### Added

- **Reproduction sections register producers and checks.** A task's `## Reproduction` section declares steps with their `deps` and `outs`; `superra repro build` reruns the steps whose inputs changed and records each successful build in the committed `repro-lock.json`.
- **The dashboard shows how results are produced:** reproduction steps, freshness, file dependencies, and task ownership. Workflow skills register and verify retained results through the `reproducibility` skill.
- **The `onboarding` skill brings an existing project into superRA,** even one without git. The agent writes a task tree and a reproduction graph for the work already done, touching nothing outside `superRA/` until the researcher approves. It then offers git, with a `.gitignore` that keeps data out, and an optional rerun in an isolated worktree that checks each result against its original before merging back.
  - Session start and `superplan` offer onboarding to any project with code, data, or results but no `superRA/`. A legacy `PLAN.md` project enters the same skill, which runs the migration.
  - `superra task create` creates the first task in a `superRA/` that holds only the wrapper.

### Changed

#### Builds and freshness

- **superRA runs builds itself; pytask is no longer a dependency.** `repro build` runs steps as subprocesses in dependency order, `-j N` at a time. A failed step skips its descendants; Ctrl-C, SIGTERM, or SIGHUP stops running steps and records them failed.
  - `status` and `build` decide freshness by one rule: SHA-256 content hashes with no size cap, and a rerun that regenerates identical bytes leaves its consumers fresh.
  - Freshness follows symlinked directories, and a sidecar-tracked saved input counts as verified when its bytes match its producer's record.
  - `status .` and `build . --dry-run` run in about 0.2 s and 0.4 s on a 14-step project, against about 0.8 s under pytask.
- **The lock holds one line per step.** `repro-lock.json` (version 2) writes each step's entry on one line, separated by blank lines, so a git merge takes each entry whole from one side and can no longer mix two builds into a false `fresh`. A conflicted lock still reads: entries the two sides disagree on are dropped and their steps read `missing`; the next build rewrites the lock without markers. `semantic-merge` gives the resolution.
- **Builds include the producer chain by default.** `repro build` and `repro status` require a target: a task path with its descendants, `task#step`, or `.` for every registered step. They also take in the steps that produce the targets' inputs, back to the external inputs, so naming the final result brings it current; a build skips fresh steps and prints the added producers it will run, with their last durations. `--only` restricts a command to the targets and uses files from producers outside them as they sit on disk. `--force` reruns the targets only. `--force-all` is retired, and `--upstream` is a hidden alias for the default.
  - `status` exits 3 when the selected steps are fine but a producer behind them is `stale`, `missing`, or `failed`, and names it. `status X --upstream` therefore exits 3 in that case, where it exited 1 before. Under `--only`, `--json` lists those producers as `behind`.
- **No command downloads a file.** An online-only file (Dropbox, Google Drive, Box, OneDrive, or iCloud through File Provider, or a legacy Dropbox placeholder) is never opened to check it. Its step reads `unverified` unless this machine has already hashed the file; the lock records each file's size, so a File Provider file whose size changed still reads as changed. `build` never runs an `unverified` step and uses its outputs as they are, and `status` exits 0 over it while listing its files with their sizes.
  - **Download gate.** A build that would run a step reading a file not on this machine, online-only or absent with no producer, runs nothing. It lists the files with their sizes and names `--only` as the way to build the rest.
- **Task targets replace reproduction tiers.** The `task tree --tier` filter and badge are removed.
- **A check that passed at these inputs elsewhere reads `fresh`**, with the reason `passed at these inputs in lock <rev> on <platform>; not run here`. A local failure still wins.
- **Scoped build guards.** Unrelated task additions and unused configuration edits no longer abort running steps. Changes to the selected execution contract or input bytes still reject inconsistent success evidence.

#### Readiness and dependencies

- **Only `depends_on` decides readiness.** A task is ready once its `depends_on` prerequisites, own or inherited, are `implemented`, `approved`, or `revise`. File edges between steps order builds and appear in `task read` and `task frontier` as inputs whose producer is `stale`, `missing`, or `failed`; they never gate.
  - A `depends_on` that runs against the file flow is a warning. Only step cycles and `depends_on` cycles are errors; a loop that appears only when file edges are grouped by task is not.
  - `task create`, `move`, `dep add`, and archive transitions print each task they take off the frontier.
- **Reproduction errors block only the builds they touch.** Planning commands and the frontier keep working, with the errors noted on stderr. `build`, `accept`, and `status` refuse on an error in a selected step's own task, a step cycle through a selected step, or project-wide configuration. `build --dry-run` reports a step whose input is missing as `cannot run`.
- **Parents retain their steps.** A task can own build steps and child tasks; adding a child preserves existing step identities and freshness. Archived subtrees leave the active graph, with warnings for their downstream consumers.

#### Reviewed acceptance and diagnosis

- **Reviewed reuse.** `repro accept <targets> --reason '…'` records why current results stand without executing anything, including first registration and outputs from interactive runs; `--dry-run` previews. Valid acceptance reads as `fresh` and preserves the last actual run. Forced verification executes its selected steps; acceptance never claims a step ran again.
- **Acceptance records are one portable file per step,** `repro-acceptance/<step>.json`. Branches that accept different steps merge cleanly, and two clones with different data roots or user names write byte-identical records. A record that does not parse disables only its own step, with a warning.
  - `--apply`, `--evidence`, and the `upstream` record field are removed; records no longer carry `actor`, `recorded_at`, or evidence paths.
  - `accept` skips steps already fresh and never rewrites an unchanged record.
  - Revoking a producer's acceptance leaves a downstream record valid; `status` reports the consumer stale while the producer is not fresh.
- **`.superra-repro/` stays on its machine.** superRA sets Dropbox's ignore flag on the folder, so another machine's in-progress run cannot mark a step failed here. Deleting the folder stales no step.
- **`explain` states the facts the stale rule acts on.** Every lock or git source states its relation to HEAD (HEAD's version, N commits behind, or on another branch). Graph errors on the explained steps are listed and make `explain` exit 1. A file several steps read prints once. A task view prints diff excerpts only with `--diff`. A history cache in `.superra-repro/history.json` makes a repeat call run no `git log`.
- **`impact` covers `superRA/config.yaml` and prints text by default,** one line per affected step with its last recorded duration and why it is affected; `--json` keeps the structured output.

#### Agent workflow

- **The `reproducibility` skill carries the everyday path and routes the rest.** `SKILL.md` defines the model (producer chain, saved input, external input), lists the core commands, and holds the gate for recording a result. Each other situation loads one reference: designing the graph, completion and Protect, the stale rule (rerun or accept), diagnosis, and adoption.
- **The Skill-Load Manifest loads `reproducibility`** for any task that plans, produces, changes, records, or reviews a result computed by code. Interactive self-review walks every loaded skill's gates.
- **The completion gate covers every step and asks before costly reruns:** `status .`, the stale rule, then `status .` again. It passes when every step reads `fresh`, by execution or acceptance, except steps reported to the researcher: those the stale rule left stale, and every `unverified` step. A tree with no steps passes only when no result rests on retained code. A subagent facing a costly rerun returns `DONE_WITH_CONCERNS` with the question in `## Results`.
- **Protect asks which inputs are external;** it no longer selects completion targets. Planners name each artifact and its planned script in the producing task's `## Details`; the implementer registers the step.
- **The edit hook catches every producer edit:** edits through any tool, paths built from `${VAR}` variables, files inside declared directory dependencies, and the first tool call of a session. A new script beside registered ones draws a softer reminder, and a `task.md` edit reports warnings for the edited tasks only.

#### Dashboard

- **The graph opens readable at 80%** on the selected task or step; Fit and Project overview still fit on request.
- **Arrows carrying only `depends_on` edges are dashed.** A task whose declaration has an error gets a red outline and a link to its finding.
- The unused search, trace, and scope modes and the `/dag` route are removed; legacy URLs open the full map. Each finding and edge travels once, cutting the 200-step fixture's payload by 38%.
- **Hovering a file link previews the file:** its size and date, plus the first lines of a text file, an image, or a PDF's first page. This covers a step's inputs and outputs and file links in task text. Images and PDFs over 2 MiB show only their size, and nothing extra loads until you hover.
- **A browser on another machine opens files inside the dashboard.** A phone, or a computer reaching an exposed `--host` server, gets a reading-pane view of the file instead of a `vscode://` link it cannot follow. The browser on the dashboard's own machine still opens files in their default application. That now holds even under `--host 0.0.0.0`, because the check is per browser rather than per bind.
- **Files behind a symlink in the project, and outside paths a `## Reproduction` step declares, can be viewed and opened.** A path containing `..` is refused.

### In preparation

- The dashboard workspace offers Tree and DAG as alternative navigators sharing task selection, the reader, comments, and attachments. Expanding one task level exposes its own steps and child groups; selecting or expanding a node does not change scope.
- UI validation and existing-project compatibility evidence remain required before release. The development version does not imply publication.

### Removed

- The `external` step state. A step whose input no step produces and is absent now reads `unverified`; "external input" still names a file no step produces.
- pytask and `pytask-parallel` as dependencies, the `_repro_hooks.py` plugin, and the `env_probe` and `code_roots` configuration keys, which now warn and are ignored. A lock's legacy probe fields are ignored on read.

### Release Prep

- Claude plugin, marketplace, and Codex plugin manifests are synchronized at `0.5.0` through `scripts/bump-version.sh`; no release tag or publication is implied.

### Fixed

- Dashboard sidebar is resizable by touch: the drag handle now shows on iPad and other coarse-pointer devices, in the pinned layout and on the open drawer, and the chosen width survives the drawer's width cap.
- Dashboard CSS/JS URLs carry a content hash, so a page reload after a server relaunch fetches the current assets instead of the hour-cached copy.

## [0.4.1] - 2026-08-19

### Changed

- `communicate` reworked: the standalone-report IO reference (`references/baseline-io.md`) is retired and its content folded into the remaining references; `rewrite.md` and `markdown.md` tightened.
- The `communicate` load requirement is stated more strictly in `communicate`, `using-superra`, and `main-agent.md`.

### Release Prep

- Version manifests bumped to `0.4.1` across the maintained Claude,
  marketplace, and Codex plugin metadata via `scripts/bump-version.sh`.

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
