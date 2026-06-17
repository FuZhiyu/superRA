---
title: "Quickstart: Your First Workflow"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

This is the walkthrough you run on day one. You will install superRA, point it at a project, and run one piece of work through a full PLAN → IMPLEMENT → INTEGRATE cycle — planning a small task tree, running a task through its implementer–reviewer pair, watching progress and reading results in the dashboard, and integrating the result. Every core idea — the task tree, the dashboard, adversarial review, status, integration — is introduced inline as you reach it, so by the end you have met the mechanics by *doing* them, not by reading definitions first.

The running example is a toy size-and-momentum sort on *simulated* equity returns: a small, public-safe analysis with no real data. Every command on this page was run as shown, and every screenshot is the dashboard rendering this exact toy project.

### Prerequisite

You need to be comfortable with git. This is a real prerequisite — not just for superRA, but for working with coding agents at all: the agent commits as it works, and you read and steer through the resulting history. Familiarity with branching and merging is strongly recommended, since superRA does its integration on a branch and merges back when the work is done.

superRA runs on **[Claude Code](https://docs.claude.com/en/docs/claude-code) or [Codex](https://developers.openai.com/codex/cli)**. This walkthrough uses Claude Code, but everything applies equally to Codex — only the install step and the way you invoke agents differ (see the [Codex install notes](docs/README.codex.md)). You also need `git` and either [`uv`](https://docs.astral.sh/uv/) or a Python 3 interpreter to run the `superra` CLI. The CLI scripts are bundled as PEP 723 self-contained scripts run via `uv run --script`, so **`uv` is the recommended path**; the core is stdlib-only, so a plain `python3` works as a fallback if you do not have `uv`. You will rarely call the CLI by hand — it is mostly the agents' interface to the tree — but the dashboard runs through it.

### Install + set up a project

Install the plugin into Claude Code as a marketplace, then restart your session:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

On Codex the install has a second piece — the named agents — and is covered in the [Codex install notes](docs/README.codex.md). The full install reference (updating, the local-clone path for forking) lives in the project [README](README.md).

The fastest way to feel superRA is to point it at work you already have. Take an existing project or some ongoing work, make sure everything is committed, start Claude Code, and ask it something like:

```text
Use superRA and retroactively create task trees for [what I'm working on],
and show me the dashboard.
```

The magic word that invokes the workflow is **`superra`**: once you say it, the agents follow the superRA workflow rather than improvising. That is all you need to know about the trigger — saying `superra` (or one of the phase words below) is what turns it on.

### A typical workflow

The rest of this page walks one piece of work end to end through the three phases. Below, the running example starts a fresh toy analysis rather than adopting existing work, so you can see planning from scratch.

#### Superplan

Tell Claude what you want to work on, in plain language, and ask it to plan. You do not need your harness's plan mode; the trigger phrase `superplan` is enough to put it on the planning track:

```text
Using superRA, superplan a small toy analysis: simulate a monthly equity
panel, sort firms into size and momentum portfolios, and report the long-short
momentum spread. Keep it to a handful of tasks on simulated data.
```

Claude loads the `superplan` skill, explores the project, and proposes a small **task tree** — for this request, three tasks under one root. The task tree is where a superRA project keeps its state: instead of holding the plan in one agent's context window, superRA writes it as a committed tree of small `task.md` files — one directory per unit of work — that the agents read and write as they go. Because the state is plain files in git, a fresh agent session or you next week can reopen the repo and see exactly what was planned, done, and left.

Planning is autonomous but stops for you at one gate: before any code is written, the planner presents the proposed decomposition and waits for your approval. Read the objectives, then approve; the planner commits the tree to `superRA/` so the structure is in git before execution starts. The full design of how task trees are scoped and decomposed is in [superplan](skills/superplan/SKILL.md).

You read the tree not through the CLI — that is the agents' interface — but through the **dashboard**, the human view of the same committed files. Ask the agent to show it, or launch it yourself from a project terminal:

```bash
./superRA/superra dashboard
```

It opens a live, auto-updating dashboard in your browser, runs in the background, and exits on its own once idle. The default **Workspace** view shows the tree with status pills and the parent rollup. Here is this toy project right after planning, with the three tasks laid out under one root:

![Dashboard Workspace view of the toy project: the task tree in the sidebar with status pills, the root objective, and subtask cards.](attachments/dashboard-workspace.png)

#### Superimplement

Now run a task. Ask Claude to `superimplement`:

```text
superimplement the next task.
```

This is where superRA's central discipline shows up: every task runs through an **implementer–reviewer pair**. An implementer agent does the work — here, the panel simulation — records what it found in the task's `## Results` section, and hands off. A separate reviewer agent then inspects the committed result *independently* — the actual files and diff, not the implementer's summary — and returns one of two verdicts. **APPROVE** advances the task; **REVISE** sends numbered, specific findings back to the implementer for a fix pass. Work never advances past a `REVISE`, however small the task looks — review is not skippable.

The reviewer is adversarial by design: its job is to find the problems the implementer missed, not to rubber-stamp the work. An agent reviewing its own work shares its own blind spots — if it dropped half the sample, it will report that everything looks fine. A fresh reviewer with a different prompt and an explicit mandate to look for failure catches the silent bad merge, the wrong aggregation, the unreproducible output. The result is that whatever advances through a superRA project has survived a second, hostile read at every step. The full role behavior is in the [implementer](agents/implementer.md) and [reviewer](agents/reviewer.md) specs.

The implementer writes its findings straight into the task file, so the panel task's `## Results` ends up reading like this:

```text
## Results

Simulated the panel in code/01_simulate_panel.py from seed 42 and wrote data/panel.csv.

- 12,000 firm-months: 200 firms × 60 months, no gaps.
- Mean monthly return -0.07%, SD 4.05% — the idiosyncratic noise dominates,
  with a persistent per-firm effect (SD 0.6%/month) that the momentum sort can pick up.
- log_size is a static per-firm draw (mean 6.02, SD 1.22), used as the size proxy in the next task.
```

#### Watch progress and read results

The dashboard auto-updates in real time as the agents work, so it is the default way to both monitor the run and read what came out of it — you rarely need the chat or the files directly. As one task is approved, the next becomes ready: superRA tracks the **frontier**, the set of tasks whose dependencies are all satisfied, and dispatches from it. The **Kanban** view shows every task as a card sorted into a column by status — the at-a-glance "what is where" across a whole tree:

![Dashboard Kanban view: tasks sorted into Not Started, In Progress, and Approved columns.](attachments/dashboard-kanban.png)

Click any task to read its objective and results in place — the same `## Objective` the implementer worked to and the `## Results` it wrote and the reviewer checked:

![Dashboard task detail for the panel task: the Objective and the Results the implementer wrote and the reviewer checked.](attachments/dashboard-task-detail.png)

Because the results live in the committed task files rather than the chat, they are the durable handoff: nothing of value sits in a context window that will be lost. If you ever want the raw file, each task is a plain markdown file you can `cat` or edit — `superRA/01-simulate-panel/task.md` — but the dashboard is the intended way to read it. The dashboard also renders a dependency DAG and lets you share a branch snapshot; the full field-by-field anatomy of a `task.md` is in [Reference › Task File](#/05-reference/01-task-file).

#### Superintegrate

When the tasks are done and approved, the work is correct — but getting a correct result is not the same as landing it safely. The INTEGRATE phase folds the work into your codebase in a way that keeps the results reproducible and coherent for the long haul. Trigger it the same way: ask Claude to `superintegrate`.

It is a phase of its own, not a final `git commit`, because each step guards against a different way good work quietly goes wrong after it is done. superRA **protects the key results against drift** by writing small automated checks that pin the numbers you care about, so a later refactor that moves them fails loudly instead of slipping through. It **syncs with your base branch by intent**, investigating what each incoming change means rather than resolving conflicts blindly line by line — never a bare `git merge`. It then **refactors the work to fit your codebase** with a minimal, reviewable diff, **matures the task findings into documentation** a future reader can follow, and only then **ships** by PR or merge. The full phase is owned by [superintegrate](skills/superintegrate/SKILL.md).

### Where to go next

You have now run a full cycle. The two pieces of discipline that do most of the work — the domain skill that enforces the right protocol for each kind of research, and the utility skills the workflow leans on — each have a page:

- **[Domain Skills](#/03-domain-skills)** — what discipline superRA enforces for data analysis, theory, writing, and more, and how a domain skill loads on top of any phase.
- **[Utility Skills](#/04-utility-skills)** — the cross-cutting tools the workflow reaches for: result protection, semantic merge, the task-tree tooling, and others.

For lookups — a field, a flag, a status, a CLI command — the [Reference](#/05-reference) section has the exact definitions with links to the files that own them. And to see a real, full-size project rather than this toy, open the [Showcase](#/06-showcase).
