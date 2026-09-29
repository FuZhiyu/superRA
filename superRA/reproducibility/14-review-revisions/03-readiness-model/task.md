---
title: "Readiness Follows depends_on; File Dependencies Inform"
status: implemented
depends_on: []
---

## Objective

Whether a task can start and whether its inputs are current are two questions with two rules. `depends_on` and task status decide what can start; file dependencies decide build order and freshness, and are reported to the agent and researcher, never enforced on starting work. The expected default is to rebuild a stale or missing input before relying on it; proceeding on it or accepting it stays the agent's call with the researcher.

### The design: two rules

| | Can this task start? | Are its inputs current? |
|---|---|---|
| Decided by | `depends_on`, on the task or an ancestor | step file edges |
| Met when | the prerequisite is `implemented`, `approved`, or `revise` | the producing step is `fresh` |
| Enforced | gates the frontier | never gates work; reported, and orders `repro build` |
| Errors block | tree edits that create a `depends_on` cycle | builds of the steps they touch |

- **Report inputs where the decision is made.** `task frontier` and `task read` list each task's inputs that are not `fresh`: file, producer, state, and `repro build <task> --upstream`. "Own work" leaves the frontier; `repro status` lists stale steps.
- **A missing input fails only the build that reads it,** naming its producer.
- **Only a loop among steps is a file-flow error.** Grouping file edges by task is a view. A `depends_on` running against the file flow (A `depends_on` B while B reads A's output) is a `task check` warning naming the file.
- **Adding a subtask rolls up status as today;** `task create` names the tasks it newly blocks.
- **Agent-facing docs state the two rules and what the reports show in a few lines,** enough for an agent to act predictably, with no rationale. Update the frontier lines in [main-agent.md](../../../../skills/using-superra/references/main-agent.md) §Resuming Work, [task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md), and [commands.md](../../../../skills/task-tree/references/commands.md) §Manage dependencies.

A file edge alone no longer orders work: a consumer whose producer task has not started is ready unless `depends_on` says otherwise.

The [0.5 design](../../attachments/v05-design.md#hierarchy-and-task-readiness) carries this rule.

### Today's rules, and the flaws this design removes

Today one task graph merges both sources, and what meets a prerequisite depends on what produces it ([_task_dependencies.py:110-132](../../../../skills/task-tree/scripts/_task_dependencies.py#L110-L132)): a task producer by its status, a parent's own step by its freshness. A parent task can own steps as well as children, and the graph is drawn once per level of the tree, with each child standing for everything inside it.

#### Flaw 1: Two rules decide readiness, and they disagree

- **Across siblings, a never-built output does not block.** `a` is `implemented` but its output was never built; its consumer `b` is ready.
- **Inside a parent, a stale output does.** Parent `P` owns step `setup`, and child `P/c` reads its output. Editing `setup.sh` makes `setup` stale, so `P/c`, already `in-progress`, drops off the frontier, and `P [own work: setup]` takes its place. Freshness is used here because `P`'s status is rolled up from its children, `P/c` included, so waiting on it would make `P/c` wait on itself.
- **Stale steps surface as "own work" for parents only** ([_task_dependencies.py:152-159](../../../../skills/task-tree/scripts/_task_dependencies.py#L152-L159)). In this repository the frontier lists `scalable-navigation [own work: dashboard-navigation-heterogeneity]`, while the approved leaves `dag-design`, `02-agent-signals`, and `edit-detection` have stale or never-built checks that appear nowhere.

Removed because readiness reads only `depends_on`: `P/c` stays on the frontier with `setup` reported as a stale input.

#### Flaw 2: A parent's steps merge into the parent one level up, inventing cycles and over-blocking

At the parent's own level its steps are separate nodes; one level higher, `project` ([_task_dependencies.py:163-169](../../../../skills/task-tree/scripts/_task_dependencies.py#L163-L169)) folds them into the parent's single task node.

- **False cycle.** `paper` owns step `tables`; sibling `robustness` reads it; `paper/estimate` reads `robustness`'s output:

  ```text
  steps:  paper:tables → robustness → paper/estimate    no cycle
  tasks:  paper → robustness → paper                    cycle
  ```

  The graph reports the cycle, and an invalid graph has an empty frontier ([_task_dependencies.py:139-140](../../../../skills/task-tree/scripts/_task_dependencies.py#L139-L140)), so no task anywhere can start.
- **Over-blocking.** `P`'s step `report` reads `q.txt` from sibling `Q`. One level up this becomes `Q → P`, which blocks every task inside `P`, including `P/c`, which reads nothing from `Q`.

Removed because task-level groupings of file edges no longer gate or invalidate anything; only the step graph is checked for cycles.

#### Flaw 3: Any error anywhere freezes all planning

`build_graph` adds every reproduction error to the task graph's findings ([_repro.py:1237-1240](../../../../skills/task-tree/scripts/_repro.py#L1237-L1240)), and any error makes the whole graph invalid: the frontier is empty and preflight ([_task_snapshot.py:9-21](../../../../skills/task-tree/scripts/_task_snapshot.py#L9-L21)) refuses every tree edit, even when the error predates the edit. With `OUT: {env: NOPE_UNSET_VAR}` in `config.yaml`, `task frontier`, `task create`, `task move`, and `task dep add` all fail with `config.yaml: variable 'OUT' reads environment variable 'NOPE_UNSET_VAR', which is not set`. On a Dropbox project used from three machines, a variable set on only one of them freezes planning on the other two.

Removed because planning commands no longer read reproduction errors.

#### Flaw 4: Archiving a producer hides its consumer's missing input

An archived task leaves the graph with its edges, so its consumer enters the frontier with no sign that its input is missing. `repro build --dry-run` on that consumer then prints a failure and "Nothing to execute: every selected step is fresh" together.

Removed in part: the consumer's missing input is reported with its archived producer. Fix separately: `build --dry-run` does not call a failing selection fresh.

### Every view computes from one snapshot

`task read`, the frontier, the DAG, `task check`, preflight, and the dashboard derive prerequisites and input states from one snapshot. Today some compute their own:

- Legacy code paths: `compute_frontier` and `_collect_frontier` in `_task_io.py` (used only by tests), `detect_cycles` and `validate_dependencies` in `_task_validate.py`, `print_frontier` in `task_query.py` (unused), and the dashboard's fallback to authored `depends_on`.
- `task read` recomputes step status itself.
- `task tree --json` builds the graph without resolving variables, so it always reports `effective_depends_on: null` and `dependencies_complete: false`.

Messages name the evidence: `task read` lists prerequisites (`depends_on`, own or inherited) apart from inputs (file, producer, state). `dep remove` on a task linked only by files says so and names the file, instead of "not in depends_on".

The failing test is resolved deliberately: `test_bundle_fixture.py::test_task_read_json_carries_comments_and_dependency_status` (the dependency `slug` is now the full path).

### Validation

Regression tests on scratch trees:

- the unset variable: `create`, `move`, `dep add`, and `frontier` work, and `repro status` reports the error;
- the `paper` chain: no error, and each task shows its inputs' state;
- `P/c` after a `setup.sh` edit: still on the frontier, with `setup` reported stale;
- an `implemented` producer never built: its consumer is ready, reported "never built", and `build --upstream` builds it;
- an archived producer whose output is missing: the consumer reports the missing input, and `build --dry-run` does not claim freshness;
- A `depends_on` B while B reads A's output: a warning naming the file;
- a subtask added to an approved producer: `task create` names the newly blocked tasks.

Behavior that already works stays covered: a `depends_on` cycle is refused with its witness and nothing written; a step cycle blocks builds of its steps with its witness; a logical-only prerequisite does not pull its producer into `repro build`.

Owning task: [unified-dependencies](../../01-section-contract/unified-dependencies/task.md).

## Details

Evidence for every flaw, with the scratch scenarios that reproduced it: [deps-report.md](../attachments/deps-report.md) M1–M4 and Minor. The unset-variable failure was also reproduced directly. The own-work example is from `task frontier` and `repro status .` on this repository on 2026-09-28.

## Results

Readiness now reads only `depends_on`; file edges are reported as inputs and never gate. [Dependencies](../../../../skills/task-tree/scripts/_task_dependencies.py) keeps `logical` edges for `prerequisites`, `blockers`, `ready`, and `frontier`, and `files` edges (archived producers included) for `inputs`. Boundary views still project both kinds for `task dag` and the dashboard.

### Each flaw is removed

- **Flaw 1, two readiness rules.** The frontier lists ready leaves only; own-work rows are gone. `P/c` stays on the frontier after a `setup.sh` edit, with `setup.txt from .#setup: stale` as an input.
- **Flaw 2, invented cycles and over-blocking.** Each boundary checks cycles over `depends_on` edges only; step cycles stay errors in [build_graph](../../../../skills/task-tree/scripts/_repro.py). The `paper` chain has no error, and each task reports its inputs. A `depends_on` against the file flow is a warning: `depends_on 'b' runs against the file flow: b reads this task's output a.txt; not blocking, but best avoided`.
- **Flaw 3, errors freeze planning.** `Dependencies.findings` holds dependency findings only, so `valid` ignores reproduction errors. [Preflight](../../../../skills/task-tree/scripts/_task_snapshot.py) builds the current and edited trees without resolving variables and refuses only a new `depends_on` error. With `OUT: {env: NOPE_UNSET_VAR}`, `create`, `dep add`, `move`, and `frontier` succeed; the frontier notes the reproduction errors on stderr, and `repro status` and `repro build` report them.
- **Flaw 4, archived producer.** The consumer's input reads `missing` with `archived producer; file is missing`. `build --dry-run` now reports a step whose input is missing as `cannot run` and exits 1 instead of claiming freshness ([repro_run.py](../../../../skills/task-tree/scripts/repro_run.py)).
- **Adding a subtask.** `task create`, `move`, `dep add`, and archive transitions print, after writing, each task they take off the frontier (`Now blocked: analysis waits on data (not-started)`) and each new dependency warning.

### Every view reads one snapshot

- **Removed parallel paths:** `compute_frontier` / `_collect_frontier`, `detect_cycles` / `validate_dependencies` with `validate_plan(dependencies=)`, `print_frontier`, and the dashboard's authored-`depends_on` fallback.
- **One status pass per command:** `task read` and `task frontier` call `step_states` once for the task's own steps and its input producers; `task_inputs` joins those states to file edges.
- **`task tree --json`** reports `effective_depends_on` from `depends_on` and `dependencies_complete: true` without resolving variables.
- **Messages name the evidence.** `task read` shows `Prerequisites (depends_on)` with `(inherited)` marks, a `Not ready: waits on …` line, and an `Inputs` section; its JSON `readiness` carries `ready`, `blockers` (with `declared_by`), and `inputs`. `dep remove` names the file of a remaining or file-only edge.
- **The bundle-fixture test passes unchanged:** `dependencies[].slug` is again the sibling directory name, and `path` carries the full path.

### Deviations and limits

- `repro build` still refuses on any reproduction error in the tree rather than only on the steps it touches; the engine owns that scope.
- A build blocked by an archived producer's missing file says `external input old.txt is missing` without naming the producer; `task read` and the frontier name it.
- [task_hook.py](../../../../skills/task-tree/scripts/task_hook.py) changed one line, dropping the removed `dependencies=False` argument.
- Tests whose expectation encoded the old rule were rewritten: grouped and mixed cycles, own-work rows, `tree --json` incompleteness, and invalid-graph fixtures that used a `depends_on` against the file flow now use a real `depends_on` cycle.

### Verification

- The [regression tests](../../../../skills/task-tree/scripts/test_task_dependencies.py) cover each scenario in the Validation list. Run against the base commit `caecfc02`, 16 of them fail; all 26 pass here.
- The task-tree suite and harness fixture tests pass: **1,378 passed, 10 skipped**.
- `readiness-model-check` built fresh. The edited scripts are declared deps of 14 other tasks' checks, which read `missing` or `stale` in this worktree (most were never stamped here); they were not rebuilt, and their test files pass in the suite above.
- Agent-facing docs: [main-agent.md](../../../../skills/using-superra/references/main-agent.md#resuming-work), [task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md), [commands.md](../../../../skills/task-tree/references/commands.md#manage-dependencies), [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md#effective-dependencies), and [internals.md](../../../../skills/task-tree/references/internals.md#effective-dependency-snapshot).

## Reproduction

```yaml
steps:
  - name: readiness-model-check
    kind: check
    cmd: "uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_task_dependencies.py tests/harness-instruction-following/test_bundle_fixture.py -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
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
      - skills/task-tree/scripts/conftest.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_check.py
      - skills/task-tree/scripts/task_create.py
      - skills/task-tree/scripts/task_link.py
      - skills/task-tree/scripts/task_query.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/task_rename.py
      - skills/task-tree/scripts/task_update.py
      - skills/task-tree/scripts/test_task_dependencies.py
      - tests/harness-instruction-following/test_bundle_fixture.py
      - tests/fixtures/task-trees/bundle-two-tasks
```
