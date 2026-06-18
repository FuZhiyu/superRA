# PLAN — Codex Agent Dispatch Preference

**Objective:** Make Codex treat a user-invoked superRA workflow as explicit authorization for the named-agent workflow, with reviewer dispatch still mandatory, warm-agent lifecycle guidance explicit, and a canonical Codex instructions reference guaranteed to load whenever `using-superra` loads.

**Methodology:** Update the one file that owns Codex-specific harness behavior, keep the shared workflow text authoritative, and validate the wording with an independent reviewer pass.

**Conventions:** Prefer one source of truth, minimal wording, and harness-specific placement. Do not fork shared workflow behavior into Codex-only copies.

**Output:** committed Codex adapter updates that (a) treat user-invoked superRA workflow/skills as explicit delegation preference in Codex, (b) keep reviewer dispatch mandatory unless the user explicitly says no or agent tools are unavailable, (c) tell Codex orchestrators not to shut down warm agents eagerly and to use warm-agent messaging when coordination is needed, (d) explicitly tell Codex agents to load `references/codex-instructions.md` whenever they load `using-superra`, (e) establish that file as the home for high-level must-know Codex-specific instructions, (f) preserve the shared workflow files as the source of truth, and (g) land the permanent Phase C records at `docs/plans/2026-04-22-codex-agent-dispatch-preference-plan.md` and `docs/plans/2026-04-22-codex-agent-dispatch-preference-results.md`.

**Expected Results / Hypotheses:** A Codex agent that has loaded superRA and is following its workflow should read the Codex instructions reference as explicit user preference for named-agent dispatch in Codex, rather than treating the harness-default anti-delegation guidance as dominant. Reviewer dispatch should remain non-optional by default, Codex orchestrators should treat long-running warm agents as normal rather than closing them eagerly, and Codex agents should explicitly load `references/codex-instructions.md` whenever they load `using-superra`.

**Sensitivity Analysis:** *(not applicable — instruction-only change)*

**Pipeline:** *(not needed — single-surface instruction update with review)*

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on data inventory + plan (`planning-workflow` Phase 2)
- [x] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`implementation-workflow` Step 3)
- [ ] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Phase A)
- [x] **Refactored** — integration reviewer `APPROVED` on the unified sync+refactor diff (`integration-workflow` Phase B)
- [x] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Phase C)
- [x] **Merged** — branch merged to main or PR opened (`integration-workflow` Phase D)

---

## Project Conventions

Walked at planning time (2026-04-22). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at `addc9ca`): contributor guidance for superRA itself. Behavior-shaping edits require reading before changing, treating skill changes as skill creation, preserving the four workflow principles, and keeping harness differences in adapter references instead of forking shared workflow text.
- `/AGENTS.md`: symlink to `/CLAUDE.md`; same contributor guidance exposed under the Codex-facing filename.
- `/AGENT.md`: symlink to `/CLAUDE.md`; convenience alias only.
- `/README.md` (HEAD at `addc9ca`): user-facing product overview. superRA promises an implementer-reviewer pair at every step, keeps Codex support split between plugin skills and named custom agents, and describes worktrees as optional workflow infrastructure.

### Module-level docs walked
- `/docs/plans/`: permanent archive for completed plan/results pairs; current naming convention is dated sibling files with `-plan.md` and `-results.md` suffixes.

### Not walked (not reachable from the planned diff)
- `docs/` outside `docs/plans/`, `tests/`, and skill directories outside the orchestration/Codex instruction surfaces — out of scope unless the authoritative change forces a consistency edit.

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
> **User decision (2026-04-22):** Make `using-superra` explicitly tell Codex agents to load `references/codex-tools.md` whenever they load the master skill.
> **Question asked:** Did the current setup actually guarantee that Codex agents would load `codex-tools` whenever they loaded `using-superra`, and if not, should it be made explicit?
> **Rationale (if given):** Clear the `Refactored` milestone and reopen Task 1 `Integration status` for a fresh Phase B review; keep `Review status` approved because the change stays on the same Codex adapter / master-skill surface.
>
> **User decision (2026-04-22):** Rename the Codex adapter reference from `codex-tools.md` to `codex-instructions.md` and treat it as the home for high-level must-know Codex-specific instructions, including cases where superRA intentionally overrides generic Codex agent defaults.
> **Question asked:** Rename `codex-tools` to `codex-instructions`, and can that file hold high-level Codex instructions such as the user-invoked superRA override?
> **Rationale (if given):** Keep the Codex-specific guidance in one obvious place and make its role broader than raw tool-name mapping.
>
> **User decision (2026-04-22):** Open a GitHub pull request for this branch after the approved Phase B follow-up.
> **Question asked:** Do we have a PR up, and if not, create it?
>
> **Integration note (2026-04-22):** Opened draft PR [#19](https://github.com/FuZhiyu/superRA/pull/19) from `analysis/codex-agent-dispatch-preference` into `main`.
>
> **User decision (2026-04-22):** Polish the Codex adapter wording so the Codex action map uses concrete Codex tool names, replacing `SendMessage` with `send_input` and preserving the explicit load rule.
> **Question asked:** Review and polish the local edits so the instruction file uses the correct Codex tool names?
> **Rationale (if given):** Keep the Codex adapter concrete and unambiguous for harness-specific actions without weakening the previously approved load semantics.
>
> **User decision (2026-04-22):** Mature the working plan/results pair into `docs/plans/2026-04-22-codex-agent-dispatch-preference-plan.md` and `docs/plans/2026-04-22-codex-agent-dispatch-preference-results.md` so the branch is ready to merge.
> **Question asked:** Mature plan and results into the right place so the branch can be merged?
> **Rationale (if given):** Follows the repo's established `docs/plans/` convention for permanent plan/results records.
>
> **Integration note (2026-04-22):** No root `results_attachments/` directory existed on this branch, so Phase C only relocated the plan/results markdown files.
>
> **Integration note (2026-04-22):** Permanent records landed at `docs/plans/2026-04-22-codex-agent-dispatch-preference-plan.md` and `docs/plans/2026-04-22-codex-agent-dispatch-preference-results.md`.
>
> **User decision (2026-04-22):** Re-enter planning after archive because direct mode still tells the main agent to read raw `agents/implementer.md` / `agents/reviewer.md`, which are not guaranteed in cross-repo Codex plugin use.
> **Question asked:** If globally installed Codex agents do not make the raw agent files available to the main agent, how should the follow-up proceed?
> **Rationale (if given):** Fix the accessibility gap before merge.
>
> **User decision (2026-04-22):** Use the simple immediate fix for the follow-up: manually copy the direct-mode role protocol into skill-owned references now, and defer automatic sync/generation to a later improvement.
> **Question asked:** Build the sync mechanism now, or take a simpler copy-paste direct-mode reference first?
> **Rationale (if given):** Unblock the immediate fix first; improve maintainability in a separate follow-up.
>
> **Integration note (2026-04-22):** The post-archive direct-mode follow-up ultimately matured into `docs/plans/2026-04-22-direct-mode-role-references-plan.md` and `docs/plans/2026-04-22-direct-mode-role-references-results.md`; this archived pair remains the permanent record for the original dispatch-preference scope.

### Task 1: Update the Codex instructions surface for dispatch, warm-agent lifecycle, and load semantics
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** `skills/using-superra/references/codex-instructions.md` and `skills/using-superra/SKILL.md` (primary); `tests/check-harness-compatibility.sh`, `skills/using-superra/references/main-agent.md`, `skills/agent-orchestration/SKILL.md`, and `README.md` only if adjacent wording becomes misleading
**Input:** repo-root contributor docs, current Codex harness adapter wording, current execution-mode/orchestration wording
**Output:** committed Codex adapter updates that (a) treat user-invoked superRA workflow/skills as explicit delegation preference in Codex, (b) keep reviewer dispatch mandatory unless the user explicitly says no or agent tools are unavailable, (c) tell Codex orchestrators not to shut down warm agents eagerly and to use warm-agent messaging when coordination is needed, (d) explicitly tell Codex agents to load `references/codex-instructions.md` whenever they load `using-superra`, (e) establish that file as the home for high-level must-know Codex-specific instructions, (f) preserve the shared workflow files as the source of truth, and (g) land the permanent Phase C records at `docs/plans/2026-04-22-codex-agent-dispatch-preference-plan.md` and `docs/plans/2026-04-22-codex-agent-dispatch-preference-results.md`

- [x] Confirmed the ownership boundary between shared workflow text and Codex-specific harness adapters.
- [x] Added the Codex-specific delegation, warm-agent lifecycle, explicit instructions-load rules, and renamed the Codex reference to match its broader role.
- [x] Updated the root contributor guidance after integration review surfaced the stale `<harness>-tools.md` naming pattern; no further consistency edits were needed.
- [x] Polished the Codex action map to name concrete Codex tools (`request_user_input`, `update_plan`, `spawn_agent`, `send_input`) and restored the explicit load/inventory wording that the local follow-up edit had softened.
- [x] Matured the working `PLAN.md` / `RESULTS.md` pair into the permanent `docs/plans/` archive using the repo's dated `-plan.md` / `-results.md` convention.
