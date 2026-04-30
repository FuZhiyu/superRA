# Integration Discipline for Theory Modeling — the Rewriting Reference

> Loaded at `Stage: integration` for theory-modeling tasks. The reference for
> rewriting an existing derivation into reader-ready form: ex-post structural
> rewriting (objective-first / onion-style), notation reuse against canonical
> `PLAN.md` and prior task ledgers, prior-result reuse, prose integration with
> surrounding sections, and reader-perspective discipline. Use when a task is
> structurally messy, when a per-task integration pass is dispatched against a
> single just-APPROVED task, or whenever an implementer or reviewer needs the
> rewriting playbook. The implementer walks it as pre-handoff self-check; the
> reviewer walks it as verification. Same content, two perspectives — no drift
> possible. `[BLOCKING]` items must be fixed to earn APPROVE; `[ADVISORY]`
> items the reviewer MAY flag as MINOR and do not block APPROVE. Verdicts
> follow `theory-modeling/SKILL.md` §The Four Gates: `APPROVE` / `REVISE`.

**Scope.** This stage owns document-internal coherence and ex-post rewriting.
It cannot introduce new math, new assumptions, or new verification claims;
if a structural rewrite surfaces a correctness fix, halt and re-dispatch as
`Stage: implementation`. The shape mirrors `Stage: sync` — broader
codebase-coherence work is out of scope for that skill in the same way new
math is out of scope here (see `semantic-merge/SKILL.md` §"out of scope").

Generic cross-cutting code-integration concerns (naming consistency, utility
reuse, PR-friendly diffs, documentation currency) live in
`refactor-and-integrate/SKILL.md`. Load both skills at this stage — this one
owns the theory-modeling-specific rewriting / coherence gates; the generic
file owns the cross-cutting code-quality gates.

Each of Sections A, B, C below follows **principle → identification protocol →
checklist**. The principle says what good rewriting looks like; the
identification protocol teaches the agent how to read existing material line
by line and detect violations; the checklist locks in the `[BLOCKING]` /
`[ADVISORY]` calls. A pure checklist is not enough — agents pass items
mechanically while missing the issue the gate was designed to catch. Section D
preserves the refactor-survival discipline that applies whenever modeling work
is reorganized.

---

## Section A — Objective-first structural rewriting

### Principle

A derivation is read forward but built backward. **Start from the object the
proof needs, then expand only the terms required to evaluate it.** Forward
writing runs along a backward dependency walk: name the target; identify what
the target requires; recurse only into terms that are not already known.

This makes the proof linear in the reader's experience: target named,
needed pieces named, structural cancellations performed, canonical objects
substituted, conclusion reached. Local placeholders introduced before the
target is named force the reader to hold a symbol with no purpose; they are
the dominant structural failure mode.

The discipline is **recursive**. A multi-step proof signposts its top-level
strategy in one sentence; each non-trivial sub-argument signposts its own
local strategy in the same form; transition prose at major joins names where
we are in the parent plan ("having established $Y$, we turn to $Z$"). A reader
entering at any point should be able to recover the local goal from the
surrounding signposts.

A worked bad/good walkthrough plus identification-training drills lives in
`references/objective-first.md`; load it on demand for the canonical example
and to practice the diagnostic move before applying the checklist.

**Differentiation from creation-time discipline.** Gate 3 in
`theory-modeling/SKILL.md` enforces stating the top-level proof goal at
creation time as an audit floor. Section A is the ex-post detection-and-rewrite
layer: even when the goal was stated, the linear narrative may still bury the
target under local detours, sub-arguments may still be missing their own
signposts, and the recursive level-by-level discipline still has to be
applied during rewrite.

### Identification protocol

Walk the existing derivation top-to-bottom in the reader's order:

1. **Read the prose preceding the first displayed equation.** Does it name the
   object the proof targets? If the first display is an assertion of an
   intermediate symbol (e.g., "$z_j := \ldots$") with no prior reference to
   the target, the structure is local-detour-first → flag.
2. **For each displayed equation, ask: which named target does this advance?**
   If the answer is "we will see in three pages why this matters," the
   structure has deferred the goal → flag.
3. **At every block longer than ~5–10 lines of algebra, ask: does the prose
   open with a one-sentence local strategy?** Sub-arguments without their own
   opening signpost force the reader to infer scope from algebra alone → flag.
4. **At every section/sub-section join, ask: does the prose name the
   transition?** ("Having $X$, we turn to $Y$.") Bare juxtaposition of blocks
   without transition prose → flag.
5. **For each placeholder symbol introduced (an object that does not appear
   in `PLAN.md` Notation Conventions and is not a canonical model object),
   ask: is the placeholder still doing structural work after rewrite, or did
   the objective-first rewrite remove its reason to exist?** Placeholders
   that survive the rewrite but no longer carry independent meaning → flag.

Pattern-watch list (read each occurrence with the question "is the target
named yet?"):

- The first displayed equation introduces a new symbol with `:=` while the
  target object has not yet appeared in prose.
- A multi-line algebraic block opens directly with manipulation, no preceding
  one-sentence strategy.
- The phrase "we will use this below" or "this will be useful later" — the
  ordering is backward; the term should appear when its use is named.
- A sub-section opens with algebra rather than prose.

### Checklist

- `[BLOCKING]` **Target named in prose before the first displayed equation.**
  The target is the object the proof is computing or signing. Derivations
  whose first move is algebra without a named target are REVISE.
- `[BLOCKING]` **Backward dependency walk recorded.** A 3–7 line walk from
  the target down to primitives or already-known objects appears in prose
  before the algebra ("we need $T$ → which requires $A$ → which requires
  $B$, which is the canonical column from §X"). The walk is what makes the
  forward writing linear; without it the reader is asked to verify each step
  in isolation.
- `[BLOCKING]` **Recursive sub-argument signposts.** Every non-trivial
  sub-argument opens with its own one-sentence strategy in the same form.
  Major transitions carry prose naming the local position. Test: cover all
  algebra and read only the prose; can a reader recover the proof's
  scaffolding from prose alone? Walls of algebra without strategy prose are
  REVISE.
- `[BLOCKING]` **Placeholder symbols introduced for detours are removed
  when the rewrite makes them unnecessary.** A placeholder that survives
  rewrite must justify its place against `Stage: implementation` Gate 1
  (the per-symbol ledger entry); otherwise it is an artifact of the old
  ordering and is REVISE.
- `[ADVISORY]` **Onion-style layering.** When the result has a clean
  baseline plus complications, present the simplest case first, then add
  complications in layers. The reader sees a sequence of self-contained
  results that get progressively richer rather than one monolithic chain.

---

## Section B — Per-step local obviousness

### Principle

Every displayed equation should be **obvious** from a roughly half-page
reading window above it. "Derivable in principle" is too weak — a reader who
has to reconstruct missing definitions, recall a 10-page-back assumption, or
unpack three substitutions collapsed into "therefore" loses the thread. The
author's job is to make each transition obvious within the local window.

When a step is not obvious, exactly one of four fixes applies:

1. **Define inline.** If a symbol is not defined in the local window, give
   its definition at first use in this region (one phrase or one displayed
   line — not a full ledger entry; the canonical entry stays in
   `RESULTS.md`).
2. **Restate the assumption.** If a step depends on an assumption stated
   far above (preferences, sign restrictions, distributional shape, timing),
   restate it in scope at the point of use: "Under the bounded-risk-aversion
   assumption (§2), …".
3. **Cite-with-form-recall.** If a step depends on a prior result that is
   too far back to assume the reader holds it, cite the result by name or
   equation number **and** restate its operative form inline in one line:
   "By Lemma 3.1, $f(x,\theta) = g(x) + \theta h(x)$, so …". A bare
   "(see §3.2)" is insufficient when the step depends on the specific form.
4. **Split the step.** If multiple substitutions, cancellations, or
   sign manipulations are collapsed into a single move, split so each
   transition is one obvious move with one named rule.

### Identification protocol

The core diagnostic is the **half-page mask test**. For each displayed
equation in the derivation:

1. Cover everything in the document except the half page (~25–40 lines)
   immediately above the equation.
2. Read only that window. Ask: is the equation obvious — not merely
   derivable with effort, but **obvious** — from what is visible?
3. If not, identify which of the four failure types is present:
   - **Undefined symbol.** A symbol used in the equation has no definition
     in the visible window and is not canonical (does not appear in
     `PLAN.md` Notation Conventions or any prior task's promoted ledger).
   - **Unrestated assumption.** The step's validity depends on an
     assumption (sign, regularity, interior solution, distributional shape)
     not visible in the window.
   - **Uncited or content-less prior result.** A previously established
     equation, lemma, or proposition is used, but either no citation is
     present or the citation is bare ("(see §3.2)") and the step depends on
     the specific form rather than just the existence of the result.
   - **Over-compressed step.** The transition combines multiple operations
     (substitution + cancellation + sign change + invocation of a rule)
     under one "therefore."
4. Apply the matching fix.

Pattern-watch list (each is an instance of one of the four failure types):

- "$X = \ldots$" asserted with no preceding definition or named rule.
- "By symmetry" / "by inspection" with no operative-form recall.
- "(see §3.2)" / "(see Lemma X)" / "(see Appendix B)" without restating the
  result's operative form when the step depends on the form.
- "Therefore" / "thus" / "it follows that" connecting a long chain in one
  step.
- A symbol last defined more than half a page back is reused without a
  one-phrase recall ("$\mathbf{c}_k$, the column-$k$ dividend loading…").

### Checklist

- `[BLOCKING]` **Every displayed equation is obvious from the local window.**
  Each symbol in the equation is defined in scope or canonically pointed to
  with its meaning recalled; each rule used is named; each prior-result
  dependency is cited with operative form visible. "Derivable with effort"
  is not enough.
- `[BLOCKING]` **Citations to results outside the local window include
  content recall when the step depends on the form.** A bare "(see §3.2)"
  is REVISE when the next move uses the specific form of §3.2's result, not
  just its existence.
- `[BLOCKING]` **Symbol freshness.** Symbols last seen more than half a
  page back are recalled in one inline phrase at re-use ("$\mathbf{c}_k$,
  the column-$k$ dividend loading defined at §2.1") rather than reused as
  if just introduced.
- `[BLOCKING]` **Step granularity.** Over-compressed steps are split so
  each transition is one obvious move with one named rule. Multiple
  substitutions, cancellations, and sign changes collapsed under "therefore"
  are REVISE.
- `[ADVISORY]` **Prefer compact inline restatement over forcing the reader
  to navigate.** When the choice is between a short inline recall and an
  uncited cross-reference, the inline recall serves the reader better even
  when the cross-reference is technically sufficient.

---

## Section C — Cross-document coherence

### Principle

A derivation correct in isolation is wrong in a paper if its symbols clash
with canonical Notation Conventions, if it re-derives an equation already
established earlier, or if its prose breaks the style of surrounding
sections. Local correctness is necessary but not sufficient — a task at
integration stage owes the document a result that fits the document.

Three coherence layers, each with its own authority:

- **Notation.** `PLAN.md` Notation Conventions is canonical. Prior-task
  RESULTS.md ledgers carry symbols that are not yet promoted but were
  introduced upstream and should be reused. Local symbols duplicating
  either of these hide the connection and force the reader to relearn the
  same object under a new name.
- **Prior results.** Equations and named statements (lemmas, propositions,
  corollaries) established earlier in the document or in a prior task are
  cited and reused. Re-deriving an equivalent result in a new section
  silently forks the document.
- **Prose integration.** Terminology, assumption phrasing, formality
  level, and notation usage match the surrounding sections. A new section
  written in a different register (e.g., chat-style commentary, leaked
  workflow vocabulary) breaks the document at the join.

### Required reads

Load these alongside the checklist below — they are the authoritative source
for reader-perspective discipline this section's `[BLOCKING]` items enforce:

- `references/audience-discipline-modeling.md` — proof-narrative prose.
- `references/audience-discipline-writing.md` — paper-body prose generally.

### Identification protocol

Walk the new task's content against three references in order:

1. **Notation pre-flight against `PLAN.md` Notation Conventions and prior
   task ledgers.** Open `PLAN.md`'s Notation Conventions table. Open every
   prior task's `RESULTS.md` Notation & Assumptions Ledger. For each
   symbol used in the current task, classify it:
   - **Canonical** — already in `PLAN.md` Notation Conventions; reuse.
   - **Prior-task-promoted** — in a prior task's ledger, naming the same
     object; reuse and cite the prior task's ledger entry.
   - **Genuinely new** — names an object no prior surface has named; it
     should have a current-task ledger entry per Gate 1, and is a candidate
     for the Step 4 promotion mechanism at
     `implementation-workflow/SKILL.md:135`.
   - **Local duplicate** — names an object an existing canonical or
     prior-task symbol already names. This is the failure mode → flag.
2. **Prior-result pre-flight.** For each derived equation or named
   statement in the current task, search prior tasks for an equivalent.
   Two matches to look for:
   - **Name match** against named lemmas, propositions, corollaries — if a
     prior task established Lemma 2.3 and the current task is re-deriving
     it under a different name, flag.
   - **Content match** against displayed equations — if a prior task's
     displayed equation is algebraically equivalent (after canonical
     notation substitution) to the current task's, flag.
3. **Prose integration pass.** Re-read the section immediately preceding
   the new task's section in the document. Compare:
   - Terminology — same words for the same objects?
   - Assumption phrasing — same form ("Suppose …" vs "Assume …" vs
     "Let …")?
   - Formality level / register — same?
   - Notation usage — same conventions for inline vs. display, same
     subscript/superscript style, same Greek-vs-roman choices?
   Then read the new section through the lens of `audience-discipline-*`:
   any chat-style meta-commentary, workflow-vocabulary leaks, or forward
   references the reader cannot resolve are coherence failures even if the
   math is right.

Pattern-watch list:

- A symbol is defined locally with the same denotation as a symbol in
  `PLAN.md` Notation Conventions but a different name.
- An equation is derived from primitives in the current task while a prior
  task established the same equation as a lemma.
- The new section uses "we" while the surrounding sections use "I", or
  vice versa.
- Workflow vocabulary (`task`, `PLAN.md`, `RESULTS.md`, `as requested`,
  `the reviewer asked`, `for now`, `referee` in paper body) appears in
  prose intended for the paper.
- Forward references to "the planning step", "as discussed earlier in
  chat", "as we noted above" with no resolvable referent inside the
  document.
- A subsection opener justifies the section's existence by contrast with
  "the main theorem" or "the main case" without that comparison being set
  up for the reader.

### Checklist

- `[BLOCKING]` **Notation pre-flight.** Every symbol in the current task is
  canonical, prior-task-promoted, or logged as a Step 4 promotion candidate
  (per `implementation-workflow/SKILL.md:135`). Local symbols duplicating
  a canonical or prior-task-promoted name are REVISE — replace with the
  upstream symbol and document the rename if relevant.
- `[BLOCKING]` **Prior-result pre-flight.** Equivalent equations and named
  statements established in prior tasks are cited and reused, not
  re-derived. Specializations of a prior result to a sub-case state the
  relationship to the prior result explicitly ("Lemma 2.3 specialized to
  the symmetric case yields …").
- `[BLOCKING]` **Prose-integration check.** Terminology, assumption
  phrasing, register, and notation conventions match the surrounding
  sections. Style breaks at section transitions are REVISE.
- `[BLOCKING]` **Reader-perspective discipline.** Per
  `audience-discipline-writing.md` and `audience-discipline-modeling.md`:
  no workflow-vocabulary leaks in paper-body prose; no mid-proof
  self-narration of agent choice; no forward references the reader cannot
  resolve inside the document; no implicit-context assumptions resting on
  chat / `RESULTS.md` only. Leaks in paper body / appendix are
  `[BLOCKING]`; leaks in working notes are `[ADVISORY]`.
- `[BLOCKING]` **Document-code consistency.** If the model feeds papers,
  slides, notes, or downstream artifacts in the repo, numerical and
  methodological inconsistencies between the refactored work and those
  artifacts are reconciled or flagged in `RESULTS.md` when reconciliation
  is out of scope.

---

## Section D — Discipline preserved through refactoring

### Principle

Refactoring can silently change assumptions, branch choices, solver
defaults, equation rendering, or which parameter set is used for
verification. **Refactored modeling work must be re-validated, not just
carried forward.** Where Sections A–C build new readability, Section D
guards against quiet loss of derivation-discipline artifacts that already
existed — ledger entries, per-step reasons, stated intuitions, verification
records, the canonical notation table's gating discipline.

### Identification protocol

Diff the pre-refactor and post-refactor versions of every modified
artifact. For each `[BLOCKING]` item in the checklist below, ask: is the
artifact still present, and does it still carry the discipline-bearing
content (intuition, interpretation, reason, ledger entry) — or has the
refactor silently collapsed it into prose, dropped it, or paraphrased it
away? Items collapsed into prose without the discipline-bearing content
preserved are REVISE.

### Checklist

- `[BLOCKING]` **Defined objects and assumptions survive the refactor.**
  The refactored code and notes still name the primitives, endogenous
  objects, and active assumptions before using them.
- `[BLOCKING]` **Step-by-step derivation survives.** Algebraic steps, case
  conditions, and justification notes are still auditable; they were not
  collapsed into opaque prose or code.
- `[BLOCKING]` **Verification checks survive.** Substitution checks,
  limiting cases, and simple numerical examples from the original work are
  present in the refactored code or notes and were rerun successfully.
- `[BLOCKING]` **Drift tests pass post-refactor.** Where drift tests
  exist, they pass on the refactored work; failures are adjudicated per
  `references/integrate-drift-tests.md`, never silenced by changing
  expectations without explanation.
- `[BLOCKING]` **Rendered markdown/LaTeX describes what the refactored
  code actually does.** Equation blocks, symbols, and case labels match
  the live derivation and numerical outputs.
- `[BLOCKING]` **No derivation-discipline artifact has been deleted.**
  Definitions, assumptions, verification notes, and renderable math blocks
  may be reorganized, but they are not silently dropped.
- `[BLOCKING]` **Stated intuition for new symbols survives.** Every
  notation entry whose original work carried an intuition or mnemonic
  (per `SKILL.md` §Gate 1 — Objects & Notation) still carries that
  intuition in the refactored notes — not collapsed into opaque prose or a
  bare code comment.
- `[BLOCKING]` **Assumption interpretations survive.** Every assumption
  whose original work carried a plain-language interpretation (per
  `SKILL.md` §Gate 2 — Assumptions) still carries that interpretation —
  not reduced to a math restriction without the economic reading, and not
  silently merged away when assumptions are consolidated.
- `[BLOCKING]` **Per-step reasons survive.** Every non-trivial derivation
  step whose original work carried both the technical rule and a
  one-sentence reason for invoking it (per `SKILL.md` §Gate 3 —
  Derivations) still carries both — mechanical rule-labels without a
  reason, or reasons silently dropped during consolidation, are REVISE.
- `[BLOCKING]` **Per-task Notation & Assumptions Ledger entries survive.**
  Every per-task ledger entry from the original work (per `SKILL.md`
  Gates 1–2) is still present in the refactored `RESULTS.md` — necessity
  rationale and near-duplicate-rejection reasons not silently collapsed
  into prose, removed, or paraphrased away. Ledger entries are the
  auditable trail of the necessity gate; they survive refactor like any
  other derivation-discipline artifact. Section A's recursive signposting,
  Section B's local-obviousness recalls, and Section C's notation /
  prior-result coherence are the rewriting-time companions to ledger
  survival — when those sections move text around, the ledger entries
  underneath must remain intact.
- `[BLOCKING]` **`PLAN.md`'s Notation Conventions table contains only
  user-confirmed promotions.** Symbols introduced during implementation
  appear in the canonical table only if a `## Decisions` log entry records
  the researcher's promotion approval (per
  `implementation-workflow/SKILL.md:135`). Orphan entries — symbols added
  to the canonical table without a logged user decision — are REVISE;
  either the decision log entry is missing (add it) or the entry was
  added without confirmation (move back to the per-task ledger). Section C's
  notation pre-flight is the rewriting-time companion: a refactor that
  moves a symbol from a per-task ledger to the canonical table without a
  user decision is the same failure surfaced at integration.

### Utility reuse and documented deviations

- `[BLOCKING]` **Reuse the existing markdown/rendering utility.**
  Human-facing markdown with equations, tables, or figures routes through
  `superRA:report-in-markdown`; do not invent a parallel rendering utility
  or formatting convention.
- `[BLOCKING]` **Document notation changes.** Any intentional rename or
  consolidation of symbols carries an explicit old-to-new mapping so
  downstream docs and readers can follow it.
- `[BLOCKING]` **Document strengthened assumptions.** If a refactor
  reveals that a result requires stronger primitive restrictions than
  previously stated, record the new restriction, where it enters, and why
  it is needed. (If the strengthened assumption is genuinely new rather
  than a clarification, this is a correctness fix — halt and re-dispatch
  as `Stage: implementation` per the header scope.)
- `[ADVISORY]` **Leave migration pointers when consolidating helpers.**
  If symbolic or numerical helper code moves to a shared location and
  older files still reference the old location, leave a one-line pointer
  so follow-on work does not silently fork the old path.

---

## Reviewer verdict protocol

Verdict protocol follows the active reviewer role; walk Sections A, B, C,
and D in order alongside `refactor-and-integrate/SKILL.md`. Two verdicts:
`APPROVE` (no `[BLOCKING]` findings) / `REVISE` (at least one `[BLOCKING]`
finding). When a structural rewrite would require introducing new math, new
assumptions, or new verification claims, halt and re-dispatch as
`Stage: implementation` rather than acting outside scope.
