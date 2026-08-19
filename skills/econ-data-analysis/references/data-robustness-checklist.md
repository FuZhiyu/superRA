# Data Robustness Checklist

A menu of checks for whether results are sensitive to data-construction choices. Draw from it when the researcher asks about robustness or a result looks fragile; **not** enforced during routine analysis.

## Alternative outlier treatment

- Re-run with **no** winsorization/trimming
- Compare cutoffs: 1/99, 2.5/97.5, 5/95 percentiles
- Report how the main coefficient and its significance move across treatments
- Sensitive to outlier treatment: find which observations drive the difference

## Alternative variable definitions

- **Functional form** — levels, logs, ranks of the key variable
- **Denominators** — alternative scaling for ratio variables (GDP, total assets, population)
- **Lag structure** — vary the lag count (1-month vs 3-month vs 12-month)
- **Aggregation method** — for micro-constructed variables: value-weighted vs equal-weighted, mean vs median

## Alternative sample restrictions

- **Time windows** — exclude crisis periods; split early/late subsamples
- **Geographic subsets** — developed vs emerging; exclude outlier countries
- **Exclusion criteria** — vary drop thresholds (minimum observations per unit, minimum coverage)
- **Balanced vs unbalanced panel** — restrict an unbalanced panel to its balanced subsample

## Sensitivity to individual observations

- **Leave-one-out** — drop each cross-sectional unit in turn; flag any whose removal substantially changes the result
- **Influential observations** — leverage or Cook's distance; investigate high-influence points
- **Jackknife** — small samples: report jackknife standard errors alongside baseline

## Alternative data sources

- Same concept from multiple providers (GDP from World Bank vs IMF vs Penn World Table): compare the constructed variable across sources
- Holding across sources strengthens credibility; differing results: find which measurement differences drive the divergence
