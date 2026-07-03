---
name: literature-review
description: Economics/finance literature-review discipline — search, screen, snowball, and organize a curated, provenance-tracked collection of papers. Use when assembling or mapping the papers on an econ/finance research area (a survey, related-work section, or reading list): finding, screening, deduping, and per-paper extraction via snowball citation search. Not for reading or citing a single already-known paper — that is zotero-paper-reader.
user-invocable: true
---
# Literature Review

Discipline for economics/finance literature reviews. The deliverable is a **curated, provenance-tracked, extracted collection** — a screened paper set, a per-paper justification and quote-grounded extraction, and a convergence judgment. Synthesis and any classification or gap map are authored per review (route that prose to `writing`); the deliverable here is the organized evidence.

Discovery is **web-first and multi-modal** — no single index is authoritative. Lead with web search across several blind lenses, use the citation graph for snowballing, and take every bibliographic field verbatim from the published version of record — an agent never types metadata.

## References

Load per workflow point, not all at once. The main agent orchestrates from `workflow.md`; each dispatched agent loads the domain references its screening/extraction step needs.

| Reference | Loaded by | Load when |
|---|---|---|
| `references/workflow.md` | main agent | orchestrating a review — interactive setup, the loop-until-dry fan-out, and the executor. |
| `references/search-and-screening.md` | screening agent (+ main) | running discovery — snowball (backward citation BFS + forward multi-lens web sweep), screen-first triage, the dedup cascade, and the stopping/convergence judgment. |
| `references/econ-corpus.md` | screening agent | judging coverage and quality — working-paper-first sourcing (SSRN / NBER / RePEc), published-version metadata with the WP-divergence flag, JEL codes, and weighting by outlet tier + identification strategy. |
| `references/grounding-and-extraction.md` | extracting agent | extracting from a paper — DOI resolution before trusting a cite, the quote-grounded concept matrix, and honest null vs "not reported". |
| `references/citation-client.md` | main agent + agents | calling the bundled citation-graph + metadata client — subcommands (`search`, `references`, `citations`, `metadata`, `dedup`, `health`) and their JSON shapes. |

## Composed skills

Route to these rather than reimplementing their work:

- **`zotero-paper-reader`** — dedup a candidate against the existing library, fetch PDFs, export BibTeX / insert cites, and (via its `add` / `attach` path) save discovered papers into the target library the setup survey selected.
- **`mistral-pdf-to-markdown`** — OCR only the curated shortlist of central included papers. Bulk OCR is deferred; screening never needs it.
- **`writing`** — any reader-facing prose (a synthesis note, gap analysis, or a related-work draft).

## Ledger schema

Each considered paper — included or excluded — gets one entry keyed on `firstauthor-year` (the dedup identity). Provenance splits into two blocks: **discovery lineage** (how the paper was found) and a **retrieval trace** (how to refetch its artifact). The entry records:

- **metadata** — verbatim published-version-of-record fields.
- **discovery lineage** — `discovered_via` (`seed` | `<parent-key>` | `web:<lens>` | `forward-cite`) and `bfs_depth`.
- **retrieval trace** — how to refetch the artifact: `ids` (`doi` / `arxiv` / `s2` / `corpus_id`, mirroring the client's normalized `id` block), `landing_url`, `pdf_url` + `access` (`oa` | `paywall` | `wp-fallback`), `pdf_path`, `md_path`, `fetched_at`. The **version-divergence flag** lives here — set it when the fetched PDF is a preprint/WP that differs from the published metadata (e.g. metadata = published JF 2024; PDF = 2021 SSRN WP). Required (see `references/econ-corpus.md`).
- **decision** — `included` / `excluded`, the reason, the failing gate when excluded, and `read_depth` (a one-line note when the screen escalated past abstract/intro — see `references/search-and-screening.md`).
- **extraction fields** — the schema the setup survey defined.

**Trace link cluster.** The written entry renders the retrieval fields as a **navigable cluster** a reader clicks straight through to the artifact — rendering only the targets that exist, never fabricating a link:

- **Zotero** — `zotero://select/library/items/<ITEM_KEY>` (personal) or `zotero://select/groups/<GROUP_ID>/items/<ITEM_KEY>` (group); optionally `zotero://open-pdf/library/items/<ITEM_KEY>` to jump to the PDF. Only when the paper was saved to Zotero and its item key is known.
- **Web** — the `landing_url`, or `https://doi.org/<doi>`.
- **PDF** — `file://<absolute-path>.pdf`.
- **Markdown (OCR)** — `vscode://file/<absolute-path>.md` (the editor scheme is configurable, e.g. `cursor://file/...`).

`file://` and `vscode://file/` deeplinks resolve only from **absolute paths**, so the ledger stores absolute paths for them — correct for a researcher's own project on their machine; in this skill's own examples use placeholder paths only. File-link citation *mechanics* are `report-in-markdown`'s — follow it for the link form; this list is only the domain-specific set a paper entry carries.

Two representations, same fields:

- **subtree-as-ledger** (inside a superRA tree) — one subtask per paper; directory name = paper key; `status` encodes the discovery frontier (`not-started` = unscreened frontier, `implemented` = screened, `approved` = confirmed, `postponed` = can't fetch); in/out is a tag (`included` / `archived`).
- **folder ledger** (standalone) — a papers ledger file plus a `Notes/papers/` store, following the project's convention.
