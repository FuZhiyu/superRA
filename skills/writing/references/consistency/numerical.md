# Consistency: Numerical (numbers, figures, tables)

> Load when a task involves checking **quantitative content** — numbers in text matching numbers in tables, figure/caption/text alignment, table caption accuracy, units and sign conventions. One of eight `consistency/*.md` dimensions. Severity: `[BLOCKING]` must fix to earn APPROVE; `[ADVISORY]` flaggable as MINOR.

Source dimensions harvested from `draft-reviewer:consistency-checker` (numerical consistency, table/figure verification) plus the folded figure/table/caption dimension (per user decision 2026-04-19 — no separate `figure-table-checklist.md`).

## Scope

Covers **quantitative correctness** of reported numbers across text, tables, and figures. Out of scope: argument logic or whether the number supports the claim (`consistency/argument-logic.md`), notation (`consistency/notation.md`).

Numerical failures come in six patterns:

1. **Text number ≠ table number.** "The effect is 0.05" in §4 but Table 3 shows 0.047 (or 5.0%).
2. **Inconsistent rounding.** Same number 0.0523 in text as 0.05 in one place, 0.052 in another.
3. **Cross-table disagreement.** Sample size 1,247 in Table 1 but 1,243 in Table 3 without explanation.
4. **Figure–caption–text misalignment.** The caption describes what the text said the figure shows; the figure itself shows something else.
5. **Unit / scale errors.** Percentage vs decimal (5% vs 0.05); percentage-points vs percent (a 2pp increase on a 10% base is a 20% increase, not a 2% increase); basis points vs percentage; dollars vs millions.
6. **Sign / direction.** "The effect doubled" when it actually grew 80%; "increased" when the number went down.

## How-To

### Every number traces to a source

For every quantitative claim in prose:

- **Source identified.** Table / figure / explicit calculation / cited paper. If none of these, the number is floating and either needs a source or should be removed.
- **Value matches source exactly** (within stated rounding).
- **Units and scale match.**

Build a small table while auditing: `text_claim | text_value | source_location | source_value | match?`.

### Rounding discipline

Pick a rounding convention (e.g., 3 decimal places for coefficients, 2 for percentages) and apply consistently:

- The same number should not appear as 0.05, 0.052, and 0.0523 in three different places unless the context demands different precision.
- "5.2%" in text and "0.0523" in the table is fine if the text rounds to one decimal place consistently.

### Cross-table sample size

- Same specification across tables → same N.
- Different specifications (adding a control that drops observations; balanced panel subset) → different N is fine but should be explained in the notes or text.

### Figure–caption–text triangle

For each figure:

- **Caption says X.** What is X?
- **Figure shows Y.** Read the axes, legend, and visual content.
- **Text claims Z.** What does the prose say the figure demonstrates?
- Check X = Y = Z. Flag every mismatch.

Common failures:

- Caption describes pre-revision version of figure; figure has been updated.
- Text claim ("the effect is monotonic in X") does not match figure shape.
- Legend entries do not match the lines actually plotted (order swapped, colors mismapped).

### Table caption accuracy

For each table, caption should match:

- Which variable is in rows vs columns.
- What the cell values represent (coefficients? t-stats? standard errors?).
- What significance stars mean (if any).
- Sample definition and time period.

### Sign / direction / magnitude claims

- "The effect is positive / negative / zero" — sign of coefficient matches.
- "The effect is large / small / substantial" — loosely true given context (compare to SD of outcome, to published effects, to the other coefficients in the table).
- "The effect doubled" / "grew by X%" — verify the arithmetic.
- "Larger than" / "smaller than" comparisons — verify the ordering in the actual numbers.

### Percentage-point vs percent — common silent bug

- "The treatment group's share grew by 2 percentage points (pp), from 10% to 12%."
- NOT: "The treatment group's share grew by 2%, from 10% to 12%." (2% of 10% is 0.2pp, not 2pp.)

Always distinguish `pp` and `%`.

### ± sign, CI, and standard errors

- "Effect of 0.05 ± 0.01" ambiguous — is that one standard error, a 95% CI half-width, or a range? Disambiguate in caption or note.
- Parentheses convention for SEs vs brackets for CIs — stable across tables.

## Gated Checklist

- `[BLOCKING]` **Every number in edited prose traces to a source** (table, figure, calculation, or citation).
- `[BLOCKING]` **Text numbers match table numbers** at the stated precision; mismatches reported.
- `[BLOCKING]` **Cross-table sample-size discrepancies explained or flagged.**
- `[BLOCKING]` **Figure–caption–text alignment verified** — for each figure touched or referenced, caption describes what figure shows, text claims what figure supports.
- `[BLOCKING]` **Table caption accuracy verified** — rows/columns, cell meaning, significance stars, sample.
- `[BLOCKING]` **Unit / scale consistency** — percent vs decimal, pp vs %, units named on every headline number.
- `[BLOCKING]` **Sign / direction claims match the numbers.**
- `[BLOCKING]` **Magnitude claims ("doubled", "grew by X%") verified arithmetically.**
- `[ADVISORY]` **Rounding convention stated (or inferrable) and applied consistently.**
- `[ADVISORY]` **SE / CI notation convention stable across tables** (parens for SEs, brackets for CIs, or equivalent).

## Reviewer verdict protocol

Walk top to bottom, never halt, return APPROVE / REVISE.

## Output format

```
[SEVERITY] Numerical: <one-line title>
Claim: "<quoted prose>" at file.tex:<line>
Source: <Table/Figure/equation reference>
Expected: <value from source>
Observed: <value in prose>
Issue: <one-line>
Recommendation: <specific fix>
```
