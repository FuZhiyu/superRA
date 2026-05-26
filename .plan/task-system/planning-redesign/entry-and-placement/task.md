---
title: "Entry Assessment, Depth Tiers, and Task Placement"
status: approved
review_status: approved
integration_status: ~
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Rewrite the planning-workflow SKILL.md entry logic and add task placement guidance to the task-system planning reference. Three integrated changes that reshape how agents enter the planning workflow and decide where work goes.

### 1. Replace Phase 0 with Entry Assessment

Current Phase 0 ("Task Tree Discovery") splits conceptually between "new plan" and "plan update." Remove this distinction. The entry assessment produces three independent outputs:

- **Where it goes** — placement in the tree (via the placement logic in §3)
- **How deep** — depth tier (quick/standard/thorough, via §2)
- **What mode** — forward planning, retroactive documentation, or consolidation (via §5)

**Placement and depth are independent dimensions.** Neither determines the other. Simple placement does not imply quick depth — work can clearly belong under an existing task but still need thorough planning. Complex placement does not imply thorough depth — uncertain tree location doesn't mean the work itself is hard to plan. Teach them as two separate questions: "where does this go?" and "how thoroughly should we plan?"

There should be no procedural difference between "creating a plan" and "updating a plan." Both placement and depth may need refinement after exploration — placement because the tree relationship wasn't clear upfront, depth because the work turned out more complex than expected.

### 2. Depth Tiers

Three tiers that modulate how deeply each subsequent phase (Exploration, Domain Setup, Design) executes. A spectrum, not rigid modes — an agent can escalate mid-planning if complexity warrants it.

- **Quick** — for minor updates, known additions, single-task changes. Light scan of existing `.plan/`, skip deep exploration, go directly to task design. Main agent does everything inline. Appropriate when: updating an objective after a scope revision, adding a well-understood subtask, adjusting dependencies.

- **Standard** — current default behavior. Main agent explores project structure, loads domain skill, designs tasks. Appropriate when: new workstreams in familiar territory, adding a significant new branch to the tree, domain hard gates need satisfying.

- **Thorough** — dispatch parallel exploration agents before task design. Routes to new `references/thorough-planning.md` for the dispatch pattern. Appropriate when: complex/unfamiliar projects, large scope spanning multiple codebase areas, user explicitly requests deep planning ("plan hard", "explore thoroughly", "I want a detailed plan").

The depth tier mainly modulates Phase 1 (Exploration) — quick skips deep exploration, standard does current behavior, thorough dispatches agents. Phase 2 (Domain Setup) and Phase 3 (Design) scale correspondingly. Phase 4 (Review & Commit) is the same at all tiers.

### 3. Task Placement

Placement is a two-step decision: first find which task's **concern** covers the new work, then decide **granularity** (how big is the extension?).

**Step 1 — Find the concern.** Walk the tree recursively. At each level, ask: does an existing task's topic/concern cover this work? If yes, that's where it goes. If no task at this level covers it, create a sibling.

**Step 2 — Decide granularity.** Once you've found the right task:

- **Update** — the extension is simple enough that the task stays right-sized for a single dispatch. Rewrite its objective to include both old and new scope. Example: a merge task that handled fund data now also needs to handle CRSP data — same concern, extended scope, still one task.

- **Nest** — the extension is complex enough to warrant its own dispatch and review cycle. Add as a child subtask. The parent's objective may also be broadened to reflect the expanded scope. Example: a data-preparation task that now needs a whole new cleaning pipeline for a second data source — same concern, but the new work needs independent implementation.

- **Create sibling** — the work doesn't belong under any existing task's concern at this level. Applied at the root level, this creates a new root-level task.

The recursion handles all levels uniformly: start at the root, walk down through the tree, land the work at the right depth.

Anti-patterns: creating a new task for what's really a scope extension; nesting 3+ levels deep when unnecessary; creating siblings with near-identical concerns.

### 4. Ask When Placement or Depth Is Unclear

Add an explicit instruction in §Entry Assessment: when the existing tree and project context do not make the placement or depth tier obvious, the agent must use `AskUserQuestion` to ask the user rather than guessing silently. Present the concrete options under consideration (e.g., "nest under task X vs. create a new root-level task" or "standard vs. thorough depth") with a one-line rationale for each. Wrong placement creates rework; wrong depth wastes effort or misses complexity.

Place this immediately after the "Placement and depth are independent dimensions" paragraph in §Entry Assessment.

### 5. Substantive Questions Throughout Planning

Add a cross-cutting instruction (not gated to any phase) adapted from Claude Code's plan mode mechanism. Three components:

**Cross-cutting instruction:** "At any point during planning, surface questions when you're making assumptions about the user's intent. Don't make large assumptions. Questions are a quality mechanism for tying loose ends, not process checkpoints. When you identify a genuine design tradeoff with distinct alternatives, present the options for the user to choose between — don't assert one and narrate your reasoning."

**Phase 4 §User Review reframe:** Replace the current procedural framing ("highlight key design decisions, and ask for approval") with alignment-and-loose-ends framing: "Verify the task tree aligns with the user's intent. Surface remaining open questions — design tradeoffs, unresolved ambiguities, choices that could reasonably go another way. Present tradeoffs as options, not assertions. If you have no genuine questions, the tree presentation itself is the review." No separate approval step.

**Multi-perspective surfacing (thorough tier):** When thorough planning returns competing designs from multiple agents, the unresolved tensions between them are the natural source of substantive questions. This is already covered by the thorough-planning reference (sibling task) but the SKILL.md should note the connection.

### 6. Entry Modes (Routing Paths)

These are routing decisions in the Entry Assessment, not separate workflows:

- **Forward planning** (default) — new work to be implemented. Routes through standard phases.
- **Retroactive documentation** — existing code/results need a `.plan/` record. Detected when the entry assessment finds code without task coverage. Routes through the same phases but sets `status: implemented` on created tasks. References existing §Retroactive Plan Creation content — no new instruction needed, just clear routing.
- **Consolidation** — tree cleanup requested or detected as needed. Routes to `references/consolidation.md`. See sibling task `consolidation/`.

### 7. Harness Plan Mode Alignment

Update `references/harness-plan-mode.md` to align with the new entry logic. In plan mode, depth tier selection happens during the exploration phase; the plan file reflects the chosen depth and placement decisions.

### Files to modify

- `skills/planning-workflow/SKILL.md` — Rewrite Phase 0, add depth tiers, embed placement logic, add substantive-questions instruction, reframe Phase 4 User Review, add entry mode routing
- `skills/task-system/references/planning.md` — Add §Placing Work in the Tree section with the concern-then-granularity logic (complements existing §Splitting Tasks)
- `skills/planning-workflow/references/harness-plan-mode.md` — Small alignment update for depth tier awareness

### Validation criteria

- The rewritten SKILL.md has no conceptual split between "new plan" and "update plan"
- Depth tiers are clearly defined with triggers and behavioral differences at each phase
- Task placement uses the concern-first, granularity-second logic — not the old "update vs nest vs create" as a flat pecking order
- Placement and depth are presented as independent dimensions — neither implies the other
- Both can be refined after exploration when needed
- The cross-cutting substantive-questions instruction exists outside any specific phase
- Phase 4 User Review is framed as alignment + loose ends, not approval
- Retroactive and consolidation modes are clean routing paths with no duplicated instruction
- The phases (Exploration, Domain Setup, Design, Review) still work at all depth levels
- No DRY violations with agent-orchestration, task-system, or §User Feedback and Changing the Task Tree
- Harness plan mode reference is consistent with the new entry logic
- §Entry Assessment includes an explicit "ask when unclear" instruction for placement and depth, placed after the independence paragraph

## Revision Notes

- **2026-05-26 — Added §4 "Ask When Placement or Depth Is Unclear."** New instruction: when the tree/context doesn't make placement or depth obvious, use `AskUserQuestion` with concrete options rather than guessing. Renumbered §§5–7.

## Results

### Changes Made

**[skills/planning-workflow/SKILL.md](skills/planning-workflow/SKILL.md):**
- Replaced Phase 0 (Task Tree Discovery) with §Entry Assessment producing three independent outputs: placement, depth tier, routing path
- Added §Depth Tiers (Quick/Standard/Thorough) with triggers and phase-modulation behavior
- Updated Phase 1 to scale with depth tier and note that placement/depth can be revised after exploration
- Reframed Phase 4 §User Review from approval-seeking to alignment-and-loose-ends
- Added §Substantive Questions as a cross-cutting instruction outside any specific phase
- Routing paths for retroactive and consolidation are clean pointers in the entry assessment, not duplicated protocol
- Added "Ask when unclear" paragraph in §Entry Assessment immediately after the independence paragraph — instructs agents to present concrete options via `AskUserQuestion` when placement or depth is ambiguous ([SKILL.md:40](skills/planning-workflow/SKILL.md#L40))

**[skills/task-system/references/planning.md](skills/task-system/references/planning.md):**
- Added §Placing Work in the Tree between §Splitting Tasks and §Root task.md Anatomy
- Two-step logic: Step 1 (find the concern via recursive tree walk) then Step 2 (decide granularity: update / nest / create sibling)
- Anti-patterns documented

**[skills/planning-workflow/references/harness-plan-mode.md](skills/planning-workflow/references/harness-plan-mode.md):**
- Replaced "Discovery" bullet with "Entry Assessment" covering placement, depth tier, and routing path
- Updated "Exploration" bullet to note depth-tier scaling

### Validation

All 12 validation criteria pass — verified by line-by-line review of the modified files (original 11 plus the new §4 criterion).
