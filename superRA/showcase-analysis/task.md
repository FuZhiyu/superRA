---
title: "Canonical Asset-Pricing Test: CAPM vs Fama-French 3-Factor on the 25 Size-B/M Portfolios"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Run a real, end-to-end empirical asset-pricing study through the full superRA PLAN -> IMPLEMENT -> INTEGRATE loop, so the executed task tree itself becomes a documentation showcase: a genuine research project a visitor can explore, with real math, real figures, and a real review history.

The study is the canonical time-series test of linear factor models. Using Ken French's monthly factor returns and his 25 portfolios formed on size and book-to-market, estimate CAPM and the Fama-French three-factor model for each of the 25 test-asset portfolios, then test whether each model prices the cross-section using the Gibbons-Ross-Shanken (GRS) joint test that all intercepts are zero. The headline question is the textbook one: does adding the size (SMB) and value (HML) factors to the market factor shrink the pricing errors enough that the model is no longer rejected?

This is a documentation artifact built from fully public data — no vendor or personal data anywhere in the tree.

### Conventions

- **Test assets:** the 25 value-weighted monthly portfolios formed on the 5×5 size × book-to-market sort.
- **Excess returns:** every portfolio return is converted to an excess return by subtracting the risk-free rate `RF`. Factor series (`Mkt-RF`, `SMB`, `HML`) are already excess/long-short returns and are used as published.
- **Units:** returns are kept in percent per month as published by Ken French, so estimated intercepts ("alphas") are in percent per month — the convention in the asset-pricing literature.
- **Baseline sample:** July 1963 through the latest complete month in the file. 1963-07 is the standard start for book-to-market test assets (pre-1963 book-equity coverage is thin).
- **Specifications.** CAPM: $R_{it}-R_{ft} = \alpha_i + \beta_i\,(\text{Mkt-RF})_t + \varepsilon_{it}$. FF3: $R_{it}-R_{ft} = \alpha_i + \beta_i\,(\text{Mkt-RF})_t + s_i\,\text{SMB}_t + h_i\,\text{HML}_t + \varepsilon_{it}$. Estimated by OLS; individual significance from OLS t-statistics; joint significance of the 25 alphas from the GRS F-test.

### Context

- **Data inventory (researcher-approved 2026-06-17).** All series are public, from the [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html), downloaded by a committed script; raw files are gitignored and regenerated on demand.

  | Series | File | Columns | Span | Notes |
  |---|---|---|---|---|
  | FF research factors (monthly) | `F-F_Research_Data_Factors_CSV.zip` | `Mkt-RF, SMB, HML, RF` | 1926-07 → present | 3 header lines; monthly panel followed by an annual panel that must be cut; values in percent |
  | 25 portfolios, size × B/M (5×5) | `25_Portfolios_5x5_CSV.zip` | 25 portfolios `SMALL LoBM … BIG HiBM` | 1926-07 → present | four stacked panels (VW-monthly, EW-monthly, VW-annual, EW-annual); use the VW-monthly panel for baseline; missing = `-99.99` / `-999` |

- **Expected results (built-in sanity benchmark).** The literature gives a known answer to check against: both models are typically *rejected* by the GRS test on these 25 portfolios over the modern sample, but FF3 produces markedly smaller and less dispersed alphas than CAPM. The small-growth corner (`SMALL LoBM`) is the classic problem portfolio that keeps a sizable negative alpha even under FF3. HML loadings should rise monotonically from growth to value columns, and SMB loadings should fall from small to big rows. A run that recovers the wrong signs on these loadings is a bug, not a finding.

### Constraints

- Public data only. The download script and the committed figures are safe to commit; raw CSVs and any intermediate `.parquet` are gitignored and rebuilt by the pipeline.
- A single committed `run_all.sh` at the tree root reproduces every output in dependency order and fails fast (`set -e`): download → build panel → estimate/test/visualize. Update it whenever a script is added.
- This tree is the showcase artifact and is exported with the **full task-tracker chrome** (status pills, rollup, DAG, kanban) — non-doc-mode — by the docs build, so each task's `## Results` should read well as a standalone, figure-bearing record.

## Planner Guidance

- Scripts live under `analysis/` (and `data/` for the downloader) at the tree root; committed figures live under each task's `attachments/`. `02-analysis` carries the regression and GRS tables plus the figures; `03-writeup` re-embeds the key figures inline.

## Results

The study ran end-to-end through the workflow and reproduces from source via [run_all.sh](run_all.sh) (`download → build panel → estimate/test/visualize`, ~3.5s).

**Headline:** adding SMB and HML to the market factor halves the average pricing error on the 25 size × book-to-market portfolios (mean $|\alpha|$ 0.195 → 0.089 %/month), yet both models are still rejected by the GRS joint test over 1963-07 → 2026-04 — CAPM $F(25,728)=4.10$ and FF3 $F(25,726)=3.55$ — the canonical textbook result. FF3 prices most of the cross-section but fails on the precisely-estimated small-growth corner (`SMALL LoBM` $\alpha=-0.47$, $t=-5.1$).

- [01-data](01-data/task.md) — public Ken French data → 754-month panel (1963-07 → 2026-04), validated against published factor magnitudes.
- [02-analysis](02-analysis/task.md) — CAPM/FF3 on all 25 portfolios, GRS test (implemented from the residual covariance, cross-checked two ways), and the four figures.
- [03-writeup](03-writeup/task.md) — the reader-facing narrative with the math and the two key figures.
