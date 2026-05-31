---
title: "Reconcile revision-note cleanup duty: point docs at the hook, regenerate reviewer artifacts"
status: not-started
depends_on:
  - revnote-status-sync
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Now that the hook owns the `## Revision Notes` lifecycle (sibling `revnote-status-sync`), remove the now-redundant *manual* revision-note-cleanup duty from the reviewer role and the planning reference so there is one mechanism, not two that can drift. The reviewer keeps owning `## Review Notes` entirely — only the revision-note removal instruction moves to the hook. Load `skill-creator` and apply the repo `CLAUDE.md` DRY + Necessity gate to every line touched.

### 1. `agents/reviewer.md` — drop the manual revision-note removal duty

Today the reviewer is told to remove `## Revision Notes` at APPROVE in several places (verified lines, recheck before editing): `:82` ("Remove `## Revision Notes` if present."), `:86` ("remove both `## Review Notes` and `## Revision Notes`"), `:112` (the `## Revision Notes` ownership bullet), `:116` (the parenthetical exception), `:156` and `:160` (pre-commit self-check items). Edit these so:
- The reviewer no longer performs revision-note removal — the hook does it on the approve transition.
- The reviewer's ownership of `## Review Notes` (write on REVISE, delete confirmed items, remove the empty section at APPROVE) is unchanged.
- Keep the reviewer's *non-edit* boundary intact: the reviewer still must not edit `## Revision Notes` *content* (planner-owned). The change is only that removing it at approve is no longer the reviewer's manual job. One short pointer that the hook handles revision-note cleanup is enough — do not describe the hook's internals (DRY: the behavior is authoritative in `task_hook.py` / `revnote-status-sync`).

### 2. `skills/task-system/references/planning.md` — update the lifecycle description

Lines `:73` and `:127` currently say the reviewer removes `## Revision Notes` when approving. Change both to state that the **hook** removes the section on the approve transition (and, for `:127`'s neighborhood, that adding a revision note to a completed task flips it to `revise`). Keep the "same lifecycle as `## Review Notes`" framing only where still accurate — the *cleanup trigger* now differs (hook vs reviewer), so do not over-claim identical handling.

### 3. `skills/task-system/SKILL.md` — note the automation where revision notes are described

The §Body sections table / revision-note description should reflect that the hook manages the revision-note lifecycle (add-on-completed → `revise`; approve → removed), consistent with the §How to Edit a Task framing from `skill-guidance`. Minimal — one accurate phrase, no internals.

### 4. Regenerate the reviewer artifacts (REQUIRED — generated files)

`agents/reviewer.md` is a generator source. After editing it, run:

```
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py
```

This regenerates `skills/using-superRA/references/direct-mode-reviewer.md` and `.codex/agents/superra_reviewer.toml`. Do NOT hand-edit those two files. Confirm with the generator's check mode (`--check`) and that `skills/codex-superra-setup/scripts/test_sync_codex_agents.py` passes. Commit the regenerated files together with the `agents/reviewer.md` change.

## Validation

- `agents/reviewer.md`, `planning.md`, `SKILL.md` no longer instruct manual revision-note removal; the reviewer's `## Review Notes` duties are intact; the planner-owned-content boundary is preserved.
- `sync_codex_agents.py --check` reports the two generated reviewer files in sync with the edited source; `test_sync_codex_agents.py` passes; the regenerated files are committed (no hand edits).
- DRY/Necessity walk on every changed line: no hook-internal restatement, no duplicated mechanism description across reviewer.md / planning.md / SKILL.md — each points at the hook as the single source of truth.
- Cross-check the historical `task-system/revision-cleanup` task: it assigned this duty to the reviewer; this task supersedes that mechanism. No need to reopen the historical task — just ensure no *live* instruction file still tells the reviewer to remove revision notes manually.

## Notes

Documentation + generated-artifact regeneration only; no `task_hook.py` or test changes (those are `revnote-status-sync`). Depends on `revnote-status-sync` so every doc statement matches shipped hook behavior.
