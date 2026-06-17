---
title: "Writeup: Does FF3 Price the Size-Value Cross-Section?"
status: revise
depends_on:
  - 02-analysis
tags: []
script: (none — narrative synthesis)
input: results from 02-analysis
output: this task's ## Results (the matured narrative)
created: 2026-06-17
---

## Review Notes

1. **MAJOR** — [task.md:26](task.md#L26), [task.md:29](task.md#L29), [task.md:50](task.md#L50), [task.md:60](task.md#L60), [task.md:69](task.md#L69), [task.md:78](task.md#L78): the six `<!-- intent: … -->` HTML comments are a Draft-mode authoring artifact addressed to the editing process, not to the showcase-visiting researcher. They render invisibly (markdown-it `html: true` + DOMPurify pass the comment nodes through, but the browser does not display them), yet they ship verbatim in the committed source the docs build exports as the showcase, and no sibling showcase node (01-data, 02-analysis) carries any. They are process-internal scaffolding leaking into a reader-facing node — the writing skill's audience discipline (write to the reader, not the conversation). **Fix:** strip all six `<!-- intent: … -->` lines (and the blank line each leaves) from `## Results`. The section headings already convey the same structure to the reader.

## Objective

Synthesize the study into a short, self-contained reader-facing narrative in `## Results` — the matured account a showcase visitor lands on. It should:

- State the question and the test, including the CAPM and FF3 specifications and the GRS statistic, rendered as math.
- Report the headline verdict for both models (GRS statistic, p-value, mean absolute alpha) from `02-analysis`.
- Embed the key figures from `02-analysis` (the CAPM-vs-FF3 alpha grids and the realized-vs-predicted scatter) inline with interpretation.
- Draw the economic conclusion: how much of the size-value cross-section FF3 explains relative to CAPM, where it still fails (the small-growth corner), and what that implies.

Write for a researcher reader following `report-in-markdown`; link down to `02-analysis` for the per-task evidence rather than restating every number. No new estimation — this task only narrates and cross-references results `02-analysis` already produced and verified.

## Results

<!-- intent: governing verdict up front — FF3 halves the pricing errors but is still rejected, the textbook answer. -->
Adding the size and value factors to the market factor halves the average pricing error on the 25 size × book-to-market portfolios, but it does not rescue the model: both CAPM and the Fama-French three-factor model are rejected by the Gibbons-Ross-Shanken joint test over 1963-07 → 2026-04. The three-factor model explains most of the size-value cross-section the market factor alone cannot, then fails on a handful of precisely-estimated corners, chiefly small-growth. This is the canonical textbook outcome, recovered here on the modern sample. The per-portfolio estimates, the full set of grids, and the implementation cross-checks live in [02-analysis](../02-analysis/task.md); this account narrates the verdict and the two figures that carry it.

<!-- intent: state the question and the test with the two specifications and the GRS statistic as math. -->
### The question and the test

The test assets are Ken French's 25 value-weighted portfolios formed on a 5×5 size × book-to-market sort, in excess of the risk-free rate, over 754 months (1963-07 → 2026-04). For each portfolio $i$ we estimate two linear factor models by OLS,

$$
R_{it}-R_{ft} = \alpha_i + \beta_i\,(\text{Mkt-RF})_t + \varepsilon_{it},
$$

$$
R_{it}-R_{ft} = \alpha_i + \beta_i\,(\text{Mkt-RF})_t + s_i\,\text{SMB}_t + h_i\,\text{HML}_t + \varepsilon_{it},
$$

and ask whether the model prices the cross-section. Under a correctly specified factor model every intercept $\alpha_i$ is zero. The Gibbons-Ross-Shanken (1989) statistic tests that null jointly across all $N=25$ portfolios,

$$
\text{GRS} = \frac{T-N-K}{N}\,\Big(1 + \bar{f}'\,\hat{\Omega}^{-1}\,\bar{f}\Big)^{-1}\,\hat{\alpha}'\,\hat{\Sigma}^{-1}\,\hat{\alpha} \;\sim\; F_{N,\;T-N-K},
$$

with $K$ factors, $T$ months, $\hat\alpha$ the $N\times1$ intercept vector, $\hat\Sigma$ the $N\times N$ residual covariance, $\bar f$ the $K\times1$ factor means, and $\hat\Omega$ the $K\times K$ factor covariance. The quadratic form $\hat\alpha'\hat\Sigma^{-1}\hat\alpha$ carries the economic content: it is the squared Sharpe ratio of the maximal pricing-error portfolio — the increment $Sh^2(\text{factors}+\text{test assets}) - Sh^2(\text{factors})$ to the maximum squared Sharpe ratio from adding the 25 test assets to the factors. It is not a ratio of Sharpe ratios. A model fails the test when the test assets offer Sharpe-ratio improvement the factors cannot span.

<!-- intent: report the headline numbers for both models from 02-analysis. -->
### The verdict

| Model | GRS $F(df_1,df_2)$ | $p$-value | Verdict | mean \|α\| (%/mo) | $\hat\alpha'\hat\Sigma^{-1}\hat\alpha$ (monthly) |
|---|---:|---:|:--|---:|---:|
| CAPM | $F(25,728)=4.10$ | $1.7\times10^{-10}$ | **reject** $H_0$ | 0.195 | 0.143 |
| FF3  | $F(25,726)=3.55$ | $1.8\times10^{-8}$  | **reject** $H_0$ | 0.089 | 0.127 |

Both models reject the null that all 25 intercepts are jointly zero, at any conventional level. The three factors halve the average pricing error — mean $|\alpha|$ falls from 0.195 to 0.089 %/month — yet the GRS statistic stays far in the rejection region. The quadratic form barely moves (0.143 → 0.127) even as mean $|\alpha|$ halves, because the residual pricing ability that defeats the three-factor model is concentrated in a few corners with large, sharply-estimated alphas rather than spread evenly across the grid. A test that weights each alpha by its precision through $\hat\Sigma^{-1}$ still rejects strongly.

<!-- intent: figure 1 — the alpha grids, the central visual of the collapse. -->
### Where the pricing errors live

The collapse of the pricing errors from CAPM to the three-factor model is visible directly on the size × book-to-market grid.

![CAPM and FF3 alpha grids on the 5×5 size × book-to-market sort, shared diverging color scale centered at zero. Cells are alphas in %/month. CAPM (left) shows a strong growth→value gradient and a large negative small-growth corner; FF3 (right) washes most cells toward zero but the small-growth corner remains blue.](attachments/fig1_alpha_grids.png)

CAPM mis-prices the value sort systematically: its alphas climb growth→value in every size row, because the market factor cannot explain the value premium, and the small-growth corner sits at a large negative $-0.53$ %/month. The three-factor panel washes most cells toward zero — the SMB and HML loadings absorb the size and value gradients — but the small-growth corner stays deep blue. That corner, `SMALL LoBM`, keeps an alpha of $-0.47$ %/month at $t=-5.1$: a large, precisely-estimated pricing error that no rotation of the three factors removes. A few other cells remain significant in the same way (big-growth $+0.17$ at $t=4.1$, `ME5 BM4` $-0.22$ at $t=-3.8$), and together they keep the model rejected. The grids with their full $t$-statistics and the SMB/HML loadings that drive the gradients are in [02-analysis](../02-analysis/task.md).

<!-- intent: figure 2 — realized vs predicted, the pricing-error-off-the-line view. -->
### Realized versus predicted returns

The same story reads off the cross-section of mean returns.

![Realized vs. predicted mean excess return (%/mo) for the 25 portfolios under CAPM (left) and FF3 (right), with a 45° perfect-pricing line. Points are tightly clustered on the diagonal under FF3 and scattered under CAPM; the small-growth portfolio is annotated and lies far below the line in both.](attachments/fig2_realized_vs_predicted.png)

Each point is one portfolio; the horizontal axis is the model's predicted mean excess return $\hat\beta_i'\bar f$ and the vertical axis the realized mean, so distance off the 45° line is the pricing error. Under CAPM the cloud is scattered and tilted off the diagonal. Under the three-factor model the points pull onto the line — the cross-section is largely priced — with the annotated small-growth portfolio the conspicuous exception, sitting far below the line in both panels. The picture matches the GRS numbers: the typical pricing error shrinks, but a few large outliers survive.

<!-- intent: economic conclusion — what FF3 explains, where it fails, what that implies. -->
### What this means

Adding SMB and HML to the market factor explains most of the size-value cross-section. The value gradient that CAPM cannot touch flattens, the typical alpha shrinks by half, and the realized returns line up with their predictions across the bulk of the 25 portfolios — the three factors do the work they were built to do. The remaining failure is narrow and specific. It is not a diffuse, model-wide mis-pricing but a small set of corners, led by small-growth, where a large alpha is estimated precisely enough to drive a joint test into rejection. Because the GRS test weights alphas by their precision, these few sharp errors outweigh the broad improvement, and the model is rejected even though its average pricing error is small.

The economic reading is the standard one. The three-factor model is a good description of the size-value cross-section but not an exact one: it leaves a robust small-growth anomaly that later models address with additional factors (notably profitability and investment). For the purpose of this showcase, the result is the textbook answer recovered end-to-end on public data — both models rejected, the three-factor model markedly closer, and the failure isolated to the corner the literature has long flagged.
