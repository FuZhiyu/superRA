# Codex Agent Dispatch Preference Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all `PLAN.md` / `RESULTS.md` editing. Use `skill-creator` when modifying any `skills/*/SKILL.md`. Keep shared workflow text canonical; put Codex-specific runtime guidance in the Codex adapter reference unless a cross-reference becomes misleading.

**Objective:** Make Codex treat a user-invoked superRA workflow as explicit authorization for the named-agent workflow, with reviewer dispatch still mandatory, warm-agent lifecycle guidance explicit, and a canonical Codex instructions reference guaranteed to load whenever `using-superRA` loads.

**Methodology:** Update the one file that owns Codex-specific harness behavior, keep the shared workflow text authoritative, and validate the wording with an independent reviewer pass.

**Conventions:** Prefer one source of truth, minimal wording, and harness-specific placement. Do not fork shared workflow behavior into Codex-only copies.

**Output:** Updated Codex harness instructions in `skills/using-superRA/references/codex-instructions.md` and the canonical `skills/using-superRA/SKILL.md` load rule, covering named-agent dispatch preference, reviewer-default behavior, Codex-only warm-agent lifecycle guidance, high-level Codex-specific instructions, and explicit Codex instructions loading, plus any narrowly necessary consistency edits if an adjacent document becomes misleading after the change.

**Expected Results / Hypotheses:** A Codex agent that has loaded superRA and is following its workflow should read the Codex instructions reference as explicit user preference for named-agent dispatch in Codex, rather than treating the harness-default anti-delegation guidance as dominant. Reviewer dispatch should remain non-optional by default, Codex orchestrators should treat long-running warm agents as normal rather than closing them eagerly, and Codex agents should explicitly load `references/codex-instructions.md` whenever they load `using-superRA`.

**Sensitivity Analysis:** *(not applicable — instruction-only change)*

**Pipeline:** *(not needed — single-surface instruction update with review)*

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on data inventory + plan (`planning-workflow` Phase 2)
- [x] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`implementation-workflow` Step 3)
- [ ] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Phase A)
- [ ] **Refactored** — integration reviewer `APPROVED` on the unified sync+refactor diff (`integration-workflow` Phase B)
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Phase C)
- [ ] **Merged** — branch merged to main or PR opened (`integration-workflow` Phase D)

---

## Project Conventions

Walked at planning time (2026-04-22). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at `addc9ca`): contributor guidance for superRA itself. Behavior-shaping edits require reading before changing, treating skill changes as skill creation, preserving the four workflow principles, and keeping harness differences in adapter references instead of forking shared workflow text.
- `/AGENTS.md`: symlink to `/CLAUDE.md`; same contributor guidance exposed under the Codex-facing filename.
- `/AGENT.md`: symlink to `/CLAUDE.md`; convenience alias only.
- `/README.md` (HEAD at `addc9ca`): user-facing product overview. superRA promises an implementer-reviewer pair at every step, keeps Codex support split between plugin skills and named custom agents, and describes worktrees as optional workflow infrastructure.

### Module-level docs walked
- *(none beyond repo root; no nested guidance docs lie on the planned diff path)*

### Not walked (not reachable from the planned diff)
- `docs/`, `tests/`, and skill directories outside the orchestration/Codex instruction surfaces — out of scope unless the authoritative change forces a consistency edit.

## Decisions

> **User decision (2026-04-22):** Skip Phase A drift-test creation and proceed directly to Phase B integration review for this branch.
> **Question asked:** Which key results should be protected with drift tests before integration?
>
> **User decision (2026-04-22):** Use `origin/main` as the Phase B integration base for this branch.
> **Question asked:** Is `origin/main` the correct integration base, or did this branch split from some other base branch?
>
> **Integration note (2026-04-22):** `origin/main` was already an ancestor of this branch at Phase B close, so no mechanical merge commit was needed before Phase C.
>
> **User decision (2026-04-22):** Extend Task 1 with Codex-only warm-agent lifecycle guidance: long-running agents are normal, do not shut them down eagerly, and use warm-agent messaging when the orchestrator needs to communicate with a running agent.
> **Question asked:** Add one more Codex-only orchestration instruction about agent lifetime and warm-agent communication?
> **Rationale (if given):** Clear the `Refactored` milestone and reopen Task 1 `Integration status` for a fresh Phase B review; keep `Review status` approved because the change stays on the same Codex adapter surface.
>
> **User decision (2026-04-22):** Make `using-superRA` explicitly tell Codex agents to load `references/codex-tools.md` whenever they load the master skill.
> **Question asked:** Did the current setup actually guarantee that Codex agents would load `codex-tools` whenever they loaded `using-superRA`, and if not, should it be made explicit?
> **Rationale (if given):** Clear the `Refactored` milestone and reopen Task 1 `Integration status` for a fresh Phase B review; keep `Review status` approved because the change stays on the same Codex adapter / master-skill surface.
>
> **User decision (2026-04-22):** Rename the Codex adapter reference from `codex-tools.md` to `codex-instructions.md` and treat it as the home for high-level must-know Codex-specific instructions, including cases where superRA intentionally overrides generic Codex agent defaults.
> **Question asked:** Rename `codex-tools` to `codex-instructions`, and can that file hold high-level Codex instructions such as the user-invoked superRA override?
> **Rationale (if given):** Keep the Codex-specific guidance in one obvious place and make its role broader than raw tool-name mapping.

### Task 1: Update the Codex instructions surface for dispatch, warm-agent lifecycle, and load semantics
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** IMPLEMENTED

**Script:** `skills/using-superRA/references/codex-instructions.md` and `skills/using-superRA/SKILL.md` (primary); `tests/check-harness-compatibility.sh`, `skills/using-superRA/references/main-agent.md`, `skills/agent-orchestration/SKILL.md`, and `README.md` only if adjacent wording becomes misleading
**Input:** repo-root contributor docs, current Codex harness adapter wording, current execution-mode/orchestration wording
**Output:** minimal committed instruction update that (a) treats user-invoked superRA workflow/skills as explicit delegation preference in Codex, (b) keeps reviewer dispatch mandatory unless the user explicitly says no or agent tools are unavailable, (c) tells Codex orchestrators not to shut down warm agents eagerly and to use warm-agent messaging when coordination is needed, (d) explicitly tells Codex agents to load `references/codex-instructions.md` whenever they load `using-superRA`, (e) establishes that file as the home for high-level must-know Codex-specific instructions, and (f) preserves the shared workflow files as the source of truth

- [x] Confirmed the ownership boundary between shared workflow text and Codex-specific harness adapters.
- [x] Added the Codex-specific delegation, warm-agent lifecycle, explicit instructions-load rules, and renamed the Codex reference to match its broader role.
- [x] Checked adjacent docs for stale or contradictory claims; no consistency edits were needed.
