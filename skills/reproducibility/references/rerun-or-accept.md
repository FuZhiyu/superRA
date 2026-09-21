# Rerun or Accept

## Preview the cost and the cause

- `superra repro build <targets> --dry-run` lists what would execute, each with its last recorded duration — `unknown` when the step has never run.
- `superra repro explain '<task>#<step>'` separates the step's own changes from upstream uncertainty and names the steps in other tasks that read its outs.
- `superra repro status <targets>` reports each selected step's freshness and its `outside readers: N` count.

## Classify the step's role

Significance is inferred from the graph, never marked in the section.

- **Task-local** — the producer sits under its task's `attachments/` and nothing outside the task consumes its outs.
- **Potentially significant** — a producer on a maintained path, an out another task or a document consumes, a Protect completion target, or a selected check. Any one is enough: a selected check is significant at zero outside readers.

## The stale rule

| The step is | Do |
|---|---|
| Task-local | Leave it stale and tell the researcher. |
| Potentially significant, cheap | Run it. |
| Potentially significant, costly | Ask the researcher, carrying the diagnosis and a build / accept / leave recommendation. |

"Cheap" is about a minute as a suggestive guideline, with no upper number — judge on site against what the result is worth. A subagent cannot reach the researcher: escalate through your return.

**Exception: a change that cannot move a result.** When the diff proves it — a comment, whitespace, a logging line, a docstring, a helper the consumer never calls — accept on your own with the reason recorded, and report that you did. The proof is the diff, not the file list or the commit message.

## Accept

**Inspect before accepting.** Review the selected producers' current specification, inputs, and outputs; on an existing baseline, read its changes with `explain`.

```bash
superra repro accept <targets> --reason 'Ran interactively and reviewed the panel'
```

One call previews, revalidates, and writes. `--dry-run` prints a token and writes nothing; `--apply <token>` then accepts exactly that preview, when review and apply want separating. Flags, records, and rejection conditions: [commands.md §Reviewed acceptance](../../task-tree/references/commands.md#reviewed-acceptance).

Accepting the same fan-out again and again is a design signal — fix it at the [script or module boundary](designing-the-graph.md#the-step-unit-follows-the-script) when that boundary is in scope.

## What acceptance never covers

- **It executes nothing.** A check that has never run must run; acceptance supplies no missing check stamp.
- **It certifies the selection only.** Producers outside the targets stay saved inputs, so accepting a consumer says nothing about its upstream.
- **It is not a substitute for unresolved work.** Unreviewed results, result-affecting changes not yet executed, and changed check assertions require running the affected producer or check.
