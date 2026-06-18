---
title: "econ-data-analysis"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You get an agent that always knows what it is holding before it changes it. The discipline at the center is the **Iron Law: describe the data before you transform it.** Shapes, keys, distributions, missingness, and balancedness come first, so the agent can't quietly drop half the sample on a bad merge and report that everything looked fine — and so the reviewer has a described baseline to check the transformation against.

The law sits inside a **describe–analyze–validate loop**: describe the data as it arrives, run the analysis step, then validate that the output is what the step should have produced. Around that loop are pitfall catalogs for the operations that bite hardest in applied work — merges that silently change row counts, time-series alignment, and aggregations that drop or double-count. The discipline is language-agnostic: it runs the same whether your code is in Python, Julia, R, or Stata.

Reach for it for any work on economic, financial, or panel data — importing, cleaning, merging, building variables, aggregating, running regressions, making figures — and especially when you hand the agent a data file whose structure it has not seen. That is the moment the Iron Law earns its keep: the agent characterizes the panel before it writes the first variable, and a merge that would have dropped observations gets caught at the describe step rather than in a published number.

For the full methodology and the per-operation pitfall catalogs, see [econ-data-analysis](skills/econ-data-analysis/SKILL.md).
