# Planning Reference

Load this reference when you are an orchestrator or planner creating, restructuring, or maintaining a `superRA/` task tree.

**Terminology:** "Plan" is the verb (the planning process), not the noun. Everything in `superRA/` is a **task**. `superRA/` is "the task tree." See `CLAUDE.md` §Terminology for the full convention.

## Writing Objectives and Planner Guidance

`## Objective` is the authoritative implementation and review contract. It describes what success looks like, not optional routes for getting there.

**Include:**
- The goal — what the task should produce or verify
- Relevant conventions — naming, paths, units, variable definitions
- Constraints — what NOT to do, what to preserve
- User or methodology decisions the implementer must preserve
- Input/output expectations — what data comes in, what form results take
- Fixed `script` / `input` / `output` expectations when they define scope
- Validation criteria — what must be true for the task to be complete

**Include enough context that an implementer with zero project context can work independently** after reading this task's objective plus the ancestor chain up to the root.

**Scoped context lives on the lowest ancestor whose subtree it governs.** The task tree is recursive — any task can carry context for its subtree, and the top task is not a special semantic owner. When a convention, constraint, or piece of context changes what an implementation or review agent does, place it in the `## Objective` of the lowest task whose subtree it applies to, under a scoped `### Context`, `### Conventions`, or `### Constraints` subsection. Project-wide conventions belong on the top task's objective; conventions that govern only one data source, model, manuscript, or workstream belong on that subtree's objective. `superra task read` renders each ancestor's full `## Objective` (nested `###` subsections included) into the dispatched agent's context, so an agent inherits exactly the scoped context above its task without re-walking the tree.

`## Planner Guidance` is optional and advisory. Use it for suggested routes, candidate files, prior exploration notes, likely sequence, implementation hints, and other context the implementer may adapt or ignore while satisfying `## Objective`.

**Steps vs subtasks vs suggestions:**
- Necessary steps that need independent tracking and review: create as **subtasks** (child directories with their own `task.md`)
- Suggestive approaches the implementer may adapt: put them in `## Planner Guidance`, e.g. "Consider using a left join on fund_id x date"
- Do NOT prescribe implementation steps — that is the implementer's job
- DO prescribe validation criteria — what must be true for the task to be complete

Existing task files without `## Planner Guidance` remain valid. Do not bulk-migrate old objectives automatically; split objective/guidance opportunistically when a task is created or materially rewritten.

## Splitting Tasks

A task should be the right size for independent dispatch and review.

**Split when:**
- Different concerns (data cleaning vs estimation vs visualization)
- Different data sources that can be loaded independently
- Independent work streams that could run in parallel
- Different domain skills apply (data analysis vs writing)

**Do not split when:**
- Trivially sequential steps with no independent review value
- Too small to justify dispatch cost (skill-load, context hydration)
- Artificially decomposing one logical operation into sub-steps

**Right-sizing test:** Can you describe the task's success criteria in one sentence? If yes, it is the right size. If the review would be trivial ("yes, you renamed a variable"), it is too small. If the description needs three paragraphs, it may need splitting.

**Goal-oriented naming:** "Merge holdings with characteristics" not "Run merge script."

## Placing Work in the Tree

A two-step decision: first find which task's **concern** covers the new work, then decide **granularity** (how big is the extension?).

### Step 1 — Find the concern

Walk the tree recursively. At each level, ask: does an existing task's topic or concern cover this work? If yes, descend into that task and repeat. If no task at this level covers it, create a sibling at this level.

### Step 2 — Decide granularity

Once you have found the right task:

- **Update** — the extension is simple enough that the task stays right-sized for a single dispatch. Rewrite its objective to include both old and new scope. Example: a merge task that handled fund data now also needs to handle CRSP data — same concern, extended scope, still one task.

- **Nest** — the extension is complex enough to warrant its own dispatch and review cycle. Add as a child subtask. The parent's objective may also be broadened to reflect the expanded scope. Example: a data-preparation task that now needs a whole new cleaning pipeline for a second data source — same concern, but the new work needs independent implementation.

- **Create sibling** — the work does not belong under any existing task's concern at this level. Applied at the root level, this creates a new root-level task.

The recursion handles all levels uniformly: start at the root, walk down through the tree, land the work at the right depth.

**Anti-patterns:** creating a new task for what is really a scope extension of an existing task; nesting three or more levels deep when unnecessary; creating siblings with near-identical concerns.

## Task Anatomy

Every `task.md` — root, branch, or leaf — uses the same body sections. The tree is recursive: a task frames its own subtree, and the top task frames the whole project only because its subtree is everything.

- **`## Objective`** — the task's goal, plus the scoped context its subtree inherits. The top task's objective frames the project-level goal, methodology summary, and scope boundaries; a branch task's objective frames its subtree's goal. Scoped `### Context`, `### Conventions`, and `### Constraints` subsections carry naming conventions, paths, units, variable definitions, and constraints that govern the task's subtree (see §Writing Objectives). Place each at the lowest task whose subtree it governs — project-wide ones at the top, narrower ones deeper.
- **`## Planner Guidance`** — optional advisory suggestions or exploration notes that are useful but not binding.
- **`## Revision Notes`** — temporary delta signal when a task is updated (what changed, significance). The reviewer removes this section when approving the task — same lifecycle as `## Review Notes`.

Branch tasks (those with children) do not carry `script`, `input`, or `output` — those belong on leaf tasks.

## Retroactive Plan Creation

When creating `superRA/` from existing work (code already written, results already obtained):

1. Read the existing code and results to understand what was done
2. Create the top `task.md` with the project objective and any project-wide scoped conventions
3. Create child tasks that mirror the logical structure of the existing work — not the file layout
4. Set status to `approved` for tasks whose work is complete and verified
5. Set status to `implemented` for tasks whose work is done but not yet reviewed
6. Populate `## Results` from existing findings
7. Run `superra dashboard` to launch the dashboard

## Hierarchy Management Commands

### Create a task

```bash
superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --guidance "Consider reusing the sample filter helper in Code/common.py." \
  --depends-on 02-merge
```

`superra task create` auto-fills the template with current dates and frontmatter defaults (`status: not-started`). `--guidance` is optional; omitted guidance creates no empty section.

### Rename a task (cascades to sibling depends_on)

```bash
superra task rename 01-data/01-load 01-data/01-load-raw
```

### Manage dependencies

```bash
superra task dep add 01-data/03-filter 02-merge

superra task dep remove 01-data/03-filter 02-merge
```

## Field-by-Field Notes

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`, `postponed`. Co-owned by implementer and reviewer for the dispatch lifecycle: implementer owns transitions up to `implemented` (and `revise → implemented` on fix rounds); reviewer owns `implemented → revise` and `implemented → approved`. `archived` and `postponed` are scope decisions set by the orchestrator / researcher, not dispatch verdicts: an `archived` task is treated as resolved/removed so its dependents proceed, while a `postponed` task is parked off the frontier and **blocks its dependents** until resumed. Resume a postponed task by setting its status back to `not-started`. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; unrelated approved tasks keep their status.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically.
- **`script` / `input` / `output`** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **`## Objective`** is planner-owned. Implementers read it but do not rewrite it.
- **`## Planner Guidance`** is planner-owned and advisory. Implementers may deviate from it when another route satisfies `## Objective`; reviewers flag guidance only when it is misleading, contradicts the objective, or would fail to achieve it.
- **`## Results`** is implementer-owned. Updated with findings, verification evidence, caveats, and material `## Planner Guidance` deviations during execution. See §Results Shape below.
- **`## Revision Notes`** carries the delta signal when a task objective is updated — what changed, why, and how significant (trivial/mechanical vs substantive). Temporary: the reviewer removes this section when approving the task. Same lifecycle as `## Review Notes`. `validate_plan` warns (it never mutates) when an `approved` task still carries a non-empty `## Revision Notes` section, so a leak surfaces through the `[task-hook]` channel; the reviewer remains responsible for removing it at approval.
- **`## Review Notes`** is present only when there are active items. On `approved`, the section content is removed entirely.

## Context and Conventions

Reusable context and conventions are captured once, on the objective of the task whose subtree they govern, so dispatched agents inherit them through `superra task read` — a focused tree (the task's position, siblings, and direct children) followed by the ancestor objectives — instead of re-walking the project tree. The planner walks the project guidance docs (`CLAUDE.md` / `AGENTS.md` / `README.md`, and data-directory `README.md`s) during planning and distills what changes implementation or review behavior into scoped `### Conventions` / `### Context` / `### Constraints` subsections of the relevant task objective.

**Discipline:**
- Place each convention at the lowest task whose subtree it governs (see §Writing Objectives).
- Captured by the planner in `## Objective`, which is planner-owned. Implementers and reviewers read inherited context but do not rewrite ancestor objectives.
- Entry format: a summary that states the behavior to follow, not a verbatim excerpt of the source doc. Stamp the walk date when the distillation reflects a docs walk.
- When the walk found no relevant convention for the subtree, say so explicitly — an absent subsection is ambiguous; naming the out-of-scope paths removes it.

## Stale Content Checklist

Common stale content to replace in place (never strike through or append "Update:"):

- Task objectives describing an approach abandoned after seeing the data — rewrite them.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review (the reviewer deletes from `## Review Notes`).
- Sibling task objectives that assume an earlier approach which has since changed.
- Task output descriptions superseded by a later task — rewrite the earlier task's `output:` frontmatter to reflect the latest shape; add a revision note if the change is non-obvious.

## Results Shape

Results live in each task's `## Results` section. The same section matures through two stages.

### Two-Stage Lifecycle

- **Stage 1 — Dev log (IMPLEMENT phase).** Each task's `## Results` is the live findings record — terse, agent-facing. "Latest state only" — re-implementation replaces a task's results; it does not append history.
- When implementation materially deviates from `## Planner Guidance`, `## Results` states the guidance not followed, the chosen route, and why it still satisfies `## Objective`.
- **Stage 2 — Permanent record (INTEGRATE Document).** Results maturation keeps findings in task files and synthesizes the matured reader-facing narrative **upward into the highest-level task the integration actually touched, per affected subtree** — for each subtree the work touched, the top task of that subtree's affected frontier carries the matured summary, with links down to the leaf tasks that hold the per-task evidence. This is the front door, not the global root and not a separate report document. Leaf `## Results` stay as lightly-cleaned evidence and caveats (so drift tests and key-result selections that reference leaf task paths still resolve); maturation promotes the narrative one level up rather than rewriting each leaf into reader-facing prose in place. An integration that touched two independent subtrees lands two matured narratives, one at each subtree's highest touched task.

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
- **Orchestrator** — during IMPLEMENT, updates the immediate parent's `## Results` when an approved child produced a major result worth surfacing for monitoring; at INTEGRATE Document, synthesizes the matured narrative into the highest touched task per affected subtree (Stage 2 above).
- **Standalone author** — everything.

Summaries that ride higher than a leaf — monitoring rollups during IMPLEMENT and the matured narrative at Document — link down to the leaf task files for full evidence and caveats; they do not recursively copy every finding up the tree.

### Figure Embedding

Figures committed to `attachments/` next to the task's `task.md` (e.g., `superRA/my-task/attachments/fig.png`). Embed with a path relative to the task file:

```markdown
![Descriptive caption](attachments/fig_name.png)
```

This keeps tasks self-contained — moving a task moves its figures, and the dashboard resolves these paths correctly via the task's `pathPrefix`.

Full figure-embedding mechanics — PDF→PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`.
