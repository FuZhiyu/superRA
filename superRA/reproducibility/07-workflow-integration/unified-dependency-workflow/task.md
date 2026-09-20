---
title: "Teach One Dependency Model and Reviewed Reuse"
status: approved
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


## Reproduction

```yaml
steps:
  - name: unified-dependency-workflow-check
    kind: check
    cmd: uv run --script superRA/reproducibility/07-workflow-integration/unified-dependency-workflow/attachments/verify_workflow.py
    deps:
      - superRA/reproducibility/07-workflow-integration/unified-dependency-workflow/attachments/verify_workflow.py
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_hooks.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/dashboard_artifact_workflow.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/plan_migrate.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_add_result.py
      - skills/task-tree/scripts/task_check.py
      - skills/task-tree/scripts/task_comment.py
      - skills/task-tree/scripts/task_create.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_link.py
      - skills/task-tree/scripts/task_query.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/task_rename.py
      - skills/task-tree/scripts/task_update.py
      - skills/task-tree/scripts/wrapper_resolver.py
```

## Results

- [Planning](../../../../skills/superplan/references/build-and-review.md#task-dependencies), [consolidation](../../../../skills/superplan/references/consolidation.md), and [scope-change invalidation](../../../../skills/superplan/references/task-tree-design.md#objective-rewrites-on-scope-expansion) use effective dependencies. Task splitting preserves parent-owned work; maturation retains step identities and acceptance evidence. Mechanics remain in the task-tree contract and commands.
- [Reviewed acceptance](../../../../skills/reproducibility/references/rerun-model.md#reviewed-acceptance) requires consumer-specific review of every changed item, directs uncertain changes and changed specifications/assertions to execution, and points to the exact preview/apply commands. [Completion](../../../../skills/reproducibility/references/protect-and-completion.md#the-completion-gate) accepts valid reuse as fresh; result reporting distinguishes reuse from execution. Shared configuration artifacts extend the existing [fan-out discipline](../../../../skills/reproducibility/references/graph-authoring.md#isolate-meaningful-recomputation).
- [README upgrade guidance](../../../../README.md#upgrading), [unreleased notes](../../../../RELEASE-NOTES.md#050---unreleased), and [docs-site sources](../../../../docs/site/04-utility-skills/01-task-tree/task.md) explain the breaking cycle audit, task/step navigation, impact inspection, and reviewed reuse. No release is claimed.

### Verification

The retained [verification companion](attachments/verify_workflow.py) creates a disposable project and exercises the public [CLI](../../../../skills/task-tree/scripts/cli.py) with pytask 0.6: a logical-only prerequisite gated the frontier; an inferred producer edge agreed between frontier and task read. A shared-helper comment edit affected two consumers; a verified baseline diff and recorded call-site evidence justified accepting only the unaffected producer. Preview/apply preserved its successful lock and execution log. An independently changed calculation and assertion had no equivalence evidence and were rerun, producing the changed result and passing its check. Routine status was fresh; forcing the accepted producer executed it. The fixture used its own Git root and was removed after verification.

| Check | Evidence |
|---|---|
| Dependency, acceptance, and harness contracts | **83 passed** across [test_task_dependencies.py](../../../../skills/task-tree/scripts/test_task_dependencies.py), [test_repro_acceptance.py](../../../../skills/task-tree/scripts/test_repro_acceptance.py), and [test_contract.py](../../../../tests/harness-instruction-following/test_contract.py). |
| Documentation generation | [docs/build_site.sh](../../../../docs/build_site.sh) produced all four nonempty HTML exports; generated files were removed after checking. |
| Instruction and Markdown checks | Changed skill lines passed DRY, same-file restatement, and necessity review; the [Markdown checker](../../../../skills/communicate/scripts/check_markdown.py) and `git diff --check` were clean. |

The harness companion-route test required a retired duplicate pointer in `communicate`. Its assertion was removed; the test still checks the unique companion-contract file and its canonical `using-superra` route, matching contributor ownership. The generic skill validator accepted `reproducibility`; it rejects `task-tree`'s unchanged, supported `user-invocable` metadata, which was preserved.

The companion is hand-authored from the task's verification requirements and the approved [dependency](../../01-section-contract/unified-dependencies/task.md) and [acceptance](../../02-runner/reviewed-acceptance/task.md) contracts. `unified-dependency-workflow-check` above runs it; the focused suite runs from the repository root:

```bash
uv run --with pytest --with pyyaml --with 'pytask>=0.6,<0.7' --with pytask-parallel --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_task_dependencies.py skills/task-tree/scripts/test_repro_acceptance.py tests/harness-instruction-following/test_contract.py -q
```
