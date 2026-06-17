---
title: "Rewrite Quickstart as the Single End-to-End Narrative"
status: approved
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Rewrite `docs/site/02-quickstart/task.md` into the spine of the whole site: one walkthrough that takes a researcher through a full task workflow and introduces every core concept *inline along the way*, instead of deferring them to a Concepts section (now deleted). Details that a reader does not need in the flow are linked to Reference, not explained. Keep the toy size-and-momentum example and the existing dashboard screenshots.

The user's design sketch committed on this branch (section headers + inline `<!-- ... -->` comments in this file) is the authoritative baseline; resolve every inline comment and remove it. The intended shape:

### Prerequisite

- Git literacy is required (branching/merging recommended) — this is a real prerequisite for using agents at all, state it plainly.
- superRA runs on **Claude Code or Codex**. The narrative uses Claude Code; note it applies equally to Codex, with install and agent-invocation being the only differences (link the Codex specifics to Reference / Install).
- Resolve the `uv` vs `python3` question accurately rather than hand-waving: the bundled CLI scripts are run via `uv run --script` (PEP 723), and `uv` is the recommended path; state the actual requirement, don't leave the reader guessing. (Authority: repo `CLAUDE.md §Local Task-Tree CLI Development`.)

### Install + set up a project

- Plugin install: the two `claude plugin …` commands, plus a one-line Codex pointer.
- Lead onboarding with the **adopt-an-existing-project** path, matching the user's edit: commit existing work, start the harness, and ask something like *"use superRA and retroactively create task trees for [what I'm working on], and show me the dashboard."*
- Introduce the trigger word at high level: **saying `superra` triggers the workflow** — that is all the reader needs. Do not explain how the hook is wired (contributor internal).

### A typical workflow — superplan → superimplement → superintegrate

Walk one workflow end to end, with a subsection per phase, introducing concepts as they first appear:

- **Superplan.** Plain-language request; trigger phrase `superplan`; no harness plan-mode needed. Introduce the **task tree** *at a high level* here — the project's state is stored as a committed tree of small task files the agent reads and writes. Do **not** teach the `superra` CLI surface (that is for agents); instead introduce the **dashboard** as how a *human* sees the tree, and show how to open it (`./superRA/superra dashboard`, or just ask the agent to show it). Keep the one-gate approval point (plan is presented before code is written). Link full task-tree design to Reference.
- **Superimplement.** Trigger `superimplement`. The **implementer–reviewer pair** is the central discipline — implementer writes, an independent reviewer returns APPROVE/REVISE, work only advances on APPROVE, review is never skipped. Introduce **roles & adversarial review** inline here (this content used to be its own Concepts page — fold the essential idea in, link the role specs for detail).
- **Watch + read results (merged).** Merge the old "watch progress" and "read results" steps. The **dashboard is the default way to monitor** — it auto-updates in real time as agents work; results live in the committed task files (durable handoff), and the dashboard is how you read them. De-emphasize the markdown-file/CLI path to a brief mention.
- **Superintegrate.** Introduce the INTEGRATE phase at high level — protect results against drift, sync with the base branch intent-aware, refactor for codebase fit, document, and ship. Link `superintegrate` for detail. (This replaces the deleted Concepts › Integration & Protection page's role in the reading flow.)

### Where to go next

End by directing the reader to the two new skill pages — [Domain Skills](#/03-domain-skills) and [Utility Skills](#/04-utility-skills) — as the next read, plus Reference for lookups and Showcase for a real tree.

## Planner Guidance

This is the longest single rewrite. Lean on the existing prose already in the file and in the soon-deleted concepts pages — you are condensing and inlining proven copy, not writing from scratch. Cut ruthlessly: anything that reads as repetition of a concept already introduced earlier in the same page is the verbosity this restructure exists to remove. Keep one paragraph per line.

## Results

Rewrote [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md) into a single end-to-end narrative spine following the design-sketch section order. All four inline `<!-- ... -->` design comments are resolved and removed (`grep "<!--"` → none).

**Structure delivered** (matching the sketch headers): Objective → Prerequisite → Install + set up a project → A typical workflow (four `####` subsections: Superplan, Superimplement, Watch progress and read results, Superintegrate) → Where to go next. The old standalone "Step 3 — Watch progress" and "Step 4 — Read the results" steps are merged into one subsection per the sketch comment, with the dashboard framed as the default monitor-and-read surface and the markdown/CLI path demoted to a brief mention.

**Concepts folded inline** (the deleted Concepts pages' essential ideas, condensed): the task tree introduced at Superplan as committed `task.md` files holding project state; the dashboard as the *human* view of those files (the agent-facing CLI surface is deliberately not taught); the implementer–reviewer pair and why adversarial review at Superimplement; the frontier at the watch step; the INTEGRATE phase (protect / sync-by-intent / refactor / document / ship) at Superintegrate. Details link out to authoritative homes rather than being re-explained.

**Prerequisite facts resolved accurately** per repo [CLAUDE.md §Local Task-Tree CLI Development](../../../../CLAUDE.md): `uv run --script` (PEP 723) is stated as the recommended path, with `python3` as a stdlib-only fallback — no hand-waving. Git literacy stated as a plain hard prerequisite. Claude Code / Codex parity stated, with Codex install + agent-invocation differences linked to [docs/README.codex.md](../../../../docs/README.codex.md) (the surviving repo authority, since the `04-how-to` install page is deleted in `05-finalize`).

**Trigger word** introduced at high level only — saying `superra` (or a phase word) turns the workflow on; the hook wiring is left as contributor internal, not documented.

**Toy example and screenshots kept**: the size-and-momentum-on-simulated-returns example and all three existing dashboard screenshots (`dashboard-workspace.png`, `dashboard-kanban.png`, `dashboard-task-detail.png`) are reused, re-anchored to the points in the narrative where each view is first relevant.

**Ends** by directing the reader to [Domain Skills](#/03-domain-skills) and [Utility Skills](#/04-utility-skills) as the next read, plus Reference and Showcase.

**Verification.** `report-in-markdown` self-diagnose reports the file clean. All five cross-page hash links resolve to existing pages (`05-reference/01-task-file`, `03-domain-skills`, `04-utility-skills`, `05-reference`, `06-showcase`); no stale `#/03-concepts` or `#/04-how-to` links remain. All six repo-file link targets and all three attachment images exist on disk. The page renders without error through the real doc-mode export path (`plan_dashboard.py generate --doc-mode --root 02-quickstart`); the only `katex-error`/`ParseError` strings in the output are literals inside the vendored KaTeX JS bundle, not rendered page content (the page has no math).

**Deviation from Planner Guidance — install-detail link target.** The objective suggested linking Codex/install specifics to "Reference / Install". There is no install page in the Reference section, and the `04-how-to/01-install-and-set-up` page is deleted in `05-finalize`, so I linked Codex specifics to the durable repo authority [docs/README.codex.md](../../../../docs/README.codex.md) and general install to the repo [README](../../../../README.md) — the same targets the welcome page already uses — rather than a target that will not survive the restructure. The reader still reaches the authoritative install detail.
