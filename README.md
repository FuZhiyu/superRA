# superRA

superRA turns AI coding agents into disciplined Research Assistants. It ships:

1. An adaptive plan-implement-integrate workflow to ensure rigor analysis, reproducibility, and long-term maintainability; 
2. Domain skills to teach agents how to do data analysis properly (writing/modeling skills are coming); 
3. Utility skills for creating human friendly jupyter notebooks, writing technical reports in markdown files, and sync data across git worktrees; 

superRA is inspired by the superpowers plugin, which centers on the test-driven development. SuperRA is adapted to scientific research, which is often explorative, iterative, and fluid. 

## Why superRA?

AI agents are fast but undisciplined:

- Agents generate a bunch of code that is way too long to review carefully, and often inconsistent with the existing codebase;
- Half of the samples are silently dropped out before running the regression while agents declare "everything looks good";
- As agents' context window is filled, agents become more error-prone, but it's difficult to start a new session afresh as you lose important steps; 
- After several iterations with the agents, somehow the results drift away from the original one, and neither you and the agent really knows why;
- ...

superRA brings disciplines to the AI agent. It follows a rigorous workflow with a pair of implementer-reviewer at every step, it teaches agents the proper protocol for each domain (e.g., always describe before analysis for data analysis), and it teaches agents how to integrate the output with the existing codebase and human friendly. 

## The Plan-Implement-Integrate Workflow

This workflow assumes basic understanding of git branch-PR workflow; worktrees are also helpful. 

superRA follows three-phase macro workflow: **PLAN → IMPLEMENT → INTEGRATE**. The phases are domain-agnostic; the domain skill supplies the discipline that applies inside each phase. 

<!-- use the diagram to express this: whenever is a change of plan, route it back to PLAN in the diagram below -->
The phases are iterative: a discovery during IMPLEMENT, a reviewer request during INTEGRATE, or a scope addition after merge all route back through `planning-workflow §User Feedback and Changing Plans`

<!-- Possible to make it a renderable diagram? -->
```
PLAN            planning-workflow
                ...
                Create and update the DAG for tasks
                PLAN.md and RESULTS.md files
                    |
IMPLEMENT       execution-workflow
                draw an implementation-review loop here
                Commit changes in every step: code + PLAN.md status + RESULTS.md findings.
                    |
INTEGRATE       integration-workflow 
                4 stages, and the fix-review loop as well
                Refactor for codebase. Integration review. Mature RESULTS.md. Merge or PR.
<!-- the latter stages should have arrows lead back to the plan stage -->
<!-- final arrow pointing to merge -->
```

### Key principles of the workflow

1. **Implementer–reviewer pair at every step.** No result ships without adversarial review. At every step, an adversarial agent review the implementation, and we only move forward after approval
2. **Handoff docs (PLAN.md and ...) always reflect the current state.** No important progress should stay in the conversation: any updates are committed into the handoff doc. A new agent can pick up the progress without any loss by reading the handoff files. 
3. **Fast early for exploration, strict for integration. Semantic merges always.** At the implementation stage, we optimize for speed and correctness; once we are happy with the results, the integration workflow ensures the code is human reviewable and integrate well with the existing code. Explain what does integration and semantic merge do. 
4. **Autonomous with human in the loop.** The agent drives work forward on its own power, and stops — via `AskUserQuestion` — only for hard blockers, decisions beyond its authority, and user-defined workflow milestones.
5. **Adaptive and composable**: research was never linear, and it never has a single style. The existing workflows provide protocols but not requirements, and can be adapted to various different workflows. The workflow is domain-agnostic: it can be applied to data analysis, model, writing. Currently we ship data analysis, other domain skills are coming. 


## Domain Skills

Domain skills are the skills agents can load when handling particular domains. 

Currently we ship data analysis skill. 

## Utility skills

- provide an rundown of the utility skills

## Installation

superRA is a fork of [Superpowers](https://github.com/obra/superpowers), adapted for economic research. The canonical repo is [github.com/FuZhiyu/superRA](https://github.com/FuZhiyu/superRA).

### Claude Code

Claude Code (v2.1+) can install plugins directly from a GitHub repo. Add superRA as a marketplace and install the plugin:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA-dev
```

That's it — restart Claude Code (or start a new session) and the skills, agents, and hooks are available.

To update later:

```bash
claude plugin marketplace update superRA-dev
claude plugin update superRA
```

### Claude Code (local clone, for development or forking)

If you want to modify superRA itself — edit skills, add a domain vertical, tune hooks — install from a local clone instead:

```bash
git clone https://github.com/FuZhiyu/superRA.git
claude plugin marketplace add ./superRA
claude plugin install superRA@superRA-dev
```

Edits to your clone are picked up on the next session start.

### Other Platforms

superRA ships entry files for several non-Claude-Code harnesses:

- **Codex / Copilot CLI / any `AGENTS.md`-aware tool** — point at [`AGENTS.md`](./AGENTS.md) at the repo root.
- **Gemini CLI** — point at [`GEMINI.md`](./GEMINI.md) and [`gemini-extension.json`](./gemini-extension.json).

Harness-specific install flow varies; see the upstream [Superpowers docs](https://github.com/obra/superpowers) for patterns, and substitute this repo's URL.

## Skills

superRA's skills split into four categories. The directory layout stays flat (one `skills/<name>/SKILL.md` per skill); `skills/CATEGORIES.md` is the authoritative grouping index.

- **Workflow skills** — domain-agnostic choreography for each phase. What agent to dispatch, in what sequence, with what handoff rules. Reused across every domain vertical.
- **Domain skills** — vertical-specific discipline (today: data analysis). Loaded by workflow skills when a task touches the matching domain. Organized with stage-scoped references so only the relevant chunk loads per phase.
- **Utility skills** — reusable, domain-neutral tools. Handoff-doc discipline, report formatting, notebook rendering, worktree management, semantic merge, verification.
- **Meta skills** — session bootstrap and skill authoring.

### Workflow

| Skill | Phase | What It Does |
|-------|-------|-------------|
| **planning-workflow** | PLAN | Scope check, task decomposition, self-review, execution handoff. Points at the active domain skill for domain-specific gates and templates. |
| **execution-workflow** | IMPLEMENT + VALIDATE | Per-task dispatch, one-pass review loop (APPROVE / REVISE) with orchestrator-discipline filter, pipeline + reproducibility verification, 4-option completion menu. |
| **integration-workflow** | INTEGRATE (pre-merge) | Drift-test creation, refactor-review loop, doc finalization (mature RESULTS.md into permanent form, audit project-level CLAUDE.md / AGENTS.md / README.md). |
| **merge-workflow** | INTEGRATE (merge) | Update analysis branch via semantic-merge, post-merge verification (drift tests + fresh integration review), local merge or PR push, worktree cleanup. |
| **agent-orchestration** | cross-cutting | Multi-agent dispatch patterns: workload balancing across tiers, parallel subagents for independent tasks, reviewer-feedback adjudication. |

### Domain — Data Analysis

| Skill | What It Does |
|-------|-------------|
| **econ-data-analysis** | Iron Law (no transformation without prior description). Three concurrent disciplines: Describe, Analyze, Validate (with sensitivity analysis as a first-class validation discipline). Diagnostics-for-validity philosophy. Pitfall catalogs for merges, time series, aggregations, filtering, variable construction, missing data. Common Rationalizations table. Stage-scoped references load per phase: `planning.md` (Data Inventory hard gate + sensitivity design), `integrate-drift-tests.md` (drift-test construction), `integration.md` (data-specific integration gates), `data-robustness-checklist.md` (robustness menu), `notebook-format.md` (cell organization + Python/Julia rendering; companion guides `jupytext-guide.md`, `julia-quarto-guide.md`). |

Future verticals — theory/modeling, literature review, simulation, writing/paper drafting — are planned; see the Roadmap section at the bottom.

### Utility

| Skill | What It Does |
|-------|-------------|
| **handoff-doc** | Handoff-doc discipline — four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, full `PLAN.md` / `RESULTS.md` anatomy templates (`plan-anatomy.md`, `results-anatomy.md`). Loaded on demand when the compact etiquette in `agents/implementer.md` / `agents/reviewer.md` step 1 is not enough, and always by doc-creators (`planning-workflow` Phase 2, `integration-workflow` Step 3 doc-writer). Usable standalone by a single author with no subagents. |
| **refactor-and-integrate** | Three integration-phase checklists: `drift-test-quality.md`, `codebase-integration.md`, `merge-quality.md`. Standalone-invokable for any refactoring task. |
| **report-in-markdown** | Format discipline for markdown reports with figures, LaTeX math, tables. Lean SKILL.md body; three references loaded on demand: `baseline-io.md`, `rich-content.md`, `final-form.md`. |
| **semantic-merge** | Intent-based branch integration. Classifies conflicts by research impact, escalates methodology decisions to the user. Invoked by `merge-workflow` Step 1 and by the merge-guard hook. |
| **worktree-data-sync** | Non-git data sync between existing worktrees (seed, diff, apply modes) and data teardown. Worktree lifecycle (create / enter / remove) lives in `agent-orchestration/references/worktree-harness-fallback.md`. |

### Meta

| Skill | What It Does |
|-------|-------------|
| **using-superRA** | Master skill every agent reads. Carries the distilled universal principles, code-change defaults, the Workflow / Domain / Utility / Meta skill inventory, the composable-design map, the seven-row Skill-Load Manifest (Stage → required skills + stage-scoped references), and the Execution Modes (subagent dispatch vs direct). Preloaded on `superRA:implementer` / `superRA:reviewer` agent frontmatter; injected at session start for the main agent. Main-agent-only cross-session detection and autonomy contract live in `references/main-agent.md`. |

## Agents

| Agent | Role |
|-------|------|
| **reviewer** | Prototype reviewer agent. Verifies work independently using APPROVE/REVISE protocol. Dispatched with a workflow skill and the active domain skill's stage reference. |
| **implementer** | Prototype implementer agent. Executes tasks under the active domain's discipline. Dispatched with a workflow skill and the active domain skill's stage reference. |

## Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| **merge-guard** | Before any `git merge/rebase/cherry-pick` | Remind to use semantic-merge skill |
| **ask-user-question-logger** | After `AskUserQuestion` | Remind to log the decision in PLAN.md before acting |
| **exit-plan-mode** | After `ExitPlanMode` | Remind to materialize plan into PLAN.md + RESULTS.md before implementing |

## Plugin Design Philosophy

- Composable
- Domain skills and utility skills can be used stand alone or in the workflow
- Lean agent: 
- DRY


## License

MIT License — see LICENSE file for details.
