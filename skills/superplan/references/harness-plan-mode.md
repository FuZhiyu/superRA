# Harness Plan Mode

Load when the harness activates plan mode AND you recognize you are in a superRA context.

---

## Core Principle

**Harness plan mode is the exploration and approval environment; `superRA/` is the output.** The plan file is a single-file flat view of what `superRA/` will contain, for review before the files exist. At exit you create `superRA/` directly from your understanding — there is no migration from the plan file.

---

## During Plan Mode

The read-only constraint blocks file creation, not exploration. Run the superplan phases that write no task files — **Entry Assessment**, **Exploration**, and **Domain Setup & Scope** (`../SKILL.md`).

Write the plan file last, after exploration is complete and any domain hard gate is satisfied — it is a presentation artifact, not a working draft.

---

## Harness Plan File Template

Write a flattened view of the planned tasks plus the tree visualization and dependency DAG. Each task entry carries the same content as its eventual `task.md` (the layout differs, not the content), so write objectives at task.md quality.

```markdown
# Plan: <project title>

## Task Tree

<indented tree visualization>
  task-a/
  task-b/
    task-b1/
    task-b2/
  task-c/

## Dependency DAG

task-b1 → task-c
task-b2 → task-c
(task-a has no dependencies)

---

## Tasks

### <path/in/tree> — <Title>

**depends_on:** [sibling-name] | (none)

**Objective:**
<Full objective text. Written at task.md quality — complete enough that an agent reading only this entry can implement the task without additional context.>

---

### <next-task-path> — <Title>

...
```

---

## At Exit from Plan Mode

Create the `superRA/` task tree from your conversation context — the exploration findings, domain inventory, and design decisions accumulated in plan mode — not by re-parsing the plan file. Use `superra task create` or write `task.md` files directly.

Commit `superRA/` as the first action after exit, before any implementation.
