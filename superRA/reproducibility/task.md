---
title: "Reproducibility: Task-Declared Build Graph with Make-Like Reruns"
status: in-progress
depends_on: []
---

## Objective

Give superRA projects one reproduction graph that agents author inside the task tree, a runner that rebuilds only what changed, a dashboard view the researcher reviews and comments on, and workflow duties that keep the graph current. Prove it on TreasuryGIV, then BondElasticity.

### Context

- **Engine: pytask 0.6.** Steps are generated in memory from task files and executed through `pytask.build(tasks=...)`; no `task_*.py` files exist in a project. pytask supplies sha256 content hashing with no size cap, early cutoff within a run, `--dry-run --explain`, the portable TOML `pytask.lock`, and `pytask-parallel`.
- **Declaration home: a `## Reproduction` section per task whose entire body is one fenced YAML block.** Frontmatter stays `title` / `status` / `depends_on`. Presence of the section registers the task; `tier: canon` opts its steps into the default build, `tier: local` (the default) registers them as allowed-stale. Project-wide config (variables, runner templates, env deps, code roots) lives under a `reproduction:` key in `superRA/config.yaml`, a new general superRA project-config file that later work may extend with other scattered configuration. The YAML in both places is a bounded subset the stdlib parser reads. Schema: [01-section-contract](01-section-contract/task.md).
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
