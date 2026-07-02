# Task Tree Consolidation

Load this reference when the task tree has accumulated structural debt — overlapping tasks, stale objectives, hidden dependencies, granularity mismatches, or temporary update scaffolding — and needs a proactive cleanup pass. Loadable standalone (user asks to clean up) or via the `superintegrate` Mature & Consolidate stage, which screens the tree, drives the user proposal, and dispatches an implementer to execute the actions defined here.

Consolidation distils each task: it decides what of the task's work survives and where it lands in a durable owner. Most scaffolding and dev-log detail drops once the work is integrated — a simple update task may collapse to a single inline line in its parent. The actions below choose the surviving altitude rather than carry a task over wholesale.

Consolidation is structure-level cleanup, distinct from:
- `superplan §User Feedback and Changing the Task Tree` — individual reactive changes.
- `superplan/references/task-tree-design.md` §Splitting Tasks — splitting heuristics, which consolidation applies retroactively.
- `task-tree/references/task-file-contract.md` §Stale Content Checklist — content-level cleanup within a task.

## When to Consolidate

Consolidation is warranted when the tree has grown through ad-hoc additions, scope pivots, or multi-session interactive work and at least two of these symptoms are present. During integration the bar is lower: a single surviving update task or action-verb parent is enough to require a pass, because at integration an approved update task is in the expected state to be folded — approval is the precondition for the fold (`superplan/references/task-tree-design.md` §Update-Task Lifecycle). The default is to fold scaffolding into its durable owner; the burden is to justify *keeping* a piece, not folding it.
- Two tasks with substantially overlapping objectives or outputs
- Tasks that read another task's output without declaring `depends_on`
- Objectives superseded by another task's results or a scope change
- Tasks too large (should split) or too small (should merge with a sibling)
- A parent with a single child where the parent adds no meaningful context
- Tasks disconnected from the dependency graph when they should be connected
- Temporary update tasks whose validated result now belongs in the durable task they modified
- Action-verb parents whose shipped result is now a durable concern, e.g. a "status-consolidation" parent that should merge into or become the status-model owner

## Survey Protocol

Read every `task.md` and build a structural picture:

1. **Run `superra task tree`** and **`superra task dag`** for the structure, status distribution, and dependency graph.
2. **Map each task's scope:** objective, `depends_on`, status, and whether it is temporary update scaffolding or a durable owner.
3. **Build a relationship matrix.** For each task pair, note shared inputs, shared outputs, sequential logic, and overlapping scope. Compare across levels, not only same-level pairs — misplacement and update tasks that should fold into the artifact they modify are inherently whole-tree, so test each task's and each subtree's concern against its parent and other subtrees via `superplan/references/task-tree-design.md` §Placing Work in the Existing Tree.
4. **Identify and classify issues** from the list below. Apply `superplan/references/task-tree-design.md` §Update-Task Lifecycle whole-tree: any task whose purpose is to improve an existing task or artifact folds back by default — a **Merge** into the task it modified, or a **Mature/Rename** when it has become the durable owner of a concern. Classify approved scaffolding into one of these by default; the open question is which fold, not whether to fold.

## Issue Classification

For each identified issue, classify the action. Each action sets the altitude the affected task lands at in the durable owner — from a dropped directory whose result already lives in a parent diff, through a one-line note or pointer, to a matured reader-facing narrative.

| Issue | Action | What it means |
|---|---|---|
| Two or more tasks with overlapping objectives or outputs | **Merge** | Combine into one task; or, when several tasks cluster on one concern with distinct deliverables, fold them into a single parent concern with the survivors as children (N-way merge into a subtree). |
| An update task that improves an existing task or artifact | **Merge** | Fold the surviving result into the task it modifies and remove the update-task directory (create-then-merge lifecycle). |
| An action-verb task whose validated result is now the stable owner of a concern | **Mature/Rename** | Rewrite it as the durable concern it now owns and optionally rename the directory to the stable concern name. |
| Task A reads task B's output but no `depends_on` declared | **Link** | Add the missing dependency. |
| Objective superseded by another task's results or a scope change | **Prune** | Delete the stale task directory, or rewrite the durable owner when the scope belongs there. |
| Task too large for independent dispatch and review | **Split** | Create subtasks under the current task. |
| Task too small to justify dispatch cost | **Merge** | Absorb into a sibling or parent. |
| Parent with a single child where the parent adds no context | **Flatten** | Absorb the child's content into the parent directory. |
| Task at the wrong level or under the wrong parent | **Restructure** | Move task to a better location in the tree. |
| A task's durable scope widened during the work | **Scope Expansion Rewrite** | Rewrite the objective and scope-defining fields as the current-state contract, invalidate affected downstream statuses, and remove stale delta prose. |

### Action Details

**Merge:** Two forms, both manual (there is no `task merge` command) so the human controls how the combined nuance integrates.

- *Pairwise.* Rewrite the surviving task's objective to cover both scopes (self-sufficient, not patched), widening its scope-defining detail so it describes the combined owner. Use the more conservative of the two statuses. Repoint every sibling `depends_on` that referenced the removed task. Delete the absorbed directory.
- *N-way into a subtree.* When several tasks cluster on one concern with distinct deliverables, designate one parent concern and make the survivors its children (a Merge+Split composite). Roll the parent's status up conservatively from the children, and rewire every `depends_on` across the cluster — the same-parent rename rewire comes from the `restructuring-tooling` hook; fix cross-parent edges by hand. For an *update task*, the merge target is the task it modifies: fold the surviving result into its `## Results` at the chosen altitude and remove the update-task directory.

**Mature/Rename:** Rewrite an action-verb task as the durable current-state concern it now owns, then rename the directory when the slug still names the update episode rather than the stable concern. Distil the task's `## Results` to the altitude the durable home warrants — a matured reader-facing narrative when this is where the work's narrative lives, a pointer when the task's own output *is* a document (one source of truth). Rewrite the scope-defining objective detail and repoint any sibling `depends_on` references affected by the rename. Use this for cases where an action parent should survive as the concern itself; otherwise classify it as Merge into the existing durable owner.

**Link:** Update `depends_on` frontmatter via `superra task dep add` / `superra task dep remove`. No objective rewrite needed unless the dependency changes the task's scope.

**Prune:** Delete the task directory entirely. Update siblings whose `depends_on` referenced the pruned task. If the pruned task had dependents, reassess whether those dependents' objectives still make sense.

**Split:** Create subtask directories under the too-large task. Move objective content into the subtasks; rewrite the parent's objective as a framing summary. Preserve the parent's status as the rollup of its new children.

**Flatten:** When a parent has a single child and adds no context beyond what the child carries, absorb the child's `task.md` content into the parent's `task.md`. Remove the child directory. Update any sibling `depends_on` that pointed to the child (they now point to the parent).

**Restructure:** Move the task directory to its new location. Update `depends_on` references in the old and new sibling scopes. Preserve the task's status and content.

**Scope Expansion Rewrite:** Follow `superplan/references/task-tree-design.md` §Objective rewrites on scope expansion, then remove stale `## Revision Notes`, review notes, or delta prose that no longer describes current state.

## User Approval Gate

Consolidation changes the tree structure. The proposal is authored from a whole-tree screening and presented before any execution. Under the `superintegrate` Mature & Consolidate stage the orchestrator authors it from its screening and it carries the combined maturation decision (each touched subtree's durable home, the structure change that realizes it, and its `## Results` altitude); a researcher running consolidation standalone authors the same proposal directly.

**Proposal format:**

1. Show the current tree (`superra task tree`).
2. Show the proposed tree (text sketch of the new structure).
3. For each change: state the action (merge/link/prune/split/flatten/restructure/mature-rename/scope-expansion rewrite), identify which tasks are affected, and explain why.
4. Ask for user approval before executing any changes.

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

Wait for explicit approval. A passing remark is not authorization — confirm intent if ambiguous.

The sign-off boundary is the existing one in `superplan §User Feedback and Changing the Task Tree`: material changes — pruning a task whose result a reader would expect, merging two substantive concerns, an ambiguous durable home, or a status-invalidating scope-expansion rewrite — need explicit approval and route through that protocol; routine distillation is presented as the proposed default the user can veto and otherwise executes as lifecycle. The approved proposal is the authority for structural edits.

## Execution Mechanics

Execution applies the approved proposal. Under the merged stage the orchestrator records each subtree's approved decision as `## Revision Notes` on the affected tasks and dispatches an implementer to execute them; a standalone consolidator executes its own approved proposal. Either way the steps are the same:

1. **Apply changes** with the task-tree CLI (`superra task create` / `rename` / `dep add` / `dep remove`) plus direct edits for objective rewrites, in dependency order: links and restructures first, then merges and splits, then prunes last — so `depends_on` references are repointed before their targets disappear. Status cascading follows each action's rule in §Action Details.

2. **Verify** with `superra task tree` and `superra task dag`: no cycles, no broken `depends_on`, no orphans, structure matches the approved proposal.

3. **Sweep for stale content** per `task-tree/references/task-file-contract.md` §Stale Content Checklist — consolidation often strands references in objectives and results. Remove stale delta prose after scope expansion once the objective carries the current contract.

4. **Commit atomically** — all changed task files in one commit titled `plan: consolidate task tree — <summary>`.

## Standalone vs Integration Use

The same protocol (survey, classify, propose, approve, execute atomically) applies in both entry paths:

**Standalone:** The user asks to clean up the tree. The consolidator runs every step itself — survey, author the proposal, get approval, execute.

**During integration:** `superintegrate/references/mature-consolidate.md` owns the choreography — it screens the whole touched tree once after Integrate closes, drives the distillation question that always fires, records decisions as `## Revision Notes`, and dispatches an implementer who applies the actions and mechanics defined here. The implementer executes the structural fold and the `## Results` altitude together on final results.
