---
title: "Define the Task Companion-File Contract"
status: approved
depends_on: []
---

## Objective

Teach every superRA execution mode one concise, authoritative lifecycle for task companion files.

- Add a load-on-demand reference routed from `using-superra` §Task Interface. Classify files as ephemeral scratch, committed task-local companions, or permanent project artifacts.
- Define the placement rule: `.md`, `.py`, `.jl`, `.r`/`.R`, and `.ipynb` companions may sit beside `task.md`; generated outputs, supporting data, and all other retained files belong in `attachments/`. Directories containing `task.md` are subtasks, but `attachments/` remains an asset container even if a generated bundle contains that filename.
- Keep an artifact task-local only when one task owns it and a later agent needs it to reproduce, review, or interpret that task's results. Link every retained artifact from `## Results` and record the generating command, inputs, and provenance needed to reproduce it; do not retain artifacts generated only from unrecorded REPL state.
- Promote an artifact before Integrate closes when another task or runtime path consumes it, it becomes a maintained pipeline/tool, or it is a promised reader-facing deliverable. Move to the project's existing convention and update the task pointer rather than preserving duplicate sources of truth.
- Fold remaining companion-file disposition into Mature & Consolidate: retain with a surviving task, relocate with folded evidence, or drop superseded material. Files supporting protected key results cannot be dropped.
- Route the rule from the smallest owning workflow and reporting surfaces. Do not add a skill, stage, manifest row, frontmatter field, or role-specific paraphrase; leave canonical role specs and generated role artifacts unchanged unless forward-testing proves the always-loaded route insufficient.
- Apply `skill-creator` and the contributor guide's DRY and Necessity gates line by line, then run skill validation and a realistic harness session that creates, reviews, and promotes or retains representative companion files.

## Planner Guidance

The new authoritative reference should live at `skills/using-superra/references/task-companion-files.md`, because `using-superra` owns the universal task interface and normal implementation/review agents do not load the task-tree contract. Likely pointer sites are [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md), [superplan/SKILL.md](../../../../skills/superplan/SKILL.md), [superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md), [integrate.md](../../../../skills/superintegrate/references/integrate.md), [mature-consolidate.md](../../../../skills/superintegrate/references/mature-consolidate.md), [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), and the baseline-IO route in [report-in-markdown/SKILL.md](../../../../skills/report-in-markdown/SKILL.md).

Preserve the figure mechanics and existing `attachments/` links in `report-in-markdown`; they are storage mechanics, not the lifecycle owner. Generalize existing figure-biased wording only where an agent would otherwise miss direct companion files. User-facing documentation should point to this contract rather than restate it.

Keep the agent-facing placement instruction silent about attachment depth. Tooling may preserve nested paths emitted by external tools, but nesting is neither a second organizational model nor a choice agents need to make.

### Generated artifacts

No generated outputs are expected because `agents/*` is out of scope. If that changes, edit canonical role specs and run `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` for the four generated role surfaces listed in the parent task; do not edit those outputs directly.

## Results

Added one authoritative [task companion-file contract](../../../../skills/using-superra/references/task-companion-files.md#classify). It classifies scratch, task-local, and permanent files; defines direct versus `attachments/` placement and the asset-container exception; requires links and reproducibility metadata; promotes permanent artifacts without duplicate sources of truth; and carries retained companions through Mature & Consolidate without dropping protected-result support.

The contract is routed from the universal [Task Interface](../../../../skills/using-superra/SKILL.md#task-interface) and the smallest planning, implementation, integration, maturation, task-tree, reporting, and [user-facing documentation](../../../../README.md#how-it-works) surfaces. Canonical role specs and generated role artifacts remain unchanged.

Verification:

- `bash tests/check-harness-compatibility.sh` passed, including five Codex agent-generation tests, generated-artifact freshness, and all skill-packaging invariants.
- A fresh isolated Codex harness created and self-reviewed representative companions: it removed session scratch, retained a hand-authored note, generated CSV, and imported bundle under `attachments/`, and promoted a Python diagnostic to the fixture project's conventional `src/` path when a runtime consumer appeared. The rerun reproduced the CSV deterministically, all 13 recorded links resolved, and task validation reported zero errors (plus the fixture's expected synthetic-root rollup warning).
- The Markdown checker reported all 13 changed Markdown files clean, and `git diff --check` passed on the final task-owned diff.
