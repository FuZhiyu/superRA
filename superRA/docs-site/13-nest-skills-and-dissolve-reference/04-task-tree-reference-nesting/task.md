---
title: "Build the task-tree Detail Subpages: task-file / CLI / status / dashboard"
status: not-started
depends_on: 
  - 03-utility-skills

tags: []
created: 2026-06-17
---

## Objective

Build the detail subpages under `04-utility-skills/01-task-tree/` (the high-level page is owned by task `03`). These are what the reader descends to for the operational detail the skill page deliberately omits. Everything here is written for the **researcher using the tooling** — the commands they run, the dashboard features they click — not for the agent.

**Relocate three existing Reference pages** as children, preserving their prose and adding the user lens:

- `01-task-file` ← from `docs/site/05-reference/01-task-file`: `task.md` anatomy — frontmatter fields, body sections, status lifecycle pointer. Keep it a human orientation that links to `task-tree/references/task-file-contract.md` as authority.
- `02-cli-commands` ← from `docs/site/05-reference/02-cli-commands`: the `superra` command surface a researcher runs day to day — read the tree, frontier, DAG, `task read`, create/move, **comments** (`task comment list`/`resolve`), diagnostics. Links to `task-tree/references/commands.md`.
- `03-status-and-frontier` ← from `docs/site/05-reference/03-status-and-frontier`: status enum, lifecycle, rollup, frontier computation.

Move the directories (e.g. `./superRA/superra task move --root docs/site …`, or `git mv` plus a manual link fix); repoint each relocated page's own internal `#/…` links to the new sibling/parent paths. Site-wide repointing of links *into* these pages is task `06`'s job, not this task's.

**Author a new `04-dashboard` page** — the user-facing dashboard and collaboration capabilities, which the current docs scatter or omit. Cover, from the researcher's point of view:

- The live dashboard — tree, DAG, and kanban views that update as work progresses (`./superRA/superra dashboard`).
- Client-side search across tasks and pages.
- **Static export** — building a shareable, self-contained HTML site from a task tree (the doc-mode export; note that this very documentation site is one such export), so a researcher can hand a collaborator a browsable snapshot of project state.
- **Task comments** — pinning a comment to a task and resolving it, and that comments surface inline in `task read` and on the dashboard — the human-in-the-loop steering channel.
- **Worktrees** — running tasks in parallel across git worktrees and keeping their data in sync; point to the [`worktree-data-sync`](#/04-utility-skills/06-worktree-data-sync) page rather than re-explaining it. Mention the dashboard version/worktree switcher only if it is actually built (`superRA/docs-site/10-version-switcher` is currently postponed — do not document an unbuilt feature).

Link the `task-tree` skill page (task `03`) down to these four children, and the `task-tree/SKILL.md` and its references as authority. Do not duplicate agent-facing behavior (authority-not-paraphrase).

Prose quality: load `writing`; user-facing framing throughout; no AI-flavored prose.

Validation: the four children render under `01-task-tree`; relocated pages keep their teaching; the dashboard page covers export, comments, and worktrees from the user's side; no unbuilt feature is documented as shipping.

## Results

