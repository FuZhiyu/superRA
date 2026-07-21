---
title: "superRA"
status: revise
depends_on: []
---

## Objective

Develop and maintain the superRA repository: the PLAN -> IMPLEMENT -> INTEGRATE research workflow, its task-tree tooling and dashboard, and the domain/utility skill library. Active workstreams nest as subtrees under this root.

### Conventions

- `CLAUDE.md` (aliased by `AGENTS.md`) at repo root is the contributor-facing authority for superRA internals — ownership boundaries, the DRY + Necessity gate, generated-artifact rules. Read it before modifying skills, hooks, agents, harness adapters, or internal docs.
- `README.md` is the user-facing product overview; keep product framing there, contributor rules in `CLAUDE.md`.

## Results

Workstream rollup (as of 2026-07-20, including the `0.3.2` cleanup release):

- [task-tree](task-tree/task.md) — the task-tree system: CLI and data layer, live SSE dashboard, hooks, migration, agent interface, and the workflow redesigns. Approved and integrated on `better-handoff`.
- [docs-site](docs-site/task.md) — the public documentation site (dogfooded task-tree doc source, GitHub Pages deploy) and README front door. Approved; its `10-version-switcher` child is postponed post-launch work.
- [showcase-analysis](showcase-analysis/task.md) — the real CAPM-vs-FF3 asset-pricing study that serves as the docs showcase; its tree and figures are a live input to `docs/build_site.sh`.
- [zotero-skills](zotero-skills/task.md) — Zotero paper-reading, BibTeX/citation support, and the vendored `mistral-pdf-to-markdown` skill.
- [slide-design-vertical](slide-design-vertical/task.md) — the slide-design domain vertical.
- [upstream-fork-cleanup](upstream-fork-cleanup/task.md) — completed `0.3.2` retirement of inactive upstream packaging, documentation, and tests; maintained Claude, marketplace, and Codex manifests are aligned and the compatibility and release-audit checks pass.

Per-workstream detail lives in each child's `## Results`; integration and release history lives in the git log and `RELEASE-NOTES.md`.
