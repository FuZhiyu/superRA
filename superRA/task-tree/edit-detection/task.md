---
title: "Detect File Edits Regardless of the Tool That Made Them"
status: not-started
depends_on: []
---

## Objective

Make the task hook's PostToolUse behaviors fire for a file edit made through any tool. Agents now write most edits as Bash Python heredocs, which the hook's command-text parsing cannot see, so task.md reconcile, the Markdown integrity check, the communicate reminder, and the reproduction reminder silently skip those edits.

- **One detector, no command parsing.** After every `Bash`, `Edit`, `Write`, and `apply_patch` call, the hook compares the watched files against a per-session rolling baseline and hands the changed paths to the existing consumers. A file counts as changed only when its content hash differs. Paths the tool call itself supplies are always included, so the call that seeds the baseline loses nothing.
- **Watched set.** Every `.md` under a task root, plus the literal-path scripts, deps, and Julia include closures of registered reproduction steps. Markdown outside a task root is watched only through the tool-supplied path.
- **`code_roots` is retired.** Delete the config key, its parser support, the hook branch, the contract row, and their tests; v0.5 is unreleased, so no compatibility surface stays. Missing-registration signals belong to [02-agent-signals](../../reproducibility/12-agent-protocol/02-agent-signals/task.md).
- **A step's out draws no reproduction reminder**, even when another step reads it as a dep: a rerun rewrites it.
- **Messages state what changed, not who changed it.** A change can come from the researcher, another agent, or a sync, and surfaces at the next tool call.
- **Approval check after the write is advisory.** A changed `task.md` that carries `status: approved` with blocking review notes draws non-blocking feedback naming the task. The PreToolUse approval and communicate gates stay as they are.
- **Structural Bash handling stays.** The `mv` / `rm` reconcile and the same-parent rename cascade keep reading the command, since a deletion or rename needs its semantics.
- **Fail open and race-safe.** Any detector error is silence. Parallel tool calls run the hook concurrently, so baseline writes are atomic; a lost update may repeat a reminder and must not corrupt state. Detector state is gitignored and lives outside `superRA/`.
- **Cost.** Report the measured latency the detector adds per Bash call on this repository's tree. Build the reproduction graph only when a watched `task.md` changed or no cached watched list exists.
- **Validation.**
  - Fixtures, each a file changed on disk followed by a `Bash` PostToolUse payload:
    - a `task.md` edit reconciles and propagates status;
    - a task-root `.md` edit draws integrity feedback;
    - a registered script edit draws the reminder once per session;
    - a rewritten out that another step reads is silent;
    - a touch with unchanged content is silent;
    - the first event of a session seeds the baseline and still handles its tool-supplied path;
    - a tree without reproduction config keeps the Markdown behaviors;
    - concurrent invocations leave a readable baseline.
  - The Codex payload shapes pass the same fixtures.
  - One realistic session per harness shows a heredoc edit of a `task.md` triggering status propagation.

## Details

- **Evidence for the shift** (local transcripts, 2026-09-20): Python-heredoc writes are about 75% of file edits for `claude-opus-5` and `claude-fable-5-1`, and about 80% for Codex `gpt-6-astra`; none followed a hook denial. In auto and bypass-permissions modes Claude Code injects a Bash-first instruction (anthropics/claude-code [#92271](https://github.com/anthropics/claude-code/issues/92271)), and a filesystem-scoped hook event is an open request ([#87356](https://github.com/anthropics/claude-code/issues/87356)). The design follows the models instead of steering them back to Edit.
- **Entry points.**
  - [task_hook.py:571](../../../skills/task-tree/scripts/task_hook.py#L571) `_handle_bash` acts only on `mv`/`rm`/`cp`/`mkdir` that mention a task root.
  - [task_hook.py:671](../../../skills/task-tree/scripts/task_hook.py#L671) `_handle_edit_write` shows the consumer sequence; every consumer already takes a `file_paths` list.
  - [task_hook.py:204](../../../skills/task-tree/scripts/task_hook.py#L204) `_reproduction_reminder` holds the `code_roots` branch to delete.
- **Suggested detector:** [HashCache](../../../skills/task-tree/scripts/_repro_state.py#L126) already persists `(size, mtime_ns, sha256)` per path, costs one `stat` on a hit, and survives Dropbox. A per-session instance is the baseline: a changed file is one whose hash differs from the cached entry before the call refreshes it.
- **Measured on this repository:** the warm hook takes about 60 ms per call, about 40 ms of it `uv` plus interpreter start; a cold first call took 245 ms. Statting the 167 files under `superRA/` takes 0.9 ms.
- **Not pursued:** a git-based diff cannot tell a new edit from an already-dirty file; a baseline refresh on UserPromptSubmit and a Stop sweep add hook wiring for reminders that are advisory anyway. Revisit the refresh only if reports of researcher edits prove noisy.
- **Stale references to sweep with the `code_roots` deletion:** [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md), [internals.md](../../../skills/task-tree/references/internals.md), the "code roots" mention in the [reproducibility](../../reproducibility/task.md) context, and [05-reminder-hook](../../reproducibility/05-reminder-hook/task.md) results.
- **Left alone:** `bash_markdown_mutation_targets` in [_apply_patch.py:158](../../../skills/task-tree/scripts/_apply_patch.py#L158) keeps serving the PreToolUse gates for `sed -i`, redirects, and `tee`.
