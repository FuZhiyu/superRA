# Protect and Completion

## Reproduction choices at Protect

Fold three reproduction decisions into the protection proposal the researcher answers (`skills/superintegrate/references/protect.md` step 3):

- **Required tasks.** Include tasks owning kept-result producers and tasks owning selected protection checks, including check-only tasks. Other tasks stay `on-demand`. Use `superra repro tier <task-path> required`.
- **A `kind: check` step for each drift test the researcher selects.** A file-consumer edge alone does not select a protection check.
- **The boundary.** Name the inputs the project receives rather than rebuilds, and get the researcher's agreement that they are not reproducible here.

Record all three in the `integrate(protect)` commit body.

## The completion gate

Run at the IMPLEMENT phase exit, once every task is approved:

```bash
superra repro build --tier required --upstream
superra repro status --tier required --upstream
```

Verify that the selection covers kept results and selected protection checks. The gate passes when the build completes and every reported step is `fresh`; an empty selection is no evidence for a result. Valid reviewed acceptance satisfies this routine gate; requested fresh execution follows [the acceptance protocol](rerun-model.md#reviewed-acceptance). On-demand claims require their own [scoped verification](../SKILL.md#build-and-status).

A failure blocks the completion menu:

- **A step failed** — inspect the log from `superra repro explain <step>` to distinguish producer, environment, and declaration failures.
- **The build succeeded and status is still dirty** — `rerun-model.md` §Diagnosing a surprise.
- **A kept result has no producer** — register it or identify its agreed external-input boundary.
