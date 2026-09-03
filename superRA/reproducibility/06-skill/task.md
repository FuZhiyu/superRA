---
title: "Author the `reproducibility` Utility Skill"
status: approved
depends_on: [01-section-contract]
---

## Objective

Write `skills/reproducibility/SKILL.md` and its references: the discipline agents follow to register, build, and review a reproduction graph. Mechanics stay in `task-tree` (contract, CLI, dashboard); this skill points to them and teaches behavior.

- **SKILL.md** (utility category, standalone-usable): when to register a step (any maintained producer of a committed exhibit or canonical result; any task companion the results cite, at `tier: local`), the tier rule (canon is opted in, normally at Protect), how to build and read `repro status`, and gated checklist items for implementers and reviewers: `[BLOCKING]` every out a task's `## Results` cites is produced by a registered step or declared external; `[BLOCKING]` `repro status --tier canon` is clean before `status: implemented` on a canon task; `[BLOCKING]` env deps and check steps declared per the contract; `[ADVISORY]` deps declared at file granularity, not whole directories, when the script reads a few files.
- **`references/rerun-model.md`:** what agents must understand to predict reruns: content hashes, the size-and-mtime cache, early cutoff, why `touch` does nothing, why identical regeneration stops the cascade, include closures, env deps, machine-specific exclusions (sysimages), sidecar trade-offs, external inputs at the graph boundary, Dropbox behavior, and how to read an `explain`.
- **`references/graph-authoring.md`:** how to declare steps from a script (read its I/O, name deps at file level, directories only for many-file outputs, `${VAR}` roots, per-file outs when scripts share a directory, check steps for drift tests), how to present a new or changed graph for review (dashboard Reproduction view, mermaid export in `## Results`), and how to act on graph comments.
- **`references/protect-and-completion.md`:** the Protect step's reproduction choices (tier per affected task, check steps for selected drift tests, boundary inputs) and the completion-gate procedure (`repro build --tier canon`, then `repro status` clean, failures block the menu).
- **Validation criteria:** each file passes the CLAUDE.md three-test gate line by line and the terse style; frontmatter description names the triggers; every command and finding name matches the contract and runner objectives. Behavioral verification is [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md), where agents follow this skill on a real pipeline; defects found there reopen this task.

## Details

- Load `skill-creator` and `superRA:communicate` before writing. Exemplars for the style: `skills/implement-task/SKILL.md`, `skills/review-task/SKILL.md`; a script-bearing utility skill: `skills/worktree-data-sync/SKILL.md`.
- Commands, schema, and finding names come from [01-section-contract](../01-section-contract/task.md) and [02-runner](../02-runner/task.md); point at the contract, do not restate the schema.
- BondElasticity lessons worth teaching (recorded in that repo's `.plan/`): lock paper-facing outputs, CSV companions for figures, never PNG hashes, one interpreter pin, boundary inputs.

## Results

The `reproducibility` skill is written and packaged: [SKILL.md](../../../skills/reproducibility/SKILL.md) plus the three references the objective names, 1,429 words total. Behavior stays unverified until [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) runs an agent through it on a real pipeline.

### What each file owns

- [SKILL.md](../../../skills/reproducibility/SKILL.md) — what gets a step, the tier opt-in and its timing, `build` / `status` as the evidence a result reproduces, and the objective's four gates.
- [graph-authoring.md](../../../skills/reproducibility/references/graph-authoring.md) — declaring steps from a script's real I/O (file granularity, `${VAR}` roots, one interpreter pin, figure data companions, `check` deps, the boundary), and presenting a graph for the researcher's canon/boundary decisions.
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
