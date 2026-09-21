---
title: "Agent Protocol: Teach Registration, Graph Design, and Rerun-or-Accept Judgment"
status: implemented
depends_on: []
---

## Objective

Make agents use the reproduction graph well without coaching: register retained code, produce recorded results through the graph, design maintainable graphs, and resolve staleness by the step's role and cost instead of rerunning everything. The CLI teaches at the point of use; the [reproducibility skill](../../../skills/reproducibility/SKILL.md) teaches judgment, disclosed progressively by the moment the agent is in.

### Decisions (researcher, 2026-09-20)

- **Registration follows placement.** Speculative exploration lives in scratch or tmp and is never registered. Code retained in the codebase or a task's `attachments/` is always registered.
- **Retained results come from `repro build`.** An expensive result already produced directly from the same committed code is registered and accepted with a reason instead of rerun.
- **A stale step is resolved by role, then cost.**
  - Task-local step: leave it stale and tell the researcher.
  - Potentially significant step, cheap: run it. About one minute is a suggestive guideline for "cheap", not a rule; no upper number. Agents and the researcher judge on site.
  - Potentially significant step, costly: ask the researcher, with the diagnosis and a build / accept / leave recommendation. A subagent escalates through its return.
  - Exception: when the diff proves no result can move (comments, whitespace, logging, docstrings, a helper the consumer never calls), the agent accepts on its own with the reason recorded and reports it.
- **Significance is inferred, not marked.** Task-local: the producer sits under `attachments/` and nothing outside the task consumes its outs. Significant: a maintained-path producer, an out another task or a document consumes, a Protect completion target, or a selected check. No schema marker returns.
- **A task companion is never upstream of main work.** A script or output under `attachments/` feeds only its own task's results. The moment a step in another task, a maintained pipeline, or a document needs it, it is promoted to the project's conventional path and registered there; promotion does not wait for integration.
- **Graph design includes script design.** One step per script is the default, and the script boundary is a design choice: when an expensive stage reruns for edits to a cheap one, split the script at a saved artifact instead of forcing both into one step; merge only scripts that always run together. Planners draw script boundaries with the graph in mind; implementers split scripts their task owns. The balance is rerun selectivity against declaration upkeep and per-step process start-up.
- **Registration signals are advisory.** Not every retained artifact belongs in the graph (a hand-edited `.tex`), so mechanical detection warns and never blocks.
- **v0.5 is unreleased: no compatibility surface.** Retired flags, legacy records, and their documentation are deleted, code included.
- **Behavioral evals are skipped for now.** Real-project use supplies the behavioral evidence and reopens the owning child on defects.

### Constraints

- Ownership split holds: flag and record semantics live only in [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction) and the [task-file contract](../../../skills/task-tree/references/task-file-contract.md#reproduction-section); the skill carries intent-shaped recipes and judgment, and restates neither.
- This group folds back into its durable owners at integration: [02-runner](../02-runner/task.md), [03-task-interface](../03-task-interface/task.md), [05-reminder-hook](../05-reminder-hook/task.md), [06-skill](../06-skill/task.md), [07-workflow-integration](../07-workflow-integration/task.md).

## Details

### Why agents misbehave today (planning diagnosis, 2026-09-20)

Observed by the researcher in real-project use: results recorded with no registered step; producers run directly instead of through `repro`; superficial staleness answered by rerunning everything; graphs that are hard to keep current.

- **The skill opens with rules, not a model.** [SKILL.md](../../../skills/reproducibility/SKILL.md) never says what a step, freshness, target scope, or the execute-versus-accept pair is before it starts issuing requirements.
- **The acceptance protocol is buried.** It is the last section of [rerun-model.md](../../../skills/reproducibility/references/rerun-model.md), a diagnostic reference, and says nothing about cost or the step's role.
- **Accepting costs more than building.** `accept` needs a preview, a copied token, and a repeated call; `build` is one call.
- **Nothing states the dependency trade-off.** [graph-authoring.md](../../../skills/reproducibility/references/graph-authoring.md) lists four isolation rules but not the asymmetry behind them, the default step unit, or the process start-up cost the TreasuryGIV pilot measured (9 minutes in-process, 42 minutes as 44 processes).
- **Scope semantics are stated twice**, in SKILL.md §Build and Status and in commands.md §Reproduction, which also carries retired flags, legacy records, and a dashboard paragraph.
- **Role skills are silent.** `implement-task`, `review-task`, and `interactive-mode.md` never mention reproduction; the only triggers are one line in `using-superra` §Task Interface and a once-per-session hook reminder.
- **[pilot-acceptance.md](../../../skills/reproducibility/references/pilot-acceptance.md) collides with `repro accept` by name**, and most of its matrix retests the runner's own suite.

`status` and `explain` already print each step's last run duration from the gitignored run records, so a cost estimate needs no new data; it is unknown on a machine that never ran the step.

[reviewed-acceptance](../02-runner/reviewed-acceptance/task.md) is `implemented` with its independent review deferred; the one-shot `accept` change edits the same module.
