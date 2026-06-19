---
title: "superRA"
status: approved
depends_on: []
tags: []
created: 2026-05-23
---

## Objective

Develop and maintain the superRA repository: the PLAN -> IMPLEMENT -> INTEGRATE research workflow, its task-tree tooling and dashboard, handoff artifacts, and the domain/utility skill library. Active workstreams nest as subtrees under this root.

The largest in-progress workstream is the handoff system — task tracking, planning artifacts, and human-readable visualization — whose integration history is recorded under ## Integration Notes below. Separate skill-development workstreams nest alongside it, including [zotero-skills](zotero-skills/task.md) (the MCP-free Zotero paper-reading skill, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` conversion skill), [01-add-slide-design-domain-vertical](01-add-slide-design-domain-vertical/task.md) (the slide-design domain vertical), and [showcase-analysis](showcase-analysis/task.md) (a real CAPM-vs-FF3 empirical asset-pricing study run end-to-end through the workflow to serve as the documentation showcase, wired into the docs site under [docs-site/13-real-analysis-showcase](docs-site/13-real-analysis-showcase/task.md)).

### Conventions

- [CLAUDE.md](../CLAUDE.md) (aliased by `AGENTS.md`) at repo root is the contributor-facing authority for superRA internals — ownership boundaries, the DRY + Necessity gate, generated-artifact rules. Read it before modifying skills, hooks, agents, harness adapters, or internal docs.
- [README.md](../README.md) is the user-facing product overview; keep product framing there, contributor rules in `CLAUDE.md`.

## Results

Workstream rollup (as of 2026-06-10):

- [task-tree](task-tree/task.md) — the handoff-system workstream: task-tree CLI and data layer, live SSE dashboard server, hooks, migration, and the `task-tree` skill docs. Most subtrees approved and integrated onto the trunk `better-handoff`; current round is record-repair on stale task records.
- [zotero-skills](zotero-skills/task.md) — Zotero paper-reading, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` skill; landed via PRs #31/#33.
- [01-add-slide-design-domain-vertical](01-add-slide-design-domain-vertical/task.md) — slide-design domain vertical with audience-context discipline, Beamer starter assets, layout-triage script, discovery-surface wiring, and trigger tests; landed via PR #35 and synced from `origin/main`.
- [sync-better-handoff](sync-better-handoff/task.md) — freshness re-sync of trunk `better-handoff` (42 commits) into this doc-redesign branch: merge all incoming skill/hook/test/code changes, then fold the post-fork features (slide-design vertical, writing deep-review, the `using-superra` case fix) into the redesigned doc IA.
- Closed integrations are listed one line each under ## Integration Notes, linking down to the per-task records that carry full detail.

## Integration Notes

- [docs-site](docs-site/task.md) + [showcase-analysis](showcase-analysis/task.md): 2026-06-18 — docs-site redesign (reading-flow IA, skills nested into the site + standalone reference dissolved, canonical quickstart/showcase pages) plus the real CAPM-vs-FF3 study dogfooded into the docs and a `sync-better-handoff` trunk freshness re-sync, squash-merged into `better-handoff` (`ff5f94e7`); docs-only delta (no `skills/`/`agents/`), integrate review APPROVED, docs build + render-integrity 27/27 + task-tree suite 690 + contract 56/56 green; Consolidation Gate clean-enough; permanent rollups in the docs-site and showcase-analysis `## Results`.
- [task-tree/agent-interface/writing-review-task-trees](task-tree/agent-interface/writing-review-task-trees/task.md): 2026-06-18 — writing-domain deep-review task-tree update integrated onto `better-handoff`; sync `dd33e301` (+ propagation `3950dc57`), integrate review APPROVED, drift = updated `test-sync-integration-contract.sh` (56/56) + full task-tree suite (690); Consolidation Gate clean-enough; closeout in the task `## Results`.
- [task-tree/dashboard/readability-redesign](task-tree/dashboard/readability-redesign/task.md): 2026-06-15 — docs-site build + dashboard readability redesign squash-merged into `better-handoff` (base re-resolved `221a7934`→`38eb36ef` at finish); integrate review APPROVED, DOMPurify gate + suite 684/2; Consolidation Gate clean-enough; permanent rollup in the readability-redesign parent `## Results`.
- `better-handoff` → `origin/main` integration (`BASE_HEAD_SHA=03b68d6b`) deferred to a future trunk-to-main PR; the stale shell-test contract findings were resolved in the 2026-06-17 `origin/main` sync.
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
- [integ-workflow](task-tree/agent-interface/integ-workflow/task.md): 2026-06-01 — integrate-cleanup redesign integrated onto `better-handoff` (merge `014dbcec`, one MAJOR fixed `11e1214b`, re-review APPROVED `4e6a67ac`); Protect = manual prose-coherence checks; suite green (247); Consolidation Gate clean-enough. The integration's Project Doc Audit walk found no additional `AGENTS.md`/`CLAUDE.md`/`README.md` under its touched paths (`agents/`, `skills/task-tree/`, `skills/superplan/`, `skills/using-superra/`, `.codex/`, the review-planning-protocol subtree) and intentionally skipped unrelated guidance under `skills/theory-modeling/`, `skills/writing/`, `tests/claude-code/`.
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
