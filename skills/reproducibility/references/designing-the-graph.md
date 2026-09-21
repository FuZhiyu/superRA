# Designing the Graph

## What earns a step

Reuse an existing registered producer rather than declaring a second one, an unchanged script serving a new finding included. Cover the producer chain to the agreed boundary, and update declarations in the commit that changes the result, the input, or the ownership.

- **A maintained producer of a committed exhibit or canonical result** — the script behind a table, figure, estimate, or dataset the manuscript, the slides, or another task's `## Results` cites.
- **A task companion the results cite** — a script under `attachments/` that produced a finding in its own task's `## Results`.
- **A drift test or validation script** — a `kind: check` step over the artifacts it reads; `[BLOCKING]` for a drift test protecting registered outs.

Unregistered: findings that are not retained, anything regenerated per machine, and boundary inputs (§Declare from the script).

**A task companion is never upstream of main work** — [promote it](../../using-superra/references/task-companion-files.md#promote) the moment anything outside its task consumes its output, rather than drawing a dep edge into another task's `attachments/`.

## The step unit follows the script

One step per script is the default, so shaping scripts shapes the graph.

- **Split a script at a saved artifact when its stages differ in cost and edit frequency.** An expensive estimation that reruns because a plotting tweak shares its file is a script-boundary problem, not a declaration problem: write the estimates out, let the plot read them.
- **Merge only scripts that always run together.**
- **Split helper modules by consumer set.** Unrelated helpers in one file couple independent consumers, since separate functions in one file still share a file-level dependency. Import the module a step needs, not an entry point that loads them all.
- **Derive configuration per consumer.** A cheap producer emitting deterministic per-consumer artifacts stops the cascade on unchanged bytes.

The balance is rerun selectivity against declaration upkeep and per-step process start-up: each step pays a fresh interpreter, which dominates a chain of short scripts.

## The dependency trade-off is a ladder

1. **Declare every true read.** A missing dep is a silently wrong result; an extra dep costs reruns only.
2. **Measure the fan-out before calling it waste** — `superra repro impact <path>` names the affected consumers, `build --dry-run` prints what each last cost.
3. **Split the scripts or modules your task owns**; report the ones it does not.
4. **Resolve what remains through [the stale rule](rerun-or-accept.md#the-stale-rule).**

Dropping a true dep is never a rung.

## Declare from the script, not from memory

Open the producer and list what it opens: its real reads are `deps`, its real writes are `outs`.

- **Name files.** Use a directory entry only when the names are generated or the count is large; two scripts writing into one directory declare per-file outs or collide on the duplicate-out error. Enumerating a directory from disk also picks up leftovers from earlier runs.
- **Declare maintained artifacts as outs.** Exclude run logs and write stamps; a directory out holding them defeats identical-output cutoff.
- **Keep declarations at their owning scope.** Stable repo-relative paths, untracked boundary inputs included, belong in the task owning the run. Reserve config variables for shared roots that need machine or branch resolution.
- **Bind declared paths to execution.** Pass the paths to the producer, or assert agreement with its runtime routing, sandbox preference included ([adoption.md](adoption.md)).
- **Pin the interpreter once**, in the `runners` template.
- **Check a figure's numerical data.** Point a selected numerical check at a deterministic artifact holding the plotted values, reusing an existing artifact or a project-native format; write a companion only when that evidence is missing. A published-result check reads the published root.
- **Stop at the boundary.** An input the project receives rather than builds — a licensed extract, a frozen upstream artifact, a hand-curated file — is a dep with no producing step.
- **Connect stages through consumed artifacts.** Upstream code is a downstream dep only when the downstream step reads or executes it; provenance alone is not a dependency.

Validate before building: `superra task check`. Repair genuine task-boundary cycles through declarations or ownership and keep true consumed-artifact edges ([dependency and hierarchy contract](../../task-tree/references/task-file-contract.md#effective-dependencies)).

## Step lifecycle

- **Retire a step only when its result or check is no longer retained and no retained consumer reads its outs.**
- **Moving or merging tasks:** move surviving steps with their names unchanged, so their evidence carries over.
- **Deleting or archiving an owner:** first move the needed producers to a surviving task, or agree a frozen boundary with the researcher.

## Presenting a graph for review

Present a new or restructured graph for the researcher's decisions on completion targets and the input boundary, applying the coverage rule in [protect-and-completion.md](protect-and-completion.md) when naming targets. The dashboard DAG navigator expands tasks into steps.

A comment anchored to a step is a graph-design finding: fix the section and rerun `superra repro status <task>`. A comment that moves what counts as canonical, or where the boundary sits, is a scope change — carry it back to the task tree instead of quietly changing the declarations.
