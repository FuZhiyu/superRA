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

Volatile bytes defeat that cutoff when the producer reruns; they do not by themselves make a just-built output stale. Sort before writing and keep run timestamps out of tracked outs — for figures, the deterministic companion in `graph-authoring.md`.

## Cache and sidecars

Warm file hashing costs one `stat` per file; variable discovery and graph construction are additional costs. A Dropbox re-sync that changes only mtime causes a rehash without invalidation.

Sidecar tracking (contract §Reproduction Section) is for one measurably slow intermediate, never for an exhibit.

## Diagnosing a surprise

`superra repro explain <step>` names the node that changed.

| It names | Read it as |
|---|---|
| An out you did not edit | Check concurrent writers, synchronization, and path routing; test determinism by comparing repeated outputs. |
| A dep under a directory you declared | Check whether the changed file is an actual input; narrow the directory when it includes unrelated files. |
| A file you did not know the step read | The include closure or `env_deps` reached it — correct, if the script really reads it. |
| Nothing, yet the step is stale | The step's own spec changed: `cmd`, `params`, or a `${VAR}` that now resolves elsewhere. |
| `external` on a generated file | Confirm the boundary: retrieve an agreed saved input, or register an in-scope producer. |
