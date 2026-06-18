---
title: "Restructure Both Role Specs + Relocate Planning-Review + Reconcile Generator"
status: approved
depends_on:
  - 03-role-spec-slim
tags: []
created: 2026-06-01
---

## Objective

The single atomic structural overhaul. Rewrite both specs to the shared skeleton, move planning-review mode out to the planning workflow, and reconcile the generator — all together, because the generator parses specs by exact headings and `--check` cannot pass until specs and generator agree (the in-progress `## Handoff` rename already breaks it). End state: both specs clean and parallel, planning-review with one home, `--check` green, generator tests green.

### A. Rewrite both specs to the shared skeleton

Rewrite [agents/implementer.md](../../../../../agents/implementer.md) and [agents/reviewer.md](../../../../../agents/reviewer.md) to the shared target skeleton in the parent task's §Conventions, removing all duplication and fixing ordering/numbering defects, so the two specs are **parallel-structured** (identical section headings and subsection order for shared concepts).

**Implementer:**
- Keep the terse persona line and the evidence-first stance.
- §Before You Start: keep the load-skills / read-task steps; fold the one-line dispatch-inputs note into the lead.
- §Execution Protocol: keep objective-vs-guidance, deviation reporting, domain discipline.
- **Merge `### Self-Review Before Reporting` and `## Pre-Commit Self-Check` into one `## Self-Check`** placed immediately before commit (the user's "reorder; right before the commit section" comment). Order: evidence-before-claims (IDENTIFY/RUN/READ/VERIFY) → completeness → **stale-content cleanup** (the user's new check: superseded text removed, no "Previously…/Update:" blocks, task reads as one current-state description) → domain `[BLOCKING]`/`[ADVISORY]` checklist walk → editing-hygiene checklist. The "every material finding is in `task.md`, not only the report" line appears **once**.
- §Handoff: What You Own (positive framing; keep "not allowed to edit other sections — report instead"), Editing Etiquette (point to `using-superra` §Task Interface + the one role rule), How You Fix the REVISE round, Commit.
- §Report Format: "Doc edits" reuses the commit delta (parent §Conventions → Commit convention).
- §Escalation: keep.

**Reviewer (symmetric — most implementer insights apply here too):**
- Keep the persona + adversarial paragraph + the user-added own-judgment-beyond-checklists paragraph.
- §Before You Start: **fix the broken numbering** (currently 1, 2, 3, 5).
- §Review Protocol: Read Files First, Verify Claims Independently, Severity Levels, Verdict — define severity and verdict **once here**; have §How You Write a Review reference §Verdict instead of restating first-review/re-review verdict mechanics.
- Add a `## Self-Check` in the same pre-commit slot as the implementer's.
- §Handoff: What You Own (positive framing — drop "What You Don't"), Editing Etiquette, How You Write a Review (point to §Verdict; keep the non-duplicated first-review/re-review/CRITICAL-override mechanics), Commit.
- Keep §Report Format and the closing `ACTION REQUIRED` line.

**Commit convention (both files):** subject `implement task <task-path>` / `review task <task-path>` (verdict stays in `status:`); body is the delta; point to `using-superra` §Commit Hygiene for staging. See parent §Conventions.

### B. Relocate planning-review mode to the planning workflow

The user's reviewer comment: "planning review should just be a reference under the planning workflow rather than duplicated here."

1. **Create a reviewer-facing planning-review reference** under superplan (suggested `skills/superplan/references/planning-review.md`) carrying the reviewer's `Stage: planning-review` execution mechanics: the two `Review mode:` values (handoff-readiness, design-review) and what each evaluates; note-ownership and status rules (findings only in the assigned target's `## Review Notes`; never edit task `status:`; on REVISE numbered `[BLOCKING]`/`[ADVISORY]` findings, linking child task files when a finding concerns a descendant; on re-review delete fixed items; on APPROVE remove `## Review Notes`; there may be no git range); the planning-review APPROVE/REVISE verdict. Moved from reviewer.md, not copied.
2. **Reconcile with [thorough-planning.md](../../../../../skills/superplan/references/thorough-planning.md) §Planning Review** so the two don't duplicate: keep planner-facing dispatch context there, move reviewer-facing mechanics into the new reference, cross-link without restating. Update the `CLAUDE.md` ownership-table row for planning-review to name the new reference as the home for the mechanics.
3. **Add a `Stage: planning-review` row to the `using-superra` §Skill-Load Manifest Generic table** loading the new reference (today it has no entry, so the reviewer wouldn't auto-load it — this row makes the relocation work). Update the manifest note ("`superplan` and `agents/reviewer.md` own its mode and task-status exceptions") to point at the reference.
4. **Replace reviewer.md's planning-review content with a one-line pointer** (at `Stage: planning-review`, follow the manifest-loaded reference). Remove `### Planning Review Mode` plus the planning-review clauses in §Before You Start / §What You Own / §How You Write a Review; strand nothing.

### C. Reconcile the generator + regenerate (`[BLOCKING]`)

Update [sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) hardcoded section names and string-matched paragraphs (`render_direct_mode_ref`, `render_*_direct_mode_before_you_start`, `cleanup_implementer_handoff`, `strip_subsection`, the reviewer planning-review handling) to match the new structure, so the direct-mode reviewer points to the planning-review reference rather than embedding the section. Update [test_sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py); regenerate the four artifacts; pass the `[BLOCKING]` regen gate (`--check` + `pytest`).

**Verification:** both specs read cleanly top-to-bottom; no duplication remains within or across files; a reviewer reading only its real load path still has the full planning-review mechanics; `--check` clean; generator tests green; `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` clean. Task 03 proves no knowledge was lost — but do not knowingly drop a behavior-shaping line here; relocate it.

## Planner Guidance

Draft the shared skeleton outline for both files first, then fill each section, so parallel structure is enforced by construction. The reviewer §Severity Levels + §Verdict are the single home for severity/verdict; collapse the §How You Write a Review duplication into a reference. The implementer's two checklists overlap on "findings live in task.md" and "stale content replaced in place" — keep one copy of each in the merged §Self-Check. This is a large, high-synthesis task touching ~9 files (two specs, the new reference, the manifest, the generator + its test, four regenerated artifacts) — warrants a higher-capability model. The planning-review reviewer mechanics to move currently live in reviewer.md §Planning Review Mode plus its clauses in §Before You Start / §What You Own / §How You Write a Review.

## Results

Both role specs are rewritten to the shared parallel skeleton, planning-review mechanics are relocated to a single home under superplan, and the generator + tests + four regenerated artifacts are all in lockstep. All gates green.

### A. Specs rewritten to the shared skeleton

[agents/implementer.md](../../../../../agents/implementer.md) and [agents/reviewer.md](../../../../../agents/reviewer.md) now share an identical top-level order for shared concepts: persona/stance → `## Before You Start` → `## Execution Protocol` / `## Review Protocol` → `## Self-Check` → `## Handoff` (`### What You Own` → `### Editing Etiquette` → `### How You Fix…` / `### How You Write a Review` → `### Commit`) → `## Report Format` → `## Escalation` / `ACTION REQUIRED`.

Defects fixed:
- **Implementer:** merged `### Self-Review Before Reporting` + `## Pre-Commit Self-Check` into one ordered `## Self-Check` placed immediately before `### Commit`, ordered evidence-before-claims → completeness → stale-content cleanup → domain checklist walk → editing-hygiene. The deleted `**Reproducibility:**` sub-block's surviving guidance ("follow the domain/project format convention, relative paths, reproducible by re-running") is folded into the completeness item. "Every material finding is in `task.md`, not only the report" appears once.
- **Reviewer:** fixed the broken `## Before You Start` numbering (was 1, 2, 3, 5 → now 1-4). Severity and verdict are defined once in `## Review Protocol` (`### Severity Levels`, `### Verdict`); `### How You Write a Review` now references them instead of restating. Dropped "What You Don't" (positive ownership framing only). Added a parallel `## Self-Check` in the same pre-commit slot as the implementer. The closing `ACTION REQUIRED` line is preserved as a top-level trailer after `## Report Format` (was nested inside Handoff).
- **Persona:** kept the user's terse reviewer persona + adversarial paragraph + the user-added own-judgment-beyond-checklists paragraph (grammar cleaned, meaning preserved). Added the reviewer's missing `For Codex agents: Load \`using-superra\` skill.` line for parity with the implementer.

**Commit convention (resolved the user's commit-message comment, symmetric across both files):** subject is `implement task <task-path>` / `review task <task-path>`; status/verdict is not in the subject (it lives in `status:`, files carry latest state); body is the **delta** (git for change, files for the latest status); the agent authors that delta once and the report's "Doc edits" field reuses the same text. Both point to `using-superra` §Commit Hygiene for staging.

All four user `<!-- ... -->` comments in scope (the two implementer Self-Review/Pre-Commit comments, the implementer commit-message comment, the reviewer planning-review comment) are resolved and removed from the shipped files. The one remaining comment in `using-superra/SKILL.md:111` (domain add-ons) is a different concern, out of this task's scope, and left untouched.

### B. Planning-review relocated to one home

- New reviewer-facing reference [skills/superplan/references/planning-review.md](../../../../../skills/superplan/references/planning-review.md) carries the full `Stage: planning-review` reviewer mechanics: the two `Review mode:` values and what each evaluates, the APPROVE/REVISE verdict, note ownership (findings only in the assigned target's `## Review Notes`; never edit `status:`; link child task files; re-review deletes fixed items; APPROVE removes the section), and "there may be no git range." Moved from `reviewer.md`, not copied.
- [thorough-planning.md](../../../../../skills/superplan/references/thorough-planning.md) §Planning Review keeps planner-facing dispatch context (what each mode evaluates from the planner's side, "planner fixes the tree inline") and now cross-links to `planning-review.md` for reviewer mechanics instead of restating them.
- [using-superra/SKILL.md](../../../../../skills/using-superra/SKILL.md) §Skill-Load Manifest: the `planning-review` Generic row now loads `skills/superplan/references/planning-review.md`; the manifest note points at the reference as the owner of mode/verdict/note-ownership mechanics.
- [CLAUDE.md](../../../../../CLAUDE.md) ownership table: added a planning-review row naming `planning-review.md` as the mechanics home (planner-facing context stays in `thorough-planning.md`).
- `reviewer.md` planning-review content is replaced by a one-line pointer in `## Before You Start` ("At `Stage: planning-review`, follow the manifest-loaded planning-review reference instead of the implementation protocol below"); `### Planning Review Mode` and the planning-review clauses in §What You Own / §How You Write a Review are removed.

### C. Generator + tests reconciled

[sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) `render_direct_mode_ref` updated to the new section names (`## Handoff`, the merged `## Self-Check`, top-level `## Report Format`); the dead `## Dispatch Inputs` drop path is gone (folded into §Before You Start). The now-unused `strip_subsection` / `find_heading_line` / `heading_level` helper chain was removed. The reviewer direct-mode before-you-start gained the planning-review pointer line. [test_sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py) gained `test_reviewer_planning_review_relocated_to_reference`, locking that neither `reviewer.md` nor its generated direct-mode reference embeds the planning-review section and both point to the reference. The four artifacts ([direct-mode-implementer.md](../../../../../skills/using-superra/references/direct-mode-implementer.md), [direct-mode-reviewer.md](../../../../../skills/using-superra/references/direct-mode-reviewer.md), [.codex/agents/superra_implementer.toml](../../../../../.codex/agents/superra_implementer.toml), [.codex/agents/superra_reviewer.toml](../../../../../.codex/agents/superra_reviewer.toml)) are regenerated.

### Verification (all green)

- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → "All generated agent files are up to date" / "All generated direct-mode role references are up to date" (was crashing with `KeyError: '## Handoff — Unified Across Stages'` before this task).
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` → 7 passed.
- `uv run pytest skills/codex-superra-setup/... skills/task-tree/scripts/test_task_tree.py` → 235 passed.
- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` → "All checks passed."
- Repo-wide grep confirms no stale references to the renamed sections (`Handoff — Unified`, `Planning Review Mode`, `Pre-Commit Self-Check`, old `review: <task-path> <verdict>` commit form) outside the new negative-assertion test.

### No-knowledge-lost note for task 03 (one reachability concern to adjudicate)

Most removed lines are relocated and reachable through each role's real load path (verdict/severity → reviewer §Review Protocol; planning-review mechanics → `planning-review.md`; reproducibility → implementer §Self-Check; integration convention-fit → `refactor-and-integrate` Project Doc Audit at `Stage: integration`). One item needs the audit's attention: the **subagent** implementer §Before You Start step "apply the scoped conventions in your inherited context" and the reviewer §Before You Start step "hold the work to scoped conventions (MAJOR integration finding)" were deleted by the user's wip baseline. They survive in the hand-authored **direct-mode** before-you-start blocks and (for integration review) in `refactor-and-integrate`, but the generic-stage *subagent* specs no longer carry an explicit "apply/walk inherited conventions" cue. I preserved the user's deletion rather than re-adding a step the user visibly removed; the natural relocation home if task 03 wants it reachable for all stages is `using-superra` §Task Interface (which the user also trimmed). Flagging for adjudication, not silently dropping.

## Review Notes

> 1. [MINOR] The generator splice this task reconciled leaves dispatch-only wording in direct-mode output: "For a bundle dispatch, run this protocol independently…" ([direct-mode-implementer.md:32](../../../../../skills/using-superra/references/direct-mode-implementer.md#L32); reviewer line 34), "unless the dispatch says otherwise" ([direct-mode-reviewer.md:81](../../../../../skills/using-superra/references/direct-mode-reviewer.md#L81)), and the "For Codex agents: Load…" line ([direct-mode-implementer.md:13](../../../../../skills/using-superra/references/direct-mode-implementer.md#L13)). The implementer variant also drops §Report Format while §Escalation still says "report with BLOCKED or NEEDS_CONTEXT" ([direct-mode-implementer.md:117](../../../../../skills/using-superra/references/direct-mode-implementer.md#L117)), leaving the enums undefined in direct mode. Extend the substitutions in [sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) and regenerate.
