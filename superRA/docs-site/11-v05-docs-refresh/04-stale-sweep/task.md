---
title: "Refresh Pages That Predate 0.5"
status: not-started
depends_on: [02-repro-page]
---

## Objective

Make every remaining docs surface describe 0.5.0 as shipped and point reproduction questions to [the reproducibility page](../02-repro-page/task.md).

- **[Dashboard page](../../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md):** drop "under development"; describe the Graph view, step freshness, and the build button as shipped.
- **Workflow pages:** [IMPLEMENT](../../../../docs/site/05-workflows/02-implement/task.md) says completion verifies retained results are fresh; [INTEGRATE](../../../../docs/site/05-workflows/03-integrate/task.md) Protect says the researcher agrees which inputs are external; the [Workflows overview](../../../../docs/site/05-workflows/task.md) names onboarding as the entry for an existing project. One or two sentences each, linking out.
- **Landing page** ([docs/site/task.md](../../../../docs/site/task.md)): the utility-skills bullet names reproduction; "Start here" links the reproducibility page.
- **[README.md](../../../../README.md):** the readiness / `--upstream` / accept paragraph leaves §Upgrading for the docs page; §Upgrading keeps only upgrade steps. The utility-skills feature bullet links the docs page.
- A final grep over `docs/site` and `README.md` for `run_all`, `pytask`, `tier`, `under development`, and `Unreleased` finds only intended hits.

## Details

- The README "0.5.0 is unreleased" banner and the `Unreleased` heading in [RELEASE-NOTES.md](../../../../RELEASE-NOTES.md) flip at Finish, not here.
