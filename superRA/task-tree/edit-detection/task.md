---
title: "Detect File Edits Regardless of the Tool That Made Them"
status: approved
depends_on: []
---

## Objective

Make the task hook's PostToolUse behaviors fire for a file edit made through any tool. Agents now write most edits as Bash Python heredocs, which the hook's command-text parsing cannot see, so task.md reconcile, the Markdown integrity check, the communicate reminder, and the reproduction reminder silently skip those edits.

- **One detector, no command parsing.** After every `Bash`, `Edit`, `Write`, and `apply_patch` call, the hook compares the watched files against a per-session rolling baseline and hands the changed paths to the existing consumers. A file counts as changed only when its content hash differs. Paths the tool call itself supplies are always included, so the call that seeds the baseline loses nothing.
- **Watched set.** Every `.md` and common script file under a task root, plus the literal-path scripts, deps, and Julia include closures of registered reproduction steps. Markdown outside a task root is watched only through the tool-supplied path.
- **An unregistered script under a task root draws the reproduction reminder** with no owning step named, in trees that carry reproduction config: a retained task companion is always registered.
- **`code_roots` is retired.** The hook is its only consumer. Delete the config key, its parser support, the hook branch, the contract row, and their tests; v0.5 is unreleased, so no compatibility surface stays. Other missing-registration signals belong to [02-agent-signals](../../reproducibility/12-agent-protocol/02-agent-signals/task.md).
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
    - an unregistered script under a task's `attachments/` draws the reminder with no owning step, and stays silent in a tree without reproduction config;
    - a rewritten out that another step reads is silent;
    - a touch with unchanged content is silent;
    - the first event of a session seeds the baseline and still handles its tool-supplied path;
    - a tree without reproduction config keeps the Markdown behaviors;
    - concurrent invocations leave a readable baseline.
  - The Codex payload shapes pass the same fixtures.
  - One realistic session per harness shows a heredoc edit of a `task.md` triggering status propagation.

## Details

- **Evidence for the shift** (local transcripts, 2026-09-20): Python-heredoc writes are about 75% of file edits for `claude-opus-5` and `claude-fable-5-1`, and about 80% for Codex `gpt-6-astra`; none followed a hook denial. In auto and bypass-permissions modes Claude Code injects a Bash-first instruction (anthropics/claude-code [#92271](https://github.com/anthropics/claude-code/issues/92271)), and a filesystem-scoped hook event is an open request ([#87356](https://github.com/anthropics/claude-code/issues/87356)). The design follows the models instead of steering them back to Edit.
- **Suggested detector:** [HashCache](../../../skills/task-tree/scripts/_repro_state.py#L126) already persists `(size, mtime_ns, sha256)` per path, costs one `stat` on a hit, and survives Dropbox. A per-session instance is the baseline: a changed file is one whose hash differs from the cached entry before the call refreshes it.
- **Which extensions count as a common script is the open design call:** start from `.jl`, `.py`, `.R`, `.do`, `.sh`, `.ipynb`, `.sql`, and `.m`, and report the rule chosen.
- **Measured on this repository:** the warm hook takes about 60 ms per call, about 40 ms of it `uv` plus interpreter start; a cold first call took 245 ms. Statting the 167 files under `superRA/` takes 0.9 ms.
- **Not pursued:** a git-based diff cannot tell a new edit from an already-dirty file; a baseline refresh on UserPromptSubmit and a Stop sweep add hook wiring for reminders that are advisory anyway. Revisit the refresh only if reports of researcher edits prove noisy.
- **Stale references to sweep with the `code_roots` deletion:** [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md), [internals.md](../../../skills/task-tree/references/internals.md), the "code roots" mention in the [reproducibility](../../reproducibility/task.md) context, and [05-reminder-hook](../../reproducibility/05-reminder-hook/task.md) results.
- **Left alone:** `bash_markdown_mutation_targets` in [_apply_patch.py:158](../../../skills/task-tree/scripts/_apply_patch.py#L158) keeps serving the PreToolUse gates for `sed -i`, redirects, and `tee`.

## Results

The task hook now handles a file edit the same way whichever tool made it. A per-session content baseline ([_edit_detect.py](../../../skills/task-tree/scripts/_edit_detect.py)) finds the changed files, and one consumer sequence ([`_process_paths`](../../../skills/task-tree/scripts/task_hook.py#L908)) replaces the separate Edit/Write and `apply_patch` handlers. Mechanics: [internals.md §Hook Architecture](../../../skills/task-tree/references/internals.md#hook-architecture).

- **A heredoc edit of a `task.md` rolls status up in a real Claude Code session.** `claude -p --plugin-dir <this worktree>` ran `ls`, then a Python heredoc flipping a child to `approved`: the root rolled up to `approved` and the model received the hook feedback.
- **The live Codex check did not run.** Codex executes only hooks whose hash `~/.codex/config.toml` trusts and sets `PLUGIN_ROOT` itself, so neither a project `hooks.json` nor an environment override reached this worktree's code, and I did not edit that config. The Codex payload shapes pass as fixtures; rerun the same two-step prompt under `codex exec` once the installed plugin carries this change.
- **Cost on this repository (157 watched files, 46 outside the task root):**

| Path | Time |
|---|---:|
| Steady call, nothing changed | 3.2 ms |
| Whole hook process, no-op Bash call | 29.7 ms before, 36.2 ms after |
| First call of a session (hash everything, build the graph) | 49 ms |
| Graph rebuild, only after a `task.md` or `config.yaml` change | 28 ms |
| Locating the trees to check, command naming nothing outside the session cwd | 0.07 ms |
| The same, when the command names a path outside it (two `git rev-parse`) | 16 ms |

### Design calls

- **Own baseline, not `HashCache`.** `HashCache` reads every file on a miss, so seeding would hash a multi-gigabyte data dep. The baseline hashes files up to 4 MB ([`HASH_MAX_BYTES`](../../../skills/task-tree/scripts/_edit_detect.py#L39)) and at most 64 MB per call, and compares the rest by size and mtime.
- **Script rule:** `.jl .py .r .do .sh .ipynb .sql .m`, case-insensitive ([`SCRIPT_SUFFIXES`](../../../skills/task-tree/scripts/_edit_detect.py#L32)).
- **Which trees are checked:** the task root beside or above the session anchor, each tool-supplied path, and each absolute path the Bash command names, because an agent in a sibling worktree addresses it by absolute path. The command is read only for where to look. The upward walk stops at a repository top, and a root with more than 5,000 watched files is ignored as mis-resolved.
- **A root in a foreign checkout is dropped,** since detection leads to a reconcile that rewrites task files. Membership is the `guard-foreign-checkout` rule, moved to [_checkout_scope.py](../../../skills/task-tree/scripts/_checkout_scope.py) and shared by the gate and the detector rather than copied: a path under the session anchor, or in a checkout sharing the anchor's git common dir, is the session's own. Every worktree of the session's repository therefore stays in reach — that is where superRA dispatches implementers — and another repository does not.
- **The anchor is shared too, not just the rule.** [`session_anchor`](../../../skills/task-tree/scripts/_checkout_scope.py#L26-L42) resolves `CLAUDE_PROJECT_DIR` before the payload `cwd`, and the gate's `main()` and the detector both call it. The payload `cwd` follows a `cd`, so a session that stepped into another checkout would otherwise read that checkout as its own — the original escape — while the gate, anchored on the project dir, saw nothing to prompt about. One function now decides for both, and the gate no longer resolves its own anchor inline.
- **The hook never reports its own writes.** Reconcile rewrites ancestor statuses, so detection runs before any reconcile, and once one ran the hook detects again and discards the result.
- **Reminder floods collapse.** More than five reproduction reminders in one call (a checkout, a merge) become one line pointing at `superra repro status .`.
- **Every reminder names a runnable target.** `superra repro status` needs at least one; a reminder with owning steps names them as `task#step` selectors, and one with none falls back to `.`, the whole active tree.
- **"Carries reproduction config"** means any step, any `## Reproduction` section, or any `reproduction:` config value ([`has_reproduction`](../../../skills/task-tree/scripts/_repro_signals.py#L194)), which also closes the `code_roots` advisory in [02-agent-signals](../../reproducibility/12-agent-protocol/02-agent-signals/task.md).
- **The post-write approval check needed no new code:** reconcile already reports `approved` with `[BLOCKING]` notes, and now runs for Bash-made edits.

### Known limits

- A Bash edit in a sibling worktree is seen only when the command names an absolute path into it, and the reach is by mention rather than by edit: naming a path in a worktree of the session's own repository gives it a self-ignored `.superra-repro/` baseline, and a later mention reconciles any `task.md` changed there. Another repository is out of reach entirely.
- A tool-supplied path is still processed wherever it points, including a foreign checkout, which keeps the pre-existing `Edit`/`Write` behavior. That route passes the `guard-foreign-checkout` PreToolUse gate first, so a foreign `task.md` write reaches the hook only after the researcher approved it — and degrades where that gate's `ask` degrades, on the runtimes [agent-cwd-isolation](../agent-cwd-isolation/task.md) §Boundaries leaves unverified.
- Directory deps are not walked, so a Bash-made edit inside a registered directory dep is silent, while an `Edit` of the same file still reminds through its tool-supplied path.
- Two edits to the same script in one session draw one reminder, as before.
- A change made by the researcher or another agent surfaces at this session's next tool call, worded as a fact about the file.
- A project that still has `code_roots` in `config.yaml` now gets an unknown-key error from the config parser.

### Validation

[test_edit_detect.py](../../../skills/task-tree/scripts/test_edit_detect.py) holds 24 cases, each a file changed on disk followed by a `Bash` payload whose command does not name it: every fixture the objective lists, plus the advisory approval feedback, a newly registered dep seeded silently, the reminder collapse, a corrupt baseline, a structural `rm` that stays quiet about the hook's own rollup, the hashing budget, the oversized-root guard, and the repository-top stop. The `code_roots` tests in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py) were rewritten onto registered deps and the companion-script rule.

- **The two-checkout reproduction is a red-green case.** `test_a_foreign_checkout_is_left_alone` builds two disposable `git init` checkouts, sends a read-only `ls` naming the foreign one from a session in the other, edits a `task.md` in each, and asserts the foreign checkout ends with exactly the one file it was edited in dirty, its root `task.md` unrolled, and no `.superra-repro/`, while the session's own tree still reconciles in that same call. Without the `plan_roots` filter it fails on the foreign root rolling up to `approved`.
- **A drifted payload `cwd` is a red-green case too.** `test_a_payload_cwd_inside_the_foreign_checkout_does_not_unlock_it` replays the reviewer's second escape — `CLAUDE_PROJECT_DIR` on one scratch checkout, payload `cwd` on the other — and asserts the same three things. Anchored on the payload `cwd` it fails on the foreign root rolling up. The fixture also drops any ambient `CLAUDE_PROJECT_DIR` from the suite's own session, so every other case reads its `tmp_path` as the anchor.
- **The sibling-worktree reach has a case of its own.** `test_edit_in_a_sibling_worktree_is_found_through_the_command` replaces the earlier version, which used two unrelated temporary directories and so no longer described the rule: it now adds a real `git worktree` and asserts a heredoc edit there is found and rolled up.
- **The gate keeps its own suite.** [tests/hooks/test-guard-foreign-checkout.sh](../../../tests/hooks/test-guard-foreign-checkout.sh), 24 checks, and [test_trace_confinement.py](../../../tests/harness-instruction-following/test_trace_confinement.py), 3 cases, both pass unchanged against the extracted rule and anchor.
- Full script suite with pytask: 1223 passed, 10 skipped (the browser suite under `tests/` deselected). The check step below was run by its command; its stamp was not built here, since `repro build` rewrites the committed `pytask.lock` from a worktree that is not merged yet. `task_hook.py` is also a dep of five other check steps, which the full suite covers; the browser check `dashboard-dag-design-interaction-check`, whose config fixture changed, passes by its own command (54 cases).

## Review Notes

### Second pass — thorough, on scope-fidelity and correctness against the design this landed beside

Read against the [12-agent-protocol group decisions](../../reproducibility/12-agent-protocol/task.md#decisions-researcher-2026-09-20) and its three children, the redesigned [reproducibility skill](../../../skills/reproducibility/SKILL.md), [_repro_signals.py](../../../skills/task-tree/scripts/_repro_signals.py), and the `guard-foreign-checkout` gate from [agent-cwd-isolation](../agent-cwd-isolation/task.md). All findings are closed.

Both routes by which the hook reached another checkout — a command naming a path into it, and a payload `cwd` that a `cd` moved into it — were replayed on two scratch checkouts, each escape reproduced first on the commit that carried it. At `a7f5585a` the foreign checkout ends with only the file it was itself edited in dirty, its root `task.md` unrolled and no `.superra-repro/`, while the session's own tree still reconciles in the same call. [test_edit_detect.py](../../../skills/task-tree/scripts/test_edit_detect.py) passes identically with and without an ambient `CLAUDE_PROJECT_DIR`, so its stripping of one hides nothing.

### First pass — thorough, on correctness and scope-fidelity

No blocking findings; four of five advisories were fixed or recorded under §Known limits after the pass, verified by the orchestrator's own tests. Verified by re-running the script suite (1088 passed, 140 skipped without pytask), by re-measuring the reported latencies, and by driving [task_hook.py](../../../skills/task-tree/scripts/task_hook.py) with payloads on scratch trees.

1. `[ADVISORY]` The objective's per-harness live-session check ran for Claude Code only. The Codex half is unrun for the reason §Results gives, and the rerun instruction it carries is the follow-up to track.

Cost claims check out: steady detection is 2.8–3.8 ms over the 159 watched files, and the whole hook process takes about 240 ms on a `task.md` change both before and after this change, so the detector adds roughly 40 ms there rather than a new reconcile cost.

## Reproduction

```yaml
steps:
  - name: edit-detection-check
    kind: check
    cmd: uv run --with pytest --with pyyaml python -m pytest skills/task-tree/scripts/test_edit_detect.py -q -p no:cacheprovider
    deps:
      - skills/task-tree/scripts/test_edit_detect.py
      - skills/task-tree/scripts/_edit_detect.py
      - skills/task-tree/scripts/_checkout_scope.py
      - skills/task-tree/scripts/task_hook.py
```
