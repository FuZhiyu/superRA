# Task Companion Files

Load before planning, creating, reviewing, integrating, or maturing any file kept in a task directory other than `task.md`.

## Classify

- **Ephemeral scratch** — supports only the current session. Outside `superRA/`, uncommitted, gone before handoff.
- **Task companion** — retained file, code included, owned by one task solely to produce, reproduce, review, or interpret its recorded results. Committed with the task; long-lived does not mean permanent project artifact.
- **Permanent project artifact** — consumed by another task or runtime path, maintained as a pipeline or tool, or promised as a reader-facing deliverable. Lives at the project's existing conventional path.

## Place

Every retained companion goes in `attachments/`; only `task.md` and child-task directories occupy the task directory itself. A directory containing `task.md` is a subtask; `attachments/` is an asset container even when a generated bundle inside it contains a file named `task.md`. Companion files are not task-tree, dependency, status-rollup, frontier, or Kanban nodes.

## Record and Reproduce

Link every companion from the owning task's `## Results`, path relative to `task.md`. Record the generating command, input paths, and source provenance; for a hand-authored companion, record the source or decision basis instead. A file generated only from unrecorded REPL state is not retainable — recreate it from a recorded script or notebook, or classify it as scratch.

## Promote

Before integration review, promote every companion that now meets the permanent-project definition: move it to the conventional path and update the `## Results` link. No duplicate task-local source of truth.

## Mature and Consolidate

Give each remaining companion a disposition: retain with a surviving task, relocate with folded evidence to the surviving task, or drop when superseded. Update relative links after any move. Never drop a file that supports a protected key result.
