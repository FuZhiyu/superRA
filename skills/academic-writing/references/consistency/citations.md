# Consistency: Citations

> Load when Review or Polish mode targets **citations** — completeness, reference-bibliography matching, format consistency, citation quality. One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks.

## Scope

Covers **citation-level correctness**: every non-common-knowledge claim supported by a citation; every in-text citation matched to a bibliography entry; consistent bibliography format; no orphan references. Out of scope: whether the cited work *actually supports* the claim (`consistency/argument-logic.md`), cross-reference rendering mechanics (`consistency/cross-references.md`).

Citations fail in six patterns:

1. **Uncited claim.** A fact or prior result asserted without a citation.
2. **Orphan citation.** `\cite{smith2020}` in text, no `smith2020` entry in the bibliography.
3. **Orphan reference.** Bibliography entry never cited — often left from deleted content.
4. **Format inconsistency.** Citation styles, "et al." thresholds, or bibliographic formats mixed.
5. **Outdated working paper.** Cited as "NBER WP 12345" three years after publication.
6. **Author-year mismatch.** `Smith (2020)` in text, 2019 in the bibliography.

## How-To

### Completeness audit

Claim sentences needing citations:

- **Factual statements not original to this paper** ("GDP grew 2.3% in 2022", "the treatment-on-the-treated effect of X is known to be biased under Y").
- **"It is well known that…"** constructions — if it is well known, name the source.
- **Methodology borrowed from another paper** — cite the origin.
- **Data sources** — every dataset gets a citation or footnote (CRSP / Compustat / WRDS / FRED / etc.).
- **Theoretical frameworks used** — Hansen-Sargent, Sims, Campbell-Shiller, whatever.
- **Empirical findings used as motivation** — each cites the paper that found it.

**Foundational references check.** Are the seminal papers for the methodology cited? Diff-in-diff → Card-Krueger or similar; RDD → Hahn-Todd-van der Klaauw; GMM → Hansen. Missing foundational cites are blocking.

### Orphan-citation and orphan-reference scan

Mechanical:

- Collect all `\cite{...}` keys from the text.
- Collect all BibTeX keys from the `.bib` file (or the bibliography list).
- **Orphan citations:** cited but absent from the bibliography → renders as `[?]` or similar.
- **Orphan references:** bibliography entries never cited → usually harmless, worth flagging.

Also: entries sharing author/year (`smith2020a`, `smith2020b`) carry the `a` / `b` disambiguator in text.

### Format-consistency audit

Pick one style; check every citation conforms:

- **In-text format.** `(Author, Year)` vs `Author (Year)` — parenthetical vs narrative. `&` vs `and` between two authors. "et al." threshold (usually 3+ authors after first reference).
- **Bibliography format.** Author names `First Last` vs `Last, First`. Journal names full vs abbreviated. Volume / issue / pages format stable. DOIs always present or consistently absent. Italics for journal names.
- **Common style issues:** periods vs commas between bibliographic elements; title vs sentence case for article titles; year placement (end vs after author).

Flag mixed-style citations — `(Smith 2020)` alongside `Smith, 2020` is sloppy even though both are legal.

### Author / year detail check

Per citation:

- Author name in text matches bibliography (typos, accented characters, Jr/Sr suffix).
- Year in text matches bibliography year.
- Page numbers given for direct quotes.
- Multiple works by the same author and year distinguished with `a`, `b`, `c`.

### Currency / outdated-working-paper check

- Working papers cited as `NBER WP XXXX` since published — check and update.
- Citations to 30+ year old papers with a more recent definitive version — flag for the researcher.

### Self-citation

Building on own prior work is fine; ten self-citations in a 50-paper reference list raises a flag.

## Gated Checklist

- `[BLOCKING]` **No orphan citations.** Every `\cite{key}` resolves to a bibliography entry.
- `[BLOCKING]` **Orphan references reported** — never-cited entries listed, flagged not deleted (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Uncited claims flagged** with location and text.
- `[BLOCKING]` **Foundational methodology references present** — the method's seminal papers cited.
- `[BLOCKING]` **Author / year mismatches flagged** with both values.
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
