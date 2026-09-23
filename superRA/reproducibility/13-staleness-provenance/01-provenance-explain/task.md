---
title: "Resolve Hash Provenance and Rebuild `explain` Around It"
status: not-started
depends_on: []
---

## Objective

Build the provenance resolver and make `superra repro explain <target>` report, for every changed node, its recorded and current hash, where each came from, a named cause, and a runnable next command. Fix the two misleading statuses the case exposed.

- **Targets.** A task gives causes grouped across its stale steps; `task#step` or a unique bare step name gives one row per changed node; a path gives that file's provenance with its producer and consumers. `build`, `accept`, and `revoke` keep rejecting bare step names.
- **Sources.** Local receipt, acceptance ledger, lock history (`git log --all -- pytask.lock`, cached per revision in `.superra-repro/`), git blob history of each changed tracked dependency (sha256 of each blob until one matches the recorded hash, depth-capped), and Dropbox conflicted copies beside the file. A dependency matched on both sides shows `git <rev> → <rev>` with a diffstat and a capped diff.
- **Closed cause set** in JSON `cause` and the same words in text, at least: older build synced here; recorded build from another branch; dependency edited in commit X; reviewed bytes replaced; no known source. Each group or row ends with an exact runnable command. A `searched:` footer names the revisions, branches, and paths examined.
- **Acceptance fallback (report §4).** An acceptance that no longer validates no longer overrides a step whose bytes match its successful lock entry: the step is fresh, and its reason names the invalid acceptance and `repro revoke`.
- **Check stamps (report §5).** A check with no local stamp whose lock entry matches the current inputs reports `passed at these inputs in lock <rev>; not run here`, distinct from a never-run check; its status stays non-fresh.
- **Output budget and cost** per the group constraints; the raw JSON dump in text output is gone.
- **Validation:** a fixture replays the report's case — two clones, a coauthor lock commit, older output bytes restored to fake sync lag, a lock hash introduced by a merged side branch, a docstring edit to a tracked dependency, the §4 accept-then-sync sequence, and a check run only in the other clone — and asserts each cause, command, and footer; the full task-tree suite passes; [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction) documents the new targets, flags, and cause set.

## Details

- **Entry points.** [repro_run.py explain wiring](../../../../skills/task-tree/scripts/repro_run.py#L715-L740), [inspect_baseline](../../../../skills/task-tree/scripts/_repro_acceptance.py#L276), [format_explain](../../../../skills/task-tree/scripts/_repro_state.py#L877), [select_steps](../../../../skills/task-tree/scripts/_repro_state.py#L755). A new `_repro_provenance.py` keeps the resolver apart from status.
- **§4 origin.** The override is in [apply_to_status](../../../../skills/task-tree/scripts/_repro_acceptance.py#L247): `if entry.status == 'fresh' or …: entry.status = 'stale'`, added in `d4d0ca08`. Nothing in that commit's task justifies overriding a lock-fresh step.
- **Bare step names were deleted on purpose** in [01-cli-decision-support](../../12-agent-protocol/01-cli-decision-support/task.md) because they were ambiguous as build targets. Explain is read-only, and a unique name is unambiguous; keep the qualified-form error for non-unique names.
- **Lock ids are logical paths** (`${OUT}/…`), so lock-history matches key on the logical node id, not the resolved path.
- **Directory and `saved-input:` states** are not file hashes; resolve them against lock history and ledger only.
- Load `superRA:task-tree` and `superRA:reproducibility` before editing. High-stakes for agent behavior: a reviewer should run `explain` on the fixture and judge the text as a fresh agent would.
