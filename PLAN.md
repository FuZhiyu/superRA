# Theory-Modeling Vertical — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all `PLAN.md` / `RESULTS.md` editing. This plan edits superRA skills, workflow docs, hooks, and tests — not empirical data — so the usual `superRA:econ-data-analysis` step discipline does not apply. The per-step cycle here is **plan → edit → verify (read / grep / targeted checks) → commit**.

**Objective:** Add a first-class `superRA:theory-modeling` domain vertical for mathematical-modeling work, with strict derivation discipline, notation and assumption controls, simple numerical verification, and renderable markdown/LaTeX output.

**Methodology:** Implement the new domain skill and stage-scoped references, wire it into the superRA skill manifest and planning/integration workflow surfaces, generalize data-only wording that blocks a second vertical, expose the skill for repo-local discovery, and verify the resulting structure with harness checks plus targeted smoke coverage.

**Implementation Inventory:**

### New files
| Artifact | Purpose |
|---|---|
| `skills/theory-modeling/SKILL.md` | Main domain skill body with trigger description, stage-scoped load map, and shared `Define–Derive–Validate` checklist |
| `skills/theory-modeling/references/planning.md` | Planning hard gate: `Model Inventory / Assumption Map` plus verification plan |
| `skills/theory-modeling/references/integrate-drift-tests.md` | Modeling-specific Phase A guidance for symbolic and numerical drift tests |
| `skills/theory-modeling/references/integration.md` | Modeling-specific integration checklist |

### Wiring surfaces
| File | Why it changes |
|---|---|
| `skills/using-superRA/SKILL.md` | Add the new domain skill to Skill Inventory and the manifest add-on table |
| `skills/planning-workflow/SKILL.md` | Route theory/modeling work to the new planning reference and generalize second-vertical wording |
| `skills/refactor-and-integrate/SKILL.md` | Point integration-stage loading at the modeling-specific integration reference |
| `skills/handoff-doc/references/plan-anatomy.md` | Generalize data-only plan template wording so a second vertical is first-class |
| `hooks/exit-plan-mode` | Remind the orchestrator about the new planning hard gate |
| `README.md`, `skills/CATEGORIES.md`, `CLAUDE.md` | Document the vertical as implemented, not roadmap-only |
| `.agents/skills/theory-modeling` | Repo-local discovery symlink |
| `tests/check-harness-compatibility.sh` | Assert the new skill is exposed and wired |

**Output:** A working `theory-modeling` vertical that auto-loads through superRA’s existing workflow, plus updated contributor/runtime docs and passing structural compatibility checks.

**Expected Results / Hypotheses:** After implementation, a modeling prompt should route through `planning-workflow` to a `Model Inventory / Assumption Map` gate before task drafting; implementer/reviewer pairs should be able to use the shared checklist to catch skipped algebra, lazy notation, hidden or uninterpretable assumptions, and broken rendering; integration should have domain-specific drift-test and refactor guidance without adding a new workflow skill.

**Pipeline:** N/A — this is plugin-engineering work, not a multi-script empirical analysis.

**Sensitivity Analysis:** N/A for this task shape. The analogue is targeted verification: wiring checks, discovery exposure, and one smoke path for planning/routing semantics.

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on the direction and the initial scope for v1
- [x] **Execution complete** — all tasks `APPROVED`, verification checks pass
- [ ] **Drift tests created** — integration-phase protection added and passing on baseline
- [ ] **Refactored** — integration reviewer `APPROVED`
- [ ] **Docs finalized** — `RESULTS.md` matured, project docs audited, doc-reviewer `APPROVED`
- [ ] **Merged** — branch merged to main or PR opened

## Decisions

> **User decision (2026-04-22):** Use the skill name `theory-modeling`.
> **Question asked:** Which naming direction should the new vertical use?
> **Rationale:** Aligns with the repo roadmap wording while still allowing the v1 body to focus on mathematical modeling.

> **User decision (2026-04-22):** V1 includes derivation discipline **plus simple numerical verification**.
> **Question asked:** What should the first wired-in version cover?
> **Rationale:** Core derivation discipline is the priority, but numerical/special-case checks are part of the trust model for this vertical.

> **User decision (2026-04-22):** Ban lazy placeholder notation, but allow genuinely conventional notation when its meaning is explicit and intuitive.
> **Question asked:** How strict should the notation rule be in v1?
> **Rationale:** The vertical should reject arbitrary `A/B/C/D` or `T1/T2` labels while still permitting field-standard notation such as `r` for an interest rate.

## Project Conventions

Walked at planning time (2026-04-22). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at `7d8f123`): Contributor-facing authority for superRA changes. New verticals must be added as domain skills, not workflow forks; shared checklists are load-bearing; `skill-creator` discipline applies when editing `skills/*/SKILL.md`; README, categories, and manifest surfaces must stay in sync; Codex discovery uses `.agents/skills/` symlinks and generated `.codex/agents/` files remain derived artifacts.
- `/AGENTS.md`: symlink to `/CLAUDE.md`; same contributor guidance for AGENTS-aware harnesses.
- `/README.md` (HEAD at `7d8f123`): User-facing overview of the plan/implement/integrate workflow, current domain skills, utility skills, installation, and hooks. Domain skill additions need matching README updates, especially the Domain Skills table and roadmap wording.

### Not walked (not needed for this plan)
- `docs/plans/` beyond targeted reference examples, `tests/claude-code/`, and harness-specific install docs outside the repo root summaries — out of scope unless verification shows a drift.

---

### Task 1: Create the `theory-modeling` domain skill and its stage-scoped references
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(set during integration — not filled at planning time)*

**Script:** `skills/theory-modeling/SKILL.md`, `skills/theory-modeling/references/*.md`
**Input:** Existing domain-skill pattern in `skills/econ-data-analysis/` plus the approved v1 requirements in this plan’s Decisions section
**Output:** New `theory-modeling` skill directory with a main checklist and the planning / drift-test / integration references

- [x] Draft `SKILL.md` with trigger language, stage-scoped references, a short iron-law equivalent, and a shared `Define–Derive–Validate` checklist using `[BLOCKING]` / `[ADVISORY]`.
- [x] Draft `references/planning.md` with the `Model Inventory / Assumption Map` hard gate and the result-verification planning rules.
- [x] Draft `references/integrate-drift-tests.md` and `references/integration.md` so integration has modeling-specific guardrails for symbolic identities, comparative statics, and simple numerical checks.
- [x] Sanity-read the new vertical for internal consistency, then update `RESULTS.md` Task 1 with the new checklist and any open caveats.

### Task 2: Wire the new vertical into runtime surfaces, docs, and discovery
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(set during integration — not filled at planning time)*

**Script:** Existing workflow/docs/hook/test files named in the Implementation Inventory, plus `.agents/skills/theory-modeling`
**Input:** The approved skill name, the new file layout from Task 1, and the current runtime/docs wording in the repo
**Output:** Updated manifest/routing/docs/hook/test surfaces that expose `theory-modeling` as an implemented vertical and remove the remaining single-vertical assumptions that would block it

- [x] Update `skills/using-superRA/SKILL.md`, `skills/planning-workflow/SKILL.md`, and `skills/refactor-and-integrate/SKILL.md` so the new vertical loads at planning, drift-test, and integration time.
- [x] Generalize `skills/handoff-doc/references/plan-anatomy.md` and `hooks/exit-plan-mode` so planning guidance and reminders support both data-analysis and theory-modeling hard gates.
- [x] Update `README.md`, `skills/CATEGORIES.md`, and `CLAUDE.md` so the vertical is documented as implemented rather than roadmap-only.
- [x] Add `.agents/skills/theory-modeling` and extend `tests/check-harness-compatibility.sh` with the new discovery/wiring assertions.

### Task 3: Verify the new vertical end to end and reconcile any drift
**Depends on:** Task 1, Task 2
**Review status:** APPROVED
**Integration status:** *(set during integration — not filled at planning time)*

**Script:** Verification commands and any touched files needed to resolve resulting failures
**Input:** Completed outputs from Tasks 1 and 2
**Output:** Passing targeted checks, updated handoff docs, and a final repo state ready for integration

- [x] Run `tests/check-harness-compatibility.sh` and fix any failures surfaced by the first verification round.
- [x] Run a targeted smoke check on the new routing and repo-local discovery surfaces.
- [x] If any agent or doc examples were touched, run the matching generated-artifact check and reconcile drift.
- [x] Generalize the Tier 3 / Never-list wording in `skills/refactor-and-integrate/references/merge-quality.md` so theory/modeling is first-class in the blocking checklist text.
- [x] Tighten the merge-quality assertion in `tests/check-harness-compatibility.sh` so it verifies the generalized wording or explicitly fails on the old data-only phrases.
- [x] Re-run the structural verification checks, then replace `RESULTS.md` Task 3 with the final verification outcome, remaining risks, and the exact checks that passed.
