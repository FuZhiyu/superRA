# Task Tree Design

Load when designing, changing, consolidating, or integration-checking a `superRA/` task tree. The `task.md` file contract lives in `skills/task-tree/references/task-file-contract.md`.

## Writing Objectives and Details

`## Objective` is the contract — with the user at planning time, with the implementer and reviewer at dispatch. It states what must be true when the task is done, and nothing else. Keep it short: a goal statement (often a close paraphrase of the user's request) plus a few binding bullets, following `superRA:communicate`. The same contract binds `## Details` and every other planning artifact.

Sort each line by the binding-versus-information test (`task-tree/references/task-file-contract.md` §Task Anatomy). Four kinds of line are binding:
- **The goal** — what the task must produce or verify, naming the artifacts that define its scope.
- **Decisions** — user or methodology choices that must be preserved.
- **Constraints** — what to avoid, what to keep intact.
- **Validation criteria** — what must be checked for the task to be complete.

The artifacts the goal names are the task's scope. **Mark a deliberately open-ended task as open-ended** — explore the space, propose options, find whatever is there — the implementer treats an unmarked objective as closed and delivers exactly what it names.

Binding conventions that live elsewhere enter as pointers, not prose (§Context Distillation). An objective outgrowing a short paragraph plus its must-bullets: either the task needs splitting (§Splitting Tasks), or the excess is information and belongs in `## Details`. Still-rejectable bullets are neither — a one-edit-surface task carries a binding bullet per concern it serves.

The implementer's working context is the assembled set of: auto-loaded `CLAUDE.md` / `AGENTS.md` (project-level plus any nested in a directory it reads), manifest-loaded skills, the assigned task and its ancestor chain via `superra task read`, and on-demand directory walking. The objective makes that set *sufficient* — pointing into it so the right standing context and files are reachable — rather than reproducing it.

`## Details` is the planner's information handoff: what planning discovered that the implementer would otherwise re-derive — candidate files and their roles, data locations and quirks, the suggested route and why, known dead ends. Any route satisfying `## Objective` is acceptable.

Work whose result is high-stakes or hard to verify from its own output: say so here, with the review tier and focuses you would want. Whoever executes decides on the day (`using-superra/references/main-agent.md` §Deciding on Review) — never schedule review by writing it into the tree as a task.

A line belongs in details only if it is task-specific and was learned during planning. Holds for any task in this domain, or already in the implementer's standing context: delete. Nothing qualifies: omit the section.

**Steps vs. subtasks vs. suggestions:**
- Necessary steps needing independent tracking and review become subtasks.
- Suggested approaches go in `## Details`, e.g. "Consider using a left join on fund_id x date."
- No implementation steps unless the step itself is the deliverable.
- Do prescribe validation criteria.

Task files without `## Details` remain valid — split objective/details opportunistically on creation or material rewrite, never as a bulk migration.

## Context Distillation

Scoped context lives on the lowest ancestor whose subtree it governs. The tree is recursive: any task can carry context for its subtree; the top task is not a special semantic owner. A convention, constraint, or context that changes what an implementation or review agent does belongs in the `## Objective` of the lowest task whose subtree it applies to, under a scoped `### Context`, `### Conventions`, or `### Constraints` subsection — meaning the agent must *reach* it from there, not that its text is copied there.

**Point over copy.** A copy is a second version that drifts; copy only when there is no reachable source to point at. Choose the tier by where the convention already lives:

1. **In the agent's standing context** — auto-loaded `CLAUDE.md` / `AGENTS.md`, or a manifest-loaded skill. Point with a self-orienting line plus path/anchor.
2. **Reachable but not standing, or in one coherent doc** (e.g. a data-directory `README`). Point with a self-orienting line plus the location, so both the human reader and the implementer's directory walk land on it.
3. **Scattered across files or not reliably discoverable.** Distill a behavior-stating summary into the scoped subsection with a source pointer — the behavior to follow, not a verbatim excerpt. Stamp the walk date.
4. **Task-specific, living nowhere else.** State it inline.

A **self-orienting line states the convention's substance** — what it requires and how it bears on this task — so the reviewer grasps it without opening the link; the link carries full detail. A bare "see X" naming only a location is not self-orienting. Tier 4 already covers when to state text inline; the one addition here is content under review itself.

Walk the project guidance docs (`CLAUDE.md` / `AGENTS.md` / `README.md`, and data-directory `README.md`s) to tier each relevant convention. No relevant convention for the subtree: say so explicitly and name the out-of-scope paths.

## Splitting Tasks

Size each task for independent execution and review.

**Split when:**
- Each child has a meaningful objective, evidence trail, and review verdict.
- Different concerns land in different artifacts, or different data sources or domain skills apply.
- Independent branches could run in parallel or be reviewed by different standards.
- Serial work has peer review units where downstream correctness depends on a completed upstream output or finding.

**Do not split when:**
- Steps are trivially sequential with no independent review value.
- The unit is too small to justify its own contract, results record, verdict, and researcher reading time — a fixed cost paid in every execution mode.
- The split artificially decomposes one logical operation.
- The children would edit the same files or reload the same context — one edit surface is one task, however many concerns it serves.

`depends_on` records prerequisite order among sibling review units; it does not justify a split. Choose the split for review value, then add dependencies for execution order. A branch may be serial, parallel, or mixed.

**Right-sizing test:** success criteria in one sentence — right size. Review would be trivial — too small. Description needs three paragraphs — may need splitting. Two siblings whose success criteria read naturally as one sentence together — one task.

Name tasks by goal: "Merge holdings with characteristics," not "Run merge script."

## Placing Work in the Existing Tree

Place each identified objective by walking down from the top-level tasks, preferring depth over breadth: update existing tasks over creating new ones.

### Recursive descent into the most related tasks

Start among the top-level tasks under `superRA/` — siblings whether or not an umbrella task groups them — and walk down.

Current node is a **branch** (has children, including the top-level task set itself):
- Covered by an existing child's objective: descend and recurse.
- Related but the child's objective is too narrow: widen the child's objective, add `## Revision Notes` when the change is non-obvious, then descend and recurse.
- Existing and new work are peers under an unrepresented broader concern: create the broader parent, move both under it, give the parent the shared objective context.
- No related child: create a new subtask under this node (a new top-level task when the node is the top-level set) — record which existing child's concern you read and why it does not cover the work.

Current node is a **leaf**:
- Simple extension: update in place.
- Complex extension: nest a subtask under it.

### Objective rewrites on scope expansion

Rewrite the owning `## Objective` as the current-state contract for the full widened concern, carrying the original durable context still needed for implementation and review. Never leave the new scope as a patch note. Add `## Revision Notes` when the change is non-obvious, substantive, or invalidates approved work.

The rewrite trims as well as adds: re-run the rejection test over every carried-forward line, deleting what the widened concern no longer makes rejectable and what the new scope made redundant. A folded-in researcher decision is stated as the current contract, never as a dated "per user decision" note — git carries the date.

Simple changes: reopen the owning or affected tasks and rewrite objectives with revision notes. Flip a directly widened `approved` task to `revise` so it re-enters the frontier; reset transitive downstream dependents whose inputs or assumptions shift to `not-started` by orchestrator judgment. Complex changes: create a temporary child under the durable home so implementation and review get their own evidence trail.

### Parent and sibling context

Durable shared assumptions, conventions, and constraints go on the lowest parent whose subtree inherits them. A dependent sibling is an ordered peer, not inherited context: write the downstream objective so it names the upstream output, finding, sample, variable, or decision it consumes.

## Update-Task Lifecycle

An update task — one whose purpose is to improve or modify an existing task or artifact — has a stage-dependent disposition.

- **Planning stage** (lenient): for a substantial update, create a self-contained subtask under the owning concern with a full, dispatchable objective. Do not merge into the target before the change exists.
- **Consolidation / Integration stage** (strict): merge the update task into the task it updates — fold the matured result into the target or parent and remove the update-task directory.

At integration, preserve validated findings in the durable owning task's `## Results`, update the owning objective if the scope changed, and remove the temporary update task. An action-named parent such as "consolidation" that has become the long-lived owner of a concern gets renamed or rewritten to that concern.

Anti-patterns: a new task for a scope extension of an existing task; a narrow improvement landed as a new top-level task instead of nested under the concern it extends; three or more levels deep without review value; an update task left standing as a separate tree after the change shipped.

## Retroactive Task-Tree Creation

Creating `superRA/` from existing work:

1. Read the existing code and results.
2. Place each logical unit by the §Placing Work in the Existing Tree descent, mirroring the logical structure of the work, not the file layout.
3. `approved` for work complete and verified.
4. `implemented` for work done with the approval decision still open.
5. Populate `## Results` from existing findings.
