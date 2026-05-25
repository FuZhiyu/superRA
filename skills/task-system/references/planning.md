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

## Root task.md Anatomy

The root `.plan/task.md` frames the entire project. It carries:

- **`## Objective`** — project-level goal, methodology summary, scope boundaries
- **`## Conventions`** — naming conventions, paths, units, variable definitions that apply across all tasks
- **`## Decisions`** — user decisions that shaped the plan (log format, append-only)

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

`task_create.py` auto-fills the template with current dates and frontmatter defaults (`status: not-started`, `review_status: ~`, `integration_status: ~`).

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

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; unrelated approved tasks keep their status.
- **`review_status`** — the implementer sets `implemented` (signaling ready-for-review); the reviewer sets `revise` or `approved`. Valid values: `~` (unset), `implemented`, `revise`, `approved`. Before execution starts, leave as `~`.
- **`integration_status`** is owned by the integration reviewer and the implementer across the Integrate step. Valid values: `~`, `implemented`, `revise`, `approved`. The same DAG cascade rule applies as for `review_status`.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically.
- **`script` / `input` / `output`** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **`## Objective`** is planner-owned. Implementers read it but do not rewrite it.
- **`## Results`** is implementer-owned. Updated with findings during execution. See §Results Shape below.
- **`## Decisions`** holds task-scoped user decisions. Uses the three-line blockquote format (see §User Decisions Log below).
- **`## Review Notes`** is present only when there are active items. On `approved`, the section content is removed entirely.

## User Decisions Log

Researcher answers to `AskUserQuestion` / plain-text pauses land in the relevant `task.md` **before** the agent acts on them, committed atomically with the work they unblock.

**Where it lands:**

- **Task-scoped decision** (affects one task's scope, methodology, or implementation) → task's `## Decisions` section.
- **Cross-task / project-level decision** (methodology affecting multiple tasks, sample definition, output scope, completion choices, drift-test selection, doc disposition) → root task.md `## Decisions` section. Append new decisions to the bottom; do not rewrite prior decisions.

**Format (both locations):**

```markdown
> **User decision (2026-04-16):** Use CRSP value-weighted returns, not equal-weighted.
> **Question asked:** Which market return definition for the benchmark?
> **Rationale (if given):** Matches prior paper; easier reviewer comparison.
```

Three lines, blockquote, dated. `Question asked` is the agent's own short restatement of what it asked — specific enough for a fresh agent to see why the decision was needed. `Rationale` is optional; include only if the researcher gave one, never invent it.

The `ask-user-question-logger` PostToolUse hook reminds the agent to log after each `AskUserQuestion` call; when the harness does not expose the hook, set a TodoWrite reminder.

If it is unclear whether an answer counts as a decision worth logging: if acting on it would change the code, data, or methodology in a way another agent could not reconstruct from the code alone, log it.

## Conventions Section

The root task.md `## Conventions` section caches project guidance so dispatched agents need not re-walk the tree.

**Discipline:**
- Populated by the orchestrator. Subagents do not edit this section.
- Entry format: one paragraph per doc — a summary, not an excerpt.
- Stamp the walk date.
- List the NOT-walked paths too — an empty section is ambiguous; explicitly naming out-of-scope directories removes the ambiguity.

## Workflow Status Checkboxes

Flipped only by the orchestrator (or standalone author), only at the moment the named workflow step completes, and only in the same commit that completes that step. Each box is a rollup over per-task statuses plus global gates. A box is unchecked again only when a scope change or post-sync refactor invalidates the milestone.

## Stale Content Checklist

Common stale content to replace in place (never strike through or append "Update:"):

- Task objectives describing an approach abandoned after seeing the data — rewrite them.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review (the reviewer deletes from `## Review Notes`).
- Sibling task objectives that assume an earlier approach which has since changed.
- Task output descriptions superseded by a later task — rewrite the earlier task's `output:` frontmatter to reflect the latest shape; keep the "what changed" narrative in the Decisions section only.

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
![Descriptive caption for fig A](results_attachments/fig_taskN_a.png)

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

Figures committed to `results_attachments/` at the project root. Embed with:

```markdown
![Descriptive caption](results_attachments/fig_name.png)
```

Full figure-embedding mechanics — PDF→PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`.
