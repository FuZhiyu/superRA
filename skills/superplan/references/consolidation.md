# Task Tree Consolidation

Load this reference when the task tree has accumulated structural debt — overlapping tasks, stale objectives, hidden dependencies, granularity mismatches — and needs a proactive cleanup pass. Loadable standalone (user asks to clean up) or via superintegrate routing.

Consolidation is structure-level cleanup. It complements but does not replace:
- `superplan §User Feedback and Changing the Task Tree` — individual reactive changes to the tree.
- `superplan §Splitting Tasks` / `task-system/references/planning.md §Splitting Tasks` — structural heuristics applied during planning; consolidation applies them retroactively.
- `task-system/references/planning.md §Stale Content Checklist` — content-level cleanup within existing tasks.

## When to Consolidate

Consolidation is warranted when the tree has grown through ad-hoc additions, scope pivots, or multi-session interactive work and at least two of these symptoms are present:
- Two tasks with substantially overlapping objectives or outputs
- Tasks that read another task's output without declaring `depends_on`
- Objectives superseded by another task's results or a scope change
- Tasks too large (should split) or too small (should merge with a sibling)
- A parent with a single child where the parent adds no meaningful context
- Tasks disconnected from the dependency graph when they should be connected

## Survey Protocol

Read every `task.md` in the tree and build a structural picture:

1. **Run `superra task tree`** to see the current structure and status distribution.
2. **Run `superra task dag`** to see the dependency graph.
3. **Map each task's scope:** objective, declared inputs/outputs, `depends_on`, status.
4. **Build a relationship matrix:** For each pair of tasks at the same level, note shared inputs, shared outputs, sequential logic, and overlapping scope.
5. **Identify issues** from the list below and classify each.

## Issue Classification

For each identified issue, classify the action:

| Issue | Action | What it means |
|---|---|---|
| Two tasks with overlapping objectives or outputs | **Merge** | Combine into one task. Rewrite the objective to cover both scopes. |
| Task A reads task B's output but no `depends_on` declared | **Link** | Add the missing dependency. |
| Objective superseded by another task's results or a scope change | **Prune** | Delete the stale task directory. |
| Task too large for independent dispatch and review | **Split** | Create subtasks under the current task. |
| Task too small to justify dispatch cost | **Merge** | Absorb into a sibling or parent. |
| Parent with a single child where the parent adds no context | **Flatten** | Absorb the child's content into the parent directory. |
| Task at the wrong level or under the wrong parent | **Restructure** | Move task to a better location in the tree. |

### Action Details

**Merge:** Rewrite the surviving task's objective to cover both scopes (self-sufficient, not patched). Use the more conservative status of the two tasks. Update all sibling `depends_on` references that pointed to the removed task. Delete the absorbed task's directory.

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

1. **Apply changes** using the task-system CLI tools (`superra task create`, `superra task rename`, `superra task dep add` / `superra task dep remove`) and direct file edits for objective rewrites. Apply in dependency order: links and restructures first, then merges and splits, then prunes last (so `depends_on` references are updated before the referenced tasks disappear).

2. **Status cascading:**
   - Merge: use the more conservative status of the two tasks.
   - Restructure / Flatten: preserve statuses where possible.
   - Prune: clear `depends_on` references in siblings; reassess dependent tasks' objectives.
   - Split: parent status becomes the rollup of its new children.

3. **Verify the result:**
   ```bash
   # Check tree structure
   superra task tree --root superRA
   # Check for cycles and broken dependencies
   superra task dag --root superRA
   ```
   Confirm: no cycles, no broken `depends_on`, no orphans with missing links, structure matches the approved proposal.

4. **Sweep for stale content** per `task-system/references/planning.md §Stale Content Checklist`. Consolidation often creates stale references in objectives and results — rewrite them in place.

5. **Commit atomically** — all changed task files in one commit:
   ```
   plan: consolidate task tree — <one-line summary of changes>
   ```

6. **Launch the dashboard** if needed (`superra dashboard --root superRA`).

## Standalone vs Integration Use

**Standalone:** The user asks to clean up the tree at any time. Load this reference, run the survey, propose, and execute.

**During integration:** The `superintegrate` consolidation gate, run once just before Document, is the concrete trigger. Its mandatory assessment routes here for the cleanup pass only on a needs-a-pass verdict; a clean-enough verdict skips it. Run the protocol, then return to Document on the consolidated tree.

In both cases, the same protocol applies: survey, classify, propose, get approval, execute atomically.
