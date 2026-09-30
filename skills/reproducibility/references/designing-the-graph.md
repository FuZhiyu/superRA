# Designing the Graph

## What earns a step

`[BLOCKING]` Retained code, and every result recorded from it, is registered in its owning task, in the commit that changes the result, its inputs, or its ownership.

- **A script whose output a result cites** — a build step whose `outs` are the files it writes. A finding recorded only in prose still registers the script that printed it.
- **A drift test or validation script** — a `kind: check` step over the artifacts it reads.

Reuse the registered producer, even when an unchanged script serves a new finding. Register the producer chain back to external inputs. Files regenerated per machine stay unregistered.

**Output of a task companion consumed outside its task:** [promote the companion](../../using-superra/references/task-companion-files.md#promote) — never a dep edge into another task's `attachments/`.

## The step unit follows the script

One step per script is the default.

- **Split a script at a saved artifact when its stages differ in cost and edit frequency** — typically expensive computation feeding an often-restyled exhibit. The computing script saves full results, not the exhibit's subset; a cheap script writes the exhibit. Computation cheap enough to rerun on every restyle stays with its exhibit.
- **Merge only scripts that always run together.** Each step pays its own interpreter start-up, which dominates a chain of short scripts.
- **Split helper modules by consumer set.** Import the module a step needs, not an entry point that loads them all.
- **Split a shared config file per consumer.** A cheap step writes one file per consumer, so an edit reruns only the consumers whose slice changed.

## The dependency trade-off is a ladder

1. **Declare every true read.** A missing dep is a silently wrong result; an extra dep costs reruns only.
2. **Measure the fan-out before calling it waste** — `superra repro impact <path>` names the affected steps and their last cost.
3. **Split the scripts or modules your task owns**; report the ones it does not.
4. **Resolve what remains through [the stale rule](rerun-or-accept.md#the-stale-rule).**

## Declare from the script, not from memory

Open the producer and list what it opens: its real reads are `deps`, its real writes are `outs`.

- **Name files.** `[ADVISORY]` A script that reads a few named files declares those files, not their directory. Use a directory entry only when the names are generated or the count is large; two scripts writing into one directory declare per-file outs.
- **Keep volatile bytes out of outs,** so an identical rerun stops the cascade: exclude run logs and write stamps, sort before writing, keep timestamps out of tracked files.
- **Reserve config variables for shared roots that need machine or branch resolution.** Declare other paths, untracked external inputs included, repo-relative in the task owning the run.
- **Bind declared paths to execution.** Pass the paths to the producer, or assert they match its runtime routing — a script that prefers a sandbox copy when present can read a file its declaration never names. Recheck after a branch change or when an input's availability changes.
- **Pin the interpreter once**, in the `runners` template.
- **Check a figure's numerical data.** Point the check at a deterministic artifact holding the plotted values, reusing an existing artifact or a project-native format; write a companion only when that evidence is missing.
- **Point a drift test of a published result at the published copy,** not at the sandbox copy a rehearsal build writes; otherwise it re-validates the run it exists to check.
- **Stop at external inputs:** declare each as a dep with no producing step.
- **Upstream code is a dep only when the step reads or executes it;** provenance alone is not a dependency.
- **Use a sidecar only for one measurably slow intermediate,** never for an exhibit.

Validate before building: `superra task check`. Fix a reported cycle through declarations or ownership, keeping true consumed-artifact edges.

## Step lifecycle

- **Retire a step only when its result or check is no longer retained and no retained consumer reads its outs.**
- **Moving or merging tasks:** move surviving steps with their names unchanged, so their evidence carries over.
- **Deleting or archiving an owner:** first move the needed producers to a surviving task, or agree with the researcher to freeze their outputs as external inputs.

## Presenting a graph for review

Present a new or restructured graph for the researcher's decision on external inputs.

A comment anchored to a step is a graph-design finding: fix the section and rerun `superra repro status <task>`. A comment that changes what a task produces or which inputs are external is a scope change — carry it back to the task tree instead of quietly changing the declarations.
