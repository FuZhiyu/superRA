# Rerun Model

Predict what a change reruns before running it, and read a state you did not expect.

## What makes a step rerun

- **Changed content, never a timestamp.** `touch` reruns nothing, and restoring a file's original bytes clears content-based invalidation. A failed forced rerun still requires a successful retry.
- **Declared helper changes invalidate their consumers.** Julia `.jl` deps also expand through statically resolved `include` paths; declare unresolved includes and other languages' helpers explicitly.
- **A `cmd` or `params` edit invalidates its step.** A root change invalidates through changed file content or resolved command text; relocation to identical bytes alone preserves freshness. Each step's spec is hashed separately.
- **Explicit `env_deps` invalidate every step when their content changes.** Environment-file handling defaults to [agent judgment](../SKILL.md#environment-changes).
- **Replacing an external input restales its consumers.** The boundary is hashed like everything else, so a redelivered vendor extract shows as stale downstream even when no repo file changed.

## What stops a cascade

**Identical regeneration.** A rerun that rewrites its out byte-for-byte leaves the descendants fresh, so a comment-only edit to a producer costs one step instead of the whole tail.

[Reviewed acceptance](#reviewed-acceptance) can also stop upstream uncertainty; independently changed downstream inputs still require work.

Volatile bytes defeat that cutoff when the producer reruns; they do not by themselves make a just-built output stale. Sort before writing and keep run timestamps out of tracked outs — figure checks: [graph authoring](graph-authoring.md).

## Cache and sidecars

Warm file hashing costs one `stat` per file; variable discovery and graph construction are additional costs. A Dropbox re-sync that changes only mtime causes a rehash without invalidation.

Sidecar tracking (contract §Reproduction Section) is for one measurably slow intermediate, never for an exhibit.

## Diagnosing a surprise

Task-scoped build/status assess saved inputs; `--upstream` includes their producers. A locally fresh result can remain stale in the full graph. Runtime declaration guards cover the frozen selected commands, paths, and relevant output ownership; unrelated tree edits do not invalidate running work. A relevant edit or changed input during execution requires retrying affected work.

`superra repro impact <path...>` identifies affected consumers and why the file is tracked; `superra repro explain <step> --json` separates own changes from upstream uncertainty and exposes verified baseline diffs when available. Impact predicts invalidation, not changed output values.

| It names | Read it as |
|---|---|
| An out you did not edit | Check concurrent writers, synchronization, and path routing; test determinism by comparing repeated outputs. |
| A dep under a directory you declared | Check whether the changed file is an actual input; narrow the directory when it includes unrelated files. |
| A file you did not know the step read | The include closure or `env_deps` reached it — correct, if the script really reads it. |
| An upstream step is stale | Follow that producer with `superra repro explain <producer>`. |
| `external` on a generated file | Confirm the boundary: retrieve an agreed saved input, or register an in-scope producer. |

## Reviewed acceptance

**Inspect before accepting.** Follow the changed inputs/specification, verified baseline diff, and include/import path for each affected consumer. Reduce recurring fan-out through [module or artifact boundaries](graph-authoring.md#isolate-meaningful-recomputation) when within scope.

**Justify every changed item.** Cite inspected code, call sites, or a focused check establishing that the selected consumer's behavior and outputs remain unchanged. Split batches when only some consumers are unaffected. Missing historical source text permits other documented evidence; unchanged output files alone do not establish equivalence.

**Rerun uncertain effects.** Changed analytical specifications, changed assertions, or insufficient evidence require execution of the affected producer/check.

**Preview the exact selection, then apply it with evidence**, using [the acceptance commands](../../task-tree/references/commands.md#reviewed-acceptance).
