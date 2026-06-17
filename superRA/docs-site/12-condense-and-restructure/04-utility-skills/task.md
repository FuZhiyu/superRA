---
title: "Author the Utility Skills Page"
status: approved
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Author `docs/site/04-utility-skills/task.md`: introduce superRA's utility skills one by one, each with its **high-level design idea**, so an adopting researcher knows what reusable, domain-neutral tools exist and what each gives them.

Open with the design idea: utility skills are domain-agnostic tools the workflow and agents compose as needed — and several are directly useful to a researcher standalone. They are the "mechanisms over contingency trees" layer: reusable pieces assembled for the situation at hand.

Then one short section per utility skill, stated as what it does for the user:

- **`task-tree`** — the filesystem-as-task-hierarchy tooling: `task.md` per task, sibling dependencies, status rollup, frontier, DAG, and the live dashboard. (This is the flagship; give it the most room.)
- **`semantic-merge`** — intent-aware branch integration: resolves conflicts by understanding what each side meant rather than a blind ours/theirs merge.
- **`result-protection`** — drift/regression tests that guard key results from silently changing later.
- **`refactor-and-integrate`** — codebase-coherence tools: convention fit, utility reuse, PR-friendly minimum-diff integration.
- **`report-in-markdown`** — the markdown style guide agents follow when writing task files and reports.
- **`worktree-data-sync`** — syncing non-git data between worktrees for parallel work.
- **`zotero-paper-reader`** / **`mistral-pdf-to-markdown`** — user-invocable standalone helpers (Zotero reading + citations; PDF→markdown). Note they are standalone, not part of the core workflow loop.

Each skill gets a framing + design idea + a link to its `SKILL.md` as the authority — thin, no paraphrase. No internal load-order or who-calls-what mechanics (contributor detail).

## Planner Guidance

`skills/CATEGORIES.md §Utility` is the source of truth for membership and one-line purpose. Decide an ordering that serves a reader (flagship `task-tree` first; standalone helpers last) rather than the alphabetical CATEGORIES order.

## Results

Authored [docs/site/04-utility-skills/task.md](../../../docs/site/04-utility-skills/task.md). The page opens with the design idea — utility skills are the domain-neutral "mechanisms over contingency trees" layer the workflow and agents compose as needed, several usable standalone — then carries one thin section per skill (framing + capability + link to its `SKILL.md` as the authority, no paraphrase), reader-ordered rather than alphabetical.

Ordering and membership confirmed against [skills/CATEGORIES.md §Utility](../../../skills/CATEGORIES.md):

- **`task-tree`** — flagship, given the most room: filesystem-as-task-hierarchy, `task.md` per task, sibling deps, status rollup, frontier, DAG, live dashboard. [skills/task-tree/SKILL.md](../../../skills/task-tree/SKILL.md).
- **`semantic-merge`** — intent-aware merging vs blind ours/theirs. [skills/semantic-merge/SKILL.md](../../../skills/semantic-merge/SKILL.md).
- **`result-protection`** — drift/regression tests guarding key results. [skills/result-protection/SKILL.md](../../../skills/result-protection/SKILL.md).
- **`refactor-and-integrate`** — codebase coherence, convention fit, minimum net diff. [skills/refactor-and-integrate/SKILL.md](../../../skills/refactor-and-integrate/SKILL.md).
- **`report-in-markdown`** — shared markdown style guide. [skills/report-in-markdown/SKILL.md](../../../skills/report-in-markdown/SKILL.md).
- **`worktree-data-sync`** — non-git data sync across worktrees. [skills/worktree-data-sync/SKILL.md](../../../skills/worktree-data-sync/SKILL.md).
- Standalone helpers last, flagged as outside the core loop: **`zotero-paper-reader`** and **`mistral-pdf-to-markdown`**. [zotero](../../../skills/zotero-paper-reader/SKILL.md), [mistral](../../../skills/mistral-pdf-to-markdown/SKILL.md).

**Authoring-contract compliance.** Frontmatter `title` only; cross-page links as `#/<path>` hash links (`#/03-domain-skills` back-link present); skill-file citations as repo-relative path targets the export rebases via `--repo-file-base`, never hardcoded GitHub URLs. One paragraph per line.

**Build verification.** `bash docs/build_site.sh /tmp/superra_site_check` exited 0 with no errors; the page content rendered into `index.html` ("filesystem is the task hierarchy" present), all eight `SKILL.md`/`CATEGORIES.md` links embed repo-relative for client-side rebasing. `report-in-markdown/scripts/check_markdown.py` reports the page clean.
