# Integration Discipline for Theory Modeling — the Rewriting Reference

> Loaded at `Stage: integration` for theory-modeling tasks. The readability
> layer for theory-modeling work: ex-post structural rewriting (Section A),
> per-step local obviousness (Section B), cross-document coherence
> (Section C), and refactor-survival of correctness artifacts (Section D).
>
> **Scope.** Document-internal coherence and ex-post rewriting. If a
> structural rewrite surfaces a correctness fix, halt and re-dispatch as
> `Stage: implementation`. Generic codebase-coherence concerns belong to
> `refactor-and-integrate/SKILL.md` — load both at this stage.

Each section follows **principle → identification protocol → checklist**.
Verdict adjudication follows the standard reviewer protocol in
`agent-orchestration`.

---

## Section A — Objective-first structural rewriting

### Principle

A derivation is read forward but built backward. **Start from the object
the proof needs, then expand only the terms required to evaluate it.**
Forward writing runs along a backward dependency walk: name the target;
identify what the target requires; recurse only into terms that are not
already known.

This makes the proof linear in the reader's experience: target named,
needed pieces named, structural cancellations performed, canonical objects
substituted, conclusion reached. Local placeholders introduced before the
target is named force the reader to hold a symbol with no purpose; they
are the dominant structural failure mode.

The discipline is **recursive**. A multi-step proof signposts its
top-level strategy in one sentence; each non-trivial sub-argument
signposts its own local strategy in the same form; transition prose at
major joins names where we are in the parent plan ("having established
$Y$, we turn to $Z$"). A reader entering at any point should be able to
recover the local goal from the surrounding signposts.

A worked bad/good walkthrough plus identification-training drills lives
in `references/objective-first.md`; load on demand for the canonical
example before applying the checklist.

### Identification protocol

Walk the existing derivation top-to-bottom in the reader's order:

1. **Read the prose preceding the first displayed equation.** Does it
   name the object the proof targets? If the first display is an
   assertion of an intermediate symbol (e.g., "$z_j := \ldots$") with no
   prior reference to the target, the structure is local-detour-first →
   flag.
2. **For each displayed equation, ask: which named target does this
   advance?** If the answer is "we will see in three pages why this
   matters," the structure has deferred the goal → flag.
3. **At every block longer than ~5–10 lines of algebra, ask: does the
   prose open with a one-sentence local strategy?** Sub-arguments
   without their own opening signpost force the reader to infer scope
   from algebra alone → flag. Watch for sub-sections that open directly
   with manipulation rather than prose, and for "we will use this below"
   phrasing — the term should appear when its use is named.
4. **At every section/sub-section join, ask: does the prose name the
   transition?** ("Having $X$, we turn to $Y$.") Bare juxtaposition of
   blocks without transition prose → flag.
5. **For each placeholder symbol introduced** (an object that does not
   appear in `PLAN.md` Notation Conventions and is not a canonical model
   object), ask: is the placeholder still doing structural work after
   rewrite, or did the objective-first rewrite remove its reason to
   exist? Surviving placeholders that no longer carry independent
   meaning → flag.

### Checklist

- `[BLOCKING]` **Target named and dependency walk visible in prose
  before the algebra.** The target is the object the proof is computing
  or signing. The chain from target down to primitives or already-known
  objects appears either as a brief prose walk ("we need $T$ ← $A$ ←
  $B$, the canonical column from §X") or as recursive sub-argument
  signposts.
- `[BLOCKING]` **Recursive sub-argument signposts.** Every non-trivial
  sub-argument opens with its own one-sentence strategy. Major
  transitions carry prose naming the local position. Test: cover all
  algebra and read only the prose; can a reader recover the proof's
  scaffolding? Walls of algebra without strategy prose → REVISE.
- `[BLOCKING]` **Placeholder symbols introduced for detours are removed
  when the rewrite makes them unnecessary.** A placeholder that survives
  rewrite must justify its place against the per-symbol ledger entry
  (Gate 1 in `theory-modeling/SKILL.md`); otherwise REVISE.
- `[ADVISORY]` **Onion-style layering.** When the result has a clean
  baseline plus complications, present the simplest case first, then add
  complications in layers.

---

## Section B — Per-step local obviousness

### Principle

Every displayed equation should be **obvious** from a roughly half-page
reading window above it. "Derivable in principle" is too weak — a reader
who has to reconstruct missing definitions, recall a 10-page-back
assumption, or unpack three substitutions collapsed into "therefore"
loses the thread. The author's job is to make each transition obvious
within the local window.

When a step is not obvious, exactly one of six fixes applies:

1. **Define inline.** If a symbol is not defined in the local window,
   give its definition at first use in this region (one phrase or one
   displayed line — the canonical entry stays in `RESULTS.md`).
2. **Restate the assumption.** If a step depends on an assumption stated
   far above, restate it in scope at the point of use ("Under the
   bounded-risk-aversion assumption (§2), …").
3. **Cite-with-form-recall.** If a step depends on a prior result too
   far back to assume the reader holds it, cite by name or equation
   number **and** restate its operative form inline ("By Lemma 3.1,
   $f(x,\theta) = g(x) + \theta h(x)$, so …"). A bare "(see §3.2)" is
   insufficient when the step depends on the specific form.
4. **Split the step.** If multiple substitutions, cancellations, or sign
   manipulations are collapsed into a single move, split so each
   transition is one obvious move with one named rule.
5. **Make the reference precise.** Prose referring to a specific
   variable uses the math symbol ($\beta$, not "the discount factor");
   prose referring to a specific equation or named statement cites it by
   number or name ("eq. (12)", "Lemma 3.1", not "the equation above" or
   "the FOC we derived"). Carve-out: introduction sites where plain
   language *is* the definition ("let $\beta$ denote the discount
   factor") are not violations — the rule governs back-references to
   objects the document already names.
6. **Disambiguate the rendering.** If a subscript, superscript, fraction,
   summation limit, or align environment renders ambiguously, restructure
   the LaTeX (explicit braces, displayed `\frac` over inline `/`, aligned
   multi-line breakdowns of long products). The symbol is defined and
   the step is logically one move, but the rendered glyphs hide which
   object the reader is looking at.

### Identification protocol

The core diagnostic is the **half-page mask test**. For each displayed
equation:

1. Cover everything except the half page (~25–40 lines) immediately
   above the equation.
2. Read only that window. Is the equation obvious — not merely derivable
   with effort, but **obvious** — from what is visible?
3. If not, identify which of the six failure types maps to the missing
   piece (undefined symbol / unrestated assumption / uncited or
   content-less prior result / over-compressed step / imprecise
   reference / ambiguous rendering) and apply the matching fix from the
   principle above.

Pattern-watch list — concrete grep-able instances:

- "$X = \ldots$" asserted with no preceding definition or named rule.
- "By symmetry" / "by inspection" with no operative-form recall.
- "(see §3.2)" / "(see Lemma X)" without restating the result's
  operative form when the step depends on the form.
- "Therefore" / "thus" / "it follows that" connecting a long chain in
  one step.
- A symbol last defined more than half a page back is reused without a
  one-phrase recall.
- Prose names a variable in English ("the discount factor") when a math
  symbol is in scope; prose points at an equation by position ("the
  equation above") rather than by number.
- Nested subscripts collapsing (`x_{i_j}` → `x_ij`); long fractions or
  summations on one line where boundaries blur.

### Checklist

- `[BLOCKING]` **Every displayed equation is obvious from the local
  window.** Each symbol is defined in scope or canonically pointed to
  with its meaning recalled; each rule used is named; each prior-result
  dependency is cited with operative form visible. "Derivable with
  effort" is not enough.
- `[BLOCKING]` **Citations to results outside the local window include
  content recall when the step depends on the form.** A bare "(see §3.2)"
  is REVISE when the next move uses the specific form.
- `[BLOCKING]` **Symbol freshness.** Symbols last seen more than half a
  page back are recalled in one inline phrase at re-use ("$\mathbf{c}_k$,
  the column-$k$ dividend loading defined at §2.1").
- `[BLOCKING]` **Step granularity.** Over-compressed steps are split so
  each transition is one obvious move with one named rule. Break long
  chains into aligned steps rather than dense one-line algebra.
- `[BLOCKING]` **Precise prose-to-math references.** Use math symbols
  for back-references to defined variables; use equation numbers / named
  statements for back-references to results.
- `[BLOCKING]` **Rendering legibility.** Markdown and LaTeX render
  unambiguously — subscripts, superscripts, fractions, summation limits,
  and align environments read cleanly. (Rendering correctness — output
  matching the computed object exactly — is owned by Gate 4 in
  `theory-modeling/SKILL.md`.)
- `[ADVISORY]` **Prefer compact inline restatement over forcing the
  reader to navigate.** When the choice is between a short inline recall
  and an uncited cross-reference, the inline recall serves the reader
  better even when the cross-reference is technically sufficient.

---

## Section C — Cross-document coherence

### Principle

A derivation correct in isolation is wrong in a paper if its symbols
clash with canonical Notation Conventions, if it re-derives an equation
already established earlier, or if its prose breaks the style of
surrounding sections. Local correctness is necessary but not sufficient —
a task at integration stage owes the document a result that fits the
document.

Three coherence layers, each with its own authority:

- **Notation.** `PLAN.md` Notation Conventions is canonical. Prior-task
  RESULTS.md ledgers carry symbols not yet promoted but introduced
  upstream and reusable. Local symbols duplicating either hide the
  connection.
- **Prior results.** Equations and named statements established earlier
  in the document or a prior task are cited and reused. Re-deriving an
  equivalent result in a new section silently forks the document.
- **Prose integration.** Terminology, assumption phrasing, formality
  level, and notation usage match the surrounding sections.

### Identification protocol

1. **Notation pre-flight against `PLAN.md` Notation Conventions and
   prior task ledgers.** For each symbol in the current task, classify:
   - **Canonical** — already in `PLAN.md` Notation Conventions; reuse.
   - **Prior-task-promoted** — in a prior task's ledger naming the same
     object; reuse and cite.
   - **Genuinely new** — names an object no prior surface has named;
     log a current-task ledger entry per Gate 1, candidate for promotion
     per `implementation-workflow/SKILL.md:135`.
   - **Local duplicate** — names an object an existing canonical or
     prior-task symbol already names → flag.
2. **Prior-result pre-flight.** For each derived equation or named
   statement, search prior tasks for a name match (a prior lemma now
   re-derived under a different name) or a content match (a prior
   displayed equation algebraically equivalent under canonical
   notation) → flag if found.
3. **Prose integration pass.** Re-read the section immediately preceding
   the new task's section and compare terminology, assumption phrasing,
   register, and notation usage. Style breaks at the join → flag.

### Checklist

- `[BLOCKING]` **Notation pre-flight.** Every symbol is canonical,
  prior-task-promoted, or logged as a Step 4 promotion candidate (per
  `implementation-workflow/SKILL.md:135`). Local duplicates → REVISE —
  replace with the upstream symbol and document the rename if relevant.
- `[BLOCKING]` **Prior-result pre-flight.** Equivalent equations and
  named statements established in prior tasks are cited and reused, not
  re-derived. Specializations of a prior result state the relationship
  explicitly ("Lemma 2.3 specialized to the symmetric case yields …").
- `[BLOCKING]` **Prose-integration check.** Terminology, assumption
  phrasing, register, and notation conventions match the surrounding
  sections. Style breaks at section transitions are REVISE.
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
carried forward.** Section D guards against quiet loss of
derivation-discipline artifacts that already existed — ledger entries,
per-step reasons, stated intuitions, verification records.

### Identification protocol

Diff the pre-refactor and post-refactor versions of every modified
artifact. For each `[BLOCKING]` item below, ask: is the artifact still
present, and does it still carry the discipline-bearing content
(intuition, interpretation, reason, ledger entry) — or has the refactor
silently collapsed it into prose, dropped it, or paraphrased it away?

### Checklist

- `[BLOCKING]` **Stated intuition for new symbols survives.** Every
  notation entry whose original work carried an intuition or mnemonic
  (per Gate 1 in `theory-modeling/SKILL.md`) still carries it in the
  refactored notes — not collapsed into opaque prose or a bare code
  comment.
- `[BLOCKING]` **Assumption interpretations survive.** Every assumption
  whose original work carried a plain-language interpretation (per
  Gate 2) still carries it — not reduced to a math restriction without
  the economic reading, and not silently merged away when assumptions
  are consolidated.
- `[BLOCKING]` **Per-step reasons survive.** Every non-trivial
  derivation step whose original work carried both the technical rule
  and a one-sentence reason for invoking it (per Gate 3) still carries
  both.
- `[BLOCKING]` **Per-task Notation & Assumptions Ledger entries
  survive.** Every per-task ledger entry from the original work (per
  Gates 1–2) is still present in the refactored `RESULTS.md` — not
  silently collapsed into prose, removed, or paraphrased away.
- `[BLOCKING]` **Verification checks survive.** Substitution checks,
  limiting cases, and simple numerical examples from the original work
  are present in the refactored code or notes and were rerun
  successfully.
- `[BLOCKING]` **Drift tests pass post-refactor.** Where drift tests
  exist, they pass on the refactored work; failures are adjudicated per
  `references/integrate-drift-tests.md`.
- `[BLOCKING]` **Rendered markdown/LaTeX matches the refactored code.**
  Equation blocks, symbols, and case labels match the live derivation
  and numerical outputs.
- `[BLOCKING]` **`PLAN.md`'s Notation Conventions table contains only
  user-confirmed promotions** (per `implementation-workflow/SKILL.md:135`).
  Orphan entries — symbols added to the canonical table without a logged
  user decision — are REVISE.

### Utility reuse and documented deviations

- `[BLOCKING]` **Route human-readable equations, tables, and figures
  through `superRA:report-in-markdown`.**
- `[BLOCKING]` **Document notation changes.** Any intentional rename or
  consolidation of symbols carries an explicit old-to-new mapping so
  downstream docs and readers can follow it.
- `[BLOCKING]` **Document strengthened assumptions.** If a refactor
  reveals a result requires stronger primitive restrictions than
  previously stated, record the new restriction, where it enters, and
  why it is needed.
- `[ADVISORY]` **Leave migration pointers when consolidating helpers.**
  If symbolic or numerical helper code moves to a shared location and
  older files still reference the old location, leave a one-line pointer.
