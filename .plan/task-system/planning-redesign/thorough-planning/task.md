---
title: "Thorough Planning Reference"
status: implemented
review_status: revise
integration_status: ~
depends_on:
  - entry-and-placement
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Create `skills/planning-workflow/references/thorough-planning.md` — the reference loaded when depth tier is "thorough." Defines the dispatch pattern for deep planning with parallel exploration and multi-perspective design, adapted from Claude Code's multi-agent plan mode for research workflows.

### What the reference must cover

**1. Exploration Dispatch**

Define how to dispatch parallel exploration agents during Phase 1. Adapted from Claude Code's Phase 1 ("Launch up to N explorer subagents in parallel"):

- Each exploration agent covers a distinct area relevant to the work: project structure, existing code patterns, data inventory, test infrastructure, related prior work in git history, etc.
- Exploration agents are read-only — they report findings, not make changes. Use `subagent_type: "Explore"` or equivalent lightweight dispatch.
- Each agent gets a focused objective: "Map the data pipeline in `src/analysis/`", "Assess existing test patterns and coverage", "Inventory the data files in `data/` and document their schemas."
- Typical count: 2–4 agents depending on project scope. The orchestrator decides count and focus based on what it learns during the Entry Assessment.
- Dispatch template should compose with agent-orchestration's existing patterns — don't reinvent dispatch shape.

**2. Exploration Synthesis**

After all exploration agents return, the main agent synthesizes findings into a unified understanding:
- Consolidate findings, resolve contradictions, identify gaps
- Map findings to the planned work: what's relevant, what changes the approach, what's surprising
- This synthesis happens before task design (Phase 3) begins

**3. Multi-Perspective Design (optional)**

For very complex work spanning multiple codebase areas or requiring different architectural approaches, the main agent may dispatch planning agents — each proposes a task design for their area or from their perspective. The main agent then reconciles into a unified task tree.

This is optional and rare. Most thorough planning needs parallel exploration but single-agent design. Include guidance on when to use this (multiple independent areas, genuinely different viable approaches) and when not to (just a large but straightforward workstream).

When multiple designs come back, the unresolved tensions between them are a natural source of substantive questions for the user — tradeoffs where the "right" answer depends on research intent. The reference should note this connection to the cross-cutting substantive-questions instruction in the planning-workflow SKILL.md (see sibling task `entry-and-placement`).

**4. Critical Files Identification**

After task design, identify 3–5 critical files for implementation — files that implementation agents should prioritize understanding because they're central to the work. Inspired by Claude Code's requirement for plans to conclude with a "Critical Files for Implementation" section.

**5. Incremental Refinement**

The task tree at thorough depth is not one-shot. The main agent may refine after:
- User feedback on the initial design
- Exploration findings that change the approach
- Domain hard gate results that constrain the scope

Each refinement round can be lighter (quick-depth update to the tree) even though the initial pass was thorough.

### Design constraints

- The reference must compose cleanly with agent-orchestration dispatch templates — exploration agents use existing dispatch patterns, not a new template shape.
- Must work both in harness plan mode (exploration dispatched during plan mode, findings inform the plan file) and in direct planning (exploration dispatched before task file creation).
- Should not duplicate content from agent-orchestration §Workload Balancing or §Dispatch Templates.
- Exploration agent prompts should be examples/templates, not rigid scripts — the orchestrator adapts them to the project.

### Files to create

- `skills/planning-workflow/references/thorough-planning.md` (NEW)

### Validation criteria

- The reference is loadable standalone (an agent reading only this reference + using-superra can execute thorough planning)
- Exploration dispatch uses existing agent-orchestration patterns
- No DRY violations with agent-orchestration or planning-workflow SKILL.md
- The dispatch pattern works for both research (data analysis, theory) and software (skill development, infrastructure) contexts
- Critical files identification is concise and actionable
- Incremental refinement composes with the depth tiers (thorough initial pass, quick refinement)

## Results

### File Created

[`skills/planning-workflow/references/thorough-planning.md`](skills/planning-workflow/references/thorough-planning.md) (126 lines) — the thorough planning reference, loaded when depth tier is "thorough."

### Coverage

Five sections covering all required topics:

1. **Exploration Dispatch** — parallel read-only agents (2-4), lightweight dispatch shape using `subagent_type: "research"` with explicit read-only instruction, example objectives for both research and software contexts, plan-mode compatibility note.
2. **Exploration Synthesis** — consolidation, mapping to work, entry assessment reassessment, gap identification. Main agent work, not delegated.
3. **Multi-Perspective Design (optional)** — when-to-use / when-not-to-use criteria, dispatch shape, reconciliation protocol with connection to `planning-workflow §Substantive Questions` for surfacing tradeoffs from competing designs.
4. **Critical Files for Implementation** — 3-5 files, qualification criteria, format as `## Critical Files` section in root `task.md`.
5. **Incremental Refinement** — refinement rounds use quick-depth mechanics, references standard change protocol, targeted follow-up exploration for missed areas.

### Validation

All 6 validation criteria pass:
- Standalone loadable: opens with load condition, self-contained pattern description, cross-references by section name
- Existing dispatch patterns: uses `Agent(subagent_type: ...)` shape from agent-orchestration; no new template shape
- No DRY violations: no content duplicated from agent-orchestration §Workload Balancing/§Dispatch Templates or planning-workflow SKILL.md phase descriptions
- Works for research and software: examples include data pipeline/analysis and skill development/code structure
- Critical files: concise section with qualification criteria and one-line format
- Incremental refinement: explicitly composes with depth tiers (thorough initial, quick refinement)

## Review Notes

1. [MAJOR] `subagent_type: "research"` is not defined in any agent spec, Claude tools adapter ([claude-tools.md](skills/using-superRA/references/claude-tools.md)), or Codex tool map ([codex-instructions.md:74-76](skills/using-superRA/references/codex-instructions.md#L74)). The system defines only `superRA:implementer`, `superRA:reviewer`, and `generic` (for sync). The parenthetical "(or any general-purpose agent the harness exposes)" at [thorough-planning.md:20](skills/planning-workflow/references/thorough-planning.md#L20) acknowledges the ambiguity but does not resolve it — an agent following this reference would not know what concrete harness action to take. Fix: either define the harness mapping for `"research"` in each adapter reference, or drop back to a generic/default agent type with an explicit note about how each harness handles it (e.g., Claude Code spawns a generic Agent with the prompt text; Codex uses `spawn_agent(agent_type="default")`). Same issue at [thorough-planning.md:73](skills/planning-workflow/references/thorough-planning.md#L73) for the multi-perspective design template.

2. [MAJOR] The exploration dispatch template ([thorough-planning.md:23-29](skills/planning-workflow/references/thorough-planning.md#L23)) introduces new fields (`Objective:`, `Scope:`) and the design template ([thorough-planning.md:73-80](skills/planning-workflow/references/thorough-planning.md#L73)) adds `Context:` — none of which exist in the canonical agent-orchestration dispatch template shape ([SKILL.md:114-132](skills/agent-orchestration/SKILL.md#L114)). The task objective's design constraint explicitly requires "not a new template shape," and the implementer's self-validation claims "no new template shape" — but this is a new shape. Fix: restructure the exploration template to use the canonical field set. Exploration agents genuinely differ from task-scoped agents (no task path or stage), so the natural fit is to use `Additionally:` to carry the exploration objective and scope constraints, making the template a thin specialization of the canonical shape rather than a parallel one. Alternatively, explicitly acknowledge this is a new lightweight template and explain why the canonical shape cannot apply — but this would require the orchestrator to accept a design-constraint relaxation.

3. [MINOR] Plan-mode subagent dispatch claim at [thorough-planning.md:39](skills/planning-workflow/references/thorough-planning.md#L39) states exploration agents "can be dispatched during plan mode" as fact. Whether a harness allows subagent dispatch during plan mode is harness-dependent. The harness-plan-mode reference supports this for the planning workflow's own text, but subagent spawning during plan mode is not guaranteed across harnesses. Fix: soften to "exploration agents are read-only and compatible with plan mode constraints; verify your harness supports subagent dispatch during plan mode" or similar.
