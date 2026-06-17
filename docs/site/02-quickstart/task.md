---
title: "Quickstart: Your First Analysis"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

This is the 20-minute walkthrough you run on day one. You will plan a tiny research analysis, watch superRA turn your request into a small task tree, run one task through its implementer–reviewer cycle, follow progress in the dashboard and the CLI, and read the results straight out of the task files. By the end you will have met the core mechanics — task tree, dispatch, review, status — by *doing* them, not by reading definitions.

The running example is a toy size-and-momentum sort on *simulated* equity returns: a small, public-safe analysis with no real data. Every command on this page was run as shown, and every screenshot is the dashboard rendering this exact toy project.

### What you need

You need three things: [Claude Code](https://docs.claude.com/en/docs/claude-code) (the primary path this tutorial follows), `git`, and either [`uv`](https://docs.astral.sh/uv/) or a Python 3 interpreter for the `superra` CLI. If you run Codex instead of Claude Code, the workflow is identical — only the install step and the way you invoke agents differ; see [Install & Set Up](#/04-how-to/01-install-and-set-up) for the Codex path.

### Install superRA

Install the plugin into Claude Code as a marketplace, then restart your session:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

That installs the skills, the implementer and reviewer agents, the lifecycle hooks, and the `superra` task-tree CLI. The full install reference — updating, the local-clone path for forking, and Codex — lives in [Install & Set Up](#/04-how-to/01-install-and-set-up).

### Start a project

Make an empty directory, turn it into a git repository, and open Claude Code there:

```bash
mkdir momentum-starter && cd momentum-starter
git init
claude
```

superRA writes its task tree into a `superRA/` directory at the repository root and expects to commit alongside your work, so a fresh git repo is the right starting point.

### Step 1 — Plan the analysis

Tell Claude what you want to study, in plain language, and ask it to plan. The phrase *make a plan* routes the request into superRA's PLAN phase:

```text
Using superRA, make a plan for a small toy analysis: simulate a monthly
equity panel, sort firms into size and momentum portfolios, and report the
long-short momentum spread. Keep it to a handful of tasks on simulated data.
```

Claude loads the `superplan` skill, explores the empty project, and proposes a small task tree — for this request, three tasks under one root. Planning is autonomous but it stops for you at one gate: before any code is written, it presents the proposed decomposition and waits for your approval. Read the objectives, then approve. The planner commits the task tree to `superRA/` so the structure is in git before execution starts.

You can see the tree any time from a terminal in the project. The filesystem *is* the task hierarchy — each task is a `task.md` file in its own directory:

```text
$ ./superRA/superra task tree
◐ Size and Momentum Sort on Simulated Equity Returns
  ● 01-simulate-panel: Simulate the monthly equity panel
  ◐ 02-build-portfolios: Construct size and momentum portfolios
  ○ 03-report-spread: Report average returns and the momentum spread
```

The glyphs are task status: `○` not started, `◐` in progress, `●` approved (reviewed and done). The root's `◐` is not set by hand — it is a *rollup* of its children, so a parent always reflects the state of the work beneath it. The three children form a chain: portfolios depend on the simulated panel, and the report depends on the portfolios. The full status model and the frontier idea below are explained in [The Task Tree](#/03-concepts/02-the-task-tree).

### Step 2 — Implement one task

Now run a task. Ask Claude to implement, and it loads the `superimplement` skill and picks up the first task whose dependencies are satisfied:

```text
Implement the next task according to the plan.
```

This is where superRA's central discipline shows up: every task runs through an **implementer–reviewer pair**. An implementer agent writes the code — here, the panel simulation — records what it found in the task's `## Results` section, and hands off. A separate reviewer agent then inspects the work independently and returns `APPROVE` or `REVISE`. Work only advances on `APPROVE`; a `REVISE` sends specific findings back to the implementer for a fix pass. Review is never skipped, however small the task looks. The roles and the review protocol are defined in [Roles & Review](#/03-concepts/03-roles-and-review).

When the first task is approved, its `task.md` carries the real outcome. Opening `superRA/01-simulate-panel/task.md` shows the results the implementer wrote and the reviewer checked:

```text
## Results

Simulated the panel in code/01_simulate_panel.py from seed 42 and wrote data/panel.csv.

- 12,000 firm-months: 200 firms × 60 months, no gaps.
- Mean monthly return -0.07%, SD 4.05% — the idiosyncratic noise dominates,
  with a persistent per-firm effect (SD 0.6%/month) that the momentum sort can pick up.
- log_size is a static per-firm draw (mean 6.02, SD 1.22), used as the size proxy in the next task.
```

### Step 3 — Watch progress

After the first task is approved, ask which task is ready next — the *frontier* is the set of leaf tasks whose dependencies are all satisfied:

```text
$ ./superRA/superra task frontier
  ◐ 02-build-portfolios: Construct size and momentum portfolios [depends: 01-simulate-panel]
```

For a visual view, launch the dashboard from a project terminal:

```bash
./superRA/superra dashboard
```

It opens a live, auto-updating dashboard in your browser, launches in the background, and exits on its own once idle. The default **Workspace** view shows the tree with status pills and the parent rollup. Here is this toy project mid-flight, with the panel task approved and the portfolio task in progress:

![Dashboard Workspace view of the toy project: the task tree in the sidebar with status pills, the root objective, and subtask cards.](attachments/dashboard-workspace.png)

The **Kanban** view shows the same tasks as a board, one column per status — the at-a-glance "what is where" across a larger tree:

![Dashboard Kanban view: tasks sorted into Not Started, In Progress, and Approved columns.](attachments/dashboard-kanban.png)

The dashboard also renders a dependency DAG and lets you share a branch snapshot through GitHub Actions. Those are covered in [See Your Work](#/04-how-to/04-see-your-work).

### Step 4 — Read the results

Results live in the task files, not in the chat. That is deliberate: a fresh agent — or you, next week — can reopen the repository and resume from the task tree and git history alone. Click any task in the dashboard to read its objective and results in place:

![Dashboard task detail for the panel task: the Objective and the Results the implementer wrote and the reviewer checked.](attachments/dashboard-task-detail.png)

The same content is a plain markdown file you can read or edit directly:

```bash
cat superRA/01-simulate-panel/task.md
```

Each task's `## Objective` records the intended work and its `## Results` records what happened. The full anatomy of a `task.md` — every frontmatter field and body section — is in [The Task File](#/05-reference/01-task-file).

### Finish, and where to go next

That is one task, end to end: you planned an analysis, ran a task through review, watched it on the dashboard, and read the result from the task file. Run the remaining two tasks the same way — *implement the next task according to the plan* — and the momentum spread report falls out at the end.

This walkthrough deliberately skipped the rest of the workflow. To go deeper:

- **Plan your own project.** Scoping a real analysis and writing good task objectives is its own skill — see [Plan a Project](#/04-how-to/02-plan-a-project).
- **Integrate and ship.** Protecting results against drift, syncing with a base branch, and opening a PR are the INTEGRATE phase — see [Integrate & Ship](#/04-how-to/05-integrate-and-ship).
- **Understand the model.** For the *why* behind the three phases and the re-entry loop, read [The Workflow](#/03-concepts/01-the-workflow).
- **See it on a real tree.** The [Showcase](#/06-showcase) embeds a full task-tree export — including superRA's own development tree — so you can explore the UI on real work.
</content>
