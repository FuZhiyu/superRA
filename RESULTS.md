# Workflow Frontier Resolver - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (over-prescription audit scope added)
**Status:** Tasks 1-4 approved; Task 5 implemented and awaiting review; Tasks 6-9 pending.

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

**Status:** Not started.

## Task 8: Audit Utility, Domain, and Meta Skills

**Status:** Implemented; awaiting review.

### Findings

Applied the `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` principle (DRY + necessity) line-by-line across the 22 in-scope files in `skills/handoff-doc/`, `skills/refactor-and-integrate/`, `skills/report-in-markdown/`, `skills/semantic-merge/`, `skills/worktree-data-sync/`, `skills/econ-data-analysis/`, and `skills/codex-superra-setup/`. Preserved standalone-usability per the Task 8 extra constraint: every domain/utility/meta skill still reads coherently when loaded directly by a researcher outside the superRA workflow.

Net change: 19 files modified, ~95 lines removed / ~69 inserted (roughly a 1:1.4 shrink where edits landed). No `SKILL.md` frontmatter changed. No gated checklist item removed. No pointer target became stale.

**Per-file summary of cuts (C), pointers (P), and kept-as-is (K):**

- `handoff-doc/SKILL.md` — C: reference-row narration that restated what the reference owns; throat-clearing "If you catch yourself..." line. P: pointer in User Decisions Log to `main-agent.md` tightened. K: four principles, inline-edit rule, stale-content checklist (all behavior-shaping).
- `handoff-doc/references/plan-anatomy.md` — C: "Subagents read the relevant header context at the start of every task" narration; `## Upstream Intent` description duplicated between Header ownership and the §Upstream Intent subsection (now a one-line pointer). K: template blocks, field-by-field notes, placement rules, `## Project Conventions` discipline, User Decisions Log format.
- `handoff-doc/references/results-anatomy.md` — C: "Together with `PLAN.md`, Stage 1 `RESULTS.md` forms a complete handoff..." motivational sentence. K: template, pre-allocated stubs, section ownership, reviewer caveats, Stage 2 transition.
- `refactor-and-integrate/SKILL.md` — C: wrapped-index narration on load contents ("with `[BLOCKING]` / `[ADVISORY]` severity markers, tuned Red Flags..."). P: each discipline now points by filename without re-narrating. K: three-disciplines principle, Load-Bearing Top Item.
- `refactor-and-integrate/references/codebase-integration.md` — C: opening "Shared cross-cutting code-quality reference..." verbosity; "One source of truth, two perspectives" flourish. K: how-to sections, Reviewer Verdict Protocol, full gated checklist.
- `refactor-and-integrate/references/drift-test-quality.md` — C: opening "Shared domain reference..." verbosity; §Cross-cutting Red Flags verbose "These rules apply wherever... The workflow skills and the SKILL.md body point at this section rather than restate the rules locally." P: failing-test escalation line now owns its own guidance and points at orchestration. K: how-to sections, tolerance worked examples, red-green cycle, gated checklist.
- `refactor-and-integrate/references/merge-quality.md` — C: opening "Shared domain reference..." verbosity. K: commit-structure templates, Tier 3 escalation, upstream-intent identification, handoff-doc coherence, integration-map format, full gated checklist.
- `report-in-markdown/SKILL.md` — C: "Figure directory: caller decides" three-bullet narration that duplicated `rich-content.md`; Invocation contract merged to three bullets. P: SKILL.md now points at `rich-content.md` for stage defaults. K: when-to-invoke, load map table, references index.
- `report-in-markdown/references/baseline-io.md` — C: parenthetical "(they have no per-task frontmatter; the file-level frontmatter, if any, is handled by `handoff-doc`)." K: path resolution, metadata capture, frontmatter spec, write/return-link procedure.
- `report-in-markdown/references/final-form.md` — C: opening load-condition verbosity; "the atomicity is the whole point" rationale flourish. K: four-ordered-commits procedure, fact-check checklist, prohibited-language patterns, output shape.
- `report-in-markdown/references/rich-content.md` — C: opening load-condition verbosity. P: fallback default line moved into the main body so the SKILL.md can point here. K: figure/math/tables/file-reference mechanics.
- `semantic-merge/SKILL.md` — C: parenthesized hook rationale inlined; `integration-workflow` caller-specific framing generalized to "caller runs drift tests" so the skill reads standalone. K: process steps, intent-identification rule, Red Flags, research-meaningful escalation.
- `worktree-data-sync/SKILL.md` — C: "See also:" phrasing at top inlined into a plain pointer; When-to-Use colon line tightened. K: CLI contract, mode semantics, managed-path discovery, examples, teardown.
- `econ-data-analysis/SKILL.md` — C: Stage-Scoped References table collapsed into one combined table (removed the two-table split + per-row "Loaded by ..." workflow narrations); Three Concurrent Disciplines teaching-content/shared-checklist meta-narration; Reviewer verdict protocol parentheticals; §Pitfalls meta-narration. K: Iron Law, discipline content (Describe/Analyze/Validate gated items), Pitfalls subsections, Common Rationalizations.
- `econ-data-analysis/references/planning.md` — C: "This reference carries two planning-only concerns that would otherwise bloat..." meta-narration; Data Inventory opening verbose "The researcher arrives..." framing; Handoff to Implementation restated the main body's discipline. K: Hard Gate checklist, principles, common mistakes, red flags, Sensitivity Analysis Design, pipeline-file requirement.
- `econ-data-analysis/references/integration.md` — C: opening two-paragraph narration that echoed the reviewer-verdict protocol and the load-both-files instruction. P: Reviewer verdict protocol pointer tightened. K: all `[BLOCKING]` / `[ADVISORY]` gates.
- `econ-data-analysis/references/integrate-drift-tests.md` — C: three-question restatement narration; opening "Load at the INTEGRATE phase... `integration-workflow` Phase A invokes this reference..." workflow narration; Cross-Cutting Integrity Rules prose paragraph reduced to a pointer; Tolerance Conventions table now a pointer to `drift-test-quality.md` §Tolerance calibration (which owns it). K: key-result identification, econ failure modes, why-drift-tests-matter framing.
- `econ-data-analysis/references/notebook-format.md` — C: opening blockquote that restated loader identity + workflow callsite. K: cell organization, markdown cells, writing discipline, output idioms, rendering sections.
- `codex-superra-setup/SKILL.md` — C: reworded opening so it reads standalone without duplicating plugin-level framing. K: scope choice, procedure, verification, notes.

**No files received structural edits** — all changes were inline within existing sections. No frontmatter `description` strings changed (they remain the primary discovery surface for harnesses).

**Standalone-usability check.** For each skill, re-read the post-edit `SKILL.md` as if loaded outside superRA:

- `handoff-doc` — still works standalone; references to `planning-workflow Phase 2` / `integration-workflow Phase C` are framed as "doc-creation call sites" examples, not prerequisites.
- `refactor-and-integrate` — standalone by design (already worded for drift-test / refactor / merge use outside INTEGRATE); no change to that story.
- `report-in-markdown` — standalone path preserved (Load map row "Standalone markdown report (any context)" survives; fallback `attachments/` default remains).
- `semantic-merge` — now reads as a research-aware merge skill with superRA Phase B as one caller among others; the caller-specific framing was generalized.
- `worktree-data-sync` — already standalone CLI-centric; opening line tightened without adding orchestration-specific wording.
- `econ-data-analysis` — standalone by design; "Stage-scoped discipline" block now frames integration-workflow Step 3 as "in superRA, see..." rather than as required.
- `codex-superra-setup` — installer skill; standalone lifecycle intact.

### Files Changed

- `skills/handoff-doc/SKILL.md`
- `skills/handoff-doc/references/plan-anatomy.md`
- `skills/handoff-doc/references/results-anatomy.md`
- `skills/refactor-and-integrate/SKILL.md`
- `skills/refactor-and-integrate/references/codebase-integration.md`
- `skills/refactor-and-integrate/references/drift-test-quality.md`
- `skills/refactor-and-integrate/references/merge-quality.md`
- `skills/report-in-markdown/SKILL.md`
- `skills/report-in-markdown/references/baseline-io.md`
- `skills/report-in-markdown/references/final-form.md`
- `skills/report-in-markdown/references/rich-content.md`
- `skills/semantic-merge/SKILL.md`
- `skills/worktree-data-sync/SKILL.md`
- `skills/econ-data-analysis/SKILL.md`
- `skills/econ-data-analysis/references/planning.md`
- `skills/econ-data-analysis/references/integration.md`
- `skills/econ-data-analysis/references/integrate-drift-tests.md`
- `skills/econ-data-analysis/references/notebook-format.md`
- `skills/codex-superra-setup/SKILL.md`

### Verification Commands

- `git diff --stat` — 19 files, ~95 deletions / ~69 insertions.
- `git diff --check` — clean (no whitespace issues).
- Pointer integrity spot-check: `grep -n "Tolerance calibration" skills/refactor-and-integrate/references/drift-test-quality.md` (§How-To → Tolerance calibration present at line 9), `grep -n "attachments directory is a caller parameter" skills/report-in-markdown/references/rich-content.md` (present at line 7), `grep -n "Upstream Intent" skills/handoff-doc/references/plan-anatomy.md` (full §Upstream Intent present at line 124).

## Task 9: Cross-Audit Consistency Sweep

**Status:** Not started.
