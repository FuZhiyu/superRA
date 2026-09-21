---
name: reproducibility
description: Register and verify task-declared reproduction graphs. Use when planning, producing, changing, or reviewing retained results that depend on executable steps, adopting reproduction, selecting protection checks, or judging reruns or evidence-backed reuse.
---

# Reproducibility

## The Model

- **Steps belong to tasks.** A step is one command with its `deps` and `outs`, declared in the owning task's `## Reproduction` section. An out feeding another step's dep orders both steps and their tasks.
- **pytask 0.6 is the engine.** Each step becomes a pytask task generated in memory — a project holds no `task_*.py` — and freshness is pytask's content-hash comparison against the committed `pytask.lock`.
- **superRA adds two things.** Targets are task-scoped: a file from a producer outside the scope is a saved input, used as it sits on disk. And reviewed acceptance is a second route to `fresh`, recording why current results stand instead of executing them.

Section schema and config keys: [task-file-contract.md §Reproduction Section](../task-tree/references/task-file-contract.md#reproduction-section). Flags, records, and step states: [commands.md §Reproduction](../task-tree/references/commands.md#reproduction).

## The Loop

1. **Registration follows placement.** Exploration lives in scratch or tmp and stays unregistered; code retained in the codebase or in a task's `attachments/` is registered in its owning task.
2. **Produce the retained result through the graph** — `superra repro build <targets>`. An expensive result already produced from the same committed code is registered and accepted with a reason instead of rerun.
3. **Read the status you are about to claim** — `superra repro status <targets>`, with `--upstream` when the claim covers the producer chain.
4. **State what the evidence covers in `## Results`:** the targets, the boundary inputs, the check outcomes, and which steps executed versus which were accepted. Commit changed execution and acceptance records with the work.

## Gates

- `[BLOCKING]` Retained code and every result recorded from it are registered, per [what earns a step](references/designing-the-graph.md#what-earns-a-step) — a finding recorded in prose with no output file of its own included.
- `[BLOCKING]` Before claiming a result reproduces, its scoped build succeeds and every step the matching status reports is `fresh`.
- `[BLOCKING]` A stale step is resolved by [the stale rule](references/rerun-or-accept.md#the-stale-rule) — run, accept with a recorded reason, or report it — never left silently stale.
- `[ADVISORY]` A step whose script reads a few named files declares those files, not their directory.

## Where to Go Next

| Load | When |
|---|---|
| [designing-the-graph.md](references/designing-the-graph.md) | Planning a task's steps, or declaring them. |
| [rerun-or-accept.md](references/rerun-or-accept.md) | A step is stale. |
| [diagnosing.md](references/diagnosing.md) | A state is not what you expected. |
| [protect-and-completion.md](references/protect-and-completion.md) | At `Stage: protection`, or at the IMPLEMENT completion gate. |
| [adoption.md](references/adoption.md) | First use of reproduction in a project. |
