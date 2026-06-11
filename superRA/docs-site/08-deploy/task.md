---
title: "Build Pipeline + GitHub Pages Deploy"
status: not-started
depends_on:
  - 02-dashboard-features
  - 03-landing-and-concepts
  - 07-showcase
tags: []
created: 2026-06-10
---

## Objective

Stand up the site build and publish it:

- A GitHub Actions workflow that builds the site — doc-mode export of the docs tree as the main site entry plus the two showcase exports — and deploys to GitHub Pages. Triggers: `workflow_dispatch` (runnable from this branch for verification now) plus push to the default branch (active once the workstream lands).
- A single committed local build script that produces the identical site output for local preview, used by the workflow (the pipeline entry point for this workstream).
- The build fails loudly on export errors or missing inputs; no silent partial deploys.
- The live site URL recorded where users discover it: repo About, `.claude-plugin`/`.codex-plugin` manifest homepage fields, and handed to `09-readme-front-door` for the README links.

**Stop point:** enabling GitHub Pages (Actions source) on the repo is a researcher/admin action — request it before the deploy verification and record the outcome here.

Validation, in-branch: the local build script succeeds, and a `workflow_dispatch` run from this branch deploys a real Pages site where the landing page, sidebar nav, search, highlighted code blocks, deep links, and both showcase exports work — verified by loading the published URL. The push-trigger path is verified after the workstream lands on the default branch (note it in `## Results` as a landing-time follow-up).

## Planner Guidance

`skills/task-tree/scripts/templates/superra-dashboard-artifact.yml` is the existing CI export precedent; the doc-mode flag/invocation comes from `02-dashboard-features/doc-mode`'s recorded `## Results`.

Content tasks 04–06 are not build prerequisites — the site can deploy with the IA-scaffolded stubs present — but confirm with the researcher before publishing a visibly incomplete site versus deploying to Pages only after 04–06 land.
