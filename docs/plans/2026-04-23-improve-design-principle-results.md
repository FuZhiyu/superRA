# Workflow Frontier Resolver - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (Phase C complete — relocated to docs/plans/; Docs finalized flipped)
**Status:** All 11 tasks reviewer-approved, integration-approved, docs finalized. Ready for Phase D merge.

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

**Status:** IMPLEMENTED — scope covered role specs (`agents/implementer.md`, `agents/reviewer.md`), the master skill (`skills/using-superRA/SKILL.md`), and every reference under `skills/using-superRA/references/`. Generated direct-mode role references were regenerated from the updated source specs per `CLAUDE.md §Architectural Patterns`.

### Summary of Cuts and Pointers

**`agents/implementer.md`** — 54 lines removed net (~35 % shorter).
- DELETED — §Stage → skills and references wrapper paragraph (already the exhaustive authoritative line in `superRA:using-superra` §Skill-Load Manifest; the wrapper was anti-pattern "wrapper instructions around authoritative content").
- DELETED — §What the dispatch prompt carries — and doesn't "narration" paragraph describing which pieces live where (pure "here is what you will receive" anti-pattern). The behavior-shaping "treat paraphrased dispatch content as over-specification" sentence was KEPT and consolidated into the renamed §Dispatch Inputs section.
- DELETED — §Execution Protocol §Data-First Discipline bullets (describe / log row counts / validate / document decisions) — owned by `econ-data-analysis`. Replaced with a one-line POINTER: "Follow the discipline of the domain skill you loaded for this Stage."
- DELETED — §Execution Protocol §While You Work paragraph (duplicated under §Escalation already).
- DELETED — Step 6 Worktree wrapper in §Before You Start ("If the dispatch includes a `Worktree:` field, follow the canned steering...") — explicitly called out as anti-pattern in Task 5. The substantive behavior is in the dispatch's `Additionally:` line itself and in `agent-orchestration §Parallelization`; the wrapper added nothing.
- DELETED — example nested bullets under Step 1 ("At integration stage, you always load ...; for data analysis work, you load ...") — these are already specified in the Skill-Load Manifest.
- POINTER — §Editing Etiquette three-rule block collapsed to three one-liners and a pointer to `superRA:handoff-doc` for the full discipline. KEPT the inline-edit / task-block-boundary / doc-before-report rules as one-liners because they are behavior-shaping for every implementer edit.
- POINTER — Worktree-return rule in §Handoff trimmed to one line ("Return the `<branch>/parallel/<slug>` branch name and HEAD SHA in your status report. Do not merge, rebase, push, or touch worktree lifecycle — the orchestrator owns harvest-out.") since the lifecycle rules themselves live in `agent-orchestration`.
- KEPT — the "Evidence before claims" IDENTIFY / RUN / READ / VERIFY gate (behavior-shaping and non-default); §What You Own, What You Don't (behavior-shaping ownership rules); §How You Fix Review Items on a REVISE Round (non-default ordering constraint); §Pre-Commit Self-Check checklist (behavior-shaping); §Report Format (field list is behavior-shaping).

**`agents/reviewer.md`** — 38 lines removed net (~20 % shorter).
- DELETED — §Stage → skills and references and §What the dispatch prompt carries wrapper paragraphs (same anti-patterns as in implementer.md).
- DELETED — example nested bullets under the manifest-loading step.
- DELETED — long "The orchestrator populated it at planning time" narration in the §Project Conventions reading step — collapsed to behavior-shaping one-liner ("code that ignores a documented convention is a MAJOR integration-review finding" is KEPT).
- POINTER — §Editing Etiquette three-rule block collapsed to one-liners plus pointer to `superRA:handoff-doc`.
- KEPT — §Severity Levels (authoritative severity rubric), §Verdict protocol (non-default ordering constraint), §How You Write a Review first-review and re-review procedures (non-default), §CRITICAL severity invariant, §Pre-Commit Self-Check, §Report Format.
- Also fixed a stray `into dispatch prompts.` fragment in the frontmatter description (dangling orphan from a prior edit).

**`skills/using-superRA/SKILL.md`** — 1 line tightened.
- Trimmed the over-long paragraph describing where handoff-doc discipline lives (it is now one sentence pointing at the role-spec compact etiquette and `superRA:handoff-doc`).
- KEPT — Runtime Workflow Map, Commit Hygiene, Skill Inventory, Skill-Load Manifest, Instruction Priority. These are all authoritative content owned by this skill.

**`skills/using-superRA/references/main-agent.md`** — §Execution Modes collapsed from 28 lines to 10 lines.
- DELETED — the Codex-agent block at the bottom of §Execution Modes (lines 139-153 pre-edit). It was a near-duplicate of `codex-instructions.md §Delegation Priority in Codex` with a typo (`spwawn`) and a dangling orphan fragment ("when the workflow allows it and the user requested it, the task is trivial, or agent tools are unavailable."). Replaced with a single-line POINTER: "Codex agents: MUST load `references/codex-instructions.md` immediately."
- KEPT — §Session Start Actions, §Load the Handoff-Doc Skill, §Workflow Frontier Resolver (Task 2 owner), §Changes of the Plan (pointer), §Three Pause Classes, §Proceed Without Asking, §Banned Phrasings, §One Question at a Time, §Log Before You Act. All behavior-shaping; most are authoritative for their concern.
- KEPT — Subagent-default sentence and the direct-mode protocol bullets. Behavior-shaping (they shape when the main agent dispatches vs stays inline).

**`skills/using-superRA/references/codex-instructions.md`** — no edits. Audit pass confirmed this file is the authoritative owner of Codex delegation priority, warm-agent lifecycle, and tool-map content; every line is either a non-default constraint or a tool-name mapping. POINTER target check: `main-agent.md`'s §Execution Modes now cites this file correctly.

**`skills/using-superRA/references/claude-tools.md`, `copilot-tools.md`, `gemini-tools.md`** — no edits. These are adapter tool-name mapping tables; every row is behavior-shaping (the tool-name mapping is the content).

**`skills/using-superRA/references/direct-mode-implementer.md`, `direct-mode-reviewer.md`** — regenerated from the updated source specs. Per `CLAUDE.md §Architectural Patterns` (Generated artifacts stay generated), these are not hand-edited. The generator now:
1. No longer reads a `## Stage → skills and references` section (removed from source per Task 6); direct-mode's own §Before You Start step 1 carries the manifest-load instruction.
2. Produces a compact direct-mode §Before You Start that mirrors the trimmed subagent version — POINTER style, no example nested bullets.
3. Keeps `cleanup_implementer_handoff` and `cleanup_reviewer_handoff` pattern-replace helpers. The implementer helper rewrites the §How You Fix Review Items opener (subagent source at `agents/implementer.md:97` references "first dispatch" and a "re-dispatch prompt" one-line delta, neither of which exists in direct mode) and strips the Parallel worktree dispatch paragraph (`agents/implementer.md:134`, a subagent dispatch-field concept) entirely. The reviewer helper rewrites the `## Upstream Intent` ownership paragraph (`agents/reviewer.md:109`) so the round context is sourced from `PLAN.md` / the current session rather than "from the dispatch." Both helpers fail loudly with `ValueError` when their expected source strings disappear — regenerator drift becomes a test failure, not a silent leak. The reviewer-side `strip_subsection` of §Report Format and the "ad-hoc default" deletion are also kept because those fragments still appear in the subagent body.

### Verification

- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` — PASS.
- `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` — 5 tests pass (generator idempotency, direct-mode round-trip, managed-header presence, conflict handling, regenerate-hint).
- `git diff --check` — clean.
- Cross-check: every POINTER inserted this round points at content that actually exists at the cited source — `superRA:handoff-doc` carries the full editing-etiquette discipline; `econ-data-analysis/SKILL.md` carries Data-First principles under `§The Iron Law` and the `[BLOCKING]` / `[ADVISORY]` gated checklists; `codex-instructions.md §Delegation Priority in Codex` carries the Codex named-agent rule.
- Leak grep: `grep -nE "first dispatch|re-dispatch prompt|Parallel worktree dispatch|Worktree.*field set|in the dispatch|orchestrator passes the round context" skills/using-superRA/references/direct-mode-*.md` returns no matches after cleanup — the preface's "no dispatch prompt" sentence is the only dispatch-word occurrence, and it is intentional.

### Files Changed

- `agents/implementer.md`
- `agents/reviewer.md`
- `skills/using-superRA/SKILL.md`
- `skills/using-superRA/references/main-agent.md`
- `skills/using-superRA/references/direct-mode-implementer.md` (regenerated)
- `skills/using-superRA/references/direct-mode-reviewer.md` (regenerated)
- `skills/codex-superra-setup/scripts/sync_codex_agents.py`
- `.codex/agents/superra_implementer.toml` (regenerated)
- `.codex/agents/superra_reviewer.toml` (regenerated)
- `skills/agent-orchestration/references/worktree-harness-fallback.md` (cross-reference repointed after review round 1 surfaced a stale pointer to `agents/implementer.md §Before You Start`, which no longer owns the Worktree-enter step)

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

**Status:** Implemented; awaiting review.

### Pointer Integrity

Verified every POINTER introduced in Tasks 7 and 8 resolves to a real anchor carrying the referenced content. (Task 6's pointers — direct-mode cleanup helpers, `worktree-harness-fallback` repoint, `superRA:handoff-doc` / `codex-instructions.md` / `econ-data-analysis` targets — were verified by the Task 6 reviewer and left untouched here.)

Task 7 pointers verified:
- `planning-workflow §Living Plan and Results Docs` → `handoff-doc §references/results-anatomy.md` — `results-anatomy.md` exists with full template, pre-allocated stub discipline at line 26 and §Section ownership at line 87.
- `planning-workflow §Execution Handoff` → `using-superra §Execution Modes` — present at `skills/using-superRA/SKILL.md:68-70`; chains to `main-agent.md §Execution Modes` at lines 126-138.
- `implementation-workflow §Step 1` / §Autonomy → `main-agent.md §Workflow Frontier Resolver` — present at `main-agent.md:25-70`.
- `integration-workflow §Phase Map` — `§Frontier Entry` deleted; replacement single-paragraph notice at lines 15-27 is self-contained and the Phase Map itself carries what the deleted section narrated.

Task 8 pointers verified:
- `econ-data-analysis/references/integrate-drift-tests.md §Tolerance Conventions` → `drift-test-quality.md §Tolerance calibration` — resolves at `drift-test-quality.md:9` (§How-To → Tolerance calibration, with worked examples).
- `handoff-doc/SKILL.md §User Decisions Log` → `references/plan-anatomy.md §User Decisions Log` — resolves at `plan-anatomy.md:101`; task-scoped vs project-level rules at line 108.
- `handoff-doc/references/plan-anatomy.md §Upstream Intent` — top-level pointer at line 65 resolves to full section at line 124.
- `report-in-markdown/SKILL.md §figure defaults` → `rich-content.md §The attachments directory is a caller parameter` — resolves at `rich-content.md:7`.
- `integration-workflow §Phase C Step 4` → `codebase-integration.md §Project Doc Audit` — resolves at line 19 (walk-up algorithm) and line 97 (checklist anchor).
- `refactor-and-integrate §Load-Bearing Top Item` → `codebase-integration.md §Reviewer Verdict Protocol` — resolves at line 38.
- `integration-workflow §Phase D Step 4` cleanup chain — `worktree-harness-fallback.md §Remove` present at line 32; `worktree-data-sync §Data Teardown` present at line 144.
- `handoff-doc §What You May NOT Edit (reviewer)` → `plan-anatomy.md §Header ownership` — resolves at line 61.
- `integration-workflow §Phase C Step 2` → `final-form.md §The consolidation pass — four ordered commits` — resolves at line 5.

No dangling pointer was found.

### Residual Duplication

Grepped for behavior-shaping phrases and confirmed each concern has one authoritative owner:

- **Data-First discipline / Iron Law / describe-analyze-validate** — owned exclusively by `skills/econ-data-analysis/SKILL.md`. Post-audit role specs carry no Data-First bullets (Task 6 removed them); `implementer.md:29` now points at "the domain skill you loaded for this Stage." No duplication.
- **Editing etiquette (Inline-edit / Preserve task-block boundaries / Doc before report)** — authoritative full version in `handoff-doc/SKILL.md §Inline-Edit Rule` + §Four Principles + §Stale Content Checklist. Compact one-liners appear in `agents/implementer.md:67-69` and `agents/reviewer.md:95-98`, each with a pointer back to `superRA:handoff-doc`. The direct-mode copies (`direct-mode-implementer.md:64-66`, `direct-mode-reviewer.md:90-91,93`) are auto-regenerated from the role specs (per Task 6 §Verification). Two-way role duplication (implementer vs reviewer) is tailored per role and cannot collapse further without breaking the role-specific context. Acceptable.
- **Execution Modes** — authoritative copy in `main-agent.md §Execution Modes` (lines 126-138); `using-superra/SKILL.md:68-70` points at it; three workflow skills (`planning-workflow:194`, `implementation-workflow:100`, `agent-orchestration:200`) all point at `using-superra §Execution Modes`. Single-chain ownership, no paraphrase duplication.
- **Skill-Load Manifest** — authoritative copy in `using-superra/SKILL.md:72` (§Skill-Load Manifest). Eight mention sites across `skills/` and `agents/` are all pointers ("see `superRA:using-superra` §Skill-Load Manifest") — no content duplication.
- **User Decisions Log** — authoritative full spec in `handoff-doc/references/plan-anatomy.md §User Decisions Log` (line 101); `handoff-doc/SKILL.md §User Decisions Log` (line 41) carries a one-paragraph summary and points at the spec. Every other mention across workflow skills is a pointer at the SKILL.md section. No duplicated content.
- **Workflow Frontier Resolver** — authoritative in `main-agent.md §Workflow Frontier Resolver`. `planning-workflow:153` and `implementation-workflow:64,73` point at it as the routing mechanism. `using-superra/SKILL.md:18-26` §Runtime Workflow Map paragraph ends by naming what the resolver adds; that is a summary, not a duplicate of the mechanism.
- **Commit Hygiene** — authoritative in `using-superra/SKILL.md §Commit Hygiene`. `agents/implementer.md:128` and `agents/reviewer.md:129` cite it rather than restate it.

No residual duplication that creates a drift risk.

### Anti-Pattern Regression

Re-ran the four CLAUDE.md anti-pattern categories against the post-audit tree.

- **(a) Wrapper instructions around authoritative content.** Grep `If the dispatch (includes|carries|contains|has) a .Worktree` returns only the CLAUDE.md example itself at line 46. Worktree-field wrapper removed from role specs (Task 6) and not reintroduced. PASS.
- **(b) "Here is what you will receive" descriptions.** Grep finds only the CLAUDE.md example itself at line 47. However, two borderline instances survive: `agents/implementer.md:15` §Dispatch Inputs and `agents/reviewer.md:22` §Dispatch Inputs each open with "The dispatch prompt carries only the Stage, a task pointer, a git range (if reviewing), and an optional `Additionally:` steering line." The second sentence ("If the dispatch paraphrases ... treat that as over-specification and use your standard protocol + the authoritative sources it points at") is behavior-shaping and was explicitly KEPT by the Task 6 reviewer. The first sentence provides the baseline for what counts as "more than this." Removing the first sentence would leave the second without a referent. **Flagged for orchestrator judgment**, not fixed in place — this is not an unambiguous anti-pattern.
- **(c) Reminders of runtime defaults.** No "if you are asked to load a skill, load the skill" style throat-clearing survives. `by default` hits are all substantive ("base branch is authoritative by default," "upstream deletions honored by default," "the cascade clears downstream by default") — each is a behavior-shaping default that agents would not infer. PASS.
- **(d) Restatements of the Skill-Load Manifest inside dispatch or role bodies.** Every site (role specs, direct-mode files, workflow skills, orchestration references) is a one-line pointer, not a content restatement. The `agents/implementer.md:19` and `agents/reviewer.md:26` lines say "Load skills per `superRA:using-superra` §Skill-Load Manifest" with no per-row content. PASS.

Three of four anti-pattern categories show no regression. Category (b) has one consistent borderline pattern across both role specs that the orchestrator should decide on — either accept (status quo, Task 6 reviewer approved it) or rewrite the §Dispatch Inputs opening to put the behavior-shaping rule first without a "here is what you will receive" framing.

### Summary

- Pointer integrity: 15/15 POINTERs verified resolvable at cited anchors.
- Residual duplication: zero drift-risk duplications; all multi-site mentions are either pointers or role-scoped compacts over a single authoritative owner.
- Anti-pattern regression: 3/4 categories clean; 1 borderline pattern flagged for orchestrator judgment.
- Nothing Tasks 6-8 deleted became unrecoverable — every trimmed line's authoritative owner carries the content at a resolvable anchor.

### Files Changed

- `PLAN.md` (Task 9 status, step checkboxes, step notes)
- `RESULTS.md` (Task 9 section)

## Task 10: Formalize Post-Audit Refinements

**Status:** Implemented; awaiting review.

### Findings

**Tolerance rubric relocation.** Moved the full rubric — point estimates, standard errors, counts, signs/significance, plus the worked "document every tolerance choice" example — from `refactor-and-integrate/references/drift-test-quality.md §Tolerance calibration — worked examples` into `econ-data-analysis/references/integrate-drift-tests.md §Tolerance Conventions for Econ Results`. The cross-cutting file now carries a one-paragraph domain-agnostic placeholder that points at the econ reference for data-analysis work; new verticals carry their own rubric in the same domain-reference slot. The `drift-test-quality.md` gated-checklist item for tolerance calibration was rephrased so it names domain reasoning generally and points at the econ reference for worked examples.

**Inverted cross-reference removed.** Deleted the `> **Data-analysis work:** also load ...` blockquote from `codebase-integration.md`. Pointer flow is now domain → cross-cutting only: `econ-data-analysis/references/integration.md` retains its companion pointer into `codebase-integration.md`, and the reverse pointer no longer inverts the dependency. Fixed one surviving in-file reference that still said "cited in the blockquote above" — now names `econ-data-analysis/references/integration.md` directly.

**Role-spec condensation (researcher WIP `93fda71`).** Accepted the researcher's manual edits to `agents/implementer.md` and `agents/reviewer.md`: shorter §Dispatch Inputs opening, new framing that `PLAN.md` is authoritative unless the dispatch explicitly overrides it (replaces the longer "treat paraphrased content as over-specification" wording with equivalent behavior-shaping content), unified handoff-doc compact etiquette, and a new "Remove superseded content, don't stack it" bullet that already matches `handoff-doc/SKILL.md §The Four Principles`. Typo `authorative → authoritative` fixed. Fixed two remaining rough edges: the missing period in `agents/implementer.md` frontmatter description ("agent Used" → "agent. Used", now matching `reviewer.md`'s frontmatter shape) and an inconsistent blank line in the compact-etiquette list that separated the fourth bullet ("Doc before report") from the first three in both files — collapsed to a single continuous 4-item list.

**Downstream regeneration.** Ran `sync_codex_agents.py --scope project`; regenerated `skills/using-superRA/references/direct-mode-implementer.md`, `direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`. Generator tests: `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` — 5/5 pass. Leak grep (`first dispatch|re-dispatch prompt|parallel worktree dispatch|in the dispatch`) on the regenerated direct-mode refs — clean.

### Files Changed

- `agents/implementer.md` (typo fix, frontmatter period, 4-bullet list collapse; condensation already in `93fda71`)
- `agents/reviewer.md` (4-bullet list collapse; condensation already in `93fda71`)
- `skills/econ-data-analysis/references/integrate-drift-tests.md` (tolerance rubric inserted)
- `skills/refactor-and-integrate/references/drift-test-quality.md` (rubric replaced with pointer; checklist reworded)
- `skills/refactor-and-integrate/references/codebase-integration.md` (inverted cross-ref + HTML comment removed)
- `skills/using-superRA/references/direct-mode-implementer.md` (regenerated)
- `skills/using-superRA/references/direct-mode-reviewer.md` (regenerated)
- `.codex/agents/superra_implementer.toml` (regenerated)
- `.codex/agents/superra_reviewer.toml` (regenerated)
- `PLAN.md` (Task 10 added, decision log entry, Workflow Status sub-comment)
- `RESULTS.md` (this section)

### Verification Commands

- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py`
- `grep -Ei "first dispatch|re-dispatch prompt|parallel worktree dispatch|in the dispatch" skills/using-superRA/references/direct-mode-*.md`

## Task 11: Enshrine the Teach-the-Protocol Principle as a Gate

**Status:** Implemented; awaiting review.

### Findings

Promoted `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` from a documented design principle to an explicit gate. The section now leads with a bold **"This is a gate."** paragraph that states:
- **Scope**: every file under `skills/*` and `agents/*`.
- **Actors**: implementers self-apply the necessity test before every commit; reviewers verify on every pass.
- **Severity**: a line that fails the test is a `[BLOCKING]` finding, not a stylistic preference.

Because `CLAUDE.md` is auto-loaded for any edit in this repo, the gate propagates to every future implementer/reviewer working on superRA internals without needing role-spec changes or regeneration. The two ordered tests (DRY, necessity), the anti-pattern list, and the "Keep" carve-out from Task 5 are preserved intact — the gate statement is additive.

### Files Changed

- `CLAUDE.md` (gate statement prepended to the section)
- `PLAN.md` (Task 11 added, decision log entries for Phase A drift tests, base-branch confirmation, and Task 11 scope add)
- `RESULTS.md` (this section; top-of-file Status and Last-updated lines)

## Known Follow-Ups (Deferred Polish)

Post-APPROVE items the reviewer flagged or surfaced for orchestrator judgment; deferred rather than blocking the integration flip. Track here so the next editor under the teach-the-protocol gate can sweep them.

- **`test_sync_codex_agents.py` hardening** (Task 6 MINOR #5). Add a smoke assertion that direct-mode outputs do not contain dispatch-only wording (`first dispatch`, `re-dispatch prompt`, `Worktree: field`, `in the dispatch` outside the opening "no dispatch prompt" preface). The restored `cleanup_*_handoff` helpers already `raise ValueError` when their source-text targets drift, so the current silent-regression class is covered; this test would belt-and-brace that.
- **Reviewer compact-etiquette bullet example** (Phase B integration review MINOR). `agents/reviewer.md:98` and its generator copy `skills/using-superRA/references/direct-mode-reviewer.md:89` use `→ implemented:` as the illustrative action in the shared boundary-preservation rule, but `→ implemented:` is implementer-only. The underlying rule (stay within the assigned task block, preserve `---` separators and `### Task N:` headings) is correct for reviewers too; the example should be reworked to a reviewer action (e.g., "when writing or removing a review-notes blockquote"). Requires regen of the direct-mode copy via `sync_codex_agents.py --scope project`.
