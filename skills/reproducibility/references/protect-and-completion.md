# Protect and Completion

## Reproduction choices at Protect

Fold three reproduction decisions into the protection proposal the researcher answers (`skills/superintegrate/references/protect.md` step 3):

- **Completion targets.** Name the tasks owning kept-result producers and the selected protection checks, including check-only tasks.
- **A `kind: check` step for each drift test the researcher selects.** A file-consumer edge alone does not select a protection check.
- **The boundary.** Name the inputs the project receives rather than rebuilds, and get the researcher's agreement that they are not reproducible here.

Record all three in the `integrate(protect)` commit body.

## The completion gate

Run at the IMPLEMENT phase exit, once every task is approved:

```bash
superra repro build <deliverable-task>... '<check-task>#<check-step>'... --upstream
superra repro status <deliverable-task>... '<check-task>#<check-step>'... --upstream
```

Target the final deliverable tasks and the selected protection checks — the Protect completion targets once recorded; `--upstream` adds their producer chains. The gate passes when the build completes and every reported step is `fresh`; an empty selection is no evidence for a result. Valid reviewed acceptance satisfies this routine gate; requested fresh execution follows [the acceptance protocol](rerun-or-accept.md#accept). Claims outside these targets require their own [scoped verification](../SKILL.md#the-loop).

A failure blocks the completion menu:

- **A step failed** — inspect the log from `superra repro explain '<task>#<step>'` to distinguish producer, environment, and declaration failures.
- **The build succeeded and status is still dirty** — [diagnosing.md](diagnosing.md).
- **A kept result has no producer** — register it or identify its agreed external-input boundary.
