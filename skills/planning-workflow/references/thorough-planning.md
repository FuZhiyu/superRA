# Thorough Planning

Load this reference when depth tier is "thorough." Defines the dispatch pattern for deep planning with parallel exploration and optional multi-perspective design.

Thorough planning replaces the main agent's inline Phase 1 exploration with parallel read-only agents, optionally extends Phase 3 with multi-perspective design agents, adds critical-files identification before handoff to implementation, and adds an agent review step in Phase 4. Phase 2 is the same as standard depth — domain setup still happens after exploration synthesis.

## Exploration Dispatch

During Phase 1, dispatch 2-4 exploration agents in parallel. Each agent covers a distinct area and returns findings — it reads files and reports, never writes or commits.

**Deciding count and focus.** The orchestrator chooses exploration areas based on what it learned during the Entry Assessment. Common splits:

- **Project structure and conventions** — directory layout, build system, existing patterns, `CLAUDE.md` / `README.md` files, test infrastructure.
- **Relevant code and data** — existing scripts, data files and their schemas, pipeline artifacts, intermediate outputs.
- **History and prior work** — git log for the affected areas, past approaches, related tasks in `.plan/` if one exists.
- **Domain-specific survey** — data inventory for analysis work, existing model notes for theory work, manuscript structure for writing work.

Two agents suffice when the work touches one codebase area. Four when the work spans independent areas or the project is unfamiliar. The orchestrator adapts — these are starting points, not rigid categories.

**Dispatch shape.** Exploration agents do not use the canonical task-scoped dispatch template — they have no task path or stage. They are simpler: a read-only `Explore` agent with the exploration objective and scope in the prompt body. Use `subagent_type: "Explore"` (Claude Code's built-in read-only search agent; other harnesses may use a different type name for lightweight read-only agents):

```
Agent(subagent_type: "Explore"):
  Map the data pipeline in `src/analysis/`: what scripts exist, what each
  produces, what the dependency order is, and what data files they read.
  Focus on `src/analysis/` and `data/processed/`.
```

The prompt body carries the exploration objective and any scope constraints. No structured fields beyond `subagent_type` — keep it plain.

**Example objectives** (adapt to the project):

- "Map the data pipeline in `src/analysis/`: what scripts exist, what each produces, what the dependency order is, and what data files they read."
- "Inventory the data files in `data/raw/` and `data/processed/`: file formats, approximate sizes, column schemas where inferrable, and any README or codebook files."
- "Survey `skills/planning-workflow/` and its references: current structure, cross-references to other skills, and patterns used in existing reference files."
- "Review git history for `src/model/` over the last 20 commits: what changed, what approaches were tried, any reverted work."

**Plan mode compatibility:** exploration agents are read-only and compatible with plan mode constraints where the harness supports subagent dispatch during plan mode. Their findings inform the plan file written at exit.

## Exploration Synthesis

After all exploration agents return, the main agent synthesizes before proceeding to Phase 2 (Domain Setup) or Phase 3 (Design).

**Synthesis steps:**

1. **Consolidate findings.** Read each agent's report. Identify overlaps, contradictions, and gaps.
2. **Map to the work.** For each finding, classify: directly relevant to the planned work, changes the approach, surprising and needs investigation, or background context only.
3. **Reassess entry assessment.** Exploration may reveal that placement or depth needs adjustment. If the work is simpler than expected, drop to standard depth for the remaining phases. If it is more complex, the thorough depth is confirmed.
4. **Identify gaps.** If a critical area was not covered by any exploration agent and the gap matters for task design, dispatch a targeted follow-up agent before proceeding.

The synthesis is the main agent's work — it is not delegated. The output is the main agent's understanding of the project context, which feeds directly into task design.

## Multi-Perspective Design (Optional)

Most thorough planning needs parallel exploration but single-agent design. The main agent designs the task tree itself after synthesis. Multi-perspective design adds a second round of parallel agents only when the work genuinely requires it.

**When to use:**

- The work spans 2+ independent codebase areas that need separate architectural consideration (e.g., a data pipeline refactor and a model redesign that must eventually compose).
- There are genuinely different viable approaches and the best choice depends on tradeoffs the main agent cannot resolve alone.
- The scope is large enough that a single agent designing the full tree would exceed useful context.

**When not to use:**

- The work is large but structurally straightforward (many tasks, one approach).
- The different "perspectives" are really just different parts of one sequential pipeline.
- A single pass with the exploration findings in hand is sufficient.

**Dispatch shape.** Design agents use the same lightweight shape as exploration agents — a read-only `Explore` agent with the design objective in the prompt body:

```
Agent(subagent_type: "Explore"):
  Propose a task tree for rebuilding the data pipeline in `src/data/`.
  Consider: the file inventory from exploration shows 12 raw CSVs and 3
  intermediate parquets; existing conventions use Julia scripts; the pipeline
  must produce a merged panel dataset. Return task titles, objectives,
  dependencies, and expected outputs as structured text. Do not create files.
```

Include relevant exploration findings and constraints directly in the prompt body — no separate structured fields.

**Example:** For a project needing both a data pipeline rebuild and a new estimation model:

- Agent A: "Propose a task tree for rebuilding the data pipeline in `src/data/`. Consider the current file inventory from exploration, existing conventions, and the requirement that the pipeline must produce a merged panel dataset."
- Agent B: "Propose a task tree for the new estimation model in `src/model/`. Consider the model spec from the user, existing model notes found during exploration, and the data schema the pipeline will produce."

**Reconciliation.** The main agent reconciles competing designs into a unified task tree. Reconciliation typically surfaces:

- **Shared assumptions** that both designs made independently (good — confirms the approach).
- **Interface disagreements** — where one design expects an output format the other does not produce. Resolve by adjusting the task objectives.
- **Genuine tradeoffs** — where the designs propose fundamentally different approaches and the right choice depends on research intent. These are substantive questions for the user per `planning-workflow §Substantive Questions`. Present the tradeoff with the competing proposals as evidence, let the user decide, then fold the decision into the task tree.

## Critical Files for Implementation

After the task tree is designed (Phase 3 complete), identify 3-5 files that are critical for implementation — files that implementation agents should prioritize understanding because they are central to the work.

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

Keep it short — 3-5 files, one line each with a brief reason. This is a prioritization aid for implementation agents, not a complete file inventory.

## Agent Review

At thorough depth, Phase 4 gains an agent review step between self-review and user review (see `planning-workflow §Agent Review (Thorough Depth Only)`). The main agent dispatches a reviewer agent that receives:

1. The complete `.plan/` directory (the task tree as designed).
2. The exploration synthesis from Phase 1 — the consolidated understanding of project context that informed the design.

The exploration synthesis is essential input because the reviewer needs the same project context the main agent used to make design decisions. Without it, the reviewer cannot evaluate whether the task decomposition fits the actual codebase structure, data layout, and existing conventions discovered during exploration.

**What the reviewer evaluates:**

- The self-review checklist from `planning-workflow §Self-Review` — domain coverage, placeholder scan, pipeline consistency, validation coverage, handoff test, verification coverage, dependency graph sanity, subtask coverage.
- **Structural coherence** — whether task boundaries align with the project structure found during exploration, dependencies are complete and correctly ordered, and decomposition granularity matches the complexity of each area.

The reviewer returns APPROVE or REVISE with findings. REVISE findings must be fixed before the tree is presented to the user.

## Incremental Refinement

The task tree at thorough depth is not one-shot. After the initial thorough pass, the main agent may refine the tree based on:

- User feedback on the initial design.
- Exploration findings that were not fully absorbed in the first pass.
- Domain hard gate results from Phase 2 that constrain the scope.

Each refinement round uses quick-depth mechanics — inline edits to existing task objectives, adding or removing subtasks, adjusting dependencies — even though the initial pass was thorough. The heavy exploration is already done; refinement applies the standard planning-workflow change protocol (`§User Feedback and Changing the Task Tree` for material changes, inline edits for non-material refinements).

If refinement reveals that a whole area was missed and needs its own exploration, dispatch a targeted exploration agent for that area rather than re-running the full parallel exploration.
