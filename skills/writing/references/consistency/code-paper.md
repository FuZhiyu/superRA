# Consistency: Code–Paper Alignment

> Load when Review or Polish mode targets a paper that wraps an empirical code project — methodology described in the paper must match the code that produced the results. One of eight `consistency/*.md` dimensions. Severity markers shape reviewer output: `[BLOCKING]` items must be reported; `[ADVISORY]` items are flaggable as MINOR. Main-specification mismatches are `CRITICAL`; variable-definition drift is usually `MAJOR`; secondary-spec differences are typically `MINOR`.

Source dimensions harvested from `draft-reviewer:code-paper-consistency` (methodology match, variable definitions, sample construction, results reproducibility).

## Scope

Covers **consistency between paper description and code implementation**: the regression in Table 3 matches the `reg y x controls, cluster(firmid)` in `Code/03_main.do`; the sample in §2 matches the filters in `Code/01_clean.py`; variable definitions in the text match how the code constructs them. Out of scope: code correctness as such (that's analysis review); whether the methodology is *appropriate* (that's `consistency/argument-logic.md` or a researcher call).

This file loads only when the paper wraps an empirical code project. For theory papers, simulation papers without empirical results, or literature reviews, this file is not relevant.

Code-paper inconsistencies come in four patterns:

1. **Specification drift.** Paper says the regression uses controls A, B, C; code runs it with A, B, C, D.
2. **Sample drift.** Paper says "firms with ≥5 years of data, 1990–2020"; code uses "firms with ≥3 years of data, 1990–2019".
3. **Variable-definition drift.** Paper says "log growth"; code uses "Davis-Haltiwanger growth". Paper says "winsorized at 1/99"; code uses 5/95.
4. **Results not reproducible from code.** Running the code produces numbers different from the paper's — usually from undocumented post-processing.

## How-To

### Map paper tables / figures → code

Before auditing, assemble the mapping:

- For each table in the paper, which code file produces it? Which output file?
- For each figure, same.
- For each summary-statistic value in the text, same.

If the mapping is missing (no file comments, no README, no pipeline file), that is itself a `MAJOR` flag — the paper is not reproducibly linked to its code.

### Methodology match

For each key regression or analysis in the paper:

- **Specification form.** The paper's equation (`y = \alpha + \beta x + X'\gamma + \epsilon`) matches the code's regression call.
- **Controls.** Every control listed in the text is in the code; every control in the code is listed in the text (or justified as nuisance / fixed effect).
- **Fixed effects.** Firm FE, year FE, firm-year FE — stated in paper, present in code.
- **Sample.** Filters, exclusions, time range as stated.
- **Standard errors.** Clustering level stated, matches code call.
- **Weights.** If weighted, weights defined in both places and match.

### Variable definitions

For each key variable:

- **Construction.** The paper's verbal / mathematical description matches what the code computes.
- **Log / level / growth / share.** Explicitly named; matches.
- **Winsorization / trimming.** Threshold and side stated; matches.
- **Missing-value handling.** Drop vs impute vs zero-fill — stated; matches.

**Red flags for silent drift:**

- Paper says "we winsorize at 1%" but code uses 2.5%.
- Paper says "log return" but code uses arithmetic return.
- Paper says "excluding financial firms" but code excludes by 2-digit SIC (which includes some non-financials and excludes some quasi-financials).

### Sample construction

Walk the code's data-prep from raw inputs through to the regression sample. At each step, does the paper describe the filter? Compare filter list side by side.

Sample-size match:

- If paper reports `N = 12,345` and code gives `N = 12,347`, investigate (off-by-two is usually a filter ambiguity or a tie in a cutoff).
- If the difference is large, either the paper or the code is out of date.

### Results reproducibility

Where possible:

- Run the code from committed state; confirm it produces the paper's headline numbers within rounding.
- If running the code is out of scope for this review, at minimum compare committed output files to paper values.
- Flag any headline number that does not reproduce.

### Version / freshness

- Code date vs paper date — is the paper describing an older or newer version of the code?
- Any "draft" comments in code suggesting work in progress?

## Gated Checklist

- `[BLOCKING]` **Table → code mapping assembled** (at least for edited / reviewed sections). Missing mappings flagged as `MAJOR`.
- `[BLOCKING]` **Main specification matches** — regression form, controls, fixed effects, SE clustering, sample, weights.
- `[BLOCKING]` **Variable definitions match** for every key variable (dependent, main independent, key controls).
- `[BLOCKING]` **Sample construction filters match** — paper and code list the same filters in the same order.
- `[BLOCKING]` **Sample size matches** (within small rounding / tie-break differences, any larger mismatch flagged).
- `[BLOCKING]` **Headline numbers reproduce from code** (or if code not run, committed output files match paper values).
- `[BLOCKING]` **Discrepancies reported, not silently fixed.** For consistency-*check* tasks, the reviewer reports; the researcher decides whether the paper or the code is the authoritative version.
- `[ADVISORY]` **Secondary specifications** (robustness tables) also match.
- `[ADVISORY]` **Code and paper version-dates** compared; flag any large gap.
- `[ADVISORY]` **Undocumented code filters flagged** — a filter in the code that is not mentioned in the paper.

## Output format

```
[SEVERITY] Code-Paper: <one-line title>
Paper location: §N.M / Table K / eq. (L)
Code location: file.ext:<line range>
Paper description: "<quoted from paper>"
Code implementation: <short summary>
Discrepancy: <one-line>
Impact: <affects main result / affects robustness / affects presentation only>
Resolution: <likely paper out of date / likely code out of date / researcher call>
Recommendation: <specific — which to update, and how to verify>
Auto-fixable: Yes / No
```
