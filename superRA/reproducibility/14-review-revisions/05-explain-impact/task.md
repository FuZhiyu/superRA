---
title: "Explain and Impact Report the Facts the Skill Acts On"
status: not-started
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

## Details

Evidence (provenance and dashboard review, reproduced on scratch projects before 01):

- With untracked outputs the text was accurate: "not in HEAD's history; on wip" and "earlier commit, 4 behind HEAD".
- `impact` already follows Julia `include` closures transitively, fans `env_deps` out to every step, and marks `--scope` correctly.
- With changed-path Bloom filters enabled, the 200,000-commit walk fell from 14 s to 0.7 s.
