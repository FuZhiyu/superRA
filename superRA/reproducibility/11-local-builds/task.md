---
title: "Build What This Machine Can Check: Producer Chain by Default, Online-Only Data Reported"
status: not-started
depends_on: []
---

## Objective

Make `superra repro` act on what the machine running it can verify. `build` and `status` include a selection's producer chain by default, `--only` restricts them to the named steps, and no command ever downloads a file: online-only and absent data are reported, not misread. The dashboard shows each state, where staleness starts, and what is online-only at a glance. At Mature, fold the result into the tasks §At Mature lists.

### Decisions

**Checking files.** A check never downloads. Each file gets one outcome:

| File | Outcome |
|---|---|
| On disk, or in this machine's hash cache at its current size and mtime | its hash: **matches** or **changed** |
| Absent, and a step produces it | **absent** (its producer reads `missing`) |
| Absent, and no step produces it | **unknown** |
| Online-only and not cached: size differs from the lock | **changed** |
| Online-only and not cached: same size; or the read fails | **unknown** |

- **Online-only means** `st_flags & SF_DATALESS` (File Provider: Dropbox, Google Drive, Box, OneDrive, iCloud), or a zero-byte file carrying the `com.dropbox.placeholder` xattr (legacy Dropbox). An mtime difference alone never counts as a change.
- **The lock records each file's size** beside its hash.

**Step states.** Each step takes the first state its own files support:

| If | State |
|---|---|
| Its definition or any of its files is **changed** | `stale` |
| An output is **absent** | `missing` |
| Any file is **unknown** | `unverified` |
| Its last run failed | `failed` |
| Otherwise, or a valid acceptance covers it | `fresh` |

- **`external` is removed as a state.** "External input" stays as the name for a file no step produces.
- **Reported state.** A `fresh` or `unverified` step whose producer is `stale`, `missing`, or `failed` is reported `stale`, with the reason naming that producer. The step's own state is kept alongside.

**Commands.**

- **Default scope.** `build`, `status`, and `build --dry-run` resolve the targets plus their transitive producers, through one resolver.
- **`--only`** restricts to the named selection; files from producers outside it are used as they sit on disk, as today. Use it when another session is editing a producer in this worktree. **`--upstream`** stays as a hidden no-op alias.
- **`--force`** reruns the named selection only; added producers run only when their state calls for it.
- **What runs.** In dependency order, a build runs `stale`, `missing`, `failed`, and forced steps. `unverified` steps never run, and their outputs are used as they are. A step stale only through upstream reruns only if its inputs changed after its producer ran (existing behavior).
- **Download gate.** Before running anything, if a step that will run reads a file not on disk (online-only, or absent with no producer), the build runs nothing. It lists those files with their sizes, capped, and points to the download notes in the `reproducibility` skill. No command downloads, and no download flag exists.
- **Build preview.** Before executing, `build` prints the added producers that will run, with their last recorded durations (capped). It does not prompt. `--dry-run` keeps its per-step listing.
- **`accept` and `revoke`** act on the named steps only. `accept` refuses to record a file it cannot hash here, naming it. After recording, it names the non-fresh producers behind the accepted step (capped) and says the step reads stale until they are built or accepted.
- **Default `status` output.**
  - One line per selected step.
  - Producers that are `stale`, `missing`, or `failed` are listed (capped); fresh producers are counted.
  - `unverified` steps outside the selection collapse to one line with their count, total online-only size, and where tracing stopped.
  - Exit 0 when every assessed step is `fresh` or `unverified`; 1 when a selected step's own state is `stale`, `missing`, or `failed`; 3 when the selection's own states are fine but a producer behind it is `stale`, `missing`, or `failed`.

**Display.** [03-state-display](03-state-display/task.md) owns the dashboard design language for these states.

**Unchanged.** Content hashing, early cutoff, acceptance validation, `explain`, and `impact`.

### Constraints

- [CLAUDE.md](../../../CLAUDE.md) §Bounded Agent-Facing Output governs every new or changed line of CLI and hook output.
- The task-tree core stays stdlib-only. Detection uses `os.lstat` flags and a `ctypes` `getxattr` call; `os.listxattr` does not exist on macOS.

## Details

### Why

- **Scoped default.** A TreasuryGIV session (transcript `02d0fe7f`, 2026-10-01) ran `status paper-reframing`, saw stale steps across two tasks, and passed all seven `task#step` selectors to `build`. Its own afterword: "Running `compile-deck` alone would've skipped stale upstream steps, so I listed them manually to avoid an unexpectedly long rerun."
- **Online-only data.** The hash cache reads any file it has not hashed at the current size and mtime ([_repro_state.py:202-220](../../../skills/task-tree/scripts/_repro_state.py#L202-L220)). On an online-only file, that read downloads it; when the read fails, the `OSError` becomes `None`, so an existing output reads `missing` and its producer reruns. A legacy Dropbox placeholder reads as an empty file and would hash as one. The producer-chain default widens both problems from the selection to its whole chain.

### Prior art (2026-10-01 surveys)

- **Upstream-by-default is the norm:** DVC, Snakemake, R `targets`, make, doit. The "only" modes are escape hatches that trust disk state: DVC `-s`, `targets` `shortcut = TRUE`.
- **Force scopes are separate** (Snakemake `-f` vs `-F`). **Accepting without running is step-local** (`dvc commit`, `make -t`, Snakemake `--touch`), and in those tools indistinguishable from a run.
- **A failed upstream:** pytask, Snakemake, and DVC skip the downstream step. Only DVC `--ignore-errors` runs it anyway, and it records the downstream step as up to date.
- **A missing raw input** is an error in make, Snakemake, and pytask, and a changed dependency in DVC; no tool has a state for it. DVC `--allow-missing` and Snakemake use existing outputs when the producer has no other change, the same rule as `unverified`.
- **No tool has `unverified`.** make and Snakemake compare mtimes, so they never read files. DVC and pytask hash, so a check downloads or fails. Hashing without implicit downloads leaves the gap `unverified` names.
- Sources: [DVC repro](https://doc.dvc.org/command-reference/repro), [DVC status](https://doc.dvc.org/command-reference/status), [Snakemake CLI](https://snakemake.readthedocs.io/en/stable/executing/cli.html), [tar_make](https://docs.ropensci.org/targets/reference/tar_make.html), [pytask CLI](https://pytask-dev.readthedocs.io/en/stable/tutorials/invoking_pytask.html).

### Online-only facts (checked on OlinStudio, macOS 15.7.3)

- **`lstat` returns the real size and mtime of an online-only File Provider file without downloading it.** Google Drive held 405 such files and Box 29, each with `st_blocks == 0` and `SF_DATALESS` set (mask it: one read `0x40000060`).
- **Directories:** `stat` inside an online-only directory can download that directory's listing ([TN3150](https://developer.apple.com/documentation/technotes/tn3150-getting-ready-for-data-less-files)), so walk a directory dep by checking each directory's flag before descending.
- **Legacy Dropbox:** Olin's `~/Dropbox` is the legacy client. Its online-only placeholders are zero-byte files with the `com.dropbox.placeholder` xattr and no `SF_DATALESS`; one exists at `~/Dropbox/764011267880-1701976534116.pdf`. None of 1,185 zero-byte files under `research_projects/` is one.
- **Downloading.** No reliable shell command exists:
  - `fileproviderctl` has no `materialize` here, and `brctl download` is iCloud-only.
  - A plain read may leave a File Provider file partial, and failed once with `ETIMEDOUT` on Google Drive.
  - Dropbox staff confirm there is no terminal option for legacy placeholders.
  - A coordinated read (`NSFileCoordinator`) requests the whole file; it works from PyObjC (`uv run --with pyobjc-framework-Cocoa`) or Swift.
- **Unverified:** whether size and mtime stay stable across download and eviction. The hash cache depends on it.

### Engine facts the change relies on

- **`accept` already ignores the scope default.** It selects with `include_ancestors=False` and reads `local_status` ([_repro_acceptance.py:438](../../../skills/task-tree/scripts/_repro_acceptance.py#L438), [:483](../../../skills/task-tree/scripts/_repro_acceptance.py#L483)).
- **The upstream cascade never forces a rerun.** It lifts a fresh step to stale in status only ([_repro_acceptance.py:384-385](../../../skills/task-tree/scripts/_repro_acceptance.py#L384-L385)). `build` reclassifies each step against its own target after its producers finish ([repro_run.py:115-120](../../../skills/task-tree/scripts/repro_run.py#L115-L120)).
- **`--force` covers the whole resolved scope today** ([repro_run.py:743](../../../skills/task-tree/scripts/repro_run.py#L743)).
- **The dashboard already assesses upstream** ([plan_dashboard.py:1483](../../../skills/task-tree/scripts/plan_dashboard.py#L1483), [_task_snapshot.py:68](../../../skills/task-tree/scripts/_task_snapshot.py#L68)).
- **Archived-task outputs are already external inputs** in the active graph, so the producer walk stops there.

### At Mature

These task files state the scoped default or the `external` state as current contract; rewrite their lines when folding: [02-runner](../02-runner/task.md), [03-task-interface](../03-task-interface/task.md), [04-dashboard-view](../04-dashboard-view/task.md), [06-skill](../06-skill/task.md), and [07-workflow-integration](../07-workflow-integration/task.md).

## Review Notes

Planning review, design-review mode, checked against the code at `6f4411bf`. The six findings of the prior review (`git show 6abd9fe6`) are resolved except where noted in items 1 and 12.

1. **[BLOCKING] §Step states contradicts the precedence in `_classify` and drops three of its cases.**
   - **A failed or interrupted run ranks below `unverified`.** Today `failed` overrides `stale` and `missing`, and an interrupted run (`running`/`pending`) always reads `failed` ([_repro_state.py:890-911](../../../skills/task-tree/scripts/_repro_state.py#L890-L911)). Under the table, a step whose last run died and which reads one online-only file is `unverified`. It never runs, and consumers use its partial outputs as they are.
   - **"Never built" is missing from the table.** Today an absent external input outranks "never built" ([_repro_state.py:872-886](../../../skills/task-tree/scripts/_repro_state.py#L872-L886)). The table does not say whether a never-built step with an absent raw input is `missing` (it must run, so the gate blocks the build) or `unverified` (it never runs). This is the residue of the prior review's item 1.
   - **A check step's absent stamp is an absent output.** Read literally, the table makes every check that passed on another machine `missing`. The code ([_repro_state.py:935](../../../skills/task-tree/scripts/_repro_state.py#L935)) and the documented `fresh` row ([commands.md:122](../../../skills/task-tree/references/commands.md#L122)) treat that check as fresh. The table also does not say what such a check reads when a dep is unknown.
   - **`stale` now precedes `missing`.** The code checks absent outputs first ([_repro_state.py:931-948](../../../skills/task-tree/scripts/_repro_state.py#L931-L948)). The run decision is the same, but reasons and tests change.

   **Fix:** rewrite the table in the code's order and add the missing rows. Put `failed` (interrupted included) above `unverified`, place "never built", and keep the check-elsewhere rule, with `unverified` when a dep is unknown.
2. **[BLOCKING] The size rule misfires on every legacy Dropbox placeholder.** `lstat` reports a placeholder's size as 0: `ls -lO ~/Dropbox/764011267880-1701976534116.pdf` shows `0` on OlinStudio. The §Checking files row "size differs from the lock → changed" therefore marks every legacy placeholder `changed`. A consumer turns `stale` and must run, so the gate blocks the build. A producer whose output is a placeholder reruns. **Fix:** compare sizes only for `SF_DATALESS` files; a legacy placeholder is always **unknown**.
3. **[BLOCKING] The download gate runs only before scheduling, but the run decision changes during the build.** `build` reclassifies each step after its producers finish ([repro_run.py:115-120](../../../skills/task-tree/scripts/repro_run.py#L115-L120)). Take a step that is `fresh` or `unverified` when the build starts. When its producer's rerun changes bytes, the step turns `stale` and runs. Its command then reads an online-only dep, which downloads it. **Fix:** in [02-upstream-default](02-upstream-default/task.md):
   - Also refuse at step start in `_missing_inputs` ([repro_run.py:123-133](../../../skills/task-tree/scripts/repro_run.py#L123-L133)): the step fails "cannot start", lists the files, and its descendants skip.
   - Define the up-front set: own state `stale`, `missing`, or `failed`, plus forced steps.
   - Say whether `--dry-run` prints the gate's file list.
4. **[BLOCKING] Some file readers bypass `HashCache`, and §Unchanged keeps `explain` as it is.**
   - **`explain` reads a dep's text for its diff** ([_repro_provenance.py:597](../../../skills/task-tree/scripts/_repro_provenance.py#L597)), and `accept`'s preview does the same ([_repro_acceptance.py:424](../../../skills/task-tree/scripts/_repro_acceptance.py#L424)). For a cached online-only file whose hash changed, both open the file and download it.
   - **`explain` prints `missing here` for any `None` hash** ([_repro_provenance.py:916](../../../skills/task-tree/scripts/_repro_provenance.py#L916)), so it would report an online-only file as missing.
   - **The `--only` saved-input check reads a sidecar's text** ([_repro_scope.py:74](../../../skills/task-tree/scripts/_repro_scope.py#L74)).

   **Fix:** list `_repro_provenance.py` and these call sites under [01-local-graph](01-local-graph/task.md) §Details. Qualify §Unchanged: `explain` reports unknown files as unknown and never opens an online-only file for a diff.
5. **[BLOCKING] The frontier hint has no exit for an `unverified` producer.** `CURRENT = {"fresh", "saved"}` ([_task_snapshot.py:11](../../../skills/task-tree/scripts/_task_snapshot.py#L11)). The frontier and `task read` would therefore list every input from an `unverified` producer with "rebuild before relying on it: superra repro build …". A build never runs `unverified` steps, so this warning recurs every session and no build clears it, which breaks §Bounded Agent-Facing Output's "Every warning has an exit". **Fix:** add a §Views bullet to 02. Either treat `unverified` as current, matching `status` exit 0, or list it with the download note in place of the build hint.
6. **[BLOCKING] No task owns the per-file outcome that the gate, `status`, and the step panel all read.** Three places need each file's outcome, online-only flag, and size: the gate's and the summary line's file lists with sizes in 02, and the panel's cloud-marked files and "N files online-only here (size)" in [03-state-display](03-state-display/task.md). `StepStatus.to_dict` carries only `deps` and `outs` ([_repro_state.py:694-719](../../../skills/task-tree/scripts/_repro_state.py#L694-L719)). Whichever task adds these fields would edit another task's surface. **Fix:** give 01 a per-file row on `StepStatus` (logical path, outcome, online-only, size) exposed in JSON, which 02 and 03 consume.
7. **[BLOCKING] In 03, "dashed" and "faded" already mean something else in the dashboard.**
   - **Dashed means a check step.** Check steps draw a dashed border with a solid left edge ([dashboard.css:1704](../../../skills/task-tree/scripts/templates/dashboard.css#L1704)), and the legend's "check step" item is dashed ([:1751](../../../skills/task-tree/scripts/templates/dashboard.css#L1751)). An inherited-stale check step would be dashed all round, and the legend would give dashed two meanings.
   - **Faded means off or unfocused.** Zero-count legend items fade to 0.45 ([:1592](../../../skills/task-tree/scripts/templates/dashboard.css#L1592)), and edge focus dims every other wire to 0.22 ([:2527](../../../skills/task-tree/scripts/templates/dashboard.css#L2527)). Faded online-only wires would read as unfocused, and the legend's "faded" sample as an empty state.

   **Fix:** re-encode check steps or pick another inherited channel. Choose a fade that differs from these two. State how a step that is own-`unverified` and inherited-`stale` draws.
8. **[ADVISORY] The 01/02 split leaks.** When 01 removes `external`, `format_status` breaks: its `_MARKS` has no `unverified` key ([_repro_state.py:1125](../../../skills/task-tree/scripts/_repro_state.py#L1125)). So do the `external` branches at [repro_run.py:124-148](../../../skills/task-tree/scripts/repro_run.py#L124-L148). `_run_step` skips only `fresh` steps ([repro_run.py:141](../../../skills/task-tree/scripts/repro_run.py#L141)), so between 01 and 02 a build runs `unverified` steps and downloads their inputs. Move into 01 the minimal rule that `unverified` never runs, plus its mark. The 03 and 04 boundaries hold apart from item 9.
9. **[ADVISORY] 03 and 04 both document the dashboard.** 03 edits "the dashboard's reproduction description" without naming the file. 04 edits the docs-site [dashboard page](../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md), which describes the cards, but does not depend on 03. Name 03's file, and either give the page to 03 or add 03 to 04's `depends_on`.
10. **[ADVISORY] Two terms need definitions.**
    - **"Where staleness starts":** the panel link and the solid-only-at-origin rule need the origin step. The cascade reason names only the immediate parent ([_repro_acceptance.py:385](../../../skills/task-tree/scripts/_repro_acceptance.py#L385)). Say whether 01 records the origin or 03 walks the graph to find it.
    - **"Where tracing stopped":** the `status` summary line and 04's §Recording a Result both use it without saying what it names.
11. **[ADVISORY] The lock-size rule leaves two node kinds open.**
    - **Directory deps** have one tree hash and no single size.
    - **Sidecar-tracked outs** hash the sidecar, while consumers read the large file ([_repro_state.py:287-298](../../../skills/task-tree/scripts/_repro_state.py#L287-L298), [:350-357](../../../skills/task-tree/scripts/_repro_state.py#L350-L357)). The gate must test the out's path, not the sidecar's.
12. **[ADVISORY] Some documentation edits have no owner.**
    - [task-file-contract.md:103](../../../skills/task-tree/references/task-file-contract.md#L103) still gives the frontier hint with `--upstream` (prior item 4).
    - 01's doc bullet places the state table in task-file-contract.md. The table is at [commands.md:120-126](../../../skills/task-tree/references/commands.md#L120-L126), on 02's surface.
    - The `--only` refusal still says "use --upstream" ([repro_run.py:381](../../../skills/task-tree/scripts/repro_run.py#L381)).
13. **[ADVISORY] The gate's only pointer is the download notes, which cannot fetch an absent raw input.** For a file that only an added producer reads, `--only` is the exit; name it in the gate message.
14. **[ADVISORY] The completion gate's treatment of `unverified` is unstated.** [protect-and-completion.md:11](../../../skills/reproducibility/references/protect-and-completion.md#L11) passes only on `fresh`, except steps the stale rule reported. 04 should say whether an `unverified` step passes the gate when it is reported.
15. **[ADVISORY] "unverified" already names something else.** Saved-input provenance and boundary changes use it to mean "no successful baseline to compare" ([_repro_scope.py:47](../../../skills/task-tree/scripts/_repro_scope.py#L47), [:102](../../../skills/task-tree/scripts/_repro_scope.py#L102)). Rename that use.
16. **[ADVISORY] Two small corrections.**
    - 03 cites `reproBuildScope` at dashboard.js:2277; it is at [:2297](../../../skills/task-tree/scripts/templates/dashboard.js#L2297).
    - 01's validation sends the File Provider check to home-studio or home-server. OlinStudio has Google Drive and Box File Provider mounts under `~/Library/CloudStorage/`, as the parent's own facts record.
