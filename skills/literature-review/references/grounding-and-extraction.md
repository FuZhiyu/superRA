# Anti-Hallucination Grounding & Extraction

Load when extracting from a paper: DOI resolution before trusting a cite, the quote-grounded concept matrix, and honest null vs "not reported".

## Principle: extraction is adversarial against your own confabulation

A language model will produce a plausible citation, a plausible finding, and a plausible number on demand — all three can be fabricated while reading as correct. Extraction discipline treats every bibliographic claim and every extracted finding as **guilty until grounded**: a cite is not trusted until its DOI resolves to the paper you mean, a finding is not recorded until a verbatim quote from the source supports it, and "no effect" is not written until the paper is shown to have tested for one. The cost of this discipline is a second pass; the cost of skipping it is a review that cites papers that do not say what it claims.

## Resolve every DOI before trusting a cite

Roughly two-thirds of fabricated citations carry a **real but unrelated DOI** — the DOI exists and resolves, so its mere existence proves nothing. Before trusting any cite, resolve its identifier (`citation_client metadata IDENTIFIER`) and check that the returned **title, first author, and year match the paper you intend to cite**. A DOI that resolves to a different title is a mismatched or fabricated cite: drop it, or correct it to the DOI that actually points to the paper.

Apply this to cites you surface from a paper's reference list too — the `unstructured` Crossref-array references are frequently DOI-less or mis-keyed. Resolve before adding to the frontier.

## The quote-grounded concept matrix

Extract into a **concept matrix**: one row per paper, **one question per column**. The columns are the extraction schema settled in setup (e.g. "what friction drives the result?", "identification strategy", "sign of the main effect", "sample and period"). One question per column forces the same question to be asked of every paper, which makes the papers comparable and makes gaps visible (see [synthesis-and-classification.md](synthesis-and-classification.md)).

**Every cell is a claim plus the verbatim quote that grounds it, with its location** (section or page). A cell is not filled from memory of the abstract or from inference — it is filled from a quote you can point to in the source. Screening reads the abstract and intro; extraction of a central paper reads the OCR'd full text (the `mistral-pdf-to-markdown` shortlist), because the answer to a schema question usually lives in the results or the model section, not the abstract.

**Extract, then verify** — two passes:

1. **Extract** — read the paper and fill the cell with the claim and the quote you believe supports it.
2. **Verify** — confirm the quote appears verbatim in the source, and read the quote against the claim to confirm it actually supports it (not merely sits near it). Paraphrase drift — a quote that is adjacent to the claim but does not state it — is the common failure; the verify pass exists to catch it.

## Honest null vs "not reported"

A **true null** — the paper tested for an effect and found none — and a **silence** — the paper does not address the question — are different findings and must be encoded differently in the matrix (e.g. `null` vs `n/r`). Collapsing them fabricates evidence: reporting "no effect" for a paper that never ran the test invents a result the authors never claimed.

**Identification protocol:** walk the matrix cell by cell and flag these tells:

- **Ungrounded cell.** A claim with no quote — it was filled from inference or memory. Every cell carries its supporting quote and location.
- **Quote that does not support its claim.** Read the quote against the cell text; a quote that is topically near the claim but does not state it is paraphrase drift, not grounding.
- **"No effect" with no test shown.** A `null` cell whose quote does not show the paper tested for the effect is a silence mislabeled as a null — recode it `n/r`.
- **Cite whose DOI resolves to another title.** Caught by resolving the identifier before trusting the cite; an unresolved or mismatched DOI is not yet a usable citation.
