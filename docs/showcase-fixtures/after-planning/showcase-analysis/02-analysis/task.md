---
title: "Estimate, Test, and Visualize: CAPM vs FF3"
status: not-started
depends_on:
  - 01-data
tags: []
script: analysis/02_analysis.py
input: data/ff_panel.parquet
output: data/regression_estimates.parquet, data/grs_results.csv, 02-analysis/attachments/*.png
created: 2026-06-17
---

## Objective

The core of the study: estimate both factor models for the 25 portfolios, run the GRS joint test on each, and produce the showcase figures — one coherent estimate→test→visualize unit.

### Regressions

For each of the 25 portfolios, estimate by OLS on the baseline sample from `01-data`:

- **CAPM:** $R_{it}-R_{ft} = \alpha_i + \beta_i\,(\text{Mkt-RF})_t + \varepsilon_{it}$
- **FF3:** $R_{it}-R_{ft} = \alpha_i + \beta_i\,(\text{Mkt-RF})_t + s_i\,\text{SMB}_t + h_i\,\text{HML}_t + \varepsilon_{it}$

Record, per portfolio and model, the intercept $\alpha_i$ (percent/month), the factor loadings, OLS t-statistics, and $R^2$. Persist the full estimate table to `data/regression_estimates.parquet`, and retain each model's $25\times1$ alpha vector and $25\times25$ residual covariance for the GRS step.

### GRS joint test

Test the null that all 25 intercepts are jointly zero, for CAPM ($K=1$) and FF3 ($K=3$), with the Gibbons-Ross-Shanken (1989) statistic:

$$ \text{GRS} = \frac{T-N-K}{N}\,\Big(1 + \bar{f}'\,\hat{\Omega}^{-1}\,\bar{f}\Big)^{-1}\,\hat{\alpha}'\,\hat{\Sigma}^{-1}\,\hat{\alpha} \;\sim\; F_{N,\;T-N-K} $$

where $N=25$ test portfolios, $K$ factors, $T$ months, $\hat{\alpha}$ the $N\times1$ intercept vector, $\hat{\Sigma}$ the $N\times N$ (ML) residual covariance, $\bar{f}$ the $K\times1$ factor means, and $\hat{\Omega}$ the $K\times K$ factor covariance. Compute the statistic, its degrees of freedom $(N,\,T-N-K)$, and the p-value for each model. Report two economic summaries of the pricing errors: the mean absolute alpha, and the quadratic form $\hat{\alpha}'\hat{\Sigma}^{-1}\hat{\alpha}$ — which is the **squared Sharpe ratio of the maximal pricing-error portfolio**, equivalently the increment $Sh^2(\text{factors}+\text{test assets}) - Sh^2(\text{factors})$ to the maximum squared Sharpe ratio from adding the test assets to the factors (it is not a ratio of Sharpe ratios). Save to `data/grs_results.csv`.

### Figures

With matplotlib (PEP 723, headless `Agg`), save PNGs into this task's `attachments/`, each embedded in `## Results` with a self-contained caption:

1. **Alpha grids (CAPM vs FF3)** — two 5×5 heatmaps of the alphas on the size × book-to-market grid, shared diverging scale, so the collapse of pricing errors from CAPM to FF3 is visually immediate.
2. **Realized vs. predicted** — scatter of mean realized excess return against model-predicted return for the 25 portfolios under each model; distance off the 45° line is the pricing error, tighter under FF3.
3. **Cumulative factor returns** — cumulative growth of \$1 in `Mkt-RF`, `SMB`, `HML` over the sample.
4. **FF3 HML loadings across the grid** — illustrating the monotone growth-to-value gradient that lets FF3 price the value sort.

### Validation

Report the regression results as 5×5 grids (CAPM alphas, FF3 alphas with t-stats, FF3 SMB and HML loadings) and the GRS results as a two-model table in `## Results`. Check against the expected results in the root `### Context`: FF3 alphas smaller and less dispersed than CAPM; `SMALL LoBM` retains a notable negative FF3 alpha; HML loadings rise growth→value, SMB loadings fall small→big; both models typically rejected on the modern sample, with FF3's GRS statistic and mean absolute alpha well below CAPM's. Cross-check the GRS implementation directly on the residual covariance (confirm $\hat{\Sigma}$ symmetric positive-definite, $T-N-K>0$) rather than trusting a black-box one-liner. State each model's verdict (reject / fail to reject) explicitly, and flag any loading sign reversal before marking done.

## Results

*(filled during implementation)*
