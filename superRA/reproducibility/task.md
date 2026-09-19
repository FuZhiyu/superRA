---
title: "Reproducibility: Task-Declared Build Graph with Make-Like Reruns"
status: revise
depends_on: []
---

## Objective

Deliver the 0.5 reproduction upgrade under the [dependency and reuse design](attachments/v05-design.md): one hierarchical dependency model, selective content-based rebuilds, reviewed acceptance as fresh, and task/step dashboard views. Verify the upgrade on an isolated existing project; BondElasticity remains postponed.

### Context

- **Engine: pytask 0.6.** Steps are generated in memory from task files and executed through `pytask.build(tasks=...)`; no `task_*.py` files exist in a project. pytask supplies sha256 content hashing with no size cap, early cutoff within a run, `--dry-run --explain`, the portable TOML `pytask.lock`, and `pytask-parallel`.
- **Declaration home: a `## Reproduction` section per task whose entire body is one fenced YAML block.** Frontmatter stays `title` / `status` / `depends_on`. Presence of the section registers the task; `tier: required` opts its steps into the default build and completion checks; `tier: on-demand` (the default) registers them for explicit execution. Accept `canon` and `local` as legacy input aliases. Project-wide config (variables, runner templates, env deps, code roots) lives under a `reproduction:` key in `superRA/config.yaml`. The YAML in both places is a bounded subset the stdlib parser reads. Schema: [01-section-contract](01-section-contract/task.md); compatibility and scoped verification: [11-scoped-verification](11-scoped-verification/task.md).
- **Dependency contract:** the [0.5 design](attachments/v05-design.md#one-task-dag-combines-both-sources-of-dependency) governs inferred and logical edges, hierarchy, validation, and task readiness. Steps remain the execution units; inferred task prerequisites are never duplicated in frontmatter.
- **Staleness is content-based.** A persistent cache keyed on size and mtime (no inode: Dropbox does not preserve it) makes a downstream-only run cost a `stat` per file. Sidecar tracking is a per-output opt-in for very large intermediates. Machine-specific files (sysimages) are never dependencies.
- **The committed lock keys nodes by logical path.** Lock ids are the variable-form paths (`${OUT}/…`) so they do not embed an author or branch; hashing happens on the paths resolved for the invocation. Root changes invalidate through changed content or resolved commands; equal-content relocation alone preserves freshness.
- **Ownership split.** `task-tree` owns the mechanics: section schema, parser, `superra repro` CLI, `task read` / `task check` / dashboard integration, hook. The new `reproducibility` utility skill owns the discipline: when to register, tiers, the hashing model agents must understand, boundary inputs, check steps, graph review, and the Protect / completion duties.
- **Enforcement:** instructions, a `task check` category, scoped verification before claiming a result, the IMPLEMENT completion gate on required producers and selected protection checks, and a PostToolUse reminder hook.
- **Detection:** agents declare deps/outs in v1; the loader adds Julia `include` closures and configured env deps. A file-open tracer is a postponed follow-up.
- **Pilots:** TreasuryGIV first (orchestrator steps only; upstream construction as external inputs; sandbox-rooted builds), BondElasticity after.

### Constraints

- The task-tree core stays stdlib-only with lazy `pyyaml`; pytask is a PEP 723 dependency of the runner entry script only, and every other command must work without it.
- Contributor gates in [CLAUDE.md](../../CLAUDE.md) apply to every task: the three-test instruction gate for `skills/*`, `skill-creator` loaded before editing any `SKILL.md`, one concern per commit.
- Skill loads for this tree: `superRA:task-tree` for every task touching `skills/task-tree/`; `superRA:communicate` `references/markdown.md` for every markdown edit.

## Details

### Exploration synthesis (2026-09-02)

- **Both pilot repos keep outputs in Dropbox, where mtimes are unreliable.** TreasuryGIV recorded Smart Sync reverting in-flight writes to stale cloud copies; BondElasticity observed mtime churn making Snakemake rules look dirty. Content hashing is required, which rules out mtime-based tools and Snakemake's default 1 MB checksum cap.
- **Survey of engines** (tested on this machine with 5 MB intermediates): pytask 0.6 and DVC hash without a cap and stop cascades when a rerun regenerates identical bytes; Snakemake 9 falls back to mtime above 1 MB and has no early cutoff; doit misses command edits; DVC changed owners in late 2025 with no release since. Julia startup with a sysimage is ~4-5 s per process, so one process per step is acceptable. sha256 runs at ~2 GB/s here.
- **pytask facts verified in source:** `pytask.lock` lives at the config root; ids are project-relative via `os.path.relpath`; symlinks are not resolved on macOS or Linux, so TreasuryGIV's `output/` symlink keeps relative ids; `pytask lock accept|reset|clean` exists (an adoption path for later); task code state is hashed per task-module file, so generated tasks must carry a per-step spec hash as a `PythonNode` dependency.
- **BondElasticity lessons** (`.plan/` records in that repo): lock what the paper shows, not intermediates; never hash PNGs, track a deterministic CSV companion; declared-but-unproduced outputs surface only in from-scratch builds; keep the interpreter pin in one place; a non-reproducible artifact belongs at the graph boundary; gate destructive wipes with a dry-run diff.
- **TreasuryGIV structure:** 44 orchestrator steps in `Code/run_all_results.jl`, ~9 min end to end with the sysimage, 68% estimation. Output paths depend on `TREASURYGIV_WRITE_CANONICAL` plus author and branch slugs; reads prefer the sandbox mirror when it exists. Steps 13 and 25 read sandbox-only paths; steps 17-19 and 11-12 share output directories; step 38 reads two artifacts whose producers are commented out. Existing tests are four standalone Julia scripts with CSV baselines.
- **superRA touch points** for the pipeline requirement today: `superplan/references/build-and-review.md` (pipeline file, self-review item 3), `econ-data-analysis/references/planning.md` §Pipeline File (a duplicate), `theory-modeling/references/planning.md` item 5, `superimplement/references/completion.md` §3, `superintegrate/references/{protect,integrate,finish}.md`, `result-protection/SKILL.md`, `implement-task/SKILL.md`, `using-superra/SKILL.md` Stage table (pinned by `tests/harness-instruction-following/test_contract.py`), `CATEGORIES.md`, `README.md`.

## Critical Files

- [skills/task-tree/scripts/_task_io.py](../../skills/task-tree/scripts/_task_io.py) — task parsing and the fence-aware section splitter every reproduction reader builds on
- [skills/task-tree/scripts/cli.py](../../skills/task-tree/scripts/cli.py) — subcommand wiring; `superra repro` and the `task read` / `task check` extensions land here
- [skills/task-tree/scripts/plan_dashboard.py](../../skills/task-tree/scripts/plan_dashboard.py) and [templates/dashboard.js](../../skills/task-tree/scripts/templates/dashboard.js) — API routes and the client the Reproduction view extends
- [skills/task-tree/references/task-file-contract.md](../../skills/task-tree/references/task-file-contract.md) — the section vocabulary the new section joins
- [CLAUDE.md](../../CLAUDE.md) — ownership table and the instruction gate every skill edit passes

## Results

### 0.5 planning and release preparation

The [design](attachments/v05-design.md) records the researcher decisions and the implementation contract. Work stays with its existing owners: [effective graph](01-section-contract/unified-dependencies/task.md), [impact and acceptance](02-runner/reviewed-acceptance/task.md), [dashboard navigation](04-dashboard-view/scalable-navigation/task.md), [workflow guidance](07-workflow-integration/unified-dependency-workflow/task.md), and [compatibility evidence](08-pilot-treasurygiv/v05-compatibility/task.md).

The Claude, marketplace, and Codex plugin manifests are at 0.5.0; [release notes](../../RELEASE-NOTES.md) mark it unreleased and distinguish existing reproduction features from planned changes. The interrupted UI experiment was removed from runtime source. The following results document the earlier implementation and do not certify the 0.5 contract.

Planning verification passed: task-tree structural checks, Markdown render checks, local-link checks for the new design/tasks, plugin packaging checks, and synchronized-version checks. Independent design review returned APPROVE after stale inherited contracts and the logical-only dashboard empty-state requirement were corrected. The subsequent archived-task refinement excludes archived work and warns active downstreams; it received structural and Markdown self-checks without another independent pass. Runtime implementation remains queued on the effective-graph task.

### Earlier implementation evidence

superRA projects now carry one reproduction graph inside the task tree, and TreasuryGIV runs on it: `superra repro build --tier canon` rebuilds only what changed, the dashboard shows the graph for review, and the workflow keeps it current. Each line points at the task that holds the detail.

- **Contract and library.** A `## Reproduction` section whose body is one YAML block registers a task's steps; the library parses the bounded subset, builds the graph, derives task edges, and expands Julia `include` closures. [01-section-contract](01-section-contract/task.md)
- **Runner.** `superra repro build | status | explain | dag | tier` over pytask 0.6, with a size-and-mtime hash cache, logical `${VAR}` lock ids, check steps, and sidecars; only `build` needs pytask. [02-runner](02-runner/task.md)
- **CLI surfaces.** `task read` shows a task's steps and derived edges, `task check` validates the graph, `task tree` badges canon tasks. [03-task-interface](03-task-interface/task.md)
- **Dashboard.** A Reproduction view with per-step state and task-section comments; scalable grouping and navigation remain in progress. [04-dashboard-view](04-dashboard-view/task.md)
- **Reminder hook.** A producer edit without a step update draws one PostToolUse reminder per session. [05-reminder-hook](05-reminder-hook/task.md)
- **Discipline.** The `reproducibility` skill: rerun model, graph authoring, Protect and completion duties. [06-skill](06-skill/task.md)
- **Workflow wiring.** The graph replaces the pipeline-file requirement at PLAN, IMPLEMENT, and INTEGRATE, and the `protection` stage loads the skill. [07-workflow-integration](07-workflow-integration/task.md)
- **Pilot.** TreasuryGIV registered 49 steps in 21 tasks with canon narrowed to the internal master deck; the pilot fixed the include resolver and added two authoring rules. [08-pilot-treasurygiv](08-pilot-treasurygiv/task.md)

- **Scoped verification and adoption.** Clear tier names, selected checks, bounded pilots, and separate targeted/complete forced reruns, with producer identity shared across path aliases and hashing limited to selected work. Both Astra/high reviews approved the fixes. [11-scoped-verification](11-scoped-verification/task.md)

### Open for the next round

- The BondElasticity migration ([09-pilot-bondelasticity](09-pilot-bondelasticity/task.md)) and `repro trace` ([10-trace](10-trace/task.md)) stay postponed.
- The superRA plugin installed for other projects predates this tree; until it is refreshed, `superra repro` and the skill reach them only through `SUPERRA_REPO_ROOT`.
