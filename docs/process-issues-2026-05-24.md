# Process Issues — Task-Tree Dogfood (2026-05-24)

Branch: `better-handoff`. Context: building and dogfooding the `.plan/` task tree across two phases (core task tree + agent interface). Issues observed during implementation and review cycles.

---

## 1. Implementer does not commit task.md status atomically with code fix

**Summary.** On a REVISE round, the implementer spec requires setting `status: implemented` and `review_status: implemented` in frontmatter and committing code + task.md together in a single atomic commit (`agents/implementer.md` lines 82-83, 109, 128-134). In practice, agents split the commit or omit the task.md update entirely.

**Observed instances:**
- `migration` task: commit `51cc93b` fixed all 3 review items in `plan_migrate.py` and restructured `.plan/`, but the new `task.md` was written with `review_status: revise` baked in — the status flip was lost in the restructure.
- `handoff-doc` task: commit `4a3d725` fixed code across 5 files but did not touch `task.md` at all. A separate commit `783d896` then flipped `status: implemented → approved` but missed `review_status`.

**Root cause.** The spec says *what* to commit but has no terminal gate ensuring the commit actually happened with the correct contents. The Pre-Commit Self-Check (line 138) verifies what to check *before* staging but doesn't enforce that staging/committing occurs. The Report Format (line 150) doesn't require a committed SHA or a `git status` verification.

**Proposed fix.** Add an explicit commit-gate invariant to `agents/implementer.md`:
1. Add to §Pre-Commit Self-Check: `- [ ] git status shows no uncommitted changes in files I touched`
2. Add `Commit:` as a required field in §Report Format (SHA + list of staged files)
3. Add a terminal paragraph after §Update the Task and Commit: "Before returning your status report, run `git status` and confirm no uncommitted changes remain in your task's scope. If the commit failed or was incomplete, fix it before reporting."

---

## 2. Parent task status not rolled up after all children approved

**Summary.** When all child tasks under a parent reach `approved`, the parent's `status:` field stays at its previous value (`not-started` or `in-progress`). Observed on `agent-interface` (10/10 children approved, parent still `not-started`), `core-and-hooks` (2/2 children approved, parent still `not-started`), and `task-tree` (all children approved, parent still `in-progress`).

**Root cause.** No agent or hook automatically rolls up parent status. The `_task_io.py` library has rollup logic for `task_query.py` display, but CLI mutations (`task_update.py`) don't trigger parent rollup. The orchestrator is implicitly responsible but has no prompt telling it to check parent status after approving the last child.

**Proposed fix.** Two options:
- (a) Add automatic parent rollup to the PostToolUse validation hooks — when a task.md's `status:` or `review_status:` changes, walk up the ancestor chain and update parents whose children are all at the same status.
- (b) Add an explicit orchestrator instruction in `agent-orchestration`: "After approving the last child task under a parent, update the parent's status to match."
Option (a) is more reliable since it doesn't depend on orchestrator discipline.

---
