---
name: using-superRA
description: Master skill for superRA agents. Carries workflow principles, skill inventory, and the Stage → skill Load Manifest. Invoke at the start of any superRA workflow (planning, execution, integration, merge) before dispatching work or touching handoff docs.
---

Loaded by all agents at dispatch time.

## Code-Change Defaults

These defaults apply whenever you write, review, or refactor code. They govern micro-level execution and do not replace the workflow rules above.

1. **Surface assumptions and ambiguity early.** Do not silently choose between materially different interpretations. State the assumption you are making, name meaningful tradeoffs, and point out a simpler path when one exists. Ask only when the ambiguity changes correctness, scope, or a decision that belongs to the researcher.

2. **Prefer the minimum code that solves the task.** No speculative features, abstractions, configurability, or defensive branches that were not requested. If a straightforward implementation works, use it.

3. **Keep edits surgical.** Touch only what the task requires. Match the surrounding style. Do not refactor adjacent code, comments, or formatting unless the task requires it. Remove imports, variables, and helper code only when your own change made them unused; mention unrelated dead code instead of deleting it.

## Commit Hygiene

Any agent that stages a commit — main agent, orchestrator, or subagent — stages **only the files it modified this turn**. Untracked files not your work (editor scratch, `__pycache__`, `.DS_Store`, harness artifacts, or other agents' in-flight edits in a shared worktree) show up in `git status`; `git add -A/./-u` sweeps them in silently and produces cross-agent commit contamination that is hard to unwind.

Before staging:

1. Run `git status` and list every modified/new file. For each, decide: did I touch this file (directly via Write/Edit) in this turn?
2. If yes -> stage it by exact path: `git add path/to/file`.
3. If no -> leave it untouched. Do NOT `git add -A`, `git add .`, or `git add -u`.
4. Before `git commit`, run `git diff --cached` and confirm only your edits are staged. If you see unexpected content, unstage it with `git restore --staged path/to/file`.

If you see unfamiliar uncommitted changes and cannot tell whether they are legitimate pending work (from the main agent between dispatches, or the user editing manually) or stale junk, stop and ask the orchestrator (if you are a subagent) or the user (if you are the main agent) — do not unilaterally discard or commit them.

## Handoff Docs

Every agent edits `PLAN.md` and `RESULTS.md` at some point — implementers rewrite step text and record findings, reviewers write review-notes blockquotes, orchestrators annotate with adjudication notes. The editing discipline (four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, `## Project Conventions` layout, full `PLAN.md` / `RESULTS.md` anatomy templates) lives in `superRA:handoff-doc`.

## Skill Inventory

Grouped Workflow / Domain / Utility / Meta. See `skills/CATEGORIES.md` for the full grouping index.

| Category | Skill | One-line purpose |
|---|---|---|
| Workflow | `planning-workflow` | PLAN phase: scope check, task decomposition, plan draft. |
| Workflow | `execution-workflow` | IMPLEMENT + VALIDATE: per-task dispatch, one-pass review, reproducibility, completion menu. |
| Workflow | `integration-workflow` | INTEGRATE (Phases A–D): drift tests, iterative sync + refactor, doc finalization, final merge / PR / cleanup. |
| Workflow | `agent-orchestration` | Cross-stage dispatch patterns, Dispatch Templates, reviewer-feedback handling, Review Status Reference. |
| Domain | `econ-data-analysis` | Data-analysis vertical: Iron Law, describe-analyze-validate, pitfalls, common rationalizations. |
| Utility | `handoff-doc` | Handoff-doc discipline — four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, full `PLAN.md` / `RESULTS.md` anatomy templates. Loaded on demand by agents that need the full discipline and always by doc-creators (planning-workflow Phase 2, integration-workflow Phase C doc-writer); usable standalone by a single author. |
| Utility | `refactor-and-integrate` | Drift-test, codebase-integration, and merge-quality checklists. |
| Utility | `report-in-markdown` | Format discipline for markdown reports — figures, LaTeX math, tables. |
| Utility | `semantic-merge` | Intent-based conflict resolution; escalates methodology conflicts. |
| Utility | `worktree-data-sync` | Non-git data sync between existing worktrees (seed, diff, apply) and data teardown. Worktree lifecycle lives in `agent-orchestration/references/worktree-harness-fallback.md`. |
| Meta | `using-superRA` | This skill — the master skill every agent reads. |

**Composable design:** Workflow skills own sequencing; domain skills own vertical discipline; utility skills are called on demand. One source of truth per concern. See `CLAUDE.md §Architectural pattern` for the full design map.

## Skill-Load Manifest

For each Stage, load the listed skills and references. The Stage is role-independent; `subagent_type` (implementer vs reviewer) encodes role. Role differentiation shows up explicitly on the `implementation` and `documentation` rows where the implementer and reviewer load different references.

**The "Required skills" column lists what loads *in addition to* `superRA:using-superRA`** — the master skill every agent already loads (implementer / reviewer via frontmatter preload at dispatch time; main agent and team teammates via explicit `Skill` invocation). `using-superRA` carries §Universal Principles, the Skill Inventory, the composable-design map, and this manifest. Handoff-doc editing discipline is owned by `superRA:handoff-doc`; subagents get a compact etiquette from `agents/implementer.md` / `agents/reviewer.md` step 1 and load the full skill only on demand or when creating docs from scratch.

| `Stage:` | Required skills | Stage-scoped references |
|---|---|---|
| `implementation` | active domain skill (for data analysis: `econ-data-analysis`) | domain §Three Concurrent Disciplines (teaching + shared severity-marked checklist). For data analysis: **implementer** additionally loads `econ-data-analysis/references/notebook-format.md`; **reviewer** loads SKILL.md only (the main body carries everything — §Three Concurrent Disciplines for verification, §Pitfalls for operation-specific correctness; if the dispatcher wants a specific Pitfalls subsection highlighted for review, it names it in `Additionally:`). |
| `integration` | `refactor-and-integrate`; domain skill | `codebase-integration.md` (generic); `integration.md` (data-analysis); `integrate-drift-tests.md` if drift tests exist |
| `drift-test` | `refactor-and-integrate`; domain skill | `integrate-drift-tests.md` + `drift-test-quality.md` |
| `merge` | `refactor-and-integrate` + `semantic-merge`; domain skill | `merge-quality.md` |
| `documentation` | `handoff-doc` + `report-in-markdown` | implementer role: `baseline-io.md` + `rich-content.md` + `final-form.md`; reviewer role: `final-form.md` |
| `planning-review` | `handoff-doc` + domain skill | `planning.md` (domain) |

The `merge` stage is used for standalone `semantic-merge` dispatches — a dedicated merge-proposer / merge-reviewer pair resolving a branch outside the normal integration-workflow. Inside `integration-workflow` Phase B, the implementer runs `Stage: integration` and loads `superRA:semantic-merge` when the integration reviewer's annotation calls for intent-based conflict resolution — no Stage switch needed.


**Main agents additionally load** `references/main-agent.md` and `superRA:handoff-doc` before dispatching subagents or touching PLAN.md. Subagents skip both.


## Instruction Priority

SuperRA skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **SuperRA skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md says "skip data description for this dataset" and a skill says "always describe first," follow the user's instructions. The user is in control.
