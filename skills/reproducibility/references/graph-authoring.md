# Graph Authoring

## Declare from the script, not from memory

Open the producer and list what it opens: its real reads are `deps`, its real writes are `outs`.

- **Outs are the artifacts a consumer reads.** A write stamp, a run log, or anything else whose bytes move on an identical rerun is never an out — a directory out that swallows one restales the whole tail on every build. An exhibit that embeds its own creation date is the same class at the leaf, where nothing downstream reads it.
- **Name files.** Use a directory entry only when the file names are generated or the count is large; two scripts writing into one directory declare per-file outs, or they collide on the duplicate-out error.
- **Root every path that moves with a `${VAR}`** from `superRA/config.yaml` — output roots, scratch, data shares — and keep literal repo-relative paths for what is committed.
- **Pin the interpreter once**, in the `runners` template.
- **Declare a figure's data, not only its picture.** PNG bytes vary with the renderer, so a byte difference on a figure is not evidence of a numeric change. Have the plotting script write a deterministic `*_data.csv` beside the image, declare both as outs, and point drift checks at the CSV.
- **Give a `check` step the artifacts it reads as `deps`**, so a stale check surfaces beside the build it protects. A pin on a published result reads the published root, not the mirror a rehearsal build writes — declare those paths, and set whatever the project uses to force that read, or the pin re-validates the run it exists to check.
- **Stop at the boundary.** An input the project receives rather than builds — a licensed extract, a frozen upstream artifact, a hand-curated file — stays a dep with no producing step.

Validate the section before building: `superra task check --category reproduction`.

## Presenting a graph for review

Present a new or restructured graph for the two answers only the researcher has: which tasks are `canon`, and which inputs are boundary rather than reproducible here.

- Export the graph into `## Results` with `superra repro dag --mermaid`.
- Point at the dashboard Reproduction view for the interactive pass — node states, per-step detail, and the comment gutter on the section.

## Acting on graph comments

A comment anchored to a step is a graph-design finding: fix the section and rerun `superra repro status`. A comment that moves what counts as canonical, or where the boundary sits, is a scope change — carry it back to the task tree instead of quietly re-tiering.
