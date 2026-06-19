---
title: "Restructure superintegrate Integrate to Do-Then-Verify"
status: approved
depends_on:
  - 01-min-net-diff-baseline
  - 02-implementer-integration-self-review
tags: []
output:
  - skills/superintegrate/SKILL.md
created: 2026-06-18
---

## Objective

Rewrite the `## Integrate` section of `skills/superintegrate/SKILL.md` so the post-sync codebase-fit work is produced proactively (do-then-verify) instead of only reactively in response to reviewer findings. Compose the discipline from [01-min-net-diff-baseline](../01-min-net-diff-baseline/task.md) and the combined role from [02-implementer-integration-self-review](../02-implementer-integration-self-review/task.md); do not restate either — the manifest loads `refactor-and-integrate` and the role spec is authoritative.

New step sequence (renumber accordingly; keep the existing `**Governing diff:** git diff BASE_HEAD_SHA..HEAD` note and Step 1 drift-test run):

1. Run the full drift-test suite. (unchanged)
2. **Integration implementer pass (refactor + self-review).** Dispatch `Stage: integration` implementer(s) to fit the post-sync diff to the host project and run the Final-Diff-Self-Check; they return with `## Review Notes` for any scope-ambiguous retained hunk and `DONE_WITH_CONCERNS`. A trivial post-sync diff collapses to an orchestrator-inline pruning sweep in Direct mode.
3. **Orchestrator adjudication.** For each first-pass concern: **fix** (dispatch an implementer to revert junk / address) or **amend** (fold the justification into the objective via `superplan §User Feedback and Changing the Task Tree`, dropping the concern). The resolving commit clears the now-moot first-pass note so the independent reviewer starts from a clean `## Review Notes` (this is what keeps `agents/reviewer.md` unchanged — see parent objective). Batch user-owned questions into one stop point.
4. **Independent integration reviewer(s).** Dispatch fresh `Stage: integration` reviewer(s) for a full first review of `BASE_HEAD_SHA..HEAD` against the trail; set per-task `approved` or `revise`.
5. **Refactor loop** for accepted `revise` items (the existing reactive loop — preserve it, renumbered).
6. **Close Integrate.** (the existing closeout — Sync-Impact removal, `superra task check`, commit — renumbered.)

Also:
- Add one line that **the number of integration implementers and reviewers is discretionary, scaled to the post-sync delta** (small single-subtree delta → one implementer pass or inline + one reviewer; large or multi-subtree delta → fan out per subtree), pointing to `agent-orchestration §Workload Balancing` rather than restating it.
- Update `§When to Lighten` (the "Integrate often collapses to a short reviewer pass" line) and `§Red Flags` to match the do-then-verify shape (e.g. a red flag for closing Integrate with no Final-Diff-Self-Check trail / reviewing before the codebase-fit pass produced it).

Preserve the existing dispatch-field shape from `agent-orchestration §Dispatch Templates`; name `Tasks in scope` task paths in the dispatches (do not hand the reviewer a bare label). Keep `BASE_HEAD_SHA..HEAD` as the governing range throughout.

Validation: the Integrate section reads do-then-verify end to end; the trivial-delta inline path and the agent-count discretion are both stated; `§When to Lighten` and `§Red Flags` are consistent; no restatement of prune discipline or role protocol; passes `CLAUDE.md §Teach the Protocol` DRY + Necessity.

## Results

Rewrote the `## Integrate` section of [skills/superintegrate/SKILL.md](../../../skills/superintegrate/SKILL.md) to a do-then-verify shape and updated the overview block, `§When to Lighten`, and `§Red Flags` for consistency.

New Integrate step sequence ([SKILL.md:170-259](../../../skills/superintegrate/SKILL.md#L170-L259)):

1. **Run the full drift-test suite** (unchanged).
2. **Integration implementer pass (refactor + self-review)** — `Stage: integration` implementer(s) fit the post-sync diff to the host project, run the Final-Diff-Self-Check, set `status: implemented`, author `## Review Notes` for scope-ambiguous retained hunks, and return `DONE_WITH_CONCERNS`. A trivial post-sync diff collapses to an orchestrator-inline pruning sweep in Direct mode.
3. **Orchestrator adjudication** — per first-pass concern, **fix** (dispatch an implementer to revert junk / address) or **amend** (fold the justification into the objective via `superplan §User Feedback and Changing the Task Tree`); the resolving commit clears the moot note so the independent reviewer starts clean.
4. **Independent integration reviewer(s)** — fresh `Stage: integration` reviewer(s) do a full first review of `BASE_HEAD_SHA..HEAD` against the Final-Diff-Self-Check trail; set per-task `approved`/`revise`.
5. **Refactor loop** — the preserved reactive loop for accepted `revise` items.
6. **Close Integrate** — the preserved closeout (Sync-Impact removal, `superra task check`, commit).

Composition (no restatement): Step 2 points to §What You Own and the loaded `refactor-and-integrate` for the prune discipline and combined-role self-review; the reviewer dispatch keeps the prior finding-coverage list. Added one discretion line at [SKILL.md:174](../../../skills/superintegrate/SKILL.md#L174) pointing to `agent-orchestration §Workload Balancing` for scaling implementer/reviewer count to the post-sync delta. `agents/reviewer.md` is untouched — Step 3's note-clearing is what preserves its full-first-review semantics.

`§When to Lighten` standalone line now reads "an inline pruning sweep plus a short reviewer pass" ([SKILL.md:369](../../../skills/superintegrate/SKILL.md#L369)). `§Red Flags` gains a line for reviewing before the codebase-fit pass produced the diff or closing Integrate with no Final-Diff-Self-Check trail ([SKILL.md:378](../../../skills/superintegrate/SKILL.md#L378)). Dispatch-field shape from `agent-orchestration §Dispatch Templates` preserved; `Tasks in scope` task paths named in every dispatch; `BASE_HEAD_SHA..HEAD` is the governing range throughout.

**Final diff self-check:** `git diff b0865e11..HEAD -- skills/superintegrate/SKILL.md` (only file changed); surviving hunks are the Integrate-section do-then-verify rewrite plus overview / §When to Lighten / §Red Flags consistency edits — all `skills/*` instruction-prose (the suspicious class), justified line by line against this task objective: the six-step sequence, the discretion line pointing to `agent-orchestration §Workload Balancing`, and the §Red Flags addition introduce no restatement of prune discipline or role protocol (both pointed to, not restated) — passes `CLAUDE.md §Teach the Protocol` DRY + Necessity. Integration-pass codebase-fit change: the rewrite added a sixth Integrate step but `§When to Lighten` "Small changes" still said "Keep the same five steps" — a stale count introduced by this rewrite — corrected to "six steps" ([SKILL.md:370](../../../skills/superintegrate/SKILL.md#L370)); line 8's "five steps" refers to the five top-level phases and is correct, left unchanged. `check_markdown.py` clean.
