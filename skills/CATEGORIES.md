# Skill Categories

superRA skills split into five categories. The directory layout stays flat (one `skills/<name>/SKILL.md` per skill) for compatibility with Claude Code, Copilot CLI, Gemini CLI, and Codex skill loaders. This file is the authoritative grouping index.

For the runtime map agents actually load — universal principles plus the Stage/Domain skill-load tables — see `superRA:using-superra` §Skill-Load Manifest. This file groups skills for contributor navigation; `using-superra` is the agent-facing authority.

## Workflow — domain-agnostic choreography

Own the procedural shape of each phase: what agent to dispatch, in what sequence, with what handoff rules. Every workflow skill is domain-neutral — a task matching an implemented vertical such as data analysis or theory/modeling gets the matching domain skill loaded. Adding a new vertical means adding a domain skill, not forking these.

| Skill | Phase | Role |
|---|---|---|
| `superplan` | PLAN | Scope check, task decomposition, self-review, execution handoff. Points at the domain skill for domain-specific planning gates. |
| `superimplement` | IMPLEMENT + VALIDATE | Autonomous execution mode: per-task dispatch, triggered review loop (APPROVE / REVISE), and the phase-exit gate — reproducibility verification plus the 4-option completion menu. |
| `superintegrate` | INTEGRATE | Choose results, permanent documentation, and protection; Sync; Mature & Consolidate the protected record; derive, approve, and execute one temporary refactoring task; then Finish. |
| `agent-orchestration` | cross-cutting | Multi-agent dispatch patterns: workload balancing, parallel subagents, reviewer-feedback adjudication. |

## Role — what a dispatched seat does

Carry the protocol for one seat on a task. A dispatch prompt's first line names the role skill; a seat the main agent fills itself loads the same one. Both pull the always-loaded `using-superra` plus the manifest's stage and domain skills.

| Skill | Seat | Role |
|---|---|---|
| `implement-task` | Implementer | Execute the objective, self-check, own `## Results` and status up to `implemented`, commit atomically, return status + SHA. |
| `review-task` | Reviewer | Verify independently against the objective and the loaded gates, own `## Review Notes` and the APPROVE / REVISE verdict, commit, return assessment + SHA. |

## Domain — vertical-specific discipline

Carry the domain-specific knowledge workflow skills invoke when a task touches that domain. Reference files split by stage so the right chunk loads at the right phase. Currently implemented: data analysis, theory/modeling, academic writing, and slide design.

| Skill | Vertical | Flagship discipline |
|---|---|---|
| `econ-data-analysis` | Data analysis | Iron Law (no transformation without prior description), three concurrent disciplines (describe-analyze-validate), diagnostics-for-validity philosophy, pitfall catalogs, common rationalizations. Stage-scoped references: `planning.md`, `integrate-drift-tests.md`, `integration.md`, `data-robustness-checklist.md`, `notebook-format.md` (+ `jupytext-guide.md` and `julia-quarto-guide.md` companions). |
| `theory-modeling` | Theory / modeling | Four-gate intuition/interpretability discipline (Objects & Notation, Assumptions, Derivations, Verification & Rendering) at creation time, plus task-level rewriting and document-internal coherence (objective-first structural rewriting, per-step local obviousness, notation/prior-result reuse, reader-perspective discipline) at integration time. Stage-scoped references: `planning.md`, `integrate-drift-tests.md`, `integration.md`, `objective-first.md`, `audience-discipline-modeling.md`, `audience-discipline-writing.md`. |
| `academic-writing` | Academic writing / paper drafting | Three working modes — Review / Polish / Draft — over a single principle (preserve substance, polish prose) and parallel-dispatched per-dimension consistency reviewers. Mode references: `planning.md`, `review.md`, `polish.md`, `draft.md`. Knowledge files: `style.md`, `structure.md`, `consistency/*.md` (8 dimension files), `long-form-review.md`, `refactor-and-compile.md`, `integration.md`. |
| `slide-design` | Research slides | Audience-context discipline for research slides — context engineering, attention management, simplification, main-vs-backup slide tradeoffs, a house Beamer starter template (`assets/beamer-starter-template.tex`), and Beamer-first layout triage for wrapped bullets, overflow, and missing assets. Stage-scoped references: `planning.md`, `beamer-techniques.md`, `beamer-overlays.md`, `layout-checks.md`, `integration.md`. |

### Future verticals (roadmap — not yet implemented)

- **Literature review** — citation integrity, claim-evidence mapping
- **Simulation** — seed discipline, sensitivity to parameter grids, stochastic reproducibility

Each plugs into the same workflow scaffolding — implementation and review discipline, task-tree handoff, autonomous-with-human-in-loop, semantic merges.

## Utility — reusable, domain-neutral tools

Agent-facing and standalone-invokable; called by workflow skills and role skills as needed.

| Skill | What it provides |
|---|---|
| `result-protection` | Tools for choosing permanent documentation, drift tests, or artifact-appropriate checks to protect key results. Loaded by Protect / `Stage: protection` agents. |
| `refactor-and-integrate` | Tools for **codebase coherence** — executing a reviewed refactoring task against the protected record, convention fit, utility reuse, consolidation, PR-friendly diffs, Project Doc Audit, and minimum net diff. Loaded by integration-phase agents. |
| `communicate` | Human-facing writing, rewriting, distillation, and review across conversation, task files, reports, reviews, and handoffs. Always loaded with `using-superra`; progressive-reveal references own structure, sentence style, rewriting, friction audits, Markdown mechanics, figures, and standalone-report IO. Academic manuscripts compose it with `academic-writing`. |
| `semantic-merge` | Tools for **semantic coherence** in branch integration. Provides mode references for workflow sync authoring, workflow sync review, and standalone merge; resolves conflicts by intent, escalates intent-changing decisions to the user, detects and resolves stale references within the merge's reach, lands a merge commit plus propagation commits as needed to reach semantic coherence (every commit leaves existing protection passing), and records the approved post-sync diff in the git log (commit messages) plus a temporary task-local `## Sync Impact` section on each affected task. Loaded by Sync / `Stage: sync` agents. |
| `task-tree` | Directory-tree task tooling — filesystem hierarchy as task hierarchy, `task.md` per task (objective + results), sibling-only dependencies, status rollup, frontier computation, DAG rendering, legacy migration from `PLAN.md` / `RESULTS.md`, live dashboard server, and static HTML export. Load-on-demand: SKILL.md is the tree-tooling layer for orchestrators/planners/contributors, with `references/commands.md` for the mutation command surface, `references/task-file-contract.md` for task-file mechanics, and `references/internals.md` for contributor-facing internals. Tree-design policy lives in `superplan/references/task-tree-design.md`. The executing-agent read/edit interface lives in `using-superra §Task Interface`, not here. |
| `worktree-data-sync` | Non-git data sync between existing worktrees (seed, diff, apply) and data teardown. Worktree lifecycle is in `agent-orchestration/references/worktree-harness-fallback.md`. |
| `zotero-paper-reader` | Read and analyze academic papers from a Zotero library, and generate citations from it. Handles search, PDF retrieval, markdown conversion via `mistral-pdf-to-markdown`, section-by-section analysis, plus BibTeX export, `\cite`/`[@key]` insertion into a draft, master-`.bib` sync, and bibliography rendering (Better BibTeX citekeys by default). User-invocable standalone; not loaded by workflow agents. |
| `mistral-pdf-to-markdown` | Convert a PDF to Markdown with image extraction via the Mistral OCR API. The conversion step behind `zotero-paper-reader`; also usable standalone for any scanned or complex-layout PDF. Needs a `MISTRAL_API_KEY`. User-invocable standalone; not loaded by workflow agents. |

## Meta — system-level

| Skill | Purpose |
|---|---|
| `using-superra` | Master workflow skill every agent reads with `communicate`. Carries commit rules, the Task Interface, and the three-axis Skill-Load Manifest (Role + Stage + Domain). Main-agent loads (workflow map, Execution Modes, cross-session detection, autonomy contract) live in `references/main-agent.md`. |

## Adding a Skill

1. Decide the category above. If it doesn't fit cleanly, it may belong in two places — default to the category that matches its primary caller (workflow-skills are called by orchestrators; domain-skills are called by workflow-skills; utility-skills are called by role skills and by other skills).
2. Create `skills/<name>/SKILL.md` — no nested folders.
3. Add a row to the table above and to the matching table in `README.md`.
4. For a domain skill, design its `references/` folder around workflow phases.
