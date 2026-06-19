---
title: "Implementer Combined-Role Self-Review at Stage: integration"
status: approved
depends_on: []
tags: []
output:
  - agents/implementer.md
  - .codex/agents/superra_implementer.toml
  - skills/using-superra/references/direct-mode-implementer.md
created: 2026-06-18
---

## Objective

The integration first pass is a combined refactor + self-review role: the implementer fits the post-sync diff to the host project **and** surfaces hunks it could not adjudicate, so writing `## Review Notes` becomes part of that role rather than an ownership violation. Encode this in `agents/implementer.md`.

- Add a stage-conditional behavior (smallest placement that the integration first pass will read — e.g. in the Self-Check gate-walk or §What You Own): at `Stage: integration`, the first pass also self-reviews the governing diff and records each scope-ambiguous retained hunk it cannot adjudicate as a `## Review Notes` item (`file:line` + why it was kept and what source it fails to match), then returns `DONE_WITH_CONCERNS`. It still sets `status: implemented` (it does not set the verdict) and still may not edit or delete any *other* review item or reviewer prose.
- This is the one narrow exception to "the implementer does not write `## Review Notes`"; state it as the combined-role behavior, not as a loophole. The concerns are a handoff to the orchestrator (consumed at [03-superintegrate-integrate-restructure](../03-superintegrate-integrate-restructure/task.md) Step 3), not to the reviewer.
- Do **not** restate the prune discipline from [01-min-net-diff-baseline](../01-min-net-diff-baseline/task.md) here — point or rely on the loaded skill; this file owns only the role permission and the status/return convention.
- Regenerate the implementer's generated artifacts: run `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` and commit `agents/implementer.md` together with the regenerated `.codex/agents/superra_implementer.toml` and `skills/using-superra/references/direct-mode-implementer.md` (the reviewer-side generated files should be unchanged this task). Verify with `--check` that targets match.

Validation: an integration first-pass implementer can determine from `agents/implementer.md` alone that it self-reviews and records residual concerns as review notes at `implemented`/`DONE_WITH_CONCERNS`; `sync_codex_agents.py --scope project --check` passes; passes `CLAUDE.md §Teach the Protocol` DRY + Necessity (no restating of prune discipline or the manifest).

## Results

Encoded the combined refactor + self-review permission in [agents/implementer.md §What You Own](../../../agents/implementer.md), then regenerated the implementer-side artifacts.

- **Placement:** added one stage-conditional bullet to §What You Own (the section that defines the role's task ownership, where "the implementer does not author `## Review Notes`" is implicit). At `Stage: integration` only, the first pass self-reviews the governing diff after fitting it to the host project, records each scope-ambiguous retained hunk it cannot adjudicate as a `## Review Notes` item (`file:line`, why kept, which source it fails to match), sets `status: implemented` (does not set the verdict), and returns `DONE_WITH_CONCERNS`. Stated as the one combined-role exception, not a loophole; it still may not edit or delete any *other* review item or reviewer prose.
- **Internal consistency:** the exception is propagated to the two other places in the file that assumed the old rule — the Self-Check editing-hygiene checkbox (line 54, "only appended" clause made stage-conditional) and the `DONE_WITH_CONCERNS` definition (line 116, `## Review Notes` added as a concern home) — so an integration first-pass implementer never walks a gate that contradicts §What You Own.
- **DRY/Necessity:** the prune discipline that classifies these hunks is pointed to ("lives in the loaded `refactor-and-integrate`"), not restated — this file owns only the role permission and the status/return convention. No manifest restatement.
- **Generated artifacts:** ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; only the implementer-side [.codex/agents/superra_implementer.toml](../../../.codex/agents/superra_implementer.toml) and [skills/using-superra/references/direct-mode-implementer.md](../../../skills/using-superra/references/direct-mode-implementer.md) were rewritten (reviewer-side files unchanged, as expected).

**Verification:** `sync_codex_agents.py --scope project --check` → exit 0 ("All generated agent files are up to date" / "All generated direct-mode role references are up to date"). `git status` shows exactly the three output files changed; the new bullet is present in both generated artifacts at their respective §What You Own.

**Final diff self-check:** `git diff b0865e11..HEAD -- agents/implementer.md .codex/agents/superra_implementer.toml skills/using-superra/references/direct-mode-implementer.md`. The `agents/implementer.md` hunks are the suspicious `agents/*` instruction-prose class, justified line by line against this task objective: one new §What You Own bullet granting the `Stage: integration` combined-role review-note authorship, plus two consistency edits (the editing-hygiene checkbox and the `DONE_WITH_CONCERNS` definition) propagating that exception to the only two other places that assumed the old rule. The prune discipline is pointed to, not restated; no manifest restatement — passes `CLAUDE.md §Teach the Protocol` DRY + Necessity. The two `.toml`/direct-mode hunks are faithful regenerations (not hand-edits), confirmed by `sync_codex_agents.py --scope project --check` → exit 0; reviewer-side generated files correctly untouched. No codebase-fit change needed this integration pass; `check_markdown.py` on `agents/implementer.md` clean.
