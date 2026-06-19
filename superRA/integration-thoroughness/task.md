---
title: "Integration-Review Thoroughness: Min-Net-Diff Baseline + Combined Refactor/Self-Review Pass"
status: approved
depends_on: []
tags: []
created: 2026-06-18
---

## Objective

The INTEGRATE phase's codebase-coherence gate (`refactor-and-integrate` walked at `Stage: integration`) under-enforces, for two structural reasons surfaced in a design session:

1. **The minimum-net-diff prune rule is binary.** `§Minimum Net Diff` / `§Final Diff Self-Check` say "revert it **or** record the justification." That forces both failure modes: an undocumented-but-necessary hunk hits "unjustified → revert" (**Type II: silent deletion of legitimate work**), and to dodge that an agent fabricates a justification (**Type I: silent retention of scope creep**). The justification baseline is the union of documented sources the skill already lists (approved objective, codebase-coherence checklist, task-file coherence, doc currency, logged user decisions, supplied Sync impact) — the task objective is one source, not the whole baseline — but the binary rule has no third branch for a hunk that matches none yet is plausibly load-bearing.

2. **Integrate ran verify-before-do.** `superintegrate` Integrate dispatched the reviewer first and an implementer only reactively for `revise` items, so no agent proactively produced the codebase-fit work or the Final-Diff-Self-Check trail; the reviewer was positioned to check work nobody was dispatched to do.

This workstream installs the agreed fix: a ternary, asymmetric prune rule (never silently delete; confident junk → revert; justified → keep + cite; ambiguous-but-load-bearing → keep and raise it, routing the gap to `superplan`), and a do-then-verify Integrate where the first pass is a combined refactor + self-review that returns review notes, the orchestrator adjudicates (fix or amend) before the independent reviewer runs.

Scope: `skills/refactor-and-integrate/SKILL.md` (discipline), `agents/implementer.md` + its generated artifacts (combined-role permission), `skills/superintegrate/SKILL.md` (choreography). Built on top of commit `b0865e11`, which already generalized the reviewer/implementer verdict gates from "domain" to "stage and domain" skills.

### Conventions

- This is superRA-internal skill-authoring work with no implemented domain vertical. Load `skill-creator` before editing any `skills/*/SKILL.md`, and self-apply the `CLAUDE.md §Teach the Protocol` DRY + Necessity gate to every added line.
- `agents/*` edits are propagated to generated artifacts: rerun `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` and commit the regenerated `.codex/agents/superra_{implementer,reviewer}.toml` and `skills/using-superra/references/direct-mode-{implementer,reviewer}.md` atomically with the source edit.
- `agents/reviewer.md` is intentionally **not** changed: the independent integration reviewer adjudicates review notes the same way regardless of author, and starts from a clean `## Review Notes` (the orchestrator clears first-pass concerns before dispatching it), so its full-first-review semantics are preserved without a special case.

## Results

Shipped on `integrate-thoroughness` off `better-handoff` (`b0865e11`). Integration review APPROVED; repo regression suite 688 passed / 2 skipped; generated-artifact `--check`, `task check`, and markdown self-diagnose all clean.

The INTEGRATE codebase-coherence gate under-enforced for two structural reasons, both fixed:

- **Minimum-net-diff baseline** ([01-min-net-diff-baseline](01-min-net-diff-baseline/task.md)) — the prune rule in `refactor-and-integrate` was binary ("revert or justify"), which forced either silent deletion of undocumented-but-necessary work (Type II) or silent retention of scope creep (Type I). It is now ternary and asymmetric: never silently delete; confident junk → revert; justified → keep + cite a source; scope-ambiguous-but-load-bearing → keep and raise, with the no-source case routed to `superplan` as a stale-task-tree signal.
- **Combined refactor + self-review role** ([02-implementer-integration-self-review](02-implementer-integration-self-review/task.md)) — at `Stage: integration` the implementer's first pass now self-reviews and authors `## Review Notes` for un-adjudicable retained hunks (returning `DONE_WITH_CONCERNS`) — the one documented exception to the implementer's no-review-notes rule, propagated to the Self-Check editing-hygiene checkbox and the `DONE_WITH_CONCERNS` definition so no gate self-contradicts. Codex/direct-mode artifacts regenerated.
- **Do-then-verify Integrate** ([03-superintegrate-integrate-restructure](03-superintegrate-integrate-restructure/task.md)) — `superintegrate` Integrate now runs implementer-first: drift → refactor + self-review pass → orchestrator fix/amend (clearing notes) → independent full-first review → refactor loop → close, with agent count scaled to the post-sync delta and a trivial-diff inline path. `agents/reviewer.md` is deliberately unchanged — the orchestrator's note-clearing preserves its full-first-review precondition.

The branch base `b0865e11` also generalized the reviewer/implementer verdict gates from "domain skill" to "stage and domain skills", so the stage-loaded `refactor-and-integrate` gates are now treated as approval gates.

**Final diff self-check:** `git diff b0865e11..HEAD` (no-op sync; base is an ancestor of HEAD). Surviving-change classes — 3 skill/agent source edits (tasks 01/02/03), 2 regenerated implementer artifacts (`.codex/.../superra_implementer.toml`, `direct-mode-implementer.md`), 4 task records, 1 status cascade. No suspicious hunks: no broad reformatting, no base-side restorations, no unjustified `skills/*`/`agents/*` edits; generated artifacts `--check` clean. Consolidation Gate: clean-enough.
