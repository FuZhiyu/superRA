# Diagnosing an Unexpected State

## What makes a step rerun

- **Changed content, never a timestamp.** `touch` reruns nothing, and restoring a file's original bytes clears content-based invalidation. A failed forced rerun still requires a successful retry.
- **A declared helper's change invalidates its consumers.** Julia `.jl` deps expand through statically resolved `include` paths; declare unresolved includes and other languages' helpers explicitly.
- **A `cmd` or `params` edit invalidates its step.** Each step's spec is hashed separately. A root change invalidates through changed file content or resolved command text; relocation to identical bytes preserves freshness.
- **Explicit `env_deps` invalidate every step when their content changes.** Environment files are otherwise left to §Environment changes.
- **A replaced external input restales its consumers.** The boundary is hashed like everything else, so a redelivered vendor extract shows stale downstream with no repo file changed.

## What stops a cascade

**Identical regeneration.** A rerun that rewrites its out byte-for-byte leaves the descendants fresh, so a comment-only edit to a producer costs one step instead of the whole tail. Volatile bytes defeat that cutoff when the producer reruns: sort before writing and keep run timestamps out of tracked outs.

[Reviewed acceptance](rerun-or-accept.md#accept) also stops upstream uncertainty; independently changed downstream inputs still require work.

## Cache and sidecars

Warm file hashing costs one `stat` per file; variable discovery and graph construction are the other costs. A Dropbox re-sync that changes only mtime causes a rehash without invalidation. Sidecar tracking is for one measurably slow intermediate, never for an exhibit.

## Read what explain names

`superra repro explain '<task>#<step>' --json` separates own changes from upstream uncertainty and exposes verified baseline diffs when available. `superra repro impact <path...>` predicts invalidation, not changed output values.

| It names | Read it as |
|---|---|
| An out you did not edit | Check concurrent writers, synchronization, and path routing; test determinism by comparing repeated outputs. |
| A dep under a directory you declared | Check whether the changed file is a real input; narrow the directory when it holds unrelated files. |
| A file you did not know the step read | The include closure or `env_deps` reached it — correct, if the script really reads it. |
| An upstream step is stale | Follow that producer with its own `explain`. |
| `external` on a generated file | Confirm the boundary: retrieve an agreed saved input, or register an in-scope producer. |

A locally fresh result can stay stale in the full graph: default status assesses saved inputs, `--upstream` assesses their producers. Runtime declaration guards freeze the selected commands, paths, and output ownership, so unrelated tree edits do not invalidate running work; a relevant edit or changed input during execution requires retrying the affected work.

## Environment changes

Keep project and lockfiles versioned but outside graph dependencies by default. When judging a rerun or investigating a reproduction failure, compare their Git diffs against the last successful run and choose the affected producers and checks from what changed. A fresh graph does not establish that an environment change was harmless.
