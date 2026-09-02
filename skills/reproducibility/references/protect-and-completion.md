# Protect and Completion

## Reproduction choices at Protect

Fold three reproduction decisions into the protection proposal the researcher answers (`skills/superintegrate/references/protect.md` step 3):

- **Tier per affected task.** Every task owning a producer of a kept result goes `canon`; the rest stay `local`.
- **A `kind: check` step for each drift test the researcher selects.**
- **The boundary.** Name the inputs the project receives rather than rebuilds, and get the researcher's agreement that they are not reproducible here.

Record all three in the `integrate(protect)` commit body.

## The completion gate

Run at the IMPLEMENT phase exit, once every task is approved:

```bash
superra repro build --tier canon
superra repro status --tier canon
```

The gate passes when the build completes and the status that follows reports no `stale`, `missing`, or `failed` step. A failure blocks the completion menu — fix it rather than reporting around it:

- **A step failed** — its log path is in `superra repro explain <step>`; that failure is the work, not a graph defect.
- **The build succeeded and status is still dirty** — `rerun-model.md` §Diagnosing a surprise.
- **A canon task cites an output no step produces** — the gate found the real gap. Register the producer.
