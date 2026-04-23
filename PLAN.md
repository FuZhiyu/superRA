# PLAN — Direct-Mode Role References

**Objective:** Remove the direct-mode requirement that the main agent
read raw `agents/implementer.md` and `agents/reviewer.md`, because that
path is not guaranteed in cross-repo Codex plugin use. Replace it with
skill-owned references that the main agent can load through
`superRA:using-superra`, document the temporary manual-maintenance
approach, and add a validation check for the new path.

**Methodology:** Take the simple immediate fix. Manually copy the
direct-mode-relevant role protocol into `skills/using-superRA/references/`,
update `main-agent.md` to load those references in direct mode, and add
doc/test coverage that makes the new dependency explicit. Defer
automatic generation/sync to a later follow-up.

**Conventions:** Keep `agents/implementer.md` and `agents/reviewer.md`
canonical. The new direct-mode references are temporary manual mirrors
owned by `skills/using-superRA/` so the main agent can load them from
the plugin skill surface. Do not delete `.agents/skills/` in this pass:
repo docs and current tests treat it as the load-bearing repo-local
Codex skill-discovery surface.

**Output:** two skill-owned direct-mode role references under
`skills/using-superRA/references/`, updated direct-mode instructions in
`skills/using-superRA/references/main-agent.md`, development-facing doc
updates describing the manual mirror rule, an archived-hand-off pointer
from `docs/plans/2026-04-22-codex-agent-dispatch-preference-{plan,results}.md`,
and validation in `tests/check-harness-compatibility.sh`.

**Expected Results / Hypotheses:** A main agent running direct mode can
follow the implementer/reviewer role protocol without depending on raw
`agents/*.md` files. The fix should work for both Codex and Claude
because the direct-mode references live under the shared skill surface.
The `.agents/skills/` symlink surface should remain in place because it
is repo-local Codex skill discovery, not a stray custom-agent artifact.

**Sensitivity Analysis:** *(not applicable — workflow/doc surface fix)*

**Pipeline:** `bash tests/check-harness-compatibility.sh`

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on data inventory + plan (`planning-workflow` Phase 2)
- [ ] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`implementation-workflow` Step 3)
- [ ] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Phase A)
- [ ] **Refactored** — integration reviewer `APPROVED` on the unified sync+refactor diff (`integration-workflow` Phase B)
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Phase C)
- [ ] **Merged** — branch merged to main or PR opened (`integration-workflow` Phase D)

---

## Project Conventions

Walked at planning time (2026-04-22). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at `addc9ca`): contributor guidance for superRA itself. Skill changes should be treated as skill creation, canonical workflow text stays shared, harness differences belong in adapter references, and Codex repo-local discovery currently relies on `.agents/skills/`.
- `/AGENTS.md`: symlink to `/CLAUDE.md`; same contributor guidance exposed under the Codex-facing filename.
- `/AGENT.md`: symlink to `/CLAUDE.md`; convenience alias only.
- `/README.md` (HEAD at `addc9ca`): user-facing Codex docs describe a split between the plugin-delivered shared skills and separately installed named agents.

### Module-level docs walked
- `/docs/plans/2026-04-22-codex-agent-dispatch-preference-plan.md`: archived permanent record for the prior scope on this branch; now carries the re-entry decision and should remain the historical record rather than the active execution tracker.
- `/docs/plans/2026-04-22-codex-agent-dispatch-preference-results.md`: archived permanent results for the prior scope; current follow-up should only add a pointer/note, not overwrite its original findings.
- `/skills/using-superRA/references/main-agent.md`: direct mode currently tells the main agent to read raw `agents/implementer.md` / `agents/reviewer.md`; this is the primary file to rewrite.
- `/agents/implementer.md` and `/agents/reviewer.md`: canonical role protocols remain here; the follow-up should copy only the direct-mode-relevant role guidance into skill-owned references, leaving these files canonical.
- `/skills/codex-superra-setup/SKILL.md`: named Codex agents expect the superRA skills to be available in the parent session; setup does not make raw repo files available to the main agent in other repos.
- `/tests/check-harness-compatibility.sh`: current top-level harness check already guards Codex metadata, agent generation, and `.agents/skills/` symlink coverage; extend it for the new direct-mode reference path.

### Not walked (not reachable from the planned diff)
- `docs/` outside the archived 2026-04-22 pair, `tests/` outside the compatibility check, and workflow/domain skills unrelated to direct mode — out of scope unless the fix forces a consistency edit.

## Decisions

> **User decision (2026-04-22):** Re-enter planning after archive because direct mode still tells the main agent to read raw `agents/implementer.md` / `agents/reviewer.md`, which are not guaranteed in cross-repo Codex plugin use.
> **Question asked:** If globally installed Codex agents do not make the raw agent files available to the main agent, how should the follow-up proceed?
> **Rationale (if given):** Fix the accessibility gap before merge.
>
> **User decision (2026-04-22):** Use the simple immediate fix: manually copy the direct-mode role protocol into skill-owned references now, and defer automatic sync/generation to a later improvement.
> **Question asked:** Build the sync mechanism now, or take a simpler copy-paste direct-mode reference first?
> **Rationale (if given):** Unblock the immediate fix first; improve maintainability in a separate follow-up.

### Task 1: Add skill-owned direct-mode role references and wire main-agent direct mode to them
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:** *(not started)*

**Script:** `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `skills/using-superRA/references/main-agent.md`
**Input:** canonical role protocols in `agents/implementer.md` and `agents/reviewer.md`, current direct-mode bullets in `skills/using-superRA/references/main-agent.md`
**Output:** two skill-owned direct-mode role references containing the role protocol the main agent needs in direct mode, plus updated direct-mode instructions that load those references instead of raw `agents/*.md`

- [x] **Step 1: Choose the manual copy boundary.** Copied the role-protocol sections the main agent actually needs in direct mode: stage-load guidance, pre-start checks, self-review / review protocol, handoff ownership, inline-edit discipline, and commit / escalation rules. Left dispatch-prompt framing, worktree-return mechanics, and orchestrator-facing report format in the canonical agent files because `main-agent.md` already owns that surface.
- [x] **Step 2: Create the skill-owned references.** Added `skills/using-superRA/references/direct-mode-implementer.md` and `skills/using-superRA/references/direct-mode-reviewer.md` with explicit notes that they are temporary manual mirrors of the canonical agent files.
- [x] **Step 3: Rewire direct mode.** Updated `skills/using-superRA/references/main-agent.md` so direct mode now loads the new skill-owned references instead of raw `agents/implementer.md` / `agents/reviewer.md`.
- [x] **Step 4: Validate the read path.** Re-read the direct-mode bullets and the new references together, then ran `bash tests/check-harness-compatibility.sh`; the direct-mode path no longer depends on raw agent files and still preserves the review requirement.

### Task 2: Document and validate the temporary manual-mirror approach
**Depends on:** 1
**Review status:** IMPLEMENTED
**Integration status:** *(not started)*

**Script:** `CLAUDE.md`, `tests/check-harness-compatibility.sh`, archived 2026-04-22 plan/results pair, `RESULTS.md`
**Input:** the new direct-mode references from Task 1, current contributor guidance, current compatibility guard, and the user concern about repo-local `.agents` surfaces
**Output:** development-facing docs that mention the temporary manual-mirror rule, a compatibility check covering the new direct-mode references, archived 2026-04-22 handoff docs updated with a pointer to this re-entry, and a recorded judgment that `.agents/skills/` stays because it is repo-local Codex skill discovery

- [x] **Step 1: Update the development-facing docs.** Added contributor guidance in `CLAUDE.md` describing the direct-mode role mirrors and the requirement to update the canonical agent files and the mirrors together until automation exists.
- [x] **Step 2: Add validation coverage.** Extended `tests/check-harness-compatibility.sh` so it now requires the new direct-mode references, checks that `main-agent.md` points at them, rejects regressions back to raw `agents/*.md`, and verifies each mirror declares its canonical source and manual-mirror status.
- [x] **Step 3: Keep the archived handoff coherent.** Confirmed the archived 2026-04-22 plan/results pair already points at this follow-up plan/results from commit `cc4ea46`; no further archive edit was needed in this pass.
- [x] **Step 4: Record the `.agents` audit result.** Recorded in `RESULTS.md` that `.agents/skills/` remains a load-bearing repo-local Codex skill-discovery surface, so this pass does not delete it.
