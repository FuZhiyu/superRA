---
name: using-superra
description: Master skill for superRA agents. Carries workflow principles, skill inventory, and the Stage → skill Load Manifest. Must invoke at the start of any superRA workflow (planning, execution, integration, merge) before dispatching work or touching handoff docs.
---

Loaded by all agents at dispatch time.

## Code-Change Defaults

These defaults apply whenever you write, review, or refactor code.

1. **Surface assumptions and ambiguity early.** Do not silently choose between materially different interpretations. State the assumption you are making, name meaningful tradeoffs, and point out a simpler path when one exists. Ask only when the ambiguity changes correctness, scope, or a decision that belongs to the researcher.

2. **Prefer the minimum code that solves the task.** No speculative features, abstractions, configurability, or defensive branches that were not requested. If a straightforward implementation works, use it.

3. **Keep edits surgical.** Touch only what the task requires. Match the surrounding style. Do not refactor adjacent code, comments, or formatting unless the task requires it. Remove imports, variables, and helper code only when your own change made them unused; mention unrelated dead code instead of deleting it.

## Runtime Workflow Map

SuperRA work moves through **PLAN -> IMPLEMENT -> INTEGRATE**:

1. `superplan` creates or revises the `superRA/` task tree, records researcher decisions, and declares which task-local statuses or workflow rollups a plan change invalidates.
2. `superimplement` executes task blocks through the implementer-reviewer loop, then verifies reproducibility and records the researcher's completion disposition before integration can begin.
3. `superintegrate` protects key results, syncs and refactors against the integration base, matures documentation, and performs the final merge / PR / cleanup action.

The map is ordered, but re-entry is normal. A changed task, reviewer finding, scope revision, or interrupted session re-enters at the earliest invalid layer for the affected task frontier while preserving unrelated approved work. The main-agent Workflow Frontier Resolver adds four things agents must do consistently: inspect durable evidence, compute the affected frontier, route to the workflow that owns the earliest invalid layer, and enforce the non-negotiable gates before advancement.

## Commit Hygiene

Any agent that stages a commit — main agent, orchestrator, or subagent — stages **only the files it modified this turn**. Untracked files not your work (editor scratch, `__pycache__`, `.DS_Store`, harness artifacts, or other agents' in-flight edits in a shared worktree) show up in `git status`; `git add -A/./-u` sweeps them in silently and produces cross-agent commit contamination that is hard to unwind.

Before staging:

1. Run `git status` and list every modified/new file. For each, decide: did I touch this file (directly via Write/Edit) in this turn?
2. If yes -> stage it by exact path: `git add path/to/file`.
3. If no -> leave it untouched. Do NOT `git add -A`, `git add .`, or `git add -u`.
4. Before `git commit`, run `git diff --cached` and confirm only your edits are staged. If you see unexpected content, unstage it with `git restore --staged path/to/file`.

If you see unfamiliar uncommitted changes and cannot tell whether they are legitimate pending work (from the main agent between dispatches, or the user editing manually) or stale junk, stop and ask the orchestrator (if you are a subagent) or the user (if you are the main agent) — do not unilaterally discard or commit them.

## Task Interface

Handoff runs through the `superRA/` task tree — `task.md` files with YAML frontmatter and `##` body sections. Reading and editing your assigned task needs only this section.

**Read** with `superra task read <path>`, not a bare `Read` of the file — it injects the inherited ancestor context and sibling dependency status that a standalone `task.md` lacks, and surfaces any unresolved comments anchored to the task so you act on them.

**Edit** the `task.md` directly with Read/Edit tools. Edit only what your role owns; raise another role's content rather than overwriting it — per-role ownership is in each role spec's §What You Own.

**Editing principles:**

- Keep the task at latest state, not a log — edit in place and delete superseded content; no "Update:" / "Previously…" blocks or strikethroughs.
- Doc before report — findings, caveats, and evidence land in the task body before any status return.
- Write the body sections you own (`## Results`, `## Review Notes`) as a self-contained, human-readable account a reader can follow standalone — with the links and embedded figures that aid understanding (see `report-in-markdown`) — not a terse changelog. The change summary belongs in the commit, not the body.

For tree-level operations (query/frontier/DAG, scaffolding, dashboard, migration), load `superRA:task-system`.

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
| Utility | `report-in-markdown` | Markdown style guide for any agent writing markdown — always-loaded alongside `using-superra`; on-demand references cover figures, LaTeX math, and tables. |
| Utility | `semantic-merge` | Tools for semantic coherence in branch integration — intent investigation, role classification, conflict resolution, stale-reference detect-and-resolve, propagation-to-coherence — with workflow sync author/reviewer mode references and standalone merge mode. |
| Utility | `worktree-data-sync` | Non-git data sync between existing worktrees (seed, diff, apply) and data teardown. Worktree lifecycle lives in `agent-orchestration/references/worktree-harness-fallback.md`. |
| Utility | `task-system` | Load-on-demand tree tooling for the `superRA/` hierarchy — query/frontier/DAG, scaffolding and restructuring, dashboard, and legacy `PLAN.md` / `RESULTS.md` migration. The executing-agent read/edit interface is §Task Interface above, not this skill. |
| Utility | `codex-superra-setup` | Generate and install the named `superra_implementer` / `superra_reviewer` Codex custom agents into `~/.codex/agents/` (global) or `.codex/agents/` (project). |
| Utility | `zotero-paper-reader` | User-invocable standalone skill — search, retrieve, and analyze papers from a Zotero library. Not loaded by workflow agents or the Manifest; invoke directly when reading, finding, or analyzing a paper by title, author, DOI, or topic. |
| Utility | `mistral-pdf-to-markdown` | User-invocable standalone skill — convert a PDF to Markdown with image extraction via the Mistral OCR API (needs `MISTRAL_API_KEY`). The conversion step behind `zotero-paper-reader`; not loaded by workflow agents or the Manifest. |
| Meta | `using-superra` | This skill — the master skill every agent reads. |

**Composable design:** Workflow skills own sequencing; domain skills own vertical discipline; utility skills are called on demand. One source of truth per concern.

**Harness adapters:** When this skill or its references mention a Claude-specific tool name (e.g. `AskUserQuestion`, `Skill`, `TodoWrite`, `Agent(subagent_type:)`), use the harness adapter reference before interpreting the tool name.

## Execution Modes

For execution throughout the workflows, the main agent can dispatch subagents for implementation, or implement the step itself (Direct mode). Subagent mode is the recommended default and all workflows assume it. Main agents: see `references/main-agent.md §Execution Modes` for the full Direct mode contract.

## Skill-Load Manifest

For each Stage, load the listed skills. The Stage is role-independent; `subagent_type` (implementer vs reviewer) encodes role. Each loaded skill's own body carries its stage- and role-scoped reference load map — after loading a skill, follow its load map for your Stage and role.

**The "Required skills" column lists what loads *in addition to* `superRA:using-superra` and `superRA:report-in-markdown`** — the two skills every agent already loads (implementer / reviewer via frontmatter preload at dispatch time; main agent and team teammates via explicit `Skill` invocation). `report-in-markdown` is always loaded because every agent writes markdown; its body carries the shared markdown rules, with deeper format discipline in references loaded on demand.

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

`Stage: planning-review` is a reviewer-only planning pass; `skills/superplan/references/planning-review.md` owns its mode, verdict, and note-ownership mechanics.

`Stage: sync` is branch-level. `superintegrate` dispatches generic sync author / sync reviewer agents with the mode references named in that workflow; the canonical implementer/reviewer role specs do not carry Sync-specific exceptions.

### Domain add-ons

If the task matches a domain skill's description in §Skill Inventory, load that skill in addition to the generic row for the current Stage. Domain add-ons compose with the generic table; they do not replace it. These apply to both the main agents as well as subagents.

**Main agents additionally load** `references/main-agent.md` and `superRA:agent-orchestration` before dispatching subagents or touching task files. Subagents skip these — they inherit context from their dispatch.

**Unknown `Stage:` values are a dispatch error** — halt and report to the orchestrator rather than guessing a skill/reference load.

## Instruction Priority

SuperRA skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **SuperRA skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md says "skip data description for this dataset" and a skill says "always describe first," follow the user's instructions. The user is in control.

**For main agents:** You MUST proceed to read `references/main-agent.md`.
