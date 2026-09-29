---
title: "Producer-Edit Reminder Catches Every Producer Edit"
status: implemented
depends_on: []
---

## Objective

When an agent edits a file that a registered step depends on, the hook reminds it to check that step's declaration, whatever tool made the edit. A new script draws a softer reminder, and the hook's other feedback concerns only the task being edited.

The hook runs after every tool call and compares file contents against a saved baseline, so it already catches edits made through Bash heredocs as well as the Edit tool. Keep that design.

### Every edit to a declared file is caught

- **Paths written with a variable.** A dependency declared as `${CODE}/est.jl` is never checked, even when `CODE` is a plain literal. The hook in [task_hook.py](../../../../skills/task-tree/scripts/task_hook.py) builds the graph without resolving variables and skips every path containing one; its docstring's claim that such a path "cannot name a real producer file" is wrong. Resolve literal and `env:` variables in the hook; never run `shell:` resolvers there.
- **Files inside a declared directory.** A Bash edit under a declared directory such as `Code/lib/` is missed, because the hook checks only declared paths that are files; the Edit tool's path catches it. Walk declared directories, with a size cap.
- **The first tool call of a session.** That call only records the baseline, so an edit made in it is missed. Record the baseline at session start or prompt submit.

### A new script draws a reminder, not an instruction

Creating `Code/new_producer.py` draws no reminder today. Remind on a new file whose extension matches a configured runner (`.jl` for a `julia` runner), under the project's code directories, skipping scratch and temporary folders. The reminder says the file may need a step if it produces retained results; many new scripts never do, so it does not tell the agent to register one.

### Feedback stays scoped

- **A `task.md` edit reports warnings for that task.** Every edit repeats tree-wide warnings, such as "archived prerequisite 'G2'", plus the communicate reminder, whichever task was edited.
- **Cost stays in range:** about 40–57 ms per no-op Bash call and 160–200 ms per `task.md` edit on a 99-task tree.

### Validation

On a scratch tree, each of these fires exactly one reminder: a heredoc edit to a literal path, a `sed -i` edit to `${CODE}/est.jl`, a Bash edit inside a declared directory, an edit in a session's first tool call, and a new `.jl` script under the code directory. A `task.md` edit shows only that task's warnings, and timings stay in range.

Owning tasks: [05-reminder-hook](../../05-reminder-hook/task.md), [02-agent-signals](../../12-agent-protocol/02-agent-signals/task.md).

## Details

Evidence with the scratch scenarios: [deps-report.md](../attachments/deps-report.md) M5 and Minor.

## Results

Every case in the Validation list now fires exactly one reminder; regression tests are in [test_edit_detect.py](../../../../skills/task-tree/scripts/test_edit_detect.py) (`TestEveryProducerEdit`, `TestScopedWarnings`).

- **Variables resolve in the hook.** `_hook_graph` in [task_hook.py](../../../../skills/task-tree/scripts/task_hook.py) builds the graph with literal and `env:` variables resolved and a `shell:` runner that returns an inert `${shell}` placeholder, so no subprocess runs and paths built from a shell variable match nothing (the step's literal paths still do). All hook graph builds (reminder, marker clearing, implemented-coverage, baseline watch list) use it. `${CODE}/est.jl` edits by `sed -i` are caught.
- **Directories.** `_repro_watch` lists declared directory dependencies; [_edit_detect.py](../../../../skills/task-tree/scripts/_edit_detect.py) scans them on every call (cap `MAX_DIR_FILES` = 2000, skipping hidden and scratch folders), so edits and new files inside them report.
- **First tool call.** The hook also handles `UserPromptSubmit` (registered in [hooks.json](../../../../hooks/hooks.json) and [hooks-codex.json](../../../../hooks/hooks-codex.json)), seeding the baseline and never reporting. A harness without that event still seeds on the first tool call, as before.
- **New scripts.** The directories of registered scripts outside the task root are scanned for files with a configured runner's suffix (`runner_suffixes`: `julia` gives `.jl`). Only a *new* file reports, with the softer message ("may need a step … many scripts never do"); a scratch/tmp folder, another language, or an edit to an existing unregistered script stays silent. Baseline format bumped to version 2 (old baselines reseed silently).
- **Scoped warnings.** A `task.md` edit reports validation and graph warnings for the edited tasks only (`_reconcile(scope=...)`); structural Bash moves still report the whole tree. The communicate reminder is unchanged: it concerns the edited markdown, not other tasks.
- **Cost** on this repo's tree: 41 ms per no-op Bash call, 108 ms for the prompt seed, 150-160 ms per `task.md` edit.
- **Test change.** `test_reproduction_reminder_never_resolves_vars` became `..._never_runs_shell_vars`: it asserted no variable resolution at all, which the design now reverses; it still proves no shell command runs.
