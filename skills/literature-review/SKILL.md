---
name: literature-review
description: "Economics/finance literature-review discipline — search, screen, snowball, and organize a curated, provenance-tracked collection of papers. Use when assembling or mapping the papers on an econ/finance research area (a survey, related-work section, or reading list): finding, screening, deduping, and per-paper extraction via snowball citation search. Not for reading or citing a single already-known paper — that is zotero-paper-reader."
user-invocable: true
---
# Literature Review

Discipline for economics/finance literature reviews. The deliverable is a **curated, provenance-tracked, extracted collection** — a screened paper set, a per-paper justification and quote-grounded extraction, and a convergence judgment. Synthesis and any classification or gap map are authored per review (route that prose to `writing`); the deliverable here is the organized evidence.

Discovery is **web-first and multi-modal** — no single index is authoritative. Lead with web search across several blind lenses, use the citation graph for snowballing, and take every bibliographic field verbatim from the published version of record — an agent never types metadata.

## References

Load per workflow point, not all at once. The main agent orchestrates from `workflow.md`; dispatched agents load only the reference for their assigned role.

| Reference | Loaded by | Load when |
|---|---|---|
| `references/workflow.md` | main agent | orchestrating a task-tree-native review — interactive setup, candidate-store setup, discovery/screening dispatch, promotion, synthesis, and saturation judgment. |
| `references/discovery.md` | discovery agent | searching a lens, expanding from a seed/included paper, creating/updating candidate-paper records, and reporting a local map. |
| `references/screening.md` | screening agent | deciding candidate membership, recording screening rationale, promoting authorized included papers, and routing discovery leads. |
| `references/econ-corpus.md` | screening agent | judging coverage and quality — working-paper-first sourcing (SSRN / NBER / RePEc), published-version metadata with the WP-divergence flag, JEL codes, and weighting by outlet tier + identification strategy. |
| `references/grounding-and-extraction.md` | extracting agent | extracting from a paper — DOI resolution before trusting a cite, the quote-grounded concept matrix, and honest null vs "not reported". |
| `references/citation-client.md` | main agent + agents | calling the bundled citation-graph + metadata client and candidate materializer — command surfaces and machine I/O shapes. |

## Composed skills

Route to these rather than reimplementing their work:

- **`zotero-paper-reader`** — dedup a candidate against the existing library, fetch PDFs, export BibTeX / insert cites, and (via its `add` / `attach` path) save discovered papers into the target library the setup survey selected.
- **`mistral-pdf-to-markdown`** — OCR only the curated shortlist of central included papers. Bulk OCR is deferred; screening never needs it.
- **`writing`** — any reader-facing prose (a synthesis note, gap analysis, or a related-work draft).

## Candidate And Paper Records

Pre-screen candidates live outside git in the project's local review-data convention as task-shaped folders, for example `Notes/literature-review/<review>/candidate-papers/<paper-key>/task.md`. Included or explicitly escalated papers are promoted into `superRA/<review>/papers/<paper-key>/task.md` by copying the same body template and adding normal task frontmatter. Do not create one dashboard task per pre-screen candidate.

Each candidate/paper record is keyed by the materializer's canonical folder name. It records:

- **metadata** — verbatim published-version-of-record fields.
- **discovery lineage** — `discovered_via` (`seed` | `<parent-key>` | `web:<lens>` | `forward-cite`), `bfs_depth`, and for citation-based finds a linked source paper plus a short quoted citation context.
- **retrieval trace** — how to refetch the artifact: `ids` (`doi` / `arxiv` / `s2` / `corpus_id`, mirroring the client's normalized `id` block), `landing_url`, `pdf_url` + `access` (`oa` | `paywall` | `wp-fallback`), `pdf_path`, `md_path`, `fetched_at`. The **version-divergence flag** lives here — set it when the fetched PDF is a preprint/WP that differs from the published metadata (e.g. metadata = published JF 2024; PDF = 2021 SSRN WP). Required (see `references/econ-corpus.md`).
- **decision** — `pending` / `included` / `excluded` / `escalate`, the reason, the failing gate when excluded, and `read_depth` when screening escalated past abstract/intro.
- **extraction fields** — the schema the setup survey defined.

## Linking Paper Mentions

**Trace link cluster.** The written entry also renders the retrieval fields as a **navigable cluster** a reader clicks straight through to the artifact:

- **Task file** — a relative markdown link to the promoted paper card, e.g. [smith-2024](papers/smith-2024/task.md). Use this first after promotion.
- **Zotero** — [smith-2024](zotero://select/library/items/<ITEM_KEY>) (personal) or [smith-2024](zotero://select/groups/<GROUP_ID>/items/<ITEM_KEY>) (group). Only when the paper was saved to Zotero and its item key is known.
- **Web** — [smith-2024](https://doi.org/<doi>), or the `landing_url`.
- **PDF** — a **relative** markdown link to the stored PDF, e.g. [smith-2024](attachments/<key>.pdf).
- **Markdown (OCR)** — a **relative** markdown link to the stored conversion, e.g. [smith-2024](attachments/<key>.md).

Whenever any task file, candidate record, Markdown ledger, report, summary, task result, candidate list, extraction note, or convergence note mentions a paper, link that paper mention to the first available target in this order: **task file** -> **Zotero** -> **Web** -> **PDF** -> **Markdown (OCR)**. Render only targets that exist, never fabricating a link.

Render file links as **relative paths only** — never absolute, never `file://` / `vscode://`. The `zotero://` scheme link passes through the dashboard renderer as a clickable deeplink.

The candidate store remains auditable outside git for excluded and pending records. The task tree stays researcher-facing: review-root progress, discovery/screening/synthesis tasks, and promoted paper cards.
