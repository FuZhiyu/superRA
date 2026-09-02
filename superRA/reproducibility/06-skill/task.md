---
title: "Author the `reproducibility` Utility Skill"
status: implemented
depends_on: [01-section-contract]
---

## Objective

Write `skills/reproducibility/SKILL.md` and its references: the discipline agents follow to register, build, and review a reproduction graph. Mechanics stay in `task-tree` (contract, CLI, dashboard); this skill points to them and teaches behavior.

- **SKILL.md** (utility category, standalone-usable): when to register a step (any maintained producer of a committed exhibit or canonical result; any task companion the results cite, at `tier: local`), the tier rule (canon is opted in, normally at Protect), how to build and read `repro status`, and gated checklist items for implementers and reviewers: `[BLOCKING]` every out a task's `## Results

The `reproducibility` skill is written and packaged: [SKILL.md](../../../skills/reproducibility/SKILL.md) plus the three references the objective names, 1,440 words total. Behavior stays unverified until [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) runs an agent through it on a real pipeline.

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
