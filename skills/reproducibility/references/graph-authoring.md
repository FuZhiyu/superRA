# Graph Authoring

## Declare from the script, not from memory

Open the producer and list what it opens: its real reads are `deps`, its real writes are `outs`.

- **Declare maintained artifacts as outs.** Exclude incidental run logs and write stamps; a directory out containing them defeats identical-output cutoff.
- **Name files.** Use a directory entry only when the file names are generated or the count is large; two scripts writing into one directory declare per-file outs, or they collide on the duplicate-out error.
- **Keep declarations at their owning scope.** Stable repo-relative paths, including untracked boundary inputs, belong in the task with its run selection and artifact names. Reserve config variables for shared roots that need machine or branch resolution.
- **Resolve paths without starting the analysis environment.** Adoption measurements: [pilot-acceptance.md](pilot-acceptance.md).
- **Bind declared paths to execution.** Pass paths to the producer or assert agreement with its runtime routing, including sandbox preference. A lightweight resolver must share that routing or be checked against it after branch and input-availability changes.
- **Pin the interpreter once**, in the `runners` template.
- **Declare a figure's data, not only its picture.** PNG bytes vary with the renderer, so a byte difference on a figure is not evidence of a numeric change. Have the plotting script write a deterministic `*_data.csv` beside the image, declare both as outs, and point drift checks at the CSV.
- **Give a `check` step the artifacts it reads as `deps`.** A published-result pin reads the published root; a rehearsal mirror would validate the run against itself.
- **Stop at the boundary.** An input the project receives rather than builds — a licensed extract, a frozen upstream artifact, a hand-curated file — stays a dep with no producing step.

Validate the section before building: `superra task check --category reproduction`.

## Presenting a graph for review

Present a new or restructured graph for the researcher's decisions on required work and the input boundary. Apply the coverage rule in [protect-and-completion.md](protect-and-completion.md) when selecting tasks.

- Export the graph into `## Results` with `superra repro dag --mermaid`.
- Point at the dashboard Reproduction view for the interactive pass — node states, per-step detail, and the comment gutter on the section.

## Acting on graph comments

A comment anchored to a step is a graph-design finding: fix the section and rerun `superra repro status`. A comment that moves what counts as canonical, or where the boundary sits, is a scope change — carry it back to the task tree instead of quietly re-tiering.
