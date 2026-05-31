---
title: "Make DAG and Kanban views navigable"
status: not-started
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

The dashboard's DAG and Kanban views are not informative and can't be clicked into. Make both navigable, and ship **both** DAG redesigns as complementary, coexisting features rather than picking one: inline per-subtree DAG panels for local context, and a clickable global DAG tab for whole-project overview. Everything routes node/card clicks through a single shared "reveal the task in the tree, expanded to its details" primitive.

The live dashboard is the FastAPI/htmx server at `skills/task-system/scripts/plan_dashboard.py`; the views live in `skills/task-system/scripts/templates/` (`base.html`, `dag.html`, `kanban.html`, `task_node.html`, `task_children.html`). A load-bearing fact for the DAG work: dependencies in this task system are **sibling-only**, so a dependency graph is inherently a per-subtree (sibling-scoped) artifact — which is why one flat global DAG reads as noise and why the inline per-subtree panel is the natural unit.

## Decomposition

- `navigate-to-task` — the shared click→reveal navigation primitive, wired first to the Kanban cards. Foundation for the two DAG designs.
- `dag-inline-panels` — Design A: a foldable per-subtree DAG panel under each parent task. Depends on `navigate-to-task`.
- `dag-global-tab` — Design B: keep the global DAG tab but make its nodes clickable and cluster it by subtree. Depends on `navigate-to-task`.
