---
title: "Reproducibility: Task-Declared Build Graph with Make-Like Reruns"
status: in-progress
depends_on: []
---

## Objective

Own superRA's reproduction graph under the [dependency and reuse design](attachments/v05-design.md): one hierarchical dependency model, selective content-based rebuilds, reviewed acceptance as fresh, and task/step dashboard views. Real-project use supplies the compatibility evidence.

### Context

- **Engine: superRA runs the build itself** ([02-runner](02-runner/task.md)). `superra repro build` walks the selected steps in dependency order, runs each as a subprocess, and runs ready steps on threads under `-j`. `status` and `build` decide freshness by one rule: sha256 content hashes with no size cap, and early cutoff when a rerun regenerates identical bytes.
- **Declaration home: a `## Reproduction` section per task whose entire body is one fenced YAML block** ([01-section-contract](01-section-contract/task.md)). Frontmatter stays `title` / `status` / `depends_on`. Presence of the section registers its steps; task and `task#step` targets select what runs. Project-wide config (variables, runner templates, env deps) lives under a `reproduction:` key in `superRA/config.yaml`. The YAML in both places is a bounded subset the stdlib parser reads.
- **Dependency contract:** the [0.5 design](attachments/v05-design.md#one-task-dag-combines-both-sources-of-dependency) governs inferred and logical edges, hierarchy, validation, and task readiness. Readiness follows `depends_on` only; file edges between steps order builds and are reported as inputs. Inferred prerequisites are never duplicated in frontmatter.
- **Staleness is content-based.** A persistent cache keyed on size and mtime (no inode: Dropbox does not preserve it) makes a downstream-only run cost a `stat` per file. No check downloads a file: an online-only file this machine has not hashed makes its step `unverified`, which `build` never runs. Sidecar tracking is a per-output opt-in for very large intermediates. Machine-specific files (sysimages) are never dependencies.
- **Committed records are portable.** `repro-lock.json` keys nodes by logical `${VAR}` path, one line per step, so it embeds no author or branch; acceptance records are one file per step under `repro-acceptance/`. Root changes invalidate through changed content or resolved commands; equal-content relocation alone preserves freshness.
- **Ownership split.** `task-tree` owns the mechanics: section schema, parser, `superra repro` CLI, `task read` / `task check` / dashboard integration, hook. The `reproducibility` utility skill owns the discipline: when to register or retire steps, the rerun model agents must understand, external inputs, check steps, graph review, the stale rule, and the Protect and completion duties.
- **Enforcement:** instructions, a `task check` category, the claim gate before recording a result, the completion gate over every step, and a PostToolUse reminder hook.
- **Detection:** agents declare deps and outs; the loader adds Julia `include` closures and configured env deps. A file-open tracer is a postponed follow-up ([10-trace](10-trace/task.md)).
- **Pilots are closed.** The archived [TreasuryGIV pilot](08-pilot-treasurygiv/task.md) keeps the adoption lessons; real-project use supplies ongoing evidence.

### Constraints

- The task-tree core, `superra repro` included, stays stdlib-only with lazy `pyyaml`.
- Contributor gates in [CLAUDE.md](../../CLAUDE.md) apply to every task: the three-test instruction gate for `skills/*`, `skill-creator` loaded before editing any `SKILL.md`, one concern per commit.
- Skill loads for this tree: `superRA:task-tree` for every task touching `skills/task-tree/`; `superRA:communicate` `references/markdown.md` for every markdown edit.

## Details

### Why content hashing (2026-09-02 survey)

- **Both pilot repos keep outputs in Dropbox, where mtimes are unreliable.** TreasuryGIV recorded Smart Sync reverting in-flight writes to stale cloud copies; BondElasticity observed mtime churn making Snakemake rules look dirty.
- **Engine survey** (5 MB intermediates): pytask 0.6 and DVC hash without a cap and stop cascades when a rerun regenerates identical bytes; Snakemake 9 falls back to mtime above 1 MB and has no early cutoff; doit misses command edits. Julia startup with a sysimage is ~4-5 s per process, so one process per step is acceptable. sha256 runs at ~2 GB/s. superRA later replaced pytask with its own loop ([02-runner](02-runner/task.md#superra-owns-the-engine)).

## Critical Files

- [skills/task-tree/scripts/_repro.py](../../skills/task-tree/scripts/_repro.py) — section parser, graph model, and validation every reproduction reader builds on
- [skills/task-tree/scripts/repro_run.py](../../skills/task-tree/scripts/repro_run.py) and [_repro_state.py](../../skills/task-tree/scripts/_repro_state.py) — the `superra repro` entry, build loop, freshness, and lock
- [skills/task-tree/scripts/plan_dashboard.py](../../skills/task-tree/scripts/plan_dashboard.py) and [templates/dashboard.js](../../skills/task-tree/scripts/templates/dashboard.js) — graph routes and the Tree/Graph workspace
- [skills/task-tree/references/task-file-contract.md](../../skills/task-tree/references/task-file-contract.md), [commands.md](../../skills/task-tree/references/commands.md), and [internals.md](../../skills/task-tree/references/internals.md) — the mechanics documentation
- [skills/reproducibility/SKILL.md](../../skills/reproducibility/SKILL.md) — the discipline agents follow
- [CLAUDE.md](../../CLAUDE.md) — ownership table and the instruction gate every skill edit passes

## Results

superRA projects carry one reproduction graph inside the task tree: `superra repro build <targets>` reruns only what changed, reviewed acceptance reuses results without rerunning them, the dashboard shows the graph for review, and the workflow keeps it current. [RELEASE-NOTES.md](../../RELEASE-NOTES.md) describes 0.5.0 for users; each line below points at the task that holds the detail.

- **Contract, library, and readiness.** A `## Reproduction` section registers a task's steps; one dependency snapshot serves every task view, and readiness follows `depends_on` only. [01-section-contract](01-section-contract/task.md)
- **Runner.** `superra repro build | status | explain | impact | accept | revoke | dag` on superRA's own engine: builds take in the producer chain, no command downloads a file, and lock and acceptance records are portable. [02-runner](02-runner/task.md)
- **CLI surfaces.** `task read` and `task frontier` show prerequisites apart from inputs whose producer needs a build; `task check` validates the graph and flags unregistered result files. [03-task-interface](03-task-interface/task.md)
- **Dashboard.** A Tree/Graph workspace over one project map that opens readable, marks only real cycles, and shows each step's reported and own state. [04-dashboard-view](04-dashboard-view/task.md)
- **Reminder hook.** Any producer edit, by any tool, draws one reminder naming the steps it stales. [05-reminder-hook](05-reminder-hook/task.md)
- **Discipline.** The `reproducibility` skill: the model, graph design, the claim gate, the stale rule, diagnosis, adoption, and Protect and completion duties. [06-skill](06-skill/task.md)
- **Workflow wiring.** Every phase's call site points to the reference that owns its rule; the manifest loads the skill for any task producing or reviewing a result from code. [07-workflow-integration](07-workflow-integration/task.md)
- **Pilot.** TreasuryGIV registered 49 steps in 21 tasks; the pilot fixed the include resolver and added authoring rules. [08-pilot-treasurygiv](08-pilot-treasurygiv/task.md)

### Open

- `repro trace` ([10-trace](10-trace/task.md)) stays postponed.
- The plugin installed for other projects predates 0.5; until it is updated, `superra repro` and the skill reach them only through `SUPERRA_REPO_ROOT`.
- This repository registers steps only for the [showcase analysis](../showcase-analysis/task.md). Protect retired the reproducibility tree's check steps with the researcher's agreement, so the pytest suite and the documentation carry its protection.
