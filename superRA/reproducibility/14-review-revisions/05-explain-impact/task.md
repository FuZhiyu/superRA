---
title: "Explain and Impact Report the Facts the Skill Acts On"
status: implemented
depends_on:
  - 02-portable-records
---

## Objective

`superra repro explain` and `superra repro impact` print, accurately and at bounded cost, the facts the reproducibility skill tells agents to act on.

- **`explain <target>`** says where each changed hash came from (a lock revision, a git revision, a local receipt) and how that revision relates to HEAD. [diagnosing.md](../../../../skills/reproducibility/references/diagnosing.md) branches on that relation: a build synced from an older commit calls for waiting, a build from another branch for rebuilding.
- **`impact <path>`** predicts which steps a change to a file would make stale.

This task starts by confirming each finding on [01](../01-engine-freshness/task.md)'s engine and `repro-lock.json`; the evidence predates them.

### `explain` states the facts agents branch on

- **Text output always states the relation to HEAD.** When outputs are tracked in git, text prints only the first matching source, the git revision (`current git c591900`), and drops the lock source that carries the relation; the JSON row for the same output holds `lock c591900 … not in HEAD's history; on wip`. `label()` in [_repro_provenance.py](../../../../skills/task-tree/scripts/_repro_provenance.py) prints one source, and git sources sort before lock sources.
- **Graph errors are reported.** On an invalid graph, `explain` exits 0, never mentions the cycle, and shows a step that `build` refuses to run as "never built". Print the findings line `status` prints.
- **One row per changed file.** `explain .` on this repository printed 22 rows for 7 changed files (154 lines, with a 1,176-character `searched:` footer), one row per consuming step. [01-provenance-explain](../../13-staleness-provenance/01-provenance-explain/task.md)'s Results already describe a `(same row)` compaction the code lacks.
- **Cost is bounded per call.** Each changed tracked file costs its own `git log` walk: 14 s per walk on a synthetic 200,000-commit repository, against 0.87 s for `explain .` on this repository's 3,172 commits. The 64 MiB blob budget applies per path rather than per call. Use one budget per call, one history pass, and a cache keyed on HEAD and path. Blob history and lock history search the same refs; today blob history covers local branches only, while lock history also covers remote-tracking branches.
- **What already works stays:** the three causes, the relation facts, the per-revision lock index, and a `status` that spawns no git.

### `impact` covers configuration and reads as text

- **Configuration changes are covered.** `impact superRA/config.yaml` reports nothing, although changing a runner template stales every step that uses it.
- **Text by default, with durations.** Output is always JSON, so `--json` has no effect, and it carries no durations, although [03-skill-redesign](../../12-agent-protocol/03-skill-redesign/task.md) tells agents to measure fan-out "with impact and recorded durations".
- **One downstream computation.** `impact` runs its own O(E²) fan-out loop instead of `downstream_steps` in [_repro_signals.py](../../../../skills/task-tree/scripts/_repro_signals.py).

### Validation

Scratch fixtures cover a git-tracked output built on a side branch, an invalid graph, one changed file read by several steps, a runner edit in `config.yaml`, and timing on a large synthetic history.

Owning tasks: [01-provenance-explain](../../13-staleness-provenance/01-provenance-explain/task.md), [01-cli-decision-support](../../12-agent-protocol/01-cli-decision-support/task.md).

## Results

Every finding reproduced on 01's engine and `repro-lock.json`; each now has a regression test that fails on the pre-change code and passes after. [explain-impact-check](#reproduction) is fresh, and the full task-tree suite passes (1,287 passed, 10 playwright-only skips).

### `explain` states the facts agents branch on

- **Every lock or git source states its relation to HEAD.** A git revision now reads like a lock revision: `git <rev> (HEAD's version)`, `(earlier commit, N behind HEAD)`, or `(not in HEAD's history; on <branch>, …)` ([_relation](../../../../skills/task-tree/scripts/_repro_provenance.py#L693)). A tracked output holding bytes built on `wip` reads `current git 85d573b (not in HEAD's history; on wip)`, and `on origin/wip` when only fetched ([test](../../../../skills/task-tree/scripts/test_repro_provenance.py#L358)). Among matching revisions, one in HEAD's history is preferred.
- **Graph errors are reported.** A graph error on an explained step is listed under `graph errors on these steps; build refuses them:`, followed by the `N graph error(s); run superra task check.` line `status` prints; `explain` exits 1, and JSON carries `errors` and `graph_errors` ([format_explain](../../../../skills/task-tree/scripts/_repro_provenance.py#L913), [test](../../../../skills/task-tree/scripts/test_repro_provenance.py#L388)).
- **One row per changed file.** A file several steps read prints once, with a `steps:` line naming up to eight of them and how many recorded a different hash ([group_rows](../../../../skills/task-tree/scripts/_repro_provenance.py#L732), [test](../../../../skills/task-tree/scripts/test_repro_provenance.py#L401)). `next:` pointers come from those rows only. JSON keeps one row per step and node, plus the `files` grouping.
  - **Deviation: a task view prints diff excerpts only with `--diff`.** Twenty lines per file kept a 29-file task view at over 600 lines. Step and file views keep the first 20 lines.
  - **The `searched:` footer counts** lock revisions and files instead of listing them, naming files only when there are at most three ([render_searched](../../../../skills/task-tree/scripts/_repro_provenance.py#L797)).
- **Cost is bounded per call** ([History](../../../../skills/task-tree/scripts/_repro_provenance.py#L199)).
  - **One history pass per call:** a `git log` over HEAD's history, then one over the local and remote-tracking branches outside it, each covering the lock files and every tracked path the rows need. The split tells each revision's place relative to HEAD without a `rev-list HEAD`, which alone costs 1 s on 200,000 commits. Lock and blob history now search the same refs.
  - **One 64 MiB blob budget per call**, spent breadth-first across files ([_digest](../../../../skills/task-tree/scripts/_repro_provenance.py#L264), [test](../../../../skills/task-tree/scripts/test_repro_provenance.py#L444)).
  - **A cache keyed on HEAD, every branch tip, and path** in `.superra-repro/history.json`: a repeat call runs no `git log`. Blob digests are content-addressed and survive a ref change ([test](../../../../skills/task-tree/scripts/test_repro_provenance.py#L420)).
  - Identical diffs between rows are computed once.
- **Behavior change: a merge that only takes one parent's lock is no longer a lock revision.** `-c` lists a merge only for files it resolved, so such a merge introduces nothing. The two-clone fixture's footer counts 4 lock revisions instead of 5; ElasticityBound's counts 81 instead of 139.
- **What already worked stays:** the three causes, the relation facts, the per-revision lock index, and `status` without git.

| `explain .` | Before | After (first call / cached) |
|---|---:|---:|
| This repository (1,088 commits; 29 changed files, 15 stale steps) | 5.3 s, 960 lines, 200 rows, 3,624-character footer | 1.6 s / 1.1 s, 85 lines, 29 rows, 227 characters |
| ElasticityBound (4,262 commits, 173 branches; 5 shared helpers edited, 74 stale steps) | 3.9 s, 153 lines, 106 rows, 751 characters | 1.6 s / 1.5 s, 32 lines, 5 rows |
| Synthetic, 200,000 commits (7 changed files, 9 steps) | 10.9 s, 63 rows | 1.4 s / 0.24 s, 7 rows |

On ElasticityBound, about 1.1 s of each call is graph construction and `status`, not `explain`. A single path-limited `git log` on the synthetic history takes 1.1 s here, not the review's 14 s; the fix makes the walk count independent of the number of files. All three ran on APFS clones in scratch; ElasticityBound's clone had its own copy of `.git`.

### `impact` covers configuration and reads as text

- **`superRA/config.yaml` is covered.** It affects every step whose definition uses a runner template or a `${VAR}` in its command or paths, and every step when `env_deps` is set, with origins such as `runner sh` and `variable OUT` ([_config_origins](../../../../skills/task-tree/scripts/_repro_acceptance.py#L501)). A step drawing on none of these is not affected.
- **Text by default, with durations.** One line per affected step: last recorded duration, then why it is affected — the file and its origin, or the file connecting it to an affected producer — marked `[outside scope]` when outside `--scope`. The header totals the known durations ([format_impact](../../../../skills/task-tree/scripts/_repro_acceptance.py#L549)). `--json` returns the previous structure, with `duration` and `task` added to each affected step.
- **One downstream computation.** `impact` uses `downstream_steps` from [_repro_signals.py](../../../../skills/task-tree/scripts/_repro_signals.py) ([impact](../../../../skills/task-tree/scripts/_repro_acceptance.py#L514)). Affected steps list the direct readers first.
- Test: [test_impact_covers_configuration_and_prints_text_with_durations](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L915).

### Docs and open items

- [commands.md](../../../../skills/task-tree/references/commands.md#explain) states the relation for git sources, the history searched and its cache, the file-per-row output, graph errors, and the new `impact` behavior.
- **Other checks over the changed modules are not rebuilt here.** `provenance-explain-check`, `portable-records-check`, `reviewed-baseline-regression-check`, and the other steps listing these files are stale in this worktree; their test files pass in the full-suite run.

## Details

Evidence (provenance and dashboard review, reproduced on scratch projects before 01):

- With untracked outputs the text was accurate: "not in HEAD's history; on wip" and "earlier commit, 4 behind HEAD".
- `impact` already follows Julia `include` closures transitively, fans `env_deps` out to every step, and marks `--scope` correctly.
- With changed-path Bloom filters enabled, the 200,000-commit walk fell from 14 s to 0.7 s.

## Reproduction

```yaml
steps:
  - name: explain-impact-check
    kind: check
    cmd: "uv run --with pytest --with pyyaml python -m pytest skills/task-tree/scripts/test_repro_provenance.py skills/task-tree/scripts/test_repro_acceptance.py skills/task-tree/scripts/test_repro_builds.py -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_checkout_scope.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_edit_detect.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_builds.py
      - skills/task-tree/scripts/_repro_provenance.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_signals.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/conftest.py
      - skills/task-tree/scripts/test_repro_acceptance.py
      - skills/task-tree/scripts/test_repro_builds.py
      - skills/task-tree/scripts/test_repro_provenance.py
      - skills/task-tree/scripts/test_repro_runner.py
```
