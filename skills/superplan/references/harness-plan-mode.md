# Harness Plan Mode

Load when the harness activates plan mode AND you recognize you are in a superRA context.

---

## Core Principle

**Harness plan mode is your exploration and approval environment; `superRA/` is the output.**

The harness plan file is not the authoritative plan. It is a single-file flat representation of what `superRA/` will contain — written so the user can review and approve the task structure before you create the actual files. At exit from plan mode you create `superRA/` directly from your full understanding; no migration from the plan file is needed or correct.

---

## During Plan Mode

The read-only constraint applies to file creation, not to exploration. Use it.

Run the superplan phases that do not require writing task files:

- **Entry Assessment** — check for an existing `superRA/`, read the root `task.md` if present, determine placement in the tree, choose a depth tier, and identify the routing path (forward, retroactive, or consolidation). Depth tier selection happens here; the plan file reflects the chosen depth and placement decisions.
- **Exploration** — read project files, load domain skill planning references, inventory data or model primitives as the domain requires, satisfy any domain hard gates that require researcher approval before task structure is drafted. Depth scales with the tier: quick skips deep exploration, standard explores relevant areas, thorough dispatches parallel exploration agents.
- **Domain Setup & Scope** — identify the domain vertical, load the matching planning reference, present the domain inventory to the researcher, and get approval before drafting task structure.

Write the harness plan file last, after exploration is complete and any domain hard gate has been satisfied. The plan file is a presentation artifact, not a working draft to iterate in-place.

---

## What Goes in the Harness Plan File

Write a flattened view of the planned `superRA/` changes. The user is reviewing the same information they would see after the task files are created — just in a single file instead of a directory tree.

For each planned task, include:

- **Path** — where the task directory will sit in the tree (e.g., `data-preparation/merge`)
- **Title** — the task title
- **Objective** — the full objective text, written at the same quality you would write it in the actual `task.md`
- **`depends_on`** — sibling directory names this task depends on (empty if none)
- **`script` / `input` / `output`** — when known at planning time

Also include the tree visualization (indented list or ASCII tree) and the dependency DAG summary so the user can verify the structure at a glance.

The template below is close enough to `task.md` format that writing the plan file is also writing the plan — the difference is layout (one file vs many), not content.

---

## Harness Plan File Template

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
**script:** <filename or ~>
**input:** <files or ~>
**output:** <files or ~>

**Objective:**
<Full objective text. Written at task.md quality — complete enough that an agent reading only this entry can implement the task without additional context.>

---

### <next-task-path> — <Title>

...
```

---

## At Exit from Plan Mode

When the user approves the plan and exits plan mode, you have full write access. Create the `superRA/` task tree directly from your conversation context — the exploration findings, domain inventory, and design decisions you accumulated in plan mode.

Use `superra task create` or create directories and write `task.md` files directly. The harness plan file provided the review vehicle; the task files are the output. Do not re-parse or "migrate" the plan file — write from your understanding.

Commit the `superRA/` directory as the first action after exit, before any implementation work begins.
