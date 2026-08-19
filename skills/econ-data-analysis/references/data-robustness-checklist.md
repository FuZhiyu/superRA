# Data Robustness Checklist

A reference for checking whether analytical results are sensitive to data construction choices. Consult this when the user asks to explore robustness or when you suspect a result may be fragile. This is **not** enforced during routine analysis — it is a menu of checks to draw from as needed.

## Alternative outlier treatment

- Re-run the analysis with **no** winsorization/trimming
- Compare results at different cutoffs: 1/99, 2.5/97.5, 5/95 percentiles
- Report how the main coefficient and its significance change across treatments
- If results are sensitive to outlier treatment, investigate which specific observations are driving the difference

## Alternative variable definitions

- **Functional form**: compare levels, logs, and ranks of the key variable
- **Denominators**: for ratio variables, try alternative scaling (e.g., GDP, total assets, population)
- **Lag structure**: vary the number of lags (e.g., 1-month vs 3-month vs 12-month)
- **Aggregation method**: if the variable is constructed from micro data, try alternative aggregation (value-weighted vs equal-weighted, mean vs median)

## Alternative sample restrictions

- **Time windows**: re-estimate excluding crisis periods, or splitting into early/late subsamples
- **Geographic subsets**: developed vs emerging, exclude specific outlier countries
- **Exclusion criteria**: vary the thresholds for dropping observations (e.g., minimum number of observations per unit, minimum coverage requirements)
- **Balanced vs unbalanced panel**: if using an unbalanced panel, check whether restricting to a balanced subsample changes results

## Sensitivity to individual observations

- **Leave-one-out**: re-estimate dropping each cross-sectional unit one at a time; flag any unit whose removal substantially changes the result
- **Influential observations**: compute leverage or Cook's distance; investigate high-influence points
- **Jackknife**: if the sample is small, report jackknife standard errors alongside baseline

## Alternative data sources

- When the same concept is measured by multiple providers (e.g., GDP from World Bank vs IMF vs Penn World Table), compare the constructed variable across sources
- If results hold across sources, this strengthens credibility
- If results differ, investigate which measurement differences drive the divergence
