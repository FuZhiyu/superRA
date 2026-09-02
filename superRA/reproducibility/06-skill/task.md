---
title: "Author the `reproducibility` Utility Skill"
status: not-started
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
