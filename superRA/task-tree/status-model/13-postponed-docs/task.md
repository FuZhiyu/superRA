---
title: "Document the postponed status"
status: revise
depends_on:
  - 11-postponed-core-semantics
tags: []
created: 2026-06-01
---

## Objective

Document `postponed` everywhere the status set is described in prose, so the enum, its semantics, and who sets it stay coherent across the skills. Load `skill-creator` before editing any `SKILL.md`, and self-apply the `CLAUDE.md` "Teach the Protocol, Don't Prescribe Each Action" DRY/Necessity gate line by line — add only lines that change what an agent would *do*; point to the authoritative source rather than paraphrasing it.

The authoritative behavior is in this feature's root `task.md` semantics table and in `01-core-semantics`; documentation here describes the final behavior, it does not redefine it. Key facts to convey: `postponed` parks a task off the frontier without deleting it; it is excluded from completion accounting; it **blocks its dependents** (unlike `archived`, which lets them through); it is set by the orchestrator/researcher as a scope-deferral decision (not an implementer/reviewer verdict); resume by setting status back to `not-started`.

### Sites to update

1. **`skills/task-tree/SKILL.md`** — the frontmatter status table (line ~80) and any status example (line ~112). Add `postponed` with a one-line meaning. Note who sets it (orchestrator/researcher), consistent with how `archived` is described.
2. **`skills/task-tree/references/planning.md`** — the status definition / co-ownership section (line ~122). Add `postponed`: not dispatchable, blocks dependents, set as a deferral decision, resumed via `not-started`.
3. **`skills/task-tree/references/internals.md`** — the `VALID_STATUSES` documentation (line ~61) and the `compute_status` rollup-rules description (line ~50-51). Reflect: postponed excluded from rollup; all-parked branch rolls up to postponed-if-any-postponed-else-archived.
4. **`skills/agent-orchestration/SKILL.md`** — the Review Status Reference table (line ~192-198). Add a `postponed` row: Meaning ≈ "Deferred and parked off the frontier; not deleted"; Orchestrator action ≈ "Not dispatchable; its dependents are blocked until resumed. Set back to `not-started` to resume." Keep the row terse — the table is a quick reference, not the spec.

### Coherence check before completing

- Re-run the generated-artifact grep from the root `## Conventions` (`grep -rn` the status enum across `skills/using-superRA/references/`, `.codex/agents/`, `agents/`). If any generated file echoes the enum, do NOT hand-edit it — update its source/generator and run `sync_codex_agents.py`. As of planning this returned nothing; confirm it still does.
- Confirm no other prose site enumerates the status set without `postponed` (grep for the other status names across `skills/` and `README.md`).

## Results

`postponed` is now documented everywhere the status set is described in prose. All edits describe the behavior already implemented in `01-core-semantics`; none redefine it.

### Sites updated

1. **[SKILL.md:80](../../../../../skills/task-tree/SKILL.md#L80)** — added `postponed` to the frontmatter status-enum row and noted that `archived` / `postponed` are set by the orchestrator / researcher (the rest of the lifecycle is implementer / reviewer). **[SKILL.md:112](../../../../../skills/task-tree/SKILL.md#L112)** — added `postponed` to the enum echo in the task-file format example.
2. **[planning.md:122](../../../../../skills/task-tree/references/planning.md#L122)** — added `postponed` to the valid-values list and a clause distinguishing the two parked statuses: both are orchestrator / researcher scope decisions (not dispatch verdicts); `archived` lets dependents proceed while `postponed` parks the task off the frontier and **blocks its dependents** until resumed via `not-started`.
3. **[internals.md:17](../../../../../skills/task-tree/references/internals.md#L17)** (`Task` dataclass status comment), **[internals.md:61](../../../../../skills/task-tree/references/internals.md#L61)** (`VALID_STATUSES`) — added `postponed` to both enum echoes. **[internals.md:50](../../../../../skills/task-tree/references/internals.md#L50)** (`compute_status`) — described parked-child exclusion from the active rollup set and the all-parked rule (rolls up to `postponed` if any child is postponed, else `archived`).
4. **[agent-orchestration/SKILL.md:197](../../../../../skills/agent-orchestration/SKILL.md#L197)** — added a terse `postponed` row to the Review Status Reference: meaning "Deferred and parked off the frontier; not deleted"; orchestrator action "Not dispatchable; its dependents are blocked until resumed. Set back to `not-started` to resume."
5. **[RELEASE-NOTES.md:3](../../../../../RELEASE-NOTES.md#L3)** — added an `## [Unreleased]` → `### Added` entry for `postponed` (the changelog's prior top section `[0.2.0]` is a cut release, and no `[Unreleased]` header existed). The bullet records the user-visible facts: new `status` frontmatter value, off-frontier + excluded-from-completion-% mirroring of `archived`, the dependency-blocking contrast with `archived`, all-parked rollup rule, the dashboard Postponed column/badge, and orchestrator/researcher-set with `not-started` resume. Version-manifest bump deliberately left untouched per the review (release-prep decision for the orchestrator).

### Coherence check

- **Generated-artifact grep** across `skills/using-superRA/references/`, `.codex/agents/`, and `agents/` found no echo of the status enum (only incidental prose mentions of single workflow states in `main-agent.md`). No generated file echoes the enum, so no `sync_codex_agents.py` regeneration is required — confirms the planning-time finding still holds.
- **Prose-enumeration grep** across `skills/` and `README.md`: no prose site enumerates the status set without `postponed`. Beyond the four planned sites, the grep surfaced a fifth enum echo — the `Task` dataclass status comment at `internals.md:17` — which was updated for coherence. Script and dashboard-template sites (`scripts/*.py`, `templates/*.html`) already carry `postponed` from tasks 01/02; `task_check.py` imports `VALID_STATUSES` so its enum validation auto-flows.

### Verification

`~/.venv/bin/pytest skills/task-tree/scripts/test_task_tree.py -q` → **215 passed**, matching the `01-core-semantics` baseline after that task's `task_check` regression was added (this task is docs-only; no code touched here). The DRY/Necessity gate was self-applied line by line: each added line either completes a stale enum or conveys a behavior-shaping, non-default fact (parked statuses are orchestrator-set; `postponed` blocks dependents while `archived` does not; resume via `not-started`); the full semantics table stays in the feature root `task.md` rather than being paraphrased here. The `RELEASE-NOTES.md` bullet is a user-facing changelog summary, not a spec restatement.

**Final diff self-check:** `git diff 876178e3..HEAD`; this task's surviving hunks are the prose-doc mirror (`skills/task-tree/SKILL.md`, `references/planning.md`, `references/internals.md`, `skills/agent-orchestration/SKILL.md`) plus the `RELEASE-NOTES.md` `[Unreleased]` entry added this turn. No suspicious hunks — the `skills/*` edits are doc-mirror prose of the implemented behavior owned by 01/02; no version-manifest change.

## Review Notes

The documentation edits themselves landed (the `postponed` prose is live in the contract, internals.md, and the orchestration table); the findings below are record-integrity issues from this task's fold-in to the status-model tree.

1. **MAJOR** — Both the objective and `## Results` reference the pre-fold-in tree: "implemented in `01-core-semantics`," "the `01-core-semantics` baseline," "from tasks 01/02," and "the generated-artifact grep from the root `## Conventions`" — no `01-core-semantics` task or root `## Conventions` section exists anywhere under [the status-model tree](../task.md); the referenced tasks are now [11-postponed-core-semantics](../11-postponed-core-semantics/task.md) and [12-postponed-rendering-surfaces](../12-postponed-rendering-surfaces/task.md). In a tree whose siblings are numbered 01–13, "tasks 01/02" actively misidentifies [01-design](../01-design/task.md) and [02-data-layer](../02-data-layer/task.md) as the owners of the postponed implementation. Fix: replace the stale slugs in place with the current sibling names (Results); flag the objective's stale references to the orchestrator/planner for the same in-place replacement (objective is planner-owned). Same fold-in artifact class as [11-postponed-core-semantics](../11-postponed-core-semantics/task.md) `## Review Notes`.
2. **MINOR** — Results item 2 cites `[planning.md:122](../../../../../skills/task-tree/references/planning.md#L122)` as an updated site, but `skills/task-tree/references/planning.md` no longer exists (content absorbed into [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md)); the surviving citations also share tasks 11/12's broken 5-up prefix (correct is 4-up), and the cited line anchors have drifted (the orchestration table is now near line 204, `VALID_STATUSES` in internals.md near line 93). Fix: repoint the planning.md citation to the contract and mechanically correct prefixes/anchors.
