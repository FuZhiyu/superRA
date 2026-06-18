---
title: "zotero-paper-reader"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Ask a bare agent to "read Reis (2021) and cite it here" and it has no path to your library: it fetches whatever it can off the web (often the wrong version or a summary confabulated from the title) and invents a BibTeX key that does not match your `.bib`. The bad key compiles cleanly and only surfaces as a dangling reference at submission.

This skill drives your real Zotero library through the local Desktop API (no credentials, falls back to the Web API when Desktop is closed) and resolves citekeys from your **Better BibTeX** plugin, so emitted keys match your master `.bib`. Ask in plain language; the agent picks the command.

**Read a paper.** "Read the Du-Tepper-Verdelhan paper from my Zotero and summarize the identification strategy." The agent searches metadata or full text, disambiguates if several match, converts the PDF via [`mistral-pdf-to-markdown`](skills/mistral-pdf-to-markdown/SKILL.md), saves it under `Notes/PaperInMarkdown/`, and reads in sections rather than dumping the whole conversion into context. Analysis is grounded in the converted text, not the title.

**Cite into a draft.** "Cite Fama-French 1993 in `paper.tex` and add it to `refs.bib`." Citation insertion dedup-appends the bibliography entry, so a citation never lands without its `.bib` entry and re-running never double-adds; you can also drop the cite at a `--marker` placeholder you left in the draft. The tool also exports BibTeX and renders formatted references (APA or another CSL style) for selected items.

If Desktop Zotero or Better BibTeX is not running, citation commands fall back to Zotero's built-in translator and flag `bbt_fallback: true` — the keys may not match your `.bib`, so keep Desktop open with Better BibTeX installed.

**Query the library.** Ask "find papers tagged `term-structure`" or "what's the Zotero key for this DOI" — list collections and tags, build a DOI-to-key map, inspect a record and its attachments.

When access breaks, the agent runs `health` to distinguish Zotero-not-running from local-API-disabled from BBT-missing. Local mode needs the local API enabled (Settings → Advanced → "Allow other applications on this computer to communicate with Zotero"); Web-API mode needs `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` from your environment or a gitignored `Notes/.env`.

The full command surface, flags, JSON fields, and troubleshooting live in [`zotero-paper-reader`](skills/zotero-paper-reader/SKILL.md).
