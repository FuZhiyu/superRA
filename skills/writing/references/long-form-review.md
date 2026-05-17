# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Loaded **in addition to** `review.md` and the relevant `consistency/<dim>.md` files; everything those references already teach is assumed and not restated here.

## Trigger

Load when scope is multi-dimensional (>1 `consistency/<dim>.md`), thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass. Quick single-dimension reviews stay in `review.md` and do not load this file.

## Doc convention

### Two-stage lifecycle

The shared review document lives through two stages that share one file.

**Stage 1 — Findings (file is `REVIEW.md` at the worktree root).** Per-aspect task blocks per `handoff-doc/references/plan-anatomy.md §Task Block Anatomy` — one block per consistency dimension (or per perspective in deep mode), all `**Depends on:** *(none)*`. Reviewers dispatched in parallel populate findings in each block's review-notes blockquote using the assigned `consistency/<dim>.md` output format unchanged. Each finding carries a stable global F-ID (F1, F2, …) assigned by the reviewer at write time. One rule covers all eight `consistency/<dim>.md` outputs: assign the next available F-ID when writing a new finding; do not reuse or renumber.

Per-aspect Stage-1 task blocks carry a `**User feedback:**` field populated by the main agent after reviewers return — one line per finding:
```
**User feedback (YYYY-MM-DD):**
- F<n>: accept | defer | reject [— optional reason]
```

**User feedback gate.** The gate between stages passes when every finding has a verdict. Main agent writes `**User feedback:**` into each Stage-1 block and commits; Workflow Status box "User feedback recorded" flips.

**Stage 1 → Stage 2 rewrite (orchestrator action, one atomic commit).** Four moves:
1. `git mv REVIEW.md PLAN.md`
2. Hoist every finding into a new `## Findings` header section — flat numbered index by F-ID, preserving the `consistency/<dim>.md`-format entry and the user-feedback verdict per finding. Rejected and deferred findings remain with their verdict marker so Stage-2 implementers can see why no task absorbed them. The section survives until Closeout.
3. Delete the per-aspect Stage-1 task blocks (their content now lives in `## Findings`).
4. Write Stage-2 actionable task blocks per the granularity rule below, each carrying `**Sources:** F2, F5, F9` pointing into `## Findings`.

Flip Workflow Status box "Plan approved" in the same commit. This is an orchestrator action; `plan-anatomy.md §Header ownership` permits header edits by the orchestrator.

**Stage 2 — Actionable plan (file is `PLAN.md`).** Standard `implementation-workflow` runs over Stage-2 task blocks unchanged. Stage-2 task blocks follow the standard `plan-anatomy.md §Task Block Anatomy`. `Integration status:` is omitted; review-driven polish work does not flow through `integration-workflow`.

**Standalone-only rename rule.** The rename applies only when the long-form review is invoked standalone (no pre-existing workflow PLAN.md). When the review rides an existing workflow with a live PLAN.md, there is no separate REVIEW.md: Stage-1 per-aspect blocks live in that PLAN.md as temporary task blocks, Stage-2 rewrites them inline within the same file. There is only ever one PLAN.md in play — no collision possible.

### Stage-2 task granularity

- One authorial-accepted finding = one task. Each authorial decision is its own work item and may need its own author conversation.
- Mechanical and conventional accepted findings batch by issue class — one task per coherent polish sweep cutting across the manuscript (e.g., all typos, all citation-format issues, all cross-ref label cleanups, terminology-variant collapse, nominalization cluster). Bucketing is by kind-of-fix, not manuscript geography.
- Final Verify task: build + cross-reference check, depends on all prior tasks.

### Workflow Status

**Stage 1 (in REVIEW.md):**
```
## Workflow Status
- [ ] Reviewers dispatched
- [ ] Findings collected — every Stage-1 per-aspect task IMPLEMENTED
- [ ] User feedback recorded — every finding has accept/defer/reject
```

**Stage 2 (replaces the Stage-1 rollup at rename time, standard PLAN.md rollup):**
```
## Workflow Status
- [ ] Plan approved — Stage-2 task blocks written from accepted findings
- [ ] Execution complete — every polish task APPROVED
- [ ] Drift tests created — N/A for review-driven polish (auto-satisfied)
- [ ] Integrated — N/A for review-driven polish (auto-satisfied)
- [ ] Docs finalized — N/A for review-driven polish (auto-satisfied)
- [ ] Finished — PLAN.md archived or deleted per the lifecycle ladder
```

### Review-time indices in `## Project Conventions`

The orchestrator builds four review-time indices in the `## Project Conventions` header of whichever doc the lifecycle ladder in `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md` resolves to (REVIEW.md standalone, the workflow's PLAN.md when riding one) before dispatch so each parallel reviewer reads them instead of cold-reading the manuscript: notation index (key symbols → meaning + first-use location), terminology index (key terms → definition + first-use), figures-and-tables index, cross-reference index. Promote to a sibling `## Document Map` section when the indices outgrow Conventions.

## Dispatch convention

Use the canonical reviewer template in `superRA:agent-orchestration §Dispatch Templates` — `subagent_type: "superRA:reviewer"`, `Stage: implementation` (no new Stage value; the writing skill add-on routes via the manifest). Two adaptations specific to Stage-1 review-as-data:

- The manuscript is the implicit "implementer output" being audited; reviewers append findings to their assigned per-aspect block instead of returning APPROVE / REVISE on a commit range.
- **No reviewer-of-reviewer pass.** The assembled `REVIEW.md` is the artifact; chaining adversarial review over the findings is recursion. An optional final-summary reviewer pass over the assembled doc is the only second pass permitted.

Parallel-dispatch + worktree-isolation steering carries over from `agent-orchestration`; one reviewer per per-aspect block.

## Multi-perspective deep mode

When thoroughness is `deep`, dispatch 2–3 reviewers per dimension with diverse stances ("skeptical referee" / "constructive mentor" / "domain expert") and ordering ("forward" / "backward from conclusions" / "most complex first"). Each reviewer writes findings into its **own** per-perspective task block under that dimension. Closeout merges findings across perspectives and weights multi-agent-confirmed findings higher in the final summary.

## Final summary block

After Findings collected, the orchestrator builds a final summary block at the top of the active Stage-1 handoff doc (REVIEW.md standalone, the workflow's PLAN.md when riding one): severity × fix-tier counts table, top-3 priorities, pointer to each per-aspect block, and a per-tier batch table (mechanical / conventional / authorial) sized for Stage-2 task construction. Optionally produced with a final-summary reviewer pass over the assembled doc.
