---
title: "Capture Stage Screenshots for the Quickstart"
status: not-started
depends_on:
  - 01-export-and-framing
tags: []
created: 2026-06-17
---

## Objective

Give the quickstart tutorial visual proof of the workflow by showing the *same real tree* at three moments, and embed the images in [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md):

1. **After planning** — the analysis tree freshly planned, every task `not-started` (the frontier laid out).
2. **Mid-implement** — a genuine mixed-status moment: some children `approved`, one `implemented` awaiting review, one in `revise`, the rest `not-started`, with the parent rolled up. This is the state that shows status pills, the rollup, and the kanban doing real work.
3. **Complete** — the whole tree `approved`.

Each screenshot is a capture of the task-tree dashboard / standalone export rendered with **full chrome** (not the doc-mode site), so the quickstart shows the actual task tracker, matching the explorable export from `01-export-and-framing`.

**Capture mechanism.** Reproduce each state, export it with `plan_dashboard.py generate` (full chrome), and render the standalone HTML to PNG headlessly — a PEP 723 Playwright/Chromium script is the expected route. The "after planning" and "complete" states are real points in the analysis tree's git history; capture them by checking out the corresponding commit. The "mid-implement" mixed composition (some `approved`, one `implemented`, one `revise`, rest `not-started`) may never exist as a single committed snapshot — the implementer-reviewer loop advances statuses across many commits and a `revise` state is transient — so if no real commit captures it, construct the snapshot deliberately: copy the `showcase-analysis/` task files to a throwaway location, hand-set the frontmatter `status` fields to the target composition (never committing these edits to the live tree), and export from there. Record the exact commits / snapshot recipe and the command used so every image regenerates. Commit the PNGs under this task's `attachments/` and reference them from the quickstart with captions tying each to its workflow phase (PLAN → IMPLEMENT mid-flight → done).

**Validation:** the three images render in the built quickstart page, visibly differ in status composition (all grey → mixed colors → all green), and the regeneration steps are documented well enough to rebuild them.

## Results

*(filled during implementation)*
