# Thorough Planning

Load when depth tier is "thorough."

Thorough planning replaces the inline Phase 1 exploration with parallel read-only agents, optionally extends Phase 3 with multi-perspective design agents, identifies critical files before handoff, and adds an agent review step in Phase 4. Phase 2 (domain setup) is unchanged and still runs after exploration synthesis.

## Exploration Dispatch

During Phase 1, dispatch 2-4 exploration agents in parallel, each covering a distinct area and reporting findings without writing or committing. Use two agents for one codebase area, four for independent areas or an unfamiliar project. Common splits (adapt to what the Entry Assessment surfaced):

- **Project structure and conventions** — directory layout, build system, existing patterns, `CLAUDE.md` / `README.md` files, test infrastructure.
- **Relevant code and data** — existing scripts, data files and their schemas, pipeline artifacts, intermediate outputs.
- **History and prior work** — git log for the affected areas, past approaches, related tasks in `superRA/` if one exists.
- **Domain-specific survey** — data inventory for analysis work, existing model notes for theory work, manuscript structure for writing work.

**Dispatch shape.** Exploration agents skip the canonical task-scoped template — they have no task path or stage. Dispatch a read-only exploration agent (consult the harness adapter reference for the harness-specific agent type) with the exploration objective and scope as plain prose in the prompt body:

```
Explore: Map the data pipeline in `src/analysis/`: what scripts exist, what each
  produces, what the dependency order is, and what data files they read.
  Focus on `src/analysis/` and `data/processed/`.
```

Being read-only, these agents are compatible with plan mode where the harness allows subagent dispatch during it.

## Exploration Synthesis

After all exploration agents return, synthesize before Phase 2 or Phase 3. This step is not delegated — its output is the project understanding that feeds task design.

1. **Consolidate findings.** Identify overlaps, contradictions, and gaps across the reports.
2. **Map to the work.** Classify each finding: directly relevant, changes the approach, surprising and needs investigation, or background only.
3. **Reassess the entry assessment.** Drop to standard depth if the work is simpler than expected; confirm thorough if more complex; adjust placement if exploration moved it.
4. **Fill gaps.** If a critical area went uncovered and matters for task design, dispatch a targeted follow-up agent before proceeding.

## Multi-Perspective Design (Optional)

Most thorough planning uses parallel exploration but single-agent design — the main agent designs the tree itself after synthesis. Add a second round of parallel design agents only when one of these holds:

- The work spans 2+ independent codebase areas needing separate architectural consideration (e.g., a pipeline refactor and a model redesign that must eventually compose).
- Genuinely different viable approaches exist and the best choice depends on tradeoffs the main agent cannot resolve alone.
- The scope is large enough that one agent designing the full tree would exceed useful context.

Do not use it when the work is large but structurally straightforward (many tasks, one approach), when the "perspectives" are really parts of one sequential pipeline, or when a single pass with the exploration findings suffices.

**Dispatch shape.** Design agents use the same lightweight read-only exploration shape. Put the design objective plus the relevant exploration findings and constraints in the prompt body, and ask for task titles, objectives, dependencies, and expected outputs as structured text with no files created:

```
Explore: Propose a task tree for rebuilding the data pipeline in `src/data/`.
  Consider: the file inventory from exploration shows 12 raw CSVs and 3
  intermediate parquets; existing conventions use Julia scripts; the pipeline
  must produce a merged panel dataset. Return task titles, objectives,
  dependencies, and expected outputs as structured text. Do not create files.
```

For a project needing both a pipeline rebuild and a new estimation model, dispatch one agent per area (pipeline in `src/data/`, model in `src/model/`), each scoped to its own exploration findings and constraints.

**Reconciliation.** The main agent reconciles competing designs into a unified task tree. Reconciliation typically surfaces:

- **Shared assumptions** that both designs made independently (good — confirms the approach).
- **Interface disagreements** — where one design expects an output format the other does not produce. Resolve by adjusting the task objectives.
- **Genuine tradeoffs** — where the designs propose fundamentally different approaches and the right choice depends on research intent. These are substantive questions for the user per `superplan §Substantive Questions`. Present the tradeoff with the competing proposals as evidence, let the user decide, then fold the decision into the task tree.

## Critical Files for Implementation

After Phase 3, identify 3-5 files central enough that implementation agents should prioritize understanding them.

**What qualifies as critical:**

- Files that multiple tasks will read or modify.
- Central configuration or convention files that shape how all tasks execute.
- Existing code that the new work must integrate with or extend.
- Data files or schemas that define the structure downstream tasks depend on.

**Format.** Add a `## Critical Files` section to the root `task.md`:

```markdown
## Critical Files

- [`src/analysis/merge.jl`](src/analysis/merge.jl) — central merge logic; tasks 02 and 03 extend this
- [`data/raw/README.md`](data/raw/README.md) — data dictionary; all data tasks reference this schema
- [`CLAUDE.md`](CLAUDE.md) — project conventions that shape every task's implementation
```

Keep it to 3-5 files, one line each with a brief reason — a prioritization aid, not a complete inventory.

## Planning Review

The planning-review step is owned by `superplan §Agent Review`. Provision the reviewer with the context behind the design decisions: the exploration synthesis for handoff-readiness, the relevant design rationale or domain context for design-review. The reviewer's mechanics (verdict, note ownership, edit scope) live in [planning-review.md](planning-review.md).

## Incremental Refinement

A thorough pass is not one-shot. Refine the tree afterward — on user feedback, exploration findings not absorbed the first time, or Phase 2 domain-gate results — using quick-depth mechanics (inline objective edits, adding or removing subtasks, adjusting dependencies) under the standard `superplan §User Feedback and Changing the Task Tree` protocol. The heavy exploration is already done.

If refinement reveals a whole area was missed, dispatch a targeted exploration agent for just that area rather than re-running the full parallel exploration.
