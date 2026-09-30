---
title: "TEMPORARY — v0.5 Integrate Refactor"
status: not-started
depends_on: []
---

## Objective

Reduce the `skills/reproducibility` branch to its minimum net diff against the protected record, then verify it. This task is temporary: Integrate deletes it at close, and it holds no durable content.

**Protect decision:** commit `27b7e181`, *integrate(protect): drop low-value tests, retire every check step, fix the record choices*. Its body lists the kept and dropped results, the durable homes, and the protection: documentation plus the pytest suite, with no registered reproduction steps.

**Governing diff:** `git diff 447f0ef16f877f83dab2582426b7029dca039085..HEAD`, with `BASE_HEAD_SHA = 447f0ef16f877f83dab2582426b7029dca039085`. Recompute it at the start of the pass. Maturation ended at `de294145`.

**Protected record.** A hunk survives only if it supports one of these artifacts, or a validation or presentation path that they document:

- [RELEASE-NOTES.md](../../RELEASE-NOTES.md) `## [0.5.0]`, [README.md](../../README.md), [CLAUDE.md](../../CLAUDE.md), [skills/CATEGORIES.md](../../skills/CATEGORIES.md), and the docs-site task-tree and hooks pages under [docs/site](../../docs/site).
- [skills/reproducibility/](../../skills/reproducibility/SKILL.md), [skills/onboarding/](../../skills/onboarding/SKILL.md), the [skills/task-tree references](../../skills/task-tree/references/internals.md), and the workflow call sites listed in [07-workflow-integration](../reproducibility/07-workflow-integration/task.md#each-call-site-points-to-its-owning-rule).
- The `## Results` of [reproducibility](../reproducibility/task.md) and its children 01–07, [08-pilot-treasurygiv](../reproducibility/08-pilot-treasurygiv/task.md) (archived), [onboarding](../onboarding/task.md), [task-tree/edit-detection](../task-tree/edit-detection/task.md), and [task-tree/agent-cwd-isolation](../task-tree/agent-cwd-isolation/task.md). Retained attachment: [v05-design.md](../reproducibility/attachments/v05-design.md).

**Support paths that must survive:**

- The code each Results section names: `skills/task-tree/scripts/` (`_repro*.py`, `repro_run.py`, `_task_dependencies.py`, `_task_snapshot.py`, `_edit_detect.py`, `_checkout_scope.py`, `_step_links.py`, `task_*.py`, `plan_dashboard.py`, `templates/`), [hooks/checkout_isolation_gate.py](../../hooks/checkout_isolation_gate.py), `guard-foreign-checkout`, and the three hook manifests.
- The protection suites: `skills/task-tree/scripts` (1056 tests) and `tests/harness-instruction-following` (130 tests), which make up the 1186 that Protect collected; the hook tests [test-guard-foreign-checkout.sh](../../tests/hooks/test-guard-foreign-checkout.sh) and [test_trace_confinement.py](../../tests/harness-instruction-following/test_trace_confinement.py); the [load contract](../../tests/harness-instruction-following/load_contract.json) rows LC008 and LC024.
- Packaging: the `.agents/skills/reproducibility` and `.agents/skills/onboarding` symlinks and the three plugin manifests at `0.5.0`.

### Actions

Execute every action. Evidence that calls for a materially different action goes back to the Mature & Consolidate reviewer; do not widen the pass here.

1. **Triage the recomputed governing diff hunk by hunk against the protected record.** At derivation, two commits had no record. List them as pruning actions:
   - `cdb33b3f` (companion gates accept a Skill load the transcript has not recorded yet): [companion_gate.py](../../hooks/companion_gate.py), [skill_ledger.py](../../hooks/skill_ledger.py), the `communicate_gate.py` and `ensure-companion` hunks, and the [test-ensure-companion.sh](../../tests/hooks/test-ensure-companion.sh) and [test-ensure-communicate.sh](../../tests/hooks/test-ensure-communicate.sh) hunks. The researcher chooses: revert the commit, or keep it and add a `### Fixed` entry through Mature & Consolidate.
   - `a4d8b604`: the "terse" → "concise" line in [communicate SKILL.md](../../skills/communicate/SKILL.md). The researcher makes the same choice.
   - Any other hunk that matches nothing in the record gets the same treatment. A hunk that landed after `de294145` is new.
2. **Remove the stale `### In preparation` section from [RELEASE-NOTES.md](../../RELEASE-NOTES.md#in-preparation).** Its first bullet describes the Tree/Graph workspace, which has shipped: move that bullet into `#### Dashboard`. Delete the second bullet, which says UI validation and compatibility evidence are still required: the pilot is closed, and [04-dashboard-view](../reproducibility/04-dashboard-view/task.md#evidence-and-limits) records the UI evidence and the unverified Safari limit.
3. **Bring [v05-design.md](../reproducibility/attachments/v05-design.md) up to the shipped state.** Rewrite the closing paragraph of §Verification and upgrade ("Publication waits…", "Existing approvals document the earlier implementation…"). Rewrite the "Required evidence" table so it reads as the behavior contract, not a list of pending checks. In §Decision basis, drop the words "proposed implementation default" and move the superseded "task-level cycle rejection" into the 2026-09-29 sentence. Keep every decision.
4. **Repoint `rerun-model.md` in the [pilot feedback attachment](../reproducibility/08-pilot-treasurygiv/attachments/2026-09-06-small-pilot-design-feedback.md).** The pointer (around line 82) currently leads only to `diagnosing.md`. It must name all three successors: [rerun-or-accept.md](../../skills/reproducibility/references/rerun-or-accept.md) for acceptance and the stale rule, [diagnosing.md](../../skills/reproducibility/references/diagnosing.md), and the contract's §What invalidates a step for rerun rules.
5. **Update the [internals.md test-module table](../../skills/task-tree/references/internals.md) (line 406 onward) to match the post-Protect suite.**
   - Remove "legacy locks" from `test_repro_engine.py` and "concurrency" from `test_repro_acceptance.py`. Protect dropped both.
   - Add rows for `test_repro_scope.py`, `test_repro_provenance.py`, `test_repro_builds.py`, `test_edit_detect.py`, `test_step_links.py`, `tests/test_navigation_projection.py`, and `tests/test_dag_workspace_browser.py`.
6. **Delete the test-only helpers `_sibling_map` and `_dep_tasks` from [task_read.py:93-108](../../skills/task-tree/scripts/task_read.py#L93-L108).** The branch replaced their production caller with `deps.prerequisites` (line 530). Port the four [test_task_tree.py](../../skills/task-tree/scripts/test_task_tree.py#L2039-L2130) tests that call them to the production path. Also fix the stale comment at test_task_tree.py:3066, which names `12-agent-protocol/02-agent-signals`.
7. **Run the Project Doc Audit walk-up.** No module-level `CLAUDE.md`, `AGENTS.md`, or `README.md` sits under `skills/task-tree/`, `hooks/`, or the edited skills. The set is the root [README.md](../../README.md), [CLAUDE.md](../../CLAUDE.md), and [tests/harness-instruction-following/README.md](../../tests/harness-instruction-following/README.md).
8. **Record the Final Diff Self-Check trail in the commit body.**

**Out of scope:**

- Finish owns the 0.5.0 release date, the README "unreleased" banner, and the `### Release Prep` wording.
- `test-codex-hooks.sh` "Codex manifest command executes task PostToolUse hook" fails identically at `447f0ef1`. The expected wording is absent from the base, so the fix is separate maintenance work.
- Unused helpers that already exist at the base: `_workflow_lines` and `_line_index` in test_task_tree.py, `default_plan_root` in `_task_io.py`, and `_append_many` in `cli.py`.

### Verification

- Both protection suites pass: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts tests/harness-instruction-following`. At `de294145` this gave 1056 + 130 passed. If the count moves by anything other than the ported tests, investigate it. Never update an expectation to match.
- `bash tests/hooks/test-guard-foreign-checkout.sh` passes. `test-ensure-companion.sh` and `test-ensure-communicate.sh` pass against whichever `cdb33b3f` choice was made. `test-codex-hooks.sh` fails only on its known case.
- `./superRA/superra task check` reports no issues, and `./superRA/superra repro status .` selects no steps.
- Every relative link under `superRA/reproducibility`, `superRA/onboarding`, `superRA/task-tree`, and `skills/` resolves. `git diff --check` is clean.

## Results
