---
title: "Skill, References, and Docs Teach the Producer Chain and Online-Only Data"
status: not-started
depends_on: [02-upstream-default]
---

## Objective

Rewrite the agent-facing and reader-facing instructions for the behavior [01-local-graph](../01-local-graph/task.md) and [02-upstream-default](../02-upstream-default/task.md) ship. An agent should name the result it wants current and let the build find the stale producers. When a step needs online-only data, the agent reports it and downloads only on the researcher's go-ahead.

- **[reproducibility SKILL.md](../../../../skills/reproducibility/SKILL.md).**
  - §The Graph: `unverified` (this machine cannot check a file without downloading it), and no `external` state.
  - §Selecting Steps:
    - Targets include their producer chain, and `--only` uses files from outside the selection as they sit on disk.
    - Builds skip fresh steps, so name the task or the final result, not each stale step.
    - When another session is editing a producer in this worktree, use `--only`.
  - §Commands table: match the new default.
  - §Recording a Result:
    - Plain `status` covers the chain.
    - A result checked with `--only`, or one resting on `unverified` steps, says so in `## Results` and names where tracing stopped.
    - A selected step must itself read `fresh`.
- **Online-only data.** Write the download notes the CLI points to, in the reference that handles a step that is not `fresh`.
  - Downloading is the researcher's call: report the files and their total size, and download only on their go-ahead.
  - **File Provider files** (under `~/Library/CloudStorage/`): Finder's Download Now or Make Available Offline. Alternatively, a coordinated read with PyObjC. A plain full read may leave the file partial, so confirm afterwards that `ls -lO` no longer shows `dataless`.
  - **Legacy Dropbox placeholders:** Dropbox's Make Available Offline only.
  - Then rerun `status`.
- **[rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) and [protect-and-completion.md](../../../../skills/reproducibility/references/protect-and-completion.md).**
  - Acceptance stays step-local: to cover a producer, name it.
  - The `--dry-run` cost now includes stale producers.
  - Accept the steps the stale rule sets aside before building the rest, or build with `--only`; a default build would rerun them. protect-and-completion.md line 8 ("building by name only the steps the rule says to run") states the scoped assumption.
- **[adoption.md](../../../../skills/reproducibility/references/adoption.md).** In an adopted project, a producer that has never been built reads `missing`, even when its outputs exist, so a default downstream build runs it. Accept or build such producers first, or use `--only`.
- **[review-task SKILL.md](../../../../skills/review-task/SKILL.md) line 28.** The evidence command becomes plain `status`.
- **Docs site.** The [reproducibility page](../../../../docs/site/04-utility-skills/09-reproducibility/task.md) and the [dashboard page](../../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md) (line 26) describe the default, `--only`, `unverified`, the Build menu's modes, and the dashboard's solid, dashed, and faded cards.
- **[RELEASE-NOTES.md](../../../../RELEASE-NOTES.md) 0.5.0.**
  - Describe the default, `--only`, `unverified`, the download gate, and the removal of `external`.
  - Note that `status X --upstream` now exits 3 instead of 1 when only a producer is stale.

### Validation

- Apply the [CLAUDE.md](../../../../CLAUDE.md) §Teach the Protocol three tests line by line to every changed `skills/*` line, then §Skill Prose Style. Load `skill-creator` before editing any `SKILL.md`.
- Two realistic harness sessions on disposable fixtures. Record the command each agent issued:
  - Stale producers in two tasks feed a final step. Asked to bring the final result current, the agent issues one target build, not a list of every stale step.
  - A step that must run reads a file shown as online-only. The agent reports the file and its size to the researcher instead of downloading it.
- `git grep -E -- '--upstream|saved input|upstream producer|external'` outside `docs/plans/` and historical `## Results` finds no instruction that still states the scoped default or the `external` state.
