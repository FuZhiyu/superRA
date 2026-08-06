# Consistency: Numerical (numbers, figures, tables)

> Load when Review or Polish mode targets **quantitative content** — text numbers matching table numbers, figure/caption/text alignment, table caption accuracy, units and sign conventions. One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks.

## Scope

Covers **quantitative correctness** of reported numbers across text, tables, and figures. Out of scope: argument logic or whether the number supports the claim (`consistency/argument-logic.md`), notation (`consistency/notation.md`).

Numerical failures come in six patterns:

1. **Text number ≠ table number.** "The effect is 0.05" in §4, Table 3 shows 0.047 (or 5.0%).
2. **Inconsistent rounding.** 0.0523 rendered 0.05 in one place, 0.052 in another.
3. **Cross-table disagreement.** Sample size 1,247 in Table 1, 1,243 in Table 3, unexplained.
4. **Figure–caption–text misalignment.** The caption describes what the text says the figure shows; the figure shows something else.
5. **Unit / scale errors.** Percent vs decimal (5% vs 0.05); percentage points vs percent (2pp on a 10% base is a 20% increase, not 2%); basis points vs percent; dollars vs millions.
6. **Sign / direction.** "Doubled" for 80% growth; "increased" when the number fell.

## How-To

### Every number traces to a source

Per quantitative claim in prose:

- **Source identified.** Table / figure / explicit calculation / cited paper. None of these → the number is floating; source it or remove it.
- **Value matches source exactly** (within stated rounding).
- **Units and scale match.**

Build a small table while auditing: `text_claim | text_value | source_location | source_value | match?`.

### Rounding discipline

Pick a convention (e.g., 3 decimal places for coefficients, 2 for percentages) and apply it consistently:

- One number should not appear as 0.05, 0.052, and 0.0523 in three places unless the context demands different precision.
- "5.2%" in text and "0.0523" in the table is fine when the text rounds to one decimal place throughout.

### Cross-table sample size

- Same specification across tables → same N.
- Different specifications (a control that drops observations, a balanced-panel subset) → different N is fine, explained in the notes or text.

### Figure–caption–text triangle

Per figure:

- **Caption says X.**
- **Figure shows Y** — read the axes, legend, and visual content.
- **Text claims Z** — what the prose says the figure demonstrates.
- Check X = Y = Z. Flag every mismatch.

Common failures:

- Caption describes the pre-revision figure; the figure has been updated.
- Text claim ("the effect is monotonic in X") does not match the figure's shape.
- Legend entries do not match the plotted lines (order swapped, colors mismapped).

### Table caption accuracy

Per table, the caption matches:

- Which variable is in rows vs columns.
- What the cell values represent (coefficients? t-stats? standard errors?).
- What significance stars mean, if any.
- Sample definition and time period.

### Sign / direction / magnitude claims

- "Positive / negative / zero" — coefficient sign matches.
- "Large / small / substantial" — loosely true in context (against the outcome's SD, published effects, the table's other coefficients).
- "Doubled" / "grew by X%" — verify the arithmetic.
- "Larger than" / "smaller than" — verify the ordering in the actual numbers.

### Percentage-point vs percent — common silent bug

- "The treatment group's share grew by 2 percentage points (pp), from 10% to 12%."
- NOT: "…grew by 2%, from 10% to 12%." (2% of 10% is 0.2pp, not 2pp.)

Always distinguish `pp` and `%`.

### ± sign, CI, and standard errors

- "Effect of 0.05 ± 0.01" is ambiguous — one standard error, a 95% CI half-width, or a range? Disambiguate in the caption or note.
- Parentheses for SEs vs brackets for CIs — stable across tables.

## Gated Checklist

- `[BLOCKING]` **Every number in edited prose traces to a source** (table, figure, calculation, or citation).
- `[BLOCKING]` **Text numbers match table numbers** at the stated precision; mismatches reported.
- `[BLOCKING]` **Cross-table sample-size discrepancies explained or flagged.**
- `[BLOCKING]` **Figure–caption–text alignment verified** for every figure touched or referenced.
- `[BLOCKING]` **Table caption accuracy verified** — rows/columns, cell meaning, significance stars, sample.
- `[BLOCKING]` **Unit / scale consistency** — percent vs decimal, pp vs %, units named on every headline number.
- `[BLOCKING]` **Sign / direction claims match the numbers.**
- `[BLOCKING]` **Magnitude claims ("doubled", "grew by X%") verified arithmetically.**
- `[ADVISORY]` **Rounding convention stated (or inferrable) and applied consistently.**
- `[ADVISORY]` **SE / CI notation convention stable across tables** (parens for SEs, brackets for CIs, or equivalent).

## Output format

```
[SEVERITY] Numerical: <one-line title>
Claim: "<quoted prose>" at [file.tex:42](file.tex#L42)
Source: <Table/Figure/equation reference>
Expected: <value from source>
Observed: <value in prose>
Issue: <one-line>
Recommendation: <specific fix>
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
