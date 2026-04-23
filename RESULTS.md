# Workflow Frontier Resolver - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (plan redesign)
**Status:** Plan changed; implementation pending.

---

## Design Diagnosis

The current resolver's real value added is narrow:

- It forces agents to read durable evidence before acting, instead of trusting chat context or an invented global state.
- It preserves unrelated approved work by computing the affected task frontier from changed tasks and dependencies.
- It routes work to the workflow that owns the earliest invalid layer, so phase ownership stays local.
- It enforces gates agents often bypass under pressure: logged user decisions, review approval, reproducibility/completion before integration, and integration/docs/freshness before merge or PR.

The lengthy named-state taxonomy is not the core mechanism. Agents can usually infer "what comes next" from a canonical workflow map if the docs give them the map, the evidence to inspect, the decision object to produce, and the hard gates they may not bypass.

There is also an overview placement gap. README explains the PLAN -> IMPLEMENT -> INTEGRATE cycle and adaptive/composable idea, but runtime agents may not read README. The compact operational overview should live in a loaded runtime surface such as `skills/using-superRA/SKILL.md`, with `main-agent.md` carrying the main-agent-specific resolver mechanism.

---

## Task 1: Add Runtime Workflow Overview and Resolver Value Proposition

**Status:** Not started after plan redesign.

### Planned Findings
- Add a concise runtime overview of PLAN -> IMPLEMENT -> INTEGRATE and the re-entry/adaptability principle.
- State the resolver's value proposition as mechanism-level guidance: durable evidence, affected frontier, owner routing, and gates.
- Avoid moving README-level product explanation into runtime skill prose.

### Files Planned
- `skills/using-superRA/SKILL.md`
- `skills/using-superRA/references/main-agent.md`

## Task 2: Replace Contingency Taxonomy with a Frontier Mechanism

**Status:** Not started after plan redesign.

### Planned Findings
- Keep the evidence contract and decision object.
- Replace `needs ...` state labels with ordered reasoning over the canonical workflow.
- Keep only explicit guards needed to prevent unpredictable or unsafe behavior.

### Files Planned
- `skills/using-superRA/references/main-agent.md`

## Task 3: Simplify Workflow Call Sites Around the Mechanism

**Status:** Not started after plan redesign.

### Planned Findings
- Workflow skills should point to the resolver for cross-workflow entry selection.
- Workflow skills should retain only their local mechanics and gates.
- Utility/domain skills should remain standalone.

### Files Planned
- `skills/planning-workflow/SKILL.md`
- `skills/implementation-workflow/SKILL.md`
- `skills/integration-workflow/SKILL.md`
- `skills/agent-orchestration/SKILL.md`
- `skills/handoff-doc/references/plan-anatomy.md`

## Task 4: Audit Against Adaptive-Composable Design

**Status:** Not started after plan redesign.

### Planned Findings
- Verify the modified docs no longer read like a contingency tree.
- Verify the canonical workflow/adaptability overview is present in a loaded runtime surface.
- Verify ownership boundaries remain consistent with AGENTS.md.
- Run `git diff --check`.

### Verification Commands Planned
- `rg -n "needs plan repair|needs implementation|awaiting review|needs validation|Current state|state machine|skip|resume|re-entry|if .* then|under .* condition" skills/using-superRA skills/*/SKILL.md`
- `git diff --check`
