---
title: "Utility Skills"
status: not-started
depends_on:  []
---

## Objective

Utility skills supply capabilities that cut across every kind of research; a [domain skill](#/03-domain-skills) supplies the discipline for one kind. Agents load the right one as the workflow runs. You can also ask for any of them by name in plain language. Each page below links the skill's `SKILL.md` as the authority; the grouping lives in [CATEGORIES.md](skills/CATEGORIES.md).

- [**task-tree**](#/04-utility-skills/01-task-tree) — keeps project state in git-tracked task files instead of the chat, so a fresh session resumes from the files; a live dashboard shows the tree, its status, and the reproduction graph of which results are current.
- [**semantic-merge**](#/04-utility-skills/02-semantic-merge) — resolves a merge, rebase, or cherry-pick by what each side meant, so a tightened filter is not silently reverted when the other side touched the same lines.
- [**reproducibility**](#/04-utility-skills/09-reproducibility) — records which commands produce each result and what they read, so after an edit you see which tables and figures are out of date and rebuild only those. Ask "which results does this edit affect?" before choosing what to rerun.
- [**result-protection**](#/04-utility-skills/03-result-protection) — helps choose the permanent record for each key result, and whether a drift test should guard it beyond documentation.
- [**refactor-and-integrate**](#/04-utility-skills/04-refactor-and-integrate) — reworks a correct-but-rough branch to match your project's naming, helpers, and docs, and prunes it to a diff a reviewer can read.
- [**communicate**](#/04-utility-skills/05-communicate) — makes conversation, task files, reports, and reviews skimmable: outcome first, evidence and caveats next, mechanics behind links.
- [**worktree-data-sync**](#/04-utility-skills/06-worktree-data-sync) — seeds, diffs, and reconciles the gitignored data git won't move between worktrees, so a parallel run doesn't start on an empty `Data/` directory.
- [**zotero-paper-reader**](#/04-utility-skills/07-zotero-paper-reader) — reads papers from your Zotero library and cites them with the Better BibTeX keys your `.bib` already uses.
- [**mistral-pdf-to-markdown**](#/04-utility-skills/08-mistral-pdf-to-markdown) — converts a PDF through Mistral OCR into Markdown with extracted images, keeping scans and two-column layouts in reading order.
