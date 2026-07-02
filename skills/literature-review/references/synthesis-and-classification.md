# Synthesis & Classification

Load when organizing the collection: concept-centric organization, matrix-sparsity gap detection, and the optional classification-axis pass.

## Principle: organize by ideas, not by authors

The deliverable is an organized map of what the literature knows, not a chronological list of who did what. The failure mode is author-centric prose — a paragraph per paper, "Smith (2020) shows X; Jones (2021) extends it to Y" — which forces the reader to hold every paper in mind and synthesize for themselves. A concept-centric map does the synthesis: it is organized by the questions and findings, and each paper appears wherever it speaks to a concept. The concept matrix built during extraction (see [grounding-and-extraction.md](grounding-and-extraction.md)) already has this shape — papers are rows, concepts are columns — so synthesis reads **down the columns**, not across the rows.

## Concept-centric organization

Read down each column: what does the literature say about this concept, across all the papers that address it — where do they agree, where do they split, what explains the split. Group the columns into an organizing structure; the usual axes are:

- **Thematic** — by mechanism, question, or finding. The default for most reviews.
- **Methodological** — by identification strategy or model class, when the interesting variation is how the question is answered.
- **Chronological** — by how the understanding evolved, when the field's trajectory is itself the point.

**Tell of author-centric drift:** a synthesis section where each paragraph opens with one paper's name and stays with that paper. That is a per-paper summary, not synthesis — rewrite it around the concept the papers share, citing each paper where it bears on that concept.

## Matrix-sparsity gap detection

The gaps in the literature are **read off the matrix**, not asserted from intuition. Where extraction filled a cell, a paper answers that question; where a cell is empty, it does not. So:

- An **empty cell** — this paper does not address this concept.
- A **sparse column** — a concept few papers address: an under-studied question.
- A **sparse region** — the intersection of a method cluster and a concept that no paper occupies (e.g. no paper studies concept C with an RD design): the structural gap, and usually the most defensible one to name.

Count filled cells per column and per method cluster; the emptiest region is the candidate gap. Before naming it as a gap, distinguish a **true gap** (no paper in the field has done this) from an **extraction gap** (a paper covers it but you did not OCR or extract it) and from a **scope gap** (it falls outside the review's boundary and was a deliberate non-expansion — recorded during discovery, see [search-and-screening.md](search-and-screening.md)). Only the true gap is a finding about the literature; the other two are findings about your own coverage.

## The optional classification-axis pass

When the setup schema defined a classification axis, run a pass that assigns each paper a class along it — a domain-structural dimension such as **model structure** (how each paper models the mechanism: representative-agent, heterogeneous-agent, search-and-matching, …) or **identification method**. The output is a taxonomy of the literature along that axis, which is itself a contribution: it shows the reader the shape of the field, not just its contents. This pass is optional — invoke it only when a classification axis was defined; a review without one still delivers the concept-centric map and gap analysis.

**Identification protocol** for the classification:

- **One class per paper per axis.** Each paper takes exactly one class on each axis, or an explicit `hybrid` with the combination named. A paper silently left unclassified is a hole in the taxonomy.
- **A bloated "other" category means the axis is wrong.** If most papers land in `other` / `misc`, the categories were imposed rather than read from the papers — redesign them from the actual distribution of approaches in the collection.
- **The axis must partition, not overlap.** If a paper genuinely fits two classes and it is not a deliberate hybrid, the classes are not mutually exclusive — sharpen their definitions.

## Close with the convergence judgment

Carry the stopping judgment from discovery into the synthesis so the map states its own completeness: note that the snowball saturated (the last round added essentially no in-scope papers) and list the deliberate non-expansions as the scope boundary. A reader then knows the empty cells are the field's gaps within a saturated, bounded map — not the review's blind spots.
