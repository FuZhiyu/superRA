# Thorough Planning

Load when depth tier is "thorough."

Thorough planning replaces inline Phase 1 exploration with parallel read-only agents, optionally extends Phase 3 with multi-perspective design agents, identifies critical files before handoff, and adds an agent review step in Phase 4. Phase 2 (domain setup) is unchanged and still runs after exploration synthesis.

## Exploration Dispatch

In Phase 1, dispatch 2-4 exploration agents in parallel, each covering a distinct area and reporting findings without writing or committing. Two agents for one codebase area, four for independent areas or an unfamiliar project. Common splits (adapt to the Entry Assessment):

- **Project structure and conventions** — directory layout, build system, existing patterns, `CLAUDE.md` / `README.md`, test infrastructure.
- **Relevant code and data** — scripts, data files and schemas, pipeline artifacts, intermediate outputs.
- **History and prior work** — git log for the affected areas, past approaches, related `superRA/` tasks.
- **Domain-specific survey** — data inventory for analysis work, model notes for theory work, manuscript structure for writing work.

**Dispatch shape.** Exploration agents skip the canonical task-scoped template — no task path, no stage. Dispatch a read-only exploration agent (agent type: harness adapter reference) with objective and scope as plain prose:

```
Explore: Map the data pipeline in `src/analysis/`: what scripts exist, what each
  produces, what the dependency order is, and what data files they read.
  Focus on `src/analysis/` and `data/processed/`.
```

Read-only, so compatible with plan mode where the harness allows subagent dispatch during it.

## Exploration Synthesis

Synthesize after all agents return, before Phase 2 or 3. Not delegated — its output is the project understanding that feeds task design. The exploration split is an evidence partition, not a task partition: cut tasks by edit surface, not by which agent or report section a finding came from.

1. **Consolidate findings.** Overlaps, contradictions, gaps across the reports.
2. **Map to the work.** Per finding: directly relevant, changes the approach, surprising and needs investigation, or background only.
3. **Reassess the entry assessment.** Drop to standard depth if simpler than expected; confirm thorough if more complex; adjust placement if exploration moved it.
4. **Fill gaps.** Critical uncovered area that matters for task design: dispatch a targeted follow-up agent first.

## Multi-Perspective Design (Optional)

Default is parallel exploration with single-agent design — the main agent designs the tree after synthesis. Add a second round of parallel design agents only when:

- The work spans 2+ independent codebase areas needing separate architectural consideration (e.g. a pipeline refactor and a model redesign that must eventually compose).
- Genuinely different viable approaches exist and the choice depends on tradeoffs the main agent cannot resolve alone.
- One agent designing the full tree would exceed useful context.

Skip it when the work is large but structurally straightforward (many tasks, one approach), when the "perspectives" are parts of one sequential pipeline, or when a single pass with the exploration findings suffices.

**Dispatch shape.** Same lightweight read-only exploration shape: design objective plus relevant exploration findings and constraints in the prompt body; ask for task titles, objectives, dependencies, and expected outputs as structured text, no files created.

```
Explore: Propose a task tree for rebuilding the data pipeline in `src/data/`.
  Consider: the file inventory from exploration shows 12 raw CSVs and 3
  intermediate parquets; existing conventions use Julia scripts; the pipeline
  must produce a merged panel dataset. Return task titles, objectives,
  dependencies, and expected outputs as structured text. Do not create files.
```

One agent per area, each scoped to its own findings and constraints.

**Reconciliation.** The main agent reconciles competing designs into one tree. What surfaces:

- **Shared assumptions** both designs made independently — confirms the approach.
- **Interface disagreements** — one design expects an output format the other does not produce. Resolve by adjusting task objectives.
- **Genuine tradeoffs** — fundamentally different approaches whose choice depends on research intent. A frontier question for the researcher (`superplan §Grilling`), carrying the competing proposals as its evidence.

## Critical Files for Implementation

After Phase 3, identify 3-5 files central enough that implementation agents should prioritize understanding them.

**Qualifies as critical:**

- Read or modified by multiple tasks. Three or more tasks modifying one file: re-cut by edit surface (`task-tree-design.md` §Splitting Tasks) before listing it.
- Central configuration or convention files shaping how all tasks execute.
- Existing code the new work must integrate with or extend.
- Data files or schemas defining structure downstream tasks depend on.

**Format.** A `## Critical Files` section in the root `task.md`:

```markdown
## Critical Files

- [`src/analysis/merge.jl`](src/analysis/merge.jl) — central merge logic; tasks 02 and 03 extend this
- [`data/raw/README.md`](data/raw/README.md) — data dictionary; all data tasks reference this schema
- [`CLAUDE.md`](CLAUDE.md) — project conventions that shape every task's implementation
```

3-5 files, one line each with a brief reason — a prioritization aid, not an inventory.

## Planning Review

`superplan §Agent Review` owns the step. Provision the reviewer with the context behind the design decisions: the exploration synthesis for handoff-readiness, the relevant design rationale or domain context for design-review. Reviewer mechanics: [planning-review.md](planning-review.md).

## Incremental Refinement

Refine the tree afterward — on user feedback, unabsorbed exploration findings, or Phase 2 domain-gate results — with quick-depth mechanics (inline objective edits, adding or removing subtasks, adjusting dependencies) under `superplan §User Feedback and Changing the Task Tree`.

A whole area missed: dispatch a targeted exploration agent for that area, not the full parallel exploration again.
