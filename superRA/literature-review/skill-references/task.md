---
title: "Skill References — Discipline, Econ Corpus, Grounding, Synthesis"
status: approved
depends_on: [skill-core]
---

## Objective

Author the stage/domain references under `skills/literature-review/references/`, each with a clear load condition from `SKILL.md`, each teaching the **principle + a line-by-line identification protocol** (not just a checklist), each standalone-usable:

1. **Search & screening + convergence.** Wohlin backward + forward snowballing to saturation; the two-phase method (backward citation BFS from seeds + forward multi-lens web sweep, each lens blind); screen-first (metadata/abstract/intro, no OCR); the dedup cascade; the stopping/convergence judgment and how to record deliberate non-expansions.
2. **Econ/finance corpus discipline.** Working-paper-first coverage (SSRN / NBER / RePEc); published-version-of-record metadata with the WP-divergence flag; JEL codes as a scope/audit facet; weighting by outlet tier (Top-5 econ / Top-3 finance) + identification strategy (RCT/DiD/IV/RD/structural), not crawlability or raw citation count.
3. **Anti-hallucination grounding + extraction.** Resolve every DOI before trusting a cite; one-question-per-column **concept matrix**, every cell quote-grounded, honest null vs "not reported"; extract-then-verify.
4. **Synthesis & classification.** Concept-centric not author-centric; thematic / methodological / chronological organization; **matrix-sparsity gap detection** (empty cells = the gap); and the optional classification-axis pass (like the model-structure classification in the manual run).

### Validation criteria
- Every reference has a stated load condition from `SKILL.md` and works when read directly by a researcher.
- Each teaches principle + identification protocol.
- Shipped prose is self-contained — no citations to repo-internal contributor docs (`CLAUDE.md`/`AGENTS.md`), no AI-flavored prose, no cross-skill pattern citations.

## Planner Guidance

Keep references one level deep. Prefer positive instructions ("ground every cell in a quote" over "don't leave cells ungrounded"). Load `skill-creator` and `writing`. The four references map to the four analytic stages; do not merge them into one wall — each is loaded at a different point in the workflow.

## Results

Authored the four references under [`skills/literature-review/references/`](../../../skills/literature-review/references/), one per analytic stage, at the exact filenames and load conditions the approved [SKILL.md References table](../../../skills/literature-review/SKILL.md) fixes (rows 19–22). Each opens with its load condition verbatim from that table, states a **principle**, teaches the mechanism, and closes with a **line-by-line identification protocol** — a "walk the ledger/matrix and flag these tells" section, not a bare checklist.

| Reference | Load condition | Principle | Identification protocol (tells) |
|---|---|---|---|
| [search-and-screening.md](../../../skills/literature-review/references/search-and-screening.md) | running discovery | discovery snowballs, it does not query once | provenance missing; seed-only depth; single-lens forward; excluded-without-a-gate; over-read screen; no stopping judgment |
| [econ-corpus.md](../../../skills/literature-review/references/econ-corpus.md) | judging coverage and quality | the econ corpus is not the published corpus | under-coverage (no WPs); missing divergence flag; citation-count justification; unstated identification |
| [grounding-and-extraction.md](../../../skills/literature-review/references/grounding-and-extraction.md) | extracting from a paper | extraction is adversarial against your own confabulation | ungrounded cell; quote-does-not-support-claim; "no effect" with no test shown; DOI resolves to another title |
| [synthesis-and-classification.md](../../../skills/literature-review/references/synthesis-and-classification.md) | organizing the collection | organize by ideas, not by authors | author-centric drift; true vs extraction vs scope gap; unclassified paper; bloated "other"; non-partitioning axis |

**Coverage of the four objective items.** (1) Wohlin two-phase snowball (backward citation BFS + forward multi-lens blind web sweep), screen-first triage, the DOI→title+year→fuzzy dedup cascade, and the saturation/convergence judgment with deliberate non-expansions. (2) Working-paper-first sourcing (SSRN/NBER/RePEc), published-version-of-record metadata + the WP-divergence flag, JEL codes as a facet-not-gate, and weighting by outlet tier (Top-5 econ / Top-3 finance) + identification strategy (RCT/DiD/IV/RD/structural) over citation count/crawlability. (3) Resolve-DOI-before-trust (guarding against real-but-unrelated DOIs), the one-question-per-column quote-grounded concept matrix, extract-then-verify, and honest `null` vs `n/r`. (4) Concept-centric (read-down-columns) organization on thematic/methodological/chronological axes, matrix-sparsity gap detection distinguishing true/extraction/scope gaps, and the optional classification-axis pass.

**Validation criteria met.**
- Each reference states its load condition (matching SKILL.md) and reads standalone — a researcher can load any one directly. Cross-references between siblings and to the composed skills (`zotero-paper-reader`, `mistral-pdf-to-markdown`) and the `citation_client` subcommands are one level deep, mirroring the existing [citation-client.md](../../../skills/literature-review/references/citation-client.md).
- Each teaches principle + identification protocol (table above).
- Prose is self-contained: no `CLAUDE.md`/`AGENTS.md` or other repo-internal citations, no cross-skill pattern citations (only routing-by-name, as SKILL.md does), no AI-flavored prose. The only external attribution is Wohlin's snowballing method, stated self-containedly.

All four pass the `report-in-markdown` renderer check (`clean`). No new filenames or load conditions were invented; the contract is the one skill-core already shipped.
