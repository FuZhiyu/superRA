---
title: "The Task File"
status: not-started
depends_on:  []
---

## Objective

Each task is a directory holding one `task.md`: three frontmatter fields, then body sections each written by one role. You read it to see a task's goal and outcome, and edit it to steer. Files only this task uses sit beside it in `attachments/`.

```
---
title: "Filter Sample"
status: not-started
depends_on:
  - 01-sample-design
---

## Objective

Drop observations before 2000 and require non-missing returns.

## Results

### Key Findings
- Retained 3.8 M of 4.7 M rows after applying filters.
```

## Frontmatter: three fields, no others

| Field | Holds |
|---|---|
| `title` | The name shown in the tree and dashboard. |
| `status` | Where the task sits in its lifecycle; a parent's is rolled up from its children. See [Status and the frontier](#/04-utility-skills/01-task-tree/03-status-and-frontier). |
| `depends_on` | Sibling directory names that must finish before this task is ready. |

Any other key is dropped the next time the tooling rewrites the file; put custom metadata in a body section.

## Body sections: one owner each

| Section | Written by | Holds |
|---|---|---|
| `## Objective` | Planner; you review and can edit | The goal. Binding: a reviewer rejects work that violates it. The agent delivers exactly what it names, so mark exploratory work as open-ended ("explore", "propose options"). |
| `## Details` | Planner, optional | Leads worth passing on: candidate files, data quirks, a suggested route. Informative, never binding, never inherited. Note here when a result is high-stakes and deserves independent review. |
| `## Revision Notes` | Planner, when an objective changes | What changed and why; removed once the implementer has worked it in. |
| `## Reproduction` | Implementer | The [reproduction steps](#/04-utility-skills/09-reproducibility) the task owns. |
| `## Results` | Implementer | Findings and the evidence behind them. Redoing the task replaces them, never appends; [INTEGRATE](#/05-workflows/03-integrate) later distills them, sometimes to a one-line pointer to the permanent document. |
| `## Review Notes` | Reviewer | Open findings while the task is at `revise`; at `approved`, the review's depth and focus plus any advisory items left open. |

Every field and section rule is in the [task-file contract](skills/task-tree/references/task-file-contract.md).

## Subtasks inherit the whole Objective

Every agent working a task reads each ancestor's full `## Objective`, including its `### Context`, `### Conventions`, and `### Constraints` subsections. `## Details` is never inherited.

- **Put a shared rule on the lowest task it governs.** A rule for the whole project goes in an optional top-level `superRA/task.md`.
- **Point rather than copy.** When the rule already lives in `CLAUDE.md` or a data README, write one line saying what it requires and link there; a copy drifts.

## Steer by rewriting in place

Edit the objective or constraint to say what it should be now: no strikethroughs, "Update:" lines, or dated decision logs. Git keeps the history. Widening a finished task's objective reopens it (see [replanning](#/05-workflows/01-plan)).

## Keep task-only files with the task

Decide where a file lives by who uses it and for how long:

| Kind | Example | Where it lives |
|---|---|---|
| **Scratch** | A quick check you won't keep | Outside `superRA/`, uncommitted |
| **Task companion** | An exploratory script, notebook, figure, or one-off validation that only this task's results rely on | The task's `attachments/`, committed and linked from `## Results` with the command that made it |
| **Project file** | Pipeline code, data another task reads, a promised deliverable | The project's usual path |

- **Explore freely inside a task.** Companions keep exploratory work reproducible without cluttering the project.
- **Promotion happens on first reuse.** Once another task or the pipeline needs a companion, the agent moves it to its project path and updates the links.
- **Only recorded work is kept.** Output produced only in a live session, with no saved script, stays scratch.

The rules are in [task-companion-files.md](skills/using-superra/references/task-companion-files.md).
