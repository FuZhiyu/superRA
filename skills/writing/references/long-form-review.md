# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Load with `review.md` and the relevant review-lane files.

## Trigger

Load when scope spans more than one review lane, thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass.

Review lanes are:

- **Language/style:** `style.md`
- **Structure:** `structure.md`
- **Consistency:** one lane per relevant `consistency/<dim>.md`

## Two-stage lifecycle

**Stage 1 — Findings.** Standalone reviews use `REVIEW.md` at the worktree root. Reviews riding an existing workflow use that workflow's `PLAN.md` and add a temporary `## Findings` section.

Findings live under one subsection per dispatched lane (`### Language & Style`, `### Structure`, `### Notation`, `### Terminology`, ...). In deep mode, use one subsection per perspective under the lane (for example, `### Language & Style — skeptical referee`).

Consistency-lane reviewers use the relevant `consistency/<dim>.md` output format unchanged. Language/style and structure reviewers use `review.md`'s finding format and add `Fix: mechanical | conventional | authorial` using `review.md §Fix tiers`.

Each finding carries a stable global F-ID assigned at write time: next available, no reuse, no renumber. F-IDs survive Stage 2 for commit-message audit.

Reviewers prefill this block at the end of every finding:

```markdown
**User feedback:**
- [ ] Accept
- [ ] Defer
- [ ] Reject
**Reason / instructions:**
```

The Stage 1 gate passes when every finding has exactly one checked verdict. The reason line may stay empty for accepted findings; deferred or rejected findings should carry the user's reason or instruction when available.

**Stage 1 → Stage 2 rewrite (orchestrator action, one atomic commit).**

1. Route the active document:
   - Standalone review: `git mv REVIEW.md PLAN.md`.
   - Existing workflow: keep the existing `PLAN.md` and rewrite it in place.
2. Replace the Stage 1 Workflow Status with the Stage 2 rollup below.
3. For every accepted finding, build an actionable Stage 2 task block per the granularity rule below. Inline each absorbed finding under `**Findings absorbed:**`, preserving the original finding body and F-ID.
4. Move every deferred or rejected finding into `## Deferred & Rejected` at the bottom of the document, retaining F-ID, verdict, and reason.
5. Delete the Stage 1 `## Findings` section after all findings have been absorbed or moved.

Flip "Plan approved" in the Workflow Status in the same commit.

**Stage 2 — Actionable plan.** `implementation-workflow` runs over the Stage 2 task blocks. Task blocks follow `handoff-doc`'s standard `plan-anatomy.md §Task Block Anatomy`. `Integration status:` is omitted; review-driven polish does not flow through `integration-workflow`.

## Stage 2 task granularity

- One accepted `authorial` finding = one task.
- Accepted `mechanical` and `conventional` findings batch by issue class: one task per coherent polish sweep across the manuscript, not one task per section.
- Add a final Verify task for build and cross-reference checks; it depends on all prior tasks.

## Workflow Status

**Stage 1:**

```markdown
## Workflow Status
- [ ] <lane-1> reviewer done
- [ ] <lane-2> reviewer done
- [ ] ...
- [ ] User feedback recorded — every finding has exactly one checked verdict
```

Use one reviewer-done checkbox per dispatched lane, or per perspective in deep mode.

**Stage 2:**

```markdown
## Workflow Status
- [ ] Plan approved — Stage 2 task blocks written from accepted findings
- [ ] Execution complete — every polish task APPROVED
- [ ] Drift tests created — N/A for review-driven polish (auto-satisfied)
- [ ] Integrated — N/A for review-driven polish (auto-satisfied)
- [ ] Docs finalized — N/A for review-driven polish (auto-satisfied)
- [ ] Finished — PLAN.md archived or deleted per the lifecycle ladder
```

## Review-time indices

Use `## Project Conventions` only for durable convention choices covered by `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`. For review-time lookup aids, create a sibling `## Document Map` section in the active Stage 1 document when useful. Common indices: key terminology, figures and tables, cross-references, and notation pointers needed for the assigned lanes.

## Dispatch convention

Dispatch through `agent-orchestration`'s canonical reviewer template. Keep `Stage: implementation`; long-form review changes the artifact reviewers write, not the superRA stage model.

Stage 1 reviewers append findings to their assigned `## Findings` subsection instead of returning APPROVE / REVISE on a commit range.

Do not dispatch a reviewer-of-reviewer pass over the assembled findings. An optional final-summary reviewer pass may read the assembled document and produce only the summary block below.

## Multi-perspective deep mode

When thoroughness is `deep`, dispatch 2-3 reviewers per lane with different stances or reading orders. Each reviewer writes to its own perspective subsection. Closeout merges duplicate findings across perspectives and gives multi-perspective agreement more weight in the final summary.

## Final summary block

After findings are collected, the orchestrator builds a final summary block at the top of the active Stage 1 document: severity by fix-tier counts, top three priorities, pointers to `## Findings` subsections, and a per-tier batch table sized for Stage 2 task construction.
