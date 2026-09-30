# Designing the Graph

## What earns a step

`[BLOCKING]` Register every retained script, and every result recorded from one, as a step in the owning task. Update the declarations in the commit that changes the result, its inputs, or its ownership.

- **A script whose output a result cites:** a build step whose `outs` are the files it writes. A finding recorded only in prose still needs the script that printed it registered.
- **A drift test or validation script:** a `kind: check` step whose `deps` are the artifacts it reads.

Cite the existing step when an unchanged script serves a new finding; register no second copy. Register the producer chain back to external inputs. Leave files regenerated per machine unregistered.

**A task companion's output read outside its task:** [promote the companion](../../using-superra/references/task-companion-files.md#promote). Never declare a dep into another task's `attachments/`.

## The step unit follows the script

One step per script is the default.

- **Split a script at a saved artifact when its stages differ in cost and edit frequency** — typically expensive computation feeding an often-restyled exhibit. The computing script saves full results, not the exhibit's subset; a cheap script writes the exhibit. Computation cheap enough to rerun on every restyle stays with its exhibit.
- **Merge only scripts that always run together.** Each step pays its own interpreter start-up, which dominates a chain of short scripts.
- **Split helper modules by consumer set.** A step imports the module it needs, not an entry point that loads them all.
- **Split a shared config file per consumer.** A cheap step writes one file per consumer, so an edit reruns only the consumers whose slice changed.

## Trade reruns for correctness, in this order

1. **Declare every true read.** A missing dep is a silently wrong result; an extra dep costs only reruns.
2. **Measure the fan-out before calling it waste:** `superra repro impact <path>` names the affected steps and how long each last took.
3. **Split the scripts or modules your task owns;** report the ones it does not.
4. **Resolve what remains through [the stale rule](rerun-or-accept.md#the-stale-rule).**

## Declare from the script, not from memory

Open the producer and list what it opens: its real reads are `deps`, its real writes are `outs`.

- **Deps**
  - **Name files.** `[ADVISORY]` A script that reads a few named files declares those files, not their directory. Use a directory entry only when the names are generated or the count is large.
  - **Stop at external inputs:** declare each as a dep that no step produces.
  - **Declare upstream code only when the step reads or executes it;** provenance alone is not a dependency.
- **Outs**
  - **Declare per-file outs when two scripts write into one directory.**
  - **Keep volatile bytes out of outs,** so an identical rerun stops the cascade: exclude run logs and write stamps, sort before writing, keep timestamps out of tracked files.
  - **Use a [sidecar](../../task-tree/references/task-file-contract.md#step-keys) only for one measurably slow intermediate,** never for an exhibit.
- **Paths**
  - **Reserve config variables for shared roots that need machine or branch resolution.** Declare other paths, untracked external inputs included, repo-relative in the task that owns the run.
  - **Bind declared paths to execution.** Pass the paths to the producer, or assert they match its runtime routing: a script that prefers a sandbox copy when present can read a file its declaration never names. Recheck after a branch change or when an input's availability changes.
  - **Pin the interpreter once,** in the `runners` template.
- **Checks**
  - **Check a figure through its numerical data.** Point the check at a deterministic artifact holding the plotted values, reusing an existing artifact or a project-native format; write a companion only when that evidence is missing.
  - **Point a drift test of a published result at the published copy,** not at a sandbox copy of the same outputs.

Validate before building: `superra task check`. Fix a reported cycle through the declarations or task ownership, keeping true consumed-artifact edges.

## Step lifecycle

- **Retire a step only when its result or check is no longer retained and no retained consumer reads its outs.**
- **Moving or merging tasks:** move surviving steps with their names unchanged, so their evidence carries over.
- **Deleting or archiving an owner:** first move the needed producers to a surviving task, or agree with the researcher to freeze their outputs as external inputs.

## Presenting a graph for review

Present a new or restructured graph to the researcher to decide which inputs are external.

A comment anchored to a step is a graph-design finding: fix the section and rerun `superra repro status <task>`. A comment that changes what a task produces or which inputs are external is a scope change: carry it back to the task tree rather than quietly changing the declarations.
