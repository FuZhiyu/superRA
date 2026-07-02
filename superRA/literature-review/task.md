---
title: "Literature Review Domain Vertical"
status: approved
depends_on: []
---

## Objective

Own the literature-review domain vertical. `skills/literature-review/` teaches the search → screen → synthesize discipline for **economics/finance** literature reviews, and ships an execution model with two halves: (1) a main-agent **interactive setup** that asks questions to settle the review's criteria and schema and scaffolds a paper ledger, and (2) a **fan-out** of agents that screen and extract from papers in a loop-until-dry snowball. It composes existing skills rather than restating them — `zotero-paper-reader` (dedup against the library, fetch PDFs, cite/BibTeX), `mistral-pdf-to-markdown` (OCR a curated shortlist), and `writing` (any prose) — and bundles one new tool: a citation-graph + metadata client. The vertical is wired into the skill-discovery surfaces and protected by a skill-trigger test, mirroring `slide-design-vertical`.

The deliverable a review produces is a **curated, provenance-tracked, extracted collection** (screened set + per-paper justification + quote-grounded extraction + convergence judgment), not a drafted prose review. Synthesis, classification, and gap analysis are **bespoke to each review** and out of scope for the vertical — the skill delivers the organized evidence, and any downstream map is authored per project.

### Context

This is skill-creation work in the superRA repo. Load `skill-creator` before editing any `skills/*/SKILL.md`; keep instructions minimal and behavior-shaping; update the inventory surfaces when adding a skill. The repo is **public** — tests and examples must never carry personal library data (real group names/ids, item keys, titles, counts, query results); use placeholders and hypothetical examples.

The design is distilled from a proven manual run (a heterogeneous-investor asset-pricing collection) plus a survey of existing tools (Elicit, Consensus, Undermind, PaperQA2, STORM) and API research. The manual run's mechanism is the spine; the research adds automation (citation APIs), anti-hallucination grounding, and econ/finance corpus discipline.

### Conventions

**Discovery is multi-modal — no single search tool.** Semantic Scholar and other citation-graph indexes lag on the newest working papers and have coverage holes, so front-line discovery **leads with web search** — the agent's WebSearch/WebFetch plus site-scoped queries (`site:ssrn.com`, `site:nber.org`, RePEc/IDEAS, arXiv q-fin, author pages), run as several blind lenses and deduped. Semantic Scholar's primary role is the **citation graph** (backward `/references`, forward `/citations`) and semantic-similarity search over indexed work — not sole front-line search. **Crossref** is the authoritative published-version-of-record resolver by DOI/title (covers NBER). arXiv supplies q-fin/econ preprint abstracts. Google Scholar has the broadest WP coverage but no API and blocks scraping — approximate it with WebSearch + site-scoped queries. **No OpenAlex** (data quality). **No Docker / translation-server** (setup friction) — the Zotero item is built from the verbatim record via a small mapper.

**No API keys required.** Semantic Scholar, Crossref, and arXiv are all keyless — S2's anonymous pool suffices because discovery is web-first, so S2 is called only for citation-graph traversal on already-screened papers (low volume). **S2 is optional:** the loop runs on web search + Crossref alone, with S2 added only to automate backward/forward citation snowballing. The only keys anywhere are Mistral (OCR shortlist) and — for the cloud Zotero write path only — a Zotero write key; the local connector needs none.

**Metadata policy — never agent-authored.** Bibliographic fields are queried and stored **verbatim**; an agent never types them. Metadata is always taken from the **published version of record** (Crossref DOI). SSRN working papers usually lack a Crossref DOI → discover/resolve them via S2/web, and adopt the published Crossref metadata once a published version exists. When a paper is in **no structured index** (a brand-new WP found via web search), take metadata from the publisher/repository page's embedded **`citation_*` / Dublin Core meta tags** (the structured fields Zotero's web translators read) — still verbatim from the source page, never agent-composed.

**PDF policy.** Fetch the PDF best-effort. On a paywall, fall back to the **latest freely-available version** (preprint/WP) and **flag the divergence** in the ledger (e.g. metadata = published JF 2024; PDF = 2021 SSRN WP). WP and published versions differ materially in economics, so the flag is required.

**Anti-hallucination.** Resolve every DOI against Crossref/S2 before trusting a cite (64% of fabricated cites carry a real-but-unrelated DOI). Ground extracted claims in verbatim quotes. Distinguish a true null from "not reported."

**Ledger modes.** Inside a superRA tree: **subtree-as-ledger** — one subtask per paper considered (included or excluded), directory name = paper key (`firstauthor-year`, the dedup identity), `status` encodes the discovery frontier (`not-started` = unscreened frontier, `implemented` = screened, `approved` = confirmed, `postponed` = can't fetch), in/out is a tag (`included` / `archived`). Standalone (no superRA tree): a **folder ledger** following the project's convention (a papers ledger file + `Notes/papers/` store).

**Screen-first.** Decide from metadata / abstract / intro — no full-text OCR during screening. Only a curated shortlist of central included papers gets OCR'd via `mistral-pdf-to-markdown`; bulk OCR is deferred.

**Econ/finance discipline.** Working-paper-first coverage (SSRN / NBER / RePEc), version-tracking, JEL codes as a scope/audit facet, and weighting by outlet tier + identification strategy — not crawlability or raw citation count.

**Snowball + convergence.** Backward citation BFS from a seed set plus a forward multi-lens web sweep; the orchestrator owns dedup + frontier growth, each agent writes only its own ledger entry. Stop when a full backward round and the forward sweep add essentially no new in-scope papers; record the stopping judgment and any deliberate non-expansions.

**Skill file layout — partition by loader.** The skill is loaded by two roles: the **main agent** (interactive setup + loop-until-dry orchestration) and the per-paper **implementer** (fetch metadata → screen → write its ledger entry → surface candidates). Orchestration lives in a main-agent-only reference; SKILL.md carries only the shared framing, references map, composed-skills routing, and ledger schema that both roles need; per-paper domain discipline lives in the references the implementer loads. See CLAUDE.md §Minimal, Targeted Instructions.

## Planner Guidance

Child order: `citation-metadata-client` is foundational (no deps). `skill-core` and `zotero-add` run in parallel after it. `skill-references` follows `skill-core`. `discovery-wiring-and-tests` is last. Precedent for a vertical build (skill + references + assets + inventory wiring + trigger test) is `slide-design-vertical` and `zotero-skills` — read both before executing.
