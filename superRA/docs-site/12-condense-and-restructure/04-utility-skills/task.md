---
title: "Author the Utility Skills Page"
status: not-started
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Author `docs/site/04-utility-skills/task.md`: introduce superRA's utility skills one by one, each with its **high-level design idea**, so an adopting researcher knows what reusable, domain-neutral tools exist and what each gives them.

Open with the design idea: utility skills are domain-agnostic tools the workflow and agents compose as needed — and several are directly useful to a researcher standalone. They are the "mechanisms over contingency trees" layer: reusable pieces assembled for the situation at hand.

Then one short section per utility skill, stated as what it does for the user:

- **`task-tree`** — the filesystem-as-task-hierarchy tooling: `task.md` per task, sibling dependencies, status rollup, frontier, DAG, and the live dashboard. (This is the flagship; give it the most room.)
- **`semantic-merge`** — intent-aware branch integration: resolves conflicts by understanding what each side meant rather than a blind ours/theirs merge.
- **`result-protection`** — drift/regression tests that guard key results from silently changing later.
- **`refactor-and-integrate`** — codebase-coherence tools: convention fit, utility reuse, PR-friendly minimum-diff integration.
- **`report-in-markdown`** — the markdown style guide agents follow when writing task files and reports.
- **`worktree-data-sync`** — syncing non-git data between worktrees for parallel work.
- **`zotero-paper-reader`** / **`mistral-pdf-to-markdown`** — user-invocable standalone helpers (Zotero reading + citations; PDF→markdown). Note they are standalone, not part of the core workflow loop.

Each skill gets a framing + design idea + a link to its `SKILL.md` as the authority — thin, no paraphrase. No internal load-order or who-calls-what mechanics (contributor detail).

## Planner Guidance

`skills/CATEGORIES.md §Utility` is the source of truth for membership and one-line purpose. Decide an ordering that serves a reader (flagship `task-tree` first; standalone helpers last) rather than the alphabetical CATEGORIES order.
