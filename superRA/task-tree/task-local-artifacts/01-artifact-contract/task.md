---
title: "Define the Task Companion-File Contract"
status: approved
depends_on: []
---

## Objective

Teach every superRA execution mode one concise, authoritative lifecycle for task companion files.

- Keep one authoritative load-on-demand reference for the full lifecycle, but state the placement decision itself in the always-loaded `using-superra` §Task Interface: session-only working files go to a scratch folder; retained files—including code—owned by one task solely to produce, reproduce, review, or interpret its recorded results go under that task's `attachments/`; maintained code, shared/runtime inputs, and promised durable outputs go to the project's conventional permanent path.
- When `econ-data-analysis` is used for a superRA task, add the task-specific result-producing code case using the companion-file definition rather than treating all analysis code as permanent project code; keep standalone use outside this storage rule.
- Define one placement rule: every retained task-local companion belongs under `attachments/`; only `task.md` and child-task directories occupy the task directory itself. Directories containing `task.md` are subtasks, but `attachments/` remains an asset container even if a generated bundle contains that filename.
- Keep an artifact task-local only when one task owns it and a later agent needs it to reproduce, review, or interpret that task's results. Link every retained artifact from `## Results` and record the generating command, inputs, and provenance needed to reproduce it; do not retain artifacts generated only from unrecorded REPL state.
- Promote an artifact before Integrate closes when another task or runtime path consumes it, it becomes a maintained pipeline/tool, or it is a promised reader-facing deliverable. Move to the project's existing convention and update the task pointer rather than preserving duplicate sources of truth.
- Fold remaining companion-file disposition into Mature & Consolidate: retain with a surviving task, relocate with folded evidence, or drop superseded material. Files supporting protected key results cannot be dropped.
- Route the rule from the smallest owning workflow and reporting surfaces. Do not add a skill, stage, manifest row, frontmatter field, or role-specific paraphrase; leave canonical role specs and generated role artifacts unchanged unless forward-testing proves the always-loaded route insufficient.
- Apply `skill-creator` and the contributor guide's DRY and Necessity gates line by line, then run skill validation and a realistic harness session that creates, reviews, and promotes or retains representative companion files.

## Planner Guidance

The new authoritative reference should live at `skills/using-superra/references/task-companion-files.md`, because `using-superra` owns the universal task interface and normal implementation/review agents do not load the task-tree contract. Likely pointer sites are [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md), [superplan/SKILL.md](../../../../skills/superplan/SKILL.md), [superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md), [econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md), [integrate.md](../../../../skills/superintegrate/references/integrate.md), [mature-consolidate.md](../../../../skills/superintegrate/references/mature-consolidate.md), [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), and the baseline-IO route in [report-in-markdown/SKILL.md](../../../../skills/report-in-markdown/SKILL.md).

Preserve the figure mechanics and existing `attachments/` links in `report-in-markdown`; they are storage mechanics, not the lifecycle owner. Generalize existing figure-biased wording only where an agent would otherwise miss non-figure companions. Keep the user-facing README focused on the product-level workflow.

Keep the agent-facing placement instruction silent about attachment depth. Tooling may preserve nested paths emitted by external tools, but nesting is neither a second organizational model nor a choice agents need to make.

## Results

The always-loaded [Task Interface](../../../../skills/using-superra/SKILL.md#task-interface) now teaches the three-way placement decision directly rather than presenting a bare pointer. It defines a task companion as any retained file—including code—owned by one task solely to produce, reproduce, review, or interpret its recorded results. Disposable session work stays in a scratch folder; task companions go under the owning task's `attachments/`; maintained code, shared or runtime-consumed files, and promised durable deliverables go to conventional permanent project paths.

The authoritative [task companion-file contract](../../../../skills/using-superra/references/task-companion-files.md#classify) now makes explicit that scratch stays outside `superRA/` and that long-lived retention does not by itself make a file a permanent project artifact. Its existing reproducibility, promotion, and maturation mechanics remain the single detailed source.

The [economic-data handoff gate](../../../../skills/econ-data-analysis/SKILL.md#documentation-and-handoff) applies the boundary only when `econ-data-analysis` is used for a superRA task: task-specific result-producing code is a companion even when committed long term, while maintained, shared, runtime-consumed, or promised code and outputs are promoted. Standalone use is unchanged. Canonical role specs and generated role artifacts remain unchanged.

Verification:

- `uv run --with pyyaml python .../skill-creator/scripts/quick_validate.py skills/using-superra` reported `Skill is valid!`.
- `bash tests/check-harness-compatibility.sh` passed, including five Codex agent-generation tests, generated-artifact freshness, and all skill-packaging invariants.
- A fresh read-only Codex harness loaded `using-superra` and `econ-data-analysis`, kept a committed long-lived Python analysis script used only for one task under that task's `attachments/`, and promoted a shared runtime loader and promised reader-facing table to permanent project paths. It also removed unrecorded REPL scratch and required task-result links plus reproduction metadata.
- The Markdown checker reported all three changed instruction files and this task clean; `superra task check` found no issues, and `git diff --check` passed.
- Re-verified after the second revise round: the placement paragraph in [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md#task-interface) now restates the classify criterion inline ("retained files—including code—owned by one task solely to produce, reproduce, review, or interpret its recorded results are task companions; put them under that task's `attachments/`"), matching the first Results paragraph above and the Objective's bullet 1 requirement to state the placement decision itself rather than deferring it to the reference. `check_markdown.py` reports [skills/using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md) and this task file clean. DRY/Necessity re-read: the one-line criterion echo between this paragraph and the reference's Classify section is intentional two-tier design (brief criterion in the always-loaded interface, full reproduce/promote/maturation mechanics only in the load-on-demand reference) — an echo tolerated per the contributor guide's own carve-out for avoiding a redundant reference load, not a drift risk since the reference no longer restates the same sentence.

## Review Notes
