# Graph Authoring

## Isolate meaningful recomputation

- **Split stages at reusable artifacts.** Separate expensive computation from independently changing presentation; save estimates for plotting to consume. Choose step boundaries by useful recomputation savings, not one step per function.
- **Separate helpers by consumer set.** Split modules when unrelated helpers couple independent consumers; separate functions within one file still share a file-level dependency. Import or include the needed modules directly instead of a shared entry point that loads them all.
- **Derive configuration per consumer.** A cheap producer can emit deterministic artifacts from shared settings; unchanged consumer-specific bytes stop the cascade.
- **Connect stages through consumed artifacts.** Declare upstream code as a downstream dependency only when that downstream step reads or executes it; provenance alone does not require a code dependency.

## Declare from the script, not from memory

Open the producer and list what it opens: its real reads are `deps`, its real writes are `outs`.

- **Declare maintained artifacts as outs.** Exclude incidental run logs and write stamps; a directory out containing them defeats identical-output cutoff.
- **Name files.** Use a directory entry only when the file names are generated or the count is large; two scripts writing into one directory declare per-file outs, or they collide on the duplicate-out error.
- **Keep declarations at their owning scope.** Stable repo-relative paths, including untracked boundary inputs, belong in the task with its run selection and artifact names. Reserve config variables for shared roots that need machine or branch resolution.
- **Resolve paths without starting the analysis environment.** Adoption measurements: [pilot-acceptance.md](pilot-acceptance.md).
- **Bind declared paths to execution.** Pass paths to the producer or assert agreement with its runtime routing, including sandbox preference. A lightweight resolver must share that routing or be checked against it after branch and input-availability changes.
- **Pin the interpreter once**, in the `runners` template.
- **Check a figure's numerical data.** For selected numerical checks, use deterministic artifacts capturing the plotted values. Reuse existing artifacts or project-native formats; write a companion only when that evidence is missing.
- **Read the published root for published-result checks.**
- **Stop at the boundary.** An input the project receives rather than builds — a licensed extract, a frozen upstream artifact, a hand-curated file — stays a dep with no producing step.

Validate declarations and the effective dependency graph before building: `superra task check`. Repair genuine task-boundary cycles by correcting declarations or ownership; retain true consumed-artifact edges. [Dependency and hierarchy contract](../../task-tree/references/task-file-contract.md#effective-dependencies).

## Presenting a graph for review

Present a new or restructured graph for the researcher's decisions on completion targets and the input boundary. Apply the coverage rule in [protect-and-completion.md](protect-and-completion.md) when naming targets.

- Use the dashboard DAG navigator for task/step expansion and evidence; graph comments use the shared task reader's Reproduction section.

## Acting on graph comments

A comment anchored to a step is a graph-design finding: fix the section and rerun `superra repro status`. A comment that moves what counts as canonical, or where the boundary sits, is a scope change — carry it back to the task tree instead of quietly changing the declarations.
