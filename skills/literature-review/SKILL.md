---
name: literature-review
description: "Economics/finance literature-review discipline — search, screen, snowball, and organize a curated, provenance-tracked collection of papers. Use when assembling or mapping the papers on an econ/finance research area (a survey, related-work section, or reading list): finding, screening, deduping, and per-paper extraction via snowball citation search. Not for reading or citing a single already-known paper — that is zotero-paper-reader."
user-invocable: true
---
# Literature Review

Discipline for economics/finance literature reviews. The deliverable is a **curated, provenance-tracked, extracted collection** — a screened paper set, a per-paper justification and quote-grounded extraction, and a convergence judgment. Synthesis and any classification or gap map are authored per review (route that prose to `writing`); the deliverable here is the organized evidence.

Discovery is **web-first and multi-modal** — no single index is authoritative. Lead with web search across several blind lenses, use the citation graph for snowballing, and take every bibliographic field verbatim from the published version of record — an agent never types metadata.

## References

Load per workflow point, not all at once. The main agent orchestrates from `workflow.md`; dispatched review agents load only the paper-work references their dispatch depth needs.

| Reference | Loaded by | Load when |
|---|---|---|
| `references/workflow.md` | main agent | orchestrating a task-tree-native review — interactive setup, candidate-store setup, frontier dispatch, permanent-record placement, synthesis, and saturation judgment. |
| `references/review-agent.md` | review agent | recon-expanding a frontier, materializing/updating candidates, claiming candidates for substantive reads, deciding membership, harvesting leads, and reporting a local map. |
| `references/econ-corpus.md` | review agent | judging coverage and quality — working-paper-first sourcing (SSRN / NBER / RePEc), published-version metadata with the WP-divergence flag, JEL codes, and weighting by outlet tier + identification strategy. |
| `references/grounding-and-extraction.md` | review agent | claimed-read dispatches — quote grounding, DOI checks, comparison fields, and narrative extraction. |
| `references/citation-client.md` | main agent + agents | calling the bundled citation-graph + metadata client and candidate materializer — command surfaces and machine I/O shapes. |

## Composed skills

Route to these rather than reimplementing their work:

- **`zotero-paper-reader`** — dedup/add during main-agent finalization when the setup survey selected a Zotero target; fetch PDFs, export BibTeX, and insert cites.
- **`mistral-pdf-to-markdown`** — OCR claimed included/escalated papers at extraction depth when source text is not already available.
- **`writing`** — any reader-facing prose (a synthesis note, gap analysis, or a related-work draft).

## Candidate And Paper Records

Pre-screen candidates live outside git in the project's local review-data convention as task-shaped folders, for example `Notes/literature-review/<review>/candidate-papers/<paper-key>/task.md`. A candidate card exists only for a specific paper with enough metadata to identify/refetch it, and begins `status: not-started`. Included or explicitly escalated papers get a main-agent-chosen permanent record; `superRA/<review>/papers/<paper-key>/task.md` is the default destination, not a requirement.

Each candidate/paper record is keyed by the materializer's canonical folder name. It records:

- **metadata** — verbatim published-version-of-record fields.
- **discovery lineage** — `discovered_via` (`seed` | `<parent-key>` | `web:<lens>` | `forward-cite`), `bfs_depth`, and for citation-based finds a linked source paper plus a short quoted citation context.
- **retrieval trace** — how to refetch the artifact: `ids` (`doi` / `arxiv` / `s2` / `corpus_id`, mirroring the client's normalized `id` block), Zotero item/attachment links when available, `landing_url`, `pdf_url` + `access` (`oa` | `paywall` | `wp-fallback`), `pdf_path`, `md_path`, `fetched_at`. The **version-divergence flag** lives here — set it when the fetched PDF is a preprint/WP that differs from the published metadata (e.g. metadata = published JF 2024; PDF = 2021 SSRN WP). Required (see `references/econ-corpus.md`).
- **reading notes** — claimed-read sessions and grounded takeaways; recon citation context for another paper belongs in discovery provenance.
- **decision** — `pending` / `included` / `excluded` / `escalate`, the reason, and the failing gate when excluded.
- **extraction fields** — the comparison columns and narrative notes the setup survey defined.

## Linking Paper Mentions

**Trace link cluster.** The written entry also renders the retrieval fields as a **navigable cluster** a reader clicks straight through to the artifact:

- **Task file** — a relative markdown link to the permanent paper record, e.g. [smith-2024](papers/smith-2024/task.md). Use this first after placement.
- **Zotero** — [smith-2024](zotero://select/library/items/<ITEM_KEY>) (personal) or [smith-2024](zotero://select/groups/<GROUP_ID>/items/<ITEM_KEY>) (group). Only when the paper was saved to Zotero and its item key is known.
- **Web** — [smith-2024](https://doi.org/<doi>), or the `landing_url`.
- **PDF** — a **relative** markdown link to the stored PDF, e.g. [smith-2024](attachments/<key>.pdf).
- **Markdown (OCR)** — a **relative** markdown link to the stored conversion, e.g. [smith-2024](attachments/<key>.md).

Whenever any task file, candidate record, Markdown ledger, report, summary, task result, candidate list, extraction note, or convergence note mentions a paper, link that paper mention to the first available target in this order: **task file** -> **Zotero** -> **Web** -> **PDF** -> **Markdown (OCR)**. Render only targets that exist, never fabricating a link.

Render file links as **relative paths only** — never absolute, never `file://` / `vscode://`. The `zotero://` scheme link passes through the dashboard renderer as a clickable deeplink.

The candidate store remains auditable outside git for excluded and pending records. The task tree stays researcher-facing: review-root progress, frontier/synthesis tasks, and permanent paper records.
