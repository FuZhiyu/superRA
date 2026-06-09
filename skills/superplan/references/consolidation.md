# Task Tree Consolidation

Load this reference when the task tree has accumulated structural debt — overlapping tasks, stale objectives, hidden dependencies, granularity mismatches — and needs a proactive cleanup pass. Loadable standalone (user asks to clean up) or via superintegrate routing.

Consolidation is structure-level cleanup, distinct from:
- `superplan §User Feedback and Changing the Task Tree` — individual reactive changes.
- `superplan/references/task-tree-design.md` §Splitting Tasks — splitting heuristics, which consolidation applies retroactively.
- `task-system/references/task-file-contract.md` §Stale Content Checklist — content-level cleanup within a task.

## When to Consolidate

Consolidation is warranted when the tree has grown through ad-hoc additions, scope pivots, or multi-session interactive work and at least two of these symptoms are present:
- Two tasks with substantially overlapping objectives or outputs
- Tasks that read another task's output without declaring `depends_on`
- Objectives superseded by another task's results or a scope change
- Tasks too large (should split) or too small (should merge with a sibling)
- A parent with a single child where the parent adds no meaningful context
- Tasks disconnected from the dependency graph when they should be connected

## Survey Protocol

Read every `task.md` and build a structural picture:

1. **Run `superra task tree`** and **`superra task dag`** for the structure, status distribution, and dependency graph.
2. **Map each task's scope:** objective, declared inputs/outputs, `depends_on`, status.
3. **Build a relationship matrix.** For each task pair, note shared inputs, shared outputs, sequential logic, and overlapping scope. Compare across levels, not only same-level pairs — misplacement and update tasks that should fold into the artifact they modify are inherently whole-tree, so test each task's and each subtree's concern against its parent and other subtrees via the recursive descent in `superplan/references/task-tree-design.md` §Placing Work by Durable Home.
4. **Identify and classify issues** from the list below. Treat any *update task* in the frontier — one whose purpose is to improve an existing task or artifact — as a **Merge** candidate by default (create-then-merge lifecycle): it folds into the task it updates rather than surviving as a standalone tree.

## Issue Classification

For each identified issue, classify the action:

| Issue | Action | What it means |
|---|---|---|
| Two or more tasks with overlapping objectives or outputs | **Merge** | Combine into one task; or, when several tasks cluster on one concern with distinct deliverables, fold them into a single parent concern with the survivors as children (N-way merge into a subtree). |
| An update task that improves an existing task or artifact | **Merge** | Fold the matured update into the task it modifies and remove the update-task directory (create-then-merge lifecycle). |
| Task A reads task B's output but no `depends_on` declared | **Link** | Add the missing dependency. |
| Objective superseded by another task's results or a scope change | **Prune** | Delete the stale task directory. |
| Task too large for independent dispatch and review | **Split** | Create subtasks under the current task. |
| Task too small to justify dispatch cost | **Merge** | Absorb into a sibling or parent. |
| Parent with a single child where the parent adds no context | **Flatten** | Absorb the child's content into the parent directory. |
| Task at the wrong level or under the wrong parent | **Restructure** | Move task to a better location in the tree. |

### Action Details

**Merge:** Two forms, both manual (there is no `task merge` command) so the human controls how the combined nuance integrates.

- *Pairwise.* Rewrite the surviving task's objective to cover both scopes (self-sufficient, not patched). Use the more conservative of the two statuses. Repoint every sibling `depends_on` that referenced the removed task. Delete the absorbed directory.
- *N-way into a subtree.* When several tasks cluster on one concern with distinct deliverables, designate one parent concern and make the survivors its children (a Merge+Split composite). Roll the parent's status up conservatively from the children, and rewire every `depends_on` across the cluster — the same-parent rename rewire comes from the `restructuring-tooling` hook; fix cross-parent edges by hand. For an *update task*, the merge target is the task it modifies: fold the matured result in and remove the update-task directory.

**Link:** Update `depends_on` frontmatter via `superra task dep add` / `superra task dep remove`. No objective rewrite needed unless the dependency changes the task's scope.

**Prune:** Delete the task directory entirely. Update siblings whose `depends_on` referenced the pruned task. If the pruned task had dependents, reassess whether those dependents' objectives still make sense.

**Split:** Create subtask directories under the too-large task. Move objective content into the subtasks; rewrite the parent's objective as a framing summary. Preserve the parent's status as the rollup of its new children.

**Flatten:** When a parent has a single child and adds no context beyond what the child carries, absorb the child's `task.md` content into the parent's `task.md`. Remove the child directory. Update any sibling `depends_on` that pointed to the child (they now point to the parent).

**Restructure:** Move the task directory to its new location. Update `depends_on` references in the old and new sibling scopes. Preserve the task's status and content.

## User Approval Gate

Consolidation changes the tree structure. Present a proposal before executing.

**Proposal format:**

1. Show the current tree (`superra task tree`).
2. Show the proposed tree (text sketch of the new structure).
3. For each change: state the action (merge/link/prune/split/flatten/restructure), identify which tasks are affected, and explain why.
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

## Execution Mechanics

After approval:

1. **Apply changes** with the task-system CLI (`superra task create` / `rename` / `dep add` / `dep remove`) plus direct edits for objective rewrites, in dependency order: links and restructures first, then merges and splits, then prunes last — so `depends_on` references are repointed before their targets disappear. Status cascading follows each action's rule in §Action Details.

2. **Verify** with `superra task tree` and `superra task dag`: no cycles, no broken `depends_on`, no orphans, structure matches the approved proposal.

3. **Sweep for stale content** per `task-system/references/task-file-contract.md` §Stale Content Checklist — consolidation often strands references in objectives and results.

4. **Commit atomically** — all changed task files in one commit titled `plan: consolidate task tree — <summary>`.

## Standalone vs Integration Use

The same protocol (survey, classify, propose, approve, execute atomically) applies in both entry paths:

**Standalone:** The user asks to clean up the tree.

**During integration:** The `superintegrate` consolidation gate (run once just before Document) routes here on a needs-a-pass verdict; a clean-enough verdict skips it. Return to Document on the consolidated tree.
