# Planning Reference

Load this reference when you are an orchestrator or planner creating, restructuring, or maintaining a `.plan/` task tree.

**Terminology:** "Plan" is the verb (the planning process), not the noun. Everything in `.plan/` is a **task**. `.plan/` is "the task tree." See `CLAUDE.md` §Terminology for the full convention.

## Writing Objectives

An objective describes what success looks like, not how to get there.

**Include:**
- The goal — what the task should produce or verify
- Relevant conventions — naming, paths, units, variable definitions
- Constraints — what NOT to do, what to preserve
- Input/output expectations — what data comes in, what form results take
- Validation criteria — what must be true for the task to be complete

**Include enough context that an implementer with zero project context can work independently** after reading this task's objective plus the ancestor chain up to the root.

**Steps vs subtasks vs suggestions:**
- Necessary steps that need independent tracking and review: create as **subtasks** (child directories with their own `task.md`)
- Suggestive approaches the implementer may adapt: state as **suggestions in prose**, e.g. "Consider using a left join on fund_id x date"
- Do NOT prescribe implementation steps — that is the implementer's job
- DO prescribe validation criteria — what must be true for the task to be complete

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

## Root task.md Anatomy

The root `.plan/task.md` frames the entire project. It carries:

- **`## Objective`** — project-level goal, methodology summary, scope boundaries
- **`## Conventions`** — naming conventions, paths, units, variable definitions that apply across all tasks
- **`## Revision Notes`** — temporary delta signal when a task is updated (what changed, significance). The reviewer removes this section when approving the task — same lifecycle as `## Review Notes`

The root task does not carry `script`, `input`, or `output` — those belong on leaf tasks.

## Retroactive Plan Creation

When creating `.plan/` from existing work (code already written, results already obtained):

1. Read the existing code and results to understand what was done
2. Create the root `task.md` with the project objective and conventions
3. Create child tasks that mirror the logical structure of the existing work — not the file layout
4. Set status to `approved` for tasks whose work is complete and verified
5. Set status to `implemented` for tasks whose work is done but not yet reviewed
6. Populate `## Results` from existing findings
7. Run `plan_dashboard.py` to generate the dashboard

## Hierarchy Management Commands

### Create a task

```bash
python3 <skill-dir>/scripts/task_create.py \
  --plan-root .plan --path 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge
```

`task_create.py` auto-fills the template with current dates and frontmatter defaults (`status: not-started`).

### Rename a task (cascades to sibling depends_on)

```bash
python3 <skill-dir>/scripts/task_rename.py \
  --plan-root .plan --from 01-data/01-load --to 01-data/01-load-raw
```

### Manage dependencies

```bash
python3 <skill-dir>/scripts/task_link.py \
  --plan-root .plan --path 01-data/03-filter --depends-on 02-merge

python3 <skill-dir>/scripts/task_link.py \
  --plan-root .plan --path 01-data/03-filter --depends-on 02-merge --remove
```

## Field-by-Field Notes

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`. Co-owned by implementer and reviewer: implementer owns transitions up to `implemented` (and `revise → implemented` on fix rounds); reviewer owns `implemented → revise` and `implemented → approved`. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; unrelated approved tasks keep their status.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically.
- **`script` / `input` / `output`** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **`## Objective`** is planner-owned. Implementers read it but do not rewrite it.
- **`## Results`** is implementer-owned. Updated with findings during execution. See §Results Shape below.
- **`## Revision Notes`** carries the delta signal when a task objective is updated — what changed, why, and how significant (trivial/mechanical vs substantive). Temporary: the reviewer removes this section when approving the task. Same lifecycle as `## Review Notes`.
- **`## Review Notes`** is present only when there are active items. On `approved`, the section content is removed entirely.

## Conventions Section

The root task.md `## Conventions` section caches project guidance so dispatched agents need not re-walk the tree.

**Discipline:**
- Populated by the orchestrator. Subagents do not edit this section.
- Entry format: one paragraph per doc — a summary, not an excerpt.
- Stamp the walk date.
- List the NOT-walked paths too — an empty section is ambiguous; explicitly naming out-of-scope directories removes the ambiguity.

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
- **Stage 2 — Permanent record (INTEGRATE phase).** Results maturation restructures for reader-facing clarity. The Stage 2 consolidation discipline lives in `skills/report-in-markdown/references/final-form.md`.

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
- **Orchestrator / standalone author** — everything.
- **Reviewers** do NOT edit `## Results`. Concerns are raised in `## Review Notes`.

### Figure Embedding

Figures committed to `attachments/` next to the task's `task.md` (e.g., `.plan/my-task/attachments/fig.png`). Embed with a path relative to the task file:

```markdown
![Descriptive caption](attachments/fig_name.png)
```

This keeps tasks self-contained — moving a task moves its figures, and the dashboard resolves these paths correctly via the task's `pathPrefix`.

Full figure-embedding mechanics — PDF→PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`.
