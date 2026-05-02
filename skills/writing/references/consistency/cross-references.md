# Consistency: Cross-References

> Load when Review or Polish mode targets **cross-references** — `\ref`, `\eqref`, `\cite`, `\label`, figure/table/section numbering, "see above" and "as shown below". One of eight `consistency/*.md` dimensions. Severity markers shape reviewer output: `[BLOCKING]` items must be reported; `[ADVISORY]` items are flaggable as MINOR.

Source dimensions harvested from `draft-reviewer:consistency-checker` (cross-reference section) and `draft-reviewer:proofreader` (LaTeX-specific issues).

## Scope

Covers the **pointers** inside a document that direct the reader to another location in the same document: labeled references (`\ref`, `\eqref`, `\autoref`, `\cref`), bibliographic citation keys (`\cite` — the *mechanical* resolution only; completeness / format is `consistency/citations.md`), phrasal references ("see above", "as shown below", "in §3.2"). Out of scope: citation bibliography completeness (`consistency/citations.md`), numbers in text matching tables (`consistency/numerical.md`).

Cross-reference fails in five patterns:

1. **Unresolved reference.** `\ref{fig:main}` renders as `??` because the label does not exist or was renamed.
2. **Wrong reference.** `As shown in Table 3` but the referenced object is actually Table 2.
3. **Phantom reference.** `See above` when the content is actually below, or in a different section.
4. **Orphan label.** `\label{fig:old-version}` defined but never cited — often a leftover from a deleted figure.
5. **Numbering inconsistency.** Figure / table numbers in captions do not match their numbers in the text ("Figure 4" in caption but "Figure 5" in the prose).

## How-To

### Mechanical scan

Most unresolved references can be caught by the build system:

- **LaTeX:** compile and scan the `.log` for `undefined references` and the output for `??`. Every `??` is a broken `\ref` or `\cite`. Many `latexmk` passes needed — ensure the document is fully resolved before reporting.
- **Quarto / Markdown:** `quarto render` logs unresolved `@ref(fig:main)` style references; scan output for `Pandoc` warnings about unresolved references.
- **Pandoc with `pandoc-crossref`:** unresolved references render as the raw key surrounded by brackets.

### Wrong-reference scan

Mechanical checks don't catch "Table 3 says X" when the author meant "Table 2 says X". Read each cited claim against the referenced object:

- For every `\ref{tab:...}` / `\ref{fig:...}` in text, open the referenced table / figure and confirm the prose description is accurate. Magnitude, sign, significance, sample size.
- For every `As shown in §N`, confirm the referenced section does show it — often §N was rewritten and the reference was not updated.
- For every `see above` / `see below` / `discussed earlier`, verify the target is actually above / below / earlier relative to the reference.

### Phantom-reference scan

Phrases that smell like references but don't point anywhere specific:

- "As noted above" — noted where?
- "As we discussed earlier" — in which section?
- "Recent literature has shown" — flag for `consistency/citations.md` (missing citation).

These read as fine to the writer (who remembers the context) and as confusing to the reader. Flag and recommend anchoring (add an explicit `§N.M` reference or add a citation).

### Orphan-label detection

`grep -r '\\label{' ` → collect all labels. `grep -r '\\ref\|\\eqref\|\\autoref\|\\cref\|\\Cref'` → collect all references. Labels in the first set but not the second are orphans. Orphans are often harmless leftovers but occasionally indicate content that was removed from the text but not the figure/table list.

### Numbering cross-check

In LaTeX this is usually automatic, but check:

- Tables inserted out of order can renumber unexpectedly if `\input{}` / `\include{}` ordering changes.
- Manually numbered figures (bad practice but common) can drift.
- Cross-references to appendix items (`Table A1`, `Table B.2`) can break if appendix naming changes.

Sample-check a handful of figures and tables: does `grep` for `Table N` in the text return a sensible set of occurrences?

## Gated Checklist

- `[BLOCKING]` **No unresolved references** in the built document (no `??`, no raw reference keys).
- `[BLOCKING]` **Wrong-reference check performed** on every `\ref{tab:...}` / `\ref{fig:...}` appearing in the edited sections — each reference's prose description matches the referenced object.
- `[BLOCKING]` **No new cross-reference breaks introduced by the edit.** Compare the set of resolved refs before vs after; nothing new broke.
- `[BLOCKING]` **Phantom references flagged** ("as noted above", "we discussed earlier" without specific anchor). Either anchored or reported.
- `[ADVISORY]` **Orphan labels reported** (labels defined but never cited).
- `[ADVISORY]` **Numbering spot-checked** — sample of 3 figures / tables chosen at random, numbers in text match numbers in captions.
- `[ADVISORY]` **Build log free of `undefined references` warnings** (or remaining warnings triaged with explanation).

## Output format

```
[SEVERITY] Cross-Reference: <one-line title>
Reference: `\ref{tab:main}` at file.tex:<line>
Issue: <undefined / wrong-target / phantom / orphan-label / numbering-mismatch>
Details:
  - Label `tab:main` defined at: <location or "not found">
  - Referenced target's actual content: <summary>
  - Prose claim at citing location: "<quoted>"
Recommendation: <specific fix>
```
