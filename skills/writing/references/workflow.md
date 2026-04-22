# Writing Workflow — Four usage modes + two hard rules

> Load on every writing task. Specifies the four modes the writing skill supports — **direct-edit, pure-review, review-edit-loop, full-workflow** — and the two non-negotiable rules that apply across all of them. Severity markers: `[BLOCKING]` must fix to earn APPROVE; `[ADVISORY]` flaggable as MINOR.

The writing skill is **standalone-usable** (per user decision 2026-04-19, recorded in `PLAN.md` §Decisions). Most writing work does NOT go through the full superRA `planning-workflow` → `implementation-workflow` → `integration-workflow` scaffold — that full workflow exists for major changes (whole-section drafts, whole-paper revisions). This reference documents the lightweight modes for everything else.

## Two Hard Rules

These apply to every mode. They are load-bearing — violating either breaks the implementer–reviewer pair principle (`superRA:using-superRA` §Universal Principles #1) or the parallelism guarantee.

### Rule 1 — Reviewer dispatch is never skipped

**In every mode — including direct edit — the reviewer is a separately-dispatched agent.** Self-review by the orchestrator is not a substitute. Independent review is load-bearing; the adversarial posture depends on role separation.

Direct corollary: **the orchestrator MAY step into the implementer role** (edit directly while in live conversation with the researcher). But the reviewer role is always a fresh dispatched agent.

Why: one full-session agent cannot reliably adversarially review its own work — the motivated-reasoning failure mode is too well-documented. A fresh agent with no context about how the edit was produced catches issues the author misses.

### Rule 2 — Parallel-dispatch multiple reviewers for multi-dimensional consistency work

When the task spans more than one consistency dimension (e.g., "check citations and cross-references and terminology"), **dispatch one reviewer per `consistency/*.md` file in parallel** — a single message with multiple Agent-tool calls.

Why:

- **Speed.** Parallel dispatch completes in about the time of the slowest reviewer, not the sum.
- **Focus.** Each reviewer loaded with one dimension produces deeper findings than one generalist reviewer loaded with all eight.
- **Clean findings.** Orchestrator adjudicates one dimension at a time rather than untangling a mixed report.

Each reviewer is dispatched with `Stage: implementation` (reviewer role) and `Additionally:` naming the specific `consistency/*.md` file to load. The canonical dispatch envelope is in `superRA:agent-orchestration` §Dispatch Templates.

---

## Four Usage Modes

### (a) Direct edit

**When.** Tiny polish or single-sentence edit, explicitly scoped, with the researcher in live conversation. The classic case: "fix this typo"; "tighten this sentence".

**Flow.**

1. Orchestrator reads the request and the target file.
2. Orchestrator performs the edit directly (in-session implementer).
3. Orchestrator **dispatches an independent reviewer** (Stage: `implementation`, reviewer role) loaded with `writing/SKILL.md` + the relevant reference(s) — typically `style-checklist.md` and `refactor-and-compile.md` for a polish.
4. Reviewer returns APPROVE / REVISE. REVISE → fix → re-dispatch reviewer (narrow re-review). APPROVE → done.
5. Commit + one-line chat confirmation.

**No `PLAN.md` / `RESULTS.md`.** Record lives in the commit message and the chat transcript. Any user decisions at escalation points go into the commit message (per `writing/references/collaboration.md` §Escalation patterns).

**When NOT to use:** anything structural, anything touching claims or arguments, anything requiring the researcher to confirm scope — those need at least mode (c) or (d).

### (b) Pure review

**When.** The researcher wants findings, not edits. "Check my citations"; "do a consistency sweep on the whole paper"; "review the introduction for clarity". The output is a findings report; the researcher decides what to act on.

**Flow — single dimension.**

1. Orchestrator dispatches one reviewer agent (Stage: `implementation`, reviewer role) loaded with the one `consistency/*.md` file (or `style-checklist.md` / `structure-checklist.md`).
2. Reviewer returns findings (the consistency file's §Output format applies — file + line + severity + recommendation, one item per finding).
3. Orchestrator relays findings to the researcher.

**Flow — multi-dimensional (Rule 2 applies).**

1. Orchestrator identifies which `consistency/*.md` dimensions apply.
2. Orchestrator dispatches N reviewers **in parallel** (single message with N Agent-tool calls), one reviewer per dimension. Each reviewer loaded with only its one file.
3. Each reviewer returns its findings.
4. Orchestrator consolidates findings by severity, groups duplicates where two reviewers flagged overlapping issues, relays to researcher.

**No edits in this mode.** If the researcher reviews the findings and wants fixes applied, that transitions the task to mode (c) or (a) with explicit scope.

**No `PLAN.md` / `RESULTS.md`** for single-dimension review; **optional** for multi-dimensional sweeps (use if the findings need to survive to a later session).

### (c) Review → edit → re-review loop

**When.** Iterative work on a section. "Proofread §3 carefully"; "clean up the results section". Typically multiple passes until the researcher or the reviewer signs off.

**Flow.**

1. **Round 1 — Review.** Orchestrator dispatches reviewer(s) per the task scope (one or more, parallel if multi-dimensional). Reviewer returns findings.
2. **Round 1 — Adjudicate.** Orchestrator (with the researcher if in conversation) decides which findings to act on. Low-value findings may be dismissed with reasoning.
3. **Round 1 — Edit.** Orchestrator edits directly (often — the live conversation is the point), or dispatches an implementer for larger batches. Apply only the accepted findings; stay within scope.
4. **Round 1 — Re-review.** Fresh reviewer dispatch, narrow re-review (verify cited fixes + any dependent findings per `writing/SKILL.md` §Three Concurrent Disciplines reviewer protocol).
5. **Iterate or terminate.** APPROVE → done. REVISE with new `[BLOCKING]` findings → loop.

**`PLAN.md` optional; `RESULTS.md` not used** (per the decision matrix in `writing/references/planning.md`). Typical: no `PLAN.md` for a single-section proofread; one lightweight `PLAN.md` for a multi-section iterative pass.

**Termination.** The loop terminates when the reviewer returns APPROVE. It may also terminate by researcher decision — "this is good enough, ship it" — in which case log the decision (commit message if no `PLAN.md`; User Decisions Log if `PLAN.md`).

**Cap at 3 rounds.** If the reviewer returns REVISE with **new** `[BLOCKING]` findings on each of three consecutive rounds (not the same unresolved item re-raised), escalate to the researcher per `superRA:agent-orchestration` §Reviewer-feedback handling. Persistent new findings usually mean the scope was under-specified or the reviewer and implementer are pulling in different directions — an orchestrator / researcher call, not another lap.

### (d) Full workflow

**When.** Major changes — whole-section drafting from scratch, whole-paper revision for R&R, pre-submission sweep of an entire paper with substantive edits, structural revision of the argument.

**Flow.** Plug into the standard superRA workflow pipeline:

1. **`superRA:planning-workflow`** — scope check (per `writing/references/planning.md` §Hard Gate), task decomposition, `PLAN.md` + `RESULTS.md` bootstrapped.
2. **`superRA:implementation-workflow`** — per-task implementer + reviewer dispatch. Each task is atomic (one section or one dimension per task).
3. **`superRA:integration-workflow`** — pre-merge gates per `writing/references/integration.md` (build clean, consistency dimensions passed, voice preserved, scope respected) and Phase D final merge / PR handling via `superRA:semantic-merge` when needed. No drift tests for pure writing tasks; the writing substitute gate is **document build + outline-stability check**. If the writing task produced numbers, data-analysis drift tests apply in addition.

**`PLAN.md` required; `RESULTS.md` required.** Full handoff-doc discipline applies (`superRA:handoff-doc`).

### Mode-transition rules

Modes transition naturally as scope clarifies:

- **(a) → (c):** "I said typo, but actually can you also check the next paragraph? And the one after? …" — at some point, escalate to (c) with a lightweight scope.
- **(b) → (c):** "I looked at the findings; apply these four." — transitions to (c) with those four as the explicit scope.
- **(c) → (d):** "Actually, this needs to become a full rewrite" — transitions to (d). Bootstrap `PLAN.md` from the work already done.
- **(d) → (c):** A task inside a full-workflow plan can internally run as a (c) loop.

Transitions are normal. What is NOT normal: silently running a (d) shape under a (a) mode — if the scope grows, upgrade the mode explicitly.

---

## Dispatch quick-reference

For orchestrator convenience — the Agent-tool dispatch envelopes for each mode, condensed. Full canonical templates in `superRA:agent-orchestration` §Dispatch Templates.

**Mode (a) reviewer dispatch (direct-edit follow-up):**

```
subagent_type: reviewer
Stage: implementation
Task: Review the single edit in <file>:<line-range>. Verify scope, voice,
      compile, cross-refs.
Additionally: Load writing/SKILL.md + references/style-checklist.md +
      references/refactor-and-compile.md. No PLAN.md — record in commit and chat.
```

**Mode (b) single-dimension review dispatch:**

```
subagent_type: reviewer
Stage: implementation
Task: Review <file> for <dimension> consistency. Report findings only;
      do not edit.
Additionally: Load writing/SKILL.md + references/consistency/<dimension>.md.
```

**Mode (b) multi-dimensional parallel dispatch:** One message, N reviewer dispatches in parallel, one per `consistency/*.md` the scope names.

**Mode (c) iterative loop:** Mode (b) + mode (a) interleaved. Each round is one reviewer dispatch + one edit batch + one narrow re-review dispatch.

**Mode (d) full workflow:** Standard `planning-workflow` → `implementation-workflow` → `integration-workflow` dispatches per their respective choreographies.

---

## Gated Checklist

- `[BLOCKING]` **Mode selected explicitly.** One of (a) / (b) / (c) / (d).
- `[BLOCKING]` **Rule 1 honored.** Reviewer dispatch scheduled — no mode skips it.
- `[BLOCKING]` **Rule 2 honored for multi-dimensional work.** Parallel dispatch, one reviewer per `consistency/*.md` file.
- `[BLOCKING]` **PLAN.md / RESULTS.md decision matches the mode** (per `writing/references/planning.md` decision matrix).
- `[BLOCKING]` **Scope handed to each reviewer is one dimension** (for consistency-dimension reviewers) or one focused checklist (for style / structure).
- `[BLOCKING]` **Termination condition named.** "Until reviewer APPROVE", "until researcher OK", "until compile passes + all consistency reviewers APPROVE".
- `[ADVISORY]` **Mode transition planned** if the scope may grow (e.g., "start as (b), upgrade to (c) if researcher asks for edits").

## Reviewer verdict protocol

Walk top to bottom, never halt, return APPROVE / REVISE.
