# Consistency: Citations

> Load when Review or Polish mode targets **citations** — completeness, reference-bibliography matching, format consistency, citation quality. One of eight `consistency/*.md` dimensions. Severity markers shape reviewer output: `[BLOCKING]` items must be reported; `[ADVISORY]` items are flaggable as MINOR.

Source dimensions harvested from `draft-reviewer:citation-checker` (completeness, orphan-citation scan, format consistency, quality).

## Scope

Covers **citation-level correctness**: every non-common-knowledge claim supported by a citation; every in-text citation matched to a bibliography entry; bibliography format consistent; no orphan references. Out of scope: argument-logic validity (`consistency/argument-logic.md` — whether the cited work *actually supports* the claim is a logic question); cross-reference rendering mechanics (`consistency/cross-references.md`).

Citations fail in six patterns:

1. **Uncited claim.** A fact or prior result asserted without a citation.
2. **Orphan citation.** `\cite{smith2020}` in text but no `smith2020` entry in the bibliography.
3. **Orphan reference.** Bibliography entry never cited — often a leftover from deleted content.
4. **Format inconsistency.** Different citation styles, "et al." thresholds, or bibliographic formats used inconsistently.
5. **Outdated working paper.** Cited as "NBER WP 12345" when it was published three years ago.
6. **Author-year mismatch.** `Smith (2020)` in text but bibliography says 2019.

## How-To

### Completeness audit

Scan the paper for claim sentences that need citations:

- **Factual statements not original to this paper** ("GDP grew 2.3% in 2022", "the treatment-on-the-treated effect of X is known to be biased under Y").
- **"It is well known that…"** constructions — these almost always need a citation. If it is well-known, name the source.
- **Methodology borrowed from another paper** — always cite the origin.
- **Data sources** — every dataset gets a citation or footnote (CRSP / Compustat / WRDS / FRED / etc.).
- **Theoretical frameworks used** — Hansen-Sargent, Sims, Campbell-Shiller, whatever.
- **Empirical findings used as motivation** — each one cites the paper that found it.

**Foundational references check.** For the paper's methodology, are the seminal papers cited? Diff-in-diff → Card-Krueger or similar; RDD → Hahn-Todd-van der Klaauw; GMM → Hansen. Missing foundational cites are `MAJOR`.

### Orphan-citation and orphan-reference scan

Mechanical:

- Collect all `\cite{...}` keys from the text.
- Collect all BibTeX keys from the `.bib` file (or the bibliography list).
- **Orphan citations:** keys cited but not in bibliography → `\cite{smith2020}` renders as `[?]` or similar.
- **Orphan references:** bibliography entries never cited → usually harmless but worth flagging.

Also check: if two entries share author/year (`smith2020a`, `smith2020b`), each is distinguished in text with the `a` / `b` disambiguator.

### Format-consistency audit

Pick one style and check every citation conforms:

- **In-text format.** `(Author, Year)` vs `Author (Year)` — parenthetical-only vs narrative citations. `&` vs `and` between two authors. "et al." threshold (usually 3+ authors after first reference).
- **Bibliography format.** Author names `First Last` vs `Last, First`. Journal names full vs abbreviated. Volume / issue / pages format stable. DOIs either always present or consistently absent. Italics for journal names.
- **Common style issues:** periods vs commas between bibliographic elements; title case vs sentence case for article titles; year placement (end vs after author).

Flag mixed-style citations — one `(Smith 2020)` and one `Smith, 2020` is sloppy even though both are legal.

### Author / year detail check

For each citation:

- Author name in text matches bibliography (typos, accented characters, Jr/Sr suffix).
- Year in text matches bibliography year.
- Page numbers given where direct quotes are used.
- Multiple works by same author same year distinguished with `a`, `b`, `c`.

### Currency / outdated-working-paper check

- Working papers cited as `NBER WP XXXX` that have since been published — check and update.
- Citations to 30+ year old papers where a more recent definitive version exists — flag for researcher.

### Self-citation

- Appropriate level (not dominating).
- Self-citations where building on own prior work are fine; ten self-citations in a 50-paper reference list raises a flag.

## Gated Checklist

- `[BLOCKING]` **No orphan citations.** Every `\cite{key}` in text resolves to a bibliography entry.
- `[BLOCKING]` **Orphan references reported.** Bibliography entries never cited are listed — flagged, not deleted (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Uncited claims flagged.** Every statement that needs a citation but lacks one is reported with location and text.
- `[BLOCKING]` **Foundational methodology references present** — the seminal papers for the paper's method are cited.
- `[BLOCKING]` **Author / year mismatches flagged.** Any text–bibliography discrepancy reported with both values.
- `[BLOCKING]` **Data-source citations present** for every dataset used.
- `[ADVISORY]` **Format consistency.** One in-text style; one bibliography style; "et al." threshold consistent; DOI handling consistent.
- `[ADVISORY]` **Currency.** Cited working papers still current (not superseded by published versions).
- `[ADVISORY]` **Self-citation proportion not flagged by the researcher as a concern.**

## Output format

```
[SEVERITY] Citation: <one-line title>
Type: <uncited-claim / orphan-citation / orphan-reference / format / author-year-mismatch>
Location: [file.tex:42](file.tex#L42)
Text: "<quoted claim>"
Bibliography entry: <entry or "NOT FOUND">
Issue: <one-line>
Recommendation: <suggest citation where known, or "researcher must supply">
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
