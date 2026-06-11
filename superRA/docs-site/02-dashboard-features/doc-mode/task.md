---
title: "Doc-Mode Rendering Toggle"
status: not-started
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Add an opt-in doc-mode to `plan_dashboard.py serve` and `generate` (plumbed through the `cli.py dashboard` surface) that renders a tree as documentation rather than as a task tracker.

In doc-mode:

- Task-workflow chrome is suppressed: status pills/badges, the header progress bar and status stats, and the kanban view toggle.
- The root node's body renders as the landing view on load, so the exported file opens on a home page rather than an empty selection.
- Tree sidebar navigation, section rendering, math, images, hash deep links, and theming all behave as today.

Success criteria: a doc-mode standalone export contains no status-pill or kanban markup; a default (no-flag) export is unchanged relative to the pre-doc-mode baseline (sibling features that legitimately ship by default are not regressions); both verified by inspecting the rendered artifact and covered by tests on the generated HTML.

## Planner Guidance

Whether the DAG view is suppressed too is implementer judgment — it is meaningless for a docs tree with no `depends_on` edges; document the call in `## Results`.

The flag name and whether doc-mode is a CLI flag, frontmatter marker on the root node, or both is implementer judgment within the additive/opt-in constraint — coordinate the choice with `08-deploy`'s build invocation by recording it in `## Results`.
