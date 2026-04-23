# Workflow Frontier Resolver - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (implementation verification)
**Status:** Implementation complete and verified; awaiting researcher disposition.

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

**Status:** Approved.

### Findings
- Added `skills/using-superRA/SKILL.md` `## Runtime Workflow Map`, which gives loaded agents the PLAN -> IMPLEMENT -> INTEGRATE order without importing README-level product explanation.
- The overview states the adaptive re-entry principle: enter at the earliest invalid layer for the affected task frontier while preserving unrelated approved work.
- The resolver value proposition is now explicit: inspect durable evidence, compute the affected frontier, route to the owning workflow, and enforce non-negotiable gates.

### Files Changed
- `skills/using-superRA/SKILL.md`
- `skills/using-superRA/references/main-agent.md`

## Task 2: Replace Contingency Taxonomy with a Frontier Mechanism

**Status:** Approved.

### Findings
- Replaced the resolver's named `needs ...` outcome list with an ordered mechanism in `skills/using-superRA/references/main-agent.md`.
- Preserved the evidence contract: git state, handoff-doc presence and consistency, workflow rollups, decisions, upstream intent, task dependencies/statuses/review notes, and RESULTS.md sections.
- Preserved the decision object: affected frontier, preserved-approved tasks, invalidated milestones, next owner/layer, and required stop point.
- Kept explicit safety invariants for the predictable failure modes: no global `Current state` field, no unlogged material decisions, no clearing unrelated task statuses, no implementation advancement without review/adjudication, no integration before reproducibility/disposition, and no merge/PR before integration/docs/freshness gates.

### Files Changed
- `skills/using-superRA/references/main-agent.md`

## Task 3: Simplify Workflow Call Sites Around the Mechanism

**Status:** Approved.

### Findings
- `implementation-workflow` no longer branches on resolver state labels. It now enters only when the resolver selects implementation, review, reproducibility verification, or the completion disposition.
- `planning-workflow` points to the resolver for cross-workflow entry selection after a material plan change and leaves local plan-change mechanics in the planning skill.
- `integration-workflow` keeps the Phase A-D gate map and scopes work to the affected frontier without restating resolver selection logic.
- `agent-orchestration` still owns dispatch and review-status mechanics; a status-table phrase was tightened so it does not resemble the old resolver taxonomy.
- `handoff-doc` and `plan-anatomy.md` remain standalone sources for handoff status semantics; no change was needed there.

### Files Changed
- `skills/agent-orchestration/SKILL.md`
- `skills/planning-workflow/SKILL.md`
- `skills/implementation-workflow/SKILL.md`
- `skills/integration-workflow/SKILL.md`

## Task 4: Audit Against Adaptive-Composable Design

**Status:** Approved.

### Findings
- The modified resolver reads as a mechanism: evidence first, affected-frontier calculation, ordered owner routing, and safety invariants.
- The loaded runtime overview is in `skills/using-superRA/SKILL.md`, not only README or AGENTS.
- Ownership boundaries remain aligned with AGENTS.md: `using-superRA` owns the shared workflow map, `main-agent.md` owns the resolver, workflow skills own local gates, `agent-orchestration` owns dispatch/status mechanics, and `handoff-doc` owns document semantics.
- Design-text search no longer finds the old resolver state labels in modified resolver/call-site prose. Remaining hits are intentional non-taxonomy uses: the explicit `Current state` prohibition, local `skip` / `re-entry` wording in workflow gates and adapter/domain skills, and unrelated discard/AskUserQuestion wording.

### Verification Commands
- `rg -n "needs plan repair|needs implementation|awaiting review|needs validation|Current state|state machine|skip|resume|re-entry|if .* then|under .* condition" skills/using-superRA skills/*/SKILL.md`
- `git diff --check`
- `uv run python /Users/zhiyufu/Dropbox/app_settings/dotfiles/claude/.claude/skills/.system/skill-creator/scripts/quick_validate.py <modified-skill-folder>` for `skills/using-superRA`, `skills/planning-workflow`, `skills/implementation-workflow`, `skills/integration-workflow`, and `skills/agent-orchestration`
