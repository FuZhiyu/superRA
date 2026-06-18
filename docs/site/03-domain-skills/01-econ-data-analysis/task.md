---
title: "econ-data-analysis"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Hand a bare agent a data file and "merge these two panels and run the regression," and it writes the merge, runs the regression, and reports a coefficient — skipping everything in between. A one-to-many merge silently fans the sample out, missing returns get read as zero, an untrimmed outlier tilts the slope, and the run looks clean the whole way. A wrong number that looks clean survives into a draft.

This skill makes that failure hard to commit quietly through one rule, the **Iron Law: no transformation without prior description.** Before merging, filtering, aggregating, or constructing a variable, the agent characterizes what it is holding (a baseline); the transformation runs against it; a validate step re-describes the affected variables and checks them against the baseline. Describe, analyze, and validate run on every step, not once at the end, so when a number moves you can name the step that moved it. It loads automatically on data work, so you do not name it.

## How you ask for it

The one non-obvious move: state your expected join level, row count, or hypothesis up front. That expectation becomes the baseline the validate step checks against, so a fan-out or a mass of unmatched rows gets reported back to you instead of buried.

> "Merge `holdings.csv` (fund-quarter) into `returns.parquet` (fund-month) and build excess returns. I expect roughly 12,000 funds; flag if the merged sample is far off."

When you plan a multi-step study with `superplan`, the skill adds a **Data Inventory gate**: it will not draft task structure until it has explored your data directories, inventoried what exists, surfaced gaps, suggested sources for what is missing, and gotten your sign-off — blocking "I'll assume we have X and check later."

For the describe–analyze–validate checklist, the per-operation pitfall catalog (merges, lags, aggregations, filters, construction, missing data), and notebook-format rules, see [econ-data-analysis](skills/econ-data-analysis/SKILL.md).
