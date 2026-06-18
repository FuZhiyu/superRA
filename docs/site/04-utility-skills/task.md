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

- [**task-tree**](#/04-utility-skills/01-task-tree) — a live view of your whole project computed from the files git tracks: the tree with rollup status, the tasks ready to work next, the dependency DAG, and the dashboard.
- [**semantic-merge**](#/04-utility-skills/02-semantic-merge) — conflict resolution that turns on what each side *meant* rather than which lines won, for syncing a branch, rebasing, or cherry-picking without silently reverting a change.
- [**result-protection**](#/04-utility-skills/03-result-protection) — drift or regression tests that pin the numbers your paper depends on and fail loudly when a later change moves them.
- [**refactor-and-integrate**](#/04-utility-skills/04-refactor-and-integrate) — a correct-but-rough analysis reworked to fit your project: local conventions matched, helpers reused, stale docs updated, the diff pruned to a clean PR.
- [**report-in-markdown**](#/04-utility-skills/05-report-in-markdown) — the shared style guide every agent follows when it writes a task file or report: line-anchored source links, rendering math, consistent tables.
- [**worktree-data-sync**](#/04-utility-skills/06-worktree-data-sync) — the non-git-controlled data files kept in sync when you run tasks in parallel across several git worktrees.
- [**zotero-paper-reader**](#/04-utility-skills/07-zotero-paper-reader) — read and analyze a paper straight from your Zotero library and pull its citations into a draft.
- [**mistral-pdf-to-markdown**](#/04-utility-skills/08-mistral-pdf-to-markdown) — a PDF converted to clean Markdown with image extraction via the Mistral OCR API, for scanned or complex-layout documents.
