---
title: "Build the task-tree Detail Subpages: task-file / CLI / status / dashboard"
status: approved
depends_on: 
  - 03-utility-skills

tags: []
created: 2026-06-17
---

## Objective

Build the detail subpages under `04-utility-skills/01-task-tree/` (the high-level page is owned by task `03`). These are what the reader descends to for the operational detail the skill page deliberately omits. Everything here is written for the **researcher using the tooling** — the commands they run, the dashboard features they click — not for the agent.

**Relocate three existing Reference pages** as children, then **rewrite each to be concise and user-oriented** — the current pages were written reference-style; trim them to what a researcher needs to do the thing, lead with the user's task, and push exhaustive field-by-field detail to the linked authority rather than reproducing it:

- `01-task-file` ← from `docs/site/05-reference/01-task-file`: `task.md` anatomy — the fields a researcher reads and edits, the body sections, status lifecycle pointer. A human orientation that links to `task-tree/references/task-file-contract.md` as authority; do not transcribe the full field contract.
- `02-cli-commands` ← from `docs/site/05-reference/02-cli-commands`: the `superra` command surface a researcher runs day to day — read the tree, frontier, DAG, `task read`, create/move, **comments** (`task comment list`/`resolve`), diagnostics. Lead with the handful of commands used constantly; link to `task-tree/references/commands.md` for the full surface.
- `03-status-and-frontier` ← from `docs/site/05-reference/03-status-and-frontier`: status enum, lifecycle, rollup, frontier computation — framed as what the researcher sees and decides, not an internal state-machine spec.

Move the directories (e.g. `./superRA/superra task move --root docs/site …`, or `git mv` plus a manual link fix); repoint each relocated page's own internal `#/…` links to the new sibling/parent paths. Preserve every genuinely user-facing fact through the rewrite — concise means tighter and better-targeted, not lossy. Site-wide repointing of links *into* these pages is task `07`'s job, not this task's.

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

Built the four detail subpages under [`04-utility-skills/01-task-tree/`](#/04-utility-skills/01-task-tree). All four render in a doc-mode export and every cross-page link resolves to a node path that exists in the tree (verified by exporting `docs/site` and grepping the output).

**Relocated and rewrote three pages.** Moved with `git mv` (doc nodes carry no real `depends_on`, so a raw move plus manual link fix is correct), then rewrote each from reference-style tables toward a lead-with-the-task orientation that pushes the exhaustive contract to the linked authority:

- [`01-task-file`](#/04-utility-skills/01-task-tree/01-task-file) (was `05-reference/01-task-file`) — now opens on the three places a researcher actually works (frontmatter, `## Objective`, `## Results`), describes the body sections by ownership, and keeps the minimal-leaf example; the full key-by-key contract is a pointer to `task-file-contract.md`. Repointed its internal status link from `#/05-reference/03-status-and-frontier` to the new sibling path.
- [`02-cli-commands`](#/04-utility-skills/01-task-tree/02-cli-commands) (was `05-reference/02-cli-commands`) — leads with the three constant commands (`task tree` / `task frontier` / `task read`), then create/move, comments, and diagnostics; full surface points to `commands.md`. Corrected the dashboard invocation to `./superRA/superra dashboard` (the page had carried `task dashboard` framing in passing) and links to the new dashboard page.
- [`03-status-and-frontier`](#/04-utility-skills/01-task-tree/03-status-and-frontier) (was `05-reference/03-status-and-frontier`) — reframed as what the researcher sees and decides: the two statuses that are theirs to set (`archived`/`postponed`) vs. the dispatch-cycle ones agents drive, rollup stated as a consequence, frontier as the payoff. Authority pointer to `task-file-contract.md` retained.

No relocated page lost a user-facing fact; the status enum, lifecycle, rollup rules, frontier definition, command surface, comments, and field/section anatomy all survive in tighter form.

**Authored the new dashboard page.** [`04-dashboard`](#/04-utility-skills/01-task-tree/04-dashboard) covers the live tree/DAG/kanban views with SSE auto-refresh, client-side search, the self-contained static export (`./superRA/superra dashboard export --output dashboard.html`, noting this site is one such export), task comments as the human-in-the-loop steering channel, and parallel worktrees (pointing to [`worktree-data-sync`](#/04-utility-skills/06-worktree-data-sync) rather than re-explaining). The export-sharing data-hygiene fact from the soon-to-be-dropped FAQ folds in here — "treat the snapshot like the repo it came from; keep real IDs/paths out of task bodies on a public project" — so task `05` can drop the standalone FAQ with that fact already homed. Did not document the docs branch/version switcher (`10-version-switcher` is postponed); the live dashboard's per-worktree resolution, which is built, is described instead.

**Parent linkage already satisfied.** The `task-tree` skill page (`04-utility-skills/01-task-tree`, owned by approved task `03`) already links down to all four children at their final nested paths, so no edit to that page was needed.

**Deviation from guidance:** the objective suggested `./superRA/superra task move --root docs/site …` as one move option; I used `git mv` (the objective's stated alternative) because doc nodes have no `depends_on` edges or inbound `#/…` links from siblings that the move command would need to carry, so the simpler raw move plus the one manual link fix is sufficient and lower-risk.

Verification: `report-in-markdown` self-diagnose clean on all four pages; doc-mode export of `docs/site` succeeds and contains all four page titles, the dashboard page's three new section headings, and every referenced node path.
