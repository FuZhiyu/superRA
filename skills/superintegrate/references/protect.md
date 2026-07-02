# Protect

Drift tests are the default protection mechanism, guarding key results through Sync, Integrate, Finish, and future work. For the writing vertical, "key results" are the manuscript artifacts; protection is satisfied by document-build success plus outline stability across the merged state — see `skills/writing/references/integration.md`.

**Always run the full drift-test suite on every integration pass.** Authoring new drift tests is scoped to the tasks this integration reopens or changes — reopened/changed tasks plus orchestrator-declared related tasks from `superplan §User Feedback and Changing the Task Tree`; running the suite is not scoped.

## Steps

1. **Extract key results from task.md `## Results` sections.** Walk the `superRA/` tree (`superra task tree`) and identify main findings across tasks. Protect main findings, not every intermediate number. Reference tasks by path (e.g., `data-preparation/merge`).
2. **Confirm coverage with the researcher.** Stop point:
   ```text
   These results seem like the key findings to protect:
   - [result 1: description and value] (from task-path/subtask)
   - [result 2: description and value] (from task-path/subtask)

   Which should be protected? Any to add or remove?
   ```
3. **Dispatch protection-creator.** `Stage: protection`, canonical implementer template. Drift tests reference task paths, not task numbers.
4. **Dispatch protection-reviewer.** `Stage: protection`, canonical reviewer template.
5. **Run tests on the current branch.** If new tests fail on existing code, fix the tests.
6. **Commit tests and task.md updates** once all confirmed key results are protected and the full drift-test suite passes. The protection commit (`integrate(protect): …`) is the record that Protect is done.
