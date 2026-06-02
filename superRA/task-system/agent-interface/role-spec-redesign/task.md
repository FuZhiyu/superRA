---
title: "Role-Spec Redesign — Clean, Deduplicated, No Knowledge Lost"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Redesign and restructure the two canonical role specs — [agents/implementer.md](../../../../agents/implementer.md) and [agents/reviewer.md](../../../../agents/reviewer.md) — so they read as clean, logically ordered, duplication-free instructions an agent can follow top-to-bottom, **while losing no behavior-shaping instruction**.

The specs accreted across many incremental passes (`../lean-interface` relocated the universal core; `../agent-protocols` and `../../../review-planning-protocol` did targeted protocol updates) and are now structurally messy: sections sit out of execution order, the implementer carries two overlapping self-check lists, the reviewer's verdict/severity mechanics are duplicated between §Review Protocol and §Handoff, the reviewer's §Before You Start numbering is broken (1, 2, 3, 5), planning-review mode is duplicated against the planning workflow, the commit-message rule is underspecified, and the two files use divergent section names for the same role concepts. The deliverable is two **parallel-structured** specs plus all coupled agent-facing surfaces brought into coherence, verified by a no-knowledge-lost audit.

This is a new concern — a holistic clarity restructure — not a reopening of the approved tasks that previously edited these files. Those tasks shipped specific content changes; this subtree changes how that content is organized and worded.

### Context

**The user's outstanding edits and inline comments are design intent, not noise.** Before this subtree was written, the user hand-edited the four affected files and left `<!-- ... -->` comments marking what they want. Treat every such comment as a binding requirement and resolve it (do not leave the comment in the shipped file). The known ones:

- implementer §Self-Review Before Reporting — "this section is a bit messy in order; reorder it; this should be right before the commit section."
- implementer §Self-Review — "add check to clean up the stale content" (the user deleted the old Reproducibility sub-block; its surviving guidance must be accounted for in the coverage audit).
- implementer commit block — "design a clearer rule for the commit message: appropriate heading, what to write; focus on the delta not the full results (`git for change, files for the latest status`); differentiate vs the report format — they should probably be the same." Resolved below under §Conventions → Commit convention.
- reviewer §Planning Review Mode — "planning review should just be a reference under the planning workflow rather than duplicated here." Resolved by task 01.
- reviewer persona — the user added a paragraph granting the reviewer its own judgment beyond the checklists; keep it.

**The user's framing:** most comments sit in the implementer file, but **many apply equally to the reviewer** — apply each insight symmetrically to both specs (commit convention, self-check-before-commit ordering, positive ownership framing, persona simplification).

**The generator is coupled by exact section headings.** [skills/codex-superra-setup/scripts/sync_codex_agents.py](../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) parses the specs by hardcoded `##`/`###` headings and string-matches specific paragraphs (`render_direct_mode_ref`, `render_*_direct_mode_before_you_start`, `cleanup_implementer_handoff`, `strip_subsection`). The user's in-progress rename of `## Handoff — Unified Across Stages` → `## Handoff` already breaks it (`--check` raises `KeyError`). Any section rename/reorder/merge therefore requires updating the generator and its test [skills/codex-superra-setup/scripts/test_sync_codex_agents.py](../../../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py) in lockstep.

### Conventions

**Shared target skeleton (both specs follow the same section order).** Where a section is role-specific, the role's name is in brackets. This is the binding structure; exact prose is the implementer's craft, but the order and the dedup decisions below are not optional.

1. Persona + stance (preface, no heading) — one line of role identity plus the role's core stance (implementer: evidence-first; reviewer: adversarial + own-judgment-beyond-checklists). Plus the Codex skill-load line.
2. `## Before You Start` — a one-line lead on the dispatch inputs, then the numbered load-skills / read-task steps. Fix the reviewer's numbering.
3. `## Execution Protocol` [implementer] / `## Review Protocol` [reviewer] — the core work discipline. The reviewer's severity levels and verdict are defined **once** here; later sections reference them rather than restating.
4. `## Self-Check` — placed immediately before Handoff/commit. The implementer's current `### Self-Review Before Reporting` and `## Pre-Commit Self-Check` merge into **one ordered gate** (evidence-before-claims → completeness → stale-content cleanup → domain checklist walk → editing-hygiene checklist). The reviewer gets a parallel pre-commit self-check in the same slot.
5. `## Handoff` (identical heading in both; drop "— Unified Across Stages") — subsections in this order: What You Own (positive framing only; drop "What You Don't"), Editing Etiquette (point to `using-superra` §Task Interface + the one role-specific rule), How You Fix [implementer] / How You Write [reviewer] the REVISE round (reference the §Protocol verdict/severity, don't restate), Commit.
6. `## Report Format` — the minimal status return: the status enum + the commit SHA, nothing re-authored (see Reporting model). For `BLOCKED`/`NEEDS_CONTEXT` the return carries the blocker instead of a SHA.
7. `## Escalation` [implementer] / the closing `ACTION REQUIRED` line [reviewer].

**Reporting model (resolved).** Three surfaces, no duplication:
- **`## Results` (task.md)** — the latest *state*: self-contained and human-readable, with the links/references and embedded figures a reader needs. Not a changelog.
- **git commit** — the *change summary*, authored **once**: subject `implement task <task-path>` / `review task <task-path>` (no status/verdict in the subject — that lives in `status:`), body = what changed this dispatch and why (`git for change, files for the latest status`). Point to `using-superra` §Commit Hygiene for staging.
- **status return (the response)** — minimal control + pointer: the status enum (implementer `DONE`/`DONE_WITH_CONCERNS`/`BLOCKED`/`NEEDS_CONTEXT`; reviewer `APPROVE`/`REVISE`) plus the commit SHA. The summary is **not** re-authored here — the orchestrator reads it from the commit and the state from `## Results`. Exception: `BLOCKED`/`NEEDS_CONTEXT` produce no commit, so the return carries the blocker/missing-context instead of a SHA.

**No-knowledge-lost invariant (load-bearing).** Every distinct behavior-shaping instruction present in the four files before this subtree must still be present somewhere after, and still reachable by every role that needs it through that role's real load path. Removing a duplicate is fine (the one surviving copy must stay reachable); removing or stranding the only copy is not. Task 04 proves this against a git snapshot of the pre-redesign surfaces.

**Contributor gates (apply to every child task; from repo `CLAUDE.md`).**
- Load `skill-creator` before editing any `skills/*/SKILL.md`. Treat all spec/skill text as skill creation.
- Apply the "Teach the Protocol, Don't Prescribe Each Action" gate line by line: every line passes DRY (point, don't paraphrase what another skill/reference/role spec already carries) and Necessity (delete a line that only tells the agent what it would already do). This subtree removes duplication; do not reintroduce it.
- Generated files — [skills/using-superRA/references/direct-mode-implementer.md](../../../../skills/using-superRA/references/direct-mode-implementer.md), [direct-mode-reviewer.md](../../../../skills/using-superRA/references/direct-mode-reviewer.md), [.codex/agents/superra_implementer.toml](../../../../.codex/agents/superra_implementer.toml), [.codex/agents/superra_reviewer.toml](../../../../.codex/agents/superra_reviewer.toml) — are produced from the specs by `sync_codex_agents.py`. Edit the source + the generator, then regenerate; never hand-edit a generated file. Regen + `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` + `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` is a `[BLOCKING]` gate on any task that changes a spec or the generator.
- Scope all edits to this worktree: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff-skill-instruction`.

## Planner Guidance

Order: 01 first; then 02 (coupled surfaces) and 03 (reporting model) both build on 01 and touch disjoint files (02 = `using-superRA` + `report-in-markdown`; 03 = the role specs + generator), so either order works; 04 (coverage audit) runs last and depends on both.

The structural work is concentrated in task 01 (rather than split across a separate planning-review-relocation task) because the generator parses the specs by exact section headings: any partial heading/structure change leaves `sync_codex_agents.py --check` failing, so all structural changes plus the generator reconciliation must land in one atomic task. Task 01 is therefore large and high-synthesis — dispatch it on a higher-capability model.

Task 03 (reporting model) was added after task 01 was approved, when the researcher refined the commit/report relationship into the single-summary model now in §Conventions. It supersedes task 01's §Report Format / §Commit; the coverage audit verifies the combined final state.

## Results
