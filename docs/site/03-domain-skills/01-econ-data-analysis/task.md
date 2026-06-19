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

## How to use

The agent loads this skill automatically once data analysis is involved, so you do not name it. What you control is how much the validate step has to check against: the more you tell it to expect, the more it can catch. Two habits make the difference.

### State your expectation up front

When you ask for a transformation, say what you expect to come out the other side: the join level, the rough row count, the sign or magnitude of a result, the hypothesis you are testing. That expectation becomes the baseline the validate step measures against, so a fan-out from a bad merge or a mass of unmatched rows gets reported back to you instead of buried under a clean-looking coefficient.

> "Merge `holdings.csv` (fund-quarter) into `returns.parquet` (fund-month) and build excess returns. I expect roughly 12,000 funds; flag if the merged sample is far off."

Without the "roughly 12,000 funds" clause the agent still merges, but it has no number to be surprised by. With it, a result of 80,000 funds — the signature of a one-to-many fan-out — stops the run instead of flowing into the regression.

### Anchor the validate step to a published number

The validate step checks numbers against internal consistency by default. You can give it an external anchor: when a prior study has used your dataset, ask the agent to add a test that reproduces a known published figure. If your reconstruction lands far from theirs, a build error surfaces before it reaches your own analysis.

> "We're on the CRSP-Compustat merged panel. Before the main regression, reproduce the value-minus-growth return spread Fama and French report for 1963–1991 and check we land close to their number."

If the rebuilt spread comes out at half the published value, the problem is in your sample construction — a wrong breakpoint, a sign error, a missing delisting return — and you find it on a number someone has already vetted, not on your headline result.

To find those anchors, compose with [`zotero-paper-reader`](#/04-utility-skills/07-zotero-paper-reader): ask the agent to search your Zotero library for papers that use the same dataset and build external-validation tests from the numbers they report.

### Planning a multi-step study

When you plan a multi-step study with `superplan`, the skill adds a **Data Inventory gate**: it will not draft task structure until it has explored your data directories, inventoried what exists, surfaced gaps, suggested sources for what is missing, and gotten your sign-off. That blocks the "I'll assume we have X and check later" failure before any task is written.

For the describe–analyze–validate checklist, the per-operation pitfall catalog (merges, lags, aggregations, filters, construction, missing data), and notebook-format rules, see [econ-data-analysis](skills/econ-data-analysis/SKILL.md).
