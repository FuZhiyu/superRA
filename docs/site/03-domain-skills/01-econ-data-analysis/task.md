---
title: "econ-data-analysis"
status: not-started
depends_on:  []
---

## Objective

`econ-data-analysis` makes the agent describe the data before every transformation and validate the result after, so a silent sample error surfaces at the step that caused it instead of in your headline coefficient. It loads automatically on data work.

## Every step is described, run, and validated

The skill's Iron Law: **no transformation without prior description.**

- **Before** a merge, filter, aggregation, or new variable, the agent records a baseline: panel structure, key-variable distributions, missingness.
- **After** it, the agent logs the row count, re-describes the affected variables against the baseline, and checks economic sense.
  - This catches a one-to-many merge that fans the sample out, missing returns read as zero, an untrimmed outlier tilting a slope.
  - Anything unexpected stops the run. A sensitivity check that flips a headline result comes back to you as a question.

## Give the validate step numbers to check against

- **State the outcome you expect** — join level, rough row count, sign or magnitude, the hypothesis.

  > "Merge `holdings.csv` (fund-quarter) into `returns.parquet` (fund-month) and build excess returns. I expect roughly 12,000 funds; flag if the merged sample is far off."

  - A result of 80,000 funds, the signature of a fan-out, then stops the run instead of flowing into the regression.
- **Anchor to a published number** — ask the agent to reproduce a figure a prior study reports on the same data.

  > "We're on the CRSP-Compustat merged panel. Before the main regression, reproduce the value-minus-growth return spread Fama and French report for 1963–1991 and check we land close to their number."

  - A rebuilt spread at half the published value points to sample construction — a wrong breakpoint, a sign error, a missing delisting return — found on a vetted number, not your headline result.
  - To find anchors, ask the agent to search your Zotero library with [zotero-paper-reader](#/04-utility-skills/07-zotero-paper-reader) for papers that use the same dataset.

## Planning starts with a data inventory

When you [plan](#/05-workflows/01-plan) a multi-step study, the agent explores your data directories and inventories each dataset before drafting any task. Gaps — and suggested sources for them — come back to you as questions, so no task rests on "assume we have X, check later."

For the full checklist and the per-operation pitfall catalog, see [econ-data-analysis](skills/econ-data-analysis/SKILL.md).
