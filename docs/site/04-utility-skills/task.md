---
title: "Utility Skills"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Utility skills are domain-neutral capabilities the workflow and agents compose as the situation needs — and several are useful to you directly in an interactive session. A [domain skill](#/03-domain-skills) supplies the discipline for a kind of research; a utility skill supplies a capability that cuts across all of them. They are reusable mechanisms the agent assembles for the work at hand rather than a fixed pipeline.

Agents are taught to reach for the right one automatically as the workflow runs. You can also request any of them explicitly, by name, in plain language.

Each page below leads with what the skill gives you, then the moment you would reach for it, and links to its `SKILL.md` as the authority for the details; the grouping lives in [CATEGORIES.md](skills/CATEGORIES.md).

- [**task-tree**](#/04-utility-skills/01-task-tree) — keeps project state in git-tracked files instead of the chat scrollback, computing the tree with rollup status, the tasks ready to start now, the dependency DAG, and a live dashboard, so a fresh session resumes from the files rather than reconstructing state and getting it wrong.
- [**semantic-merge**](#/04-utility-skills/02-semantic-merge) — resolves a merge, rebase, or cherry-pick by what each side meant rather than which lines arrived last, so a tightened filter or a protected coefficient isn't silently reverted when the other side touched the same region for an unrelated reason.
- [**result-protection**](#/04-utility-skills/03-result-protection) — pins the specific numbers your paper depends on in drift tests verified red-green, so a refactor that slides a headline coefficient turns a passing build into a red test in the same run, not a referee's catch six months later.
- [**refactor-and-integrate**](#/04-utility-skills/04-refactor-and-integrate) — reworks a correct-but-rough branch to fit your project — match naming, reuse helpers, fix docs the diff contradicts — and prunes it to the minimum net diff, so a sprawling single-shot output lands as a PR a reviewer can read.
- [**report-in-markdown**](#/04-utility-skills/05-report-in-markdown) — the one style guide every agent follows for task files and reports — line-anchored source links, KaTeX-safe math, consistent tables — so citations are clickable and a display equation doesn't get silently swallowed into a paragraph.
- [**worktree-data-sync**](#/04-utility-skills/06-worktree-data-sync) — seeds, diffs, and reconciles the gitignored data git won't move between worktrees, so a parallel run doesn't start on an empty `Data/` directory or strand each branch's outputs with no record of what diverged.
- [**zotero-paper-reader**](#/04-utility-skills/07-zotero-paper-reader) — reads a paper from your actual Zotero library and cites it with the Better BibTeX key your `.bib` already uses, so the agent doesn't summarize the wrong web version or invent a citekey that dangles only at submission.
- [**mistral-pdf-to-markdown**](#/04-utility-skills/08-mistral-pdf-to-markdown) — converts a PDF through Mistral OCR into structured Markdown with extracted images, so a scan or two-column layout reconstructs in correct reading order instead of returning empty strings or columns spliced across the page.
