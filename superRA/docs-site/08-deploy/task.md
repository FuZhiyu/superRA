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

- A GitHub Actions workflow that builds the site — doc-mode export of the docs tree as the main site entry plus the two showcase exports — and deploys to GitHub Pages. Triggers: `workflow_dispatch` plus push to the default branch (the push trigger goes live once the workstream lands). GitHub registers `workflow_dispatch` only for workflow files present on the default branch, so in-branch verification requires seeding the workflow file onto `main` first, then dispatching with `--ref` pointing at this branch.
- A single committed local build script that produces the identical site output for local preview, used by the workflow (the pipeline entry point for this workstream).
- The build fails loudly on export errors or missing inputs; no silent partial deploys.
- The live site URL recorded where users discover it: repo About, `.claude-plugin`/`.codex-plugin` manifest homepage fields, and handed to `09-readme-front-door` for the README links.

**Stop point:** two researcher/admin actions gate the deploy verification — enabling GitHub Pages (Actions source) and seeding the workflow file onto the default branch (a push to `main` outside the normal squash-merge landing). Request both before verification and record the outcomes here. If the researcher declines to touch `main` early, the in-branch criterion is the fallback below and the live-URL validation defers to landing.

Validation, in-branch: the local build script succeeds, and — per the stop-point outcome — either a `workflow_dispatch --ref <this branch>` run deploys a real Pages site where the landing page, sidebar nav, search, highlighted code blocks, deep links, and both showcase exports work (verified by loading the published URL), or, on the fallback path, the exported site artifact is verified locally and the live-URL check is recorded in `## Results` as a landing-time follow-up. The push-trigger path is verified after the workstream lands on the default branch.

**Known plumbing issue to resolve (found by 03 during authoring):** the standalone export re-bases repo-relative file links against the doc node's directory under the docs root, so a contract-compliant authority link like `skills/superplan/SKILL.md` on a page at `03-concepts/01-the-workflow/` resolves to `<repo-file-base>/site/03-concepts/01-the-workflow/skills/superplan/SKILL.md` — a nonexistent path. The build must make repo-file links resolve repo-root-relative against `--repo-file-base` (an export-flag or doc-mode change coordinated with the `02-dashboard-features/doc-mode` flag surface). Acceptance: every authority link on the built site points at a real blob URL.

## Planner Guidance

`skills/task-tree/scripts/templates/superra-dashboard-artifact.yml` is the existing CI export precedent; the doc-mode flag/invocation comes from `02-dashboard-features/doc-mode`'s recorded `## Results`.

Content tasks 04–06 are not build prerequisites — the site can deploy with the IA-scaffolded stubs present — but confirm with the researcher before publishing a visibly incomplete site versus deploying to Pages only after 04–06 land.
