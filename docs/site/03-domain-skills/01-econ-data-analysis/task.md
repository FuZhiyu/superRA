---
title: "econ-data-analysis"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Hand a bare agent a data file and "merge these two panels and run the regression," and it writes the merge, runs the regression, and reports a coefficient. What it skips is everything in between: it never checks whether the join key is unique on both sides, so a one-to-many merge silently fans 40,000 rows into 180,000; it never logs the row count before and after, so the inflation is invisible; it treats missing returns as zero because that made the column numeric; and it never looks at the tails, so one fat-fingered price of 9999 drags the mean and tilts the slope. Each is a clean-looking run that produces a wrong number, and a wrong number that looks clean survives into a draft.

This skill makes that failure hard to commit quietly. Its center is one rule, the **Iron Law: no transformation without prior description.** Before the agent merges, filters, aggregates, or constructs a variable, it characterizes what it is holding — panel and time IDs, unique-ID and unique-period counts, balancedness, types, missingness, and the tail percentiles (p1/p5/p95/p99) that catch outliers. That describe step produces a baseline; the transformation runs against it; a validate step re-describes the affected variables and checks the result against the baseline. Describe, analyze, and validate run on every step, not once at the end, so when a number moves you can name the step that moved it. The discipline is the same whether the code is Python, Julia, R, or Stata.

You do not invoke it by name. It loads automatically on any data task — importing, cleaning, merging, constructing variables, aggregating, running regressions, making figures — so "using" it means handing the agent real data work and letting the law fire.

## What it forces the agent to do

**Describe before and after.** On every input, before the first transformation: panel structure (panel ID, time ID, counts, date range, balancedness), variable diagnostics on the key variables (mean/median/std plus the p1/p5/p95/p99 tails), data types, and per-variable missingness. After every merge, filter, construction, or aggregation, it re-runs describe on the affected variables and compares; an unexpected distribution shift flags silent corruption.

**One operation per step, with row-count logging.** No chaining merge + filter + construct into one untraceable cell. Every sample-changing operation prints `before → after` so a dropped or duplicated row is visible at the step that caused it.

**Validate against economic sense, not just internal consistency.** Row counts match the join's expectation; magnitudes are plausible (GDP growth of 300% is wrong); signs and correlations match known stylized facts; constructed variables and growth rates get spot-checked by hand against published benchmarks (IMF WEO, World Bank, prior literature). When the task states expected results or a hypothesis, findings are compared against them explicitly and divergences flagged before the agent moves on.

**Operation-specific pitfall checks**, walked only when the task does that operation:

- **Merges** declare 1:1 / m:1 / 1:m up front (many-to-many is almost always a Cartesian-product bug) and log unmatched rows on both sides.
- **Lags/leads/diffs** sort by panel-time first and check for gaps before shifting — a naive `shift(1)` across a missing period is silently wrong (in Julia, `PanelShift.jl` handles gaps correctly).
- **Aggregations** check the function matches the content (sum dollars, average rates, never the reverse) and that duplicates are cleared before grouping.
- **Filters** verify `&`-vs-`|` boolean logic and check whether drops are concentrated rather than random.
- **Variable construction** enforces `log → winsorize → standardize` order and checks ratio denominators for near-zero.
- **Missing data** disambiguates "no position (→ 0)" from "didn't report (→ missing)" — missing returns treated as zero is almost always wrong.

When a sensitivity check flips a headline coefficient's sign or kills its significance, the agent stops and asks you with `AskUserQuestion`. Divergence is a methodology call, not an RA decision.

## How you invoke it

Frame the task in data terms and state the unknowns up front. The expected join level and an expected count become the baseline the validate step checks against, so a fan-out or a mass of unmatched rows gets reported back to you instead of buried:

> "Merge `holdings.csv` (fund-quarter) into `returns.parquet` (fund-month) and build excess returns. I expect roughly 12,000 funds; flag if the merged sample is far off."

Other framings that play to the skill's strengths:

- **Name the operations you know are coming** ("this needs a lag, and the panel has entry/exit"), so the agent loads the matching pitfall subsection and sorts before shifting.
- **State expected results or hypotheses**, even loosely ("treated firms should show a small positive effect"). The validate step compares findings against them and flags divergence.
- **Ask for a specific stress test** ("rerun the headline regression winsorizing at 1/99 instead of trimming"). One variation per check; the skill escalates to you if a variation changes the story.

A construction-and-tabulation task runs the same loop end to end:

> "Construct annual firm-level leverage from this Compustat extract, winsorize at 1/99, and report summary stats by Fama-French industry."

The agent describes the extract, flags the winsorization cutoff in a markdown cell, logs the rows affected, and re-describes leverage after winsorizing before it tabulates anything.

When you plan a multi-step study with `superplan`, the skill adds a **Data Inventory hard gate**: it will not draft task structure until it has explored your data directories, inventoried what exists (path, format, rows × columns, key variables, date range, source), surfaced gaps, suggested concrete sources (WRDS, FRED, IMF WEO, replication packages) for what is missing, and gotten your sign-off. The gate blocks "I'll assume we have X and check later." Planning also designs sensitivity checks as their own tasks.

Analysis scripts come back in notebook format (jupytext percent for Python; QuartoNotebookRunner for Julia — not jupytext, which breaks `include()` and `@__DIR__`), with a markdown cell stating intent and expectations before each code cell and findings after. Figures land in the task's `attachments/` and findings are written into the task's `## Results`. If the agent transformed before it described, that is a reviewable violation, not a judgment call — the baseline either exists or it does not.

For the full describe–analyze–validate checklist, the per-operation pitfall catalog, and the planning, robustness, and notebook references, see [econ-data-analysis](skills/econ-data-analysis/SKILL.md).
