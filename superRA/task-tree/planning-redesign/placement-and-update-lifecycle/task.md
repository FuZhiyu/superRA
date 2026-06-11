---
title: "Cross-Stage Placement + the Update-Task Lifecycle"
status: approved
depends_on:
  - entry-and-placement
  - consolidation
tags: [planning-redesign, placement, consolidation, lifecycle]
created: 2026-06-01
---

## Objective

Close the design gap that let new improvement work be created as a misplaced standalone task instead of being folded into the task that owns its concern. Make "modify/merge the existing owner" the default and "create a new task" the justified exception, reframe placement as a cross-stage concern (not planning-only), and define the stage-dependent lifecycle of an *update task* so these transient improvement tasks are spun out cleanly during planning and merged back at integration.

This evolves the two approved siblings it depends on — `entry-and-placement` (Entry Assessment + §Placing Work) and `consolidation` (survey protocol + symptom list + integration routing hook) — rather than overwriting them. Per the very rule below, a big planning-stage update is spun out as a self-contained subtask now and merged into its targets at integration.

### The problem (observed 2026-06-01)

During a superintegrate dogfood, an improvement to the integration workflow was created as a **new root-level task** (`integrate-cleanup`) when it was actually an update to the existing `task-tree/agent-interface/integ-workflow` task, which owns the integration-workflow SKILL and was thereby left stale. Two skill weaknesses allowed it:

1. **Placement is passive and CREATE is frictionless.** `§Placing Work in the Tree` Step 1 ("walk the tree, find the concern") produces no evidence, so a confident agent skips the walk and jumps to "Create sibling." "Prefer modifying existing task.md files over adding new tasks" exists only as a buried one-liner in `superplan §User Feedback`, far from the entry-assessment placement decision. The anti-pattern is named in prose but not gated.
2. **The consolidation gate/survey cannot see misplacement.** The "Task at the wrong level or under the wrong parent → Restructure" symptom is inherently *whole-tree*, but the survey protocol builds its relationship matrix "for each pair of tasks at the same level," and the new superintegrate consolidation gate reads as frontier-internal. So the gate that is supposed to be the backstop rubber-stamped the misplaced subtree as "clean-enough."

### Design

**1. The placement algorithm — recursive descent, preference ladder, burden of proof (cross-stage).** Rewrite `task-tree/references/planning.md §Placing Work in the Tree` as an explicit recursive procedure whose presumption is MODIFY/MERGE the owning task, with new-task creation — especially root-level — as the justified exception.

The algorithm walks from the root. The invariant is that you only descend into `node` because the work relates to `node`'s concern, so the question at each node is never *whether* the work belongs here but *how deep* it lands. Split on **leaf vs branch first**; the descend-vs-add-child choice is a sub-decision within the branch case:

- **Branch** (a node with children — a concern container that holds no deliverable work of its own):
  - a child's concern covers the work → **descend** into that child and recurse;
  - no child covers it → **add a new child subtask** under this node. At the root, that new child is a new root-level workstream — the last-resort, highest-stakes move; record which existing child's concern was read and why it does not cover the work.
- **Leaf** (a node with no children — a unit of work):
  - *simple* → **update it in place** and flip its status `approved`→`revise`; no new task;
  - *complex* → **nest a subtask** under it.

"Create a sibling / new root-level task" is **not** a separate operation — a sibling is just a new child of the shared parent, so it falls out of the branch rule's "add a new child" evaluated at the root. Root-misuse is therefore controlled by the same rule, not a special case. The justification requirement on adding a child at the root cannot be written without doing the walk, which forces the read and surfaces the owner. This replaces the current "if no task at this level covers it, create a sibling" exit, which fires sideways on any non-exact match and is the structural source of duplicate root tasks. There is no "unrelated at the leaf" case: you only reach a leaf by descending through related concerns, so at a leaf the work is related by construction. Status flip references the existing status lifecycle; it does not redefine status semantics.

Frame placement explicitly as a **cross-stage** concern that applies in planning, consolidation, and integration — not a planning-only step. (The researcher's note: "it's not only about planning.") Decide and state the framing: reframe the §Placing Work section as cross-stage in place, OR — if consolidation and integration need to load placement rules directly — extract it into a dedicated `task-tree/references/placement.md` that planning, consolidation, and the integration gate all point to. Tradeoff: extraction gives clean cross-stage loading but adds a file + links to maintain; in-place reframe is less churn but leaves placement inside a planning-named reference. Recommend the option that lets the consolidation gate and superintegrate point at one placement owner.

**Positive root-task definition.** State, in the same section, that a root-level task is a **whole workstream/project** and the single root frames the entire repo — a narrow feature related to an existing workstream nests by the ladder above and therefore cannot land at root unless it is genuinely unrelated to everything. This makes root-task misuse a *consequence* of the ladder rather than a separate rule. Detection of pre-existing narrow-root debt is the advisory `task check` category in the sibling `restructuring-tooling` task (item 5).

**2. Define the update-task lifecycle (the core new rule).** An *update task* — a task whose purpose is to improve or modify an existing task or artifact — has a stage-dependent disposition driven by a real tradeoff. The governing principle is **asymmetric aggressiveness**: planning is lenient (a complex fix may be spun out as its own task), consolidation is strict (the fix folds back into the task it modified). This is the "the tree represents latest state, not a log" rule — already enforced *within* a task's body — applied to the tree *structure*: a standalone "fix/update task X" is a delta, the structural equivalent of a log entry, and must be squashed into its target at integration.

- **Tradeoff.** Merging the change into the target task keeps one source of truth, but done *prematurely* (before the change is built and validated) it overwrites the target's nuance/history and conflates unsettled work with settled work. Spinning out a separate self-contained subtask preserves a clear, independently reviewable objective, but proliferates tasks that are harder to clean up later. Weigh by complexity, validation maturity, and reviewability.
- **Rule of thumb.**
  - **Planning stage (pre-implementation):** for a substantial update, CREATE a self-contained subtask under the owning concern. Give it a full, dispatchable objective. Do not merge into the target yet — premature merge loses nuance before the change even exists.
  - **Consolidation / Integration stage:** MERGE update tasks into the task they update — fold the matured result into the target/parent and remove the update-task directory. An update task should not survive integration as a standalone artifact. This is the create-then-merge lifecycle: spin out during planning/implementation, merge back at consolidation/integration.
- **Worked example (already applied).** The integration-workflow redesign was first created as a misplaced root-level `integrate-cleanup` task, then — applying this rule ahead of its codification — merged into `integ-workflow` at integration (its objective/Results refreshed to the shipped design, stale content dropped) and the standalone task removed (2026-06-01). Use this as the concrete example in the rule text: an update task does not survive integration as a separate tree.

**3. Make the consolidation survey + gate whole-tree for placement, and Merge N-way.** Fix `skills/superplan/references/consolidation.md` so the wrong-parent/Restructure check compares each task/subtree's concern against parents and other subtrees, not only same-level pairs; and fix the superintegrate Consolidation Gate so its placement/Restructure check is whole-tree, not frontier-internal. Tie the gate to the lifecycle rule: at the consolidation gate, update tasks present in the frontier are merge candidates by default. (The gate implementation is in `skills/superintegrate/SKILL.md`; its task record now lives in `integ-workflow` after the 2026-06-01 merge — land the whole-tree fix there.)

Also strengthen the **Merge** action from pairwise-only to **N-way merge into a subtree**: when several tasks cluster on one concern, fold them into a single parent concern with the distinct survivors as children (a Merge+Split composite), rolling up status conservatively and rewiring all `depends_on` across the cluster. Dependency-rewiring on rename/delete is provided by the sibling `restructuring-tooling` task (item 5); the N-way merge itself stays a **manual** consolidation step so the human controls how the combined tasks' nuance is integrated — no `task merge` command.

**4. Auditability net (optional, cheap).** Add one line to `superplan` Phase 4 / User Review surfacing the placement decision: for each new task — especially root-level — state the existing concern considered and why it does not cover the work. Keeps a human catch in the loop without enforcement machinery.

**5. Safe-execution + detection tooling (sibling task).** The rules above are skill-prose; their safe, repeatable *execution* and the detection of pre-existing debt live in the sibling `task-tree/restructuring-tooling` task: a lossless `depends_on` rewire in the PostToolUse hook for same-parent renames (YAML metadata only — the class the hook already auto-writes for status rollups), an advisory `task check --category placement` that flags narrow-root / single-child-root / branch-carrying-`script` / misplacement smells, and the agent-facing documentation of that hook behavior so a rename's dep-cascade is expected rather than surprising. (Merge stays manual — no command — so merge decisions remain human-controlled.) That task depends logically on this one (the detector encodes the codified rules); the edge is cross-tree and so cannot be a sibling `depends_on` — it is tracked in prose, and is itself an instance of the sibling-only-dependency limitation that motivates the rewire tooling.

### Owners / files (point, do not paraphrase)

- `task-tree/references/planning.md §Placing Work` (or extracted `placement.md`) — authoritative placement: the recursive descent + leaf base case + preference ladder + burden-of-proof + positive root-task definition + cross-stage framing + the update-task lifecycle rule.
- `skills/superplan/references/consolidation.md` — survey whole-tree scope; N-way Merge-into-subtree; merge-as-default for update tasks at consolidation.
- `skills/superintegrate/SKILL.md` Consolidation Gate — whole-tree placement check; update-task merge at integration (land in the surviving post-merge location).
- `skills/superplan/SKILL.md` Entry Assessment + User Review — point at the placement owner; remove the root-biased shorthands ("nest vs. new root-level task" binary; "one per workstream"); add the placement-justification surface. Pointer, not paraphrase.
- `task-tree/restructuring-tooling` (sibling task) — safe-execution substrate: hook dep-rewire (+ agent-facing docs of that behavior), advisory placement `task check`. Merge stays manual (no command). Cross-tree logical dependency, not a frontmatter edge.

### Constraints

- Do not overwrite the approved `entry-and-placement` / `consolidation` tasks; this subtask evolves their output (it is itself an instance of the planning-stage "spin out a self-contained subtask" rule).
- Mechanisms over contingency trees; positive, behavior-shaping instructions; one source of truth per concern. Apply the CLAUDE.md DRY/Necessity gate line by line. `skill-creator` is unavailable in this environment — use the discipline encoded in root `CLAUDE.md` as the fallback.
- No new `Stage:` value (placement/consolidation/gate are orchestrator/reference concerns).

## Planner Guidance

Likely decomposes at implementation into ~3 self-contained subtasks — (a) placement burden-of-proof + cross-stage reframe, (b) the update-task lifecycle rule, (c) consolidation survey + gate whole-tree scope — but leave that decomposition to the implement/superplan pass rather than imposing it now. The lifecycle rule (b) is the load-bearing idea; (a) and (c) are the placement and backstop halves that make it stick.

## Results

Codified cross-stage placement + the update-task lifecycle into the live skill files the two approved siblings own, evolving (not overwriting) their output. The siblings' own task records are left untouched — their fold-back happens at integration, per this task's own lifecycle rule.

### What landed

**1. Authoritative placement rewrite** — originally written to `task-tree/references/planning.md §Placing Work in the Tree` (historical path — that file was deleted by `task-tree-design/01-reference-ownership`; the policy now lives in [task-tree-design.md §Placing Work by Durable Home](../../../../skills/superplan/references/task-tree-design.md)). Replaced the passive "two-step: find concern, then granularity / create a sibling on any non-exact match" procedure with an explicit **recursive descent** keyed on the framing in the objective:

- Split **leaf vs branch first**. Branch: a child covers it → descend; no child covers it → add a new child (at the root, that child is a new root-level workstream — record which child's concern was read and why it does not cover the work). Leaf: simple → update-in-place and flip `approved`→`revise`; complex → nest a subtask.
- "Create a sibling / new root-level task" is **not** a separate primitive — it is "add a child at the parent" evaluated at the root, so root misuse is controlled by the same justification requirement rather than a special case. This deletes the old "create a sibling on any non-exact match" exit that was the structural source of duplicate root tasks. Implemented exactly as the leaf/branch-primary form the dispatch specified — no flat update/nest/sibling pecking order.
- Added the **positive root-task definition** (root = whole workstream; root misuse is a *consequence* of skipping the ladder) and the **cross-stage** framing (planning, consolidation, integration all load this one section).
- Added the **update-task lifecycle** — the load-bearing rule — with the governing **asymmetric-aggressiveness / latest-state** principle, the merge-vs-spinout tradeoff, the planning-lenient / consolidation-strict rule of thumb, and the `integrate-cleanup`→`integ-workflow` worked example.

**Placement decision (cross-stage framing):** chose **in-place reframe** of §Placing Work, not extraction into a new `placement.md`. The consolidation survey and the superintegrate gate now both point at `task-tree-design.md §Placing Work by Durable Home` as the authoritative single owner — the lower-churn / DRY choice; no new file or link surface to maintain.

**2. Consolidation survey + Merge action whole-tree — [`skills/superplan/references/consolidation.md`](../../../../skills/superplan/references/consolidation.md).** Survey step 4 now compares **across levels** (each task/subtree's concern vs parent and other subtrees, via §Placing Work), not only same-level pairs — so whole-tree misplacement is visible. Step 5 + the issue table + Merge action detail now treat any **update task** as a Merge-by-default candidate, and the **Merge** action is extended from pairwise-only to **N-way merge into a subtree** (Merge+Split composite: one parent concern, distinct survivors as children, conservative status rollup, `depends_on` rewire). Merge stays **manual — no `task merge` command** — so the human controls nuance integration.

**3. Consolidation Gate whole-tree — [`skills/superintegrate/SKILL.md` §Consolidation Gate](../../../../skills/superintegrate/SKILL.md).** The gate's placement / wrong-parent check is now explicitly **whole-tree, not frontier-internal**, and ties update tasks in the frontier to merge-by-default per the create-then-merge lifecycle.

**4. Entry Assessment + User Review + User Feedback — [`skills/superplan/SKILL.md`](../../../../skills/superplan/SKILL.md).** Removed the root-biased shorthands ("nest under X vs. create a new root-level task" framed as a binary in the "Ask when unclear" line; "one per workstream" in the scope check) and pointed them at §Placing Work. Added the **placement-justification surface** to User Review (for each new task, state the concern considered and why it does not cover the work). Reframed the §User Feedback Step 2 placement decision to point at the recursive descent and the MODIFY/MERGE presumption, replacing the buried "prefer modifying existing task.md files" one-liner with a pointer to the authoritative owner.

### Cross-tree dependency note

The safe-execution + detection substrate (lossless `depends_on` rewire hook, advisory `task check --category placement`) lives in the sibling `task-tree/restructuring-tooling` task, which depends logically on this one (the detector encodes these codified rules). That edge is cross-tree and so cannot be a frontmatter `depends_on` (sibling-only) — it is the very limitation the rewire tooling works around; tracked in prose here and in that task. The consolidation N-way-merge text references that hook for same-parent rename rewires.

### Verification

- `superra task tree --root superRA` and `superra task read <this task>` both succeed (CLI unaffected — edits are skill prose).
- DRY/Necessity gate applied line by line per the dispatch (skill-creator unavailable): no `placement.md` created (would duplicate the owner already pointed-at); superplan/superintegrate edits are pointers to §Placing Work, not paraphrases; the only restated content is the one-line "update task → Merge by default" cue at each stage's entry point, kept because the alternative is forcing a redundant cross-reference load at the decision site.
- No stale "create a sibling" / two-step / same-level-only placement language remains in the touched files (grep confirms the sole surviving "same-level" mention is the corrected line that explicitly negates same-level-only scope).

## Review Notes

1. **[MINOR]** The Results promise "their fold-back happens at integration, per this task's own lifecycle rule" — that fold-back has not happened: this task and the superseded `entry-and-placement` sibling survive as standalone approved update tasks, the exact pattern this task's lifecycle rule expires at consolidation/integration. Fix: execute the merge/prune at the next consolidation gate.
