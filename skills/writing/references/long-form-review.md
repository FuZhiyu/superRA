# Long-Form Review Protocol

> Multi-agent review orchestration for academic drafts. Loaded **in addition to** `review.md` and the relevant `consistency/<dim>.md` files; everything those references already teach is assumed and not restated here.

## Trigger

Load when scope is multi-dimensional (>1 `consistency/<dim>.md`), thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass. Quick single-dimension reviews stay in `review.md` and do not load this file.

## Doc convention

### Two-stage lifecycle

The shared review document lives through two stages that share one file.

**Stage 1 — Findings (file is `REVIEW.md` at the worktree root).** Per-aspect task blocks per `handoff-doc/references/plan-anatomy.md §Task Block Anatomy` — one block per consistency dimension (or per perspective in deep mode), all `**Depends on:** *(none)*`. Reviewers dispatched in parallel populate findings in each block's review-notes blockquote using the assigned `consistency/<dim>.md` output format unchanged. Each finding carries a stable global F-ID (F1, F2, …) assigned by the reviewer at write time; this ID is used for cross-referencing throughout both stages. One rule covers all eight `consistency/<dim>.md` outputs: assign the next available F-ID when writing a new finding; do not reuse or renumber.

Per-aspect Stage-1 task blocks carry a `**User feedback:**` field populated by the main agent after reviewers return — one line per finding: `F<n>: accept | defer | reject [— optional reason]`. Granularity is per-finding because authorial decisions and per-item exceptions need explicit authorization; per-task tier directives bolt exceptions on awkwardly.

**User feedback gate.** The gate between stages passes when every finding has a verdict. Main agent writes `**User feedback:**` into each Stage-1 block and commits; Workflow Status box "User feedback recorded" flips.

**Stage 1 → Stage 2 rewrite (orchestrator action, one atomic commit).** Four moves:
1. `git mv REVIEW.md PLAN.md`
2. Hoist every finding into a new `## Findings` header section — flat numbered index by F-ID, preserving the `consistency/<dim>.md`-format entry and the user-feedback verdict per finding. Rejected and deferred findings remain with their verdict marker so Stage-2 implementers can see why no task absorbed them. The section survives until Closeout.
3. Delete the per-aspect Stage-1 task blocks (their content now lives in `## Findings`).
4. Write Stage-2 actionable task blocks per the granularity rule below, each carrying `**Sources:** F2, F5, F9` pointing into `## Findings`.

Flip Workflow Status box "Plan approved" in the same commit. This is an orchestrator action; `plan-anatomy.md §Header ownership` permits header edits by the orchestrator.

**Stage 2 — Actionable plan (file is `PLAN.md`).** Standard `implementation-workflow` runs over Stage-2 task blocks unchanged — agents read this file exactly as they read any other PLAN.md. Each Stage-2 task uses the standard Task Block Anatomy from `plan-anatomy.md`: `Depends on`, `Review status`, Steps with the polish work, review-notes blockquote on REVISE rounds. `Integration status:` is omitted; review-driven polish work does not flow through `integration-workflow`.

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

The orchestrator builds four review-time indices in the `## Project Conventions` header before dispatch so each parallel reviewer reads them instead of cold-reading the manuscript: notation index (key symbols → meaning + first-use location), terminology index (key terms → definition + first-use), figures-and-tables index, cross-reference index. Promote to a sibling `## Document Map` section when the indices outgrow Conventions.

## Dispatch convention

Use the canonical reviewer template in `superRA:agent-orchestration §Dispatch Templates` — `subagent_type: "superRA:reviewer"`, `Stage: implementation` (no new Stage value; the writing skill add-on routes via the manifest). Two adaptations specific to Stage-1 review-as-data:

- The manuscript is the implicit "implementer output" being audited; reviewers append findings to their assigned per-aspect block instead of returning APPROVE / REVISE on a commit range.
- **No reviewer-of-reviewer pass.** The assembled `REVIEW.md` is the artifact; chaining adversarial review over the findings is recursion. An optional final-summary reviewer pass over the assembled doc is the only second pass permitted.

Parallel-dispatch + worktree-isolation steering carries over from `agent-orchestration`; one reviewer per per-aspect block.

## Implementer / reviewer interaction walk-through

**Stage 1 — parallel reviewer dispatch.** Each per-aspect block's Step says: review the manuscript for dimension D; write findings into the review-notes blockquote per `consistency/<dim>.md` output format; assign each finding a global F-ID. The orchestrator dispatches `subagent_type: superRA:reviewer` per the Dispatch convention above. Reviewer sets `**Review status:** IMPLEMENTED` after writing findings and committing. No implementer in Stage 1.

**User feedback gate.** Main agent collects user decisions per finding, writes `**User feedback:**` into each Stage-1 task block, commits. Workflow Status "User feedback recorded" flips when every finding has a verdict.

**Stage 1 → Stage 2 rewrite.** Orchestrator performs `git mv REVIEW.md PLAN.md` plus the four-move rewrite in one atomic commit and flips "Plan approved." Orchestrator action — not a dispatched agent.

**Stage 2 implementer dispatch.** Orchestrator dispatches `subagent_type: superRA:implementer`, `Stage: implementation`, writing skill add-on, pointing at PLAN.md Task K. The implementer reads its task block, sees `**Sources:** F2, F5, F9`, looks up those entries in `## Findings` (header read covered by `implementer.md §Before You Start`), loads `polish.md` (mode routing recognizes shape-C "apply review findings"), applies per tier, commits, sets `**Review status:** IMPLEMENTED`.

**Stage 2 reviewer dispatch.** Standard `subagent_type: superRA:reviewer` against the commit range. Reads the task block, the cited Findings, and the diff; returns APPROVE or REVISE with review-notes blockquote per the canonical protocol. REVISE round uses the standard `→ implemented:` annotation pattern. Cycle terminates at APPROVED.

**Verify task.** Standard implementer runs build per `refactor-and-compile.md §Compile` and cross-reference check; standard reviewer APPROVES on green. Workflow Status "Execution complete" flips when every Stage-2 task is APPROVED.

**Closeout.** Main agent deletes or archives PLAN.md per the lifecycle ladder; flips "Finished."

## Multi-perspective deep mode

When thoroughness is `deep`, dispatch 2–3 reviewers per dimension with diverse stances ("skeptical referee" / "constructive mentor" / "domain expert") and ordering ("forward" / "backward from conclusions" / "most complex first"). Each reviewer writes findings into its **own** per-perspective task block under that dimension. Closeout merges findings across perspectives and weights multi-agent-confirmed findings higher in the final summary.

## Final summary block

After Findings collected, the orchestrator builds a final summary block at the top of REVIEW.md: severity × fix-tier counts table, top-3 priorities, pointer to each per-aspect block, and a per-tier batch table (mechanical / conventional / authorial) sized for Stage-2 task construction. Optionally produced with a final-summary reviewer pass over the assembled doc.
