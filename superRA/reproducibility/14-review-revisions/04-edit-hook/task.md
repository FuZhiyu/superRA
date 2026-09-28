---
title: "Producer-Edit Reminder Catches Every Producer Edit"
status: not-started
depends_on: []
---

## Objective

The PostToolUse reproduction reminder fires for every edit to a registered producer file, whatever tool made it, and its task-edit feedback stays scoped to the edited task.

- **Paths behind a `${VAR}` are checked.** [task_hook.py:872](../../../../skills/task-tree/scripts/task_hook.py#L872) skips every variable, even a plain literal like `CODE: Code`, and its docstring claim that such a path "cannot name a real producer file" is wrong. Resolve literal and `env:` variables without running shell resolvers.
- **Files inside a declared dependency directory are checked** on Bash edits; the `is_file()` filter at [task_hook.py:875](../../../../skills/task-tree/scripts/task_hook.py#L875) drops them. Walk directory deps with a size cap.
- **The first hooked call of a session is covered.** It currently only seeds the content baseline; seed at session start or prompt submit.
- **Tree-wide warnings do not repeat on every `task.md` edit.** Warnings such as "archived prerequisite 'G2'" and the communicate reminder recur whichever task was edited ([task_hook.py:538-540](../../../../skills/task-tree/scripts/task_hook.py#L538-L540)).
- **Cost stays in range:** about 40–57 ms per no-op Bash call and 160–200 ms per `task.md` edit on a 99-task tree today.

### Researcher decisions

- **New scripts outside `superRA/`.** A new `Code/new_producer.py` never draws a "register a step" reminder. Recommendation: remind on new files whose extension matches a configured runner, under the project's code directories.

Owning tasks: [05-reminder-hook](../../05-reminder-hook/task.md), [02-agent-signals](../../12-agent-protocol/02-agent-signals/task.md).

## Details

Full evidence: [deps-report.md](../attachments/deps-report.md) M5 and Minor. The hook compares file contents against a baseline rather than parsing commands, so a Bash heredoc edit to a literal producer path already fires; keep that design.
