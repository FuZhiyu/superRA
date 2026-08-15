# Task File Contract

Load for the `task.md` contract: frontmatter, body sections, status/dependency mechanics, inherited context rendering, results shape, stale-content cleanup, figure embedding.

Tree-design judgment — objective writing, splitting, placement, durable homes, update-task lifecycle, context distillation, retroactive tree creation — lives in `skills/superplan/references/task-tree-design.md`.

## Tree Shape

`superRA/` holds top-level tasks as direct subdirectories, each with its own `task.md`. An umbrella `superRA/task.md` is optional — add one only when a shared `## Objective` / `### Context` spans every top-level task, per `task-tree-design.md` §Context Distillation's lowest-ancestor rule. It is an ordinary task, not a privileged one.

"Top-level" describes position (no parent), not scope — such a task may be leaf or branch, narrow or broad, like any nested task.

Files retained in a task directory are not task nodes — placement and the `attachments/` task-discovery exception in `skills/using-superra/references/task-companion-files.md`.

## Task Anatomy

Every `task.md` — top-level, branch, or leaf — uses the same frontmatter and body sections. The tree is recursive: a task frames its own subtree; an umbrella task frames the whole project only because its subtree is everything.

**Binding content goes in `## Objective`; everything else is information and goes in `## Details`.** Binding means a reviewer rejects work that violates it. A descendant inherits ancestor objectives and nothing else (§Context Inheritance), so the same test decides what a subtree sees. Each skill classifies its own artifacts against it.

The frontmatter field set is **closed**: `title`, `status`, `depends_on`. Any other key is discarded the next time a CLI mutation rewrites the file (including ancestor-status rollups) — put custom metadata in a body section.

- **`status`** — task-local validity marker. Values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`, `postponed`. Co-owned across the dispatch lifecycle: implementer owns transitions up to `implemented` (including `revise` → `implemented` on fix rounds); reviewer owns `implemented` → `revise`, `implemented` → `approved`, and `approved` → `revise` when integration review surfaces issues in a previously approved task. Independent review is triggered, not scheduled — when none runs, the orchestrating agent sets `implemented` → `approved` on its own verification. Replan transitions — flipping a widened `approved` task to `revise`, resetting downstream dependents — are planner judgment, owned by `superplan/references/task-tree-design.md` §Objective rewrites on scope expansion. `archived` and `postponed` are orchestrator/researcher scope decisions, not dispatch verdicts: `archived` counts as resolved so dependents proceed; `postponed` parks the task off the frontier and blocks its dependents until resumed (set back to `not-started`). Review-only trees (e.g. writing-workflow review lanes) skip the implementer states — tasks go from `not-started` straight to `revise` or `approved` as the reviewer sets them.
- **`depends_on`** — sibling directory names, sibling-only; parent status rolls up from children automatically. Dependent siblings are ordered peers, not inherited context — read a dependency's `## Results` only when the downstream objective needs it.
- **`## Objective`** — planner-owned: the task's goal plus any scoped `### Context` / `### Conventions` / `### Constraints` its subtree inherits. Implementers read it but do not rewrite it.
- **`## Details`** — planner-owned, optional: planning findings, domain surveys, a suggested route. Implementers may deviate when another route satisfies `## Objective`; reviewers flag details only when they mislead, contradict the objective, or would fail to achieve it.
- **`## Results`** — implementer-owned findings record. See §Results Shape.
- **`## Revision Notes`** — temporary update delta: what changed, why, how significant (trivial/mechanical vs. substantive). Planner- or orchestrator-authored on an objective rewrite (`task-tree-design.md` §Objective rewrites on scope expansion); the implementer removes it once incorporated, in the same commit that sets `status: implemented` (`implement-task` §Execution) — whether or not review follows.
- **`## Review Notes`** — reviewer-owned. Present while any item remains: open `[BLOCKING]` findings at `revise`, or the tier/focus header and any un-actioned `[ADVISORY]` items at `approved`. A task may sit at `revise` with deferred findings while the orchestrator advances dependent work.
- **`## Sync Impact`** — temporary, integration-phase-only. Added by the sync author during `superintegrate` Sync to tasks whose post-sync diff needs task-specific context; removed at Integrate closeout. Format owned by `semantic-merge/references/workflow-sync-author.md`.

## Context Inheritance

`superra task read <path>` renders the task with its ancestor chain, including each ancestor's full `## Objective` and nested `### Context` / `### Conventions` / `### Constraints` — that is how a scoped subsection reaches every descendant's agent. What a subsection carries, and when to point rather than distill: `skills/superplan/references/task-tree-design.md` §Context Distillation.

## Hierarchy Management Commands

The mutation command surface — `task create`, `task rename`, `task dep add/remove`, bulk status ops, the move/rename cascade rules — lives in `references/commands.md`. Single-field edits, including `status`, go through direct edit per `using-superra/SKILL.md` §Task Interface.

## Stale Content Checklist

Common stale content to replace in place (never strike through or append "Update:"):

- Task objectives describing an approach abandoned after seeing the data.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review.
- Sibling task objectives that assume an earlier approach which has since changed.
- Task `## Objective` or `## Results` descriptions superseded by a later task — rewrite in place to the latest shape; see `## Revision Notes` above for when to add one.
- Dated decision ledgers — a "Decisions" section, or a "per user decision `<date>`" note on a rule. A researcher decision enters a task file by rewriting the owning objective or constraint to its current state; date and deliberation stay in git.

## Results Shape

Each task's `## Results` matures through two stages.

### Two-Stage Lifecycle

- **Stage 1 — Dev log (IMPLEMENT phase).** `## Results` is the live, agent-facing findings record. A line belongs only if a future reader needs it to use, reproduce, or trust the result — the inclusion test mirrors the objective's rejection test in `task-tree-design.md` §Writing Objectives and Details. Detail that clears the test sits low in the pyramid or behind a link; anything a linked artifact, commit, or upstream task already carries is pointed at, not restated (`communicate`). Re-implementation replaces a task's results; it never appends history.
- **Stage 2 — Permanent record (INTEGRATE Mature & Consolidate).** After Protect selects results, documentation homes, consolidation dispositions, and protection mechanisms: create the user-facing documentation and result files first, then distil each touched task's `## Results` to a disposition below and apply the structural fold owned by `skills/superplan/references/consolidation.md`. Ordering and record verification: `superintegrate/references/mature-consolidate.md`.

### Maturation Disposition Menu

Stage-2 distillation picks one disposition:

- **Mature** — default for key or substantive results. Synthesize the findings into the agreed user-facing document or result file at its project-appropriate durable home, then leave a concise reader-facing account in the durable task linking the permanent artifact and any retained task-local evidence. A short retained subsection suffices when a full narrative would overstate minor work.
- **Trim-to-pointer** — the task's own output *is* a document (report, rendered note, manuscript section): reduce `## Results` to a one-line pointer, so the document stays the single source of truth rather than a summary that duplicates it and drifts.
- **Drop** — Protect selected the result for omission, or the task is a minor fix not worth surfacing as an outcome: trim heavily or drop `## Results`.

When the consolidation fold removes a task's directory (Merge or Flatten), its distilled results move into the **target** task's `## Results` at the chosen level — a one-line note, a short subsection, or folded into the target's narrative. Nothing is left behind in the deleted directory.

**Guardrail:** results selected to keep at Protect are never dropped. Permanent documentation, result files, and matured task results form the protected record; selected automated checks supplement it.

### Subsection menu

Most results are a few lines under `## Results` with no subsections. Add one only when it carries a takeaway the inclusion test keeps — the default for every entry below is to omit it.

| Subsection | Add when |
|---|---|
| `### Key Findings` | more than one finding a researcher would quote or act on needs separating from the surrounding narrative |
| `### Row Counts / Sample` | a downstream task or reviewer must reconcile against the sample the work produced |
| `### Figures and Tables` | the task produced a figure or table a reader needs to see — embed as `![caption](attachments/fig_name.png)` |
| `### Notes` | a caveat, data quirk, or decision changes how the result is read |
| `### Notation & Assumptions Ledger` | theory-modeling tasks — required by `theory-modeling/SKILL.md`; tasks introducing nothing record "None." |

`superra task result add --finding` is the exception: it appends under a `### Key Findings` heading, creating it when absent, since it needs a fixed insertion anchor rather than parsing hand-written prose. Results assembled by direct edit — the usual path — follow the menu.

### Section Ownership

Implementer and reviewer duties on `## Results` live in the role skills (`superRA:implement-task`, `superRA:review-task`); orchestrator parent-rollup and disposition duties in `superimplement` and `superintegrate/references/mature-consolidate.md`. Beyond those: the planner creates `task.md` with an empty or placeholder `## Results`; a standalone author owns everything.

Any `## Results` riding higher than the task that produced a finding — a parent rollup, a monitoring summary, the matured narrative — links down to the owning task rather than copying the finding up the tree. A rollup is strictly shorter than the children it covers.

### Figure Embedding

Commit figures to `attachments/` beside the task's `task.md` and embed relative to the task file — `![caption](attachments/fig_name.png)` — so moving a task moves its figures and the dashboard resolves them via `pathPrefix`. Full mechanics — PDF-to-PNG conversion, caption discipline, file-reference conventions — in `skills/communicate/references/markdown.md` §Figures.
