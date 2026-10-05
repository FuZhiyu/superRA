---
title: "zotero-paper-reader"
status: not-started
depends_on:  []
---

## Objective

This skill lets the agent read and cite papers from your own Zotero library, with the citekeys your `.bib` already uses. Without it, an agent asked to "read Reis (2021) and cite it" summarizes whatever version it finds on the web and invents a key that dangles at compile time.

## Set up Zotero once

- **Keep Zotero Desktop running, with the local API on:** Settings → Advanced → "Allow other applications on this computer to communicate with Zotero." No credentials needed.
- **Install [Better BibTeX](https://retorque.re/zotero-better-bibtex/)** for citation work. It gives each item one stable citekey (the `key` in `\cite{key}`), so keys the agent emits match your master `.bib`.
  - Without it, citing still works through Zotero's built-in exporter, but its keys differ from Better BibTeX's, and the agent warns you that they may not match your `.bib`.
- **Optional Web API fallback** when Desktop is closed: set `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` in your environment or in `Notes/.env`. Better BibTeX keys need Desktop, so citations made in Web mode always carry the mismatch warning.

When access breaks, ask the agent to run `health`: it tells apart Zotero not running, the local API disabled, and Better BibTeX missing.

## Ask in plain language

| You say | The agent |
|---|---|
| "Read the Du-Tepper-Verdelhan paper from my Zotero and summarize the identification strategy." | Finds the paper, converts its PDF with [`mistral-pdf-to-markdown`](#/03-utility-skills/09-mistral-pdf-to-markdown) into `Notes/PaperInMarkdown/`, and reads it section by section |
| "Add Fama-French 1993 to `refs.bib`." | Appends the entry, skipping it if that citekey is already there |
| "Cite Fama-French 1993 in `paper.tex`." | Appends `\cite{key}` to the draft (`[@key]` in Markdown) and adds the entry to your `.bib` |
| "Cite it at `[CITE-FF]`." | Replaces that placeholder instead of appending; stops with an error if the placeholder is not found |
| "Format these three papers in Chicago for my reading list." | Renders formatted references in any CSL style (APA by default) |
| "Find papers tagged `term-structure`." | Searches metadata, full text, collections, tags, or DOIs |

- **Your `.bib` is only ever appended to.** Existing entries are never reordered or rewritten, so asking twice leaves one entry.
- **Group libraries work too.** Name the group, and the agent targets it instead of My Library.

Commands, flags, and JSON output are in [`zotero-paper-reader`](skills/zotero-paper-reader/SKILL.md).
