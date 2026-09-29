---
title: "Reproduction Instructions Pass the CLAUDE.md Gate"
status: not-started
depends_on:
  - 01-engine-freshness
  - 02-portable-records
  - 03-readiness-model
  - 05-explain-impact
---

## Objective

An agent reading the reproduction instructions finds each rule once, in its owning file, worded so it can act on it. This is what [CLAUDE.md](../../../../CLAUDE.md) requires of every line under `skills/*`: §Teach the Protocol's three tests (DRY, same-file restatement, necessity) and §Skill Prose Style. The [audit](../attachments/gate-audit.md) found both failure directions: about 30% of the text repeats itself, one fact ten times, while key terms go undefined or carry two meanings.

Scope:

- [skills/reproducibility/](../../../../skills/reproducibility/SKILL.md): `SKILL.md` and its five references.
- [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), from §Effective Dependencies to the end.
- [commands.md](../../../../skills/task-tree/references/commands.md) §Reproduction.

Load `skill-creator` before editing any `SKILL.md`. Write against the mechanics as 01, 02, 03, and 05 leave them.

### `SKILL.md` says what the skill is for and carries no stage gates

- **Purpose first.** `SKILL.md` opens with §The Model and never says why an agent loads the skill. Open with the job: every retained result can be re-run from committed code, and after any change an agent can tell which results are no longer current and whether to rerun, accept, or report them.
- **Each gate moves to the situation that applies it.** §Gates mixes three stages: registering code while producing it, claiming a result reproduces in `## Results` or at the completion check, and resolving a stale step whenever one appears. Each gate moves into the reference loaded in that situation, and §The Loop, which restates the gates, goes with them. `SKILL.md` keeps the purpose, the model, and the table routing each situation to its reference. [08](../08-workflow-wiring/task.md) points the call sites at those references.

### Each fact has one home

- **Repeated facts collapse to one copy** in the owner CLAUDE.md §Ownership Boundaries names: mechanics in the task-tree docs, discipline in the reproducibility skill. Other places point to that copy or drop the fact. The largest clusters ([gate-audit.md](../attachments/gate-audit.md) §1):
  - What a saved input is, and what `--upstream` adds: 10 copies.
  - Acceptance executes nothing, so a never-run check must still run: 7 copies.
  - What makes a step rerun: `diagnosing.md` repeats the contract's mechanics. The contract keeps them; `diagnosing.md` keeps the actions.
  - Identical output stops the rerun cascade: 5 copies.
  - Smaller ones: the accept preview, the significance sentence in `commands.md`, and "registration follows placement".
- **Implementation detail leaves agent-loaded text.** The record fields, size caps, and lock-history mechanics in the contract's record sections move to task-tree `references/internals.md`. Subagents that register a step load the contract's reproduction section, so that section carries only what they act on.
- **Output descriptions and background go:** the 251-word layout of `explain`'s output, `rerun-or-accept.md` §Preview (which describes command output), wrapper lines, and the background in `SKILL.md` §The Model.

### Every term an agent acts on is defined where it is loaded

- **"Boundary" becomes two terms.** `designing-the-graph.md` uses it for an input no step produces; the CLI's `boundary_inputs` uses it for files from producers outside the selection. An agent cannot tell which to list in `## Results`. Define once in `SKILL.md`:
  - *external input*: a file no step produces;
  - *saved input*: a file from a producer outside the selection, used as it sits on disk.
- **Producer chain is defined in `SKILL.md`.** It is used in `designing-the-graph.md` and `rerun-or-accept.md` but defined only in `protect-and-completion.md` and `commands.md`.
- **No named class of important results.** A result's importance is its position in the task DAG, and no list of important results is kept. "Completion targets", "final deliverable tasks", "canonical result", "maintained producer", and "kept result" leave the reproducibility skill:
  - The completion check covers every active step (`repro status .`) instead of a target list chosen at Protect.
  - The stale rule classes a step by graph facts alone. Today a producer outside `attachments/`, with no readers and not on a "maintained path" (a term defined nowhere), matches no row. Make task-local the explicit class and everything else potentially significant.
- **One drift-test rule.** [designing-the-graph.md:9](../../../../skills/reproducibility/references/designing-the-graph.md#L9) makes a check step blocking for every drift test protecting registered outputs; [protect-and-completion.md:8](../../../../skills/reproducibility/references/protect-and-completion.md#L8) registers one only for drift tests the researcher selects.
- **Unparseable lines are rewritten,** such as "stops upstream uncertainty" and "a finding recorded in prose with no output file of its own included" ([gate-audit.md](../attachments/gate-audit.md) §2 item 4).
- **Engine lines match 01.** Lines naming pytask or `pytask.lock` (audit items SK:11, CMD:148, TFC:225, DX:40) are rewritten, not compressed, against superRA's own engine and `repro-lock.json`.

### Subagents are not sent into `commands.md`

The skill links `commands.md` three times: `SKILL.md` for flags, records, and step states; `rerun-or-accept.md` for accept flags; `diagnosing.md` for `explain`'s row format. CLAUDE.md §Agent Load Surface does not allow subagents there, and they need none of it: the step states they act on belong in the stale rule, flags come from `superra repro --help`, and `explain` output reads on its own. Drop the three links; `commands.md` stays the command reference for the main agent and the researcher.

### Validation

- Word counts before and after; the audit estimates about −30% across the three documents.
- Every gate, enum, default, and ordering constraint survives in its new home, checked by listing them before and after.
- One realistic harness session registers a step and applies the stale rule.

Owning tasks: [06-skill](../../06-skill/task.md), [03-skill-redesign](../../12-agent-protocol/03-skill-redesign/task.md), [03-diagnosis-guidance](../../13-staleness-provenance/03-diagnosis-guidance/task.md).

## Details

The audit's ten highest-value edits and every file:line are in [gate-audit.md](../attachments/gate-audit.md) §5.
