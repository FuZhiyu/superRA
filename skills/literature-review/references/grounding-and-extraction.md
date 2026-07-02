# Anti-Hallucination Grounding & Extraction

Load when extracting from a paper: DOI resolution before trusting a cite, the quote-grounded concept matrix, and honest null vs "not reported".

Treat every bibliographic claim and extracted finding as **guilty until grounded**: do not trust a cite until its DOI resolves to the paper you mean, do not record a finding until a verbatim quote from the source supports it, and do not write "no effect" until the paper is shown to have tested for one.

## Resolve every DOI before trusting a cite

A resolving DOI is not enough — a fabricated cite often carries a real but unrelated DOI. Before trusting any cite, resolve its identifier (`citation_client metadata IDENTIFIER`) and check that the returned **title, first author, and year match the paper you intend to cite**. A DOI that resolves to a different title is a mismatched or fabricated cite: drop it, or correct it to the DOI that actually points to the paper.

Apply this to cites you surface from a paper's reference list too — the `unstructured` Crossref-array references are frequently DOI-less or mis-keyed. Resolve before adding to the frontier.

## The quote-grounded concept matrix

Extract into a **concept matrix**: one row per paper, **one question per column**. The columns are the extraction schema settled in setup (e.g. "what friction drives the result?", "identification strategy", "sign of the main effect", "sample and period"). One question per column forces the same question of every paper, which makes the papers comparable.

**Every cell is a claim plus the verbatim quote that grounds it, with its location** (section or page). A cell is not filled from memory of the abstract or from inference — it is filled from a quote you can point to in the source. Screening reads the abstract and intro; extraction of a central paper reads the OCR'd full text (the `mistral-pdf-to-markdown` shortlist), because the answer to a schema question usually lives in the results or the model section, not the abstract.

**Extract, then verify** — two passes:

1. **Extract** — read the paper and fill the cell with the claim and the quote you believe supports it.
2. **Verify** — confirm the quote appears verbatim in the source, and read the quote against the claim to confirm it actually supports it, not merely sits near it. A quote adjacent to the claim but not stating it is paraphrase drift — reject it.

## Honest null vs "not reported"

Encode a **true null** — the paper tested for an effect and found none — differently from a **silence** — the paper does not address the question (e.g. `null` vs `n/r`). Reporting "no effect" for a paper that never ran the test invents a result the authors never claimed.

**Identification protocol:** walk the matrix cell by cell and flag these tells:

- **Ungrounded cell.** A claim with no quote — it was filled from inference or memory. Every cell carries its supporting quote and location.
- **Quote that does not support its claim.** Read the quote against the cell text; a quote that is topically near the claim but does not state it is paraphrase drift, not grounding.
- **"No effect" with no test shown.** A `null` cell whose quote does not show the paper tested for the effect is a silence mislabeled as a null — recode it `n/r`.
- **Cite whose DOI resolves to another title.** Caught by resolving the identifier before trusting the cite; an unresolved or mismatched DOI is not yet a usable citation.
