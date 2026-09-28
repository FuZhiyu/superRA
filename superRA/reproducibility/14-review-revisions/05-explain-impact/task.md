---
title: "Explain and Impact Report the Facts the Skill Acts On"
status: not-started
depends_on:
  - 02-portable-records
---

## Objective

`repro explain` and `repro impact` print, accurately and at bounded cost, the facts [diagnosing.md](../../../../skills/reproducibility/references/diagnosing.md) and [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) tell agents to act on.

- **The relation to HEAD is always printed.** `label()` prints only the first source ([_repro_provenance.py:566-571](../../../../skills/task-tree/scripts/_repro_provenance.py#L566-L571)), and the git source is ordered before the lock source ([:350-358](../../../../skills/task-tree/scripts/_repro_provenance.py#L350-L358)); with git-tracked outputs the text loses "not in HEAD's history; on wip", the fact diagnosing.md branches on.
- **Graph errors are reported.** On an invalid graph `explain` exits 0, never mentions the cycle, and shows a blocked step as "never built".
- **Rows are grouped by changed file**, matching the `(same row)` compaction [01-provenance-explain](../../13-staleness-provenance/01-provenance-explain/task.md)'s Results already describe.
- **Cost is bounded per call:** one byte budget per call (the 64 MiB budget applies per path today), one history pass, and a cache keyed on HEAD and path. Blob history and lock history search the same refs (blob history: local branches only; lock history: remote-tracking branches too).
- **`impact` covers configuration and speaks text.** `impact superRA/config.yaml` reports the steps a runner or variable change stales; text is the default with `--json` optional; recorded durations appear, as [03-skill-redesign](../../12-agent-protocol/03-skill-redesign/task.md) promises; the fan-out reuses `_repro_signals.downstream_steps` instead of its own O(E²) loop.

Owning tasks: [01-provenance-explain](../../13-staleness-provenance/01-provenance-explain/task.md), [01-cli-decision-support](../../12-agent-protocol/01-cli-decision-support/task.md).

## Details

### Evidence (dashboard and provenance review, reproduced on scratch projects)

- **Relation to HEAD.** With outputs committed to git, text printed `current git c591900` while the JSON row held `lock c591900 … not in HEAD's history; on wip`. With untracked outputs, text was accurate: "not in HEAD's history; on wip" and "earlier commit, 4 behind HEAD".
- **Row repetition.** `explain .` on this repo printed 22 rows for 7 changed files (13 KB, 154 lines); the `searched:` footer alone was 1,176 characters.
- **Cost.** Each walk is one path-limited `git log` for the lock plus one per changed tracked file (`_repro_provenance.py:199`, `:320`). On a synthetic 200,000-commit repo each walk took 14 s (0.7 s with changed-path Bloom filters); on this repo (3,172 commits) `explain .` took 0.87 s. `status` spawns no git (0.11 s); keep that.
- **Impact.** Include closures are followed transitively, `env_deps` fan out to every step, and `--scope` marks steps correctly.
- **Keep:** the three causes, the relation facts, the per-revision lock index, and the cached lock commit.
