---
name: using-superra
description: Master skill for superRA agents. Carries workflow principles, skill inventory, and the Stage → skill Load Manifest. Must invoke at the start of any superRA workflow (planning, execution, integration, merge) before dispatching work or touching handoff docs.
---

Loaded by all agents at dispatch time.

## Code-Change Defaults

These apply whenever you write, review, or refactor code.

1. **Surface assumptions and ambiguity early.** Do not silently choose between materially different interpretations. State the assumption you are making, name meaningful tradeoffs, and point out a simpler path when one exists. Ask only when the ambiguity changes correctness, scope, or a decision that belongs to the researcher.

2. **Prefer the minimum code that solves the task.** No speculative features, abstractions, configurability, or defensive branches that were not requested. If a straightforward implementation works, use it.

3. **Keep edits surgical.** Touch only what the task requires. Match the surrounding style. Do not refactor adjacent code, comments, or formatting unless the task requires it. Remove imports, variables, and helper code only when your own change made them unused; mention unrelated dead code instead of deleting it.

## Runtime Workflow Map

SuperRA work moves through **PLAN -> IMPLEMENT -> INTEGRATE**:

1. `superplan` creates or revises the `superRA/` task tree, records researcher decisions, and declares which task-local statuses or workflow rollups a plan change invalidates.
2. `superimplement` executes task blocks through the implementer-reviewer loop, then verifies reproducibility and records the researcher's completion disposition before integration can begin.
3. `superintegrate` protects key results, syncs and refactors against the integration base, matures documentation, and performs the final merge / PR / cleanup action.

The map is ordered, but re-entry is normal. A changed task, reviewer finding, scope revision, or interrupted session re-enters at the earliest invalid layer for the affected task frontier while preserving unrelated approved work. Main agents run the §Workflow Frontier Resolver in `references/main-agent.md` to inspect durable evidence, compute the affected frontier, route to the owning workflow, and enforce gates before advancement.

## Commit Hygiene

Any agent that stages a commit — main agent, orchestrator, or subagent — stages **only the files it modified this turn**, by exact path. A shared worktree carries others' in-flight edits and scratch files (`__pycache__`, `.DS_Store`, harness artifacts) that `git add -A/./-u` would sweep in, producing cross-agent contamination that is hard to unwind.

Before staging:

1. Run `git status`; for each modified/new file decide whether you touched it via Write/Edit this turn.
2. Stage only those, by exact path: `git add path/to/file`. Never `git add -A`, `git add .`, or `git add -u`.
3. Before `git commit`, run `git diff --cached` and unstage anything you did not write with `git restore --staged path/to/file`.

If you see unfamiliar uncommitted changes and cannot tell whether they are legitimate pending work (from the main agent between dispatches, or the user editing manually) or stale junk, stop and ask the orchestrator (if you are a subagent) or the user (if you are the main agent) — do not unilaterally discard or commit them.

## Task Interface

Handoff runs through the `superRA/` task tree. Reading and editing your assigned task needs only this section.

**Read** with the committed wrapper — `./superRA/superra task read <path>` — not a bare `Read` of the file: the wrapper injects inherited ancestor context, sibling dependency status, and any unresolved comments anchored to the task. Every `<path>` is **relative to the task root and omits the `superRA/` prefix** (e.g. `task-tree/planning-redesign`).

**Edit** the `task.md` directly with Read/Edit. Edit only what your role owns; raise another role's content rather than overwriting it — per-role ownership is in each role spec's §What You Own. Flipping a child task's status cascades up to every ancestor automatically via hooks; this is intended, do not undo it.

**Editing principles:**

- Keep the task at latest state, not a log — edit in place and delete superseded content; no "Update:" / "Previously…" blocks or strikethroughs.
- Doc before report — findings, caveats, and evidence land in the task body before any status return.
- Write the body sections you own (`## Results`, `## Review Notes`) as a self-contained account a reader can follow standalone, with links and embedded figures (see `report-in-markdown`). The change summary belongs in the commit, not the body.

For tree-level operations (query/frontier/DAG, scaffolding, dashboard, migration), load `superRA:task-tree`.

## Skill Inventory

Grouped Workflow / Domain / Utility / Meta. See `skills/CATEGORIES.md` for the full grouping index.

| Category | Skill | One-line purpose |
|---|---|---|
| Workflow | `superplan` | PLAN phase: scope check, task decomposition, plan draft. |
| Workflow | `superimplement` | IMPLEMENT + VALIDATE: per-task dispatch, one-pass review, reproducibility, completion menu. |
| Workflow | `superintegrate` | INTEGRATE: Protect, Sync, Integrate, Document, Finish. |
| Workflow | `agent-orchestration` | Cross-stage dispatch patterns, Dispatch Templates, reviewer-feedback handling, Review Status Reference. |
| Domain | `econ-data-analysis` | Economic / financial / panel data — importing, cleaning, merging, filtering, constructing variables, summary stats, regressions (CRSP, Compustat, WRDS, etc.). Iron Law, describe-analyze-validate, pitfalls, common rationalizations. |
| Domain | `theory-modeling` | Theoretical / mathematical modeling — derivations, equilibrium setup, symbolic manipulation, proofs, comparative statics, or simple numerical verification of derived formulas. Four-gate intuition/interpretability checklist (Objects & Notation, Assumptions, Derivations, Verification & Rendering), notation and assumption discipline, proof and numerical verification. |
| Domain | `writing` | Editing, polishing, proofreading, consistency-checking, refactoring wording, or drafting technical sections of an academic paper or manuscript. Review / Polish / Draft modes, preserve-substance-polish-prose principle, per-dimension consistency reviewers. |
| Utility | `result-protection` | Tools for protecting key results from unintended changes; drift tests are the current/default mechanism. |
| Utility | `refactor-and-integrate` | Tools for codebase coherence — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff, and supplied Sync impact as justification evidence. |
| Utility | `report-in-markdown` | Markdown style guide for any agent writing markdown — always-loaded alongside `using-superra`; on-demand references cover figures, LaTeX math, and tables; ships a render-integrity self-diagnose CLI (`scripts/check_markdown.py`). |
| Utility | `semantic-merge` | Tools for semantic coherence in branch integration — intent investigation, role classification, conflict resolution, stale-reference detect-and-resolve, propagation-to-coherence — with workflow sync author/reviewer mode references and standalone merge mode. |
| Utility | `worktree-data-sync` | Non-git data sync between existing worktrees (seed, diff, apply) and data teardown. Worktree lifecycle lives in `agent-orchestration/references/worktree-harness-fallback.md`. |
| Utility | `task-tree` | Load-on-demand tree tooling for the `superRA/` hierarchy — query/frontier/DAG, scaffolding and restructuring, dashboard, and legacy `PLAN.md` / `RESULTS.md` migration. The executing-agent read/edit interface is §Task Interface above, not this skill. |
| Utility | `codex-superra-setup` | Generate and install the named `superra_implementer` / `superra_reviewer` Codex custom agents into `~/.codex/agents/` (global) or `.codex/agents/` (project). |
| Utility | `zotero-paper-reader` | User-invocable standalone skill — search, retrieve, and analyze papers from a Zotero library, and generate citations from it (BibTeX export, `\cite`/`[@key]` insertion, master-`.bib` sync, bibliography rendering — Better BibTeX citekeys by default). Not loaded by workflow agents or the Manifest; invoke directly when reading, finding, or analyzing a paper, or when citing one. |
| Utility | `mistral-pdf-to-markdown` | User-invocable standalone skill — convert a PDF to Markdown with image extraction via the Mistral OCR API (needs `MISTRAL_API_KEY`). The conversion step behind `zotero-paper-reader`; not loaded by workflow agents or the Manifest. |
| Meta | `using-superra` | This skill — the master skill every agent reads. |

**Harness adapters:** When this skill or its references name a Claude-specific tool (e.g. `AskUserQuestion`, `Skill`, `TodoWrite`, `Agent(subagent_type:)`), consult the harness adapter reference before interpreting it.

## Execution Modes

For execution throughout the workflows, the main agent can dispatch subagents for implementation, or implement the step itself (Direct mode). Subagent mode is the recommended default and all workflows assume it. Main agents: see `references/main-agent.md §Execution Modes` for the full Direct mode contract.

## Skill-Load Manifest

For each Stage, load the listed skills. The Stage is role-independent; `subagent_type` (implementer vs reviewer) encodes role. After loading a skill, follow its body's stage- and role-scoped reference load map.

**The "Required skills" column lists what loads *in addition to* `superRA:using-superra` and `superRA:report-in-markdown`** — the two skills every agent already loads (subagents via frontmatter preload, main agent and teammates via explicit `Skill` invocation).

### Generic (stage-driven)

Apply to every dispatch regardless of domain.

| `Stage:` | Emitted by | Required skills |
|---|---|---|
| `planning-review` | `superplan` | `skills/superplan/references/planning-review.md` (reviewer mechanics) |
| `implementation` | `superimplement` | — |
| `protection` | `superintegrate` Protect | `result-protection` |
| `sync` | `superintegrate` Sync | `semantic-merge` |
| `integration` | `superintegrate` Integrate | `refactor-and-integrate` |
| `documentation` | `superintegrate` Document | `report-in-markdown` |

`Stage: planning-review` is a reviewer-only planning pass; its mechanics live in `skills/superplan/references/planning-review.md`.

`Stage: sync` is branch-level: `superintegrate` dispatches generic sync author / sync reviewer agents with the mode references it names; the canonical role specs carry no Sync-specific exceptions.

### Domain add-ons

If the task matches a domain skill's description in §Skill Inventory, load that skill in addition to (not instead of) the generic Stage row. This applies to main agents and subagents alike.

**Main agents additionally load** `references/main-agent.md` and `superRA:agent-orchestration` before dispatching subagents or touching task files. Subagents inherit this context from their dispatch.

**Unknown `Stage:` values are a dispatch error** — halt and report to the orchestrator rather than guessing a skill/reference load.

## Instruction Priority

SuperRA skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **SuperRA skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

When a skill says "always describe first" but CLAUDE.md says "skip data description for this dataset," follow the user. The user is in control.

**Main agents:** continue to `references/main-agent.md`.
