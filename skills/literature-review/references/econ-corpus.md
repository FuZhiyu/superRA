# Econ/Finance Corpus Discipline

Load when judging coverage and quality: working-paper-first sourcing, published-version metadata with the divergence flag, JEL codes, and weighting by outlet tier + identification strategy.

## Principle: the econ corpus is not the published corpus

Economics and finance move on working papers. A result circulates as an SSRN or NBER paper for two to five years — presented, cited, and built on — before it appears in a journal, and the journal version can differ materially in sample, method, and even conclusion. A review that covers only published papers is stale in any active area. So coverage leads with the working-paper repositories, metadata is anchored to the published version of record once one exists, and quality is judged by where the work landed and how it identified its effect — not by how easily a crawler found it or how many times it has been cited.

## Working-paper-first coverage

The primary discovery surfaces are the working-paper repositories: **SSRN**, **NBER**, and **RePEc/IDEAS**. arXiv `q-fin`/`econ` carries the preprints. Reach these through the site-scoped web lenses in [search-and-screening.md](search-and-screening.md); the citation client's indexed search supplements but lags the newest papers.

**Tell of under-coverage:** an active area whose ledger contains no working papers — only journal articles — has not reached the frontier. The most recent in-scope work in a live literature is almost always still a WP; its absence means the forward sweep did not reach SSRN/NBER.

## Published-version-of-record metadata + the divergence flag

Take every bibliographic field verbatim from the **published version of record** — the Crossref record resolved from the DOI (`citation_client metadata IDENTIFIER`). An agent never types metadata. A working paper with no published DOI keeps its WP metadata, taken verbatim from the source page's `citation_*` / Dublin Core tags; adopt the published Crossref record once a published version exists.

When the PDF you fetched is a preprint or WP that differs from the published metadata, record the **version-divergence flag** on the entry: metadata year vs PDF year and source (e.g. metadata = *Journal of Finance* 2024; PDF = 2021 SSRN WP). This is required, not optional — WP and published versions differ materially in economics, and a reader extracting from the 2021 PDF must know the citable version is the 2024 one and may report different numbers.

**Tell of a missing flag:** any entry whose metadata year and PDF year differ with no divergence flag. Check it — either the flag was dropped or the two are the same version and the year mismatch is an error.

## JEL codes as a scope/audit facet

Record each paper's JEL codes (e.g. `G12` asset pricing, `G14` information and market efficiency, `D83` search and learning) verbatim from the source. JEL codes are a **facet, not a gate** — they do not decide inclusion. Their use is auditing coverage: if the review's scope maps to a set of JEL codes, a code with thin representation in the ledger is a candidate gap, and a large cluster under a code the scope did not intend is a scope-creep signal. Use them to check the shape of the corpus, not to admit or reject a paper.

## Weighting by outlet tier + identification strategy

Quality weighting in this corpus rests on two signals, and on neither crawlability nor raw citation count.

**Outlet tier** — where the work landed:

- **Top-5 economics** — *American Economic Review*, *Econometrica*, *Journal of Political Economy*, *Quarterly Journal of Economics*, *Review of Economic Studies*.
- **Top-3 finance** — *Journal of Finance*, *Journal of Financial Economics*, *Review of Financial Studies*.
- Field-leading journals below the top tier (e.g. *RAND*, *JFQA*, *Management Science*) carry weight in their subfield.

Tier is a signal, not a filter: a well-identified working paper outweighs a weakly-identified published one, and unpublished frontier work is included on its merits.

**Identification strategy** — how the paper establishes its effect: RCT, difference-in-differences (DiD), instrumental variables (IV), regression discontinuity (RD), or a structural model. Weight by the credibility of the identification for the claim being made. **Raw citation count is not a quality signal here** — it reflects a paper's age and its field's size far more than its rigor, and it systematically undercounts recent working papers that carry the frontier.

**Identification protocol:** for each included paper, the quality note should name its outlet tier and its identification strategy — the two facts a reader needs to weight it. Two tells to flag:

- **Citation-count justification.** An inclusion or ranking justified only by citation count — re-judge on tier and identification.
- **Unstated identification.** An empirical paper included with no identification strategy recorded — the strategy is the credibility of the result and belongs in the entry.
