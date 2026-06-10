# Task File Contract

Load this reference when you need the `task.md` file contract: frontmatter, body sections, status/dependency mechanics, inherited context rendering, results shape, stale-content cleanup, or figure embedding.

Tree-design judgment — objective writing, splitting, placement, durable homes, update-task lifecycle, context distillation, and retroactive task-tree creation — lives in `skills/superplan/references/task-tree-design.md`.

## Task Anatomy

Every `task.md` — root, branch, or leaf — uses the same body sections. The tree is recursive: a task frames its own subtree, and the top task frames the whole project only because its subtree is everything.

- **`## Objective`** — the task's goal plus any scoped `### Context` / `### Conventions` / `### Constraints` its subtree inherits. The top task's objective frames the project-level goal and scope; a branch task's objective frames its subtree's goal.
- **`## Planner Guidance`** — optional advisory suggestions or exploration notes, useful but not binding.
- **`## Revision Notes`** — temporary delta signal when a task is updated; the reviewer removes it at approval.
- **`## Workflow Status`** — integration-phase progress record, present only on the root task during INTEGRATE. Carries checkboxes for the four superintegrate milestones (`Drift tests created`, `Integrated`, `Docs finalized`, and the final action). These checkboxes are an integration-phase-only exception to the "no checkboxes in tasks" rule — they track cross-stage workflow state, not implementation steps, and are written and flipped by the orchestrator during INTEGRATE. Remove the section after Finish.

Branch tasks (those with children) do not carry `script`, `input`, or `output` — those belong on leaf tasks.

## Field-by-Field Notes

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`, `postponed`. Co-owned by implementer and reviewer for the dispatch lifecycle: implementer owns transitions up to `implemented` (and `revise` to `implemented` on fix rounds); reviewer owns `implemented` to `revise` and `implemented` to `approved`. `archived` and `postponed` are scope decisions set by the orchestrator / researcher, not dispatch verdicts: an `archived` task is treated as resolved/removed so its dependents proceed, while a `postponed` task is parked off the frontier and blocks its dependents until resumed. Resume a postponed task by setting its status back to `not-started`. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; unrelated approved tasks keep their status.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically.
- **`script` / `input` / `output`** are fixed at planning time and only the orchestrator may change them because they define task scope.
- **`## Objective`** is planner-owned. Implementers read it but do not rewrite it.
- **`## Planner Guidance`** is planner-owned and advisory. Implementers may deviate from it when another route satisfies `## Objective`; reviewers flag guidance only when it is misleading, contradicts the objective, or would fail to achieve it.
- **`## Results`** is implementer-owned. Updated with findings, verification evidence, caveats, and material `## Planner Guidance` deviations during execution. See §Results Shape.
- **`## Revision Notes`** carries the delta signal when a task objective is updated: what changed, why, and how significant (trivial/mechanical vs. substantive). It is temporary, with the same lifecycle as `## Review Notes`. `validate_plan` warns when an `approved` task still carries a non-empty `## Revision Notes` section; the reviewer remains responsible for removing it at approval.
- **`## Review Notes`** is present only when there are active items. On approval, the reviewer removes the section content entirely.
- **`## Workflow Status`** is orchestrator-owned on the root task during INTEGRATE only. See §Task Anatomy for the full contract. Not present in normal task files; `superplan §Phase 3` must not create it.

## Context Inheritance

`superra task read <path>` renders the assigned task with its ancestor chain, including each ancestor's full `## Objective` and nested `### Context` / `### Conventions` / `### Constraints` subsections. Agents inherit scoped context from the task tree; they do not need to re-walk project guidance docs when the governing objectives already contain the needed conventions.

Dependent siblings are ordered peers, not inherited context. Read a dependency's `## Results` only when the downstream task's objective needs that result, output file, sample, variable, or decision.

## Hierarchy Management Commands

The mutation command surface — `task create`, `task rename`, `task dep add/remove`, bulk status ops, and the move/rename cascade rules — lives in `references/commands.md`. Single-field edits, including `status`, go through direct edit per `using-superRA/SKILL.md` §Task Interface.

## Stale Content Checklist

Common stale content to replace in place (never strike through or append "Update:"):

- Task objectives describing an approach abandoned after seeing the data.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review.
- Sibling task objectives that assume an earlier approach which has since changed.
- Task output descriptions superseded by a later task; rewrite the earlier task's `output:` frontmatter to reflect the latest shape, and add a revision note if the change is non-obvious.

## Results Shape

Results live in each task's `## Results` section. The same section matures through two stages.

### Two-Stage Lifecycle

- **Stage 1 — Dev log (IMPLEMENT phase).** Each task's `## Results` is the live findings record — terse, agent-facing. Re-implementation replaces a task's results; it does not append history.
- When implementation materially deviates from `## Planner Guidance`, `## Results` states the guidance not followed, the chosen route, and why it still satisfies `## Objective`.
- **Stage 2 — Permanent record (INTEGRATE Document).** Findings stay in task files; the matured reader-facing narrative is synthesized upward into the highest task the integration actually touched, per affected subtree — not the global root, not a separate report doc — with links down to the leaf tasks holding per-task evidence. Leaf `## Results` stay as lightly-cleaned evidence and caveats.

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

- **Planner** — creates task.md with `## Results` section (empty or with placeholder text).
- **Implementer** — fills and updates `## Results` during execution. On subsequent iterations, replaces the section's prior content in place.
- **Reviewer** — verifies the assigned task's `## Results` are substantive enough before approval. Concerns are raised in `## Review Notes`.
- **Orchestrator** — during IMPLEMENT, updates the immediate parent's `## Results` when an approved child produced a major result worth surfacing for monitoring; at INTEGRATE Document, synthesizes the matured narrative into the highest touched task per affected subtree.
- **Standalone author** — everything.

Summaries riding higher than a leaf — monitoring rollups and the matured narrative — link down to leaf task files rather than copying every finding up the tree.

### Figure Embedding

Commit figures to `attachments/` next to the task's `task.md` and embed with a path relative to the task file, e.g. `![caption](attachments/fig_name.png)`, so moving a task moves its figures and the dashboard resolves them via the task's `pathPrefix`. Full mechanics — PDF-to-PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`.
