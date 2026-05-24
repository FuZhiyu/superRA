# Planning Reference

Load this reference when you are an orchestrator or planner creating, restructuring, or maintaining a `.plan/` task tree.

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
