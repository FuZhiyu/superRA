---
title: "Refresh Pages That Predate 0.5"
status: approved
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

## Results

Every docs surface outside the Quickstart now describes 0.5.0 as shipped and routes reproduction questions to the [reproducibility page](../../../../docs/site/04-utility-skills/09-reproducibility/task.md). `docs/build_site.sh` exits 0 and `superra task check --root docs/site` passes.

- **Objective items, as specified:**
  - [Dashboard page](../../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md): Tree and Graph views, a `Step freshness in the Graph view` section covering step states, step details, and the live-only Build menu. Kanban is gone from the page, since the dashboard removed it.
  - [IMPLEMENT](../../../../docs/site/05-workflows/02-implement/task.md), [INTEGRATE](../../../../docs/site/05-workflows/03-integrate/task.md) Protect, and the [Workflows overview](../../../../docs/site/05-workflows/task.md): one sentence each on the completion freshness check, agreeing external inputs, and onboarding as the entry for an existing project.
  - [Landing page](../../../../docs/site/task.md): the utility-skills bullet names reproduction; "Start here" gains a Reproducibility line.
  - [README.md](../../../../README.md): the readiness / `--upstream` / accept paragraph is deleted from §Upgrading, which now holds only the 0.5.0 and 0.4.0 upgrade steps; the utility-skills bullet links the docs page.
- **Three more stale pages, fixed beyond the named list:**
  - [Showcase page](../../../../docs/site/07-showcase/task.md): the "DAG" and "kanban board" bullets became one Graph-view bullet.
  - [Task-tree overview](../../../../docs/site/04-utility-skills/01-task-tree/task.md): "open the dashboard" no longer promises a frontier, DAG, and kanban view.
  - [Hooks page](../../../../docs/site/06-hooks/task.md): the `task-hook` row now names the producer-edit reminder.
- **Grep over `docs/site` and `README.md`: two unintended hits remain, both in the Quickstart, which [03-quickstart](../03-quickstart/task.md) owns.**
  - [02-quickstart/task.md:91](../../../../docs/site/02-quickstart/task.md#L91) cites `run_all.sh`.
  - [02-quickstart/task.md:114](../../../../docs/site/02-quickstart/task.md#L114) tells the reader to toggle a **Kanban** view that no longer exists.
  - Intended hits: the review "depth tier" (IMPLEMENT page), academic-writing's "fix tiers", Mistral's "free tier", and the README `Unreleased` banner and §Upgrading step text (`tier:`, `pytask.lock`), which stay until Finish.
