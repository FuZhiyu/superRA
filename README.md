# superRA

superRA is a complete economic research workflow for AI coding agents, built as a fork of [Superpowers](https://github.com/obra/superpowers). It turns your coding agent into a disciplined Research Assistant that follows data-first principles, enforces reproducibility, and maintains full session-to-session handoff — so you never lose work when context runs out.

## Why superRA?

AI agents are eager but undisciplined. They skip data description, merge without checking row counts, and declare "looks fine" without verification. In economic research, these shortcuts produce wrong results that look right.

superRA enforces a single non-negotiable rule — the **Iron Law of Data Analysis**:

> **NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION**

Every data operation follows a Describe-Analyze-Doc cycle. Every task gets a two-stage review (data integrity, then implementation correctness). Every session leaves enough state in PLAN.md and RESULTS_UPDATE.md that a fresh agent can pick up exactly where the last one stopped.

## How It Works

superRA activates automatically. When your agent sees a research task, it doesn't jump into code — it follows a structured workflow:

```
data-exploration          Inventory available data. Hard gate: no analysis until approved.
       |
analysis-planning         Break work into tasks with actual code at every step.
       |
executing-analysis        Dispatch one agent per task. Two-stage review after each.
       |                    Implementer -> Data Review -> Implementation Review -> Next task
       |
finishing-analysis        Verify reproducibility. Generate report. Present merge/PR options.
       |
pre-merge-gate            Create drift tests to protect results. Refactor for integration.
```

Each task produces an atomic commit: code + PLAN.md status + RESULTS_UPDATE.md findings. If the session dies at any point, the next session sees exactly what's done, what's under review, and what has open issues.

## Installation

superRA is a fork of [Superpowers](https://github.com/obra/superpowers), adapted for economic research. Clone and install as a local plugin:

### Claude Code

```bash
git clone https://github.com/FuZhiyu/econ-superpowers.git
# Then add as a local plugin in your project's .claude/settings.json
```

### Other Platforms

See the upstream [Superpowers docs](https://github.com/obra/superpowers) for plugin installation patterns on Cursor, Codex, Copilot CLI, and Gemini CLI. Point them at this repo instead of the upstream.

## Skills

### Core Discipline

| Skill | What It Does |
|-------|-------------|
| **econ-data-analysis** | Iron Law enforcement. Describe-Analyze-Doc cycle. Pitfall checklists for merges, aggregations, filtering, variable construction. Every agent loads this. |
| **verification-before-completion** | No completion claims without fresh verification evidence. Prevents "looks fine" from reaching merge. |

### Research Workflow

| Skill | What It Does |
|-------|-------------|
| **data-exploration** | Inventory available data, identify gaps, research sources. Hard gate: no analysis starts without approved inventory. |
| **analysis-planning** | Create step-by-step plans with actual code. Every step has describe-validate discipline. Plans are living handoff documents. |
| **executing-analysis** | Dispatch fresh subagent per task with two-stage review (data integrity then implementation). Falls back to direct execution when requested. |
| **finishing-analysis** | Verify reproducibility, generate work journal, present options: merge locally, push & PR, keep branch, or discard. |

### Quality Gates

| Skill | What It Does |
|-------|-------------|
| **pre-merge-gate** | Create drift tests to protect key results. Refactor code for integration. Review quality. Three stages with iteration. |
| **requesting-analysis-review** | Ad-hoc single-pass review for quick checks, before-merge verification, or when data looks unexpected. |
| **receiving-code-review** | Technical evaluation of review feedback. Verify before implementing. No performative agreement. |

### Infrastructure

| Skill | What It Does |
|-------|-------------|
| **using-analysis-worktrees** | Isolated git worktrees with data seeding. Parallel analysis without branch switching. |
| **worktree-data-sync** | Sync non-git data between worktrees (seed, diff, apply modes). |
| **semantic-merge** | Intent-based branch integration. Classifies conflicts by research impact. Escalates methodology decisions to user. |
| **agent-orchestration** | Multi-agent dispatch: parallel subagents for independent tasks, Agent Teams for iterative workflows. |

### Meta

| Skill | What It Does |
|-------|-------------|
| **using-superRA** | Session startup. Cross-session detection. Skill discovery and activation rules. |
| **writing-skills** | Create new skills using test-driven methodology. |

## Agents

| Agent | Role |
|-------|------|
| **reviewer** | Prototype reviewer agent. Verifies work independently using APPROVE/REVISE protocol. Dispatched with a skill and domain reference per stage. |
| **implementer** | Prototype implementer agent. Executes tasks with data-first discipline. Dispatched with a skill and domain reference per stage. |

## Key Design Decisions

**Agent-owned doc updates.** Each agent commits its doc changes atomically with its work. The implementer commits code + PLAN.md status + RESULTS_UPDATE.md findings in a single commit. Reviewers commit review notes and APPROVED status separately. No orchestrator transcription step.

**Review status protocol.** Tasks in PLAN.md carry a status line: `IMPLEMENTED` (code done, awaiting review), `REVISE (data integrity)` or `REVISE (implementation)` (reviewer found issues — data integrity REVISE blocks implementation review from starting), `APPROVED` (both reviews passed). A fresh session can tell exactly where each task stands.

**Two-stage review.** Data integrity first, implementation correctness second. Data review must pass before implementation review begins. Review is never skipped — even in direct execution mode.

**Scope rule.** Agents only edit their own task's sections in PLAN.md and RESULTS_UPDATE.md. Never touch other tasks.

**RA framing.** The agent is a Research Assistant implementing the researcher's ideas, not judging methodology. It executes, validates, and escalates — but the researcher decides the approach.

**Lean agent definitions.** Two prototype agents (implementer, reviewer) define roles, not rules. Domain-specific checklists come from reference files read at dispatch time. Every agent loads `superRA:econ-data-analysis` via the Skill tool for data discipline. One source of truth, easy to maintain.

## Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| **session-start** | Session start, `/clear`, `/compact` | Inject using-superRA skill, check for Agent Teams availability |
| **merge-guard** | Before any `git merge/rebase/cherry-pick` | Remind to use semantic-merge skill |

## Philosophy

- **Data-first** — Understand before transforming. Always.
- **Reproducibility is a requirement** — Drift tests, pipeline files, committed code. Not optional.
- **Evidence over claims** — Run the pipeline before saying it works.
- **Session resilience** — PLAN.md + RESULTS_UPDATE.md + git = complete handoff.
- **Researcher decides, agent implements** — Methodology is not the agent's call.

## Upstream

superRA is a fork of [Superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://blog.fsck.com). The upstream project provides the plugin infrastructure, skill system, and several general-purpose skills that superRA inherits and extends.

## License

MIT License — see LICENSE file for details.
