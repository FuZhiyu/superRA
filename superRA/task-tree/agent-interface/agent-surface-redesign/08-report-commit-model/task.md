---
title: "Collapse Reporting onto Commit = Summary, Return = Status + SHA"
status: implemented
depends_on:
  - 06-restructure-specs
tags: []
created: 2026-06-01
---

## Objective

Collapse the per-dispatch reporting onto the parent §Conventions "Reporting model": the git commit message is the **single authored change summary**, and the agent's status return shrinks to **status enum + commit SHA**. This supersedes the §Report Format and §Commit that task 01 shipped (which still carried a multi-field report whose "Doc edits" duplicated the commit). Apply symmetrically to [agents/implementer.md](../../../../../agents/implementer.md) and [agents/reviewer.md](../../../../../agents/reviewer.md).

**This task builds on the user's in-progress hand-edits to `implementer.md` (persona trimmed, the "delta is only a pointer" sentence removed) — preserve them; do not revert.**

**§Commit (both specs).** The commit body is the full change summary — what changed this dispatch and why — and is the *only* place the summary is authored. Subject unchanged: `implement task <task-path>` / `review task <task-path>` (status/verdict stays in `status:`). Keep the pointer to `using-superra` §Commit Hygiene.

**§Report Format (both specs) → the minimal status return.** Keep the `## Report Format` heading (avoids extra generator churn), but reduce its body to:
- Implementer: the status enum (`DONE`/`DONE_WITH_CONCERNS`/`BLOCKED`/`NEEDS_CONTEXT`) + the commit SHA. Drop the Summary / Key findings / Concerns / Doc edits fields. `DONE_WITH_CONCERNS` → the concern lives in `## Results` (caveat) and/or the commit body; the enum flags the orchestrator to read. `BLOCKED`/`NEEDS_CONTEXT` → no commit exists, so the return carries the blocker / missing-context instead of a SHA. Keep the worktree-return line for parallel dispatch (branch + HEAD SHA) since that is control state the orchestrator needs and has no other home.
- Reviewer: the assessment (`APPROVE`/`REVISE`) + the commit SHA. Drop the Review Summary block's Scope/Headline/Doc-edits fields. Findings stay in `## Review Notes`. Evaluate whether the closing `ACTION REQUIRED (REVISE)` footer is now redundant with the orchestrator's own iterate-on-REVISE protocol (`agent-orchestration`/`superimplement`) and drop it under DRY if so.

**§Results human-readability (binding — supersedes the earlier conditional phrasing).** The "Results = state" leg of the Reporting model must be made explicit in **three** places (an earlier draft made this optional — "add only if not already implied" — and the implementer judged it implied and added nothing; it is now required):
1. **`using-superRA` §Task Interface → Editing principles** (the shared home, loaded by both roles): add a principle — *write the body sections you own (`## Results`, `## Review Notes`) as a self-contained, human-readable account a reader can follow standalone, with links and embedded figures where they aid understanding (see `report-in-markdown`), not a terse changelog; the change summary belongs in the commit, not the body.*
2. **Implementer `## Self-Check`**: add a checklist step verifying `## Results` is that self-contained, human-readable account (not just "findings present").
3. **Reviewer**: the reviewer verifies the same — that the implementer's `## Results` reads as a self-contained, human-readable account — as part of its review pass.

Do not duplicate `report-in-markdown`'s figure/link mechanics — point to it. Keep the principle stated once in §Task Interface; the §Self-Check step and the reviewer check reference that quality, they don't restate the mechanics.

**Generator (`[BLOCKING]`).** The §Report Format content shrinks (headings stay). Update [sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) only where it string-matches now-removed report paragraphs (e.g. the reviewer `strip_subsection("### Report Format")` path and any matched report wording); update [test_sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py); regenerate the four artifacts; pass `--check` + `pytest`.

**Cross-surface check.** Confirm no skill that consumes the report (`agent-orchestration` §Handling Implementer Status / §Review Status Reference, `superimplement` Step 2) depends on a now-removed report field — they key off the status enum and read the commit/task.md, so they should be unaffected; flag in `## Results` if any does.

**Verification:** both specs' return is status-enum + SHA (blocker text when no commit); the commit body is the sole summary; `--check` clean; generator tests green; `task_check.py --plan-root superRA` clean.

## Planner Guidance

This is a focused, surgical change to two sections per spec plus a small generator/test touch — medium model is fine. The reviewer (task 01) and implementer specs share the new model, so draft the minimal `## Report Format` body once and mirror it. The orchestrator-facing change (it now reads the commit instead of a prose report) needs no edit to `agent-orchestration` — that skill already treats the return as a navigation aid and the diff/task as the evidence; just confirm it.

## Results

**Implementer `## Report Format`** ([agents/implementer.md](../../../../../agents/implementer.md)): shrunk to status enum + commit SHA + worktree-return line (path B only). Removed: Summary, Key findings, Concerns, Doc edits. `DONE_WITH_CONCERNS` and `BLOCKED`/`NEEDS_CONTEXT` behavior explained inline. Worktree-return line moved from `### Commit` to here (its only home for control state).

**Implementer `### Commit`**: removed the "Author that delta once; the status report's 'Doc edits' field reuses the same text" sentence and the worktree block (relocated to `## Report Format`).

**Reviewer `## Report Format`** ([agents/reviewer.md](../../../../../agents/reviewer.md)): shrunk to assessment + commit SHA. Removed: Review Summary block (Scope/Headline findings/Doc edits fields). Removed `ACTION REQUIRED (REVISE)` footer — DRY against the orchestrator's iterate-on-REVISE protocol in `agent-orchestration`. Updated "Headline findings" reference in §How You Write a Review to "commit body" since the field no longer exists.

**Reviewer `### Commit`**: removed the "Author that delta once; the status report's 'Doc edits' field reuses the same text" sentence.

**Escalation-channel consistency (review item 1)**: standardized every ad-hoc escalation/observation routing onto the **status return** — the surface the orchestrator actually reads when an agent comes back (`agent-orchestration` §Handling Implementer Status "Read the concerns"; §Handling Reviewer Feedback expects the reviewer to "escalate" on its return). Reverted reviewer line 123 ("Orchestrator override you disagree with") from "commit body" back to "status return"; normalized reviewer line 129 ("CRITICAL cannot be silently overridden") and implementer lines 51/83/86 from "status report"/"report" to "status return". Also normalized the two doc-before-report self-check bullets (implementer §Self-Check, reviewer §Self-Check) from "status report" to "status return" so the term is uniform. The commit body remains the change-summary surface; ad-hoc escalations belong in the return (consistent with the BLOCKED/NEEDS_CONTEXT free-text precedent the §Report Format already permits).

**§Results human-readability (binding scope addition) — three touchpoints landed**:
1. **`using-superRA` §Task Interface → Editing principles** ([SKILL.md:53](../../../../../skills/using-superRA/SKILL.md#L53)): added the shared principle — owned body sections (`## Results`, `## Review Notes`) are a self-contained, human-readable account a reader follows standalone (links + embedded figures per `report-in-markdown`), not a terse changelog; the change summary belongs in the commit. Mechanics point to `report-in-markdown`, not restated.
2. **Implementer `## Self-Check`** ([implementer.md:46](../../../../../agents/implementer.md#L46)): added a distinct completeness bullet verifying `## Results` reads as that self-contained, human-readable account (referencing §Task Interface), separate from the existing content-presence bullet (line 45, which I trimmed of its former "self-contained summary" phrasing to avoid overlap).
3. **Reviewer `## Review Protocol` → Read Files First** ([reviewer.md:38](../../../../../agents/reviewer.md#L38)): added a verification that the implementer's `## Results` reads as the self-contained account required by §Task Interface; a changelog-only `## Results` is a MINOR finding.

**Cross-surface check**: `agent-orchestration` §Handling Implementer Status keys off status enums only (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED); §Review Status Reference keys off `status:` frontmatter. Neither depends on removed report fields. One stale reference in [agent-teams.md:144](../../../../../skills/agent-orchestration/references/agent-teams.md#L144) ("Read each `**Doc edits:**` line") was updated to "Read each agent's commit body to understand what changed."

**Generator** ([sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py)): the `cleanup_implementer_handoff` worktree-block stripping was already removed in the prior round; this round fixed the stale `render_direct_mode_ref` comment (review item 2) that still listed "Worktree: fields" as a stripped fragment — it now describes the actual remaining behavior (the §How You Fix opener rewrite). No other string-matching on removed report paragraphs exists. Regenerated all four artifacts; `--check` clean; `pytest` 7/7 passed.

**Verification commands:**
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → clean
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` → 7 passed
- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` → all checks passed

## Review Notes

> 1. [MAJOR] The worktree-return line this task kept references "path B" / "path A" ([implementer.md:115](../../../../../agents/implementer.md#L115)) — terms defined nowhere in the repo (a whole-tree grep finds no other occurrence, including `agent-orchestration` and its worktree reference), so an implementer reading its spec cannot resolve when the field applies. The dangling vocabulary propagates into both generated surfaces. Replace with the concrete condition (e.g. "only when dispatched with a `Worktree:` field") and regenerate.
>    → implemented: replaced "path B only" / "path A" with "only when dispatched with a `Worktree:` field" / "when no `Worktree:` field was present" ([implementer.md:115](../../../../../agents/implementer.md#L115)); regenerated all four artifacts; `--check` exits 0
