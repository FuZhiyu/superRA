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

### Each fact has one home

- **Repeated facts collapse to one copy** in the owner CLAUDE.md §Ownership Boundaries names: mechanics in the task-tree docs, discipline in the reproducibility skill. Other places point to that copy or drop the fact. The largest clusters ([gate-audit.md](../attachments/gate-audit.md) §1):
  - What a saved input is, and what `--upstream` adds: 10 copies.
  - Acceptance executes nothing, so a never-run check must still run: 7 copies.
  - What makes a step rerun: `diagnosing.md` repeats the contract's mechanics. The contract keeps them; `diagnosing.md` keeps the actions.
  - Identical output stops the rerun cascade: 5 copies.
  - Smaller ones: the accept preview, the significance sentence in `commands.md`, "registration follows placement", and Loop steps in `SKILL.md` that restate its Gates.
- **Implementation detail leaves agent-loaded text.** The record fields, size caps, and lock-history mechanics in the contract's record sections move to task-tree `references/internals.md`. Subagents that register a step load the contract's reproduction section, so that section carries only what they act on.
- **Output descriptions and background go:** the 251-word layout of `explain`'s output, `rerun-or-accept.md` §Preview (which describes command output), wrapper lines, and the background in `SKILL.md` §The Model.

### Every term an agent acts on is defined where it is loaded

- **"Boundary" becomes two terms.** `designing-the-graph.md` uses it for an input no step produces; the CLI's `boundary_inputs` uses it for files from producers outside the selection. An agent cannot tell which to list in `## Results`. Define once in `SKILL.md`:
  - *external input*: a file no step produces;
  - *saved input*: a file from a producer outside the selection, used as it sits on disk.
- **Completion targets and producer chain are defined in `SKILL.md`.** Both are used in `designing-the-graph.md` and `rerun-or-accept.md` but defined only in `protect-and-completion.md` and `commands.md`.
- **The stale rule covers every step.** Its classes, task-local and potentially significant, leave a gap: a producer outside `attachments/`, with no readers and not on a "maintained path" (a term defined nowhere), matches no row. Make task-local the explicit class and everything else potentially significant.
- **One drift-test rule, in §Gates.** [designing-the-graph.md:9](../../../../skills/reproducibility/references/designing-the-graph.md#L9) makes a check step blocking for every drift test protecting registered outputs; [protect-and-completion.md:8](../../../../skills/reproducibility/references/protect-and-completion.md#L8) registers one only for drift tests the researcher selects.
- **Unparseable lines are rewritten,** such as "stops upstream uncertainty" and "a finding recorded in prose with no output file of its own included" ([gate-audit.md](../attachments/gate-audit.md) §2 item 4).
- **Engine lines match 01.** Lines naming pytask or `pytask.lock` (audit items SK:11, CMD:148, TFC:225, DX:40) are rewritten, not compressed, against superRA's own engine and `repro-lock.json`.

### Subagents load only what CLAUDE.md allows

- The skill sends subagents into `commands.md`, while CLAUDE.md §Agent Load Surface allows them only the contract's reproduction section (decision below).

### Validation

- Word counts before and after; the audit estimates about −30% across the three documents.
- Every gate, enum, default, and ordering constraint survives, checked by listing them before and after.
- One realistic harness session registers a step and applies the stale rule.

### Researcher decision

- **Subagents and `commands.md`.**
  - (a) Add `commands.md` §Reproduction to CLAUDE.md's subagent exception, and trim it as an agent reference.
  - (b) Point subagents to `superra repro --help` instead.
  - Recommendation: (a). `--help` cannot carry the status meanings agents act on.

Owning tasks: [06-skill](../../06-skill/task.md), [03-skill-redesign](../../12-agent-protocol/03-skill-redesign/task.md), [03-diagnosis-guidance](../../13-staleness-provenance/03-diagnosis-guidance/task.md).

## Details

The audit's ten highest-value edits and every file:line are in [gate-audit.md](../attachments/gate-audit.md) §5.
