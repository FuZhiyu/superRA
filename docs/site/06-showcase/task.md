---
title: "Showcase: An Example Task Tree"
status: not-started
depends_on:  []
---

## Objective

Open a finished example superRA task tree and click around. It is the same dashboard you get when you run superRA — this documentation site is one too.

[Open the asset-pricing study →](showcase-analysis-tree.html)

## The study: do CAPM and Fama-French three-factor price the cross-section?

The tree runs the canonical time-series test of linear factor models on public data: it estimates CAPM and the Fama-French three-factor model on Ken French's 25 size and book-to-market portfolios, then applies the Gibbons-Ross-Shanken (GRS) joint test.

- **Every task is `approved`**, so you are reading the completed state: regression tables and figures embedded in each task's `## Results`.
- **`02-analysis`** holds the GRS verdict; **`03-writeup`** holds the reader-facing narrative with the math.

## What to look for

- **Status pills.** Green `approved`, yellow `implemented` (done, approval open), red `revise` (sent back by a reviewer), blue `in-progress`, grey `not-started`. The [status lifecycle](#/03-utility-skills/01-task-tree) explains the transitions.
- **Rollup.** A parent's status is computed from its children, so an unfinished child shows on the parent.
- **The Graph view.** Switch from **Tree** to **Graph** to see each task's [reproduction steps](#/03-utility-skills/02-reproducibility) and their freshness; the [task-tree page](#/03-utility-skills/01-task-tree) explains how to read it.
- **Inside a task.** Click a task to read its `task.md`: the objective, then the results the implementer wrote. The [task-tree page](#/03-utility-skills/01-task-tree) gives the full anatomy.
- **Deep links.** The address bar tracks the task you are viewing, so you can bookmark or share a link to one task.

## Make one of your own

Ask the agent to export the dashboard, or run `./superRA/superra dashboard export --output dashboard.html`. You get one self-contained HTML file like this one ([task-tree](#/03-utility-skills/01-task-tree) covers sharing). The [Quickstart](#/01-quickstart) also links this study at two earlier moments: right after planning and mid-implementation.
