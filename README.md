# superRA

> ⚠️ **Beta.** superRA updates often; please [report bugs](https://github.com/FuZhiyu/superRA/issues). **Upgrading to 0.5.0:** coauthors on a shared project upgrade together ([Upgrading](#upgrading)).

**superRA turns AI agents into research assistants whose work you can see, steer, and reproduce.** It brings a plan–implement–integrate workflow, domain discipline, and a reproduction graph that traces every table and figure to the code that made it. A live dashboard ties them together: every task, decision, and result is a committed file, so you see where the work stands and which results are current. It runs on Claude Code and Codex.

**[📖 Documentation](http://fuzhiyu.me/superRA/)** · **[Explore an example project →](http://fuzhiyu.me/superRA/showcase-analysis-tree.html)**

![The superRA dashboard: the live Graph view of an asset-pricing study after an edit to the analysis script. The data step reads fresh; the analysis step reads stale, with a hover card naming the changed file; its downstream check is stale through it. The selected task's results and figures sit beside the graph.](docs/site/02-quickstart/attachments/showcase-graph.webp)

## Why superRA?

Research is exploratory, rarely testable in advance, and judged by people, so the researcher has to stay in the loop. Agent work makes that hard because it lives in the chat, not in a record. The reasoning vanishes when the session ends, the project's stage is invisible, and nothing logs which script and inputs produced each result, so no one can tell whether a table still comes from the current code and data.

Frameworks such as [Superpowers](https://github.com/obra/superpowers) target software, where unit tests verify the work and the goal is to take the human out of the loop. superRA keeps you in it: the project lives where you and the agent both see it.

## What you get

- **[A dashboard for the whole project.](http://fuzhiyu.me/superRA/#/04-utility-skills/01-task-tree)**
  - **Persistent history.** Each task's objective, decisions, results, and reviews are committed files. Any session or coauthor resumes from them; one exported HTML file shares them.
  - **Task management.** A task tree with status, dependencies, and what is ready next. Pin a comment to a task to steer it.
  - **The project's stage at a glance.** Status rolls up the tree: planned, in progress, awaiting your call, done.
- **[Know which results are current.](http://fuzhiyu.me/superRA/#/04-utility-skills/09-reproducibility)** Each table and figure traces to the script that made it. After an edit, the Graph view marks what went stale and rebuilds only that.
- **[An agent that works with you.](http://fuzhiyu.me/superRA/#/05-workflows)** It edits the task file with you as a live canvas, pauses for feedback, and asks before spending on a review. Autonomous runs on request.
- **Discipline as the work goes.** [Domain skills](http://fuzhiyu.me/superRA/#/03-domain-skills) for data analysis, theory, writing, and slides; independent review where it earns its cost; an integration step that lands the work as clean, protected code.
- **Quality-of-life utilities.** [Utility skills](http://fuzhiyu.me/superRA/#/04-utility-skills) that read and cite papers from Zotero, convert PDFs to Markdown, merge branches by intent, and sync data across worktrees.

## Get started

### Claude Code

Requires Claude Code v2.1+:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

Restart Claude Code, then in a project ask:

```text
Use superRA to onboard this project and show me the dashboard.
```

Onboarding builds a task tree and reproduction graph for the work already there, and changes nothing outside `superRA/` until you approve. For new work, the [Quickstart](http://fuzhiyu.me/superRA/#/02-quickstart) runs one study end to end.

To update later:

```bash
claude plugin marketplace update superRA
claude plugin update superRA@superRA
```

For Codex setup and a local-clone install (to track or modify superRA itself), see [`docs/README.codex.md`](docs/README.codex.md). Any other harness that supports skills and subagents installs the same plugin sources.

### Upgrading

**0.5.0:** every coauthor on a shared project upgrades superRA before anyone commits a 0.5 build or acceptance — an older superRA reads neither `repro-lock.json` nor `repro-acceptance/`, so its steps read stale or missing. Then follow the [upgrade steps](RELEASE-NOTES.md#upgrading-a-project-that-used-the-reproduction-pre-release).

**Older projects:**

- **0.4.0** retired the dedicated role agents for role skills. A Codex session that finds stale `~/.codex/agents/superra_*.toml` files deletes them with your confirmation.
- **Pre-0.3** `PLAN.md` / `RESULTS.md` projects are detected at session start and offered onboarding, which migrates them (`superra task migrate from-plan`).

## Contributing

Design principles, DRY / composability rules, skill-design patterns, and the extension path for adding a new domain vertical live in [`CLAUDE.md`](./CLAUDE.md). Read it before modifying skills, hooks, or harness adapters.

## Upstream

superRA started as a fork of [Superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://blog.fsck.com). The upstream project provides the plugin infrastructure, skill system, and several general-purpose skills that superRA inherits and extends.

## License

MIT License — see the `LICENSE` file for details.
