---
title: "Author the `reproducibility` Utility Skill"
status: approved
depends_on: [01-section-contract]
---

## Objective

Write `skills/reproducibility/SKILL.md` and its references: the discipline agents follow to register, build, and review a reproduction graph. Mechanics stay in `task-tree` (contract, CLI, dashboard); this skill points to them and teaches behavior.

- **SKILL.md** (utility category, standalone-usable): registration, step lifecycle, scoped build/status verification, environment-change judgment, and the reproduction gates.
- **`references/rerun-model.md`:** what agents must understand to predict reruns: content hashes, the size-and-mtime cache, early cutoff, why `touch` does nothing, why identical regeneration stops the cascade, include closures, env deps, machine-specific exclusions (sysimages), sidecar trade-offs, external inputs at the graph boundary, Dropbox behavior, and how to read an `explain`.
- **`references/graph-authoring.md`:** how to declare steps from a script (read its I/O, name deps at file level, directories only for many-file outputs, `${VAR}` roots, per-file outs when scripts share a directory, check steps for drift tests), how to separate producer stages and helper modules to isolate meaningful recomputation without requiring one file or step per function, how to present a new or changed graph for review (dashboard DAG navigator), and how to act on graph comments.
- **`references/protect-and-completion.md`:** the Protect step's reproduction choices (completion targets, check steps for selected drift tests, boundary inputs) and completion verification scoped to those targets.
- **Validation criteria:** each file passes the CLAUDE.md three-test gate line by line and the terse style; frontmatter description names the triggers; every command and finding name matches the contract and runner objectives. Behavioral verification is [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md), where agents follow this skill on a real pipeline; defects found there reopen this task. Verify dependency separation with a small pipeline: a presentation-only edit leaves estimation and independent consumers unexecuted, while changed estimates rerun their consumers.

## Details

- Load `skill-creator` and `superRA:communicate` before writing. Exemplars for the style: `skills/implement-task/SKILL.md`, `skills/review-task/SKILL.md`; a script-bearing utility skill: `skills/worktree-data-sync/SKILL.md`.
- Commands, schema, and finding names come from [01-section-contract](../01-section-contract/task.md) and [02-runner](../02-runner/task.md); point at the contract, do not restate the schema.
- BondElasticity lessons worth teaching (recorded in that repo's `.plan/`): lock paper-facing outputs, CSV companions for figures, never PNG hashes, one interpreter pin, boundary inputs.

## Results
Graph review uses the dashboard DAG navigator; embedding a Mermaid export in task results is optional.


The [reproducibility skill](../../../skills/reproducibility/SKILL.md) and its references define graph-authoring and verification discipline. Real-pipeline findings are recorded in [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md); scoped verification and tier updates are recorded in [11-scoped-verification](../11-scoped-verification/task.md).

### What each file owns

- [SKILL.md](../../../skills/reproducibility/SKILL.md) — what gets a step, the tier opt-in and its timing, `build` / `status` as the evidence a result reproduces, and the reproduction gates.
- [graph-authoring.md](../../../skills/reproducibility/references/graph-authoring.md) — declaring steps from a script's real I/O (file granularity, `${VAR}` roots, one interpreter pin, figure data companions, `check` deps, the boundary), and presenting a graph for the researcher's required-tier/boundary decisions.
- [rerun-model.md](../../../skills/reproducibility/references/rerun-model.md) — the five things that rerun a step, identical regeneration as the cascade stopper, the size-and-mtime cache under Dropbox, and a five-row table for reading `explain`.
- [protect-and-completion.md](../../../skills/reproducibility/references/protect-and-completion.md) — the three Protect decisions folded into the researcher proposal, and the completion-gate commands with failure triage.

### Boundaries held

- **Mechanics stay in `task-tree`.** The skill points at [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) §Reproduction Section for schema, config keys, and findings; it contains no YAML block, so the inline-list quoting rule from [01-section-contract](../01-section-contract/task.md) has no surface to drift from.
- **Command names come from [02-runner](../02-runner/task.md) §Objective** — `build`, `status`, `explain`, `dag --mermaid`, `tier`, the `--tier canon` flag, and the `fresh` / `stale` / `missing` / `failed` / `external` states. `task check --category reproduction` comes from [03-task-interface](../03-task-interface/task.md). Nothing was invented.
- **Inventory registration is [07-workflow-integration](../07-workflow-integration/task.md)'s objective**, so `CATEGORIES.md`, `README.md`, the `CLAUDE.md` ownership table, and the `using-superra` manifest are untouched here.

### Packaging is in scope, inventory prose is not

`.agents/skills/reproducibility` is a new symlink: [check-harness-compatibility.sh](../../../tests/check-harness-compatibility.sh) asserts every `skills/*/SKILL.md` has one, and failed without it. The check passes now, as does the markdown check on all four files.

### Lessons carried in from BondElasticity

- Figures declare a deterministic `*_data.csv` beside the PNG and drift checks read the CSV: that repo's clean-room rerun found all seven PNGs byte-different from the baseline with the numbers identical ([detect-drift/task.md:138](/Users/zhiyufu/Dropbox/BondElasticity-Reproduction/.plan/detect-drift/task.md#L138)).
- One interpreter pin, in the `runners` template rather than per step.
- Frozen upstream artifacts stay boundary inputs with no producing step.

### Lessons carried in from TreasuryGIV

**Outs are the artifacts a consumer reads; a write stamp is never one.** A directory out whose producer restamps a file in place restaled 36 downstream steps on an otherwise unchanged rerun. `graph-authoring.md` §Declare from the script now carries the rule on the `outs` bullet. Full incident: [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) §What the pilot taught the model.

**A drift pin declares the published root, not a rehearsal mirror.** A project with an opt-in publish path has two roots, and a pin declared against the wrong one can be silently set from one worktree's sandbox. `graph-authoring.md` §Declare from the script now carries the rule on the `check`-step bullet. Full incident: [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) §What the pilot taught the model.

### Dependency boundaries

[Graph authoring](../../../skills/reproducibility/references/graph-authoring.md#isolate-meaningful-recomputation) covers stage boundaries, helper-module separation, and artifact dependencies between stages.

A temporary three-step pipeline (estimation, plotting, table formatting) exercised the live runner with separate presentation helpers. Five scenarios passed: warm builds and unrelated code edits ran no steps; a plotting-helper edit ran only plotting; changed estimates ran all three steps; a comment-only estimation edit ran estimation alone. Every scenario ended fresh, and both consumer outputs contained the changed estimate.

The existing [runner tests](../../../skills/task-tree/scripts/test_repro_runner.py) for identical regeneration and unchanged-content touches also passed (2 passed).
