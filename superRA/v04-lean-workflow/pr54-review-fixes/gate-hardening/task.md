---
title: "Harden the Approval and Communicate Gates"
status: not-started
depends_on: []
---

## Objective

The PreToolUse gates deny every bypass the review confirmed, across all three harness registries, with a denying regression test per bypass.

- One shared apply_patch parser — new `skills/task-tree/scripts/_apply_patch.py` — replaces the three hand-rolled copies (`task_approval_gate.py`, `task_hook.py`, `communicate_gate.py`), handling `Add/Update/Delete File` and `Move to:` headers.
- Hunk lines starting with neither `+` nor `-` — including the empty string — are context; each hunk matches from position 0, not only forward from the previous hunk.
- The approval gate fails closed on task.md targets: when it cannot reconstruct the patch result, it denies if the patch's added lines set `status: approved` and the file's `## Review Notes` carries `[BLOCKING]`. Same conservative deny for Bash in-place mutations (redirect, `tee`, `sed -i`, `cp`/`mv` targets), whose results are never reconstructable.
- The communicate gate counts only read evidence as a skill load: the exact `skill`-field match, Read-tool `file_path` records, and shell segments starting with a read verb (`cat`, `head`, `bat`, `less`, `sed -n`) targeting `skills/communicate/SKILL.md`. Mentions in `git diff`, `grep`, or other commands do not clear the gate. Subagent detection is `agent_id or agent_type`.
- Registry sweep: `hooks-codex.json` ensure-communicate (PreToolUse) and task-hook (PostToolUse) matchers gain `apply_patch`; guard-task-approval gains `Bash` in all three registries; `hooks-cursor.json` gains agent-model-guard.
- Shim cleanups: the identical 18-line gate shims dedupe into a shared `hooks/run-python-gate` (wrapper files kept so registry entries and executable bits are unchanged); `hooks/agent-model-guard` drops the `cat`/`printf` stdin buffering and execs python3 reading stdin directly.

## Details

File/line map from the review:

- Blank-context / out-of-order fail-open: [task_approval_gate.py:126](../../../../hooks/task_approval_gate.py#L126) (`line[:1] in (" ", "-")` classification, forward-only `cursor`).
- `Move to:` parser reset: [task_approval_gate.py:13](../../../../hooks/task_approval_gate.py#L13); the stronger grammars to consolidate are [task_hook.py:237](../../../../skills/task-tree/scripts/task_hook.py#L237) and [communicate_gate.py:15](../../../../hooks/communicate_gate.py#L15).
- Substring evidence: [communicate_gate.py:147](../../../../hooks/communicate_gate.py#L147); `_transcript_evidence` must carry `tool_name` per record to scope path evidence to reads.
- Subagent detection: [communicate_gate.py:160](../../../../hooks/communicate_gate.py#L160); mirror [sdk_load_harness.py:162](../../../../tests/harness-instruction-following/sdk_load_harness.py#L162).
- Matchers: [hooks-codex.json:33](../../../../hooks/hooks-codex.json#L33) and [:53](../../../../hooks/hooks-codex.json#L53) (`apply_patch`), [hooks.json:26](../../../../hooks/hooks.json#L26) (`Bash`), [hooks-cursor.json](../../../../hooks/hooks-cursor.json) (agent-model-guard entry; safe there because the script self-filters on tool_name).
- Tests pinning the old behavior: [test-ensure-communicate.sh:117](../../../../tests/hooks/test-ensure-communicate.sh#L117) pins the matcher without `apply_patch`; `test-codex-hooks.sh` and `check-harness-compatibility.sh` may pin matcher strings; `test-agent-model-guard.sh` may assert the `cat`/`printf` internals.

The Bash branch of the approval gate reuses the communicate gate's Bash-target regexes — move them into the shared module. A false deny from the conservative fallback is acceptable; the deny message should say to split the status flip from the notes edit. Residual accepted for the communicate gate: a genuine Read of the SKILL.md still counts as loaded.
