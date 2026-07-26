# Task Companion Files

Load this reference before planning, creating, reviewing, integrating, or maturing any file kept in a task directory other than `task.md`.

## Classify

Classify each file before deciding where it belongs:

- **Ephemeral scratch** supports only the current session. Keep it outside `superRA/`, uncommitted, and remove it before handoff.
- **Task companion** is any retained file—including code—owned by one task solely to produce, reproduce, review, or interpret its recorded results. Commit it with the task; long-lived does not by itself mean permanent project artifact.
- **Permanent project artifact** is consumed by another task or runtime path, maintained as a pipeline or tool, or promised as a reader-facing deliverable. Store it in the project's existing conventional path.

## Place

- Put every retained task-local companion in `attachments/`; only `task.md` and child-task directories occupy the task directory itself.
- Treat directories containing `task.md` as subtasks. Treat `attachments/` as an asset container even when a generated bundle inside it contains a file named `task.md`.

Companion files are not task-tree, dependency, status-rollup, frontier, or Kanban nodes.

## Record and Reproduce

Link every retained task-local companion from the owning task's `## Results` with a path relative to `task.md`. Record the generating command, input paths, and source provenance needed to reproduce each generated file. For a hand-authored companion, record the source or decision basis instead of inventing a generating command.

Do not retain a file generated only from unrecorded REPL state. Recreate it from a recorded script or notebook, or classify it as scratch.

## Promote

Before integration review, promote every task-local companion that now meets the permanent-project definition. Move it to the project's existing conventional path and update the task's `## Results` link; do not preserve a duplicate task-local source of truth.

## Mature and Consolidate

Include each remaining companion in its task's Mature & Consolidate disposition:

- retain it with a surviving task;
- relocate it with folded evidence to the surviving task; or
- drop it when superseded.

Update relative links after any move. Never drop a file that supports a protected key result.
