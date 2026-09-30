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
- Extend existing `graph-authoring.md` (now [designing-the-graph.md](../../../../skills/reproducibility/references/designing-the-graph.md)) locality discipline instead of creating a parallel protocol. Agent acceptance is bounded by exact inspected changes and evidence; it does not require a new permission round for every authorized code edit.
- Docs HTML is produced by [docs/build_site.sh](../../../../docs/build_site.sh), never edited directly. The three version manifests are already at 0.5.0; keep the release unreleased until implementation and compatibility evidence land.

## Results

- [Planning](../../../../skills/superplan/references/build-and-review.md#task-dependencies), [consolidation](../../../../skills/superplan/references/consolidation.md), and [scope-change invalidation](../../../../skills/superplan/references/task-tree-design.md#objective-rewrites-on-scope-expansion) use effective dependencies. Task splitting preserves parent-owned work; maturation retains step identities and acceptance evidence. Mechanics remain in the task-tree contract and commands.
- [Reviewed acceptance](../../../../skills/reproducibility/references/rerun-or-accept.md#accept) supports reviewed current baselines for interactive results; the [acceptance task](../../02-runner/reviewed-acceptance/task.md) records that extension. Unresolved producer work and changed check assertions still require execution. [Completion](../../../../skills/reproducibility/references/protect-and-completion.md#the-completion-gate) accepts valid reuse as fresh; result reporting distinguishes reuse from execution. Shared configuration artifacts extend the existing [fan-out discipline](../../../../skills/reproducibility/references/designing-the-graph.md#the-step-unit-follows-the-script).
- [README upgrade guidance](../../../../README.md#upgrading), [unreleased notes](../../../../RELEASE-NOTES.md#050---unreleased), and [docs-site sources](../../../../docs/site/04-utility-skills/01-task-tree/task.md) explain the upgrade order, readiness from `depends_on`, task/step navigation, impact inspection, and reviewed reuse ([09-upgrade-and-records](../../14-review-revisions/09-upgrade-and-records/task.md)). No release is claimed.

- **Check update:** the verification companion follows the readiness model (`depends_on` gates, file inputs are reported) and the immediate-apply `accept` without evidence files; rebuilt `unified-dependency-workflow-check` is fresh.

### Verification

The retained [verification companion](attachments/verify_workflow.py) creates a disposable project and exercises the public [CLI](../../../../skills/task-tree/scripts/cli.py): `depends_on` alone gated the frontier; an inferred producer edge did not, and task read reported no logical dependency for it (readiness model of [03](../../14-review-revisions/03-readiness-model/task.md)). A shared-helper comment edit affected two consumers; a verified baseline diff and recorded call-site evidence justified accepting only the unaffected producer. Accepting (dry run first) preserved its successful lock and execution log. An independently changed calculation and assertion had no equivalence evidence and were rerun, producing the changed result and passing its check. Routine status was fresh; forcing the accepted producer executed it. The fixture used its own Git root and was removed after verification.

| Check | Evidence |
|---|---|
| Dependency, acceptance, and harness contracts | **83 passed** across [test_task_dependencies.py](../../../../skills/task-tree/scripts/test_task_dependencies.py), [test_repro_acceptance.py](../../../../skills/task-tree/scripts/test_repro_acceptance.py), and [test_contract.py](../../../../tests/harness-instruction-following/test_contract.py). |
| Documentation generation | [docs/build_site.sh](../../../../docs/build_site.sh) produced all four nonempty HTML exports; generated files were removed after checking. |
| Instruction and Markdown checks | Changed skill lines passed DRY, same-file restatement, and necessity review; the [Markdown checker](../../../../skills/communicate/scripts/check_markdown.py) and `git diff --check` were clean. |

The harness companion-route test required a retired duplicate pointer in `communicate`. Its assertion was removed; the test still checks the unique companion-contract file and its canonical `using-superra` route, matching contributor ownership. The generic skill validator accepted `reproducibility`; it rejects `task-tree`'s unchanged, supported `user-invocable` metadata, which was preserved.

The companion is hand-authored from the task's verification requirements and the approved [dependency](../../01-section-contract/unified-dependencies/task.md) and [acceptance](../../02-runner/reviewed-acceptance/task.md) contracts. `unified-dependency-workflow-check` above runs it; the focused suite runs from the repository root:

```bash
uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_task_dependencies.py skills/task-tree/scripts/test_repro_acceptance.py tests/harness-instruction-following/test_contract.py -q
```
