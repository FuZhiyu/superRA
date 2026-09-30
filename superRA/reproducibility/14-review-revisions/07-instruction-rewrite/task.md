---
title: "Reproduction Instructions Pass the CLAUDE.md Gate"
status: revise
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

## Results

The reproduction instructions now state each rule once, in its owning file, and agent-loaded text is 21% shorter. `SKILL.md` opens with the skill's job, defines the terms agents act on, and routes each situation to the reference that carries its gate. A harness session registered a step and applied the stale rule's exception correctly.

### Word counts fall 24% across the three documents

| Document | Before | After | Change |
|---|---:|---:|---:|
| [skills/reproducibility/](../../../../skills/reproducibility/SKILL.md) (`SKILL.md` + 5 references) | 2,795 | 2,349 | −16% |
| [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md#effective-dependencies) §Effective Dependencies → end | 2,376 | 1,710 | −28% |
| [commands.md](../../../../skills/task-tree/references/commands.md#reproduction) §Reproduction | 1,959 | 1,336 | −32% |
| Total | 7,130 | 5,395 | −24% |

- The subagent load surface (skill plus the contract's reproduction sections) falls from 5,171 to 4,059 words (−21%).
- The skill shrank less than the audit's −26% because it gained what the objective adds: the purpose line, three defined terms, the readiness bullet, and the step states the stale rule acts on.
- Record formats, receipts, build guards, lock history, `explain`'s source and history-search mechanics, the Julia `include` forms, and the `pyyaml` resolver note moved to [internals.md §Reproduction records](../../../../skills/task-tree/references/internals.md#reproduction-records) (+62 lines, outside every agent load).

### Each gate lives in the reference loaded when it applies

`SKILL.md` keeps the purpose, §The Model, and the routing table. §Gates and §The Loop are gone.

| Gate, enum, or ordering constraint | New home |
|---|---|
| `[BLOCKING]` retained code and its results are registered | [designing-the-graph.md §What earns a step](../../../../skills/reproducibility/references/designing-the-graph.md#what-earns-a-step) |
| `[ADVISORY]` name files, not their directory | same file, §Declare from the script |
| `[BLOCKING]` a claimed result reads `fresh` in `status <targets>`, `--upstream` when the claim covers the producer chain; then state coverage in `## Results` and commit the records | [protect-and-completion.md §Claiming a result reproduces](../../../../skills/reproducibility/references/protect-and-completion.md#claiming-a-result-reproduces) |
| `[BLOCKING]` a step not `fresh` is resolved by the stale rule | top of [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) |
| Stale-rule classes and its three rows; the cannot-move-a-result exception; "cheap" ≈ a minute | rerun-or-accept.md §The stale rule, unchanged in content |
| Step states `fresh`/`stale`/`missing`/`failed`/`external` | stale rule (what to do per state); commands.md state table (meaning) |
| `kind` `build` (default) / `check`; one step per script (default); environment files outside graph deps (default) | contract §Step keys; designing-the-graph.md; diagnosing.md §Environment changes |
| Inspect before accepting; dry-run and explain before the stale rule; the dependency ladder's order; retire, move, or archive order; `task check` before building | unchanged in their sections |

- The claim gate drops "its scoped build succeeds": a failed build reads `failed`, and an accepted result is fresh without a build, which the old loop already allowed.
- Anchors that call sites use are kept: `#the-stale-rule`, §What earns a step, §Step lifecycle, §The completion gate, §Reproduction choices at Protect.

### Decisions this task made

- **One drift-test rule:** every drift test or validation script is a `kind: check` step, because it is retained code. Protect only selects which drift tests exist.
- **The completion gate covers `.` and runs the stale rule before building:** `status .`, the stale rule with named builds, then `status .` again. It passes when every step is `fresh`, except steps the stale rule left stale and reported to the researcher; without that exception, a task-local companion left stale would block completion forever. [08](../08-workflow-wiring/task.md) still owns the call sites.
- **Protect makes one reproduction decision,** which inputs are external. Completion targets are gone, and so is the `integrate(protect)` commit-body record: the declarations themselves record external inputs.
- **The stale rule classes steps from graph facts alone:** a step is task-local when its producer is under `attachments/` and `status` reports `outside readers: 0`; every other step is potentially significant.

### Terms

- `SKILL.md` §The Model defines **producer chain**, **saved input**, and **external input**.
  - "Boundary" no longer appears in agent-facing text except the `boundary_inputs` JSON key, which commands.md glosses as the saved inputs.
  - "Completion targets", "final deliverable tasks", "canonical result", "maintained producer/path", and "kept result" are gone from the skill.
- The unparseable lines ("…included", "stops upstream uncertainty", "requested fresh execution follows the acceptance protocol", "lockfiles", "published root", "Derive configuration per consumer", "resolver") are rewritten.
- **pytask:** the only remaining mention is commands.md's upgrade sentence and Python 3.11 note, both current; the lock-legacy details are in internals.md.
- **Readiness versus freshness** gets one bullet in §The Model: readiness is `depends_on` only, and the stale rule decides about inputs that are not fresh.

### Subagents are no longer sent into `commands.md`

- The three links are dropped. `SKILL.md` names `superra repro <command> --help` for flags.
- The contract's new §What invalidates a step carries the rerun rules, including those `diagnosing.md` used to restate. Its §Records table carries what the records are: tracked or ignored, and never hand-edited.
- `diagnosing.md` keeps only actions.
- commands.md's inverted link into `diagnosing.md` is removed.

### Harness session

A fresh implementer (Sonnet) got a scratch project: an approved `01-data` whose 75-second producer went stale from a coauthor's comment-only commit, and a `02-table` task to produce and record a table.

- It registered `size-by-industry` and built it.
- It applied the exception: it accepted `build-panel` with the commit in the reason instead of rerunning it, and reported that.
- Its `## Results` names the saved input and which steps executed versus were accepted, and `status --upstream` reads both steps fresh.
- **Routing miss:** it read `SKILL.md`, `rerun-or-accept.md`, and `designing-the-graph.md`, but not `protect-and-completion.md`, even though it was claiming a result; it followed the claim steps anyway. implement-task's pointer to `reproducibility` §Gates, which no longer exists, gave it no route there.

### Left for 08

These call sites still point at removed text or name completion targets:

- [implement-task:50](../../../../skills/implement-task/SKILL.md#L50) and [review-task:28](../../../../skills/review-task/SKILL.md#L28) point to `reproducibility` §Gates.
- [load_contract.json:220](../../../../tests/harness-instruction-following/load_contract.json#L220) cites `SKILL.md#L12-L18`.
- `completion.md:18`, `integrate.md:9`, and `finish.md:39` run `build <targets> --upstream` before status.
- `protect.md:15` still frames the Protect choices around targets.
- `using-superra/SKILL.md` §Task Interface still restates "registration follows placement" (audit C8).

## Review Notes

Tier: thorough. Focuses: the CLAUDE.md §Teach the Protocol gate and §Skill Prose Style on every edited line under `skills/*`; survival of every gate, enum, default, and ordering constraint; whether each reference is actionable in its situation; the researcher's critique. Call sites outside the skill and the task-tree references are 08's scope and were not reviewed.

1. **[BLOCKING] Two edited lines fail the §Teach the Protocol gate.**
   - [rerun-or-accept.md:40](../../../../skills/reproducibility/references/rerun-or-accept.md#L40): "**It executes nothing.**" restates [SKILL.md:13](../../../../skills/reproducibility/SKILL.md#L13) ("executing nothing"), which every reader of this reference has already loaded (test 1). Fix: lead the bullet with its new content, e.g. "**A check that has never run must run.**"
   - [task-file-contract.md:136](../../../../skills/task-tree/references/task-file-contract.md#L136): "The dashboard reveals and selects the step." describes UI behavior that no agent acts on (test 3). Fix: delete the sentence and keep the link form.

2. **[ADVISORY] The claim gate is hard to reach when an agent records a result.** The harness implementer claimed a result without opening `protect-and-completion.md`. The file name leads with Protect and completion, and the [SKILL.md:27](../../../../skills/reproducibility/SKILL.md#L27) row files `Stage: protection` under "Claiming a result reproduces", which does not describe it. Fix: split the row (claims in `## Results` or at the completion check / `Stage: protection`), or name the file for its first situation and coordinate the rename with 08.

3. **[ADVISORY] Drift-test authors are routed through a paraphrase.** The designing-the-graph row ([SKILL.md:26](../../../../skills/reproducibility/SKILL.md#L26)) covers code "that produces a retained result". A drift test checks a result, so its author reaches the check-step rule only through [protect-and-completion.md:29](../../../../skills/reproducibility/references/protect-and-completion.md#L29) sentence 2. That sentence paraphrases [designing-the-graph.md:8](../../../../skills/reproducibility/references/designing-the-graph.md#L8) and keeps the old "the researcher selects" qualifier. Fix: change the row to "Writing or registering retained code", then drop that sentence. In the same line, "received rather than rebuilt, and not reproducible here" paraphrases [SKILL.md:17](../../../../skills/reproducibility/SKILL.md#L17), so "which inputs are external" is enough.

4. **[ADVISORY] The registration gate gained a timing clause.** [designing-the-graph.md:5](../../../../skills/reproducibility/references/designing-the-graph.md#L5) puts "in the commit that changes the result, its inputs, or its ownership" inside the `[BLOCKING]` sentence. Before this change, the gate required registration only and the timing was ungated guidance. Fix: confirm the stricter gate with the researcher, or move the clause into its own sentence.

5. **[ADVISORY] The stale rule gives no exit for the agent's own work.** It now covers `missing` and `failed` ([rerun-or-accept.md:9-18](../../../../skills/reproducibility/references/rerun-or-accept.md#L9-L18)).
   - A step the agent has just registered reads `missing`. If it is task-local, it matches "Leave it stale".
   - A task-local `failed` step is "fixed first" and then left stale.
   - Fix: say the rule covers steps the agent is not producing, and that a fixed failure is rerun.

6. **[ADVISORY] Borderline necessity and restatement.**
   - [task-file-contract.md:239](../../../../skills/task-tree/references/task-file-contract.md#L239): "so both read the same on every machine and branch" leads to no action.
   - [task-file-contract.md:193](../../../../skills/task-tree/references/task-file-contract.md#L193) repeats the `params` row at L154 ("changing a value reruns the step"), which fails test 2. Fix: trim L154's clause.
   - [SKILL.md:22](../../../../skills/reproducibility/SKILL.md#L22): "Each reference carries the gates for its situation." describes the references and gives no instruction.

7. **[ADVISORY] Wording.**
   - [SKILL.md:8](../../../../skills/reproducibility/SKILL.md#L8): "Every retained result re-runs from committed code" reads as if results rerun on their own. The objective's "can be re-run" states the job.
   - [SKILL.md:3](../../../../skills/reproducibility/SKILL.md#L3): the description still triggers on "selecting protection checks". The skill's Protect role is now the external-input decision.
   - [designing-the-graph.md:40](../../../../skills/reproducibility/references/designing-the-graph.md#L40): "rehearsal build" is not defined anywhere, and the trailing rationale clause can be cut.

8. **[ADVISORY] The researcher's agreement on external inputs is no longer recorded anywhere.** The `integrate(protect)` record line is gone. The body list at [protect.md:30](../../../../skills/superintegrate/references/protect.md#L30) names no external inputs, and a dep with no producer does not show that the researcher agreed to it. For 08: add external inputs to that body list.

9. **[ADVISORY] A stale term remains outside this task's scope.** The reproducibility row in [CLAUDE.md](../../../../CLAUDE.md) §Ownership Boundaries still says "boundary inputs". For 08 or 09.

10. **[ADVISORY] No harness evidence was retained.** `## Results` describes the session but links no transcript or scratch project, so the routing miss in item 2 cannot be rechecked.
