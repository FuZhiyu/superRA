---
title: "Utility Skills"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Utility skills are domain-neutral tools the workflow and agents compose as the situation needs — and several are useful to you directly in an interactive session. They are superRA's "mechanisms over contingency trees" layer: reusable pieces assembled for the work at hand rather than a fixed pipeline. Where a [domain skill](#/03-domain-skills) supplies discipline for a kind of research, a utility skill supplies a capability that cuts across all of them.

The sections below introduce each one with the capability it gives you. Each links to its `SKILL.md` as the authority for the details; the authoritative grouping lives in [CATEGORIES.md](skills/CATEGORIES.md).

## The task tree — `task-tree`

This is the flagship, and the thing you are looking at right now: this documentation site is itself a task tree rendered by the same dashboard.

The core idea is **the filesystem is the task hierarchy.** Every task is a directory with a `task.md` holding its objective and results; nesting a directory nests the task; a task depends only on its siblings. From that committed structure the tooling computes everything else: status that rolls up from children to parents, the *frontier* of tasks ready to work next, a dependency DAG, and a live dashboard with tree, DAG, and kanban views that updates as work progresses. Because the whole project state lives in files you can read and git can track, a fresh agent — or you, a week later — can open the repo and resume from the files alone. See [`task-tree/SKILL.md`](skills/task-tree/SKILL.md).

## Intent-aware merging — `semantic-merge`

When you sync a branch with its base, this resolves conflicts by understanding what each side *meant* rather than picking ours or theirs blindly. It reads the intent behind both changes, escalates to you when a resolution would change meaning, and sweeps for references that went stale across the merge — so the merged result is coherent, not just conflict-free. See [`semantic-merge/SKILL.md`](skills/semantic-merge/SKILL.md).

## Protecting results — `result-protection`

Findings drift. A refactor, a re-run, or a future edit can quietly change a number that a paper depends on. This skill guards key results with drift or regression tests: it captures the result you care about and fails loudly if a later change moves it, so a silent regression becomes a visible test failure. See [`result-protection/SKILL.md`](skills/result-protection/SKILL.md).

## Fitting the codebase — `refactor-and-integrate`

Single-shot agent output rarely matches the surrounding code. This skill carries the codebase-coherence tools the integration phase uses: fitting local conventions, reusing existing utilities instead of duplicating them, and pruning a change down to the minimum net diff so what lands is a clean, reviewable PR rather than a pile of one-off scripts. See [`refactor-and-integrate/SKILL.md`](skills/refactor-and-integrate/SKILL.md).

## Markdown reports — `report-in-markdown`

The shared style guide every agent follows when it writes a task file or a report — source-file citations as line-anchored links, LaTeX math that renders in the dashboard, and consistent tables. It is why task results across the tree read consistently rather than each agent inventing its own conventions. See [`report-in-markdown/SKILL.md`](skills/report-in-markdown/SKILL.md).

## Worktree data sync — `worktree-data-sync`

When you run tasks in parallel across multiple git worktrees, the code is versioned but the data usually is not. This skill seeds a new worktree's data, diffs data between worktrees, and reconciles changes after parallel work — keeping the non-git-controlled files in sync without committing large data into the repo. See [`worktree-data-sync/SKILL.md`](skills/worktree-data-sync/SKILL.md).

## Standalone helpers

These two are user-invocable on their own and are not part of the core workflow loop — reach for them directly when you need them.

- **`zotero-paper-reader`** — read and analyze papers from your Zotero library and generate citations from it: search, PDF retrieval, section-by-section analysis, BibTeX export, and inserting `\cite`/`[@key]` into a draft. See [`zotero-paper-reader/SKILL.md`](skills/zotero-paper-reader/SKILL.md).
- **`mistral-pdf-to-markdown`** — convert a PDF to Markdown with image extraction via the Mistral OCR API, useful for scanned or complex-layout documents. It is the conversion step behind the Zotero reader and works standalone too. See [`mistral-pdf-to-markdown/SKILL.md`](skills/mistral-pdf-to-markdown/SKILL.md).
