---
title: "Advisory Signals: Missing Registration and the Staleness an Edit Causes"
status: approved
depends_on: []
---

## Objective

Tell the agent, at the moment it can still act cheaply, that a retained result has no registered producer or that its edit made steps stale. Every signal is advisory and non-blocking: some retained artifacts legitimately have no producer step (a hand-edited `.tex`, a boundary input).

- **The producer-edit reminder names the fan-out.** When an edited file is a registered step's script, dep, or include, the existing reminder also lists the downstream steps the edit stales, with their last recorded durations. It reads the graph alone: no hashing, no `${VAR}` resolution, no subprocess.
- **Edits made through Bash are seen.** After a Bash call the hook detects changed code deps without relying on the tool's file path, so a `sed`, a Python rewrite, or a `git checkout` draws the same reminder. The check stays cheap enough to run on every Bash call; report its measured cost.
- **`task check` warning.** A `[WARNING]` in the `reproduction` category when a task's `## Results` links a generated-looking output file that no active step declares as an out and no step reads as a boundary dep. It names the file and the task.
- **Hook reminder at `implemented`.** When a leaf flips to `implemented` with such uncovered files, the task hook emits one non-blocking reminder naming them and pointing at `superRA:reproducibility`.
- **Quiet by default.** No finding for trees without reproduction config, for documents and source files, or for files under scratch paths. A false-positive rate that trains agents to ignore the signal fails the task.
- **Validation:** fixtures for the fan-out listing, a Bash-made edit, a covered artifact, an uncovered artifact, a linked `.tex` and `.md` (silent), a boundary dep (silent), and a tree without config (silent); each reminder fires once per file per session and the `implemented` reminder once per transition.

## Details

- Entry points: [task_hook.py](../../../../skills/task-tree/scripts/task_hook.py) (`_reproduction_reminder` at line 204 is the existing reminder; its PostToolUse matcher already includes Bash, but only Edit, Write, and apply_patch supply file paths today), [task_check.py](../../../../skills/task-tree/scripts/task_check.py), [_task_validate.py](../../../../skills/task-tree/scripts/_task_validate.py).
- Suggested Bash detection: a size-and-mtime pass over the graph's literal-path code deps against the existing hash cache; hash only files whose stat changed.
- Which extensions count as generated output is the open design call: start from data and exhibit formats (`.csv`, `.parquet`, `.arrow`, `.png`, `.pdf`, generated `.tex` tables under an output root) and report the rule chosen and its misses.
- Load `superRA:task-tree` for every edit under `skills/task-tree/`.

## Results

Three signals ship, sharing one analysis module: [_repro_signals.py](../../../../skills/task-tree/scripts/_repro_signals.py). It is read-only, resolves no `${VAR}`, hashes nothing, and starts no subprocess, so every caller — including the edit hot path — pays graph reads alone.

- **The producer-edit reminder names the fan-out.** The owning steps plus their transitive consumers over `graph.step_edges`, each with the duration its last run record carries: `Stales build-panel (12.4s), fit-model (3.0s), make-figure (no recorded duration).` ([_repro_signals.py:42-80](../../../../skills/task-tree/scripts/_repro_signals.py#L42-L80), wired at [task_hook.py:212](../../../../skills/task-tree/scripts/task_hook.py#L212)). Upstream steps are excluded — an edit to a consumer's script never implies rerunning its producers.
- **`task check` warns on an unregistered results artifact.** One `[WARNING]` per file a task's `## Results` links that looks generated and that no active step declares as an out and no step reads as a dep ([_repro_signals.py:199](../../../../skills/task-tree/scripts/_repro_signals.py#L199), wired at [task_check.py:243](../../../../skills/task-tree/scripts/task_check.py#L243); contract at [task-file-contract.md §Validation](../../../../skills/task-tree/references/task-file-contract.md#validation)).
- **The `implemented` reminder follows the transition, not the session.** [`_implemented_coverage_reminder`](../../../../skills/task-tree/scripts/task_hook.py#L372) fires once when a leaf's `task.md` edit leaves it at `implemented` with such files, and its marker is cleared whenever the task is not `implemented`, so a task that leaves and returns reminds again. Cheap gates — status, leaf, a link in `## Results` — run before any graph build.

Detection of *which* files changed is not this task's: [`_repro_emit`](../../../../skills/task-tree/scripts/task_hook.py#L226) is the shared emission point — marker, owner lookup, fan-out — and takes project-relative paths from whichever detector found them, today the tool file path and next the tool-agnostic detector in [edit-detection](../../../task-tree/edit-detection/task.md).

### The generated-file rule, and what it misses

A linked file counts as generated when its extension is a data or exhibit format (`.arrow .csv .dta .feather .jld2 .parquet .rds .tsv`, `.eps .jpeg .jpg .pdf .png .svg`), or when it is a `.tex` inside a directory some step already writes into ([_repro_signals.py:22-31](../../../../skills/task-tree/scripts/_repro_signals.py#L22-L31)). Silence otherwise: a tree with no `## Reproduction` section and no `code_roots`, a link to prose or source, a path with a `tmp`/`temp`/`scratch`/`cache`/`sandbox`/`node_modules` segment or a dotted one, and a file not on disk.

Known misses, all deliberate and all in the quiet direction:

- A generated `.txt`, `.json`, `.html`, or `.log` — too often config, notes, or a checked-in fixture to warn on.
- A generated `.tex` written outside every out directory, and any generated file in a scratch-named directory.
- An out or dep still carrying an unresolved `${VAR}` is matched on its literal tail, found as a run of whole path segments ([_repro_signals.py:94-114](../../../../skills/task-tree/scripts/_repro_signals.py#L94-L114)): `${OUT}/estimates` covers `output/estimates/alpha.csv`, and a declaration that is only a variable covers everything. The match is deliberately loose in the covering direction, so the hook's unresolved graph over-suppresses rather than warning on a registered out.

### What fires on a real tree

`superra task check --category reproduction` on this checkout reports 11 coverage warnings across 3 tasks, each naming a retained exhibit with no producer step:

- 6 figures and a `.csv` across two `showcase-analysis` tasks, a demo tree whose tasks carry no `## Reproduction` section at all — the case the signal is for.
- 4 dashboard screenshots under [04-dashboard-view/attachments](../../04-dashboard-view/task.md), captured by hand. These are the legitimately producer-less class: correct by the rule, and repeated on every `task check` with no way to acknowledge them (review note 4, deferred).

Nothing fired on prose links, on `.tex` beside the manuscript, on boundary inputs, or on the many tasks whose results link only code and task files.

### Validation

[test_task_tree.py](../../../../skills/task-tree/scripts/test_task_tree.py) gains 21 cases: the fan-out listing and its upstream exclusion; the `implemented` reminder with its once-per-transition marker and its round-trip re-fire; `${VAR}` coverage for a var-rooted file, a var-rooted directory, a bare variable root, a tail deeper in the path, and a non-matching path, under both resolution modes; and coverage fixtures for a covered out, a boundary dep, a `.tex` inside and outside an out directory, a `.md`, a scratch path, a missing file, and a tree without config. Full script suite: 1208 passed, 10 skipped. The registered check steps my edits stale were run by their own commands and pass — 195 cases for `task-scoped-builds-check` (which covers `reviewed-baseline-regression-check`'s files), 54 for `dashboard-dag-design-interaction-check`, and the `unified-dependency-workflow-check` verifier. Their stamps were not rebuilt here, since `repro build` would rewrite the committed `pytask.lock` from a worktree the orchestrator has yet to merge. The new `agent-signals-check` step below registers this task's own suite and was run by the same command.

## Review Notes

Tier: quick, with two spot checks; narrow re-review. Focus: correctness, scope-fidelity. Reviewer: main agent. Deferred by the orchestrator:

1. `[ADVISORY]` A legitimately producer-less file warns on every `task check` with no way to acknowledge it: the 4 hand-captured dashboard screenshots are that class.
2. `[ADVISORY]` `has_reproduction` reads `code_roots`, which [edit-detection](../../../task-tree/edit-detection/task.md) retires; that task's sweep covers it.

## Reproduction` section and no `code_roots`, a link to prose or source, a path with a `tmp`/`temp`/`scratch`/`cache`/`sandbox`/`node_modules` segment or a dotted one, and a file not on disk.

Known misses, all deliberate and all in the quiet direction:

- A generated `.txt`, `.json`, `.html`, or `.log` — too often config, notes, or a checked-in fixture to warn on.
- A generated `.tex` written outside every out directory, and any generated file in a scratch-named directory.
- An out or dep still carrying an unresolved `${VAR}` is matched on its literal tail, found as a run of whole path segments ([_repro_signals.py:94-114](../../../../skills/task-tree/scripts/_repro_signals.py#L94-L114)): `${OUT}/estimates` covers `output/estimates/alpha.csv`, and a declaration that is only a variable covers everything. The match is deliberately loose in the covering direction, so the hook's unresolved graph over-suppresses rather than warning on a registered out.

### What fires on a real tree

`superra task check --category reproduction` on this checkout reports 11 coverage warnings across 3 tasks, each naming a retained exhibit with no producer step:

- 6 figures and a `.csv` across two `showcase-analysis` tasks, a demo tree whose tasks carry no `## Reproduction` section at all — the case the signal is for.
- 4 dashboard screenshots under [04-dashboard-view/attachments](../../04-dashboard-view/task.md), captured by hand. These are the legitimately producer-less class: correct by the rule, and repeated on every `task check` with no way to acknowledge them (review note 4, deferred).

Nothing fired on prose links, on `.tex` beside the manuscript, on boundary inputs, or on the many tasks whose results link only code and task files.

### Validation

[test_task_tree.py](../../../../skills/task-tree/scripts/test_task_tree.py) gains 21 cases: the fan-out listing and its upstream exclusion; the `implemented` reminder with its once-per-transition marker and its round-trip re-fire; `${VAR}` coverage for a var-rooted file, a var-rooted directory, a bare variable root, a tail deeper in the path, and a non-matching path, under both resolution modes; and coverage fixtures for a covered out, a boundary dep, a `.tex` inside and outside an out directory, a `.md`, a scratch path, a missing file, and a tree without config. Full script suite: 1208 passed, 10 skipped. The registered check steps my edits stale were run by their own commands and pass — 195 cases for `task-scoped-builds-check` (which covers `reviewed-baseline-regression-check`'s files), 54 for `dashboard-dag-design-interaction-check`, and the `unified-dependency-workflow-check` verifier. Their stamps were not rebuilt here, since `repro build` would rewrite the committed `pytask.lock` from a worktree the orchestrator has yet to merge. The new `agent-signals-check` step below registers this task's own suite and was run by the same command.

## Review Notes

Tier: quick, with two spot checks. Focus: correctness, scope-fidelity. Reviewer: main agent.

1. `[BLOCKING]` **A directory out or dep rooted in a `${VAR}` does not cover the files inside it, so the `implemented` reminder fires false positives.** [_repro_signals.py:163-165](../../../../skills/task-tree/scripts/_repro_signals.py#L163-L165) accepts only `candidate == tail` or `candidate.endswith("/" + tail)`. Spot check: `_matches("output/estimates/a.csv", "${OUT}/estimates")` and `_matches("output/a.csv", "${OUT}")` both return `False`. The hook builds its graph with `resolve_vars=False` ([task_hook.py:414](../../../../skills/task-tree/scripts/task_hook.py#L414)), and variable-rooted directory outs are the norm in TreasuryGIV, so the Results claim that the unresolved graph "cannot manufacture a false positive" does not hold. Fix: match the tail as a run of whole segments anywhere in the candidate, treat an empty tail as covering, and add fixtures for both cases.
   → implemented: [_repro_signals.py:94-114](../../../../skills/task-tree/scripts/_repro_signals.py#L94-L114) now matches a `${VAR}` declaration's literal tail as a run of whole segments and covers everything when the tail is empty; fixtures are the reviewer's two spot checks plus a var-rooted directory out end to end through the hook.
2. `[BLOCKING]` **Bash-edit detection is no longer this task's.** The researcher revised the objective after dispatch: changed paths now come from the tool-agnostic detector in [edit-detection](../../../task-tree/edit-detection/task.md), and this task "adds no detection of its own". Remove `_reproduction_bash_reminder`, `changed_code_deps`, `code_dep_paths`, `CODE_SUFFIXES`, their tests, the matching [internals.md](../../../../skills/task-tree/references/internals.md) text, and the Bash and cost parts of `## Results`. Keep `_repro_emit` as the shared entry the detector will feed.
   → implemented: the Bash detector, its helpers, `CODE_SUFFIXES`, its four tests, the `internals.md` paragraph, and the Bash and cost parts of `## Results` are gone; [`_repro_emit`](../../../../skills/task-tree/scripts/task_hook.py#L226) stays, taking project-relative paths from whichever detector found them.
3. `[ADVISORY]` "never run" is wrong for a step with no local run record: an accepted step, a zero-second duration, or a fresh clone. Say "no recorded duration". [_repro_signals.py:82](../../../../skills/task-tree/scripts/_repro_signals.py#L82)
   → implemented: [_repro_signals.py:72-80](../../../../skills/task-tree/scripts/_repro_signals.py#L72-L80) says "no recorded duration".
4. `[ADVISORY]` A legitimately producer-less file warns on every `task check` with no way to acknowledge it: the 4 hand-captured dashboard screenshots are that class, not "real unregistered exhibits".
5. `[ADVISORY]` `has_reproduction` reads `code_roots` ([_repro_signals.py:248](../../../../skills/task-tree/scripts/_repro_signals.py#L248)), which [edit-detection](../../../task-tree/edit-detection/task.md) retires.

## Reproduction

```yaml
steps:
  - name: agent-signals-check
    kind: check
    cmd: uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_task_tree.py -q -p no:cacheprovider
    deps:
      - skills/task-tree/scripts/test_task_tree.py
      - skills/task-tree/scripts/_repro_signals.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_check.py
```
