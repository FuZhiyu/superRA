---
title: "superRA"
status: approved
depends_on: []
tags: []
created: 2026-05-23
---

## Objective

Develop and maintain the superRA repository: the PLAN -> IMPLEMENT -> INTEGRATE research workflow, its task-tree tooling and dashboard, handoff artifacts, and the domain/utility skill library. Active workstreams nest as subtrees under this root.

The largest in-progress workstream is the handoff system — task tracking, planning artifacts, and human-readable visualization — whose integration history is recorded under ## Integration Notes and ## Sync Map below. Separate skill-development workstreams nest alongside it, including [zotero-skills](zotero-skills/task.md) (the MCP-free Zotero paper-reading skill, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` conversion skill).

### Conventions

- [CLAUDE.md](../CLAUDE.md) (aliased by `AGENTS.md`) at repo root is the contributor-facing authority for superRA internals — ownership boundaries, the DRY + Necessity gate, generated-artifact rules. Read it before modifying skills, hooks, agents, harness adapters, or internal docs.
- [README.md](../README.md) is the user-facing product overview; keep product framing there, contributor rules in `CLAUDE.md`.

## Results

Workstream rollup (as of 2026-06-10):

- [task-tree](task-tree/task.md) — the handoff-system workstream: task-tree CLI and data layer, live SSE dashboard server, hooks, migration, and the `task-tree` skill docs. Most subtrees approved and integrated onto the trunk `better-handoff`; current round is record-repair on stale task records.
- [zotero-skills](zotero-skills/task.md) — Zotero paper-reading, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` skill; landed via PRs #31/#33.
- Closed integrations are listed one line each under ## Integration Notes, linking down to the per-task records that carry full detail.

## Integration Notes

- [task-tree/skill-definition/task-tree-rename](task-tree/skill-definition/task-tree-rename/task.md): 2026-06-10 — branch `rename-task-tree` synced through `19322cf3`, integration review APPROVED, full suite + generated-artifact + stale-name checks green; Consolidation Gate clean-enough.
- [task-tree/cli-scripts](task-tree/cli-scripts/task.md): Sync-base decision — `better-handoff` confirmed for the packaged CLI redesign; incoming `postponed` status support preserved.
- [task-tree/task-root-rename](task-tree/task-root-rename/task.md): Sync-base decision — `better-handoff` confirmed.
- [task-tree/task-root-rename](task-tree/task-root-rename/task.md): synced through `981715db` (merge `104d96f3`), integration review APPROVED at `1bfed861`, final checks passed (375 tests + generated-artifact + task-check clean).
- [task-tree/planning-redesign/planmd-sweep](task-tree/planning-redesign/planmd-sweep/task.md): Protect decision — manual integration checks over drift tests for protocol-level results; base `better-handoff`.
- [task-tree/planning-redesign/planmd-sweep](task-tree/planning-redesign/planmd-sweep/task.md): synced through `19457675`, sync + integration reviewed, consolidation completed, targeted tests passed (205).
- [task-tree/dashboard/view-navigation](task-tree/dashboard/view-navigation/task.md): synced through `aad548e3` (merge `018a4f88`), sync + integration reviews APPROVED; dead code pruned, card-flow tests added (244 passing).
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): merged `plan/codex-task-hooks` into `better-handoff` from base `66693ccf`; `updated` frontmatter metadata removed tree-wide; verification passed (288 tests + task-check).
- [task-tree/planning-redesign/review-planning-protocol](task-tree/planning-redesign/review-planning-protocol/task.md): synced through `75a86cce` (merge `1d14b1f1`), fix round landed `2afde1d2`, re-review APPROVED at `59d1ee4`; final validation passed (379 tests + generated-artifact + task-check clean).
- [task-tree/planning-redesign/review-planning-protocol](task-tree/planning-redesign/review-planning-protocol/task.md) + [task-tree/cli-scripts/path-containment](task-tree/cli-scripts/path-containment/task.md): PR #29 follow-up integrated onto `better-handoff`, synced through `876178e3` (merge `76c2a9af`), sync + integration reviews APPROVED; checks passed (216 tests + generated-artifact + task-check clean).
- [integ-workflow](task-tree/agent-interface/integ-workflow/task.md): 2026-06-01 — integrate-cleanup redesign integrated onto `better-handoff` (merge `014dbcec`, one MAJOR fixed `11e1214b`, re-review APPROVED `4e6a67ac`); Protect = manual prose-coherence checks; suite green (247); Consolidation Gate clean-enough. The integration's Project Doc Audit walk found no additional `AGENTS.md`/`CLAUDE.md`/`README.md` under its touched paths (`agents/`, `skills/task-tree/`, `skills/superplan/`, `skills/using-superRA/`, `.codex/`, the review-planning-protocol subtree) and intentionally skipped unrelated guidance under `skills/theory-modeling/`, `skills/writing/`, `tests/claude-code/`.
- [task-tree/cli-scripts](task-tree/cli-scripts/task.md): synced through `9ca25479` (merge `136a19c9`), integration review APPROVED `abe49e78`, packaged-CLI smoke + checks green (333 tests); Consolidation Gate clean-enough.
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): Sync-base decision — local `better-handoff` confirmed before `04-docs-tests-and-compat`.
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): 2026-06-02 — Sync re-check no-op (base already an ancestor; incoming range empty).
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): Protect decision 2026-06-02 — existing regression/compatibility tests sufficient for this non-numeric hook-packaging result set.
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): Integrate closed, review APPROVED `2fade6f2`; validation passed (232 tests + hook tests 14/14 + task-check); Consolidation Gate clean-enough.
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): 2026-06-02 — documentation maturation review APPROVED; parent `## Results` is the permanent record.
- [task-tree/dashboard/serve-lifecycle](task-tree/dashboard/serve-lifecycle/task.md): 2026-06-04 — governing base `8c70b4e1` (tag `pre-serve-lifecycle`); Sync no-op; Protect = the feature's 23 regression tests; integration review APPROVED; suite green (484); Consolidation Gate clean-enough.
- [task-tree/dashboard/mobile-ipad-ui](task-tree/dashboard/mobile-ipad-ui/task.md): 2026-06-04 — adaptation-only touch UI; clean non-overlapping sync (merge `509744ef`); Protect = shipped touch-behavior regression tests; integration review APPROVED; squash-merged via `dashboard-mobile-ui`; Consolidation Gate clean-enough.
- [task-tree/cli-scripts/cli-source-resolution](task-tree/cli-scripts/cli-source-resolution/task.md): 2026-06-07 — uvx-resolver integration (synced `1a9f2916`, review APPROVED `cc21203a`, suite 569). **Superseded 2026-06-08** by the `uv run --script` rework below; see the task's record.
- [task-tree/cli-scripts/cli-source-resolution](task-tree/cli-scripts/cli-source-resolution/task.md): 2026-06-08 — `uv run --script` rework landed (PEP 723 single dependency source, `pyproject.toml` dropped, committed wrapper as universal agent entry); integration coherence review APPROVED `b89d308d`; suite 596/2 skipped on Python 3.12 and 3.14; Consolidation Gate clean-enough.
- Release-prep CLAUDE.md-discipline integration review: 2026-06-08 — audited the `5dfe928b..HEAD` skills/agents prose delta against the Teach-the-Protocol gate; 14 findings fixed plus follow-ups; generated artifacts regenerated and check-clean; suite green (603/2); Consolidation Gate clean-enough.

## Sync Map

- [task-tree/skill-definition/task-tree-rename](task-tree/skill-definition/task-tree-rename/task.md): synced local `better-handoff` (`19322cf387dd2096a436e0401815804e1c21fe9f`) into `rename-task-tree` on 2026-06-10 from merge base `6e88cd51771acf4e34da475bf396eabab6e5ded0`. Material overlap was the skill/task tree rename versus incoming dashboard browser auto-open work committed under the old `skills/task-system` and `superRA/task-system` paths. Resolution carried the source/test changes into `skills/task-tree/scripts/plan_dashboard.py` and `skills/task-tree/scripts/test_task_tree.py`, relocated `03-browser-auto-open` under `superRA/task-tree/dashboard/serve-lifecycle/`, and updated the merged task record to cite task-tree paths and commands.
- [task-tree/codex-task-hooks](task-tree/codex-task-hooks/task.md): merged `better-handoff-impl/semantic-move-hook-json-agent/parallel/posttooluse-empty-json` into `better-handoff` on 2026-06-10 from merge base `8f5dd1d5`. Resolution preserved the incoming Codex parseable empty-JSON hook behavior, updated active task-hook internals documentation, and folded the temporary `06-posttooluse-empty-json` update task into the durable approved `codex-task-hooks` parent rather than leaving an integration-stage update task standing.
- [task-tree/dashboard/github-artifact-action](task-tree/dashboard/github-artifact-action/task.md): synced against local `better-handoff` on 2026-06-04. Feature-branch pre-sync merge base = `35feea5f`; artifact branch head = `73212f9b`; first incoming `better-handoff` head = `6b6d4d30`; final integration base head = `1069da5f`. Material code overlap was the dashboard command surface and docs/tests: incoming made `superra dashboard` background-by-default with `--foreground` and `superra dashboard stop`, while this branch added `superra dashboard artifact setup`. Resolution keeps both command paths, preserves browser auto-open for plain `superra dashboard` unless `--no-open` is passed, routes artifact setup without invoking the dashboard server, and preserves the base-side mobile/iPad dashboard integration record from `1069da5f`.
- [zotero-skills](zotero-skills/task.md): synced `origin/main` (PR #31, commit `5dfe928b`) into the trunk on 2026-06-05. Incoming is purely additive — the MCP-free `zotero-paper-reader` skill, the vendored `mistral-pdf-to-markdown` skill, their tests, and `README.md` / `skills/CATEGORIES.md` / `skills/using-superRA/SKILL.md` inventory entries. Two conflicts: `.gitignore` resolved by union (kept the trunk's `.plan/` + `**.pyc` entries, added `superRA/dashboard.html`); `superRA/task.md` was an add/add collision of two unrelated roots. Per researcher decision the trunk root was reframed from "Better Handoff" to the repo-level "superRA" root, and the incoming zotero workstream root + its 01–06 task subdirs were relocated as the `zotero-skills/` subtree (no content loss). Dashboard regenerated to reflect the new tree.
- [zotero-skills](zotero-skills/task.md): synced local `main` (`b797260c`, PR #33 plus the #32 Mistral dependency fix) into `better-handoff` on 2026-06-09 from merge base `5dfe928b`. Incoming added BibTeX export, citation insertion, bibliography rendering, Better BibTeX key support, and related tests/docs. Resolution preserved the branch's repo-level `superRA/task.md`, relocated incoming tasks 07-10 into the existing `zotero-skills/` subtree, and kept the task-specific results under [zotero-skills](zotero-skills/task.md) rather than restoring the old standalone Zotero root.

