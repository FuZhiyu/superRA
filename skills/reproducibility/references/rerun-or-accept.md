# Rerun or Accept

`[BLOCKING]` Resolve every step that is not `fresh` by [the stale rule](#the-stale-rule): run it, accept it with a recorded reason, or report it. Never leave one silently stale.

Before applying the rule, get the cost, stale producers included, from `superra repro build <targets> --dry-run` and the cause from `superra repro explain <target>` ([reading explain](diagnosing.md#read-what-explain-names)).

## The stale rule

The rule covers every step `status` reports as `stale`, `missing`, or `failed`. Build or accept your own work — a step you just registered or a failure you fixed — rather than leaving it stale. An `unverified` step is outside the rule: report it with the files `status` lists as not checkable here; for an absent external input, retrieve it or register its producer.

Classify the step from the graph:

- **Task-local** — its producer sits under its task's `attachments/`, and `status` reports `outside readers: 0`.
- **Potentially significant** — every other step.

| The step is | Do |
|---|---|
| Task-local | Leave it stale and tell the researcher. |
| Potentially significant, cheap | Run it. |
| Potentially significant, costly | Ask the researcher, carrying the diagnosis and a build / accept / leave recommendation. |

"Cheap" means about a minute — a guide, not a cap; judge it against what the result is worth. A subagent cannot reach the researcher: return `DONE_WITH_CONCERNS` with the question in `## Results`.

**Exception: a change that cannot move a result.** When the diff proves it — a comment, whitespace, a logging line, a docstring, a helper the consumer never calls — accept on your own with the reason recorded, and report that you did. The proof is the diff, not the file list or the commit message.

**Record the rule's acceptances before you build.** While a producer stays stale by the rule, build with `--only`, or the default build reruns it.

## Accept

Accept an expensive result already produced from the same committed code, such as by an interactive run, instead of rerunning it.

**Inspect before accepting.** Review the selected producers' current definitions, inputs, and outputs; on an existing baseline, read what changed with `explain`. Cite any evidence file in the reason:

```bash
superra repro accept <targets> --reason 'Ran interactively and reviewed the panel'
```

Accepting the same fan-out again and again is a design signal: fix it at the [script or module boundary](designing-the-graph.md#the-step-unit-follows-the-script) when that boundary is in scope.

## What acceptance never covers

- **A check that has never run.** Run it.
- **Producers you did not name.** To cover one, name it or build it.
- **Unresolved work.** Unreviewed results, result-affecting changes not yet executed, and changed check assertions require running the affected producer or check.
