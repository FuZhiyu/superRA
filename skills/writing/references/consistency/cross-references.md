# Consistency: Cross-References

> Load when Review or Polish mode targets **cross-references** — `\ref`, `\eqref`, `\cite`, `\label`, figure/table/section numbering, "see above" and "as shown below". One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks.

## Scope

Covers the **pointers** directing the reader to another location in the same document: labeled references (`\ref`, `\eqref`, `\autoref`, `\cref`), bibliographic citation keys (`\cite` — *mechanical* resolution only), phrasal references ("see above", "as shown below", "in §3.2"). Out of scope: citation completeness and format (`consistency/citations.md`), numbers in text matching tables (`consistency/numerical.md`).

Cross-reference fails in five patterns:

1. **Unresolved reference.** `\ref{fig:main}` renders as `??` — label missing or renamed.
2. **Wrong reference.** "As shown in Table 3" when the object is Table 2.
3. **Phantom reference.** "See above" when the content is below, or in a different section.
4. **Orphan label.** `\label{fig:old-version}` defined but never cited — often left from a deleted figure.
5. **Numbering inconsistency.** Caption numbers not matching the text ("Figure 4" in the caption, "Figure 5" in the prose).

## How-To

### Mechanical scan

The build system catches most unresolved references:

- **LaTeX:** compile, scan the `.log` for `undefined references` and the output for `??`. Every `??` is a broken `\ref` or `\cite`. Run enough `latexmk` passes to fully resolve the document before reporting.
- **Quarto / Markdown:** `quarto render` logs unresolved `@ref(fig:main)` style references; scan output for `Pandoc` unresolved-reference warnings.
- **Pandoc with `pandoc-crossref`:** unresolved references render as the raw key in brackets.

### Wrong-reference scan

Mechanical checks miss "Table 3 says X" when the author meant Table 2. Read each cited claim against the referenced object:

- Every `\ref{tab:...}` / `\ref{fig:...}`: open the target and confirm the prose description — magnitude, sign, significance, sample size.
- Every "As shown in §N": confirm §N shows it — often §N was rewritten and the reference was not.
- Every "see above" / "see below" / "discussed earlier": confirm the target is above / below / earlier.

### Phantom-reference scan

Phrases that smell like references but point nowhere specific:

- "As noted above" — noted where?
- "As we discussed earlier" — in which section?
- "Recent literature has shown" — flag for `consistency/citations.md` (missing citation).

They read fine to the writer, who remembers the context, and confusing to the reader. Flag and recommend anchoring — an explicit `§N.M` reference or a citation.

### Orphan-label detection

`grep -r '\\label{' ` collects all labels; `grep -r '\\ref\|\\eqref\|\\autoref\|\\cref\|\\Cref'` collects all references. Labels in the first set but not the second are orphans — usually harmless leftovers, occasionally content removed from the text but not the figure/table list.

### Numbering cross-check

Usually automatic in LaTeX, but check:

- Tables inserted out of order renumber unexpectedly when `\input{}` / `\include{}` ordering changes.
- Manually numbered figures (bad practice, common) drift.
- References to appendix items (`Table A1`, `Table B.2`) break when appendix naming changes.

Sample-check a handful of figures and tables: does `grep` for `Table N` in the text return a sensible set of occurrences?

## Gated Checklist

- `[BLOCKING]` **No unresolved references** in the built document (no `??`, no raw reference keys).
- `[BLOCKING]` **Wrong-reference check performed** on every `\ref{tab:...}` / `\ref{fig:...}` in the edited sections — each prose description matches the referenced object.
- `[BLOCKING]` **No new cross-reference breaks introduced.** Resolved-ref set compared before vs after.
- `[BLOCKING]` **Phantom references flagged** ("as noted above", "we discussed earlier" without an anchor) — anchored or reported.
- `[ADVISORY]` **Orphan labels reported** (defined, never cited).
- `[ADVISORY]` **Numbering spot-checked** — 3 random figures / tables, text numbers matching captions.
- `[ADVISORY]` **Build log free of `undefined references` warnings**, or remaining ones triaged.

## Output format

```
[SEVERITY] Cross-Reference: <one-line title>
Reference: `\ref{tab:main}` at [file.tex:42](file.tex#L42)
Issue: <undefined / wrong-target / phantom / orphan-label / numbering-mismatch>
Details:
  - Label `tab:main` defined at: <location or "not found">
  - Referenced target's actual content: <summary>
  - Prose claim at citing location: "<quoted>"
Recommendation: <specific fix>
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
