---
name: planning-workflow
description: "Requires `superRA:using-superra` loaded first. Use when starting new research work, adding work to an existing task tree, or revising an existing task tree. Triggers include \"let's analyze X\", \"write me a plan for Y\", \"we're starting a new project on Z\", \"before writing any code\", an empty working directory for a new task, or an existing `.plan/` that needs new tasks or restructuring. Sits at the PLAN phase of the superRA PLAN -> IMPLEMENT -> INTEGRATE workflow; hands off to `implementation-workflow` once the task tree is approved. Domain-agnostic: for implemented verticals such as data analysis or theory/modeling, invokes the matching domain skill and planning reference before task drafting."
---

# Planning Workflow

**First, load `superRA:using-superra` if not already loaded.**

**If the harness has activated plan mode, load `references/harness-plan-mode.md` before proceeding.**

## Overview

Workflow skill for the **PLAN** phase of the superRA workflow. Owns the procedural shape of task-tree creation: discovery of existing work, exploration, domain setup, task decomposition, self-review, and execution handoff. Outputs a `.plan/` task tree for the implementation-workflow to consume.

Write comprehensive task objectives for a reader skilled at the craft but with zero context for this specific project — which files to create, what inputs to load, how to transform them, what to validate, and how to document results.

**"Plan" is the verb, not the noun.** "Planning" refers to this workflow — the process of scoping and decomposing work. Everything in `.plan/` is a **task** — root-level tasks scope a workstream, nested tasks are dispatchable work. `.plan/` is "the task tree," not "the plan." There is no separate "plan" artifact type. Use "task tree" when referring to the `.plan/` artifact, "planning" when referring to the process.

**Announce at start:** "I'm using the planning-workflow skill to create the task tree."

**Output:** A `.plan/` directory at the project root (if in a worktree, the worktree root; otherwise, the project root or user-specified location) containing a root `task.md` and child task directories. User preferences for location override this default.

Commit the task tree before proceeding to execution.

## Entry Assessment

Before any exploration or task design, assess three independent dimensions of the incoming work. There is no procedural difference between creating a task tree and updating one — both pass through the same entry assessment.

**1. Where it goes — Placement.** If `.plan/` exists, read the tree and walk it to find where the new work belongs, using the concern-first placement logic in `task-system/references/planning.md` §Placing Work in the Tree. If `.plan/` does not exist, check for a legacy `PLAN.md` (offer migration via `task-system` §Migration if found) and then the new work becomes the first root-level task.

**2. How deep — Depth tier.** Choose a tier that modulates how deeply the subsequent phases execute. See §Depth Tiers below. Both placement and depth may need refinement after exploration — placement because the tree relationship was not clear upfront, depth because the work turned out more complex than expected.

**3. What mode — Routing path.** Most work is forward planning (the default). Two alternatives:
- **Retroactive documentation** — existing code/results need a `.plan/` record. Detected when the entry assessment finds code without task coverage. Routes through the same phases but sets `status: implemented` on created tasks. See §Retroactive Plan Creation.
- **Consolidation** — tree cleanup requested or detected as needed. Routes to `references/consolidation.md`.

**Placement and depth are independent dimensions.** Neither determines the other. Work can clearly belong under an existing task but still need thorough planning; uncertain tree location does not mean the work itself is hard to plan.

**Ask when unclear.** When the existing tree and project context do not make placement or depth obvious, ask the user rather than guessing silently. Present the concrete options under consideration — e.g., "nest under task X vs. create a new root-level task" or "standard vs. thorough depth" — with a one-line rationale for each. Wrong placement creates rework; wrong depth wastes effort or misses complexity.

## Depth Tiers

Three tiers that modulate how deeply each subsequent phase executes. A spectrum, not rigid modes — escalate mid-planning if complexity warrants it.

**Quick** — for minor updates, known additions, single-task changes. Light scan of existing `.plan/`, skip deep exploration, go directly to task design. The main agent does everything inline. Appropriate when: updating an objective after a scope revision, adding a well-understood subtask, adjusting dependencies.

**Standard** — the default. Main agent explores project structure, loads domain skill, designs tasks. Appropriate when: new workstreams in familiar territory, adding a significant new branch to the tree, domain hard gates need satisfying.

**Thorough** — dispatch parallel exploration agents before task design. Load `references/thorough-planning.md` for the dispatch pattern. Appropriate when: complex or unfamiliar projects, large scope spanning multiple codebase areas, user explicitly requests deep planning ("plan hard", "explore thoroughly", "I want a detailed plan"). When thorough planning returns competing designs from multiple agents, the unresolved tensions between them are a natural source of substantive questions for the user — see §Substantive Questions.

The depth tier mainly modulates Phase 1 (Exploration) — quick skips deep exploration, standard does the current default, thorough dispatches agents. Phase 2 (Domain Setup) and Phase 3 (Design) scale correspondingly. Phase 4 (Review & Commit) is the same at all tiers except that thorough depth adds an agent review step between self-review and user review — see §Agent Review below.

## Phase 1: Exploration

Context exploration before task design. Read project structure, existing code, data directories, documentation, CLAUDE.md/README.md files, and git history for relevant prior work.

Depth scales with the tier chosen in §Entry Assessment. Quick tier: light scan of the tree neighborhood where the work will land. Standard tier: systematic exploration of the relevant project areas. Thorough tier: dispatch parallel exploration agents per `references/thorough-planning.md`. Domain skills' hard-gate data gathering (data inventory, model primitives survey, manuscript assessment) begins here, but the phase itself is domain-neutral.

Exploration may reveal that the initial placement or depth tier needs adjustment — revisit the entry assessment if so.

## Phase 2: Domain Setup & Scope

Identify the domain of the work and load the matching domain skill's planning reference. The domain skill carries domain-specific hard gates and templates that must be satisfied before tasks are drafted.

**Currently implemented verticals:**

| Vertical | Trigger | Domain skill |
|---|---|---|
| Data analysis | task involves loading, cleaning, merging, transforming, modeling, or visualizing data | `superRA:econ-data-analysis` |
| Theory / modeling | task involves deriving or analyzing a mathematical model, equilibrium conditions, comparative statics, proofs, symbolic manipulation, or model notes | `superRA:theory-modeling` |
| Writing | task involves editing, polishing, proofreading, consistency-checking, refactoring wording, or drafting technical sections of an academic paper or manuscript | `superRA:writing` |

**Stop here, load the matching domain skill, follow its planning-stage reference per its own stage-load table, and satisfy its planning hard gate before returning to Phase 3.** The researcher must approve the domain skill's planning-stage inventory artifact before any task structure is drafted.

If the task is in a domain without an implemented vertical: proceed to Phase 3, but flag the gap to the researcher.

**Scope check:** If the work covers multiple independent workstreams, suggest splitting into separate root-level tasks — one per workstream. Each should produce complete, documented results on its own.

## Phase 3: Design & Task Decomposition

### Artifact Pipeline

Before defining tasks, map out the artifact pipeline:

- What scripts, notebooks, or documents will be created? One per logical phase. Follow any artifact-format guidance the active domain skill loads.
- What files are inputs? Where do outputs go?
- Follow existing project conventions for directory structure.

**Walk the project guidance docs and cache them in root task.md `## Conventions`.** Before drafting tasks, walk up from every directory the task tree will touch and `Read` every `CLAUDE.md` / `AGENTS.md` / `README.md` you encounter along the path; also read the repo-root `CLAUDE.md` and every `README.md` in a data directory the tasks will load from. Populate the root `.plan/task.md` `## Conventions` section (see `task-system/references/planning.md` §Conventions Section for format).

**Pipeline file (required for multi-artifact work):** If the work involves more than one script or executable artifact, include a pipeline file that runs all artifacts in the correct order — a single entry point that reproduces every output from source. The pipeline file must run scripts in dependency order, fail fast on errors (`set -e` or equivalent), be committed to version control, and be updated whenever a new script is added.

### Task Structure

**Each task is one logical unit of work with full discipline applied.** The active domain skill defines that discipline. Documentation is written continuously alongside the work, not as a separate task.

For the objective writing guide and task splitting heuristics, see `task-system/references/planning.md` §Writing Objectives and §Splitting Tasks.

### Creating Tasks

Use `task_create.py` to create tasks (auto-fills template with dates, frontmatter defaults):

```bash
python3 <skill-dir>/scripts/task_create.py \
  --plan-root .plan --path 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge
```

Or create task directories and write `task.md` files directly — the format is self-explanatory (see `task-system/SKILL.md` §Task File Format).

**No checkboxes.** Tasks do not contain step checkboxes (`- [ ]` / `- [x]`). If a step needs independent tracking and review, it becomes a subtask.

### Task Dependencies

Each task declares dependencies in its `depends_on:` frontmatter field (sibling directory names). See `task-system/references/planning.md` §Field-by-Field Notes for semantics.

Identify independent branches so the orchestrator can dispatch them in parallel (see `agent-orchestration` §Workload Balancing).

**A task depends on another when it:**
- reads the other task's output files;
- needs a sample / variable / methodology decision finalized in the other task; or
- runs sensitivity / robustness on the other task's baseline results.

**After writing all tasks:** trace the dependency edges — no cycles, no references to nonexistent siblings; terminal task(s) produce the top-line results.

### Root task.md and Task Anatomy

For the canonical task structure — root task.md anatomy, per-task anatomy, and field-by-field notes — see `task-system/references/planning.md`. Domain-specific root sections come from the domain skill's planning reference.

### Create the `.plan/` Directory

1. Create `.plan/task.md` (root) with `## Objective` (project-level goal, methodology, scope) and `## Conventions` (cached project guidance).
2. Create child task directories with full objectives per §Task Structure above.

## Phase 4: Review & Commit

### Self-Review

After writing the complete task tree:

1. **Domain inventory coverage (where applicable):** For domains with a planning hard gate, can you point to task coverage for every item in the inventory?
2. **Placeholder scan:** Search for vague objectives — "process the data", "clean up results", "finalize" without concrete success criteria. Fix them.
3. **Pipeline consistency:** Do the artifact names in the pipeline file match the artifacts created in each task? Are they in the right order?
4. **Validation coverage:** Does every transformative task have a corresponding validation criterion in its objective?
5. **Handoff test:** If you stopped here and a new agent read the root task.md plus the ancestor chain of any leaf task, could they continue? Is there enough context?
6. **Verification coverage (where applicable):** Does the task tree cover the active domain skill's verification / robustness requirements?
7. **Dependency graph sanity:** Every task has `depends_on:` declared. No cycles. Independent branches are marked parallelizable.
8. **Subtask coverage:** No task carries implicit sub-steps that should be separate subtasks.

Fix issues inline. No need to re-review — just fix and move on.

### Agent Review (Thorough Depth Only)

At thorough depth, dispatch a reviewer agent before presenting the tree to the user. The reviewer receives the complete `.plan/` directory and the exploration synthesis from Phase 1. It evaluates the self-review checklist above plus structural coherence across tasks: whether task boundaries make sense, dependencies are complete, and decomposition granularity is appropriate for the work scope.

The reviewer returns APPROVE or REVISE with findings. REVISE findings must be fixed before proceeding to User Review — the user should see a structurally sound tree, not one with known issues.

Skip this step at quick and standard depth — the self-review checklist is sufficient when the main agent designed the tree itself without parallel exploration.

### User Review

Verify the task tree aligns with the user's intent. Present the tree (via `task_query.py --tree`) and surface remaining open questions — design tradeoffs, unresolved ambiguities, choices that could reasonably go another way. Present tradeoffs as options, not assertions. If you have no genuine questions, the tree presentation itself is the review.

### Execution Handoff

Commit the `.plan/` directory atomically. Then hand off to `superRA:implementation-workflow`, which owns execution-mode selection, frontier-based dispatch, and review discipline.

## Substantive Questions

At any point during planning, surface questions when you are making assumptions about the user's intent. Do not make large assumptions silently. When you identify a genuine design tradeoff with distinct alternatives, present the options for the user to choose between — do not assert one and narrate your reasoning. Questions are a quality mechanism for tying loose ends, not process checkpoints.

## Retroactive Plan Creation

When documenting existing exploratory work into `.plan/`:

1. Survey existing code, outputs, and notebooks
2. Create `.plan/` structure with `task_create.py` — one task per logical unit of work done
3. Edit each `task.md`: set `status: implemented` in frontmatter, fill body sections with what was done (`## Objective`: what was the goal) and found (`## Results`: what was discovered)
4. Hooks validate + rebuild dashboard. The task tree is now a retroactive record that can drive review, integration, and future work

See `task-system/references/planning.md` §Retroactive Plan Creation for the full workflow.

## Living Task Tree

**The task tree is NOT a static spec.** Work reveals surprises; the task tree evolves in place.

Distinguish two kinds of drift: (a) **agent-discovered refinements** during in-flight work (a task's approach adjusted after seeing the data, expected results tuned to early findings) — handle these as inline edits to the task's body sections per the editing discipline in `agents/implementer.md` §Editing Etiquette; (b) **researcher-initiated scope changes** mid-session (new tasks, removed tasks, methodology pivots, sample redefinition) — these MUST be routed through §User Feedback and Changing the Task Tree below.

**Results:** Each task's `## Results` section is the live findings record. See `task-system/references/planning.md` §Results Shape for the template and two-stage lifecycle.

### .plan/ Is the Task Tracker

**`.plan/` is the primary task tracker** — not `Todo` tools, not chat, not status reports, not a session-internal scratchpad. The task files with their frontmatter `status:` / `review_status:` fields are the authoritative state of what is planned, what is in progress, and what is done.

`TodoWrite` (or any equivalent harness-provided todo UI) has a narrower role: a transient view of what the agent is doing right now in this session. It is acceptable for ephemeral session-internal todos that do not represent analysis tasks. It is **not** acceptable as a substitute for a `.plan/` task. If the work is part of the analysis — a new task, a discovered subtask, a methodology check, a sensitivity run, a refactor pass — it lives in `.plan/` first.

**Rule of thumb:** if losing this todo at session end would lose work the researcher cares about, it belongs in `.plan/`, not `TodoWrite`.

**Banned patterns:**

- Tracking analysis tasks only in `TodoWrite` while leaving `.plan/` stale.
- Discovering a new subtask, adding it to `TodoWrite`, completing it, and never reflecting it in `.plan/`.
- Using `TodoWrite` to coordinate work between sessions (it does not persist; the next session sees nothing).

If `TodoWrite` and `.plan/` ever disagree about the state of analysis work, `.plan/` is right by definition.

## Revision Notes

When a task is updated (scope change, methodology pivot, added/removed work), add a `## Revision Notes` section with a brief delta: what changed, why, and how significant (trivial/mechanical vs substantive). This signals to the next agent whether they need to re-explore or can proceed directly.

Revision notes follow the same cleanup lifecycle as review notes — cleaned out when the task is re-implemented and approved. The objective is always self-sufficient — rewritten fully on every update, not patched. The revision note carries only the delta signal; the objective carries the full current state.

## User Feedback and Changing the Task Tree

When the task tree changes — task details updated, tasks added, removed, or restructured, objective shifted — whether prompted by explicit user feedback or surfaced during execution, follow this protocol. The same procedure applies whether the change is raised mid-execution or after integration / merge. Update task files inline; do not start a parallel task tree, append an "Addendum" section, or carry the change in chat.

**Material (require this protocol):**

- Adding, removing, or restructuring task directories.
- Changing a task's objective, script, input, or output.
- Changing the analysis-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge.
- Substantive restructure findings surfaced mid-INTEGRATE. The orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (handle as inline discovery edits per §Living Task Tree above):**

- Rewording a task objective to match what the data forced (within the same scope).
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Use `AskUserQuestion` (or a plain-text question if the tool is not available) to confirm the researcher wants the change.
2. **Update `.plan/` inline:**
   - **Prefer modifying existing task.md files over adding new tasks.** Walk the task tree and identify every task whose objective or output is affected. Update each in place.
   - **New task** — Only when the change is genuinely independent of every existing task's scope.
   - **Modified task** — Rewrite the objective to be fully self-sufficient with the new scope (all planning context included, not just the changed part). Add a `## Revision Notes` section with the delta signal.
   - **Removed task** — Delete the directory entirely.
   - **Root task.md** — After the task edits above, rewrite any field in root task.md that no longer matches the new tree.

3. **Update statuses** by orchestrator judgment. Clear `review_status` and `integration_status` only for the changed task(s) and transitive downstream dependents whose inputs or assumptions shift; preserve unrelated `approved` tasks.
4. **Sweep for stale content** per `task-system/references/planning.md` §Stale Content Checklist.
5. **Commit atomically** — all affected task.md files + any code touched by the change, in one commit. Title: `plan: <one-line scope change>`.
6. **Resolve the next frontier.** Run `using-superRA/references/main-agent.md` §Workflow Frontier Resolver to choose the next workflow entry point.

**Banned shortcuts:**

- Carrying the new task in chat or only in `TodoWrite` without writing it into `.plan/`.
- Resuming the in-flight task before reflecting the change in the committed task files — the change is not real until it is committed.
- Treating an invalidated workflow milestone as permission to clear unrelated approved tasks.

## Remember

- Exact file paths always
- Complete content in every task objective
- Domain-appropriate discipline applied at each task, with documentation written continuously
- When the active domain has a hard gate or required verification, the finished tasks visibly cover it
- Pipeline file for multi-artifact work
