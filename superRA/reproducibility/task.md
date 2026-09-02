---
title: "Reproducibility: Task-Declared Build Graph with Make-Like Reruns"
status: not-started
depends_on: []
---

## Objective

Give superRA projects one reproduction graph that agents author inside the task tree, a runner that rebuilds only what changed, a dashboard view the researcher reviews and comments on, and workflow duties that keep the graph current. Prove it on TreasuryGIV, then BondElasticity.

### Context

- **Engine: pytask 0.6.** Steps are generated in memory from task files and executed through `pytask.build(tasks=...)`; no `task_*.py` files exist in a project. pytask supplies sha256 content hashing with no size cap, early cutoff within a run, `--dry-run --explain`, the portable TOML `pytask.lock`, and `pytask-parallel`.
- **Declaration home: a `## Reproduction` section per task whose entire body is one fenced YAML block.** Frontmatter stays `title` / `status` / `depends_on`. Presence of the section registers the task; `tier: canon` opts its steps into the default build, `tier: local` (the default) registers them as allowed-stale. A `config` key (variables, runner templates, env deps, code roots) may appear in any task's section and governs that task's subtree, nearest ancestor winning; project-wide config sits in the umbrella `superRA/task.md`, which the shared-context rule permits creating for this purpose. The YAML is a bounded subset the stdlib parser reads. Schema: [01-section-contract](01-section-contract/task.md).
- **Build unit is a step, never a task.** Step-to-step edges are inferred from files. Task `depends_on` stays sibling-only orchestration; task-level reproduction dependencies are derived from step files for display and consistency checks, never declared.
- **Staleness is content-based.** A persistent cache keyed on size and mtime (no inode: Dropbox does not preserve it) makes a downstream-only run cost a `stat` per file. Sidecar tracking is a per-output opt-in for very large intermediates. Machine-specific files (sysimages) are never dependencies.
- **The committed lock keys nodes by logical path.** Lock ids are the variable-form paths (`${OUT}/…`) so they do not embed an author or branch; hashing happens on the paths resolved for the invocation. Switching roots therefore reports stale honestly and never rewrites ids.
- **Ownership split.** `task-tree` owns the mechanics: section schema, parser, `superra repro` CLI, `task read` / `task check` / dashboard integration, hook. The new `reproducibility` utility skill owns the discipline: when to register, tiers, the hashing model agents must understand, boundary inputs, check steps, graph review, and the Protect / completion duties.
- **Enforcement:** instructions, a `task check` category, the IMPLEMENT completion gate on `repro status --tier canon`, and a PostToolUse reminder hook.
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

## Review Notes

Planning review, design-review mode, over the parent and all ten children. `superra task check` is clean; the findings below are design and dependency issues the structural check does not see.

### [BLOCKING]

1. **The root-task `config` home contradicts the umbrella-optional contract.** `### Decisions` and [01-section-contract](01-section-contract/task.md) place `vars` / `runners` / `env_deps` / `code_roots` in `superRA/task.md` only, and make "a non-root task carrying `config`" a validation finding. [task-file-contract.md §Tree Shape](../../skills/task-tree/references/task-file-contract.md#L7) states the umbrella is optional and "an ordinary task, not a privileged one" — a decision the `task-tree` subtree landed and recorded in [its `## Results`](../task-tree/task.md). A project with no umbrella task has nowhere to put reproduction config. Fix: give config a home that does not require the umbrella (a sidecar file, or the nearest ancestor task carrying `config`), or reopen the umbrella-optional decision explicitly.

2. **A committed `pytask.lock` and sandbox-rooted outs cannot both hold.** [02-runner](02-runner/task.md) commits the lock at a fixed project-relative path, and ids are `os.path.relpath` from the config root. [08-pilot-treasurygiv](08-pilot-treasurygiv/task.md) routes `${OUT}` to `output/sandbox/<email-local-part>/<branch>/`, and [01-section-contract](01-section-contract/task.md) applies `${VAR}` interpolation to `outs` — so every out id embeds an author and a branch, and the committed lock churns per author and per branch. That defeats the portable lock that motivated the engine choice. Fix: decide whether the lock is committed only for canonical builds, gitignored, or whether out ids stay canonical with sandbox routing applied below the id; pin the project root and the lock path in the contract while deciding.

3. **[06-skill](06-skill/task.md) cannot meet its acceptance criterion at its declared dependency point.** Its validation requires "an agent given only this skill and a fixture project registers a two-step pipeline that `repro build` executes", but `depends_on` is `01-section-contract` alone and §Execution order schedules 06 in parallel with [02-runner](02-runner/task.md). Fix: add `02-runner` to 06's `depends_on`, or move the live dry run to [07-workflow-integration](07-workflow-integration/task.md) or [08-pilot-treasurygiv](08-pilot-treasurygiv/task.md).

4. **[04-dashboard-view](04-dashboard-view/task.md) and [08-pilot-treasurygiv](08-pilot-treasurygiv/task.md) form an acceptance cycle.** 04's validation requires "a manual pass on the TreasuryGIV pilot graph … with a screenshot in `attachments/`", while 08 lists 04 in `depends_on` — so 04 cannot reach approval until 08 runs. 08 already carries the same check ("the dashboard Reproduction view renders the graph and one node comment round-trips"). Fix: run 04's manual pass on a fixture graph and leave the real-graph verification in 08.

5. **The stdlib read path has no bounded YAML subset.** `### Constraints` keeps the core "stdlib-only with lazy `pyyaml`" and 01 requires "a stdlib-only (no `pyyaml`) parse of a well-formed section", but [03-task-interface](03-task-interface/task.md), [04-dashboard-view](04-dashboard-view/task.md), and [05-reminder-hook](05-reminder-hook/task.md) all read the section on the bare-`python3` path, and the declared schema uses nested mappings, lists of mappings, and inline maps (`{path: …, sidecar: …}`). Hand-rolling that parser is unbounded scope. The repo hit this before and solved it by writing the comment sidecar as JSON, a strict YAML subset ([_comments.py:179](../../skills/task-tree/scripts/_comments.py#L179)). Fix: pin the supported subset in 01 and constrain the schema to it, reuse the JSON-subset approach, or accept `pyyaml` for reproduction reads and drop the criterion.

6. **[05-reminder-hook](05-reminder-hook/task.md)'s trigger condition is unsatisfiable.** "no `## Reproduction` section changed in the same tool call" is never false: PostToolUse carries one `tool_input.file_path` per invocation ([task_hook.py:475](../../skills/task-tree/scripts/task_hook.py#L475)), so no Edit or Write touches both a producer and a task file. The reminder fires on every producer edit, including the one right after its step was registered, and the "edit-with-section-change (no reminder)" test case is unreachable. Fix: state the suppression window the design means — turn or session — and where that state lives.

### [ADVISORY]

7. **The `canon` never-built finding fires on every fresh clone.** [01-section-contract](01-section-contract/task.md) makes "a `canon` task with a step whose outs are absent" a validation finding and [03-task-interface](03-task-interface/task.md) runs the `reproduction` category by default, so `task check` is dirty on any checkout before the first build. Separate "declared and never produced anywhere" from "not built here".

8. **§Execution order restates `depends_on`.** Every edge in that paragraph is already in the children's frontmatter, and its postponed note is the `status` field. Two copies drift; delete the paragraph.

9. **`tier: task` collides with "task", the tree unit.** `--tier task`, "task-level edges", and "the task's tier" land in adjacent sentences. A value such as `local` reads unambiguously.

10. **`### Decisions` is off the objective subsection vocabulary.** [task-file-contract.md §Task Anatomy](../../skills/task-tree/references/task-file-contract.md#L15) names `### Context` / `### Conventions` / `### Constraints`, and §Stale Content Checklist names "a 'Decisions' section" as content to fold into the objective or its constraints. Several bullets there are already constraints ("machine-specific files … are never dependencies"; "task `depends_on` stays sibling-only orchestration").

11. **[08-pilot-treasurygiv](08-pilot-treasurygiv/task.md) bundles four review units** — worktree setup, registering 44 steps with tiers, a six-clause verification, and a cross-repo defect-routing protocol. Consider splitting registration from verification-and-harvest.

12. **Stale line citation.** [04-dashboard-view](04-dashboard-view/task.md) cites `dashboard.js#L2246`; `buildChildFlow` is at line 2252.
