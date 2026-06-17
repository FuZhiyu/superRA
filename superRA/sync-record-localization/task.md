---
title: "Localize the Sync Record: Drop Sync Map + SEMANTIC_MERGE.md, Keep Temporary Task-Local ## Sync Impact"
status: not-started
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Realign the semantic-merge skill and the INTEGRATE-phase skills (`superintegrate`, `refactor-and-integrate`) to the current task-tree contract. The legacy design assumed a single `PLAN.md` file with a "header" that served as a natural home for a branch-level sync summary; the current design is a directory of `task.md` files with no central summary home. Three drifts follow from that and are the scope of this workstream:

1. **Eliminate the branch-level `## Sync Map`.** The sync's branch-level narrative belongs in the git log (the merge commit plus any propagation commit messages), not a `## Sync Map` dumped onto the root `superRA/task.md`. The only sync record that lives in the task tree is the **localized, temporary `## Sync Impact`** section on each affected task.
2. **Standardize and re-anchor task-local sync context as a `## Sync Impact` section.** It is currently described three inconsistent ways (inline `**Sync impact:**` field anchored after a dead `**Integration status:**` field in semantic-merge; `## Sync Impact` section in superintegrate; `**Sync impact:**` field in refactor-and-integrate). The single canonical form is a `## Sync Impact` **section heading**, self-contained, with an enforced cleanup mechanism because it is temporary scaffolding.
3. **Delete `SEMANTIC_MERGE.md`.** Standalone-merge records belong in the commit body / git log, by the same "git for change" principle, not a tracked doc file.

Alongside these, sweep the stale terminology the redesign left behind: "task block(s)" (tasks are `task.md` files, referenced by path), "handoff doc(s)/artifact(s)/record" (the handoff-doc skill is deprecated), and the dead inline `**Integration status:**` field (integration review reuses the single `status:` frontmatter field). Align the sync author / sync reviewer dispatch-and-return to the current reporting model.

### Conventions

- **This is skill/contributor editing — load `skill-creator` before editing any `skills/*/SKILL.md` or reference, per the repo CLAUDE.md.** Self-apply the "Teach the Protocol, Don't Prescribe Each Action" gate (DRY + Necessity) to every line touched; the goal is a *leaner* surface, not more prose.
- **One source of truth per concern.** The canonical localized-Sync-Impact model is authored once in `01-canonical-model` (owner: `semantic-merge/references/workflow-sync-author.md` + `task-tree/references/task-file-contract.md`); every other task points to it rather than restating the format.
- **Reporting model:** commit message = change summary; agent return = status + SHA. With `## Sync Map` removed, the sync author/reviewer verbose return blob collapses to status + the sync commit SHA(s); the branch narrative is the commit messages.
- **Sync-review findings use the standard review mechanism:** task-scoped sync findings go in that task's `## Review Notes`; a branch-level finding with no single task home rides the REVISE return and is fixed before re-review. There is no separate "Sync review notes" home now that `## Sync Map` is gone.
- **User decisions during sync** are folded into the relevant task `## Objective` (durable) and recorded in the commit body — never a doc file.

### Constraints

- Do not touch `docs/plans/*` or `docs/process-issues-*` — those are dated historical records of the old design and stay as-is.
- The working tree currently carries an unrelated in-flight terminology sweep ("analysis branch/scope" → "feature branch / task scope") in several of the same files. That must be committed before this workstream starts so implementers branch from a clean base; see §Planner Guidance.
- No task here edits generated artifacts (direct-mode role references, Codex `.toml`). If any agent-spec edit surfaces, route it through `sync_codex_agents.py` rather than hand-editing.

## Planner Guidance

Suggested ordering: `01-canonical-model` is the keystone and must land + approve first; `02`–`05` are file-disjoint and parallelizable after it.

Verification across the workstream is grep-based plus the task-tree test suite for `04`: after the tree is approved, no `## Sync Map`, `SEMANTIC_MERGE.md`, `**Integration status:**`, or "task block" survives in `skills/` or `CLAUDE.md` (historical `docs/plans/*` excluded), and `./superRA/superra task check` cleanly flags a lingering `## Sync Impact`.

Pre-start housekeeping: commit the in-flight vertical-neutral terminology sweep (`git diff --stat` shows it across superintegrate, refactor-and-integrate, semantic-merge worktree ref, superimplement, superplan, docs/site, agents/implementer.md, the codex toml) as its own commit titled e.g. `skills: generalize analysis→feature/task terminology` before dispatching any implementer.
