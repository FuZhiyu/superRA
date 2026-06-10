---
title: "Integration Workflow: .plan/-Native, Consolidation Gate, Maturation Home"
status: implemented
depends_on:
  - agent-protocols
  - handoff-doc
tags: []
created: 2026-05-24
---

## Objective

Own the design of the INTEGRATE workflow skill (`skills/superintegrate/SKILL.md`, formerly `integration-workflow`) for `.plan/`-native operation, including the consolidation gate and the results-maturation home. This task absorbed the `integrate-cleanup` workstream at integration (consolidation Merge, 2026-06-01) per the update-task lifecycle: a transient improvement task spun out during planning is merged back into the task that owns its concern at integration, rather than surviving as a separate tree.

### Design by phase

- **Protect:** drift tests reference task paths (e.g., `data-preparation/merge`) instead of task numbers; key-result selection walks the `.plan/` tree.
- **Sync:** temporary `## Sync Map` in root task.md (removed at Integrate closeout); task-local impact in each affected task's `## Sync Impact` section.
- **Integrate:** `integration_status:` in frontmatter; integration reviewer edits frontmatter directly; post-sync refactor commits code + task.md atomically; closeout removes the temporary `## Sync Map` / `## Sync Impact`.
- **Consolidation Gate (between Integrate-close and Document):** a mandatory assessment with an optional pass. Once per integration the orchestrator surveys the tree against `consolidation.md §When to Consolidate` and records a one-line verdict in the durable integration record; only a needs-a-pass verdict runs the consolidation protocol. Orchestrator inline work — no `Stage:` value, no dispatch.
- **Document:** Stage-2 results maturation synthesizes the reader-facing narrative **upward into the highest-level task the integration touched, per affected subtree**, with leaf `## Results` kept as lightly-cleaned linked evidence. Not in-place per-leaf rewriting, not a separate `RESULTS.md`. `superintegrate` §Document points at `task-tree/references/task-file-contract.md` §Results Shape as the lifecycle owner.
- **Finish:** `.plan/` committed as-is; workflow status recorded in the root durable integration record.

## Results

`skills/superintegrate/SKILL.md` is `.plan/`-native across all phases and now carries the consolidation gate and the highest-touched-task maturation home. Two change-sets landed: the original `.plan/`-native migration, then the `integrate-cleanup` redesign merged in here.

### `.plan/`-native migration (across all five phases)

- **Frontmatter / triggers:** removed `RESULTS.md` / `PLAN.md` references.
- **Protect:** key-result extraction walks the `.plan/` tree via `task_query.py --tree`; drift tests reference task paths; workflow status flipped in root task.md.
- **Sync:** `## Sync Map` lives in root task.md; task-local impact in each affected task's `## Sync Impact`; decisions logged in root task.md.
- **Integrate:** `integration_status:` frontmatter field (lowercase enum); reviewer edits frontmatter directly; review notes in `## Review Notes`; refactor commits code + task.md atomically; closeout removes the temporary sync sections.
- **Finish:** `.plan/` committed as-is; removed conditional "if PLAN.md still exists" logic.
- **Red Flags / When to Lighten:** references updated from `PLAN.md ## Sync Map` to `root task.md ## Sync Map`, from `Integration status: APPROVED` to `integration_status: approved`.

### The integrate-cleanup redesign (merged 2026-06-01)

The `superRA/` tree wears two hats — dispatch/decomposition structure and permanent reader-facing record — and two INTEGRATE-phase gaps let them collide: consolidation was an optional, ungated clause (a messy tree could reach the matured record unexamined), and maturation happened in place in each leaf's `## Results` (the reader-facing record inherited dispatch granularity and overwrote the dev log, with no front door). Both closed without a new `Stage:` value, without reintroducing a separate `RESULTS.md`, keeping one source of truth per concern:

**1. Gated consolidation assessment.** `skills/superintegrate/SKILL.md` carries a `## Consolidation Gate` section ([SKILL.md:242](../../../../skills/superintegrate/SKILL.md#L242)) between `### Step 5: Close Integrate` and `## Document`, surfaced in the workflow overview as a boundary check rather than a sixth phase ([SKILL.md:16](../../../../skills/superintegrate/SKILL.md#L16)). The assessment is mandatory (survey `--tree`/`--dag`, judge against `consolidation.md §When to Consolidate`, record a one-line verdict in the durable integration record); the pass is conditional, and material restructures still route through `superplan §User Feedback`. The stale §When to Lighten "before or during Integrate … optional" bullet was rewritten to point at the gate ([SKILL.md:358](../../../../skills/superintegrate/SKILL.md#L358)), and `consolidation.md §Standalone vs Integration Use` now names the gate as the concrete integration-time trigger. The symptom list and protocol are pointed to, never paraphrased (DRY); no `Stage:`/manifest row added (orchestrator inline work). *Known limitation (tracked in `planning-redesign/placement-and-update-lifecycle`): the gate's wrong-parent/Restructure check is currently frontier-internal and cannot detect a misplaced subtree — it must be made whole-tree.*

**2. Results-maturation home = highest-level touched task.** `skills/task-tree/references/task-file-contract.md` §Results Shape (the lifecycle owner) defines Stage-2 maturation's primary deliverable as the matured narrative synthesized upward into the highest-level task the integration touched, per affected subtree, with leaf `## Results` kept as linked evidence ([task-file-contract.md §Results Shape](../../../../skills/task-tree/references/task-file-contract.md#L48)). Two touched subtrees land two matured narratives. This gives a front door without overwriting the leaf dev log or creating a second source of truth, and because drift tests reference leaf task paths, keeping leaf evidence intact preserves result-protection. `superintegrate` §Document points at the redefined Results Shape (the old "root task" option removed; doc-reviewer dispatch de-rooted, [SKILL.md:294](../../../../skills/superintegrate/SKILL.md#L294)).

**Integration finding caught and fixed:** the consolidation-gate verdict was initially written to a temporary `## Revision Notes` slot, which warns on approved tasks and is matured/removed downstream — wrong home for durable provenance. Relocated to the root durable integration record (`11e1214b`, re-review APPROVED `4e6a67ac`).

### Verification

- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` clean; targeted suite green at integration close (247 passed); `git diff --check` clean over the integration range.
- integrate-cleanup children correctness-reviewed and APPROVED (`afa70c6f`, `4e6a67ac`); sync review APPROVED (`728ab399`); post-sync integration review closed after the one finding above. The integration's own consolidation-gate verdict was **clean-enough — pass skipped**.

## Review Notes

> 1. [MAJOR] `## Objective` and `## Results` state `skills/task-tree/references/planning.md §Results Shape` as the lifecycle owner and cite `planning.md:168/:201/:204` as evidence; that file no longer exists — Results Shape now lives in [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) §Results Shape — so the ownership claim is contradicted by the current repo and the evidence links 404. Repoint the claim and citations in place.
>    → implemented: updated both `## Objective` §Document and `## Results` §The integrate-cleanup redesign to cite [task-file-contract.md §Results Shape](../../../../skills/task-tree/references/task-file-contract.md#L48) instead of the removed planning.md
