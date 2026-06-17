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

### Prerequisite

Basic knowledge of git is absolutely necessary (in my view, not only for this plugin but for use agents at all). Knowledge of branching and merging is highly recommended. 



<!-- we support claude code or codex -->
You need three things: [Claude Code](https://docs.claude.com/en/docs/claude-code) or [Codex], `git`, and either [`uv`](https://docs.astral.sh/uv/) or a Python 3 interpreter for the `superra` CLI. If you run Codex instead of Claude Code, the workflow is identical — only the install step and the way you invoke agents differ; see [Install & Set Up](#/04-how-to/01-install-and-set-up) for the Codex path.

<!-- are you sure python3 is sufficient? i thought to sort through the dependency we need uv?  -->

### Install superRA

In this guide, we use claude code for narrative though they equally apply to codex. 

Install the plugin into Claude Code as a marketplace, then restart your session:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

<!-- add codex instruction -->

The full install reference — updating, the local-clone path for forking, and Codex — lives in [Install & Set Up](#/04-how-to/01-install-and-set-up).

### Set up a project

Take an existing project or some ongoing work, make sure all existing changes are commited, and start the Claude Code and ask:

``use superRA and retroactively create task trees for [tasks I'm working on|xxxx], and show me the dashboard"

The magical word to invoke superra skill is `superra`---a hook will ensure once you say the spell, agents will follow the superra. 

### A Typical Workflow

### Superplan

Tell Claude what you want to work on, in plain language, and ask it to plan. You don't need to be in the Plan mode in codex/claude. To ensure it follows the superra workflow, you can use the trigger phrase `superplan`

```text
Using superRA, make a plan for a small toy analysis: simulate a monthly
equity panel, sort firms into size and momentum portfolios, and report the
long-short momentum spread. Keep it to a handful of tasks on simulated data.
```

Claude loads the `superplan` skill, explores the existing project, and proposes a small task tree — for this request, three tasks under one root. Planning is autonomous but it stops for you at one gate: before any code is written, it presents the proposed decomposition and waits for your approval. Read the objectives, then approve. The planner commits the task tree to `superRA/` so the structure is in git before execution starts.

<!-- explain how the tasks are stored in high level. do not explain the cli here. cli is for agents. explain the dashboard instead. explain how to show the dashboard superra/superra dashboard or ask agents to show you-->

<!-- You can see the tree any time from a terminal in the project. The filesystem *is* the task hierarchy — each task is a `task.md` file in its own directory: -->

<!-- make them nested tasks under the current page and provide the  -->

```text
$ ./superRA/superra task tree
◐ Size and Momentum Sort on Simulated Equity Returns
  ● 01-simulate-panel: Simulate the monthly equity panel
  ◐ 02-build-portfolios: Construct size and momentum portfolios
  ○ 03-report-spread: Report average returns and the momentum spread
```

The full task-tree desig are explained in [The Task Tree](#/03-concepts/02-the-task-tree).

### Superimplement

Now run a task. Ask Claude to `superimplement`

```text
superImplement task @...
```

This is where superRA's central discipline shows up: every task runs through an **implementer–reviewer pair**. An implementer agent writes the code — here, the panel simulation — records what it found in the task's `## Results` section, and hands off. A separate reviewer agent then inspects the work independently and returns `APPROVE` or `REVISE`. Work only advances on `APPROVE`; a `REVISE` sends specific findings back to the implementer for a fix pass. Review is never skipped, however small the task looks. The roles and the review protocol are defined in [Roles & Review](#/03-concepts/03-roles-and-review).

The dashboard will be real-time updated as the agents are doing their work. 


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

<!-- this should be the deafult mode for monitoring rather than the markdown files-->
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
<!-- 3 and 4 should be merged. -->
Results live in the task files, not in the chat. That is deliberate: a fresh agent — or you, next week — can reopen the repository and resume from the task tree and git history alone. Click any task in the dashboard to read its objective and results in place:

![Dashboard task detail for the panel task: the Objective and the Results the implementer wrote and the reviewer checked.](attachments/dashboard-task-detail.png)

The same content is a plain markdown file you can read or edit directly:

```bash
cat superRA/01-simulate-panel/task.md
```

Each task's `## Objective` records the intended work and its `## Results` records what happened. The full anatomy of a `task.md` — every frontmatter field and body section — is in [The Task File](#/05-reference/01-task-file).

### Superintegrate





### Skills