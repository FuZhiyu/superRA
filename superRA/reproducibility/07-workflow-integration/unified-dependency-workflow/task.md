---
title: "Teach One Dependency Model and Reviewed Reuse"
status: not-started
depends_on: []
---

## Objective

Align workflow and public guidance with the [0.5 design](../../attachments/v05-design.md). Agents author only additional logical prerequisites, use effective dependencies for planning and downstream invalidation, minimize avoidable fan-out, and apply scoped reviewed acceptance without presenting it as a rerun.

- Update the owning task-tree, superplan, main-agent, and reproduction skill instructions; retain one authority for each mechanism. Parent tasks may own steps, and adding a subtask is not a migration trigger.
- Keep routine completion compatible with acceptance-as-fresh. Forced verification must execute its selected targets. Preserve the selected protection checks and the distinction between task readiness and reproducibility evidence.
- Update README upgrade guidance, release notes, and the affected docs-site sources with the breaking union-cycle rule, task/step expansion, impact diagnosis, and acceptance. Remove guidance that tells agents to duplicate file-derived dependencies manually.
- Verify at least one realistic agent/harness or script-level journey through a no-reproduction task, inferred dependency, harmless shared-helper edit, evidence-backed acceptance, and uncertain change requiring rerun. Apply the contributor instruction gate to every changed skill line.

## Details

- **Ownership:** workflow/domain/utility skill prose, [task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md) routing, [README.md](../../../../README.md), [RELEASE-NOTES.md](../../../../RELEASE-NOTES.md), and relevant source pages under [docs/site](../../../../docs/site/). Runtime schema and command details are owned by the graph and runner tasks; point to them.
- Confirmed stale sites: [consolidation.md](../../../../skills/superplan/references/consolidation.md) asks for explicit dependencies for all output consumers; [main-agent.md](../../../../skills/using-superra/references/main-agent.md) and [task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md) invalidate only declared dependents. [build-and-review.md](../../../../skills/superplan/references/build-and-review.md) must cover effective-graph validation while still supporting plans whose step dependencies do not exist yet.
- Extend existing [graph-authoring.md](../../../../skills/reproducibility/references/graph-authoring.md) locality discipline instead of creating a parallel protocol. Agent acceptance is bounded by exact inspected changes and evidence; it does not require a new permission round for every authorized code edit.
- Docs HTML is produced by [docs/build_site.sh](../../../../docs/build_site.sh), never edited directly. The three version manifests are already at 0.5.0; keep the release unreleased until implementation and compatibility evidence land.
