---
title: "Define the Task Companion-File Contract"
status: revise
depends_on: []
---

## Objective

Teach every superRA execution mode one concise, authoritative lifecycle for task companion files.

- Keep one authoritative load-on-demand reference for the full lifecycle, but state the placement decision itself in the always-loaded `using-superra` §Task Interface and the user-facing README: session-only working files go to scratch outside `superRA/`; retained files—including code—owned by one task solely to produce, reproduce, review, or interpret its recorded results go under that task's `attachments/`; maintained code, shared/runtime inputs, and promised durable outputs go to the project's conventional permanent path.
- When `econ-data-analysis` is used for a superRA task, add the task-specific result-producing code case using the companion-file definition rather than treating all analysis code as permanent project code; keep standalone use outside this storage rule.
- Define one placement rule: every retained task-local companion belongs under `attachments/`; only `task.md` and child-task directories occupy the task directory itself. Directories containing `task.md` are subtasks, but `attachments/` remains an asset container even if a generated bundle contains that filename.
- Keep an artifact task-local only when one task owns it and a later agent needs it to reproduce, review, or interpret that task's results. Link every retained artifact from `## Results` and record the generating command, inputs, and provenance needed to reproduce it; do not retain artifacts generated only from unrecorded REPL state.
- Promote an artifact before Integrate closes when another task or runtime path consumes it, it becomes a maintained pipeline/tool, or it is a promised reader-facing deliverable. Move to the project's existing convention and update the task pointer rather than preserving duplicate sources of truth.
- Fold remaining companion-file disposition into Mature & Consolidate: retain with a surviving task, relocate with folded evidence, or drop superseded material. Files supporting protected key results cannot be dropped.
- Route the rule from the smallest owning workflow and reporting surfaces. Do not add a skill, stage, manifest row, frontmatter field, or role-specific paraphrase; leave canonical role specs and generated role artifacts unchanged unless forward-testing proves the always-loaded route insufficient.
- Apply `skill-creator` and the contributor guide's DRY and Necessity gates line by line, then run skill validation and a realistic harness session that creates, reviews, and promotes or retains representative companion files.

## Revision Notes

On 2026-07-25 the researcher reported that the existing bare pointers do not teach users or newly dispatched agents when to choose scratch, task-local `attachments/`, or a permanent project path. The researcher then clarified that a companion is defined by single-task ownership, not short lifespan: task-specific code kept solely to produce or support that task's results is a companion. The economic-data specialization applies only when that skill is used for a superRA task, not in standalone use. Preserve the detailed reference as the single lifecycle authority, make the three-tier placement decision visible at the two surfaces where users and agents first need it, and give superRA economic-data agents the concrete code case.

## Planner Guidance

The new authoritative reference should live at `skills/using-superra/references/task-companion-files.md`, because `using-superra` owns the universal task interface and normal implementation/review agents do not load the task-tree contract. Likely pointer sites are [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md), [superplan/SKILL.md](../../../../skills/superplan/SKILL.md), [superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md), [econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md), [integrate.md](../../../../skills/superintegrate/references/integrate.md), [mature-consolidate.md](../../../../skills/superintegrate/references/mature-consolidate.md), [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), and the baseline-IO route in [report-in-markdown/SKILL.md](../../../../skills/report-in-markdown/SKILL.md).

Preserve the figure mechanics and existing `attachments/` links in `report-in-markdown`; they are storage mechanics, not the lifecycle owner. Generalize existing figure-biased wording only where an agent would otherwise miss non-figure companions. User-facing documentation should point to this contract rather than restate it.

Keep the agent-facing placement instruction silent about attachment depth. Tooling may preserve nested paths emitted by external tools, but nesting is neither a second organizational model nor a choice agents need to make.

## Results

The authoritative [task companion-file contract](../../../../skills/using-superra/references/task-companion-files.md#classify) classifies scratch, task-local, and permanent files and now gives retained task-local files one placement boundary: `attachments/`. Only `task.md` and child-task directories occupy the task directory itself; the `attachments/` asset-container exception still applies when a generated bundle contains a file named `task.md`.

The contract also requires links and reproducibility metadata, promotes permanent artifacts without duplicate sources of truth, and carries retained companions through Mature & Consolidate without dropping protected-result support. It remains routed from the universal [Task Interface](../../../../skills/using-superra/SKILL.md#task-interface) and the smallest planning, implementation, integration, maturation, task-tree, reporting, and [user-facing documentation](../../../../README.md#how-it-works) surfaces. Canonical role specs and generated role artifacts remain unchanged.

The owning ancestor's injected `## Results` now states the same attachment-only boundary and identifies the data-path and UI redesigns as pending rather than presenting their rejected direct-companion behavior as current.

Verification:

- `uv run --with pyyaml python .../skill-creator/scripts/quick_validate.py skills/using-superra` reported `Skill is valid!`.
- `bash tests/check-harness-compatibility.sh` passed, including five Codex agent-generation tests, generated-artifact freshness, and all skill-packaging invariants.
- A fresh isolated Codex harness read the revised contract, removed calculation scratch, retained a hand-authored Markdown note and reproducible CSV under the task's `attachments/`, and promoted the runtime-consumed Python generator to the fixture project's `src/` path without a task-local duplicate. Independent checks confirmed the task directory contained only `task.md` and `attachments/`, all recorded files existed, and a fresh generator run reproduced the retained CSV byte-for-byte.
- The Markdown checker reported the contract, this task, and its owning ancestor clean; `superra task check` found no issues, and `git diff --check` passed.
