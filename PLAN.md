# Workflow Frontier Resolver Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is a package-design change, not a data-analysis task. Task statuses describe the current workflow frontier; do not mark tasks `APPROVED` until a reviewer has actually approved them.

**Objective:** Centralize partial-workflow and mixed-state handling in `skills/using-superRA/references/main-agent.md` so workflow skills can compose around a single frontier resolver instead of carrying duplicated re-entry contingencies.

**Methodology:** Add a main-agent frontier protocol over existing durable facts, then replace duplicated resume/re-entry prose in workflow skills with pointers to that resolver while preserving local phase gates.

**Data Inventory:** Not applicable. This change edits package documentation and skill references only.

**Conventions:** Preserve one source of truth per concern: main-agent reference owns cross-workflow entry selection; workflow skills own local mechanics; `handoff-doc` owns document state semantics; `agent-orchestration` owns dispatch and review-loop mechanics.

**Output:** Updated workflow/reference docs plus this retroactive `PLAN.md` and `RESULTS.md` handoff pair.

**Expected Results / Hypotheses:** Agents can resume safely from mixed branch states without collapsing the branch into one global state label or reworking unrelated approved tasks.

**Sensitivity Analysis:** Verify the acceptance case where Task 3 changes after implementation and refactor: only Task 3 plus affected downstream tasks lose local validity, unrelated approved tasks remain preserved, rollup milestones are unchecked only where false, and global gates still rerun before merge / PR.

**Pipeline:** Not applicable. Verification is static documentation audit plus `git diff --check`.

---

## Workflow Status

- [x] **Plan approved** - researcher supplied and approved the implementation handoff plan in chat.
- [ ] **Execution complete** - implementation exists, but task review approval has not run.
- [ ] **Drift tests created** - not yet reached; documentation/package integration gate remains pending.
- [ ] **Refactored** - not yet reached; integration review remains pending.
- [ ] **Docs finalized** - not yet reached; this RESULTS.md is Stage 1 handoff state.
- [ ] **Merged** - branch has not been merged or opened as a PR by this workflow.

## Project Conventions

Walked at planning time (2026-04-23). Re-walk on-demand only.

### Repo root
- `/AGENTS.md`: contributor-facing entry point. It says superRA internal changes should be evaluated against adaptive/composable workflow design, DRY ownership, lean agents with rich references, and skill-authoring discipline when editing `skills/*/SKILL.md`.
- `/CLAUDE.md`: currently modified in this worktree as part of the broader contributor-guide cleanup. Preserve that outstanding change and do not conflate it with the frontier-resolver task.
- `/README.md`: user-facing project design belongs there; this task does not duplicate README-level product exposition into runtime skills.

### Relevant skill/reference files
- `skills/using-superRA/references/main-agent.md`: owns main-agent session start, autonomy, direct mode, and now cross-workflow frontier resolution.
- `skills/planning-workflow/SKILL.md`: owns plan creation and the material plan-change protocol, including which task-local statuses and rollup milestones are invalidated.
- `skills/implementation-workflow/SKILL.md`: owns implementation, review, and reproducibility mechanics after the resolver selects an implementation/review frontier.
- `skills/integration-workflow/SKILL.md`: owns Phase A-D integration mechanics after the resolver selects an integration/documentation/finalization frontier.
- `skills/agent-orchestration/SKILL.md`: owns dispatch, reviewer-feedback adjudication, and status-return mechanics inside a selected frontier.
- `skills/handoff-doc/references/plan-anatomy.md`: owns task-block and workflow-status semantics for handoff docs.

### Not walked
- `tests/`, `hooks/`, `scripts/`, and package metadata were not in the planned diff and were not needed for this documentation-design change.

## Decisions

> **User decision (2026-04-23):** Implement the "Workflow Frontier Resolver Handoff" plan using a frontier model, not a single global state model.
> **Question asked:** Which design should govern mixed-state workflow re-entry?
> **Rationale (if given):** The hard problem is safe workflow re-entry from any repo state, while preserving unrelated completed work and avoiding rigid contingency rules.

> **User decision (2026-04-23):** Keep domain-neutral cleanup out of scope for this change.
> **Question asked:** Should domain-neutral design issues be handled in this task?
> **Rationale (if given):** Domain-neutral cleanup will be addressed separately; this change focuses only on workflow design flexibility.

> **User decision (2026-04-23):** Create `PLAN.md` and `RESULTS.md` retroactively after direct implementation.
> **Question asked:** Should the already-implemented change be recorded in superRA handoff docs?
> **Rationale (if given):** The package should dogfood its own workflow state discipline.

---

### Task 1: Add Main-Agent Frontier Resolver
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** Not applicable; documentation/reference edit.
**Input:** User handoff plan; `skills/using-superRA/references/main-agent.md`.
**Output:** `skills/using-superRA/references/main-agent.md`.

- [x] **Step 1: Add resolver section**

Add a concise `Workflow Frontier Resolver` section to the main-agent reference.

- [x] **Step 2: Define resolver over durable facts**

Define the resolver as a protocol over existing durable facts: `PLAN.md`, `RESULTS.md`, task dependencies, `Review status`, `Integration status`, `## Workflow Status`, review blockquotes, `## Upstream Intent`, and git status/log. Do not introduce a new durable schema or `Current state` field.

- [x] **Step 3: Normalize frontier categories**

Include the categories `needs plan repair`, `needs implementation`, `awaiting review`, `needs revise/adjudication`, `needs integration`, `needs documentation`, `ready for merge`, `preserved-approved`, and `inconsistent`.

- [x] **Step 4: Encode mixed-state and rollup rules**

State that mixed state is normal, preserved-approved tasks are not reworked because a rollup was unchecked, and unchecked rollups are evidence rather than commands to redo every task.

- [x] **Step 5: Add required guarantees**

Add guarantees for review approval before advancement, logging user decisions before action, current handoff docs before status reports, blocking review item handling, and merge / PR only after integration, documentation, and freshness gates are valid.

### Task 2: Simplify Workflow Re-Entry Prose
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** Not applicable; documentation/reference edit.
**Input:** `skills/planning-workflow/SKILL.md`, `skills/implementation-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`.
**Output:** Updated workflow skills that delegate cross-workflow entry selection to the main-agent resolver.

- [x] **Step 1: Keep planning mechanics local**

Update `planning-workflow` so it keeps the material plan-change protocol and status-clearing mechanics, then points post-edit resume decisions to the Workflow Frontier Resolver.

- [x] **Step 2: Delegate implementation resume selection**

Update `implementation-workflow` so it treats `## Workflow Status` and task statuses as frontier evidence and continues locally only for implementation/review/adjudication frontiers.

- [x] **Step 3: Simplify integration entry prose**

Update `integration-workflow` so the main-agent resolver selects Phase A-D entry while the integration skill keeps local gates, freshness checks, doc review, and merge/PR mechanics.

- [x] **Step 4: Keep orchestration scoped to selected frontier**

Update `agent-orchestration` so it owns dispatch and review loops inside a selected frontier rather than choosing the workflow phase.

### Task 3: Clarify Handoff-Doc State Semantics
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** Not applicable; documentation/reference edit.
**Input:** `skills/handoff-doc/references/plan-anatomy.md`.
**Output:** Clarified handoff-doc status semantics in `plan-anatomy.md`.

- [x] **Step 1: Define task statuses as local validity markers**

State that `Review status` and `Integration status` are task-local validity markers.

- [x] **Step 2: Define workflow checkboxes as rollups**

Clarify that `## Workflow Status` checkboxes summarize task-local markers plus required global gates.

- [x] **Step 3: Preserve unrelated local status**

Add the rule that invalidating a rollup does not clear unrelated task-local statuses.

### Task 4: Audit and Tighten References
**Depends on:** Task 2, Task 3
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** Static documentation audit.
**Input:** Modified skill/reference files.
**Output:** Verified diff and audit notes in `RESULTS.md`.

- [x] **Step 1: Search for duplicated state logic**

Search for duplicated resume, re-entry, skip, frontier, and workflow-status logic across the modified workflow/reference files.

- [x] **Step 2: Replace duplicated entry selection**

Replace broad duplicate entry-selection prose with pointers to `main-agent.md` unless the prose describes local phase mechanics.

- [x] **Step 3: Verify no new durable state field**

Confirm the change uses the existing durable facts and does not add a new `Current state` field or state-machine schema.

- [x] **Step 4: Verify scope boundaries**

Confirm domain-neutral cleanup is not mixed into this change.

- [x] **Step 5: Run diff hygiene check**

Run `git diff --check`.
