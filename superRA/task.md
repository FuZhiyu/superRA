---
title: "superRA"
status: in-progress
depends_on: []
---

## Objective

Develop and maintain the superRA repository: the PLAN -> IMPLEMENT -> INTEGRATE research workflow, its task-tree tooling and dashboard, and the domain/utility skill library. Active workstreams nest as subtrees under this root.

### Conventions

- `CLAUDE.md` (aliased by `AGENTS.md`) at repo root is the contributor-facing authority for superRA internals — ownership boundaries, the DRY + Necessity gate, generated-artifact rules. Read it before modifying skills, hooks, agents, harness adapters, or internal docs.
- `README.md` is the user-facing product overview; keep product framing there, contributor rules in `CLAUDE.md`.

## Results

Workstream rollup as of 2026-08-18, through the unreleased `0.4.0`.

- [v04-lean-workflow](v04-lean-workflow/task.md) — the `0.4.0` release: roles became skills, independent review became a triggered decision, interactive execution became the default, one `communicate` contract governs everything agents write, planners cut tasks by edit surface, and skill prose was restyled repo-wide.
- [interactive-mode](interactive-mode/task.md) — the two-mode execution model and the interactive canvas loop, shipped in `0.3.4`; `v04-lean-workflow` later flipped its default and moved its reference.
- [agent-model-selection](agent-model-selection/task.md) — explicit model selection on every generic agent dispatch, enforced by a shared `PreToolUse` guard. Proven on Claude Code; Codex 0.147.0 bypasses the enforcement point, recorded as a limitation.
- [worktree-data-sync-redesign](worktree-data-sync-redesign/task.md) — fast seeding, denylisted discovery, cwd-relative `--from`, and per-path failures for the non-git data sync.
- [task-tree](task-tree/task.md) — the task-tree system: CLI and data layer, live SSE dashboard, hooks, migration, agent interface, the task-file contract, and the planning-workflow redesign. In progress pending the dashboard's postponed `nonloopback-host-serve` child and the not-started `agent-cwd-isolation`.
- [docs-site](docs-site/task.md) — the shipped public documentation site (dogfooded task-tree doc source, GitHub Pages deploy) and README front door. Postponed, including its `10-version-switcher` post-launch child.
- [showcase-analysis](showcase-analysis/task.md) — the CAPM-vs-FF3 asset-pricing study that serves as the docs showcase; its tree and figures are a live input to `docs/build_site.sh`.
- [zotero-skills](zotero-skills/task.md) — Zotero paper-reading, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` skill.
- [slide-design-vertical](slide-design-vertical/task.md) — the slide-design domain vertical.
- [upstream-fork-cleanup](upstream-fork-cleanup/task.md) — the `0.3.2` retirement of inactive upstream packaging, documentation, and tests.

Two efficiency rules also went into [econ-data-analysis](../skills/econ-data-analysis/SKILL.md) in `0.3.4` as domain discipline: data verification assesses committed diagnostics and outputs first and re-executes only on a suspected discrepancy, and headline findings are presented visually unless a figure would not clarify them.

Per-workstream detail lives in each child's `## Results`; integration and release history lives in the git log and [RELEASE-NOTES.md](../RELEASE-NOTES.md).
