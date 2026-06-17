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

Each section below leads with what the skill gives you, then the moment you would reach for it. Each links to its `SKILL.md` as the authority for the details; the grouping lives in [CATEGORIES.md](skills/CATEGORIES.md).

## The task tree — task-tree

You get a live view of your whole project — a tree with rollup status, the set of tasks ready to work next, a dependency DAG, and a kanban board — all computed from plain files git tracks. The idea underneath is that the filesystem is the task hierarchy: every task is a directory with a `task.md` holding its objective and results, nesting a directory nests the task, and a task depends only on its siblings. From that committed structure the tooling derives everything else — status that rolls up from children to parents, the dispatchable frontier, the DAG, and a dashboard that updates as work progresses. Reach for it once a project grows past a handful of moving parts and you start losing the thread of which task is done, which is ready next, and what a finished one actually found. Because the whole state lives in files, a fresh agent — or you, a week later — opens the repo and resumes from the files alone. See [`task-tree`](skills/task-tree/SKILL.md).

## Intent-aware merging — semantic-merge

You get conflict resolution that turns on what each side *meant* rather than which lines won. Reach for it when you sync your branch with main, rebase, or cherry-pick and `git` drops conflict markers into a dozen files — resolving them by hand, picking ours or theirs line by line, is how a careful change quietly gets reverted. `semantic-merge` reads the intent behind both changes, synthesizes where both are valid, escalates to you when a resolution would change what the branch means, and sweeps for references that went stale across the merge — so what lands is coherent, not just free of markers. See [`semantic-merge`](skills/semantic-merge/SKILL.md).

## Protecting results — result-protection

You get drift or regression tests that pin the numbers your paper depends on and fail loudly when a later change moves them. Reach for it when a result you care about — a coefficient from a regression three weeks ago, a headline spread — could be shifted by a refactor, a re-run on fresh data, or an edit to shared code without anyone noticing until a referee does. The skill captures the key number and turns a silent regression into a visible test failure. It guards the results you confirm as key, not every intermediate number. See [`result-protection`](skills/result-protection/SKILL.md).

## Fitting the codebase — refactor-and-integrate

You get a correct-but-rough analysis reworked into a change that fits your project: local conventions matched, helpers you already have reused instead of re-implemented, stale project docs updated, and the diff pruned to the minimum net change so what lands is a clean, reviewable PR rather than a pile of one-off scripts. Reach for it when single-shot agent output is right but does not match the surrounding code. The integration phase leans on it most, but you can invoke it any time you want a branch made codebase-coherent before review. See [`refactor-and-integrate`](skills/refactor-and-integrate/SKILL.md).

## Markdown reports — report-in-markdown

You get task files and reports that read alike across the whole tree instead of each agent inventing its own conventions: source files cited as line-anchored links you can follow to the exact line, LaTeX math that renders in the dashboard, consistent tables. It is the shared style guide every agent follows when it writes a task file or a status report, and you can load it directly for any markdown you want held to the same standard. See [`report-in-markdown`](skills/report-in-markdown/SKILL.md).

## Worktree data sync — worktree-data-sync

You get the non-git-controlled files kept in sync when you run tasks in parallel across several git worktrees. The code is versioned and travels with each worktree, but the data usually is not — a new worktree starts empty, and parallel runs leave each one's data files out of step. The skill works in three modes. It **seeds** a fresh worktree with the data it needs, copying or symlinking only the files that are missing and never overwriting what is already there. It **diffs** two worktrees, reporting which data files are new or modified between them. And it **applies** selected changes from one worktree into another to reconcile after parallel work — either overwriting in place, or copying alongside with a suffix so neither version is lost. It figures out which files count as data on its own — gitignored paths and symlinks that point outside the repo — so you don't enumerate them, and there is no separate cleanup step: deleting a worktree removes its seeded data while the source is left untouched. The exact CLI, flags, and symlink-versus-copy controls are in the skill reference. See [`worktree-data-sync`](skills/worktree-data-sync/SKILL.md).

## Reading your library — zotero-paper-reader

You get a way to read and analyze a paper straight from your Zotero library and pull its citations into a draft: it searches the library by metadata or full text, retrieves and analyzes the PDF section by section, exports BibTeX, and inserts `\cite`/`[@key]` where you want them. Reach for it whenever you want to work with a paper you already have in Zotero. See [`zotero-paper-reader`](skills/zotero-paper-reader/SKILL.md).

## PDF to Markdown — mistral-pdf-to-markdown

You get a PDF converted to clean Markdown with image extraction via the Mistral OCR API, which handles the scanned or complex-layout documents that plain text extraction mangles. It is the conversion step behind the Zotero reader and works standalone too. See [`mistral-pdf-to-markdown`](skills/mistral-pdf-to-markdown/SKILL.md).
</content>
