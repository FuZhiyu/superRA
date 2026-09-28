---
title: "Committed Records Stay Portable Across Machines and Branches"
status: not-started
depends_on:
  - 01-engine-freshness
---

## Objective

The committed reproduction records hold no machine-specific or user-identifying data, change only when their content changes, and merge across branches without routine conflicts; per-machine state stays on its machine.

- **No resolved absolute paths in `repro-acceptance.json`.** They appear under `baseline.spec.deps/outs[].resolved` when a variable resolves to an absolute root, against the contract's "a resolved root never enters the committed record". The committed baseline keeps only what reuse needs; `spec`, `run`, and `receipt` stay local.
- **No user name committed.** `actor = getpass.getuser()` ([_repro_acceptance.py:414](../../../../skills/task-tree/scripts/_repro_acceptance.py#L414)) contradicts [13-staleness-provenance](../../13-staleness-provenance/task.md)'s "No host or user name is committed anywhere"; git records the committer.
- **`env_probe` output cannot leak paths.** Its stdout is committed verbatim — today in `repro-builds.json` ([_repro_builds.py:88-91](../../../../skills/task-tree/scripts/_repro_builds.py#L88-L91)), after [01](../01-engine-freshness/task.md) in the `probes` table of `repro-lock.json` — and only a docs line guards it. Commit the digest, or enforce the rule.
- **Acceptance merges and degrades gracefully.** Slim each record, write none for a step whose state is unchanged, and set aside a malformed record instead of failing every command. A record's copy of the lock entry keeps only `spec`, `deps`, and `outs` from the `repro-lock.json` shape [01](../01-engine-freshness/task.md) settles, never `built_on`.
- **Per-machine state does not travel through Dropbox.** Run records, check stamps, receipts, and the mutation lock under `.superra-repro/` stop crossing machines.

Validation: two clones with different absolute roots and user names produce byte-identical committed records for the same build; two branches accepting different steps merge cleanly, or conflict without disabling `status`, `build`, and `accept`.

### Researcher decisions

- **Where per-machine state lives.** Recommendation: `~/.cache/superra/<project-id>/`. The alternative tags run records with a host and ignores foreign ones.
- **Which acceptance features stay.** The [0.5 design](../../attachments/v05-design.md#reviewed-acceptance-is-evidence-distinct-from-execution) keeps exact preview/apply, the `upstream` field, evidence-file hashing, and per-node notes. Recommendation: cut the token apply step, `upstream`, and evidence hashing; the required reason can cite evidence.

Owning tasks: [reviewed-acceptance](../../02-runner/reviewed-acceptance/task.md), [02-build-record](../../13-staleness-provenance/02-build-record/task.md).

## Details

### Evidence (engine and dashboard reviews, reproduced on scratch projects)

- **Absolute paths.** With `OUT: {env: OUTROOT}` set to an absolute path, build then accept wrote that path five times into `repro-acceptance.json`. Accepting on Olin (`/Users/juliezfu`) and at home (`/Users/zhiyufu`) would churn the file.
- **User name.** `accept` wrote `"actor": "zhiyufu"`. A probe of `echo $HOME` committed `/Users/zhiyufu` to `repro-builds.json`.
- **Merge.** Accepting `clean` on branch A and `estimate` on branch B, then merging, gave `CONFLICT (content): Merge conflict in repro-acceptance.json`; `pytask.lock` and `repro-builds.json` merged cleanly. While conflicted, `status`, `build`, and `accept` all exit with an error because `read_ledger` raises for the whole file.
- **Size and duplication.** A record is ~3.5 KB per step against ~560 B per step in the lock. `baseline.lock` copies the lock entry, `baseline.run` the run record, and `baseline.spec` the receipt; `state.outputs` equals `state.products` without a sidecar; `boundary_inputs` is stored twice. Accepting a task also writes records for steps already fresh.
- **Dropbox sync (*inferred*).** `.superra-repro/` is only gitignored, so in a Dropbox project it syncs anyway. `flock` cannot stop two machines building at once, and a `running` record from another machine reads here as interrupted, so the step reports `failed`.

### Workflow follow-up

Merge guidance for these root records in parallel dispatch and Sync belongs to [08-workflow-wiring](../08-workflow-wiring/task.md), written against the formats this task settles.
