# Consistency: Notation

> Load when Review or Polish mode targets **mathematical notation** — symbols, subscripts, superscripts, typographic conventions. One of eight `consistency/*.md` dimensions; multi-dimensional sweeps dispatch one reviewer per file in parallel. Severity markers shape reviewer output: `[BLOCKING]` items must be reported; `[ADVISORY]` items are flaggable as MINOR.

Source dimensions harvested from `draft-reviewer:mathematical-reviewer` (notation consistency section) and LRS / Chaubey conventions on symbol discipline.

## Scope

Covers **typographic and symbolic consistency** of math notation. Out of scope: derivation correctness (`consistency/math.md`), named terms in prose (`consistency/terminology.md`), equation labels and cross-refs (`consistency/cross-references.md`).

Notation fails in four patterns:

1. **Same symbol, different meanings.** `\beta` is the treatment coefficient in §3 and the discount rate in §5 — reader cannot tell in §6.
2. **Different symbols, same meaning.** The same object is `\epsilon_{it}` in the body and `u_{it}` in the appendix — reader has to infer these are the error term.
3. **Typographic drift.** Bold/italic/hat conventions applied inconsistently — vector `\mathbf{x}` becomes `x` becomes `\vec{x}`.
4. **Subscript / superscript reuse conflict.** `i` indexes firms in one section and time periods in another; `*` means "optimal" here and "significant" elsewhere.

## How-To

### Build a notation index

For each symbol the paper defines or uses carrying real meaning:

- **First use.** Section, page, equation number.
- **Definition.** Full verbal reading ("the coefficient on the treatment indicator", "the vector of firm-level controls", "the idiosyncratic error term").
- **Type / dimension.** Scalar / vector / matrix; dimensions (`\mathbf{X}` is `N × K`).
- **Typographic convention.** Bold, italic, hat, tilde, asterisk.

Flag every symbol that fails the stability test below.

### Four-pattern audit

**Same symbol, different meanings.** `grep` each key symbol across the paper; if meaning changes between occurrences, report.

**Different symbols, same meaning.** For each defined object, scan the rest of the paper (especially appendices — common drift site) for alternate symbols. Report.

**Typographic drift.** Verify:

- Vectors consistently bold (`\mathbf{}` or `\bm{}`) or consistently arrow (`\vec{}`); not mixed.
- Matrices consistently capital bold or capital italic; stable.
- Estimated / hatted quantities always `\hat{}`; never dropped.
- Stars: `*` consistently means one thing (usually "optimal" in theory, significance in empirical tables; pick and signal).
- Tildes: `\tilde{}` used for one role only (often deviations from mean, or alternative estimators).

**Subscript / superscript reuse conflict.** For each index letter (`i`, `j`, `t`, `s`, `k`, `l`, `n`), confirm it indexes one and only one thing across the whole paper. `i` for firms in the body and `i` for countries in the appendix is a drift. Greek letters for parameters should not collide with other Greek letters playing a different role.

### Greek-letter-conflict scan

`\alpha`, `\beta`, `\gamma`, `\delta`, `\epsilon`, `\theta`, `\lambda`, `\mu`, `\sigma`, `\rho`, `\phi`, `\pi` are the common culprits. Each should play one role in the paper. Reusing `\sigma` as "standard deviation" and "a cross-sectional moment" requires at a minimum a typographic differentiation (`\sigma_y` vs `\sigma^2`).

### Abbreviations in notation

`SD`, `SE`, `LHS`, `RHS`, `DGP`, `iid`, `w.r.t.` — each defined on first use (or so standard for the audience that definition is unnecessary). Consistent capitalization and spacing.

## Gated Checklist

- `[BLOCKING]` **Same-symbol-different-meaning conflicts flagged** (both uses cited).
- `[BLOCKING]` **Different-symbols-same-meaning drift flagged** (all variants cited).
- `[BLOCKING]` **Subscript reuse conflicts flagged** (every index letter playing multiple roles is reported).
- `[BLOCKING]` **Greek-letter conflicts flagged.**
- `[BLOCKING]` **No silent rewrites beyond scope.** For consistency-*check* tasks, report rather than fix.
- `[ADVISORY]` **Typographic conventions consistent** — bold / italic / hat / tilde / asterisk each stable across the paper.
- `[ADVISORY]` **Notation index attached to handoff** (short one — symbol, definition, dimensions, convention).
- `[ADVISORY]` **Abbreviations defined on first use** unless convention-standard for the audience.
- `[ADVISORY]` **Code / variable names in text match variable names in equations** (soft consistency with `consistency/terminology.md`).

## Output format

```
[SEVERITY] Notation: <one-line title>
Symbol: `\beta`
Meanings observed:
  - eq. (3) / §3.1 p. 12: "treatment coefficient"
  - eq. (15) / §5.2 p. 22: "discount rate"
Issue: same symbol, two meanings
Recommendation: rename one (e.g., \delta for discount rate per convention) or escalate
Auto-fixable: Yes / No
```
