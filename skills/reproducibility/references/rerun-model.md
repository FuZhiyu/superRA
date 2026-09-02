# Rerun Model

Predict what a change reruns before running it, and read a state you did not expect.

## What makes a step rerun

- **Changed content, never a timestamp.** `touch` reruns nothing, and restoring a file's original bytes makes its consumers fresh again.
- **A helper edit reruns every step whose entry script reaches it.** A `.jl` dep expands to its `include` closure, so a step's rerun set is wider than its `deps` list.
- **An edit to `cmd`, `params`, or a resolved path reruns that step, not its siblings.** Each step's spec is hashed separately.
- **An `env_deps` change restales the whole subtree.** A `Manifest.toml` bump is meant to; a file regenerated per machine — sysimage, compile cache — would leave `repro status` permanently dirty and the completion gate unpassable.
- **Replacing an external input restales its consumers.** The boundary is hashed like everything else, so a redelivered vendor extract shows as stale downstream even when no repo file changed.

## What stops a cascade

**Identical regeneration.** A rerun that rewrites its out byte-for-byte leaves the descendants fresh, so a comment-only edit to a producer costs one step instead of the whole tail.

That holds only for a deterministic producer. A run timestamp, an unsorted dictionary, or a renderer version baked into the payload rebuilds the tail on every build and dirties git each time. Sort before writing, and keep volatile bytes out of tracked outs — for figures, the deterministic companion in `graph-authoring.md`.

## Cache and sidecars

File state is a content hash cached against size and mtime, so a status check costs one `stat` per file. A Dropbox re-sync rewrites mtime without changing bytes: the cache misses, rehashes, and reports the same state — cost, not drift.

Sidecar tracking (contract §Reproduction Section) is for one measurably slow intermediate, never for an exhibit.

## Diagnosing a surprise

`superra repro explain <step>` names the node that changed.

| It names | Read it as |
|---|---|
| An out you did not edit | The producer is nondeterministic. Make it deterministic before touching the graph. |
| A dep under a directory you declared | The directory is too coarse; declare the files the script reads. |
| A file you did not know the step read | The include closure or `env_deps` reached it — correct, if the script really reads it. |
| Nothing, yet the step is stale | The step's own spec changed: `cmd`, `params`, or a `${VAR}` that now resolves elsewhere. |
| `external` on a file some script writes | That producer is unregistered. Register it. |
