# Merge Integration Quality Standards

Shared domain reference for merge proposals and merge review. Both the implementer (merge proposer) and reviewer walk the gated checklist at the bottom; the how-to sections above give the commit-message templates, integration-map format, and Tier 3 escalation procedure the checklist items encode. Loaded whenever `Stage:` is `merge` (per `superRA:using-superRA` §Skill-Load Manifest).

---

## How-To

### Commit structure — one or more commits, separate when intent differs

A merge integration can land as **one commit or many**. The load-bearing discipline is *intent separation*, not commit count: mechanical reconciliation and intent-bearing adaptation are different kinds of work, and when they are both non-trivial they must not be conflated. The two-commit shape below is the canonical example of that separation, not a mandate.

**When one commit is sufficient:** the mechanical merge is trivial (no real conflicts, or a clean fast-forward) **and** the integration adaptation is small enough that the commit message can describe both pieces honestly. A plain `git merge --ff-only` or a near-empty `--no-ff` merge with a few label fixes is the typical shape.

**When to split into multiple commits (the canonical template):** either side is non-trivial — conflicts need human-visible reconciliation, or the intent adaptation rewrites derived artifacts, regenerates outputs, or touches multiple files. Split so a reviewer can see the mechanical reconciliation alone, then the intent adaptation alone.

**Commit 1 (mechanical merge) — when split:**
- Complete the merge with lowest-assumption reconciliation
- Preserve information from both sides
- Restore a buildable, runnable state
- No opportunistic cleanup or reinterpretation
- Message: `"merge [incoming] into [current]: mechanical resolution"`

**Commit 2 (integration) — when split:**
- Adapt code, docs, tests, and generated artifacts so the branch incorporates the incoming objective
- Rewrite stale names, labels, paths, and references
- Regenerate derived outputs from merged source code
- Message: `"integrate [incoming] intent: [brief description]"`

**More than two commits:** legitimate when the intent adaptation decomposes into independent logical changes (e.g., one commit per affected task in a multi-task integration). Sequence them after Commit 1; keep each one's message honest about what it carries.

### Research-Meaningful Escalation (Tier 3)

These conflicts **MUST** be flagged for the researcher. Ask via `AskUserQuestion` (plain text if unavailable) — when the resolution has a closed set of options (`--ours`, `--theirs`, synthesize, regenerate, roll back), pass them as question options; when it's methodology-level, ask in free-form prose. Mark such rows as `ASK USER` in the integration map while still open, and replace with the researcher's resolution once it comes back. Every answer is a user decision and must be logged per `handoff-doc` §User Decisions Log before the resolution is committed — into `PLAN.md`'s `## Decisions` section if the branch still has `PLAN.md`, otherwise into the integration commit message (which becomes the record of record once `PLAN.md` is gone).

- **Variable definitions:** Incoming changes redefine a variable used in this branch's analysis
- **Sample construction:** Incoming changes alter sample filters or data sources
- **Econometric specifications:** Incoming changes alter model specifications, control variables, or clustering
- **Data processing:** Incoming changes alter merge logic, data cleaning, or transformations
- **Results:** Incoming changes affect analysis outputs

**Never:**
- Silently change analysis results
- Choose ours/theirs for research-meaningful conflicts
- Remove data discipline artifacts
- Judge whether a methodology choice is correct

### Handoff-doc coherence through the merge

The incoming branch can carry edits to `PLAN.md` / `RESULTS.md` that substantively restructure the work — adding, removing, or combining tasks; flipping a DAG edge; invalidating a prior `APPROVED` (review or integration) status because the incoming diff changed an upstream task's outputs. These are **not** content conflicts to resolve mechanically. They are plan changes.

**Before the merge proceeds**, escalate any such restructure to `planning-workflow §User Feedback and Changing Plans`: the orchestrator authors the Restructure Proposal, the researcher decides, the plan change is logged per `handoff-doc` §User Decisions Log, and `PLAN.md` is updated atomically. Only after the plan-change protocol completes does the merge continue — Commit 2 (integration) then reflects the post-restructure plan, not the pre-merge plan.

Trigger list — if any of these is present in the incoming diff or in the merged state of `PLAN.md`, escalate before Commit 2:

- **Task add / remove / combine** — the incoming branch introduces, deletes, or fuses task blocks relative to the base.
- **DAG edge flip** — `Depends on:` is changed in a way that re-orders downstream dispatch.
- **APPROVED status invalidation** — any task with `Review status: APPROVED` or `Integration status: APPROVED` has its upstream inputs materially changed by the merge (per the DAG cascade rule in `handoff-doc/references/plan-anatomy.md`). The cascade must be reflected in `PLAN.md` before the integration commit lands.

Routine content conflicts in `PLAN.md` / `RESULTS.md` (reworded prose, updated numbers inside an unchanged task block, new review-notes blockquote text) are resolved mechanically in Commit 1 and adapted in Commit 2 like any other file — no escalation needed.

### Integration map format

For each conflict area, document:
- File and location
- Classification (analysis / data-processing / methodology / infrastructure / docs / generated / config)
- Decision: keep-incoming / keep-current / synthesize / regenerate / ASK USER
- Rationale (why this resolution)

Present user decisions in terms of **intent and consequences**, not raw diffs.

---

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for APPROVE; `[ADVISORY]` items MAY be flagged as MINOR but do not block APPROVE.

**Intent preservation:**

- `[BLOCKING]` **Incoming intent understood.** Correctly identified what the incoming changes were trying to accomplish — read commits and diffs to understand WHY, not just WHAT.
- `[BLOCKING]` **Current branch preserved** where intended.
- `[BLOCKING]` **No silent losses.** No changes from either side silently dropped without justification.
- `[ADVISORY]` **Synthesis coherent.** Where both sides were combined, result is logically consistent.

**Research integrity:**

- `[BLOCKING]` **No silent result changes.** Analysis outputs are either unchanged, or the change was flagged to the user.
- `[BLOCKING]` **Variable definitions consistent** across merged code.
- `[BLOCKING]` **Sample construction preserved.** Sample filters and data sources are correct in the merged result.
- `[BLOCKING]` **User decisions implemented correctly** (Tier 3) — the researcher's decisions on research-meaningful conflicts were implemented as stated.

**Commit structure (templates in §How-To → Commit structure):**

- `[BLOCKING]` **Intent separation.** If both the mechanical reconciliation and the intent adaptation are non-trivial, they land in separate commits (canonical two-commit shape, templates in §How-To). A single commit is acceptable only when one side is trivial (clean fast-forward or near-empty intent edit) and the commit message honestly describes both pieces.
- `[ADVISORY]` **Mechanical-commit discipline (when split):** lowest-assumption reconciliation; preserves information from both sides; restores a buildable, runnable state; no opportunistic cleanup or reinterpretation.
- `[ADVISORY]` **Integration-commit discipline (when split):** adapts code, docs, tests, and generated artifacts so the branch incorporates the incoming objective; rewrites stale names, labels, paths, and references; regenerates derived outputs from merged source code (not hand-edited).

**Research-Meaningful Escalation (full procedure and Never-list in §How-To → Research-Meaningful Escalation (Tier 3)):**

- `[BLOCKING]` Every Tier 3 conflict (variable definitions, sample construction, econometric specifications, data processing, results) flagged to the researcher via `AskUserQuestion`, logged per `handoff-doc` §User Decisions Log, and implemented per the answer.
- `[BLOCKING]` None of the four Tier 3 "Never" items violated (silent result changes, ours/theirs on research-meaningful conflicts, removing data discipline artifacts, judging methodology choices).

**Handoff-doc coherence (full procedure in §How-To → Handoff-doc coherence through the merge):**

- `[BLOCKING]` **Handoff-doc coherence.** `PLAN.md` / `RESULTS.md` in the merged state reflect a single coherent plan. Substantive handoff-doc restructures introduced by the incoming branch — task add/remove/combine, DAG edge flip, or APPROVED (review or integration) status invalidation from a cascade — were escalated to `planning-workflow §User Feedback and Changing Plans` **before** the merge proceeded (orchestrator authors proposal, researcher decides, decision logged per `handoff-doc` §User Decisions Log). Commit 2 (integration) reflects the post-restructure plan. Routine content conflicts (reworded prose, updated numbers, new review-notes text) are resolved inline in Commit 1/2 without escalation.

**Integration map (format in §How-To → Integration map format):**

- `[BLOCKING]` For each conflict area, documented file + location, classification, decision, and rationale. User decisions presented in terms of **intent and consequences**, not raw diffs.

**Verification:**

- `[BLOCKING]` **Drift tests pass** (or failures appropriately escalated to user per `drift-test-quality.md` §Cross-cutting Red Flags).
- `[BLOCKING]` **No stale references:** Old variable names, file paths, function names updated.
- `[BLOCKING]` **Pipeline runs** (if applicable): End-to-end pipeline produces expected outputs.
- `[ADVISORY]` **No outdated labels:** Comments, docstrings, and documentation reflect the merged state.

**Data discipline:**

- `[BLOCKING]` Data discipline artifacts (description steps, row counts, validation checks, documentation cells) preserved through the merge. See loaded `econ-data-analysis` for the full list of artifacts.
