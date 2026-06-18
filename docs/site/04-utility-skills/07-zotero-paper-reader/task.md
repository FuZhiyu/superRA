---
title: "zotero-paper-reader"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Ask a bare agent to "read Reis (2021) on inflation expectations and cite it here" and it has no path to your library. It reaches for whatever it can fetch off the web — often the wrong version, a preprint, or a summary confabulated from the title — and when you ask it to cite, it invents a BibTeX key that does not match the one your `.bib` already uses. That last failure is costly because the citation compiles cleanly, looks right, and resolves to a dangling reference only at submission time.

This skill drives your actual Zotero library through one bundled tool, `scripts/zotero_tool.py` (run via `uv run --script <skill-dir>/scripts/zotero_tool.py …`). It runs against the Zotero Desktop local API by default — no credentials, no network — and falls back to the Zotero Web API when desktop Zotero is closed. Every command emits JSON for the agent to read; every read or citation command accepts `--library <group-id>` to target a group library instead of My Library. Credentials, when the Web-API path needs them, are never echoed into the transcript.

**Reading a paper.** Ask in plain language — "read the Du-Tepper-Verdelhan paper from my Zotero and summarize the identification strategy," "summarize the methods of the term-structure paper I saved last week." The agent runs a fixed pipeline rather than guessing: `search "query"` (metadata) or `search "phrase" --fulltext` (indexed body text), disambiguates with a short list when several papers match, finds the PDF attachment with `children`, resolves its stored path with `pdf`, hands the file to the `mistral-pdf-to-markdown` skill, and saves the result under `Notes/PaperInMarkdown/Author_Year_ShortTitle.md`. It then reads in sections — abstract and introduction first, targeted sections on request — instead of dumping a 40-page conversion into context. The analysis is grounded in the converted text, not in what the agent assumes a paper with that title says.

**Citing into a draft.** Three commands resolve citekeys from your **Better BibTeX (BBT)** plugin by default, so the key they emit is the key your master `.bib` already uses:

- "Cite Fama-French 1993 here in `paper.tex` and add it to `refs.bib`" → `cite --query "Fama French 1993" --tex paper.tex --bib refs.bib` inserts `\cite{KEY}` (or `[@KEY]` with `--markdown`) and dedup-appends the matching entry, so re-running never double-adds and a citation never lands without its bibliography entry. Add `--marker "[CITE-FF]"` to drop the citation at a placeholder you left in the draft; a missing marker errors rather than appending in the wrong place.
- "Export bibtex for these two papers into `refs.bib`" → `bibtex --item-key ABCD1234 --item-key EFGH5678 --bib refs.bib`. Select items by `--item-key`, `--query`, or `--doi` (each repeatable).
- "Render an APA reference for this" → `bibliography --query "monetary policy"` (APA by default; `--style chicago-author-date --text` for another CSL style as plain lines).

When desktop Zotero or the Better BibTeX plugin is not running, these commands still work through Zotero's built-in translator, but they print a key-mismatch warning and set `bbt_fallback: true` in the JSON — the emitted keys may not match your BBT `.bib`. Keep desktop Zotero open with Better BibTeX installed to get matching keys.

**Library queries.** The same tool answers the lookups you would otherwise click through Zotero for: `collections` and `tags` list your collections and tags, `doiindex` builds a DOI-to-key map, `item KEY` and `children KEY` inspect a record and its attachments. Ask things like "find papers tagged `term-structure`" or "what's the Zotero key for this DOI."

**When access breaks.** Run `health`: it reports `active_mode`, `local_api_available`, `web_api_configured`, and `better_bibtex_available`, which distinguishes Zotero-not-running from local-API-disabled from BBT-missing. Local mode needs only Zotero Desktop with the local API enabled (Settings → Advanced → "Allow other applications on this computer to communicate with Zotero"); Web-API mode needs `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY`, read from your environment or a gitignored `Notes/.env`.

The full command surface, JSON field reference, the Better BibTeX key model, and access-mode troubleshooting live in [`zotero-paper-reader`](skills/zotero-paper-reader/SKILL.md).
