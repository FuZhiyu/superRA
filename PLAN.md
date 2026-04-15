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
- [ ] Atomic commit: `docs(plan): condense Round 2; queue Round 3 master-skill tasks`.

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

**Review status:** IMPLEMENTED

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

**Review status:** not started

**Depends on:** Task 14 APPROVE (needs `using-superRA` §Execution Modes in place so Direct Mode pointer has a target).

**Objective:** Keep Overview, Decision Framework, Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer Feedback, Review Status Reference, Integration in `agent-orchestration/SKILL.md`. Move TeamCreate mechanics, task-graph construction, parallel-dispatch patterns, Known Limitations to new `references/agent-teams.md`. Delete Team Recipes entirely (stale — still describes retired 3-teammate Analysis Team; redundant — duplicates manifest info; rigid). Replace with a one-paragraph note derived from the manifest. Delete `## Direct Mode` (moves to `using-superRA` in Task 14; leave one-line pointer). Rewrite parallel-dispatch examples to the canonical `Stage:` / `Task:` / `Additionally:` template.

**Files touched:**

- `skills/agent-orchestration/SKILL.md` — delete Team Recipes + Direct Mode; rewrite parallel-dispatch examples; keep high-level orchestration content.
- `skills/agent-orchestration/references/agent-teams.md` — new reference.

**Steps:**

- [ ] **Describe.** Re-read `agent-orchestration/SKILL.md`; mark each sub-section as (a) high-level orchestration vs (b) team mechanics.
- [ ] **Analyze.** Lift (b) to `references/agent-teams.md` with pointers: "For skill-loads per stage, see `using-superRA` §Skill-Load Manifest"; "Team composition: spawn one teammate per stage the workflow runs; `subagent_type` encodes role." Delete Team Recipes (one-paragraph replacement). Delete Direct Mode (one-line pointer to `using-superRA` §Execution Modes). Rewrite parallel-dispatch examples to canonical template.
- [ ] **Validate.** SKILL.md length shrinks ≥30%. `grep` for `### Team Recipes` in SKILL.md → 0 hits. `TeamCreate` in SKILL.md only appears in pointers. Invariant block #22: `references/agent-teams.md` exists with `TeamCreate` content.
- [ ] Atomic commit: `refactor(agent-orchestration): split SKILL.md into high-level + references/agent-teams.md; drop stale Team Recipes`.

---

## Task 17: Finalize Direct Mode relocation + execution-workflow pointer

**Review status:** not started

**Depends on:** Task 14 APPROVE (§Execution Modes in place); Task 16 APPROVE (old §Direct Mode removed).

**Objective:** Verify `using-superRA` §Execution Modes carries the full Direct Mode prose (read agent file for role, load per manifest, no dispatch-prompt contract, self-review gate applies, review never skipped). Retarget every remaining Direct Mode pointer to `superRA:using-superRA` §Execution Modes.

**Files touched:**

- `skills/using-superRA/SKILL.md` — verify §Execution Modes is complete (touched in Task 14).
- `skills/agent-orchestration/SKILL.md` — one-line pointer at `superRA:using-superRA` §Execution Modes.
- `skills/execution-workflow/SKILL.md` L170 — retarget direct-mode parenthetical.
- Any other skill mentioning Direct Mode → retarget.

**Steps:**

- [ ] `Grep` for `Direct Mode` / `§Direct Mode` plugin-wide.
- [ ] Retarget every non-`using-superRA` mention to a pointer.
- [ ] Invariant block #23: `using-superRA/SKILL.md` contains `## Execution Modes` AND `Direct mode`; no other SKILL.md carries a full §Direct Mode section.
- [ ] Atomic commit: `refactor: finalize Direct Mode relocation to using-superRA §Execution Modes`.

---

## Task 18: Manual-review fixes + structural invariants + RELEASE-NOTES + push

**Review status:** not started

**Depends on:** Tasks 14–17 APPROVE.

**Objective:** Delete `handoff-doc` principles #4 and #5. Add `[STANDARD]` **Document-code consistency** item to `econ-data-analysis/references/integration.md`. Consolidate invariant blocks #20–#23 (renumber tail if needed). Update RELEASE-NOTES.md with Round 3 narrative. Push to PR #1.

**Files touched:**

- `skills/handoff-doc/SKILL.md` — delete principles #4 and #5; renumber remaining.
- `skills/econ-data-analysis/references/integration.md` — new `[STANDARD]` Document-code consistency item.
- `tests/structural-invariants.sh` — consolidate blocks #20–#23; add handoff-doc check (no `4. **Ownership` / `5. **Explicit what-changed` lines); add integration.md check (contains `Document-code consistency`).
- `RELEASE-NOTES.md` — append Round 3 paragraph.

**Steps:**

- [ ] Delete handoff-doc #4 + #5; renumber.
- [ ] Add Document-code consistency item to integration.md (with reconciliation guidance).
- [ ] Consolidate invariants.
- [ ] Update RELEASE-NOTES.
- [ ] `bash tests/structural-invariants.sh` → all PASS, 2 known WARN, 0 FAIL.
- [ ] Atomic commit: `test+docs: finalize invariants and release notes for Round 3 master-skill refactor`.
- [ ] Push `refactor/workflow-domain-split` to origin; PR #1 updates.
