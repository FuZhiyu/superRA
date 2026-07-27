---
title: "Task Companion Files and Dashboard"
status: approved
depends_on: []
---

## Objective

Give every task one version-controlled `attachments/` workspace for small companion files that support the task without becoming permanent project code, and make those files first-class reading surfaces in the dashboard.

- Distinguish ephemeral scratch, retained task-local companions, and permanent project artifacts; require retained files to be reproducible and linked from the owning task's `## Results`.
- Keep the storage boundary simple: every retained task-local file goes under `attachments/`. Immediate directories containing `task.md` are subtasks, while `attachments/` is always a non-task asset container.
- Promote shared, pipeline-critical, or promised deliverables into project-conventional paths during Integrate, before integration review. Mature & Consolidate must retain, relocate, or drop the companion files that remain task-local without breaking their links.
- Let the live and standalone dashboards expose a collapsed Attachments pseudo-branch beneath the owning task and render selected Markdown, Python, Julia, R, notebook, image, PDF, and text files in the normal full-width detail pane. Attachment nodes participate in navigation only; they never become task-tree, DAG, status-rollup, frontier, or Kanban nodes.
- Verify instruction behavior with a realistic harness exercise and dashboard behavior with focused and full task-tree tests.

### Generated artifacts

Canonical role specs are outside the intended scope, so no generated role outputs should change. If implementation expands into `agents/*`, follow the generated-artifact protocol in the repo-root contributor guide: regenerate `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; never hand-edit them.

## Planner Guidance

The repository already carries figures in task-local `attachments/`, moves the whole task directory, rewrites links in every Markdown file under a moved task, and runs Markdown integrity checks on sidecars. The missing capability is the lifecycle contract plus dashboard discovery, safe delivery, hot reload, rendering, and export.

Put every retained task-local file in `attachments/`. The agent-facing contract should name that destination without teaching a nesting policy; the dashboard and file APIs should tolerate recursively generated attachment layouts as an implementation detail. Do not require a manifest file; the owning `## Results` is the concise provenance and entry-point record.

The existing [HTML Dashboard](../dashboard/task.md) concern covers dashboard behavior but not the cross-workflow storage and promotion contract, so this work is a sibling durable concern under Task Tree Skill. The contract lands first; the backend data path and user interface then follow in dependency order.

## Critical Files

- [using-superra/SKILL.md](../../../skills/using-superra/SKILL.md) — universal task interface loaded by main agents, implementers, reviewers, and direct mode
- [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) — current task anatomy, results lifecycle, and figure-attachment contract
- [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md) — durable-home and directory-fold decisions for retained evidence
- [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) — task discovery, routes, watchers, search/export state, and standalone rendering
- [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) — active-task navigation and client-side Markdown rendering

## Results

The approved companion-file lifecycle and dashboard now use one storage boundary
and one reading surface:

- The [companion-file contract](01-artifact-contract/task.md#results) requires every retained task-local file under `attachments/`; only `task.md` and child-task directories occupy the task directory itself. It distinguishes scratch, retained evidence, and permanent project artifacts; requires reproducibility metadata; and promotes shared or maintained artifacts before Integrate closes.
- The [attachment-only data path](02-dashboard-artifact-data/task.md#results) recursively discovers and serves only `attachments/`, with bounded no-follow descriptor reads shared by previews, downloads, and standalone attachment images. Direct files are excluded, and attachment nodes remain outside task discovery and status semantics.
- The [tree-native attachment UI](03-dashboard-artifact-ui/task.md#results) removes the Files modal. A collapsed Attachments pseudo-branch lives beneath each owning task, while selected Markdown, highlighted source, notebooks, images, PDFs, and text render in the normal full-width detail pane with URL/history, live refresh, standalone, worktree, and unified keyboard-tree behavior.

Independent review approved all three children. The full task-tree suite passed
`772` tests with four known non-failing warnings; dedicated installed-Chromium
regressions cover rendering, sanitization, hot reload, worktree isolation, and
the unified attachment/task navigation model.

### Result protection

The researcher confirmed three key results for drift protection:

- **One authoritative companion contract.** The new
  [canonical-route regression](../../../tests/harness-instruction-following/test_contract.py#L273-L289)
  requires exactly one `task-companion-files.md` under `skills/` and verifies
  that the always-loaded task interface and reporting skill route to it. The
  lifecycle prose remains governed by this task's Objective and Results plus
  the contributor DRY + Necessity review gate; no brittle sentence or Markdown
  layout oracle was added.
- **Attachment-only, race-safe data access.** Existing
  [attachment discovery coverage](../../../skills/task-tree/scripts/tests/test_artifacts.py#L68-L109)
  proves direct files stay outside the manifest. The
  [descriptor-race regression](../../../skills/task-tree/scripts/tests/test_artifacts.py#L448-L488)
  now exercises safe Markdown preview in addition to explicit and unsafe
  implicit downloads, and the
  [standalone-figure race regression](../../../skills/task-tree/scripts/tests/test_artifacts.py#L782-L820)
  continues to reject an intermediate-directory symlink swap without exposing
  outside bytes.
- **Tree-native sanitized reading.** The existing
  [installed-Chromium regression](../../../skills/task-tree/scripts/test_artifact_ui.py#L270-L480)
  protects the collapsed pseudo-branch, unified roving-tabindex tree,
  full-width routing and history, sanitized Markdown/notebook/SVG/HTML output,
  highlighted Python/Julia/R, relative attachment links, and hot reload.

These are categorical path, security, and UI invariants, so numerical
tolerances do not apply. Each test builds its own temporary fixture and runs
without a project pipeline. Red-green verification ran the selected protections
green (`7 passed`), deliberately perturbed every selected expectation and
observed `7 failed`, then restored the expectations and reran green
(`7 passed`, two dependency deprecation warnings). The complete
harness-instruction suite passed `127` tests. The complete task-tree suite
passed `741` tests with four known non-failing fixture/dependency warnings.

## Review Notes

1. **MAJOR — The contract regression does not protect the confirmed placement/lifecycle result.** The [new test](../../../tests/harness-instruction-following/test_contract.py#L273-L289) proves that one file has the canonical filename and that two skills point to it, but it never checks the substantive classification, `attachments/` placement, Results/provenance, promotion, or maturation invariants in the [authoritative contract](../../../skills/using-superra/references/task-companion-files.md#L5-L38). Emptying that reference while leaving the two pointers intact remains green, so the researcher-confirmed contract can drift without detection and the result-protection coverage gate is not met. Add stable semantic/section-level assertions for the lifecycle invariants (or an equally durable instruction-behavior regression) and run the selected red-green cycle again; this need not use a brittle full-sentence oracle.

2. **MAJOR — The Results give conflicting current full-suite totals.** The earlier verification says [the full task-tree suite passed 772 tests](task.md#L46-L49), while the protection record says [the complete task-tree suite passed 741](task.md#L79-L84). The latter is reproducible on the protected commit (`741 passed, 4 warnings`); the former predates the sync that consolidated the suite. Reconcile the earlier paragraph with the current result (or explicitly distinguish immutable commit-scoped evidence) so `## Results` is a self-contained latest-state account rather than two incompatible unqualified totals.
