# Task Tree Consolidation

Load on structural debt — overlapping tasks, stale objectives, hidden dependencies, granularity mismatches, temporary update scaffolding. Entered standalone (user asks to clean up) or via the `superintegrate` Mature & Consolidate stage.

Consolidation distils each task: what of its work survives, and where it lands in a durable owner. Most scaffolding and dev-log detail drops once the work is integrated — a simple update task may collapse to one inline line in its parent. Each action below picks the surviving altitude rather than carrying a task over wholesale.

Structure-level cleanup, distinct from:
- `superplan §User Feedback and Changing the Task Tree` — individual reactive changes.
- `superplan/references/task-tree-design.md` §Splitting Tasks — splitting heuristics, which consolidation applies retroactively.
- `task-tree/references/task-file-contract.md` §Stale Content Checklist — content-level cleanup within a task.

## When to Consolidate

Standalone bar: at least two symptoms below, after ad-hoc additions, scope pivots, or multi-session interactive work. Integration bar: one surviving update task or action-verb parent — an approved update task is already in the state to be folded (`task-tree-design.md` §Update-Task Lifecycle). Default is folding scaffolding into its durable owner; justify *keeping* a piece, not folding it.

- Two tasks with substantially overlapping objectives, outputs, or edit surfaces
- Tasks that read another task's output without declaring `depends_on`
- Objectives superseded by another task's results or a scope change
- Tasks too large (should split) or too small (should merge with a sibling)
- A parent with a single child where the parent adds no meaningful context
- Tasks disconnected from the dependency graph when they should be connected
- The same finding, number, or figure caption in more than one task's `## Results`, or a `## Results` restating a document, diff, or commit body it could point at
- Temporary update tasks whose validated result now belongs in the durable task they modified
- Action-verb parents whose shipped result is now a durable concern, e.g. a "status-consolidation" parent that should merge into or become the status-model owner

## Survey Protocol

Read every `task.md` and build a structural picture:

1. **Run `superra task tree` and `superra task dag`** for structure, status distribution, dependency graph.
2. **Map each task's scope:** objective, `depends_on`, status, and whether it is temporary update scaffolding or a durable owner.
3. **Build a relationship matrix.** Per task pair: shared inputs, shared outputs, sequential logic, overlapping scope. Compare across levels, not only same-level pairs — misplacement and update tasks are inherently whole-tree, so test each task's and each subtree's concern against its parent and other subtrees via `task-tree-design.md` §Placing Work in the Existing Tree.
4. **Identify and classify issues** from the table below, applying `task-tree-design.md` §Update-Task Lifecycle whole-tree: any task whose purpose is to improve an existing task or artifact folds back by default — **Merge** into the task it modified, or **Mature/Rename** when it has become the durable owner of a concern. The open question is which fold, not whether to fold.

## Issue Classification

Each action sets the altitude the affected task lands at in the durable owner — from a dropped directory whose result already lives in a parent diff, through a one-line note or pointer, to a matured reader-facing narrative.

| Issue | Action | What it means |
|---|---|---|
| Two or more tasks with overlapping objectives, outputs, or edit surfaces | **Merge** | Combine into one task; or, when several tasks cluster on one concern with distinct deliverables, fold them into a single parent concern with the survivors as children (N-way merge into a subtree). |
| An update task that improves an existing task or artifact | **Merge** | Fold the surviving result into the task it modifies and remove the update-task directory (create-then-merge lifecycle). |
| An action-verb task whose validated result is now the stable owner of a concern | **Mature/Rename** | Rewrite it as the durable concern it now owns and optionally rename the directory to the stable concern name. |
| Task A reads task B's output but no `depends_on` declared | **Link** | Add the missing dependency. |
| Objective superseded by another task's results or a scope change | **Prune** | Delete the stale task directory, or rewrite the durable owner when the scope belongs there. |
| Task too large for independent execution and review | **Split** | Create subtasks under the current task. |
| Task too small to justify its own contract, results record, and verdict | **Merge** | Absorb into a sibling or parent. |
| Parent with a single child where the parent adds no context | **Flatten** | Absorb the child's content into the parent directory. |
| Task at the wrong level or under the wrong parent | **Restructure** | Move task to a better location in the tree. |
| A task's durable scope widened during the work | **Scope Expansion Rewrite** | Rewrite the objective and scope-defining fields as the current-state contract, invalidate affected downstream statuses, and remove stale delta prose. |

### Action Details

**Merge:** two forms, both manual (there is no `task merge` command) so the human controls how the combined nuance integrates.

- *Pairwise.* Rewrite the surviving objective to cover both scopes — self-sufficient, not patched — widening its scope-defining detail to describe the combined owner. Take the more conservative of the two statuses. Repoint every sibling `depends_on` that referenced the removed task. Delete the absorbed directory.
- *N-way into a subtree.* Designate one parent concern and make the survivors its children (a Merge+Split composite). Roll the parent's status up conservatively from the children; rewire every `depends_on` across the cluster — the `restructuring-tooling` hook handles same-parent rename rewires, cross-parent edges by hand. For an *update task*, the merge target is the task it modifies: fold the surviving result into its `## Results` at the chosen altitude and remove the update-task directory.

**Mature/Rename:** rewrite an action-verb task as the durable current-state concern it now owns; rename the directory when the slug still names the update episode. Distil its `## Results` to the altitude the durable home warrants — a matured reader-facing narrative where the work's narrative lives, a pointer when the task's own output *is* a document (one source of truth). Rewrite the scope-defining objective detail and repoint sibling `depends_on` references affected by the rename. Use where an action parent should survive as the concern itself; otherwise Merge into the existing durable owner.

**Link:** update `depends_on` via `superra task dep add` / `superra task dep remove`. Objective rewrite only when the dependency changes the task's scope.

**Prune:** delete the task directory. Update siblings whose `depends_on` referenced it. Had dependents: reassess whether their objectives still make sense.

**Split:** create subtask directories under the too-large task. Move objective content into the subtasks; rewrite the parent's objective as a framing summary. Parent status becomes the rollup of its new children.

**Flatten:** absorb the single child's `task.md` content into the parent's, remove the child directory, repoint sibling `depends_on` that pointed to the child.

**Restructure:** move the task directory. Update `depends_on` in the old and new sibling scopes. Status and content survive.

**Scope Expansion Rewrite:** follow `task-tree-design.md` §Objective rewrites on scope expansion, then remove stale `## Revision Notes`, review notes, or delta prose.

## User Approval Gate

Standalone: author and approve the proposal before execution. During INTEGRATE: Protect already supplies the result and durable-home choices, so Mature & Consolidate applies the structural fold in recoverable commits and its reviewer derives the temporary refactoring task; Integrate owns the combined researcher gate.

**Proposal format:**

1. Current tree (`superra task tree`).
2. Proposed tree (text sketch).
3. Per change: the action (merge/link/prune/split/flatten/restructure/mature-rename/scope-expansion rewrite), affected tasks, why.
4. Ask for user approval before executing.

Example:

```text
The task tree has accumulated some structural debt. Here is my consolidation proposal:

Current tree:
<output of superra task tree>

Proposed changes:
1. [Merge] "01-load-raw" + "02-load-clean" -> "01-load" — both load the same
   source file; 02 just applies filters that belong in the same task.
2. [Prune] "04-old-approach" — superseded by 05-revised-approach; no other task
   depends on it.
3. [Link] "06-regression" depends on "03-merge" but does not declare it.

Proposed tree after consolidation:
<text sketch>

Should I proceed with all changes, a subset, or none?
```

Standalone: wait for explicit approval.

## Execution Mechanics

Choices come from Protect during INTEGRATE (edits land before the combined review) or from the approved proposal standalone. Mechanics are the same:

1. **Apply changes** with the task-tree CLI (`superra task create` / `rename` / `dep add` / `dep remove`) plus direct edits for objective rewrites, in dependency order: links and restructures first, then merges and splits, then prunes last — so `depends_on` references are repointed before their targets disappear. Status cascading follows each action's rule in §Action Details.
2. **Verify** with `superra task tree` and `superra task dag`: no cycles, no broken `depends_on`, no orphans, structure matches the approved proposal.
3. **Sweep for stale content** per `task-tree/references/task-file-contract.md` §Stale Content Checklist — consolidation strands references in objectives and results. Remove stale delta prose once the objective carries the current contract.
4. **Commit recoverably** — all changed task files in one commit titled `plan: consolidate task tree — <summary>` standalone, or the `integrate(mature): …` series owned by Mature & Consolidate.

## Standalone vs Integration Use

**Standalone:** the consolidator runs every step itself — survey, proposal, approval, execution.

**During integration:** `superintegrate/references/mature-consolidate.md` materializes and reviews the permanent documentation, structural fold, and `## Results` maturation after Sync, then derives the temporary refactoring task. `superintegrate/references/integrate.md` runs the combined researcher gate and executes the approved work.
