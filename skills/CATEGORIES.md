# Skill Categories

superRA skills split into four categories. The directory layout stays flat (one `skills/<name>/SKILL.md` per skill) for compatibility with Claude Code, Copilot CLI, Gemini CLI, and Codex skill loaders. This file is the authoritative grouping index — when adding a skill, place it in the right category here and in the `README.md` skill tables.

For the runtime-facing master map (universal principles, skill-discovery rules, and the Stage → required-skills / references table agents actually load), see `superRA:using-superra` §Skill Inventory and §Skill-Load Manifest. This file groups skills for contributor navigation; `using-superra` is the agent-facing authority.

## Workflow — domain-agnostic choreography

Own the procedural shape of each phase: what agent to dispatch, in what sequence, with what handoff rules. Every workflow skill is domain-neutral — when a task matches an implemented vertical such as data analysis or theory/modeling, the workflow skill instructs the agent to load the matching domain skill. Adding a new vertical means adding a domain skill, not forking these.

| Skill | Phase | Role |
|---|---|---|
| `superplan` | PLAN | Scope check, task decomposition, self-review, execution handoff. Points at the domain skill for domain-specific planning gates. |
| `superimplement` | IMPLEMENT + VALIDATE | Per-task dispatch, one-pass review loop (APPROVE / REVISE), reproducibility verification, 4-option completion menu. |
| `superintegrate` | INTEGRATE | Protect key results, Sync with the current base, Integrate/refactor the post-sync diff, Document final results, then Finish with PR / fast-forward / cleanup. |
| `agent-orchestration` | cross-cutting | Multi-agent dispatch patterns: workload balancing, parallel subagents, reviewer-feedback adjudication. |

## Domain — vertical-specific discipline

Carry the domain-specific knowledge that workflow skills invoke when a task touches that domain. Organized by reference files split by stage so the right chunk loads at the right phase. Currently implemented: data analysis, theory/modeling, and writing. The architecture is designed to grow by adding more verticals without forking the workflow skills.

| Skill | Vertical | Flagship discipline |
|---|---|---|
| `econ-data-analysis` | Data analysis | Iron Law (no transformation without prior description), three concurrent disciplines (describe-analyze-validate), diagnostics-for-validity philosophy, pitfall catalogs, common rationalizations. Stage-scoped references: `planning.md`, `integrate-drift-tests.md`, `integration.md`, `data-robustness-checklist.md`, `notebook-format.md` (+ `jupytext-guide.md` and `julia-quarto-guide.md` companions). |
| `theory-modeling` | Theory / modeling | Four-gate intuition/interpretability discipline (Objects & Notation, Assumptions, Derivations, Verification & Rendering) at creation time, plus task-level rewriting and document-internal coherence (objective-first structural rewriting, per-step local obviousness, notation/prior-result reuse, reader-perspective discipline) at integration time. Stage-scoped references: `planning.md`, `integrate-drift-tests.md`, `integration.md`, `objective-first.md`, `audience-discipline-modeling.md`, `audience-discipline-writing.md`. |
| `writing` | Writing / paper drafting | Three working modes — Review / Polish / Draft — over a single principle (preserve substance, polish prose) and parallel-dispatched per-dimension consistency reviewers. Mode references: `planning.md`, `review.md`, `polish.md`, `draft.md`. Knowledge files: `style.md`, `structure.md`, `consistency/*.md` (8 dimension files), `long-form-review.md`, `refactor-and-compile.md`, `integration.md`. |

### Future verticals (roadmap — not yet implemented)

- **Literature review** — citation integrity, claim-evidence mapping
- **Simulation** — seed discipline, sensitivity to parameter grids, stochastic reproducibility

Each future vertical plugs into the same workflow scaffolding — implementer + reviewer pair, handoff docs, autonomous-with-human-in-loop, semantic merges.

## Utility — reusable, domain-neutral tools

Agent-facing and standalone-invokable. Called by workflow skills and agent files as needed. Domain-agnostic; reusable across verticals.

| Skill | What it provides |
|---|---|
| `handoff-doc` | Handoff-doc discipline — four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, full `PLAN.md` / `RESULTS.md` anatomy templates (`plan-anatomy.md`, `results-anatomy.md`). Loaded on demand when the compact etiquette in `agents/implementer.md` / `agents/reviewer.md` step 1 is not enough, and always by doc-creators (`superplan` Phase 2, `superintegrate` Document doc-writer). Usable standalone by a single author with no subagents. |
| `result-protection` | Tools for protecting key research results from unintended changes; drift/regression tests are the current/default mechanism. Loaded by Protect / `Stage: protection` agents. |
| `refactor-and-integrate` | Tools for **codebase coherence** — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host, and supplied Sync impact as justification evidence. Loaded by integration-phase agents. |
| `report-in-markdown` | Markdown style guide for any agent writing markdown, with progressive-reveal references for figures, LaTeX math, and tables. |
| `semantic-merge` | Tools for **semantic coherence** in branch integration. Provides mode references for workflow sync authoring, workflow sync review, and standalone merge; resolves conflicts by intent, escalates intent-changing decisions to the user, detects and resolves stale references within the merge's reach, lands a merge commit plus propagation commits as needed to reach semantic coherence (every commit leaves existing protection passing), and records branch-level / task-local / file-local context explaining the approved post-sync diff. Loaded by Sync / `Stage: sync` agents. |
| `worktree-data-sync` | Non-git data sync between existing worktrees (seed, diff, apply) and data teardown. Worktree lifecycle is in `agent-orchestration/references/worktree-harness-fallback.md`. |
| `zotero-paper-reader` | Read and analyze academic papers from a Zotero library. Handles search, PDF retrieval, markdown conversion via `mistral-pdf-to-markdown`, and section-by-section analysis. User-invocable standalone; not loaded by workflow agents. |
| `mistral-pdf-to-markdown` | Convert a PDF to Markdown with image extraction via the Mistral OCR API. The conversion step behind `zotero-paper-reader`; also usable standalone for any scanned or complex-layout PDF. Needs a `MISTRAL_API_KEY`. User-invocable standalone; not loaded by workflow agents. |

## Meta — system-level

| Skill | Purpose |
|---|---|
| `using-superra` | Master skill every agent reads. Carries the distilled universal principles, code-change defaults, the Workflow / Domain / Utility / Meta skill inventory, the composable-design map, the Skill-Load Manifest (Stage → required skills + stage-scoped references), and the Execution Modes (subagent dispatch vs direct). Main-agent loads (cross-session detection, autonomy contract, handoff-doc default) live in `references/main-agent.md`. |

## Adding a Skill

1. Decide the category above. If it doesn't fit cleanly, it may belong in two places — default to the category that matches its primary caller (workflow-skills are called by orchestrators; domain-skills are called by workflow-skills; utility-skills are called by agent files and by other skills).
2. Create `skills/<name>/SKILL.md` (flat layout — no nested folders).
3. Add a row to the table above and to the matching table in `README.md`.
4. If it's a domain skill, design its `references/` folder around workflow phases so agents can load the right chunk per stage.
