---
title: "Quickstart: Your First Workflow"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

This tutorial walks you through installing superRA, pointing it at a project, and pushing one piece of work through a full PLAN → IMPLEMENT → INTEGRATE cycle: plan a small task tree, run a task through its implementer–reviewer pair, watch progress and read results in the dashboard, and integrate the result.

### Prerequisite

**git** is the one real prerequisite — as it is for any agentic coding workflow. Think of it as the rope in climbing: it lets you explore boldly, and it catches you when things go south. superRA is built around git, so use it.

A branch-and-PR workflow is recommended but not required. To get the most out of superRA, `git worktree` lets you push on several fronts at once while an agent runs in the background; the [`worktree-data-sync`](#/04-utility-skills/06-worktree-data-sync) skill keeps non-git-controlled data in sync across those isolated worktrees.

superRA runs on **[Claude Code](https://docs.claude.com/en/docs/claude-code) or [Codex](https://developers.openai.com/codex/cli)**. This walkthrough uses Claude Code; everything applies to Codex too — only the install step and the way you invoke agents differ (see the [Codex install notes](docs/README.codex.md)). 

You also need [`uv`](https://docs.astral.sh/uv/) to launch the dashboard.

### Install + set up a project

Install the plugin into Claude Code as a marketplace, then restart your session:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

The quickest way to try superRA is to point it at work you already have. Take an existing project (commit everything first if you haven't), start Claude Code, and ask it something like:

```text
Use superRA and retroactively create task trees for [what I'm working on],
and show me the dashboard.
```

The trigger is the word **`superra`**: with it in the prompt, the agents follow the workflow instead of improvising. 

### A typical workflow

The rest of this page walks one piece of work through all three phases. The example below is a real empirical asset-pricing study: estimate CAPM and the Fama-French three-factor model on Ken French's 25 portfolios sorted by size and book-to-market, then run the Gibbons-Ross-Shanken (GRS) joint test to ask whether either model prices the cross-section. 


#### Superplan

Tell Claude what you want to work on in plain language and ask it to `superplan`. (Don't use your harness's built-in `plan` mode — in Claude Code or Codex it blocks the file writes the planner needs.)

```text
Using superRA, superplan an asset-pricing study on public Ken French data:
download the factors and the 25 size-B/M portfolios, estimate CAPM and the
Fama-French 3-factor model, and run the GRS joint test. Keep it to a handful
of tasks.
```


Claude loads the `superplan` skill, explores the project, and proposes a small **task tree** — here, three tasks under one root: build the panel, run the regressions and the GRS test, and write up the result. The task tree holds the project's state. Instead of keeping the plan in one agent's context window or a temporary plan file, superRA writes it as a committed tree of small `task.md` files — one directory per unit of work — that the agents read and write as they go. The state is plain files in git, so a fresh agent session, or you next week, can reopen the repo and see exactly what was planned, done, and left.

Planning is autonomous but stops at one gate: before any code is written, the planner shows you the proposed plan and waits. You read the task tree on the **dashboard** — ask the agent to show it, or launch it yourself from a project terminal:

```bash
./superRA/superra dashboard
```
A live, auto-updating dashboard opens in your browser. The default **Workspace** view shows the tree, with a colored status pill on each task. 

Here is this study right after planning — three tasks under one root, every one `not-started` (grey), so the root rolls up to `not-started` too. Open it and click a task to read the objective the planner wrote. Read the objectives and approve — or leave a comment on the dashboard and ask the agent to revise.

[Open the freshly-planned tree →](showcase-after-planning.html)

#### Superimplement

Now run a task. Ask Claude to `superimplement`:

```text
superimplement @superRA/showcase-analysis.
```

By default, the main agent dispatches a separate implementer subagent for each task. This keeps the main agent's context window clean, so it stays sharp and can run far longer without degrading — at the cost of more tokens than working inline. To work inline instead, ask the main agent to run in **direct mode**.

Here is superRA's central discipline: every task runs through an **implementer–reviewer pair**. The implementer does the work — here, downloading the Ken French data and building the monthly panel — records what it found in the task's `## Results` section, and hands off. A separate reviewer then inspects the committed result *independently*. 

The reviewer is adversarial by design. An agent reviewing its own work shares its own blind spots: drop half the sample, and it reports everything looks fine. A fresh reviewer with a different prompt and a mandate to find failure catches the silent bad merge, the wrong aggregation, the unreproducible output. Anything that advances through a superRA project has passed a second, independent read at every step. The full role behavior is in the [implementer](agents/implementer.md) and [reviewer](agents/reviewer.md) specs.

The implementer writes its findings straight into the task file, so the panel task's `## Results` reads like this:

```text
## Results

Built the baseline monthly panel end-to-end from public Ken French data.
Re-running superRA/showcase-analysis/run_all.sh reproduces every output.

- data/ff_panel.parquet: 754 months × 29 columns, indexed by month-end date
  over 1963-07 → 2026-04. Columns: Mkt-RF, SMB, HML, RF plus the 25 portfolio
  excess-return series.
- Merge: 1:1 inner join on the month index, 1198 → 1198 rows, 0 unmatched.
  No within-sample month gaps; no missing values over the baseline sample.
- Factor magnitudes match published scales — market premium 0.597%/mo,
  market volatility 4.47%/mo — so downstream regressions start from clean data.
```

During implementation, agents commit atomically by default, so every step is tracked in git. Because that produces many small commits, it is recommended to work on a separate branch rather than directly on your default branch.

The dashboard shows the loop in flight. Open this study mid-run — the panel task is `approved` (green), the regression-and-GRS task is `implemented` (yellow) and waiting for its reviewer, the writeup is still `not-started` (grey), and the parent has rolled up to `in-progress`. Click the implemented task to see the results already written and waiting on review:

[Open the study mid-implement →](showcase-mid-implement.html)

#### Watch progress and read results

The dashboard auto-updates in real time as the agents work, so it is the default way to both watch the run and read what came out. As one task is approved, the next one becomes ready: the agent picks up the next task whose dependencies are satisfied, and you watch the order unfold on the dashboard. Once every task has survived its review, the whole tree is `approved` (green) — the state INTEGRATE picks up:

[Open the finished study →](showcase-analysis-tree.html)

This is the completed tree, every task green. Toggle the **Kanban** view (the view switch at the top of the page) to see every task as a card in a column by status — the at-a-glance "what is where" across the whole tree.

Click any task to read its objective and results in place — the same `## Objective` the implementer worked to, and the `## Results` it wrote and the reviewer checked. The regression-and-GRS task opens straight to its objective math and the results the implementer wrote and the reviewer checked:

[Read the finished regression task →](showcase-analysis-tree.html#/02-analysis)

Because the results live in committed task files rather than the chat, they are the durable handoff: nothing of value sits in a context window waiting to be lost. Each task is a plain markdown file (`superRA/showcase-analysis/01-data/task.md`) you can open or edit directly, but the dashboard is the intended way to read it. The dashboard also renders a dependency DAG and lets you share a branch snapshot. The full field-by-field anatomy of a `task.md` is in [The Task File](#/04-utility-skills/01-task-tree/01-task-file).

#### Superintegrate

The tasks are done and approved, but a correct result still has to be landed safely. The INTEGRATE phase folds the work into your codebase so the results stay reproducible and coherent over the long term. Trigger it the same way: ask Claude to `superintegrate`.

Superintegration consists of five stages, and each stage guards against a different way good work goes wrong after it is done:

1. **Protect** — pin the key results from the implementation phase with small drift tests, guided by what you flag as important, so a later change that moves a number you care about fails loudly instead of slipping through silently.
2. **Sync** — when the base branch has moved (a coauthor pushed while you worked, say), fold those changes in **semantically**: superRA reads the intent behind each incoming change and reconciles it, rather than resolving conflicts line by line — never a bare `git merge`.
3. **Refactor** — reshape the agent's working code to fit your codebase: reuse the utilities and conventions you already have, consolidate throwaway exploration scripts into coherent modules, and leave a minimal, reviewable diff instead of a pile of single-shot files.
4. **Mature & Consolidate** — a running project accumulates many small interim tasks, which become noise for anyone reading it later. This stage settles the tree's shape — fold finished scaffolding into the tasks that own it, prune what is not worth keeping — and distills the surviving findings into documentation a future reader can follow.
5. **Finish** — ship by PR or merge.

The full phase is owned by [superintegrate](skills/superintegrate/SKILL.md).

#### Composable and iterative

Research is rarely linear, and superRA does not force it to be. The phases form a cycle, not a one-way pipeline: a discovery mid-implementation, or a scope change after integration, routes back to planning and resumes at the right point, leaving finished work untouched. The tree is a living structure you steer, not a plan you lock in up front.

In practice that means you can edit the tree at any time, in plain language. Add a task to a tree that is already running:

```text
Using superRA, add a task under showcase-analysis for a robustness check
on the post-2000 subsample, depending on the regression task.
```

Revise a task's objective as your understanding shifts:

```text
Using superRA, update the regression task to also report Newey-West
standard errors.
```

Or point superRA at work you have already done and have it build the tree retroactively — the adoption prompt at the top of this page is exactly that.

### Where to go next

You have run a full cycle. Two further pieces of discipline each have a page — the domain skill that enforces the right protocol for each kind of research, and the utility skills the workflow leans on:

- **[Domain Skills](#/03-domain-skills)** — what discipline superRA enforces for data analysis, theory, writing, and more, and how a domain skill loads on top of any phase.
- **[Utility Skills](#/04-utility-skills)** — the domain-neutral tools the workflow reaches for: result protection, semantic merge, the task-tree tooling, and others.

For more on the three phases — what each does for you and what you decide along the way — see the [Workflows](#/05-workflows) section. For lookups, the task-tree detail pages have the exact definitions: [task-file fields](#/04-utility-skills/01-task-tree/01-task-file), [CLI commands](#/04-utility-skills/01-task-tree/02-cli-commands), and the [status lifecycle](#/04-utility-skills/01-task-tree/03-status-and-frontier). To open and click through the finished study this page walked you through — the live task tree with its regression tables, figures, and full review history — go to the [Showcase](#/07-showcase).
