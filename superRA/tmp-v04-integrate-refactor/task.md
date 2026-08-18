---
title: "TEMPORARY — v0.4 Integrate Refactor"
status: implemented
depends_on:  []
---

## Objective

Reduce the `worktree-v0.4-redesign` branch to its minimum net diff against the protected record. Integrate deletes this task at close; nothing here is a durable home.

**Protect decision:** commit `c1cb9990` — `integrate(protect): record v0.4 permanent-record and consolidation decisions`. Its body carries the kept results, durable homes, consolidation dispositions, and the protection choice (documentation-only; the existing suites are the drift protection).

**Protected record.** A hunk survives only when it supports one of these, or a reproduction, validation, interpretation, or presentation path documented in them:

- [RELEASE-NOTES.md](../../RELEASE-NOTES.md) — the `0.4.0` entry, extended at `cb352250` to cover the post-08-03 work.
- Durable task `## Results`: [root](../task.md), [v04-lean-workflow](../v04-lean-workflow/task.md), [interactive-mode](../interactive-mode/task.md), [agent-model-selection](../agent-model-selection/task.md), [worktree-data-sync-redesign](../worktree-data-sync-redesign/task.md), [task-tree/skill-definition](../task-tree/skill-definition/task.md), [task-tree/planning-redesign](../task-tree/planning-redesign/task.md), and the children each links down to.
- Permanent homes the decision names: `skills/`, [docs/site](../../docs/site), [CLAUDE.md](../../CLAUDE.md), [README.md](../../README.md).

**Support paths that must survive.** Each is named in the record above and carries a protected behavior:

- Hook scripts and both wirings: [agent-model-guard](../../hooks/agent-model-guard), [ensure-communicate](../../hooks/ensure-communicate) + [communicate_gate.py](../../hooks/communicate_gate.py), [guard-task-approval](../../hooks/guard-task-approval) + [task_approval_gate.py](../../hooks/task_approval_gate.py), [ensure-companion](../../hooks/ensure-companion), [task-hook](../../hooks/task-hook), and the [Claude](../../hooks/hooks.json), [Codex](../../hooks/hooks-codex.json), and [Cursor](../../hooks/hooks-cursor.json) manifests.
- Drift protection: [tests/harness-instruction-following](../../tests/harness-instruction-following), [tests/hooks](../../tests/hooks), [tests/fixtures](../../tests/fixtures), [check-harness-compatibility.sh](../../tests/check-harness-compatibility.sh), the `skills/task-tree/scripts` pytest suite, and [test_worktree_data_sync.py](../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py).
- Packaging: the `.agents/skills/` symlinks and the Claude, marketplace, and Codex plugin manifests at `0.4.0`.
- Retained evidence: [v04-lean-workflow/attachments/](../v04-lean-workflow/attachments/), which that task's `## Results` names file by file.

**Governing diff:** `git diff 12e1de918dc7f6062a74946d8984977761d6c274..HEAD`. `BASE_HEAD_SHA = 12e1de918dc7f6062a74946d8984977761d6c274`.

### Actions

Execute all three. New evidence demanding a materially different action returns to the Mature & Consolidate reviewer rather than widening here.

1. **Revert the `refresh-cache` line in [.gitignore](../../.gitignore).** Added by `468beeb7` to hide an untracked machine-local plugin-cache script; no protected result depends on it, so it is unmatched diff. Keep it only if the researcher says so at the Integrate gate.
2. **Repoint the two `econ-data-efficiency/task.md` citations in [map-writing-surfaces.md](../v04-lean-workflow/attachments/map-writing-surfaces.md)** (lines 39 and 66). That task directory was deleted at `66b0ef45`; its two rules now live in [econ-data-analysis/SKILL.md](../../skills/econ-data-analysis/SKILL.md) and the `0.3.4` release notes.
3. **Retire the `agents/` surface from the root docs, then run the `refactor-and-integrate` §Project Doc Audit walk-up over the rest of the governing diff.** [README.md:85](../../README.md#L85) ("or agent files") and [CLAUDE.md:170](../../CLAUDE.md#L170) ("The workflow skills, agent files, orchestration skill…") still name a directory this branch deleted — rewrite both to the role skills. The walk-up set for the remaining diff is the root [README.md](../../README.md) and [CLAUDE.md](../../CLAUDE.md), [docs/README.codex.md](../../docs/README.codex.md), [skills/CATEGORIES.md](../../skills/CATEGORIES.md), [tests/harness-instruction-following/README.md](../../tests/harness-instruction-following/README.md), and [skills/task-tree/scripts/vendor/README.md](../../skills/task-tree/scripts/vendor/README.md).

### Verification

Every check below passes before this task goes `implemented`; the parenthesised figure is the review baseline on `f7414b22`, so a changed number is a regression to investigate, not a new expectation to record.

```bash
uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' \
  --with watchfiles --with httpx python -m pytest tests/harness-instruction-following -q   # 126 passed
uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' \
  --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q              # 809 passed
uv run --with pytest python -m pytest \
  skills/worktree-data-sync/scripts/test_worktree_data_sync.py -q                          # 43 passed
bash tests/check-harness-compatibility.sh                                                  # exit 0
for f in tests/hooks/test-*.sh; do bash "$f"; done                                          # all pass
./superRA/superra task check                                                                # no findings
```

Also: every relative Markdown link under `superRA/` resolves (0 broken at review), and `git grep -n 'econ-data-efficiency\|details-rename\|superRA/grilling'` returns nothing outside `docs/plans/`, which is dated history.

## Details

**Triaged and cleared at review — do not re-litigate.** Each family below is matched by a named result in the protected record, so it stays:

- `skills/` restyle, retirement, and rename hunks (`writing/` → `academic-writing/`, `report-in-markdown/` and `codex-superra-setup/` deleted, `communicate/` and the two role skills added) — [v04-lean-workflow](../v04-lean-workflow/task.md) `## Results`.
- `agents/`, `.codex/agents/`, and resolver deletions — the same record's `role-skills` bullet and the `0.4.0` **Removed** section.
- `tests/` and `tests/fixtures/` churn — [prose-test-cleanup](../interactive-mode/prose-test-cleanup/task.md) records the deleted assertion classes, and `f7414b22` repointed the last two stale contract tests.
- `hooks/` additions and all three manifests — [agent-model-selection](../agent-model-selection/task.md) and [reporting-contract/communicate/hooks](../v04-lean-workflow/reporting-contract/communicate/hooks/task.md).
- `docs/site`, `docs/showcase-fixtures`, `skills/CATEGORIES.md`, and the plugin-manifest version bumps — the `workflow-defaults`, `review-skill`, `academic-writing-rename`, and `skill-definition` records plus the `0.4.0` **Release Prep** entry.
- `## Planner Guidance` → `## Details` across the tree and the fixtures — [task-tree/skill-definition](../task-tree/skill-definition/task.md); no occurrence survives outside that task's own prose and the alias test.

`tests/hooks/test-e2e-cli.sh` runs for minutes; budget for it rather than treating a timeout as a failure.

## Results

All three actions executed as authored; no scope widening.

1. Dropped the `refresh-cache` line from [.gitignore](../../.gitignore).
2. Repointed both `econ-data-efficiency/task.md` citations in [map-writing-surfaces.md:39,66](../v04-lean-workflow/attachments/map-writing-surfaces.md) to name `econ-data-analysis/SKILL.md` and the `0.3.4` release notes as the rules' current home, keeping the deleted path as a labeled historical pointer rather than a dangling reference.
3. Rewrote `agent files` → `role skills` at [README.md:85](../../README.md#L85) and [CLAUDE.md:170](../../CLAUDE.md#L170). Project Doc Audit walk-up over `docs/README.codex.md`, `skills/CATEGORIES.md`, `tests/harness-instruction-following/README.md`, and `skills/task-tree/scripts/vendor/README.md`: all four already current against the governing diff (checked hook-table/test-file/CDN-asset claims against the live repo state) — no further edits needed.

**Verification** (all outside the sandbox — `uv`/shimmed `python3` panic inside it, per dispatch note):

- `tests/harness-instruction-following` — 126 passed (matches baseline).
- `skills/task-tree/scripts` — 809 passed (matches baseline).
- `skills/worktree-data-sync/scripts/test_worktree_data_sync.py` — 43 passed (matches baseline).
- `tests/check-harness-compatibility.sh` — exit 0.
- `tests/hooks/test-*.sh` — all pass, including `test-e2e-cli.sh` on a clean run (6/6). Two earlier runs of that suite hit a live-model flake in scenario S7: the model resolved the fixture's `superRA/01-child/task.md` against the real repo path (embedded in its prompt as `$REPO_ROOT`) instead of the isolated tmp cwd, writing an untracked `superRA/01-child/` into this checkout each time; removed both times (`git status` confirms no residue). Unrelated to this task's diff — `test-e2e-cli.sh` itself is untouched by the governing diff, and the failure mode is model path selection, not hook/CLI behavior.
- `./superRA/superra task check` — no findings.
- Relative Markdown links under `superRA/` — 0 broken (scripted check).
- `git grep -n 'econ-data-efficiency\|details-rename\|superRA/grilling'` outside `docs/plans/` — hits only in this task's own Action 2/Verification prose and the two repointed `map-writing-surfaces.md` citations, both of which name the string as a forward-pointing historical label per Action 2, not a stale reference.

Left untouched: an unrelated pre-existing uncommitted change to `superRA/v04-lean-workflow/review-skill/comments.yaml` (a dashboard comment-resolution artifact, not part of this task) — not staged or discarded.
