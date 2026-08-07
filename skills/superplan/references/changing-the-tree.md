# Changing the Task Tree

Load when the task tree changes after initial authoring — an in-flight refinement during execution, or a researcher-initiated scope change raised mid-session, mid-INTEGRATE, or after merge. Owns the materiality test and the confirm / update / reset / sweep / commit protocol.

## Living Task Tree

**The task tree is NOT a static spec.** Work reveals surprises; the tree evolves in place.

Two kinds of drift:

- **Agent-discovered refinements** during in-flight work — a task's approach adjusted after seeing the data, expected results tuned to early findings. Rewrite task-body sections in place per `superRA:communicate`.
- **Researcher-initiated scope changes** mid-session — new tasks, removed tasks, methodology pivots, sample redefinition. Route through §User Feedback and Changing the Task Tree.

**Results:** each task's `## Results` is the live findings record — inclusion test, subsection menu, two-stage lifecycle in `task-tree/references/task-file-contract.md` §Results Shape.

### `superRA/` Is the Task Tracker

`superRA/` task files and their `status:` fields are the state of record — not chat, status reports, or `TodoWrite` (a transient within-session view). Project work lives in `superRA/` first: if losing a todo at session end would lose work the researcher cares about, it belongs there. On disagreement, `superRA/` is right.

## User Feedback and Changing the Task Tree

Update task files inline; never start a parallel tree, append an "Addendum", or leave the change in chat.

**Material (require this protocol):**

- Adding, removing, or restructuring task directories.
- Changing a task's objective.
- Changing the project-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge.
- Substantive restructure findings surfaced mid-INTEGRATE — the orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (inline discovery edits per §Living Task Tree):**

- Rewording an objective to match what the data forced, within the same scope.
- Adjusting expected results based on early findings.
- Refining methodology details the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization — confirm with `AskUserQuestion`. Decisions the change leaves unsettled run through `superplan §Grilling`.
2. **Update `superRA/` inline.** Place, rewrite, split, merge, or remove tasks by `task-tree-design.md` §Placing Work in the Existing Tree and §Objective rewrites on scope expansion. Then rewrite any governing-ancestor field that no longer matches the new tree.
3. **Update statuses** by orchestrator judgment, per `task-tree-design.md` §Objective rewrites on scope expansion.
4. **Sweep for stale content** per `task-tree/references/task-file-contract.md` §Stale Content Checklist.
5. **Commit atomically** — all affected task.md files plus any code the change touched, one commit. PLAN is one multi-step phase, so the subject carries the sub-step in scope per `using-superra` §Commits: `plan(<sub-step>): <summary>`, `<sub-step>` ∈ `add` (tree authoring), `revise` (this path), `rollup` (status rollup), `review` (a planning-review verdict commit, which carries its `<STATE>`: `plan(review): APPROVE|REVISE — <summary>`). This path commits `plan(revise): <one-line scope change>`.
6. **Resume** on the affected frontier per `using-superra/references/main-agent.md` §Resuming Work.

Do not resume the in-flight task before the change is committed — it is not real until then. An invalidated milestone is not license to clear unrelated approved tasks.
