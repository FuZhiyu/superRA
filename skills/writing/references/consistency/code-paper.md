# Consistency: Code–Paper Alignment

> Load when Review or Polish mode targets a paper that wraps an empirical code project — methodology described in the paper must match the code that produced the results. One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks. A main-specification mismatch or variable-definition drift is blocking; a secondary-spec difference is usually advisory.

## Scope

Covers **consistency between paper description and code implementation**: Table 3's regression matches `reg y x controls, cluster(firmid)` in `Code/03_main.do`; §2's sample matches the filters in `Code/01_clean.py`; variable definitions in the text match what the code constructs. Out of scope: code correctness (analysis review), whether the methodology is *appropriate* (`consistency/argument-logic.md` or a researcher call).

Loads only when the paper wraps an empirical code project — not for theory papers, simulation papers without empirical results, or literature reviews.

Code-paper inconsistencies come in four patterns:

1. **Specification drift.** Paper says controls A, B, C; code runs A, B, C, D.
2. **Sample drift.** Paper says "firms with ≥5 years of data, 1990–2020"; code uses ≥3 years, 1990–2019.
3. **Variable-definition drift.** Paper says "log growth", code uses Davis-Haltiwanger growth; paper says "winsorized at 1/99", code uses 5/95.
4. **Results not reproducible from code.** The code's numbers differ from the paper's — usually undocumented post-processing.

## How-To

### Map paper tables / figures → code

Assemble the mapping before auditing: per table, figure, and in-text summary statistic, which code file and which output file produce it. A missing mapping (no file comments, no README, no pipeline file) is itself blocking — the paper is not reproducibly linked to its code.

### Methodology match

Per key regression or analysis:

- **Specification form.** The paper's equation (`y = \alpha + \beta x + X'\gamma + \epsilon`) matches the code's regression call.
- **Controls.** Every control in the text is in the code, and vice versa (or justified as nuisance / fixed effect).
- **Fixed effects.** Firm FE, year FE, firm-year FE — stated in paper, present in code.
- **Sample.** Filters, exclusions, time range as stated.
- **Standard errors.** Clustering level stated, matching the code call.
- **Weights.** Defined in both places, matching.

### Variable definitions

Per key variable:

- **Construction.** The paper's verbal / mathematical description matches what the code computes.
- **Log / level / growth / share.** Explicitly named; matches.
- **Winsorization / trimming.** Threshold and side stated; matches.
- **Missing-value handling.** Drop vs impute vs zero-fill — stated; matches.

**Red flags for silent drift:**

- Paper "we winsorize at 1%", code 2.5%.
- Paper "log return", code arithmetic return.
- Paper "excluding financial firms", code excluding by 2-digit SIC (which sweeps in some non-financials and misses some quasi-financials).

### Sample construction

Walk the code's data prep from raw inputs to the regression sample, comparing each filter against the paper's description side by side.

Sample-size match:

- Paper `N = 12,345` vs code `N = 12,347`: investigate — off-by-two is usually a filter ambiguity or a cutoff tie.
- A large difference means the paper or the code is out of date.

### Results reproducibility

- Run the code from committed state; confirm the paper's headline numbers within rounding.
- Running the code out of scope: at minimum compare committed output files to paper values.
- Flag any headline number that does not reproduce.

### Version / freshness

- Code date vs paper date — does the paper describe an older or newer version of the code?
- Any "draft" comments in code suggesting work in progress?

## Gated Checklist

- `[BLOCKING]` **Table → code mapping assembled** for the edited / reviewed sections.
- `[BLOCKING]` **Main specification matches** — regression form, controls, fixed effects, SE clustering, sample, weights.
- `[BLOCKING]` **Variable definitions match** for every key variable (dependent, main independent, key controls).
- `[BLOCKING]` **Sample construction filters match** — same filters, same order, in paper and code.
- `[BLOCKING]` **Sample size matches** within small rounding / tie-break differences; larger mismatches flagged.
- `[BLOCKING]` **Headline numbers reproduce from code**, or committed output files match paper values when the code is not run.
- `[BLOCKING]` **Discrepancies reported, not silently fixed** — the researcher decides whether paper or code is authoritative.
- `[ADVISORY]` **Secondary specifications** (robustness tables) also match.
- `[ADVISORY]` **Code and paper version-dates** compared; large gaps flagged.
- `[ADVISORY]` **Undocumented code filters flagged** — in the code, unmentioned in the paper.

## Output format

```
[SEVERITY] Code-Paper: <one-line title>
Paper location: §N.M / Table K / eq. (L)
Code location: [file.ext:40-50](file.ext#L40-L50)
Paper description: "<quoted from paper>"
Code implementation: <short summary>
Discrepancy: <one-line>
Impact: <affects main result / affects robustness / affects presentation only>
Resolution: <likely paper out of date / likely code out of date / researcher call>
Recommendation: <specific — which to update, and how to verify>
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
