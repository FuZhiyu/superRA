# Completion and Protect

## The completion gate

Run at the IMPLEMENT phase exit, once every task is approved, over every active step:

1. `superra repro status .`
2. Resolve each step not `fresh` by [the stale rule](rerun-or-accept.md#the-stale-rule), building the ones it says to run by name.
3. `superra repro status .` again.

The gate passes when every step reads `fresh`, by execution or reviewed acceptance, except the steps the stale rule left stale and reported to the researcher. An empty selection is no evidence for a result. When the researcher asks for fresh execution, build the named targets with `--force`.

A failure blocks the completion menu:

- **A step failed** — read the log its status reason names to tell producer, environment, and declaration failures apart.
- **The build succeeded and status is still not fresh** — [diagnosing.md](diagnosing.md).
- **A result has no producer** — register one, or agree with the researcher that its input is external.

## Reproduction choices at Protect

Fold one reproduction decision into the protection proposal the researcher answers: which inputs are external.
