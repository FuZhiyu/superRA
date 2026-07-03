# Anti-Hallucination Grounding & Extraction

Review-agent reference. Load when extracting from a claimed included paper; this is the extraction-depth checklist for the same claimed-read session.

Treat every bibliographic claim and extracted finding as **guilty until grounded**: do not trust a cite until its DOI resolves to the paper you mean, do not record a finding until a verbatim quote from the source supports it, and do not write "no effect" until the paper is shown to have tested for one.

## Resolve every DOI before trusting a cite

A resolving DOI is not enough — a fabricated cite often carries a real but unrelated DOI. Before trusting any cite, resolve its identifier (`citation_client metadata IDENTIFIER`) and check that the returned **title, first author, and year match the paper you intend to cite**. A DOI that resolves to a different title is a mismatched or fabricated cite: drop it, or correct it to the DOI that actually points to the paper.

Apply this to cites you surface from a paper's reference list too — the `unstructured` Crossref-array references are frequently DOI-less or mis-keyed. Resolve before adding to the frontier.

## Extraction Shape

The setup survey defines comparison columns: facts that must be comparable across every included paper. The set may be empty. Fill those columns when present; otherwise extraction is narrative-only.

Everything outside the comparison columns is a free-form grounded narrative note per paper.

Every extracted claim carries a verbatim quote and location (section or page). Extraction reads the OCR'd full text when the needed evidence is not already available, because the answer usually lives in the results or model section, not the abstract.

Convert **once**: before OCR'ing a shortlist paper, check its `md_path` and reuse an existing conversion — Mistral OCR is billed, so never re-convert a paper already saved. A fresh conversion writes `<key>.md` plus extracted images into the durable store and records `md_path` + `fetched_at`.

**Extract, then verify** — two passes:

1. **Extract** — read the paper and write the claim with the quote you believe supports it.
2. **Verify** — confirm the quote appears verbatim in the source, and read the quote against the claim to confirm it actually supports it, not merely sits near it. A quote adjacent to the claim but not stating it is paraphrase drift — reject it.

## Honest null vs "not reported"

Encode a **true null** — the paper tested for an effect and found none — differently from a **silence** — the paper does not address the question (e.g. `null` vs `n/r`). Reporting "no effect" for a paper that never ran the test invents a result the authors never claimed.

**Identification protocol:** walk the extracted claims and flag these tells:

- **Ungrounded claim.** A claim with no quote — it was filled from inference or memory. Every claim carries its supporting quote and location.
- **Quote that does not support its claim.** Read the quote against the claim; a quote that is topically near the claim but does not state it is paraphrase drift, not grounding.
- **"No effect" with no test shown.** A `null` cell whose quote does not show the paper tested for the effect is a silence mislabeled as a null — recode it `n/r`.
- **Cite whose DOI resolves to another title.** Caught by resolving the identifier before trusting the cite; an unresolved or mismatched DOI is not yet a usable citation.
