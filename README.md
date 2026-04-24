# superRA

superRA turns AI coding agents into disciplined Research Assistants. It ships:

1. An adaptive **plan-implement-integrate workflow** that enforces reviewer sign-off at every step and keeps results reproducible long-term.
2. **Domain skills** that teach agents how to do research work properly — starting with economic data analysis; theory, writing, and modeling are on the roadmap.
3. **Utility skills** for technical reports in markdown, gated integration checklists, semantic branch merges, and data sync across git worktrees.

superRA is inspired by the [Superpowers](https://github.com/obra/superpowers) plugin, which centers on test-driven software development. superRA adapts the same spine to scientific research, which is exploratory, iterative, and fluid.

superRA is compatible with Claude Code, Codex, and any other harness that supports skills and subagents. See below for installation. 

## Why superRA?

AI agents are fast but undisciplined:

- Agents generate far more code than anyone will carefully review, often inconsistent with the existing codebase.
- As the context window fills, agents become more error-prone — but starting fresh loses the thread of what was done and why.
- After several iterations, the results quietly drift from the original, and neither you nor the agent can reconstruct why.
- Half the sample is silently dropped before a regression runs, while the agent declares "everything looks good".

superRA brings discipline to the agent on three fronts. An **implementer–reviewer pair** sits at every step so no result ships without adversarial review. **Domain skills** teach the agent the right protocol for the work at hand (for data analysis: always describe before you transform). And an explicit **integration phase** folds each task into the existing codebase and maturing documentation, so what lands on `main` is coherent rather than a pile of single-shot outputs.

## The Plan-Implement-Integrate Workflow

This workflow assumes basic familiarity with git branch/PR workflow; worktrees help but are optional.

superRA organizes work into three phases: **PLAN → IMPLEMENT → INTEGRATE**. Each phase corresponds to a workflow skill to teach agents how to carry out in order, and a `using-superra` skill serves as the shared disciplines and knowledges across agents. The phases are domain-agnostic; the domain skill supplies the discipline that applies inside each phase. The phases form a cycle, not a pipeline: a discovery during IMPLEMENT, a reviewer request during INTEGRATE, or a scope change after merge all route back through `planning-workflow §User Feedback and Changing Plans`, which walks the task DAG and resumes at the right re-entry point.

```mermaid
flowchart TB
    PLAN["<b>PLAN</b><br/>scope · task decomposition<br/>PLAN.md + RESULTS.md"]
    IMPLEMENT["<b>IMPLEMENT</b> (per task)<br/>implementer ⇄ reviewer loop<br/>APPROVE advances · REVISE loops back"]
    INTEGRATE["<b>INTEGRATE</b><br/>Protection (default: drift tests)<br/>Sync with base<br/>Integrate/refactor<br/>Document<br/>Finish"]
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

To invoke the workflow, use the keywords: `using superRA`, `make a plan on...`, `implement according to the plan`, `integrate it with the update on the main`, ...

### Key principles of the workflow

1. **Implementer–reviewer pair at every step.** An adversarial reviewer inspects every implementation; work only advances after `APPROVE`. Review is never skipped, regardless of how trivial a step looks.
2. **Handoff docs always reflect the current state.** Material progress lives in committed `PLAN.md` and `RESULTS.md`, not in the chat log. A fresh agent can open the repo and resume from the docs plus git state alone.
3. **Fast early for exploration, strict for integration. Semantic sync always.** During implementation, optimize for speed and correctness of the analysis itself. Once results are in hand, the integration phase protects key results (drift tests are the default mechanism), syncs against the current base with `semantic-merge`, runs a dedicated sync review, refactors the post-sync diff to fit the codebase, and matures documentation for the long haul. Intent-aware branch syncs never use a bare `git merge`.
4. **Autonomous with human in the loop.** The agent drives work forward on its own power and stops — via `AskUserQuestion` — only for hard blockers, decisions beyond its authority, and user-defined workflow milestones.
5. **Adaptive and composable.** Research is rarely linear and never has a single style. The workflow supplies protocols, not requirements, and can be adapted to different rhythms. It is domain-agnostic: data analysis today; theory, modeling, and writing in the pipeline.

## Domain Skills

Domain skills teach agents the discipline that applies to a particular kind of research work. They load on top of the workflow skills when a task touches their domain. Domain skills will be invoked automatically when agents detect the relevant domain, or they can be invoked stand alone during interactive sessions. 

| Skill | Flagship discipline |
|-------|---------------------|
| **econ-data-analysis** | Iron Law: no transformation without prior description. Three concurrent disciplines — Describe, Analyze, Validate — plus pitfall catalogs for merges, time series, aggregations, filtering, variable construction, and missing data, and how to render human-friendly notebook. |

Future verticals are planned hooks, not commitments:

- **Theory / modeling** — derivation discipline, notation consistency, proof checks, numerical verification of derived formulas.
- **Literature review** — citation integrity, claim-evidence mapping, coverage audits.
- **Simulation** — seed discipline, stochastic reproducibility, parameter-grid sensitivity.
- **Writing / paper drafting** — figure/table consistency with the underlying code, cross-reference integrity, manuscript versioning alongside the analysis branch.

## Utility Skills

Utility skills are domain-neutral tools callable by workflow skills, agents, or directly by a human. Each carries both *what* it provides and *when* you would reach for it.

| Skill | What + when to use |
|-------|--------------------|
| **handoff-doc** | Teaches agents how to create a handoff document. Editing discipline for `PLAN.md` / `RESULTS.md` — four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, full task-block anatomy templates. Use when creating a handoff doc from scratch, maturing `RESULTS.md` into its permanent form, or when the compact etiquette baked into the agent files is not enough. |
| **report-in-markdown** | Format rules for markdown reports containing figures, LaTeX math, or tables. Use when producing a standalone human-readable report, or when an implementer task section in `RESULTS.md` embeds a figure or math expression. |
| **result-protection** | Tools for protecting key research results from unintended changes. Drift/regression tests are the current/default mechanism. Use during Protect or whenever key-result expectations need guarded review. |
| **refactor-and-integrate** | Tools for **codebase coherence** — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host, and supplied Sync impact as justification evidence. Shared by implementer and reviewer. Use during Integrate, or standalone for any refactor that needs consistent quality gates. |
| **semantic-merge** | Tools for **semantic coherence** in branch integration — intent investigation, role classification (behavior/API, data/schema, docs, generated outputs, tests, config/build), conflict resolution, intent-changing escalation, stale-reference detect-and-resolve, and propagation-to-coherence. Lands a merge commit plus propagation commits as needed to reach semantic coherence, with every commit leaving existing protection passing, and records branch-level / task-local / file-local context explaining the approved post-sync diff. Use whenever you would otherwise run `git merge` / `git rebase` / `git cherry-pick` — the `merge-guard` hook flags bare invocations automatically. |
| **worktree-data-sync** | Research project often depends on non-git-controlled data. It syncs data between existing git-controlled worktrees (seed, diff, apply) plus data teardown. Use when copying data into a new worktree, reconciling data across parallel worktrees, or tearing down a worktree's data cleanly. Worktree lifecycle itself (create/enter/remove) lives in `agent-orchestration`. |


## Agents

| Agent | Role |
|-------|------|
| **implementer** | Prototype implementer agent. Executes tasks under the active domain's discipline. Dispatched with a workflow skill and the active domain skill's stage reference. |
| **reviewer** | Prototype reviewer agent. Verifies work independently using the APPROVE / REVISE protocol. Dispatched with a workflow skill and the active domain skill's stage reference. |

## Hooks

Currently hooks are only supported by Claude Code. 

| Hook | Trigger | Purpose |
|------|---------|---------|
| **merge-guard** | Before any `git merge` / `git rebase` / `git cherry-pick` | Remind to use the `semantic-merge` skill. |
| **ask-user-question-logger** | After `AskUserQuestion` | Remind to log the decision in `PLAN.md` before acting on it. |
| **exit-plan-mode** | After `ExitPlanMode` | Remind to materialize the plan into `PLAN.md` + `RESULTS.md` before implementing. |
| **autoload-superra** | `UserPromptSubmit` when the prompt mentions a superRA term | Inject a reminder to load `superRA:using-superRA` if the master skill has not yet loaded this session. |
| **ensure-using-superra** | `PreToolUse` on `Skill(superRA:*-workflow)` | Hard-deny the workflow-skill call when `superRA:using-superRA` is not yet loaded; reason directs Claude to load it and retry. |
| **ensure-agent-orchestration** | `PreToolUse` on `Skill(superRA:*-workflow)` | Same pattern as above, gating on `superRA:agent-orchestration`. |

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

### Claude Code (local clone, for development or forking)

If you want to modify superRA itself — edit skills, add a domain vertical, tune hooks — install from a local clone instead:

```bash
git clone https://github.com/FuZhiyu/superRA.git
```

The committed repo marketplace now targets the published GitHub source so remote installs work cleanly in Codex. For a live local-development install, create your own personal marketplace entry that points directly at your clone instead of relying on the repo's committed marketplace file.

### Codex

Codex installation has two pieces:

- **Plugin bundle** from [`.codex-plugin/plugin.json`](./.codex-plugin/plugin.json). This installs the shared superRA skills.
- **Named custom agents** from `codex-superra-setup`. This installs `superra_implementer` and `superra_reviewer`.

This split is Codex-specific and deliberate. In Codex, plugins are the installable distribution unit for shared skills, while custom agents are discovered separately from `~/.codex/agents/`.

#### Remote marketplace install (recommended)

1. Add the repo as a marketplace:

   ```bash
   codex plugin marketplace add FuZhiyu/superRA
   ```

2. Restart Codex, open the Plugins UI (or run `/plugins` in the CLI), and install `superra`.
3. Run `codex-superra-setup`.
4. Choose **global** scope so `superra_implementer` and `superra_reviewer` install into `~/.codex/agents/`.
5. Restart Codex or start a fresh session if agent discovery has not refreshed yet.

Codex should cache the plugin after install under `~/.codex/plugins/cache/...`.

#### Manual local-clone install (for development or explicit local control)

1. Clone this repo somewhere durable:

   ```bash
   git clone https://github.com/FuZhiyu/superRA.git ~/.codex/plugins/superra
   ```

2. Add a personal plugin marketplace at `~/.agents/plugins/marketplace.json` that points at that clone. Minimal example:

   ```json
   {
     "name": "superra",
     "interface": {
       "displayName": "superRA"
     },
     "plugins": [
       {
         "name": "superra",
         "source": {
           "source": "local",
           "path": "./.codex/plugins/superra"
         },
         "policy": {
           "installation": "AVAILABLE",
           "authentication": "ON_INSTALL"
         },
         "category": "Productivity"
       }
     ]
   }
   ```

3. Restart Codex, open the Plugins UI (or run `/plugins` in the CLI), and install `superra`.
4. Run `codex-superra-setup`.
5. Choose **global** scope so `superra_implementer` and `superra_reviewer` install into `~/.codex/agents/`.
6. Restart Codex or start a fresh session if agent discovery has not refreshed yet.

#### Updating a Codex install

- **Remote marketplace install:** update the marketplace and plugin from Codex, then restart if the UI has not refreshed yet.
- **Manual local-clone install:** Codex tracks the directory named in your personal marketplace entry. Update that clone, then restart Codex so it reloads the plugin files. For the example above, that usually means `git -C ~/.codex/plugins/superra pull`.
- **Agent updates:** rerun `codex-superra-setup` after updating if you want to refresh the generated custom agents. This is required whenever [`agents/implementer.md`](./agents/implementer.md) or [`agents/reviewer.md`](./agents/reviewer.md) changes.
- **Verification:** the global install should create `~/.codex/agents/superra_implementer.toml` and `~/.codex/agents/superra_reviewer.toml`.

For more detail, see the official [Codex plugin docs](https://developers.openai.com/codex/plugins/build) and [`docs/README.codex.md`](./docs/README.codex.md).

### Other Platforms

superRA ships entry files for several non-Claude-Code harnesses:

- **Copilot CLI / any other `AGENTS.md`-aware tool** — point at [`AGENTS.md`](./AGENTS.md) at the repo root.
- **Gemini CLI** — point at [`GEMINI.md`](./GEMINI.md) and [`gemini-extension.json`](./gemini-extension.json).

Harness-specific install flow varies; see the upstream [Superpowers docs](https://github.com/obra/superpowers) for patterns, and substitute this repo's URL.


## Contributing

Design principles, DRY / composability rules, skill-design patterns, and the extension path for adding a new domain vertical live in [`CLAUDE.md`](./CLAUDE.md). Read it before modifying skills, hooks, or agent files.

## Upstream

superRA started as a fork of [Superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://blog.fsck.com). The upstream project provides the plugin infrastructure, skill system, and several general-purpose skills that superRA inherits and extends.

## License

MIT License — see the `LICENSE` file for details.
