---
title: "superRA"
status: approved
depends_on: []
tags: []
created: 2026-05-23
---

## Objective

Develop and maintain the superRA repository: the PLAN -> IMPLEMENT -> INTEGRATE research workflow, its task-tree tooling and dashboard, handoff artifacts, and the domain/utility skill library. Active workstreams nest as subtrees under this root.

The largest in-progress workstream is the handoff system — task tracking, planning artifacts, and human-readable visualization — whose integration history is recorded under ## Integration Notes below. Separate skill-development workstreams nest alongside it, including [zotero-skills](zotero-skills/task.md) (the MCP-free Zotero paper-reading skill, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` conversion skill) and [01-add-slide-design-domain-vertical](01-add-slide-design-domain-vertical/task.md) (the slide-design domain vertical).

### Conventions

- [CLAUDE.md](../CLAUDE.md) (aliased by `AGENTS.md`) at repo root is the contributor-facing authority for superRA internals — ownership boundaries, the DRY + Necessity gate, generated-artifact rules. Read it before modifying skills, hooks, agents, harness adapters, or internal docs.
- [README.md](../README.md) is the user-facing product overview; keep product framing there, contributor rules in `CLAUDE.md`.

## Results

Workstream rollup (as of 2026-06-10):

- [task-tree](task-tree/task.md) — the handoff-system workstream: task-tree CLI and data layer, live SSE dashboard server, hooks, migration, and the `task-tree` skill docs. Most subtrees approved and integrated onto the trunk `better-handoff`; current round is record-repair on stale task records.
- [zotero-skills](zotero-skills/task.md) — Zotero paper-reading, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` skill; landed via PRs #31/#33.
- [01-add-slide-design-domain-vertical](01-add-slide-design-domain-vertical/task.md) — slide-design domain vertical with audience-context discipline, Beamer starter assets, layout-triage script, discovery-surface wiring, and trigger tests; landed via PR #35 and synced from `origin/main`.
- Closed integrations are listed one line each under ## Integration Notes, linking down to the per-task records that carry full detail.

## Workflow Status

Integration of `writing-review-task-trees` into trunk `better-handoff` (2026-06-18). Scope: [task-tree/agent-interface/writing-review-task-trees](task-tree/agent-interface/writing-review-task-trees/task.md), the writing-domain deep-review task-tree workflow update. Completion disposition from superimplement Step 4: proceed with integration. `BASE_REF=better-handoff` (researcher confirmed).

- [ ] Drift tests created
- [ ] Integrated
- [ ] Docs finalized
- [ ] Final action

Integration of `better-handoff-doc` into trunk `better-handoff` (2026-06-15). Whole-branch scope (researcher decision): the docs-site build plus the dashboard readability redesign. `BASE_REF=better-handoff`. The integration review ran against `221a7934..HEAD` while the trunk sat at `221a7934`. At finish the trunk had advanced one commit to `38eb36ef` ("sharpen skill descriptions and finish the manifest-restructure sweep"), so `BASE_HEAD_SHA` was re-resolved to `38eb36ef` and the work re-synced against it (see Final action below). Final action: squash-merge into `better-handoff` (researcher decision).

- [x] Drift tests created — Protect: behavioral contracts are the key results for this tooling branch; protection = the full dashboard suite (684 passed / 2 skipped on HEAD), now including the readability round's locks (`TestRawHtmlSanitization` HTML-sanitization security gate plus the doc-mode / typography structural checks in `test_dashboard.py`). No new drift tests authored — every task is approved with no scope change, and authoring is scoped to non-approved/related tasks.
- [x] Integrated — whole-branch integration review of `221a7934..HEAD` APPROVED; delta minimal, every hunk tied to an approved objective or doc-currency fix, DOMPurify security gate verified, vendored-asset SHAs match, no generated artifacts in delta, suite 684/2. Four non-blocking advisories adjudicated: (1) `_site/` added to `.gitignore` this pass; (2) `docs-site.yml` `paths` omits `superRA/**` — accepted (dev-tree export is a snapshot; avoids noisy rebuilds); (3) no `docs/CLAUDE.md` — deferred (low value, mitigated by `build_site.sh` header + the IA authoring contract); (4) homepage `http://` vs `https://` in README/plugin manifests — left as implementer-chosen, flagged for researcher (depends on live custom-domain HTTPS state).
- Consolidation Gate: clean-enough — placement check passes, no misplaced or episodic tasks; the readability-redesign subtree is properly homed under `task-tree/dashboard/`.
- [x] Docs finalized — maturation review APPROVED (doc-reviewer, no findings); the [readability-redesign](task-tree/dashboard/readability-redesign/task.md) parent `## Results` is the permanent reader-facing rollup, fact-checked against child Results and code (type roles, DOMPurify 3.4.10 + SHA, doc-mode scoping, recomputed contrast residuals, the `<ol>` diagram, all six child links, suite 684/2, the four deferred follow-ups). docs-site leaf Results were already matured at implementation time.
- Post-review refinement (direct-edit, in-lane): after live review on a wide display, the dashboard reading measure was widened (72ch → `--measure: 96ch`) and the reading column centered at `max-width: 100ch` in both tracker and doc-mode (doc-mode's 76ch `#active-node` override collapsed into the shared rule). Verified live on the real user path; suite re-run green (684/2); no tests hardcoded the old measure. Recorded in the readability-redesign parent `## Results` §Integration refinement. Too small to re-dispatch a reviewer.
- [x] Final action — squash-merged `better-handoff-doc` into `better-handoff` (2026-06-15). Base-freshness check at finish found the trunk had advanced from `221a7934` to `38eb36ef` (one commit, a skill-description/manifest-restructure sweep). Re-sync: the only file both sides touched is [report-in-markdown/SKILL.md](../skills/report-in-markdown/SKILL.md) in disjoint regions — trunk trimmed the frontmatter `description:`, our task-02 work added the `## Raw HTML` body section — so the 3-way squash-merge applies both with no conflict; all other trunk-swept files (skill descriptions, manifest, agent specs, theory/econ skills) are disjoint from the docs/dashboard delta. Squash-merge base = `38eb36ef`.

The prior `better-handoff` → `origin/main` integration episode (`BASE_HEAD_SHA=03b68d6b`) is deferred to a future trunk-to-main PR. Its stale shell-test contract findings were resolved during the 2026-06-17 `origin/main` sync: the sync-integration contract now checks the current no-Sync-Map protocol, the manifest carries qualified domain skill ids, and `tests/check-harness-compatibility.sh` passes.

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
