# Rerun or Accept

`[BLOCKING]` A step that is not `fresh` is resolved by [the stale rule](#the-stale-rule) — run, accept with a recorded reason, or report it — never left silently stale.

Before applying the rule: `superra repro build <targets> --dry-run` for the cost, `superra repro explain <target>` for the cause ([reading explain](diagnosing.md#read-what-explain-names)).

## The stale rule

It covers steps a change left `stale`, `missing` (an out is gone), or `failed`. Your own work is built, never left stale: a step you just registered, or a `failed` step once you fix what the log its reason names shows. A step reported `external` waits on a missing external input: retrieve it, or register its producer.

Classify the step from the graph:

- **Task-local** — its producer sits under its task's `attachments/` and `status` reports `outside readers: 0`.
- **Potentially significant** — every other step.

| The step is | Do |
|---|---|
| Task-local | Leave it stale and tell the researcher. |
| Potentially significant, cheap | Run it. |
| Potentially significant, costly | Ask the researcher, carrying the diagnosis and a build / accept / leave recommendation. |

"Cheap" is about a minute, a guide rather than a cap — judge on site against what the result is worth. A subagent cannot reach the researcher: escalate through your return.

**Exception: a change that cannot move a result.** When the diff proves it — a comment, whitespace, a logging line, a docstring, a helper the consumer never calls — accept on your own with the reason recorded, and report that you did. The proof is the diff, not the file list or the commit message.

## Accept

**Inspect before accepting.** Review the selected producers' current specification, inputs, and outputs; on an existing baseline, read its changes with `explain`.

```bash
superra repro accept <targets> --reason 'Ran interactively and reviewed the panel'
```

Cite any evidence file in the reason. An expensive result already produced from the same committed code, such as by an interactive run, is accepted this way instead of rerun.

Accepting the same fan-out again and again is a design signal — fix it at the [script or module boundary](designing-the-graph.md#the-step-unit-follows-the-script) when that boundary is in scope.

## What acceptance never covers

- **A check that has never run must run.**
- **It covers the selection only.** Accepting a consumer says nothing about the producers of its saved inputs; when the claim covers them, accept or build them too.
- **It does not replace unresolved work.** Unreviewed results, result-affecting changes not yet executed, and changed check assertions require running the affected producer or check.
