# Completion and Protect

## The completion gate

Run over every active step, once every task is approved:

1. `superra repro status .`
2. Resolve each step not `fresh` by [the stale rule](rerun-or-accept.md#the-stale-rule), costed by `superra repro build <steps> --dry-run`; build by name only the steps it says to run.
3. `superra repro status .` again.

The gate passes when every step reads `fresh`, by execution or reviewed acceptance, except the steps the stale rule left stale and reported to the researcher. When the researcher asks for fresh execution, build the named targets with `--force`.

**No registered steps** — `status .` reports that it selects no steps. An empty selection is no evidence for a result: the gate passes only when no `## Results` rests on retained code, as in a prose, slide, or pen-and-paper tree. Otherwise register the producers ([designing-the-graph.md](designing-the-graph.md#what-earns-a-step)) and run the gate.

A failure blocks the completion menu:

- **A step failed** — read the log its status reason names to tell producer, environment, and declaration failures apart.
- **The build succeeded and status is still not fresh** — [diagnosing.md](diagnosing.md).
- **A result has no producer** — register one, or agree with the researcher that its input is external.

## Reproduction choices at Protect

Fold one reproduction decision into the protection proposal the researcher answers: which inputs are external.
