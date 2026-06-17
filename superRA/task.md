---
title: "Slide Design Domain Vertical"
status: approved
depends_on: []
tags:
  - skill-creation
  - slide-design
created: 2026-05-26
---

## Objective

Add a `slide-design` domain vertical to superRA: a domain skill that teaches agents audience-context discipline for research presentation slides — context engineering, attention management, simplification, and the communication-vs-rigor tradeoff — with Beamer-first implementation support (a house starter template, overlay/technique references, and a nonvisual layout-triage script), wired into the skill-discovery surfaces and verified at the script level.

### Context

The vertical composes the existing PLAN → IMPLEMENT → INTEGRATE workflow with a new domain skill; the workflow, agent, orchestration, and generic utility skills carry over unchanged. Skill edits follow `skill-creator` and keep instructions minimal and behavior-shaping. A new domain vertical registers in `skills/using-superRA/SKILL.md` (skill inventory + domain add-on table), `skills/superplan/SKILL.md` (Phase 2 "Currently implemented verticals" table), `skills/CATEGORIES.md`, `README.md`, and the skill-triggering test harness.

### Constraints

This repo is **public**: skill artifacts must not embed personal data. The Beamer starter template and references must stay generic. Layout triage runs without a visual renderer where possible.

## Workflow Status

- Integration base: `main`. This branch (`slide-design-vertical`) was cut fresh from `main` so its diff against `main` contains only slide-design work.
- The vertical was developed on `superRA-slides-making` (which carries the unrelated better-handoff lineage) and extracted post-sync (source commit `c96f8bcc`) onto this branch. See [01-add-slide-design-domain-vertical](01-add-slide-design-domain-vertical/task.md) §Results for the provenance note.
- Integration: APPROVED against `main` (base unchanged at `84715d69`). Final action — PR to `main` opened 2026-06-12.

## Results

### Key Findings

The `slide-design` domain vertical is complete and verified. It teaches audience-context discipline for research slides and ships Beamer-first implementation support, wired into every skill-discovery surface.

- **Vertical** ([01-add-slide-design-domain-vertical](01-add-slide-design-domain-vertical/task.md)) — `skills/slide-design/SKILL.md` plus stage-scoped references (`planning.md`, `beamer-techniques.md`, `beamer-overlays.md`, `layout-checks.md`, `integration.md`), a house Beamer starter template (`assets/beamer-starter-template.tex`), and `scripts/check_slide_layout.py` for nonvisual layout triage (compile errors, missing assets, overfull boxes, likely-wrapped bullets, boundary text). Registered in `using-superRA` (inventory + domain add-on), `superplan` Phase 2 verticals table, `CATEGORIES.md`, `README.md`, and the skill-triggering test runner.

The nine child tasks under the vertical (`01`–`09`) cover the starter template, layout-checker hardening, reference dedup, Mondrian chrome refinement, the shared checklist + inventory gate, resizebox-scope reconciliation, the non-Beamer fallback, placeholder detection, and the highlight palette — all `approved`.

### Verification

- `uv run --script skills/slide-design/scripts/check_slide_layout.py skills/slide-design/assets/beamer-starter-template.tex --no-fail` — clean apart from the two known info-level possible-wrap false positives (pages 6, 7).
- From a temp directory, `uv run --script /Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/slide-design-vertical/skills/slide-design/scripts/check_slide_layout.py /Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/slide-design-vertical/skills/slide-design/assets/beamer-starter-template.tex --no-fail` — confirms the documented `<skill-dir>` invocation is independent of the caller's cwd.
- `bash tests/test-slide-design-skill-text.sh` — 8/8 PASS; guards `<skill-dir>` script/template references.
- Smoke deck (starter template + a frame calling `\includeifexists{nonexistent-figure.pdf}`) flags `missing-asset` (warning) on the rendered placeholder page.
- `bash -n tests/skill-triggering/run-all.sh` — syntax OK.
- `git diff main --stat` — only slide-design surfaces (skill dir, wiring rows, task-tree swap, `.agents/skills` symlinks) plus the slide-design path-regression test.
- `git diff main --check` — clean.
- `bash tests/check-harness-compatibility.sh` — PASS; sync integration contract 54/54, codex agents and direct-mode references up to date, and `.agents/skills` packaging invariant satisfied for every skill.
- Implementation review of the review-fix delta — APPROVE; no file:line findings.

**Final diff self-check:** `git diff main..HEAD`; surviving hunks are (1) net-new slide-design skill dir + references + script + assets, (2) per-skill wiring rows in `using-superRA`/`CATEGORIES.md`/`README.md`/`superplan` + the skill-triggering prompt/runner + `.agents/skills` symlinks + slide-design text guard, (3) the `superRA/` task-tree swap (zotero tree removed, slide-design tree added, root rewritten) — main's convention is that `superRA/` holds the live workstream's tree wholesale. No suspicious hunks: every change ties to the extraction objective; the `superplan` Phase 2 row is authored fresh per the source-branch integration-review finding.
