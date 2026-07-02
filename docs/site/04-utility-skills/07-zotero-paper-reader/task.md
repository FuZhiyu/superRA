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

### Why Better BibTeX

A **citekey** is the short label you cite a paper by — the `key` in `\cite{key}` — and every entry in your `.bib` file carries one. The problem is that Zotero's built-in export does not assign these keys stably: the same paper can come out as a different key on different exports, so the key the agent emits today may not be the key already sitting in your master `.bib`, and the mismatch only surfaces as a dangling reference when you build the document.

[Better BibTeX](https://retorque.re/zotero-better-bibtex/) is a Zotero plugin that fixes this by giving each item one deterministic citekey — the same `Author_Year` form every time. That stability is what lets the agent cite a paper and have the key line up with the entry already in your `.bib`. Install it and keep Zotero Desktop running for any citation work. Without it the skill still works but falls back to Zotero's built-in translator, and it warns you that the keys it emits may not match your master `.bib`.

### Reading and citing

**Read a paper.** "Read the Du-Tepper-Verdelhan paper from my Zotero and summarize the identification strategy." The agent searches metadata or full text, disambiguates if several match, converts the PDF via [`mistral-pdf-to-markdown`](skills/mistral-pdf-to-markdown/SKILL.md), saves it under `Notes/PaperInMarkdown/`, and reads in sections rather than dumping the whole conversion into context. Analysis is grounded in the converted text, not the title.

**Add an entry to your `.bib`.** "Add Fama-French 1993 to `refs.bib`" looks the paper up in your library and appends its bibliography entry to the file you name. The append is deduplicated by citekey: if an entry with that key is already in the file it is skipped, and existing entries are never reordered or rewritten. That makes the command idempotent — running it twice on the same paper leaves exactly one entry, so you can re-ask freely without worrying about double-adding.

**Cite into a draft.** "Cite Fama-French 1993 in `paper.tex`" does two things at once: it inserts the `\cite{key}` into the draft *and* syncs that entry into your `.bib`, so a citation never lands without its bibliography entry. By default the `\cite{}` is appended at the end of the draft. If instead you have left a placeholder where the citation should go — say you typed `[CITE-FF]` while drafting — tell the agent to drop it at that marker, and it replaces the placeholder in place rather than appending. (If the placeholder text is not found it stops with an error rather than guessing a spot, so a typo cannot bury the citation somewhere wrong.)

**Export references without a draft.** The same path also exports plain BibTeX on its own, and renders formatted reference strings for a reading list or a response letter. The formatting follows a **CSL style** — Citation Style Language, the standard that defines how a reference reads in APA, Chicago, and the other journal formats — defaulting to APA and switchable to any style Zotero or Better BibTeX knows.

**Query the library.** Ask "find papers tagged `term-structure`" or "what's the Zotero key for this DOI" — list collections and tags, build a DOI-to-key map, inspect a record and its attachments.

When access breaks, the agent runs `health` to distinguish Zotero-not-running from local-API-disabled from BBT-missing. Local mode needs the local API enabled (Settings → Advanced → "Allow other applications on this computer to communicate with Zotero"); Web-API mode needs `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` from your environment or a gitignored `Notes/.env`.

The full command surface, flags, JSON fields, and troubleshooting live in [`zotero-paper-reader`](skills/zotero-paper-reader/SKILL.md).
