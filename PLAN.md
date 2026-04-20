# PLAN: Simplify superRA Skills

## Objective

Reduce verbosity and token cost of superRA skills while preserving load-bearing discipline (the four workflow principles, Iron Law, tuned Red Flags / rationalization tables, severity markers). Align every skill with the §Skill Design Patterns in `CLAUDE.md` and the progressive-disclosure / concise-description guidance in `skill-creator`.

Target: ~10–15% body-text reduction across the 11 skills; tighter YAML `description:` fields; elimination of cross-skill duplication for the Reviewer Verdict Protocol and drift-test tolerances.

## Guardrails (do NOT touch)

- Iron Law and Common Rationalizations table (`econ-data-analysis`).
- §Three Concurrent Disciplines with `[BLOCKING]` / `[ADVISORY]` markers.
- Red Flags tables anywhere they appear.
- Four workflow principles where they are the load-bearing choreography of a skill.
- RA-framing language, severity protocols, stop-point definitions.
- Skill-Load Manifest structure in `using-superRA` (authoritative mapping).

## Cross-cutting rules applied in every task

1. **Descriptions**: trigger + what-it-does, no design reasoning, no restatement of body sections.
2. **Body**: drop "why it is structured this way" / "domain-agnostic" / "future verticals" asides and "does not duplicate X" defensive lines. Rationale belongs in commit messages and `CLAUDE.md`.
3. **Duplication**: one source of truth per concern; replace restated content with one-line pointers.
4. **Negative → positive instructions only when the positive form is equally clear.** Keep prohibitions where the "don't" / "never" is the point (Iron Law, banned-dispatch patterns, Agent-tool isolation ban, etc.). Convert only (a) conditional decision trees phrased as "No X? → …" branches, and (b) defensive "does not duplicate" / "no hard-coding" asides that can be dropped entirely. The recon flagged only one true candidate: `execution-workflow` L22–34 Execution Modes.
5. **Role-targeted content** moves from top-level SKILL.md into stage-scoped references when only one role needs it.

---

## Task 1 — `planning-workflow/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- L12–13: delete domain-agnostic + future-verticals disclaimer (design reasoning).
- L14–16: collapse two-paragraph "assume reader has zero context" to one sentence.
- L49–52: demote notebook-format reference to a parenthetical or move to stage-scoped reference.
- L56–57: drop "This is a reproducibility requirement" (MUST already carries it).
- L76–102: compress Task Dependencies prose to a 3-bullet test (reads outputs / needs methodology from / runs sensitivity on).

---

## Task 2 — `execution-workflow/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- L10–13: delete "Core principle:" restatement already in YAML description.
- L22–34: rewrite Execution Modes as a positive 3-step decision list (load plan → subagent mode if available and not overridden → otherwise direct).
- L36–53: consolidate outer loop + "Per-task inner loop" into one numbered flow; remove redundant header.
- L58–89: keep the Step 0 / 0b checks, drop scenario narratives ("they exited CLI plan-mode and jumped straight…").
- L93–107: replace re-explanation of `## Project Conventions` with a one-line pointer to `handoff-doc/references/plan-anatomy.md`.
- L205–208: delete Model Selection section (generic and delegated to domain skill).

---

## Task 3 — `integration-workflow/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- L10–12: delete Core Principle restatement duplicating description.
- L33–41: replace autonomy-contract paragraph with one-line pointer to `using-superRA §Universal Principles`; keep only integration-specific stop points.
- L43–48: collapse Dispatch Convention + checklist-discipline pointers to a single line referencing `agent-orchestration §Dispatch Templates` and `using-superRA §Skill-Load Manifest`.
- L149–151: tighten Phase C purpose to one sentence; drop "format discipline lives in report-in-markdown, this phase orchestrates" meta-line.
- L341–355: keep Red Flag bullets (tuned); cut trailing ownership paragraph (already in `CLAUDE.md §DRY`).

---

## Task 4 — `agent-orchestration/SKILL.md` (+ references)

**Status**: NOT STARTED

**Cuts / tightens**:
- L6–14: drop "phases are a cycle" design-reasoning aside; delete the "See §Workload Balancing" preamble.
- L59–69: replace Difficulty and Agent Type with a one-line pointer to `using-superRA §Code-Change Defaults #2`.
- L83–120: remove Parallelization and Worktree Isolation section — duplicates `references/agent-teams.md` (archived) and `references/worktree-harness-fallback.md`. Replace with a short pointer noting Teams-mode is deprecated.
- L174–177: fold "Banned in dispatch prompts" into the same bullet list as "Optional steering is strictly additive" (currently reads as two rules for one principle).

---

## Task 5 — `using-superRA/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- Description: trim to "Master skill for superRA agents. Carries workflow principles, skill inventory, and the Stage → skill Load Manifest."
- L8–19: replace intro paragraph with one sentence: "Loaded by all agents at dispatch time."
- L29–31: drop "The context window is a public good" motivational opener.
- L65–67: §Composable Design duplicates `CLAUDE.md §Architectural pattern` — replace with a one-line pointer.
- L86–89: rewrite Main-agent default loads as an imperative ("Main agents additionally load …") with no conditional preamble.

---

## Task 6 — `handoff-doc/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- L6–8: separate skill-ownership pointer from the load-bearing four principles; trim ownership block.
- L13: drop "This skill does not duplicate that" defensive sentence.
- L27: drop "PLAN.md is the primary task tracker, not TodoWrite" commentary (the surrounding rule already carries it).
- L48–52: split Project Conventions and Figure Embedding into two one-line pointers, or cut if fully covered by `plan-anatomy.md` / `results-anatomy.md`.
- L53–59: delete "How This Skill Is Used" meta-section.

---

## Task 7 — `econ-data-analysis/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- Description (L25–26): compress to "Domain skill for rigorous economic data work; body carries §Three Concurrent Disciplines, §Pitfalls, §Common Rationalizations."
- L39–40: drop "implementer additionally loads … by the manifest" (loading is `using-superRA`'s concern).
- L59–60: drop "Violating the letter is violating the spirit" rationale line.
- L85–86: compress "shortest of the three disciplines" intro to one sentence.
- L99–112: remove motivational preamble before the `[ADVISORY]` visualization bullets.

**Guardrail**: Iron Law text, §Three Concurrent Disciplines gated checklist, Common Rationalizations table, Pitfalls catalog — all untouched.

---

## Task 8 — `refactor-and-integrate/SKILL.md` (+ references)

**Status**: NOT STARTED

**Cuts / tightens**:
- L14: drop "utility skill not workflow skill" positioning line.
- L15–16: drop DRY rationale; replace with one sentence: "Load per stage; implementer self-checks, reviewer verifies the same content."
- L18–21: move or delete "Used by:" metadata (belongs in `CATEGORIES.md`).
- L23–44: collapse three-discipline intros to one line each: "Stage `X` → load `references/<file>.md`."
- L57–68 + L72–82: delete in-body §Reviewer Verdict Protocol and §Implementer Self-Check — both already live in full detail in `references/codebase-integration.md`. Replace with pointers.

---

## Task 9 — Cross-skill dedup: Reviewer Verdict Protocol

**Status**: NOT STARTED

The two-verdict (APPROVE / REVISE), one-pass, dependent-findings protocol is currently stated in **three** places:
- `refactor-and-integrate/SKILL.md` §Reviewer Verdict Protocol
- `refactor-and-integrate/references/codebase-integration.md` L38–72
- `econ-data-analysis/references/integration.md` L33–42

**Action**: keep the full protocol only in `refactor-and-integrate/references/codebase-integration.md`. Replace the other two with a one-line pointer: "Verdict protocol: `refactor-and-integrate/references/codebase-integration.md §Reviewer Verdict Protocol`."

Savings: ~25 lines.

---

## Task 10 — Cross-skill dedup: Drift-test tolerances

**Status**: NOT STARTED

`econ-data-analysis/references/integrate-drift-tests.md` L44–56 re-summarizes tolerance rubric already fully specified in `refactor-and-integrate/references/drift-test-quality.md` L13–36.

**Action**: in `integrate-drift-tests.md`, keep only the at-a-glance table (if any) and a pointer to `drift-test-quality.md` for the full rubric. Delete the narrative re-summary.

Savings: ~20 lines.

---

## Task 11 — `semantic-merge/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- L10–12: drop parallel-worktree ex-ante rationale.
- L99–108: delete "Working Principles" section (restates `CLAUDE.md §Workflow principles`).
- L109–119: delete "When to Ask the User" — duplicates §Step 4 L67–80.

---

## Task 12 — `report-in-markdown/` (SKILL.md + references)

**Status**: NOT STARTED

**Cuts / tightens**:
- SKILL.md L9–10: drop "rules live in references so callers only pay for what they need" meta-line.
- `references/baseline-io.md` L15–16: drop "superRA skills should never hard-code …" design principle.
- `references/final-form.md` L3–5: drop Stage 1 vs Stage 2 design-philosophy paragraph; keep checklist + four-commit structure.
- `references/final-form.md` L123–131: remove Phase-B regression commentary (belongs in `integration-workflow`).

---

## Task 14 — Cut meta-integration sections across all skills

**Status**: NOT STARTED

Sections like `§Used by:`, `§How This Skill Is Used`, `§Composable Design`, `§Integration` (where they describe *which other skills load this one* rather than execution steps) are contributor-facing meta. Agents already learn loading from `using-superRA §Skill-Load Manifest` and ordering from the dispatching workflow skill.

**Action**: in each SKILL.md, delete sections whose content is purely "this skill is loaded by X / sits next to Y / composes with Z." Keep inline pointers where they are part of an execution step (e.g., "at Phase C, dispatch via `report-in-markdown`"). When in doubt, ask: does an agent executing a step need this sentence? If no, cut.

This task is applied in-flight by each per-skill implementer (Tasks 1–8, 11–13).

---

## Task 13 — `worktree-data-sync/SKILL.md`

**Status**: NOT STARTED

**Cuts / tightens**:
- L7–9: collapse lifecycle/out-of-scope repetition into one "See also" line.
- L24: remove "Announce at start: 'I'm using the worktree-data-sync skill …'" ceremony.
- L37–42: compress CLI entrypoint explanation to a single invocation line plus the example block.

---

## Tasks 15–20 — DRY recon follow-ups (NEW, discovered during this round)

From the background DRY recon. Not applied in this round — record for a follow-up pass.

- **Task 15** — Verdict protocol is also duplicated *in the body* of `econ-data-analysis/SKILL.md` L70–81. After this round, the `refactor-and-integrate/SKILL.md` body copy is gone (Task 9). The `econ-data-analysis/SKILL.md` body copy remains and should be cut to a pointer to `refactor-and-integrate/references/codebase-integration.md §Reviewer Verdict Protocol`. ~12 lines.
- **Task 16** — Three-pause-classes re-described in `execution-workflow/SKILL.md` §Autonomy and Stop Points L224–232 and `integration-workflow/SKILL.md` §Autonomy L33–41. `using-superRA/references/main-agent.md` is authoritative. Replace class descriptions in both workflow skills with pointers; keep only phase-specific stop-point lists. ~15 lines.
- **Task 17** — `integration-workflow/SKILL.md` Phase B Step 1 worked dispatch L89–116 restates the canonical shape preamble from `agent-orchestration §Dispatch Templates`. Keep the `Additionally:` content (example-specific), drop the re-stated shape rules. ~8 lines.
- **Task 18** — Four document principles + inline-edit rule restated in `planning-workflow/SKILL.md §Living Plan and Results Docs` L119–140. `handoff-doc` owns. Replace with a pointer + the material/not-material distinction list which is genuinely planning-workflow-owned. ~15 lines.
- **Task 19** — Semantic-merge escalation rules (research-meaningful conflicts, PLAN.md restructure) stated in both `semantic-merge/SKILL.md` L60–74 and `refactor-and-integrate/references/merge-quality.md` L33–60. Keep the checklist in `merge-quality.md`; `semantic-merge` points. ~20 lines.
- **Task 20** — Project doc walk-up algorithm restated in `planning-workflow/SKILL.md` L52–54 and `execution-workflow/SKILL.md` L99. `refactor-and-integrate/references/codebase-integration.md §Project Doc Audit` owns the algorithm; workflow skills keep only phase-specific context. ~12 lines.

Total additional savings if applied: ~80 lines.

---

## Execution Notes

- Each task is independent except Tasks 9 and 10 (cross-skill dedups) which modify files also touched by Tasks 7, 8. Run 9 and 10 *after* 7 and 8, or coordinate in the same commit per file.
- One commit per task (per `CLAUDE.md §Working in This Repo` — one problem per commit). Commit message should state the problem (bloat / duplication / design reasoning in body), not just the diff.
- After each task, spot-check the edited skill in a real session — verify trigger behavior is unchanged (descriptions still fire) and no load-bearing discipline was cut.
- Measure before/after line counts per SKILL.md; expected total body reduction ~200–300 lines across the 11 skills.

## Project Conventions

- Skill edits are behavior-shaping; test on Claude Code before claiming done.
- YAML `description:` is the trigger — changes here need a real-session check that the skill still activates on intended prompts.
- Prefer editing in place over rewriting files wholesale (preserves git blame for tuned content).
