# superRA

superRA is a complete economic research workflow for AI coding agents, built as a fork of [Superpowers](https://github.com/obra/superpowers). It turns your coding agent into a disciplined Research Assistant that follows data-first principles, enforces reproducibility, and maintains full session-to-session handoff — so you never lose work when context runs out.

## Why superRA?

AI agents are eager but undisciplined. They skip data description, merge without checking row counts, and declare "looks fine" without verification. In economic research, these shortcuts produce wrong results that look right.

superRA enforces a single non-negotiable rule — the **Iron Law of Data Analysis**:

> **NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION**

Every data operation follows a Describe-Analyze-Doc cycle. Every task gets a two-stage review (data integrity, then implementation correctness). Every session leaves enough state in PLAN.md and RESULTS.md that a fresh agent can pick up exactly where the last one stopped.

## How It Works

superRA activates automatically. When your agent sees a research task, it doesn't jump into code — it follows a four-phase macro workflow: **PLAN → IMPLEMENT → VALIDATE → INTEGRATE**.

```
PLAN            planning-workflow (Phase 1 inventory → Phase 2 plan creation)
                Inventory data (hard gate). Break work into tasks with code at every step.
                Output: PLAN.md + RESULTS.md (living handoff documents)
                    |
IMPLEMENT       execution-workflow (implementer agent per task)
                Follow econ-data-analysis discipline: Describe → Analyze → Doc.
                Atomic commit per task: code + PLAN.md status + RESULTS.md findings.
                    |
VALIDATE        execution-workflow (reviewer agent after each task)
                Two-stage review: data integrity → implementation correctness.
                REVISE loops until APPROVED. Review is never skipped.
                    |
INTEGRATE       integration-workflow → merge-workflow (uses semantic-merge)
                Verify reproducibility. Create drift tests. Refactor for codebase.
                Integration review. Generate report. Merge or PR.
```

Each task produces an atomic commit. If the session dies at any point, the next session reads PLAN.md + RESULTS.md + git state and picks up exactly where the last one stopped.

## Design Principles

Four workflow principles are baked into every skill in the repo. Every contribution is evaluated against them (see `CLAUDE.md` for the full version).

1. **Enforced implementer–reviewer pair at every step.** No result is accepted until a reviewer signs off. Two-stage review during execution (data integrity → implementation correctness), drift-test and integration reviews before merge, and a fresh integration review after semantic-merge. Review is never skipped. The reviewer's role is adversarial — flag everything, err on the side of over-criticism. The orchestrator arbitrates with big-picture context, filtering through the reviewer's over-critical bias and overruling with documented reasoning when warranted.

2. **Handoff docs are the auditable record AND the continuation point.** All material findings, decisions, and results land in committed `PLAN.md` / `RESULTS.md` *before* they appear in any chat reply. Any fresh agent can resume work from the docs + git state alone — no prompt history required. Atomic commits bundle code + doc edits together.

3. **Fast early, strict before merge. Semantic merges always.** Analysis code is written for speed during implementation — no codebase-fit checks at interim checkpoints. Refactoring, drift tests, codebase integration, and documentation finalization (maturing RESULTS.md and auditing project docs) happen only when the user chooses to merge. Every merge into main runs through `semantic-merge`, never a bare `git merge` / `rebase` / `cherry-pick`.

4. **Autonomous with human in the loop.** The agent drives the workflow forward on its own between legitimate stop points — no "should I continue?" check-ins on approved plans. It stops, and uses `AskUserQuestion` when available, only for hard blockers, decisions beyond the RA's authority (methodology, scope, research intent), or user-defined milestones. Every user decision at a stop point is logged into `PLAN.md` before the agent acts on it.

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

superRA's skills split into four categories. The directory layout stays flat (one `skills/<name>/SKILL.md` per skill); `skills/CATEGORIES.md` is the authoritative grouping index.

- **Workflow skills** — domain-agnostic choreography for each phase. What agent to dispatch, in what sequence, with what handoff rules. Reused across every domain vertical.
- **Domain skills** — vertical-specific discipline (today: data analysis). Loaded by workflow skills when a task touches the matching domain. Organized with stage-scoped references so only the relevant chunk loads per phase.
- **Utility skills** — reusable, domain-neutral tools. Handoff-doc discipline, report formatting, notebook rendering, worktree management, semantic merge, verification.
- **Meta skills** — session bootstrap and skill authoring.

### Workflow

| Skill | Phase | What It Does |
|-------|-------|-------------|
| **planning-workflow** | PLAN | Scope check, task decomposition, self-review, execution handoff. Points at the active domain skill for domain-specific gates and templates. |
| **execution-workflow** | IMPLEMENT + VALIDATE | Per-task dispatch, two-stage review loop with orchestrator-discipline filter, pipeline + reproducibility verification, 4-option completion menu. |
| **integration-workflow** | INTEGRATE (pre-merge) | Drift-test creation, refactor-review loop, doc finalization (mature RESULTS.md into permanent form, audit project-level CLAUDE.md / AGENTS.md / README.md). |
| **merge-workflow** | INTEGRATE (merge) | Update analysis branch via semantic-merge, post-merge verification (drift tests + fresh integration review), local merge or PR push, worktree cleanup. |
| **agent-orchestration** | cross-cutting | Multi-agent dispatch patterns: parallel subagents for independent tasks, Agent Teams for iterative workflows. |

### Domain — Data Analysis

| Skill | What It Does |
|-------|-------------|
| **econ-data-analysis** | Iron Law (no transformation without prior description). Describe-Analyze-Doc cycle. Diagnostics-for-validity philosophy. Pitfall catalogs for merges, time series, aggregations, filtering, variable construction, missing data. Red Flags table. Stage-scoped references load per phase: `planning.md` (Data Inventory hard gate + sensitivity design), `integrate-drift-tests.md` (drift-test construction), `data-robustness-checklist.md` (robustness menu). |

Future verticals — theory/modeling, literature review, simulation, writing/paper drafting — are planned; see the Roadmap section at the bottom.

### Utility

| Skill | What It Does |
|-------|-------------|
| **handoff-doc** | Document-level discipline for PLAN.md / RESULTS.md — six principles (latest-state-only, inline-edit, task-block structure, ownership-by-role, what-changed deltas, doc-is-the-record), stale-content checklist, figure embedding rule. Progressive-reveal references carry full PLAN.md and RESULTS.md anatomy. Single source of truth for doc mechanics. |
| **verification-before-completion** | No completion claims without fresh verification evidence. Prevents "looks fine" from reaching merge. |
| **script-to-notebook** | Cell organization, markdown narrative, and rendering for analysis scripts. Python (jupytext) and Julia (QuartoNotebookRunner). |
| **refactor-and-integrate** | Three integration-phase checklists: `drift-test-quality.md`, `codebase-integration.md`, `merge-quality.md`. Standalone-invokable for any refactoring task. |
| **report-in-markdown** | Format discipline for markdown reports with figures, LaTeX math, tables. Lean SKILL.md body; three references loaded on demand: `baseline-io.md`, `rich-content.md`, `final-form.md`. |
| **semantic-merge** | Intent-based branch integration. Classifies conflicts by research impact, escalates methodology decisions to the user. Invoked by `merge-workflow` Step 1 and by the merge-guard hook. |
| **using-analysis-worktrees** | Isolated git worktrees with data seeding. Parallel analysis without branch switching. |
| **worktree-data-sync** | Sync non-git data between worktrees (seed, diff, apply modes). |
| **implementer-protocol** | Alias skill — loads the implementer agent protocol when the main agent implements work directly. |
| **reviewer-protocol** | Alias skill — loads the reviewer agent protocol when the main agent reviews work directly. |

### Meta

| Skill | What It Does |
|-------|-------------|
| **using-superRA** | Session startup, cross-session detection, skill discovery rules, workflow principles the orchestrator internalizes. |
| **writing-skills** | Create or modify skills using test-driven methodology. |

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

**Agent-owned doc updates.** Each agent commits its doc changes atomically with its work. The implementer commits code + PLAN.md status + RESULTS.md findings in a single commit. Reviewers commit review notes and APPROVED status separately. No orchestrator transcription step.

**Review status protocol.** Tasks in PLAN.md carry a status line: `IMPLEMENTED` (code done, awaiting review), `REVISE (data integrity)` or `REVISE (implementation)` (reviewer found issues — data integrity REVISE blocks implementation review from starting), `APPROVED` (both reviews passed). A fresh session can tell exactly where each task stands.

**Two-stage review.** Data integrity first, implementation correctness second. Data review must pass before implementation review begins. Review is never skipped — even in direct execution mode.

**Scope rule.** Agents only edit their own task's sections in PLAN.md and RESULTS.md. Never touch other tasks.

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
- **Session resilience** — PLAN.md + RESULTS.md + git = complete handoff.
- **Researcher decides, agent implements** — Methodology is not the agent's call.

## Upstream

superRA is a fork of [Superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://blog.fsck.com). The upstream project provides the plugin infrastructure, skill system, and several general-purpose skills that superRA inherits and extends.

## License

MIT License — see LICENSE file for details.
