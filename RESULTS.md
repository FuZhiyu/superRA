# Workflow Frontier Resolver - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (over-prescription audit scope added)
**Status:** Tasks 1-4 approved; Task 5 approved; Task 7 implemented and awaiting review; Tasks 6, 8, 9 pending.

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
- The clarity revision now separates diagnosis/routing from workflow-owned actions: `main-agent.md` says the resolver diagnoses and routes, while the owning workflow performs plan edits, implementation, integration, or merge work.
- The rollup wording now says checked milestones are invalid when they no longer match task evidence or required global gates; the owning workflow or plan-change protocol should uncheck them and record why.
- The plan-change boundary is explicit: material plan changes route to `planning-workflow §User Feedback and Changing Plans`, then the resolver runs again after the docs are updated.

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
- The next audit will add reviewer feedback specifically on clarity and the boundary between resolver routing and the change-plan protocol.
- A focused reviewer pass approved the clarity revision, including the diagnosis/routing distinction, change-plan boundary, workflow-status rollups, and task-local status preservation.

### Verification Commands
- `rg -n "needs plan repair|needs implementation|awaiting review|needs validation|Current state|state machine|skip|resume|re-entry|if .* then|under .* condition" skills/using-superRA skills/*/SKILL.md`
- `git diff --check`
- `uv run python /Users/zhiyufu/Dropbox/app_settings/dotfiles/claude/.claude/skills/.system/skill-creator/scripts/quick_validate.py <modified-skill-folder>` for `skills/using-superRA`, `skills/planning-workflow`, `skills/implementation-workflow`, `skills/integration-workflow`, and `skills/agent-orchestration`

## Task 5: Document "Teach the Protocol, Don't Prescribe Each Action" Principle

**Status:** Implemented; awaiting review.

### Findings
- Added `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` under `## Internal Design Philosophy` with the governing test, two ordered sub-tests (DRY, necessity), anti-patterns drawn from current repo examples, and a distinction for behavior-shaping instructions that must be kept.
- Extended `## Design Audit Checklist` with a per-line test: does removing it change what the agent would *do*, or only what it would *understand*?

### Files Changed
- `CLAUDE.md`

## Task 6: Audit Agent Role Specs and `using-superRA` Surfaces

**Status:** Not started.

## Task 7: Audit Workflow Skills and `agent-orchestration`

**Status:** Implemented; awaiting review.

### Findings

Applied the two tests from `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` to every paragraph in `skills/planning-workflow/SKILL.md`, `skills/implementation-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`, and the two `agent-orchestration/references/` files.

A prior audit session had already trimmed obvious prescription wrappers (the "what the standard protocol carries" rephrasings at each workflow skill's top, the full Handling Reviewer Feedback paraphrase inside `implementation-workflow`, the closing "Before proceeding…" reminders, and the banned-fields paraphrase in the Dispatch Convention lines). This pass extended that work along the audit targets called out in the Task 7 scope warning.

**Edits this pass:**

- **`planning-workflow/SKILL.md`**:
  - **POINTER** — Living Plan and Results Docs: trimmed the Results-stub narration ("header and one pre-allocated stub per task block — same order, same task name…") to a pointer at `handoff-doc/references/results-anatomy.md`. The anatomy is authoritative there.
  - **DELETE** — end of §PLAN.md Is the Task Tracker: removed the duplicated "After the plan edit is committed, the main agent runs … Workflow Frontier Resolver to choose the next workflow entry point" sentence. The same instruction appears as Step 7 of the §User Feedback and Changing Plans protocol immediately below.
  - **POINTER/TIGHTEN** — Step 7 of the change-plan protocol: removed the "It owns cross-workflow entry selection; the target workflow then runs the local gates and any global verification required before merge / PR" paraphrase. The resolver section at `main-agent.md` is authoritative.
  - **POINTER** — §Execution Handoff: collapsed the two-paragraph "Subagent-Driven vs Inline Execution" description into a single pointer at `using-superra` §Execution Modes. The description was duplicating the Execution Modes definition that `using-superra` owns.
- **`implementation-workflow/SKILL.md`**:
  - **TIGHTEN** — Step 1 item 2: shortened the resolver-entry protocol paragraph while preserving the behavior-shaping content (continue only when resolver selects this workflow; skip to Step 3 / 4 when all selected tasks are `APPROVED`).
  - **TIGHTEN** — §Autonomy and Stop Points: removed the inaccurate "merge now / continue another task / sensitivity task / discard" paraphrase of the Step 4 menu options (the actual options differ) and pointed at Step 4 instead.
- **`integration-workflow/SKILL.md`**:
  - **DELETE** — §Frontier Entry: removed the whole section. It restated what §Phase Map already says ("the resolver chooses where to enter this map; run the selected phase's local gates exactly; do not redo task-local approvals outside the affected frontier").
- **`agent-orchestration/SKILL.md`**:
  - **TIGHTEN** — Dispatch-template inline comments: shortened the "never restate what the default protocol, skill-load manifest, or PLAN.md already says" boilerplate that appeared inside both Implementer and Reviewer template code blocks. The same rule is stated in the surrounding prose (once in the prefix description, once in "Optional steering is strictly additive"); the in-template copy was a third restatement.

**KEEP (behavior-shaping, not prescription):**

- All local phase gates, step-ordering rules, stop points, status transitions, and review-verdict discipline across the four files.
- Dispatch Template shape, canonical-prefix description, and "Optional steering is strictly additive" rule in `agent-orchestration` — this skill's raison d'être.
- Per-workflow `Agent Loads` one-liners pointing at the Skill-Load Manifest — tolerable one-line echoes that save agents a manifest lookup.
- "First, load `superRA:using-superra` if not already loaded" at the top of each workflow skill — one-line echoes of the frontmatter precondition.
- Red Flags blocks in `implementation-workflow` / `integration-workflow` — negative-form behavior-shaping rules.

**Ownership boundaries after the trim (re-checked against `CLAUDE.md §Ownership Boundaries`):**

- Phase choreography, stop points, status transitions → still owned by the three workflow skills.
- Cross-stage orchestration, dispatch-prompt shape, verdict adjudication → still owned by `agent-orchestration`.
- Execution modes and Skill-Load Manifest → now fully owned by `using-superra`; `planning-workflow §Execution Handoff` points at it instead of restating it.
- Handoff-doc mechanics, templates, stale-content rules → `planning-workflow §Living Plan and Results Docs` now points at `handoff-doc/references/results-anatomy.md` rather than excerpting it.
- Workflow Frontier Resolver → still owned by `main-agent.md`; the duplicated "run the resolver after a plan edit" sentence in planning-workflow is removed.

No ambiguity or newly-introduced gap detected. The deleted `integration-workflow §Frontier Entry` content is fully covered by the Phase Map paragraph that remains. The deleted planning-workflow Resolver sentence is fully covered by Step 7 of the change-plan protocol.

### Files Changed

- `skills/planning-workflow/SKILL.md`
- `skills/implementation-workflow/SKILL.md`
- `skills/integration-workflow/SKILL.md`
- `skills/agent-orchestration/SKILL.md`
- `PLAN.md` (Task 7 status)
- `RESULTS.md` (Task 7 section)

## Task 8: Audit Utility, Domain, and Meta Skills

**Status:** Not started.

## Task 9: Cross-Audit Consistency Sweep

**Status:** Not started.
