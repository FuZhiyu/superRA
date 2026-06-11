---
title: "Task-Tree Showcase: Embedded Real Exports"
status: not-started
depends_on:
  - 01-information-architecture
tags: []
created: 2026-06-10
---

## Objective

Produce the showcase that lets a visitor *see* the task tree instead of reading about it:

- **A curated demo task tree** — a small, realistic, public-safe hypothetical research analysis (a handful of tasks with objectives, results, review notes, a figure, statuses mid-flight) — committed as a source tree and exported with the standard (non-doc-mode) standalone export so the full task-tracker UI shows: status pills, rollup, DAG, kanban.
- **superRA's own development tree** — the real `superRA/` tree of this repo, exported the same way, as the existence proof.
- Both exports wired into the site per the IA (linked pages or embeds), with a short framing page explaining what the visitor is looking at and how it maps to the concepts section.
- A documented regeneration command for each export so `08-deploy` can rebuild them in CI; exports themselves are not committed.

Validation: open each exported file and verify the trees render with full chrome, deep links work, and the demo tree contains no real personal or project data.

## Planner Guidance

The demo tree doubles as seed material for `04-quickstart-tutorial`'s example; coordinate so the tutorial's toy analysis and the demo tree don't tell conflicting stories.
