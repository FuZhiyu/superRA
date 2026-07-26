# Task File Contract

Load this reference when you need the `task.md` file contract: frontmatter, body sections, status/dependency mechanics, inherited context rendering, results shape, stale-content cleanup, or figure embedding.

Tree-design judgment — objective writing, splitting, placement, durable homes, update-task lifecycle, context distillation, and retroactive task-tree creation — lives in `skills/superplan/references/task-tree-design.md`.

## Tree Shape

`superRA/` holds top-level tasks as direct subdirectories, each with its own `task.md`. An umbrella `superRA/task.md` is optional: add one only when a shared `## Objective` / `### Context` genuinely spans every top-level task, per `task-tree-design.md` §Context Distillation's lowest-ancestor rule. When present, the umbrella is an ordinary task like any other — not a privileged one.

"Top-level task" describes position only (no parent), not required scope: a top-level task may be a leaf or a branch, narrow or broad, the same as any nested task.

## Task Anatomy

Every `task.md` — top-level, branch, or leaf — uses the same frontmatter and body sections. The tree is recursive: a task frames its own subtree; an umbrella task, when one exists, frames the whole project only because its subtree is everything.

The frontmatter field set is **closed**: `title`, `status`, `depends_on`. Any other key is discarded the next time a CLI mutation rewrites the file (including automatic ancestor-status rollups), so do not store custom metadata in frontmatter — put it in a body section instead.

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`, `postponed`. Co-owned by implementer and reviewer for the dispatch lifecycle: implementer owns transitions up to `implemented` (and `revise` to `implemented` on fix rounds); reviewer owns `implemented` to `revise`, `implemented` to `approved`, and `approved` to `revise` during integration (when integration review surfaces issues in a previously approved task). Replan transitions — flipping a widened `approved` task to `revise`, resetting downstream dependents — are planner judgment owned by `superplan/references/task-tree-design.md` §Objective rewrites on scope expansion. `archived` and `postponed` are scope decisions set by the orchestrator / researcher, not dispatch verdicts: an `archived` task is treated as resolved/removed so its dependents proceed, while a `postponed` task is parked off the frontier and blocks its dependents until resumed (set it back to `not-started`). Exception: review-only trees (e.g. writing-workflow review lanes) skip the implementer states entirely — tasks go directly from `not-started` to `revise` or `approved` as the reviewer sets them.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically. Dependent siblings are ordered peers, not inherited context: a dependency's `## Results` is read only when the downstream task's objective needs it.
- **`## Objective`** — planner-owned: the task's goal plus any scoped `### Context` / `### Conventions` / `### Constraints` its subtree inherits. Implementers read it but do not rewrite it.
- **`## Planner Guidance`** — planner-owned, optional; the planner's information handoff — findings from planning plus suggested route. Advisory: implementers may deviate from it when another route satisfies `## Objective`; reviewers flag guidance only when it is misleading, contradicts the objective, or would fail to achieve it.
- **`## Results`** — implementer-owned findings record. See §Results Shape.
- **`## Revision Notes`** — temporary, planner-owned delta signal when a task is updated: what changed, why, and how significant (trivial/mechanical vs. substantive). Removed at approval (the reviewer's duty, per its role spec); `validate_plan` warns when an `approved` task still carries a non-empty one.
- **`## Review Notes`** — reviewer-owned; present only when there are active items; removed entirely at approval.
- **`## Sync Impact`** — conditional, integration-phase-only, temporary. Added by the sync author during `superintegrate` Sync only to tasks whose post-sync diff needs task-specific context; removed at Integrate closeout. Format owned by `semantic-merge/references/workflow-sync-author.md`.

## Context Inheritance

`superra task read <path>` renders the assigned task with its ancestor chain, including each ancestor's full `## Objective` and nested `### Context` / `### Conventions` / `### Constraints` subsections — that is how a scoped subsection reaches every descendant task's agent. What a subsection should carry, and when to point rather than distill, is owned by `skills/superplan/references/task-tree-design.md` §Context Distillation.

## Hierarchy Management Commands

The mutation command surface — `task create`, `task rename`, `task dep add/remove`, bulk status ops, and the move/rename cascade rules — lives in `references/commands.md`. Single-field edits, including `status`, go through direct edit per `using-superra/SKILL.md` §Task Interface.

## Stale Content Checklist

Common stale content to replace in place (never strike through or append "Update:"):

- Task objectives describing an approach abandoned after seeing the data.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review.
- Sibling task objectives that assume an earlier approach which has since changed.
- Task `## Objective` or `## Results` descriptions superseded by a later task; rewrite them in place to reflect the latest shape, and add a revision note if the change is non-obvious.

## Results Shape

Results live in each task's `## Results` section. The same section matures through two stages.

### Two-Stage Lifecycle

- **Stage 1 — Dev log (IMPLEMENT phase).** Each task's `## Results` is the live findings record — terse, agent-facing. Re-implementation replaces a task's results; it does not append history.
- **Stage 2 — Permanent record (INTEGRATE Mature & Consolidate).** After Protect selects the results, documentation homes, consolidation dispositions, and protection mechanisms, create the user-facing documentation and result files first. Then distil each touched task's `## Results` to one of the dispositions below and apply the structural fold owned by `skills/superplan/references/consolidation.md`. `superintegrate/references/mature-consolidate.md` owns the ordering and record verification.

### Maturation Disposition Menu

Distilling a task's `## Results` at Stage 2 picks one disposition:

- **Mature** — synthesize substantive findings into the agreed user-facing document or result file at its project-appropriate durable home, then leave a concise reader-facing account in the durable task with links to the permanent artifact and any retained task-local evidence. The default for key or substantive results. A short retained subsection is appropriate when a full narrative would overstate minor work.
- **Trim-to-pointer** — when a task's own output *is* a document (a report, rendered note, manuscript section), reduce its `## Results` to a one-line pointer to that document, so the document is the single source of truth instead of a summary that duplicates it and drifts.
- **Drop** — when Protect selected a provisional result for omission or a task is a minor fix not worth surfacing as an outcome, trim heavily or drop its `## Results`.

When the consolidation fold removes a task's directory (Merge or Flatten), its distilled results move into the **target** task's `## Results` at the chosen level — a one-line note, a short subsection, or folded into the target's narrative. Nothing is left behind in the deleted directory.

**Guardrail:** results selected to keep at Protect are never dropped. The permanent documentation, result files, and mature task results together form the protected record; any selected automated checks supplement that record.

### Per-task results template

```markdown
## Results

### Key Findings
- [primary result, with number]
- [secondary result]

### Row Counts / Sample
- Input: N rows
- After [operation]: N rows (delta: +/- N)
- Final sample: N rows

### Figures and Tables
![Descriptive caption for fig A](attachments/fig_taskN_a.png)

### Notes
- [any caveat, data quirk, or decision the reader needs to interpret the results]

### Notation & Assumptions Ledger
*(theory-modeling tasks only — required by `theory-modeling/SKILL.md`. Tasks introducing nothing record "None.")*
```

Omit subsections that do not apply.

### Section Ownership

Implementer and reviewer duties on `## Results` live in each role spec's §What You Own; the orchestrator's parent-rollup and disposition duties live in `superimplement` and `superintegrate/references/mature-consolidate.md`. Beyond those: the planner creates `task.md` with an empty or placeholder `## Results`; a standalone author owns everything.

Summaries riding higher than a leaf — monitoring rollups and the matured narrative — link down to leaf task files rather than copying every finding up the tree.

### Figure Embedding

Commit figures to `attachments/` next to the task's `task.md` and embed with a path relative to the task file, e.g. `![caption](attachments/fig_name.png)`, so moving a task moves its figures and the dashboard resolves them via the task's `pathPrefix`. Full mechanics — PDF-to-PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`.
