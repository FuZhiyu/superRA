---
title: "Define the Task Companion-File Contract"
status: not-started
depends_on: []
---

## Objective

Teach every superRA execution mode one concise, authoritative lifecycle for task companion files.

- Add a load-on-demand reference routed from `using-superra` §Task Interface. Classify files as ephemeral scratch, committed task-local companions, or permanent project artifacts.
- Define the flat layout: regular files beside `task.md` are companions; directories containing `task.md` are subtasks; `attachments/` is the one backward-compatible non-task directory for existing assets or coherent generated bundles. New work creates no other ancillary directories and does not require `attachments/`.
- Keep an artifact task-local only when one task owns it and a later agent needs it to reproduce, review, or interpret that task's results. Link every retained artifact from `## Results` and record the generating command, inputs, and provenance needed to reproduce it; do not retain artifacts generated only from unrecorded REPL state.
- Promote an artifact before Integrate closes when another task or runtime path consumes it, it becomes a maintained pipeline/tool, or it is a promised reader-facing deliverable. Move to the project's existing convention and update the task pointer rather than preserving duplicate sources of truth.
- Fold remaining companion-file disposition into Mature & Consolidate: retain with a surviving task, relocate with folded evidence, or drop superseded material. Files supporting protected key results cannot be dropped.
- Route the rule from the smallest owning workflow and reporting surfaces. Do not add a skill, stage, manifest row, frontmatter field, or role-specific paraphrase; leave canonical role specs and generated role artifacts unchanged unless forward-testing proves the always-loaded route insufficient.
- Apply `skill-creator` and the contributor guide's DRY and Necessity gates line by line, then run skill validation and a realistic harness session that creates, reviews, and promotes or retains representative companion files.

## Planner Guidance

The new authoritative reference should live at `skills/using-superra/references/task-companion-files.md`, because `using-superra` owns the universal task interface and normal implementation/review agents do not load the task-tree contract. Likely pointer sites are [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md), [superplan/SKILL.md](../../../../skills/superplan/SKILL.md), [superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md), [integrate.md](../../../../skills/superintegrate/references/integrate.md), [mature-consolidate.md](../../../../skills/superintegrate/references/mature-consolidate.md), [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), and the baseline-IO route in [report-in-markdown/SKILL.md](../../../../skills/report-in-markdown/SKILL.md).

Preserve the figure mechanics and existing `attachments/` links in `report-in-markdown`; they are backward-compatible storage mechanics, not the lifecycle owner. Generalize existing figure-biased wording only where an agent would otherwise miss direct companion files. User-facing documentation should point to this contract rather than restate it.

### Generated artifacts

No generated outputs are expected because `agents/*` is out of scope. If that changes, edit canonical role specs and run `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` for the four generated role surfaces listed in the parent task; do not edit those outputs directly.

## Results
