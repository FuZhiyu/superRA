# superRA Plugin Restructure Plan — Round 3 (Master Skill + Skill-Load Manifest)

> **For agentic workers:** this is a PLUGIN META-REFACTOR — the "analysis" is the superRA plugin itself. Use `superRA:execution-workflow` (one-pass review per the canonical post-Task-6 protocol). The domain skill `superRA:econ-data-analysis` applies only when tasks touch data-analysis content; most tasks here are skill-file edits.

**Objective (Round 3).** Promote `superRA:using-superRA` to the master skill that every agent (main + dispatched subagent + Team teammate) reads. It carries the distilled universal principles, the Workflow / Domain / Utility / Meta skill inventory, the composable-design map, and a single authoritative **Skill-Load Manifest** (six role-independent Stages with required skills + stage-scoped references). `skills:` frontmatter on `agents/implementer.md` and `agents/reviewer.md` preloads `using-superRA` for CC subagent dispatches; SessionStart injection covers the main agent; Team teammates pick it up via their regular-session path. The 11-row Stage tables in both agent files collapse to one-line pointers at the manifest. `auto-load` / `auto-loaded` language is retired plugin-wide (no meta-explanation — agents only need the manifest). `agent-orchestration/SKILL.md` is split: high-level orchestration stays in SKILL.md; TeamCreate mechanics + parallel-dispatch patterns move to `references/agent-teams.md`; the stale Team Recipes section is deleted. `## Direct Mode` relocates to `using-superRA` §Execution Modes. `handoff-doc` principles #4 and #5 are deleted. `econ-data-analysis/references/integration.md` gains a `[STANDARD]` document-code consistency item. The plugin's `CLAUDE.md` is contributor-only — every principle agents must know is restated in `using-superRA`.

**Methodology.** Implementer + reviewer pair per task (one comprehensive pass, APPROVE / REVISE / CONDITIONAL APPROVE). Atomic commits on `refactor/workflow-domain-split`. `bash tests/structural-invariants.sh` green at each step. PR #1 updates on push.

**Data Inventory.** N/A — plugin meta-refactor. No datasets.

**Output.** Rewritten `using-superRA/SKILL.md` + new `references/session-bootstrap.md`. Frontmatter-preloaded `agents/implementer.md` + `agents/reviewer.md` with Stage tables replaced by pointers. Split `agent-orchestration/SKILL.md` + new `references/agent-teams.md`. Retargeted Direct Mode pointers across the plugin. Deleted handoff-doc #4 + #5; added integration.md document-code consistency item. Updated `tests/structural-invariants.sh` (blocks #20–#23). Extended `RELEASE-NOTES.md`.

**Pipeline.** `bash tests/structural-invariants.sh`.

**Background plan document.** `/Users/zhiyufu/.claude/plans/agile-orbiting-star.md` carries the full Round 3 design rationale, decisions, and risk-rollback. This PLAN.md is the task tracker.

---

## Decisions

> **User decision (2026-04-15, Round 3 post-push):** chose Option 2 (merge via PR) at `execution-workflow` Step 4. Retroactive invocation — the first three rounds pushed directly to PR #1 without running `integration-workflow` or `merge-workflow`; we now run `integration-workflow` before the actual main merge, to catch drift that the push-direct pattern skipped. Also accepted: broaden `refactor-and-integrate/references/codebase-integration.md` §Documentation Currency generically (any structural/organizational claim, not just output lists) as a Stage 2 refactor item if the integration reviewer surfaces it.

> **User decision (2026-04-15, Round 1):** one comprehensive review pass per task; `APPROVE` / `REVISE` / `CONDITIONAL APPROVE` verdict protocol. Reviewer walks the full checklist even on gating failure; CONDITIONAL re-review is narrow (verify gating fix + downstream still holds).

> **User decision (2026-04-15, Round 1):** shared gating lives in `econ-data-analysis/SKILL.md` main body. One source of truth for implementer self-check and reviewer verification.

> **User decision (2026-04-15, Round 1):** dispatch prompts use the "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …" prefix; required fields first, `Additionally:` anchor last.

> **User decision (2026-04-15, Round 2):** **DRY / composability / extensibility** becomes a first-class design principle. One source of truth per concern. Workflow skills own choreography; `agent-orchestration` owns cross-stage orchestration; domain skills own domain discipline; `refactor-and-integrate` owns generic integration discipline.

> **User decision (2026-04-15, Round 2):** **Shared-flow** for every gated checklist. Implementer and reviewer always walk the same file; `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers encode severity.

> **User decision (2026-04-15, Round 2):** delete `implementer-protocol` + `reviewer-protocol` alias skills. `agent-orchestration` §Direct Mode covers the direct-execution rubric in one section (relocated again in Round 3 to `using-superRA` §Execution Modes).

> **User decision (2026-04-15, Round 2):** `integration-workflow` is purely a workflow skill. Data-specific integration checks move to `econ-data-analysis/references/integration.md`.

> **User decision (2026-04-15, Round 3):** `using-superRA` is the master skill every agent reads. It carries the distilled universal principles (restated — the plugin's CLAUDE.md is contributor-only and not visible at runtime), the Workflow / Domain / Utility / Meta inventory, the composable-design map, the skill-load manifest, and the Execution Modes section (subagent dispatch vs direct). `<SUBAGENT-STOP>` is removed. Cross-session detection moves to `references/session-bootstrap.md` loaded by the main agent only.

> **User decision (2026-04-15, Round 3):** the skill-load manifest lives in `using-superRA/SKILL.md` §Skill-Load Manifest. Six role-independent Stages (`implementation`, `refactoring`, `drift-test`, `merge`, `documentation`, `planning-review`) each list required skills + stage-scoped references. `handoff-doc` is in every row. Domain-skill column reads "active domain skill (for data analysis: econ-data-analysis + script-to-notebook)" — no hardcoded vertical. Role-differentiation only where it matters (documentation row); otherwise `subagent_type` encodes role. Fallback rule: unknown Stage → default to `implementation` loads + flag.

> **User decision (2026-04-15, Round 3):** no meta-preamble about "nothing auto-loads" or any explanation of load mechanics. The manifest simply says "for Stage X, load Y." Agents don't need to be taught how loading works.

> **User decision (2026-04-15, Round 3):** `skills: [superRA:using-superRA]` frontmatter on `agents/implementer.md` and `agents/reviewer.md` preloads the master skill for Claude-Code subagent dispatches. Team teammates load it via the SessionStart-injection path. Non-CC harnesses (Copilot, Gemini, Codex) rely on the agent-file step-1 "load `superRA:using-superRA`" fallback.

> **User decision (2026-04-15, Round 3):** split `agent-orchestration/SKILL.md`. Keep high-level orchestration in SKILL.md (Overview, Decision Framework, Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer Feedback, Review Status Reference, Integration). Move TeamCreate mechanics + parallel-dispatch patterns + Known Limitations to `references/agent-teams.md`. Delete Team Recipes (stale, redundant, rigid). Rewrite parallel-dispatch examples to canonical template.

> **User decision (2026-04-15, Round 3):** relocate `## Direct Mode` from `agent-orchestration` to `using-superRA` §Execution Modes.

> **User decision (2026-04-15, Round 3):** retire `auto-load` / `auto-loaded` language plugin-wide.

> **User decision (2026-04-15, Round 3):** delete `handoff-doc` principles #4 (role ownership) and #5 (what-changed deltas) entirely — pointer targets already live in their owning skills.

> **User decision (2026-04-15, Round 3):** add `[STANDARD]` **Document-code consistency** item to `econ-data-analysis/references/integration.md` — if analysis results feed papers, slides, notes, or long-standing downstream artifacts, reconcile inconsistencies or flag unreconciled ones in RESULTS.md Limitations.

> **Deferred to a future round:** PreToolUse hook on `Agent` dispatches that parses `Stage:` and injects the manifest row as a system-reminder into the subagent's prompt. Ship manifest-as-table first; add the hook after one real usage cycle.

---

## Completed (PR #1 — Round 1, Workflow-Domain-Split Restructure)

Tasks 1–6 all APPROVED and pushed through commit `b8c6239`. Seven outcomes: DAV rename, dispatch-prompt protocol standardization, §Review & Self-Check Discipline shared gating, CONDITIONAL APPROVE verdict protocol, `execution-workflow` domain-agnosticism, agent Stage tables + dispatch-prompt contract + §Self-Review walk, companion-workflow light audit. Structural-invariants blocks 10a/10b, 11, 12, 13 landed. See `RELEASE-NOTES.md` Unreleased entry.

## Completed (PR #1 — Round 2, DRY/Composability Refactor)

Tasks 7–12 all APPROVED and pushed through commit `9c3f5c4`. Seven outcomes:

1. **Cross-stage orchestration moved to `agent-orchestration`.** Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer Feedback, Review Status Reference, and Direct Mode became top-level sections. `execution-workflow`, `integration-workflow`, and `handoff-doc` shrank to one-line pointers.
2. **Alias protocol skills deleted.** `skills/implementer-protocol/` and `skills/reviewer-protocol/` removed; `agent-orchestration` §Direct Mode replaced them.
3. **`integration-workflow` genericized.** Stripped of data-specific "what to check" content; new `econ-data-analysis/references/integration.md` carries data-specific integration gates with shared-flow preamble + `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers. `refactor-and-integrate/references/codebase-integration.md` reduced to generic cross-cutting checks.
4. **DRY / composability / extensibility elevated to first-class design principle** in `CLAUDE.md` §Design Principles and `README.md` §Design Principles, with a shared-flow corollary. Stale `two-stage review` / `REVISE (data integrity)` language purged from `README.md`.
5. **Workflow-stage-to-skill Mermaid map** added to `README.md` between §How It Works and §Design Principles.
6. **Structural-invariants extended.** Blocks #14 (agent-orchestration headings), #15 (protocol-skill directories absent), #16 (`integration.md` + `codebase-integration.md` cleanup), #17 (workflow map present), #19 (DRY principle + stale language purged) landed. Block #18 reserved for README 'Why superRA?' lead.
7. **RELEASE-NOTES.md Unreleased entry** rewritten as a coherent Round 1 + Round 2 narrative.

See `RELEASE-NOTES.md` Unreleased entry for the full narrative.

---

## Task 13: Update PLAN.md — condense Round 2; queue Round 3

**Review status:** IMPLEMENTED (orchestrator-owned; no subagent dispatch — pattern mirrors Round 1's Task 7 and Round 2's Task 7)

**Objective:** This file. Collapse Round 2 Tasks 7–12 into a single Completed summary; rewrite Objective for Round 3 (master-skill + manifest); append Round 3 decision entries; queue Tasks 14–18 as new checklist blocks.

**Steps:**

- [x] Collapse Round 2 Tasks 7–12 into `## Completed (PR #1 — Round 2, DRY/Composability Refactor)`.
- [x] Rewrite Objective to describe Round 3 master-skill promotion + manifest.
- [x] Append Round 3 decision entries to `## Decisions`.
- [x] Queue Tasks 14–18 as new checklist blocks (below).
- [x] Atomic commit: `docs(plan): condense Round 2; queue Round 3 master-skill tasks`.

---

## Task 14: Refactor `using-superRA` into the master skill

**Review status:** APPROVED

**Objective:** Restructure `skills/using-superRA/SKILL.md` to be the master skill every agent reads. It carries: distilled universal principles (four workflow principles + RA framing, restated since the plugin's `CLAUDE.md` is contributor-only); skill inventory (Workflow / Domain / Utility / Meta); composable-design map; §Skill-Load Manifest (six role-independent Stages, `handoff-doc` in every row, domain-routing column); §Execution Modes (subagent dispatch + direct mode, lifted from `agent-orchestration` §Direct Mode); §When to Invoke Which Skill (kept from current). Remove `<SUBAGENT-STOP>`. Move cross-session detection / resume-from-PLAN.md logic to new `references/session-bootstrap.md`.

**Files touched:**

- `skills/using-superRA/SKILL.md` — full restructure.
- `skills/using-superRA/references/session-bootstrap.md` — new reference (main-agent only).
- Before any SKILL.md body edits, audit the SessionStart hook that injects `using-superRA` at session start to confirm the injection is content-agnostic (references the skill, doesn't embed a specific slice).

**Steps:**

- [x] **Describe.** Re-read current `using-superRA/SKILL.md`; catalog what moves vs stays vs deletes. Read the SessionStart hook script to confirm injection mechanism. Draft the six-row manifest with `handoff-doc` in every row and role-differentiation on `documentation` row only.
- [x] **Analyze.** Rewrite SKILL.md per Round-3 structure (header + Universal Principles + Skill Inventory + Composable Design + Skill-Load Manifest + Execution Modes + When to Invoke Which Skill). Create `references/session-bootstrap.md` with the lifted detection commands + a lead paragraph ("Main agent loads this at session start; subagents skip — they inherit task context from their dispatch"). Preserve the SessionStart-injection hook contract.
- [x] **Validate.** Invariant block #20: `using-superRA/SKILL.md` contains `## Skill-Load Manifest`, `## Skill Inventory`, `## Execution Modes`; carries exactly 6 `Stage:` rows; `handoff-doc` on every row; `<SUBAGENT-STOP>` absent. `references/session-bootstrap.md` exists with cross-session detection commands.
- [x] Atomic commit: `feat(using-superRA): promote to master skill with skill-load manifest; move session bootstrap to reference`.

---

## Task 15: Preload `using-superRA` in agent files; retire Stage tables and auto-load language

**Review status:** APPROVED

**Depends on:** Task 14 APPROVE.

**Objective:** Guarantee `using-superRA` loads for every subagent dispatch by adding `skills: [superRA:using-superRA]` frontmatter to both agent files. Collapse the 11-row Stage tables in `agents/implementer.md` and `agents/reviewer.md` into one-line pointers at the manifest. Retire `auto-load` / `auto-loaded` language plugin-wide — replace with honest "required" / "load" / "the manifest specifies" phrasing without meta-preamble.

**Files touched:**

- `agents/implementer.md` — added `skills: [superRA:using-superRA]` to frontmatter; replaced Stage table with one-paragraph pointer at the manifest; kept fallback rule; updated §Before You Start step 2 and the "What the dispatch prompt carries" contract paragraph.
- `agents/reviewer.md` — same treatment.
- `skills/agent-orchestration/SKILL.md` — retired `auto-load` in §Dispatch Templates preamble, §Banned in dispatch prompts, and the three remaining Team Recipes "All teammates ..." lines (Team Recipes deletion proper is Task 16).
- `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/script-to-notebook/SKILL.md`, `skills/econ-data-analysis/SKILL.md`, `skills/refactor-and-integrate/SKILL.md` — grep + replaced residual `auto-load` hits with manifest-anchored phrasing.
- `README.md` — retired `auto-load` in two spots (Lean agent definitions paragraph; Stage → references paragraph now cites the manifest).
- `RELEASE-NOTES.md`, `RESULTS.md` — retired `auto-load` in historical Unreleased-block descriptions (replaced with "load" / "stage-based loads per the manifest").
- `tests/structural-invariants.sh` — retired `auto-load` in block #13 comment.

**Steps:**

- [x] **Describe.** `Grep -r 'auto-load'` plugin-wide; enumerated sites (agent files, 4 workflow skills, 3 utility skills, README, RELEASE-NOTES, RESULTS, tests comment).
- [x] **Analyze.** Added `skills: [superRA:using-superRA]` frontmatter to both agent files. Replaced 11-row Stage tables in both with one-paragraph manifest pointers + fallback rule; updated §Before You Start step 2 and the dispatch-contract paragraph to match. Rewrote every `auto-load` / `auto-loaded` hit outside PLAN.md (PLAN.md hits are meta-references describing the retirement decision and the task spec itself).
- [x] **Validate.** `grep -rn 'auto-load\|auto-loaded'` → hits remain only in PLAN.md as meta-references (user decisions + this task block describing the retirement). Both agent files carry `skills: [superRA:using-superRA]` in frontmatter and a `## Stage → skills and references` section pointing at `superRA:using-superRA` §Skill-Load Manifest (no multi-row table). Invariant block #21 is Task 18's responsibility.
- [x] Atomic commit: `refactor(agents): preload using-superRA; retire Stage tables in favor of the manifest`.

---

## Task 16: Split `agent-orchestration/SKILL.md` — SKILL.md (high-level) + `references/agent-teams.md` (technical)

**Review status:** APPROVED

**Depends on:** Task 14 APPROVE (needs `using-superRA` §Execution Modes in place so Direct Mode pointer has a target).

**Objective:** Keep Overview, Decision Framework, Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer Feedback, Review Status Reference, Integration in `agent-orchestration/SKILL.md`. Move TeamCreate mechanics, task-graph construction, parallel-dispatch patterns, Known Limitations to new `references/agent-teams.md`. Delete Team Recipes entirely (stale — still describes retired 3-teammate Analysis Team; redundant — duplicates manifest info; rigid). Replace with a one-paragraph note derived from the manifest. Delete `## Direct Mode` (moves to `using-superRA` in Task 14; leave one-line pointer). Rewrite parallel-dispatch examples to the canonical `Stage:` / `Task:` / `Additionally:` template.

**Files touched:**

- `skills/agent-orchestration/SKILL.md` — deleted Team Recipes + `## Direct Mode` (replaced with one-line pointer to `superRA:using-superRA` §Execution Modes); rewrote Overview with a derived-from-manifest team-composition paragraph; kept Overview, Decision Framework, Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer Feedback, Review Status Reference, Integration. Parallel-dispatch how-to lifted to the reference; SKILL.md shrank from 548 to 154 lines (~72% reduction).
- `skills/agent-orchestration/references/agent-teams.md` — new reference carrying TeamCreate mechanics, task-graph construction, parallel-dispatch how-to (with canonical `Stage:` / `Task:` / `Additionally:` examples using placeholders), lifecycle + cleanup protocol, constraints, and known limitations. Top-of-file pointers at `superRA:using-superRA` §Skill-Load Manifest and at manifest-driven team composition.

**Steps:**

- [x] **Describe.** Re-read `agent-orchestration/SKILL.md`; mark each sub-section as (a) high-level orchestration vs (b) team mechanics.
- [x] **Analyze.** Lift (b) to `references/agent-teams.md` with pointers: "For skill-loads per stage, see `using-superRA` §Skill-Load Manifest"; "Team composition: spawn one teammate per stage the workflow runs; `subagent_type` encodes role." Delete Team Recipes (one-paragraph replacement in Overview). Delete Direct Mode (one-line pointer to `using-superRA` §Execution Modes at the end of §Review Status Reference). Rewrite parallel-dispatch examples to canonical template (placeholders, not concrete stage names).
- [x] **Validate.** SKILL.md length shrinks from 548 → 154 lines (~72%, ≥30%). `grep '### Team Recipes' skills/agent-orchestration/SKILL.md` → 0 hits. `grep '## Direct Mode' skills/agent-orchestration/SKILL.md` → 0 hits. `TeamCreate` in SKILL.md only appears in pointers (Overview paragraph + Rule-of-thumb paragraph). `references/agent-teams.md` exists with 3 `TeamCreate` mentions in how-to context. Invariant block #22 is Task 18's responsibility.
- [x] Atomic commit: `refactor(agent-orchestration): split SKILL.md into high-level + references/agent-teams.md; drop stale Team Recipes`.

---

## Task 17: Finalize Direct Mode relocation + execution-workflow pointer

**Review status:** APPROVED

**Depends on:** Task 14 APPROVE (§Execution Modes in place); Task 16 APPROVE (old §Direct Mode removed).

**Objective:** Retarget remaining Direct Mode pointers to `superRA:using-superRA` §Execution Modes. (§Execution Modes prose already added to `using-superRA` in Task 14; old `agent-orchestration` §Direct Mode already deleted in Task 16.)

**Files touched:**

- `skills/execution-workflow/SKILL.md` — L161 Per-Task step 1 and L169 "In direct mode:" parenthetical retargeted from `superRA:agent-orchestration` §Direct Mode to `superRA:using-superRA` §Execution Modes. Obsolete HTML comment (`<!-- see the other note. direct mode should not be there. -->`) removed.
- `README.md` — workflow-map CROSS node re-ordered: `using-superRA` moves to first position with expanded bullets (universal principles · skill inventory · skill-load manifest · execution modes (subagent/direct) · session bootstrap); `agent-orchestration` loses the `direct mode` bullet.

**Steps:**

- [x] `Grep` for `Direct Mode` / `§Direct Mode` plugin-wide. Found 3 retargetable sites + 1 preserved self-description in `using-superRA/SKILL.md:74` (§Execution Modes body).
- [x] Retarget every non-`using-superRA` mention. execution-workflow/SKILL.md and README.md updated.
- [x] Invariant block #23 (consolidated in Task 18): `using-superRA/SKILL.md` contains `## Execution Modes` AND `Direct mode`; no other SKILL.md carries a full §Direct Mode section.
- [x] Atomic commit: `refactor: finalize Direct Mode relocation to using-superRA §Execution Modes`.

---

## Task 18: Manual-review fixes + structural invariants + RELEASE-NOTES + push

**Review status:** APPROVED

**Depends on:** Tasks 14–17 APPROVE.

**Objective:** Delete `handoff-doc` principles #4 and #5 (and update downstream "six principles" mentions to "four"). Add `[STANDARD]` **Document-code consistency** item to `econ-data-analysis/references/integration.md` and restore the shared-flow preamble keyphrase that invariant #16 guards. Consolidate invariant blocks: update the stale #13 (agent-file Stage tables retired) and #14 (Direct Mode dropped from agent-orchestration); add new blocks #20 (using-superRA master skill shape), #21 (frontmatter preload + retired Stage tables + `auto-load` token absent), #22 (agent-orchestration split), #23 (Direct Mode canonicalized in `using-superRA`), #24 (handoff-doc principles pruned to four), #25 (integration.md carries Document-code consistency). Extend RELEASE-NOTES.md Unreleased entry with Round 3 narrative. Push to PR #1.

**Files touched:**

- `skills/handoff-doc/SKILL.md` — deleted principles #4 and #5; renumbered (old #6 → new #4); section heading "The Six Principles" → "The Four Principles".
- `skills/CATEGORIES.md`, `README.md`, `skills/planning-workflow/references/results-template.md`, `skills/using-superRA/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md` — downstream "six principles" → "four principles"; README principle-list parenthetical pruned to four items.
- `skills/econ-data-analysis/references/integration.md` — new `[STANDARD]` Document-code consistency item; restored the shared-flow preamble phrase "single source of truth for data-analysis integration discipline" (commit 3b25912 had shortened it and dropped the invariant-#16 keyphrase).
- `tests/structural-invariants.sh` — rewrote block #13 (Stage-table retirement pointer + dispatch-contract preserved); rewrote block #14 (four orchestration sections, Direct Mode dropped); added blocks #20–#25.
- `RELEASE-NOTES.md` — extended Unreleased entry with Round 3 paragraphs (master-skill promotion, frontmatter preload + Stage-table retirement, agent-orchestration split, small semantic fixes, structural-invariants additions/updates); header title extended to cover Round 3.

**Steps:**

- [x] Delete handoff-doc #4 + #5; renumber; update downstream "six principles" mentions.
- [x] Add Document-code consistency item to integration.md; restore shared-flow preamble phrase.
- [x] Consolidate invariants (update #13, #14; add #20–#25).
- [x] Update RELEASE-NOTES with Round 3 narrative.
- [x] `bash tests/structural-invariants.sh` → all PASS, 2 known WARN, 0 FAIL.
- [ ] Atomic commit: `test+docs: finalize invariants and release notes for Round 3 master-skill refactor`.
- [ ] Push `refactor/workflow-domain-split` to origin; PR #1 updates.

---

## Retroactive Integration Review (post-Task-18)

**Review status:** IMPLEMENTED

**Scope:** All commits 917e5f5..35f02c1 (PR #1 — Rounds 1 + 2 + 3 combined). Stage 2 of `integration-workflow` (codebase-integration review). Applied `refactor-and-integrate/references/codebase-integration.md` §Code Integration, §Handling Inconsistencies, §PR Quality, §Documentation Currency (broadened generically per the 2026-04-15 user decision). Cross-checked stale "where X lives" / "what N things exist" claims against the four design principles.

`bash tests/structural-invariants.sh` is green (27 PASS, 2 known WARN, 0 FAIL). The structural invariants encode Round-3-specific shape assertions but do not catch downstream prose drift in `CLAUDE.md`, `skills/CATEGORIES.md`, or skill-frontmatter `description:` strings — which is where most of the residual drift lives.

> **Review notes:**
> 1. [MAJOR] `skills/handoff-doc/SKILL.md:3` — frontmatter `description:` still reads "Defines the **six** discipline principles". Task 18 changed the SKILL.md body heading "The Six Principles" → "The Four Principles" and pruned principles #4 and #5, but missed the description that loaders surface to agents. Other skills' descriptions are the trigger surface; this one mis-advertises the skill's own contents. Fix: change "six discipline principles" → "four discipline principles".
>    → implemented: `skills/handoff-doc/SKILL.md:3` — frontmatter `description:` now reads "four discipline principles".
> 2. [MAJOR] `CLAUDE.md:46` (Architectural pattern bullet) — claims "Stage tables in `agents/implementer.md` and `agents/reviewer.md` are the authoritative map from `Stage:` value to references loaded." Task 15 retired those Stage tables in favor of the Skill-Load Manifest in `using-superRA`. The contributor guide now mis-locates the authoritative map. Fix: rewrite to "The Skill-Load Manifest in `superRA:using-superRA` is the authoritative map from `Stage:` value to required skills + stage-scoped references; `agents/implementer.md` / `agents/reviewer.md` carry one-line pointers at it." (Mirrors README.md L190 wording.)
>    → implemented: `CLAUDE.md:46` — Architectural-pattern bullet rewritten to name the Skill-Load Manifest in `superRA:using-superRA` as authoritative; agent files carry one-line pointers (mirrors README.md L190).
> 3. [MAJOR] `CLAUDE.md:56` (DRY ownership map for `agent-orchestration`) — lists "team recipes, and the direct-mode rubric" as concerns owned by `agent-orchestration`. Round 3 deleted Team Recipes outright (Task 16) and relocated Direct Mode to `using-superRA` §Execution Modes (Tasks 14 + 17). Fix: drop "team recipes" (or replace with "team mechanics in `references/agent-teams.md`"); drop "and the direct-mode rubric" or retarget to "Execution Modes are owned by `using-superRA`."
>    → implemented: `CLAUDE.md:56` — replaced "team recipes, and the direct-mode rubric" with "team mechanics in `references/agent-teams.md`"; appended sentence "Execution Modes (subagent dispatch vs direct) are owned by `superRA:using-superRA`."
> 4. [MAJOR] `skills/CATEGORIES.md:12` — `execution-workflow` row says "two-stage review loop". Round 1 collapsed two-stage review into one comprehensive pass; Round 2 explicitly purged this language from `README.md` (Round 2 outcome #4); structural invariant block #11 protects only `README.md`. CATEGORIES.md was missed. Fix: "two-stage review loop" → "one-pass review loop (APPROVE / REVISE / CONDITIONAL APPROVE)".
>    → implemented: `skills/CATEGORIES.md:14` — replaced "two-stage review loop" with "one-pass review loop (APPROVE / REVISE / CONDITIONAL APPROVE)".
> 5. [MAJOR] `skills/CATEGORIES.md:15` — `agent-orchestration` row says "Multi-agent dispatch patterns and Agent Teams **recipes**." Round 3 Task 16 deleted Team Recipes. Fix: "Agent Teams recipes" → "Agent Teams mechanics in `references/agent-teams.md`" (or simply drop "recipes" wording).
>    → implemented: `skills/CATEGORIES.md:17` — replaced "Agent Teams recipes" with "Agent Teams mechanics in `references/agent-teams.md`".
> 6. [MAJOR] `skills/CATEGORIES.md:23` — `econ-data-analysis` "Stage-scoped references" enumeration lists only `planning.md` and `integrate-drift-tests.md`. The directory actually carries four references: `planning.md`, `integrate-drift-tests.md`, `integration.md` (added Round 2 Task 9), and `data-robustness-checklist.md`. README.md L151 lists three (drops `integration.md`); CLAUDE.md L73 lists three (drops `integration.md`). The three stale enumerations disagree with each other. Fix: enumerate all four in CATEGORIES.md; align README.md L151 and CLAUDE.md L73 to the same four-reference list (or settle on a single canonical phrasing like "see `references/` for the full list").
>    → implemented: `skills/CATEGORIES.md:25` and `README.md:151` — both now enumerate all four references (`planning.md`, `integrate-drift-tests.md`, `integration.md`, `data-robustness-checklist.md`); `CLAUDE.md:73` already carried all four.
> 7. [MAJOR] `skills/CATEGORIES.md:53` — `using-superRA` row reads "Session startup, cross-session detection, skill discovery rules, and the high-level workflow principles the orchestrator internalizes." Post-Round-3 it is the master skill: universal principles + skill inventory + composable-design map + Skill-Load Manifest + Execution Modes; cross-session detection moved out to `references/session-bootstrap.md`. The CATEGORIES row describes the pre-Round-3 role. Fix: rewrite to mirror README.md L172 master-skill description (or use the SKILL.md frontmatter description verbatim).
>    → implemented: `skills/CATEGORIES.md:55` — `using-superRA` row rewritten to the master-skill description (universal principles + inventory + composable-design map + Skill-Load Manifest + Execution Modes; cross-session detection in `references/session-bootstrap.md`), mirroring README.md:172.
> 8. [MINOR] `skills/agent-orchestration/references/agent-teams.md:162` — pointer reads "`superRA:using-superRA` §references/session-bootstrap.md" — mixes the section-symbol convention (`§`) with a file path. Use either "`superRA:using-superRA` `references/session-bootstrap.md`" or drop `§`. Cosmetic but the convention elsewhere is `§<heading>` for headings, plain backticks for files.
>    → implemented: `skills/agent-orchestration/references/agent-teams.md:162` — dropped `§`; pointer now reads "`superRA:using-superRA` `references/session-bootstrap.md`".
> 9. [MINOR] `RESULTS.md:11` (Round 1 Task 7 entry) — phrase "teammate pairing now lives in `agent-orchestration` team recipes only" describes a Round-1 endpoint that was overtaken by Round 3 (Team Recipes are deleted). RESULTS.md is the Stage 1 dev log (handoff-doc principle #1: latest-state-only) — this is not a historical record exempt from drift cleanup. Fix: rewrite the parenthetical to point at the manifest or at `references/agent-teams.md`.
>    → implemented: `RESULTS.md:11` — parenthetical rewritten to "teammate pairing is now derived from the Skill-Load Manifest in `superRA:using-superRA`; team mechanics live in `agent-orchestration/references/agent-teams.md`".
> 10. [MINOR] `skills/CATEGORIES.md` overall — does not mention the Composable Design map / Skill-Load Manifest / master-skill concept that `using-superRA` now carries, even though `CATEGORIES.md` is named in `CLAUDE.md` as "the authoritative grouping index." A short pointer line referencing `using-superRA` §Skill Inventory + §Skill-Load Manifest as the more granular map would resolve the contradiction.
>     → implemented: `skills/CATEGORIES.md:5` — added pointer paragraph directing runtime-facing readers to `superRA:using-superRA` §Skill Inventory + §Skill-Load Manifest; clarifies that CATEGORIES is the contributor grouping index and `using-superRA` is the agent-facing authority.

> **Review notes (Round-1/2-focused pass, post-first-pass):**
>
> Second retroactive integration-review pass; first pass was Round-3-anchored and the brief for this pass was to surface Round-1 and Round-2 drift the first reviewer may have underweighted. Items 1–6 are Round-1 scope (two-stage-review retirement / CONDITIONAL APPROVE exposure / pre-Round-1 verdict labels). Items 7–8 are Round-3 scope inside Round-2-genericized files (`integration-workflow/SKILL.md`, `RELEASE-NOTES.md` Unreleased block) that landed outside the first reviewer's CLAUDE.md/CATEGORIES.md/README.md focus. Disjoint from the first pass's file:line sites — do not double-adjudicate.
>
> 1. [MAJOR] `agents/reviewer.md:182` — the `Doc edits` example inside the Report Format block reads `"PLAN.md — Task 3: set Review status: REVISE (implementation), wrote blockquote with 2 MAJOR + 1 MINOR items."` The `REVISE (implementation)` label is the pre-Round-1 two-stage-review verdict. Round 1 collapsed `REVISE (data integrity)` + `REVISE (implementation)` into a single `REVISE`; the §Verdict block above (L100, L114) already uses unified `REVISE` / `CONDITIONAL APPROVE`. This sample-text line is the authoritative "how to write a status report" template for every dispatched reviewer — drift here ships to every review round. Fix: rewrite the example to `"PLAN.md — Task 3: set Review status: REVISE, wrote blockquote with 2 MAJOR + 1 MINOR items."`
>    → implemented: `agents/reviewer.md:182` — Doc edits sample-text rewritten to use unified `REVISE` (dropped `(implementation)` parenthetical).
> 2. [MAJOR] `agents/reviewer.md:190` — the end-of-report boilerplate reads `ACTION REQUIRED (REVISE only): Fix the above issues, then re-dispatch this reviewer. Iterate until APPROVE.` The Round-1 three-verdict protocol adds `CONDITIONAL APPROVE`, which also requires re-dispatch (narrow re-review). The `(REVISE only)` parenthetical misses that branch and contradicts §Verdict L102–104 and the Assessment line L178 that explicitly names `CONDITIONAL APPROVE`. Fix: `ACTION REQUIRED (REVISE or CONDITIONAL APPROVE): Fix the above issues, then re-dispatch this reviewer. Iterate until APPROVE.`
>    → implemented: `agents/reviewer.md:190` — parenthetical changed to `(REVISE or CONDITIONAL APPROVE)`.
> 3. [MAJOR] `skills/handoff-doc/SKILL.md:48` — At-a-Glance-Structure example shows `**Review status:** REVISE (implementation)` inside a Task 2 illustration. Same Round-1-retired label as item 1. This is the canonical PLAN.md anatomy example loaded by every agent at dispatch time. Fix: change to `**Review status:** REVISE` (or illustrate `CONDITIONAL APPROVE` to also show the gating verdict).
>    → implemented: `skills/handoff-doc/SKILL.md:48` — At-a-Glance example now shows `**Review status:** REVISE` (dropped `(implementation)`).
> 4. [MAJOR] `skills/report-in-markdown/SKILL.md:33` — "When to use what" table row reads `| `execution-workflow` reviewer (data integrity, implementation correctness) | nothing beyond this file |`. Round 1 retired the "(data integrity, implementation correctness)" two-stage framing plugin-wide and relabeled the single reviewer stage as `implementation review`. Fix: change to `execution-workflow reviewer (implementation review)` or drop the parenthetical.
>    → implemented: `skills/report-in-markdown/SKILL.md:33` — table row now reads `execution-workflow reviewer (implementation review)`.
> 5. [MAJOR] `skills/econ-data-analysis/references/integrate-drift-tests.md:21` — sentence reads "Drift tests are not a substitute for the two-stage review or the describe-analyze-validate discipline." Round 1 collapsed two-stage review into one comprehensive pass (§Review & Self-Check Discipline in the SKILL.md main body). Fix: "Drift tests are not a substitute for the one-pass review or the describe-analyze-validate discipline" (or point at `econ-data-analysis/SKILL.md §Review & Self-Check Discipline`).
>    → implemented: `skills/econ-data-analysis/references/integrate-drift-tests.md:21` — "two-stage review" → "one-pass review".
> 6. [MAJOR] `skills/refactor-and-integrate/references/drift-test-quality.md:79` — Never-bullet reads "**Treat the drift tests as the only safety net.** They protect key results; they do not replace the two-stage review or the data-discipline protocol." Same Round-1 stale phrasing; this is a load-bearing never-rule read by every drift-test implementer and reviewer. Fix: "they do not replace the one-pass review or the data-discipline protocol" (or point at "§Review & Self-Check Discipline").
>    → implemented: `skills/refactor-and-integrate/references/drift-test-quality.md:79` — "two-stage review" → "one-pass review".
> 7. [MAJOR] `skills/integration-workflow/SKILL.md:187,208,459,473` — four sentences pointing the dispatched reviewer/refactorer at "the **Stage-table references** for `integration review` / `refactoring`" (and at L187/L208 specifically "The reviewer's Stage table owns the reference load" / "The implementer's Stage table owns the reference load"). Round 3 Task 15 retired the in-agent Stage tables in favor of the single `superRA:using-superRA` §Skill-Load Manifest; Block #13 of `tests/structural-invariants.sh` now encodes that retirement. integration-workflow still routes readers to a construct that no longer exists. Fix: replace every "Stage-table references" / "Stage table owns the reference load" with "Skill-Load Manifest" / "`superRA:using-superRA` §Skill-Load Manifest specifies the reference load for your Stage." (Four sites; grep `Stage-table\|Stage table` in the file.)
>    → implemented: `skills/integration-workflow/SKILL.md:187,208,459,473` — all four sites retargeted from "Stage-table references" / "Stage table owns the reference load" to `superRA:using-superRA` §Skill-Load Manifest.
> 8. [MINOR] `RELEASE-NOTES.md:172` — current-skill-description line for `execution-workflow` reads "Per-task dispatch with **two-stage review**, orchestrator-discipline filter …". This lives inside a frozen earlier release block describing the original skill-split refactor — the Unreleased entry at the top of the file already credits Round 1's workflow-domain-split (one-pass review). Keeping the two-stage phrasing here is arguably defensible as a historical snapshot, but the same block is the canonical "what execution-workflow does" description that downstream readers cite, and it now disagrees with the skill. Fix (light touch): replace "two-stage review" with "per-task review" or "one-pass review" so the description remains true against the current skill without rewriting the release narrative. Leave `RELEASE-NOTES.md:185` (the `requesting-analysis-review` deletion rationale) alone — that is historical rationale for a retired skill and rewriting it obscures why the deletion made sense at the time.
>    → implemented: `RELEASE-NOTES.md:172` — "two-stage review" → "one-pass review" in the `execution-workflow` current-skill-description line. Chose the fix (not "leave as historical") because the sentence is the canonical current-state description cited downstream, not pre-Round-1 history. L185 left untouched per reviewer guidance.
