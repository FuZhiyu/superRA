---
name: reproducibility
description: Register and verify task-declared reproduction graphs. Use when planning, producing, changing, recording, or reviewing retained results that depend on executable steps, writing drift tests or validation scripts, adopting reproduction, deciding external inputs at Protect, or judging whether to rerun or accept a stale result.
---

# Reproducibility

Every retained result can be re-run from committed code. After any change, an agent can tell which results are no longer current and whether to rerun, accept, or report them.

## The Model

- **A step is one command with its `deps` and `outs`,** declared in its owning task's `## Reproduction` section ([schema and invalidation rules](../task-tree/references/task-file-contract.md#reproduction-section)).
- **A step is `fresh`** when the content hashes of its deps, definition, and outs match its last successful build in the committed `repro-lock.json` or its reviewed acceptance. `superra repro build` executes steps that are not fresh; `superra repro accept --reason` records why the current results stand, executing nothing.
- **Targets select steps:** task paths with their descendants, `task#step`, or `.` for the whole tree. Flags: `superra repro <command> --help`.
  - **Producer chain** — the steps that produce a selection's inputs, transitively; `--upstream` adds them.
  - **Saved input** — a file from a producer outside the selection, used as it sits on disk. A selection's status says nothing about that producer.
  - **External input** — a dep no step produces: a licensed extract, a frozen upstream artifact, a hand-curated file. The researcher agrees which inputs are external.
- **Readiness is not freshness.** A task is ready once its `depends_on` prerequisites are done; inputs that `task read` lists as not fresh never hold it back. [The stale rule](references/rerun-or-accept.md#the-stale-rule) decides whether to rebuild them before building on them.

## Where to Go Next

| Load | When |
|---|---|
| [designing-the-graph.md](references/designing-the-graph.md) | Writing or registering retained code, drift tests and validation scripts included; planning, moving, or retiring steps. |
| [claiming-results.md](references/claiming-results.md) | Recording a result from retained code in `## Results`. |
| [protect-and-completion.md](references/protect-and-completion.md) | The IMPLEMENT completion check, or `Stage: protection`. |
| [rerun-or-accept.md](references/rerun-or-accept.md) | A step is not `fresh`. |
| [diagnosing.md](references/diagnosing.md) | A state you did not expect. |
| [adoption.md](references/adoption.md) | First use of reproduction in a project. |
