# Changing the Task Tree

Load when the task tree changes after initial authoring — whether an in-flight refinement during execution or a researcher-initiated scope change raised mid-session, mid-INTEGRATE, or after merge. Owns the materiality test and the confirm / update / reset / sweep / commit protocol that `superplan §User Feedback and Changing the Task Tree` routes to.

## Living Task Tree

**The task tree is NOT a static spec.** Work reveals surprises; the task tree evolves in place.

Distinguish two kinds of drift: (a) **agent-discovered refinements** during in-flight work (a task's approach adjusted after seeing the data, expected results tuned to early findings) — handle these as inline edits to the task's body sections per the editing discipline in `agents/implementer.md` §Editing Etiquette; (b) **researcher-initiated scope changes** mid-session (new tasks, removed tasks, methodology pivots, sample redefinition) — these MUST be routed through §User Feedback and Changing the Task Tree below.

**Results:** Each task's `## Results` section is the live findings record. See `task-tree/references/task-file-contract.md` §Results Shape for the template and two-stage lifecycle.

### `superRA/` Is the Task Tracker

`superRA/` is the authoritative task tracker — its task files and frontmatter `status:` fields are the state of record, not chat, status reports, or `TodoWrite` (a transient within-session view that does not persist). Any work that is part of the project lives in `superRA/` first; if losing a todo at session end would lose work the researcher cares about, it belongs there. When the two disagree, `superRA/` is right.

## User Feedback and Changing the Task Tree

When the task tree changes — details updated, tasks added/removed/restructured, objective shifted — follow this protocol, whether the change is raised mid-execution or after integration/merge. Update task files inline; never start a parallel tree, append an "Addendum", or leave the change in chat.

**Material (require this protocol):**

- Adding, removing, or restructuring task directories.
- Changing a task's objective.
- Changing the project-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge.
- Substantive restructure findings surfaced mid-INTEGRATE. The orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (handle as inline discovery edits per §Living Task Tree above):**

- Rewording a task objective to match what the data forced (within the same scope).
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Ask (`AskUserQuestion`) to confirm the researcher wants the change.
2. **Update `superRA/` inline:** Place, rewrite, split, merge, or remove tasks by `task-tree-design.md` §Placing Work in the Existing Tree and §Objective rewrites on scope expansion. After task edits, rewrite any field in a governing ancestor task that no longer matches the new tree.
3. **Update statuses** by orchestrator judgment, per `task-tree-design.md` §Objective rewrites on scope expansion.
4. **Sweep for stale content** per `task-tree/references/task-file-contract.md` §Stale Content Checklist.
5. **Commit atomically** — all affected task.md files + any code touched by the change, in one commit. PLAN is one multi-step phase, so its commit subject carries the sub-step in the scope per `using-superra` §Commit Hygiene: `plan(<sub-step>): <summary>`, where `<sub-step>` is `add` (tree authoring), `revise` (this update-task path), `rollup` (status rollup), or `review` (a planning-review verdict commit, which carries its `<STATE>`: `plan(review): APPROVE|REVISE — <summary>`). This update-task change is `plan(revise): <one-line scope change>`.
6. **Resume** on the affected frontier per `using-superra/references/main-agent.md` §Resuming Work.

Do not resume the in-flight task before the change is committed — it is not real until then — and do not treat an invalidated milestone as license to clear unrelated approved tasks.
