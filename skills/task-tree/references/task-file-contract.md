# Task File Contract

Load this reference when you need the `task.md` file contract: frontmatter, body sections, status/dependency mechanics, inherited context rendering, results shape, stale-content cleanup, or figure embedding.

Tree-design judgment — objective writing, splitting, placement, durable homes, update-task lifecycle, context distillation, and retroactive task-tree creation — lives in `skills/superplan/references/task-tree-design.md`.

## Tree Shape

`superRA/` holds top-level tasks as direct subdirectories, each with its own `task.md`. An umbrella `superRA/task.md` is optional: add one only when a shared `## Objective` / `### Context` genuinely spans every top-level task, per `task-tree-design.md` §Context Distillation's lowest-ancestor rule. When present, the umbrella is an ordinary task like any other — not a privileged one.

"Top-level task" describes position only (no parent), not required scope: a top-level task may be a leaf or a branch, narrow or broad, the same as any nested task.

## Task Anatomy

Every `task.md` — top-level, branch, or leaf — uses the same body sections. The tree is recursive: a task frames its own subtree; an umbrella task, when one exists, frames the whole project only because its subtree is everything.

- **`## Objective`** — the task's goal plus any scoped `### Context` / `### Conventions` / `### Constraints` its subtree inherits. An umbrella task's objective, when one exists, frames the project-level goal and scope; otherwise each top-level task's objective frames its own concern; a branch task's objective frames its subtree's goal.
- **`## Planner Guidance`** — optional advisory suggestions or exploration notes, useful but not binding.
- **`## Revision Notes`** — temporary delta signal when a task is updated; the reviewer removes it at approval.
- **`## Sync Impact`** — conditional, integration-phase-only, temporary. Added by the sync author during `superintegrate` Sync only to tasks whose post-sync diff needs task-specific context; removed at Integrate closeout. Format owned by `semantic-merge/references/workflow-sync-author.md`.

## Field-by-Field Notes

The frontmatter field set is **closed**: `title`, `status`, `depends_on`. Any other key is discarded the next time a CLI mutation rewrites the file (including automatic ancestor-status rollups), so do not store custom metadata in frontmatter — put it in a body section instead.

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`, `postponed`. Co-owned by implementer and reviewer for the dispatch lifecycle: implementer owns transitions up to `implemented` (and `revise` to `implemented` on fix rounds); reviewer owns `implemented` to `revise`, `implemented` to `approved`, and `approved` to `revise` during integration (when integration review surfaces issues in a previously approved task); the planner also sets `approved` to `revise` when widening that task's own objective in place at planning time (`superplan/references/task-tree-design.md` §Objective rewrites on scope expansion). `archived` and `postponed` are scope decisions set by the orchestrator / researcher, not dispatch verdicts: an `archived` task is treated as resolved/removed so its dependents proceed, while a `postponed` task is parked off the frontier and blocks its dependents until resumed. Resume a postponed task by setting its status back to `not-started`. On re-entry, the orchestrator resets tasks in the transitive downstream closure of a modified task to `not-started` by judgment; unrelated approved tasks keep their status. Exception: review-only trees (e.g. writing-workflow review lanes) skip the implementer states entirely — tasks go directly from `not-started` to `revise` or `approved` as the reviewer sets them.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically.
- **`## Objective`** is planner-owned. Implementers read it but do not rewrite it.
- **`## Planner Guidance`** is planner-owned and advisory. Implementers may deviate from it when another route satisfies `## Objective`; reviewers flag guidance only when it is misleading, contradicts the objective, or would fail to achieve it.
- **`## Results`** is implementer-owned. Updated with findings, verification evidence, caveats, and material `## Planner Guidance` deviations during execution. See §Results Shape.
- **`## Revision Notes`** carries the delta signal when a task objective is updated: what changed, why, and how significant (trivial/mechanical vs. substantive). It is temporary, with the same lifecycle as `## Review Notes`. `validate_plan` warns when an `approved` task still carries a non-empty `## Revision Notes` section; the reviewer remains responsible for removing it at approval.
- **`## Review Notes`** is present only when there are active items. On approval, the reviewer removes the section content entirely.

## Context Inheritance

`superra task read <path>` renders the assigned task with its ancestor chain, including each ancestor's full `## Objective` and nested `### Context` / `### Conventions` / `### Constraints` subsections. This rendered chain is one part of the agent's working context, alongside auto-loaded `CLAUDE.md` / `AGENTS.md` (project-level plus any nested in a directory the agent reads), manifest-loaded skills, and on-demand directory walking when a touched file needs a convention the chain does not cover. A scoped subsection makes a convention reachable from the task either by distilling it or by pointing to where it already lives (an auto-loaded doc, a manifest skill, a coherent `README`); planners choose point-vs-distill per `skills/superplan/references/task-tree-design.md` §Context Distillation.

Dependent siblings are ordered peers, not inherited context. Read a dependency's `## Results` only when the downstream task's objective needs that result, output file, sample, variable, or decision.

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
- When implementation materially deviates from `## Planner Guidance`, `## Results` states the guidance not followed, the chosen route, and why it still satisfies `## Objective`.
- **Stage 2 — Permanent record (INTEGRATE Mature & Consolidate).** Each touched task's `## Results` is distilled to one of the dispositions below. The structural fold that moves or removes the task is `skills/superplan/references/consolidation.md`'s; the disposition here sets how much of the results survive. The disposition is chosen in the merged stage's combined proposal and arrives to the implementer as a `## Revision Notes` instruction on the affected task; `superintegrate/SKILL.md` §Mature & Consolidate owns when and who decides.

### Maturation Disposition Menu

Distilling a task's `## Results` at Stage 2 picks one disposition:

- **Mature** — synthesize the substantive findings into a reader-facing narrative at the durable home: the highest task the integration actually touched, per affected subtree — not the global root, not a separate report doc — with links down to the leaf tasks holding per-task evidence, whose `## Results` stay as lightly-cleaned evidence and caveats. The default for key or substantive results. A *short retained subsection* — a few findings kept in place rather than synthesized upward — is the lighter end of this disposition when a full narrative would over-state minor work.
- **Trim-to-pointer** — when a task's own output *is* a document (a report, rendered note, manuscript section), reduce its `## Results` to a one-line pointer to that document, so the document is the single source of truth instead of a summary that duplicates it and drifts.
- **Drop** — when a task is a minor fix not worth surfacing as a feature, trim heavily or drop its `## Results`, because each retained file is added drift surface to maintain.

When the consolidation fold removes a task's directory (Merge or Flatten), its distilled results move into the **target** task's `## Results` at the chosen level — a one-line note, a short subsection, or folded into the target's narrative. Nothing is left behind in the deleted directory.

**Guardrail:** key results selected at Protect (`result-protection`) are never dropped. Trimming and dropping apply to non-key, low-value, or document-duplicated results only.

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
- **Orchestrator** — during IMPLEMENT, updates the immediate parent's `## Results` when an approved child produced a major result worth surfacing for monitoring; at INTEGRATE Mature & Consolidate, proposes each touched task's disposition (§Maturation Disposition Menu) and records it as a `## Revision Notes` instruction for the implementer to execute.
- **Standalone author** — everything.

Summaries riding higher than a leaf — monitoring rollups and the matured narrative — link down to leaf task files rather than copying every finding up the tree.

### Figure Embedding

Commit figures to `attachments/` next to the task's `task.md` and embed with a path relative to the task file, e.g. `![caption](attachments/fig_name.png)`, so moving a task moves its figures and the dashboard resolves them via the task's `pathPrefix`. Full mechanics — PDF-to-PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`.
