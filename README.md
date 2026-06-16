# superRA

> ⚠️ **Breaking change (0.2.0):** the three workflow phase skills were renamed — `planning-workflow` → `superplan`, `implementation-workflow` → `superimplement`, `integration-workflow` → `superintegrate` — to avoid colliding with Claude Code's Workflow tool / `/workflows`. Update any saved `Skill(superRA:planning-workflow|implementation-workflow|integration-workflow)` calls to the new ids, and refresh globally-installed Codex agents by rerunning `codex-superra-setup`. See [RELEASE-NOTES](RELEASE-NOTES.md) for the migration note.

**[📖 Read the documentation →](http://fuzhiyu.me/superRA/)** — start with the [Quickstart](http://fuzhiyu.me/superRA/#/02-quickstart) (one analysis end to end in ~20 min), then the [How-To guides](http://fuzhiyu.me/superRA/#/04-how-to), [Concepts](http://fuzhiyu.me/superRA/#/03-concepts), [Reference](http://fuzhiyu.me/superRA/#/05-reference), and a live task-tree [Showcase](http://fuzhiyu.me/superRA/#/06-showcase).

superRA turns an AI coding agent into a disciplined research assistant. You bring a research question; superRA gives the agent a workflow that plans the work, implements it under adversarial review, and integrates the result into your codebase without letting the findings quietly drift. It runs on Claude Code, Codex, or any harness that supports skills and subagents.

It exists because agents are fast but undisciplined. They generate more code than anyone will read, drop half a sample before running a regression while reporting that "everything looks good", and lose the thread of what was done and why as the context window fills. After a few iterations the results have drifted from what you asked for, and neither you nor the agent can reconstruct the path back. superRA's answer is structure:

- An **implementer–reviewer pair** sits at every step, so no result ships without an independent adversarial second look.
- **Domain skills** teach the agent the right protocol for the work at hand — for data analysis, never transform data before describing it; for theory, define objects and assumptions before manipulating equations.
- The work lives in a **task tree** of plain files you can read and edit, and an explicit **integration phase** folds each piece into your codebase rather than leaving a pile of one-shot outputs.

superRA is inspired by the [Superpowers](https://github.com/obra/superpowers) plugin, which centers on test-driven software development. superRA adapts the same spine to scientific research, which is exploratory, iterative, and fluid.

## The Plan-Implement-Integrate Workflow

superRA organizes every project into three phases — **PLAN → IMPLEMENT → INTEGRATE**. The phases are domain-agnostic; the active domain skill supplies the discipline that applies inside each one. They form a cycle, not a pipeline: a discovery while implementing or a scope change after merge routes back to planning and resumes at the right re-entry point, leaving unrelated finished work untouched.

```mermaid
flowchart TB
    PLAN["<b>PLAN</b><br/>scope · task decomposition<br/>superRA/ task tree"]
    IMPLEMENT["<b>IMPLEMENT</b> (per task)<br/>implementer ⇄ reviewer loop<br/>APPROVE advances · REVISE loops back"]
    INTEGRATE["<b>INTEGRATE</b><br/>Protect results <br/>Sync with base<br/>Integrate/refactor<br/>Document<br/>Finish"]
    FINISHED(["finished"])

    PLAN --> IMPLEMENT
    IMPLEMENT --> INTEGRATE
    INTEGRATE --> FINISHED

    IMPLEMENT -. "plan change" .-> PLAN
    INTEGRATE -. "plan change" .-> PLAN

    classDef phase fill:#eef7ff,stroke:#0366d6,color:#000
    classDef terminal fill:#e8f5e9,stroke:#2e7d32,color:#000
    class PLAN,IMPLEMENT,INTEGRATE phase
    class FINISHED terminal
```

To start, just describe what you want — `make a plan on...`, `implement according to the plan`, `integrate it with the update on main` — or name a phase skill directly: `superplan`, `superimplement`, `superintegrate`. The [Concepts](http://fuzhiyu.me/superRA/#/03-concepts) section explains each phase, re-entry, and the autonomy-with-human-in-the-loop model.

The project's state lives in a task tree — a directory of small `task.md` files, each holding one unit of work — that you can read at any time. Run `superra dashboard` to watch and steer it through tree, DAG, and kanban views that auto-update as tasks progress; the [dashboard guide](http://fuzhiyu.me/superRA/#/04-how-to/04-see-your-work) covers live serve and branch-snapshot sharing.

![The superRA dashboard rendering a task tree — sidebar hierarchy, a task's objective and conventions, and its subtasks with status.](docs/assets/task-tree-dashboard.png)

## Skills, Agents, and Hooks

superRA ships **domain skills** — currently economic data analysis, theory-modeling, and academic writing, with literature review and simulation on the roadmap — that load on top of the workflow when a task touches their domain, plus **utility skills** for markdown reports, result-protecting drift tests, semantic branch merges, gated integration refactors, and worktree data sync. The [Skills & Agents concept page](http://fuzhiyu.me/superRA/#/03-concepts/04-skills-and-agents) explains the model, and the [reference](http://fuzhiyu.me/superRA/#/05-reference/04-skills-and-agents) lists every skill and the Stage → skill load map.

The agents that carry out the work are an [implementer and a reviewer](http://fuzhiyu.me/superRA/#/03-concepts/03-roles-and-review), and superRA installs [lifecycle hooks](http://fuzhiyu.me/superRA/#/05-reference/07-hooks) for Claude Code and Codex that nudge agents toward the right skill at the right moment.

## Installation

### Claude Code

Claude Code (v2.1+) can install plugins directly from a GitHub repo. Add superRA as a marketplace and install the plugin:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

That's it — restart Claude Code (or start a new session) and the skills, agents, and hooks are available.

To update later:

```bash
claude plugin marketplace update superRA
claude plugin update superRA
```

For a local-clone install (to modify superRA itself), Codex setup, and other harnesses (Copilot CLI, Gemini CLI), see the [Install & Set Up guide](http://fuzhiyu.me/superRA/#/04-how-to/01-install-and-set-up).

## Contributing

Design principles, DRY / composability rules, skill-design patterns, and the extension path for adding a new domain vertical live in [`CLAUDE.md`](./CLAUDE.md). Read it before modifying skills, hooks, or agent files.

## Upstream

superRA started as a fork of [Superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://blog.fsck.com). The upstream project provides the plugin infrastructure, skill system, and several general-purpose skills that superRA inherits and extends.

## License

MIT License — see the `LICENSE` file for details.
