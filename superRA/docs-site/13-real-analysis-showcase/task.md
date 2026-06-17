---
title: "Wire the Real Asset-Pricing Tree into the Docs"
status: not-started
depends_on:
  - 07-showcase
tags: []
created: 2026-06-17
---

## Objective

Surface the executed [showcase-analysis](../../showcase-analysis/task.md) tree (the real CAPM-vs-FF3 study) in the documentation site, in the two places the researcher named: as a standalone explorable export, and as stage screenshots in the quickstart. This extends the showcase that `07-showcase` built (the simulated demo tree and superRA's own dev tree) with the *real, executed* counterpart.

This branch depends on the `showcase-analysis` workstream being complete (all children `approved`) so that the exported tree carries finished results and figures. That dependency is cross-subtree and cannot be expressed in `depends_on`; the orchestrator sequences it.

### Context

- The export and embed mechanics — `plan_dashboard.py generate`, `docs/build_site.sh`, the framing page at `docs/site/06-showcase/task.md`, and the GitHub Actions path filters — are owned and documented by `07-showcase` and `08-deploy`. Reuse them; do not reinvent.
- The showcase tree is a subtree of `superRA/`, so it is exported by scoping the full repo tree to it: `--plan-root superRA --root showcase-analysis --repo-file-prefix superRA/showcase-analysis`.

### Constraints

- The explorable export must use the **full task-tracker chrome** (status pills, rollup, DAG, kanban) — i.e. the standard `generate` without `--doc-mode`, exactly like the existing `demo-tree.html` and `superra-dev-tree.html` exports. It must not render as a flattened doc page.
- Exports are CI-built, never committed; only sources (the build script, framing-page edits, and committed screenshot PNGs) are committed.

## Planner Guidance

Two children, independently dispatchable once `showcase-analysis` is done.
