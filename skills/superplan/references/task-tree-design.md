# Task Tree Design

Load this reference when designing, changing, consolidating, or integration-checking a `superRA/` task tree. The file contract for `task.md` lives in `skills/task-tree/references/task-file-contract.md`.

## Writing Objectives and Planner Guidance

`## Objective` is the authoritative implementation and review contract. It describes what success looks like, not optional routes for getting there.

**Include:**
- The goal — what the task should produce or verify.
- Relevant conventions — naming, paths, units, variable definitions.
- Constraints — what to avoid and what to preserve.
- User or methodology decisions the implementer must preserve.
- Input/output expectations — what data comes in and what form results take.
- Fixed `script` / `input` / `output` expectations when they define scope.
- Validation criteria — what must be true for the task to be complete.

The implementer's working context is the assembled set of: auto-loaded `CLAUDE.md` / `AGENTS.md` (the project-level ones plus any nested in a directory the agent reads), manifest-loaded skills, the assigned task plus its ancestor chain via `superra task read`, and on-demand directory walking when a touched file needs a convention the chain does not cover. The objective's job is to make that assembled set *sufficient* — point into it so the right standing context and the right files are reachable — not to reproduce context that already lives there. See §Context Distillation for the point-vs-distill choice.

`## Planner Guidance` is optional and advisory. Use it for suggested routes, candidate files, prior exploration notes, likely sequence, implementation hints, and other context the implementer may adapt or ignore while satisfying `## Objective`.

**Steps vs. subtasks vs. suggestions:**
- Necessary steps that need independent tracking and review become subtasks.
- Suggested approaches belong in `## Planner Guidance`, e.g. "Consider using a left join on fund_id x date."
- Do not prescribe implementation steps unless the step itself is the deliverable.
- Do prescribe validation criteria.

Existing task files without `## Planner Guidance` remain valid. Do not bulk-migrate old objectives automatically; split objective/guidance opportunistically when a task is created or materially rewritten.

## Context Distillation

Scoped context lives on the lowest ancestor whose subtree it governs. The task tree is recursive: any task can carry context for its subtree, and the top task is not a special semantic owner. When a convention, constraint, or piece of context changes what an implementation or review agent does, it belongs in the `## Objective` of the lowest task whose subtree it applies to, under a scoped `### Context`, `### Conventions`, or `### Constraints` subsection — but "belongs in the objective" means the agent must reach it from there, not that its text must be copied there.

For each behavior-changing convention, choose how to put it in reach by where it already lives. Point over copy: when the convention already lives somewhere the agent reaches, a pointer keeps the task readable and leaves one source of truth, while a copy is a second version that drifts from the original as either changes. Copy only when there is no reachable source to point at.

1. **Already in the agent's standing context** — auto-loaded `CLAUDE.md` / `AGENTS.md` (project-level or nested in a directory the agent reads), or a manifest-loaded skill. Point with a self-orienting line plus the path/anchor. Do not copy.
2. **Reachable but not standing, or living in one coherent doc** (e.g. a data-directory `README`). Point with a self-orienting line plus the location, so both the human reader and the implementer's on-demand directory walk land on it.
3. **Scattered across multiple files or not reliably discoverable.** Distill a behavior-stating summary into the scoped subsection, with a source pointer. Write the behavior to follow, not a verbatim excerpt; stamp the walk date.
4. **Task-specific context that lives nowhere else.** State it inline; there is no tradeoff.

A **self-orienting line states the convention's substance** — the gist of what it requires and how it bears on this task — so the reviewer grasps it without opening the link; the link carries full detail. A bare "see X" that names only a location is not self-orienting. This concise-substance line is what lets a pointer satisfy human readability in tiers 1–2 without reproducing the full rule text. Reserve inline reproduction of rule *text* for context that is task-specific or is itself the thing under review.

Walk the project guidance docs (`CLAUDE.md` / `AGENTS.md` / `README.md`, and data-directory `README.md`s) to classify each relevant convention into a tier. When the walk found no relevant convention for the subtree, say so explicitly and name the out-of-scope paths.

## Splitting Tasks

A task should be the right size for independent dispatch and review.

**Split when:**
- Each child has a meaningful objective, evidence trail, and review verdict.
- Different concerns, data sources, artifact families, or domain skills apply.
- Independent branches could run in parallel or be reviewed by different standards.
- Serial work has peer review units where downstream correctness depends on a completed upstream output or finding.

**Do not split when:**
- Steps are trivially sequential with no independent review value.
- The unit is too small to justify dispatch cost.
- The split artificially decomposes one logical operation.

`depends_on` records prerequisite order among sibling review units. It does not justify a split by itself: choose the split for review value, then add dependencies for execution order. A branch may be serial, parallel, or mixed.

**Right-sizing test:** Can you describe the task's success criteria in one sentence? If yes, it is the right size. If the review would be trivial, it is too small. If the description needs three paragraphs, it may need splitting.

Name tasks by their goal: "Merge holdings with characteristics," not "Run merge script."

## Placing Work by Durable Home

Place work by the durable home that should own the result after integration: the implementation surface, artifact family, and future maintenance concern. Historical provenance is evidence, not ownership. Widen an existing owner before adding breadth; an existing objective is an editable current-state contract, not a closed historical scope.

Branch for independent review value, then use `depends_on` only for prerequisite ordering. Parent objectives are inherited shared context. Dependent sibling tasks are ordered peers whose results are read only when the downstream objective needs them.

The presumption is modify or merge the task that already owns the concern. Creating a new task — especially a root-level task — is the justified exception.

Use motivating cases as evidence for the general rule: a semantic `task move` command belongs under the CLI command surface that will maintain it, while its restructuring provenance belongs in context; a niche status-model update such as `postponed-status` belongs under the status model / task-tree concern that owns it, not as a level-1 workstream.

### Recursive descent

Walk from the root. Descend into a node only because the work relates to that node's concern, so at every node the question is not whether the work belongs there but how deep it lands. Split on leaf vs. branch first.

**Branch** (a node with children):

- A child's concern covers the work: descend into that child and recurse.
- An existing child owns the durable concern but its objective is too narrow: widen that child objective, add `## Revision Notes` when the change is non-obvious, and recurse.
- Existing and new work are peers under an unrepresented broader concern: create the broader parent, move both under it, and give the parent the shared objective context.
- No child covers the work: add a new child under this node. At the root, that child is a new root-level workstream; record which existing child's concern you read and why it does not cover the work.

**Leaf** (a node with no children):

- Simple extension: update it in place and flip its status from `approved` to `revise`. Rewrite its objective to be self-sufficient with both old and new scope.
- Complex extension: nest a subtask under it.

A sibling is just a new child of the shared parent. There is no "unrelated at the leaf" case: you reach a leaf only by descending through related concerns.

### Objective rewrites on scope expansion

When scope expands, rewrite the owning `## Objective` as the current-state contract for the full widened concern. Include the original durable context still needed for implementation and review; do not leave the new scope as a patch note. Add `## Revision Notes` when the change is non-obvious, substantive, or invalidates approved work.

For simple changes, reopen the existing owning task or affected tasks, rewrite objectives, add revision notes, and reset affected approved tasks plus transitive downstream dependents to `not-started` by orchestrator judgment so they re-enter the frontier. For complex changes, create a temporary child under the durable home so implementation and review have their own evidence trail.

### Root-task definition

A root-level task is a whole workstream or project. A narrow feature related to an existing workstream nests by the descent above and cannot land at root unless it is genuinely unrelated to everything in the tree.

### Parent and sibling context

Put durable shared assumptions, conventions, and constraints on the lowest parent whose subtree inherits them. A dependent sibling is an ordered peer, not inherited context: write the downstream objective so it names the upstream output, finding, sample, variable, or decision it consumes.

## Update-Task Lifecycle

An update task — one whose purpose is to improve or modify an existing task or artifact — has a stage-dependent disposition. Planning is lenient: a complex fix may be spun out as its own task. Consolidation and integration are strict: the fix folds back into the task it modified.

- **Planning stage:** for a substantial update, create a self-contained subtask under the owning concern with a full, dispatchable objective. Do not merge into the target before the change exists.
- **Consolidation / Integration stage:** merge the update task into the task it updates — fold the matured result into the target or parent and remove the update-task directory.

At integration, preserve validated findings in the durable owning task's `## Results`, update the owning objective if the scope changed, and remove the temporary update task. When an action-named parent such as "consolidation" becomes the long-lived owner of a concern, rename or rewrite it to the durable concern it now represents.

Anti-patterns: creating a new task for a scope extension of an existing task; landing a narrow improvement at the root; nesting three or more levels deep without review value; leaving an update task standing as a separate tree after the change has shipped.

## Retroactive Task-Tree Creation

When creating `superRA/` from existing work:

1. Read the existing code and results to understand what was done.
2. Create the top `task.md` with the project objective and any project-wide scoped conventions.
3. Create child tasks that mirror the logical structure of the existing work, not the file layout.
4. Set status to `approved` for tasks whose work is complete and verified.
5. Set status to `implemented` for tasks whose work is done but not yet reviewed.
6. Populate `## Results` from existing findings.
7. Run `superra dashboard` to launch the dashboard.
