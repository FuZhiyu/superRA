# Workflow Frontier Resolver - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (Task 4, Step 5)
**Status:** In Progress - implementation complete, awaiting review

---

## Task 1: Add Main-Agent Frontier Resolver

**Status:** Completed implementation on 2026-04-23; review pending.

### Key Findings
- `skills/using-superRA/references/main-agent.md` now has a `Workflow Frontier Resolver` section.
- The resolver derives the current frontier from existing durable facts instead of introducing a new `Current state` field.
- The resolver explicitly treats mixed state as normal: changed tasks and affected downstream tasks can roll back while unrelated approved/integrated tasks remain preserved.
- The resolver returns a concrete decision shape: affected frontier, preserved-approved tasks, invalidated milestones, next safe workflow entry point, and required stop point.
- Required guarantees were added for review approval, logged user decisions, current handoff docs, blocking review-item handling, and merge/PR gates.

### Files Changed
- `skills/using-superRA/references/main-agent.md`

### Notes
- The current resolver implementation distinguishes `needs plan repair` from `inconsistent`: missing/incomplete required plan state routes to plan repair; contradictory facts that cannot be mechanically repaired route to an explicit stop point.

## Task 2: Simplify Workflow Re-Entry Prose

**Status:** Completed implementation on 2026-04-23; review pending.

### Key Findings
- `planning-workflow` keeps the material plan-change protocol and now delegates post-edit entry selection to the main-agent resolver.
- `planning-workflow` now clears `Review status` and `Integration status` only for changed tasks and affected downstream dependents, while preserving unrelated `APPROVED` tasks.
- `implementation-workflow` now reads workflow/task statuses as frontier evidence and only continues locally for implementation/review/adjudication frontiers.
- `integration-workflow` no longer carries broad re-entry/lighten contingency prose; it keeps Phase A-D local gates after the resolver selects entry.
- `agent-orchestration` now scopes task sequencing and dispatch to the selected frontier instead of owning workflow-phase choice.

### Files Changed
- `skills/planning-workflow/SKILL.md`
- `skills/implementation-workflow/SKILL.md`
- `skills/integration-workflow/SKILL.md`
- `skills/agent-orchestration/SKILL.md`

### Notes
- Local gates intentionally remain in workflow skills: integration freshness checks, full drift-test execution, doc review, and review-loop adjudication are mechanics of their owning workflows rather than duplicate frontier selection.

## Task 3: Clarify Handoff-Doc State Semantics

**Status:** Completed implementation on 2026-04-23; review pending.

### Key Findings
- `skills/handoff-doc/references/plan-anatomy.md` now describes `Review status` and `Integration status` as task-local validity markers.
- `## Workflow Status` checkboxes are now described as milestone rollups over task-local markers plus required global gates.
- The doc now states that unchecking a rollup records that the rollup is false; it does not clear unrelated task-local status.

### Files Changed
- `skills/handoff-doc/references/plan-anatomy.md`

### Notes
- This is the core semantic support for the acceptance case: changing Task 3 after refactor can invalidate downstream/frontier rollups without erasing unrelated task approvals.

## Task 4: Audit and Tighten References

**Status:** Completed implementation on 2026-04-23; review pending.

### Key Findings
- Static search found the intended resolver references and remaining local gate language.
- Broad duplicated entry-selection language was replaced with pointers to the main-agent resolver.
- No new durable state field was introduced; the only `Current state` wording is the explicit instruction not to add or trust such a field.
- Domain-neutral cleanup was kept out of the modified workflow/reference files for this change.
- `git diff --check` passed.

### Verification Commands
- `git diff --check`
- `rg -n "resume|re-enter|re-entry|skip|When to Lighten|Workflow Status|Review status|Integration status|frontier|Current state|state machine|invariant" ...`
- `rg -n "continue from next incomplete|Execution complete.*skip|unchecked.*APPROVED|Resume the appropriate workflow|resume implementation-workflow|When to Lighten|state label|single global state|Current state" skills`

### Notes
- Because the implementation was performed directly before these handoff docs were created, all task `Review status` values remain `IMPLEMENTED`, not `APPROVED`.
- The next safe workflow frontier is implementation review for Tasks 1-4.
