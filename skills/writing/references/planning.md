# Writing Planning — Scope inventory + task-size triage + PLAN/RESULTS optionality

> Load at the **PLAN phase** (or at the start of any writing task) when the work touches writing. This reference is what a fresh orchestrator reads first to decide: *what is the task, what shape of workflow does it need, does it need `PLAN.md` / `RESULTS.md` at all?* Severity markers: `[BLOCKING]` must fix to earn APPROVE; `[ADVISORY]` flaggable as MINOR.

This reference is the planning-time analogue of `econ-data-analysis/references/planning.md`. Writing work is more elastic than data work: a typo fix needs no plan; a whole-paper revision needs the full `PLAN.md` + `RESULTS.md` scaffold. The decision matrix below teaches the orchestrator to match workflow shape to task size.

Reviewer dispatch is **never skipped** (main SKILL.md §Mode selection hard rule #1). That applies across every row of the decision matrix — the orchestrator may skip `PLAN.md` for small tasks, never the reviewer.

## Scope Inventory

Before drafting tasks (or deciding no tasks are needed), assemble a short scope inventory. Ask — once, concisely — enough to characterize the work:

1. **What document?** Paper / manuscript / section / paragraph. File format (LaTeX / Quarto / Markdown / plain text).
2. **Which section(s)?** Whole document, named sections, or named paragraphs / sentences.
3. **What kind of work?** Edit types — polish, proofread, consistency-check, refactor wording, structural rewrite, draft new section.
4. **Voice / audience.** Who reads this? (Submission target journal / seminar audience / coauthor / grant reviewer / general academic.)
5. **Deadline.** Is there time pressure? Submission in 24 hours is a different workflow than a draft being revised over two weeks.
6. **Known concerns.** Anything the researcher already knows is a problem that this task should address.
7. **Known in-progress work.** Is the researcher actively editing the same files? What sections should be left alone?

The inventory is **lightweight** for most writing work. A one-sentence "polish §3.2 for clarity; no deadline; leave §3.3 alone, I'm rewriting it" is a complete scope inventory. Do not over-ask.

## Task-Size Triage

Classify the task into one of six shapes. Each shape maps to a workflow mode in `writing/references/workflow.md`.

| Shape | Example | Rough effort |
|---|---|---|
| **Typo / sentence polish** | "Fix the typo in line 42 of intro.tex"; "Tighten the first paragraph of §2." | Seconds to minutes |
| **Single-aspect review** | "Check my citations for orphans"; "Verify every number in §4 matches Table 3." | Minutes |
| **Multi-aspect consistency sweep** | "Do a pre-submission consistency sweep on the whole paper." | Tens of minutes |
| **Iterative section proofread** | "Proofread §3 carefully — check style, citations, and cross-references." | Tens of minutes |
| **Section draft / major revision** | "Draft the methods section from the methodology notes"; "Revise §4 for the R&R." | Hours |
| **Whole-paper review / drafting** | "Do a full pre-submission polish"; "Draft the paper from the outline." | Hours to days |

## PLAN.md / RESULTS.md Decision Matrix

Two orthogonal decisions: does this task need a `PLAN.md`? Does it need a `RESULTS.md`?

| Task shape | `PLAN.md`? | `RESULTS.md`? | Mode (see `workflow.md`) |
|---|---|---|---|
| Typo / one-sentence polish | No | No | (a) Direct-edit |
| Single-aspect review | No | No | (b) Pure-review |
| Multi-aspect consistency sweep | Optional | Optional | (b) Pure-review + parallel reviewers |
| Iterative section proofread | Optional | No | (c) Review → edit → re-review loop |
| Drafting a new section / major revision | **Yes** | **Yes** | (d) Full workflow |
| Whole-paper review / pre-submission sweep | **Yes** | **Yes** | (d) Full workflow |

**Optional rows.** "Optional" means: use `PLAN.md` / `RESULTS.md` if the task will span multiple dispatches, if the findings need to survive session compaction, or if the researcher explicitly asks for a written record. Skip otherwise — the commit messages + chat transcript suffice.

**Required rows (Yes).** Section drafting and whole-paper work always get `PLAN.md` + `RESULTS.md`. These are multi-task, multi-session workflows; the handoff doc is load-bearing.

### Rationale

- **Handoff-doc discipline is non-negotiable for multi-session work** (`superRA:using-superRA` §Universal Principles #2). Drafting a section is multi-session; losing continuity costs days.
- **Handoff-doc discipline is bureaucratic overhead for trivial work.** A typo fix doesn't need a plan; the diff + commit message is the record.
- **The middle cases are judgment calls.** Err on the side of `PLAN.md` if (a) the findings need to survive to a later dispatch, (b) the researcher will want to see a written summary, (c) the work is longer than one session can reasonably contain.

### What "record" means when there is no PLAN.md / RESULTS.md

The record still exists — it's just distributed:

- **Commit message** — one-liner on what was edited.
- **Chat transcript** — what the researcher asked, what the agent did, what the reviewer found.
- **Escalation decisions** — per `handoff-doc` §User Decisions Log, log in the commit message even without a `PLAN.md` (e.g., "user confirmed: reword §3.2 'attenuates' → 'weakens'; no scope change").

The handoff-doc principle (findings land in a committed artifact before they appear in chat) still applies — the commit *is* the artifact in this case.

## What a writing `PLAN.md` looks like

When `PLAN.md` is warranted, follow `superRA:handoff-doc` `references/plan-anatomy.md` for the overall shape. Writing-specific header sections:

- **Document target.** Path + format.
- **Scope.** Which sections are in / out.
- **Mode.** Workflow mode (typically (d) full workflow; occasionally (c) review-edit loop graduated to formal plan).
- **Consistency dimensions targeted.** Which `consistency/*.md` files apply (can be all, for a pre-submission sweep; can be one, for a focused check).
- **Compile target.** Which build command validates the work.

Tasks are typically structured as:

1. One task per major section being drafted / revised.
2. One task per consistency dimension for a full sweep (dispatched in parallel per `workflow.md` §Mode (b)).
3. A final integration task for pre-submission work — full build + outline-stability check (per `writing/references/integration.md`).

## What a writing `RESULTS.md` looks like

Mirrors `PLAN.md` task structure. For each task:

- **Status.** IMPLEMENTED / APPROVED / REVISE.
- **Key findings.** What changed; what was flagged; what remains.
- **Build status.** Pass / fail; warnings enumerated.
- **Consistency findings.** For consistency tasks, a list of findings with file + line + severity.

See `superRA:handoff-doc` `references/results-anatomy.md` for the overall shape.

## Hard Gate (when the full workflow applies)

When the task routes to mode (d) full-workflow (i.e., `PLAN.md` is required), there is one hard gate before task drafting:

<HARD-GATE>
Confirm the scope with the researcher before drafting tasks. Specifically: document target, which sections are in scope, which are out of scope (especially any sections the researcher is currently editing), deadline, target audience if non-obvious. This is a one-exchange conversation — do not draft a plan for a section the researcher hasn't agreed is in scope.
</HARD-GATE>

This is the writing-vertical analogue of the `econ-data-analysis` Data Inventory hard gate. It is lighter-weight because writing scope is generally simpler than data inventory, but the principle is the same: the plan cannot be written without the researcher's scope confirmation. Skipping the gate means writing a plan that will be revised after the researcher objects — throwing away the draft.

For smaller tasks (modes a, b, c), the gate does not apply; those tasks run against an explicit one-sentence scope from the researcher.

## Gated Checklist

- `[BLOCKING]` **Task-size triage performed** — one of the six shapes chosen, with rationale.
- `[BLOCKING]` **PLAN.md / RESULTS.md decision made** per the matrix; rationale recorded for optional-row choices.
- `[BLOCKING]` **Scope inventory captured** (1–2 sentences is enough for small tasks; full header for full-workflow tasks).
- `[BLOCKING]` **Sections the researcher is actively editing identified and marked out-of-scope** unless the request names them.
- `[BLOCKING]` **If mode (d) full-workflow:** scope-confirmation hard gate passed before task drafting.
- `[BLOCKING]` **Workflow mode chosen** — one of the four in `workflow.md`.
- `[BLOCKING]` **Reviewer dispatch plan** — even for direct-edit mode, the downstream reviewer dispatch is named in the plan.
- `[ADVISORY]` **Consistency dimensions targeted** listed explicitly (which `consistency/*.md` files apply).
- `[ADVISORY]` **Compile target** stated (which build command validates the work).

## Reviewer verdict protocol

Walk top to bottom, never halt, return APPROVE / REVISE. `planning-review` stage; loaded via `superRA:using-superRA` §Skill-Load Manifest.
