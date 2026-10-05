---
title: "The Dashboard"
status: not-started
depends_on:  []
---

## Objective

The dashboard is a live browser view of your task tree that refreshes as agents work. Ask the agent to bring it up:

```text
Open the superRA dashboard and point me at what is in review.
```

## Two views of the same tree

- **Tree** — the task hierarchy, for reading task bodies and results.
- **Graph** — each task as a card holding its [reproduction steps](#/04-utility-skills/09-reproducibility). Solid arrows are files passed between steps; dashed arrows are `depends_on` prerequisites. Expand a task to show its steps and child tasks.

## Step cards show whether each result is current

Each step card shows its state (`fresh`, `stale`, `missing`, `failed`, or `unverified`) and its last run time; each task card and Tree row counts its steps per state. This state is separate from workflow status, so an `approved` task can hold a stale step. A task whose `## Reproduction` section has an error is outlined in red, linking the finding.

- **Border, glyph, and label: the state a build acts on.** A step stale only because of its producer reads `stale · upstream`.
- **Fill: the step's own evidence.**
  - Tinted: its own state, so the tint marks where staleness starts.
  - Empty: inherited from upstream; the step reruns only if rebuilding its producers changes its inputs.
  - Hatched: some of its files are online-only here (for example in Dropbox or iCloud, not downloaded), so it reads `unverified`.

Hover a step that is not fresh to see why; select it for its inputs, outputs, last run, and any acceptance reason.

## Build from the graph

On the live dashboard, each task and step card has a **Build** button. Its menu builds the selection with the producers it reads, only the selection, or a forced rerun, and shows the `superra repro build` command and a time estimate from past runs. A build that would read a file not on this machine runs nothing and lists the files.

## Open and preview files

- **On your own machine:** the **Open** buttons and file links hand a file to its default application; the header **VS Code** button opens the task's `task.md` in VS Code. Set `SUPERRA_EDITOR` (for example to `cursor`) to use a VS Code fork.
- **Anywhere on the live page:** hover a file link for its size and a preview. A browser on another machine gets no Open buttons; file links open in the reading pane instead.

## Steer with comments

Pin a note — a correction, question, or constraint — to a block of a task to steer it without editing the objective. It shows on the dashboard and inline in [`task read`](#/04-utility-skills/01-task-tree/02-cli-commands), so the next agent on that task sees it. Resolve it once addressed. Editing the block a comment is pinned to leaves the comment orphaned, shown with its original text.

## Share a snapshot

```text
Export the dashboard to a file I can send.
```

The export is one self-contained HTML file — tree, task bodies, math, images, and graph — that opens in any browser with no superRA install, server, or repo. This documentation site is one. It has no Build or Open controls.

- **Everything in a task is in the export.** On a public project keep subject IDs, private group names, query results, and internal paths out of task bodies.
- **To publish one per push,** `./superRA/superra dashboard artifact setup` installs a GitHub Actions workflow that uploads each branch's export as a downloadable artifact.

## Parallel worktrees share one server

One server shows every git worktree of the repo, one per tab. Data usually is not versioned per worktree; keep it in step with [`worktree-data-sync`](#/04-utility-skills/06-worktree-data-sync).

## Commands

```bash
./superRA/superra dashboard                                  # start the live view in the background, or reuse a running one
./superRA/superra dashboard stop                             # shut it down
./superRA/superra dashboard export --output dashboard.html   # write a self-contained snapshot
```

Serving, ports, and export internals are in the [`task-tree`](skills/task-tree/SKILL.md) skill and its [internals reference](skills/task-tree/references/internals.md).
