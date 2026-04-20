# Refactor-and-Compile — Safe find-replace + build gate

> Load at the **IMPLEMENT phase** whenever edits are made — every batch of edits ends with a build. Also loaded for any terminology / notation / variable-name refactor, and for fixing compile failures. Severity markers: `[BLOCKING]` must fix to earn APPROVE; `[ADVISORY]` flaggable as MINOR.

This reference has two sections:

- **§Refactor** — context-aware find-replace across a document (rename a variable, change a term of art, update a convention). Per the Iron Law (main SKILL.md), every refactor must respect authorial intent and scope.
- **§Compile** — build commands per engine (LaTeX, Quarto, Pandoc, Markdown), warning triage heuristics, and error-escalation rules.

---

## §Refactor

**Principle.** A find-replace across a document is cheap to run and expensive to get wrong. Naive substitution destroys text that looks similar to the target but means something different. The discipline is: **always preview, always confirm word-boundary, always check case and plural variants, always build after.**

### The Four Always

1. **Always preview matches first.** Before any substitution, run a read-only search (`grep -n`, editor find) and list every match. Review the list; mark each as *rename* or *leave*. Only after confirming the list do you run the substitution.
2. **Always confirm word-boundary.** `estimate` matches inside `underestimate`, `estimates`, `estimator`, `estimation`. `Table` matches inside `acceptable`. Use `\b` (regex word boundary) or `-w` (grep whole-word) where the tool supports it.
3. **Always check case variants.** `Treatment`, `treatment`, `TREATMENT` — the substitution may need all three, or exactly one. Decide explicitly.
4. **Always check plural / inflection variants.** `treatment` vs `treatments`; `ran` vs `run` vs `running` — are they all in scope for the refactor? Often they are, but not always.

### Worked examples of false-positive matches

| Target | False-positive matches | Fix |
|---|---|---|
| `estimate` | `underestimate`, `estimation`, `estimator`, `estimates` | Word-boundary + decide on inflections explicitly |
| `Table 1` | `acceptable`, `Tablespoon` (if unlikely but imagine) | Word-boundary; or search `Table 1\b` |
| `y` (variable name) | Every word containing `y` — `policy`, `they`, `yield` | Never substitute a single letter without a mathmode / code-block constraint |
| `OLS` | `ROLS`, `TOOLS` (unlikely but imagine) | Word-boundary; all-caps-only often enough |
| `reg` | `region`, `regardless`, `aggregate` | Almost always a bad target — use a longer, more unique target |
| `r_i` | `r_ij`, `r_{i,t}` | Decide whether the refactor covers the subscripted forms; LaTeX subscripts complicate matching |
| `\cite{foo}` | `\citep{foo}`, `\citet{foo}` | Usually the refactor covers all three; list them and confirm |

### Math-mode refactors

Math-mode identifiers (`\beta`, `x_i`, `\mathbf{x}`) are especially trap-laden because:

- The same letter in math mode and text mode are *different* (`\beta` in an equation vs `beta` in prose).
- Subscripts, superscripts, and decorators (`\hat`, `\tilde`, `\bar`) multiply the patterns.
- A rename that changes `x` → `z` will match every `x` character in every equation — including equations where `x` is playing a different role.

Approach:

1. Scope the refactor to math-mode only where possible (the tool may support `$...$` matching; if not, use explicit patterns).
2. List every location first.
3. Consider whether subscripted (`x_i`, `x_{i,t}`) and decorated (`\hat x`, `\bar x`) forms should all change. Usually yes.
4. Build after.

### Terminology refactors (prose)

When renaming a term of art (`treatment group` → `treated sample`):

- The new term must be a legitimate synonym *for this paper's audience*. Consult `writing/references/consistency/terminology.md`.
- Check for plural, possessive, hyphenated, and capitalized variants.
- Respect case and capitalization contextually — sentence-start capitalization vs mid-sentence.
- If the old term appears in a direct quotation (block quote, citation), **do not substitute** — quotes are sacred.

### After any refactor — verify

- **Build the document.** See §Compile below. Errors introduced by the refactor block the refactor.
- **Cross-reference check.** Any label, citation key, or bib key touched? See `writing/references/consistency/cross-references.md`.
- **Diff review.** Read the git diff end-to-end. Every changed hunk should look intended.

### Refactor Gated Checklist

- `[BLOCKING]` Every substitution was previewed before being applied.
- `[BLOCKING]` Word-boundary correctness confirmed — no false-positive matches remain in the diff.
- `[BLOCKING]` Case and plural/inflection variants considered explicitly.
- `[BLOCKING]` Direct quotations and block quotes not touched (quotes are sacred).
- `[BLOCKING]` Document builds after the refactor (§Compile).
- `[BLOCKING]` Git diff read end-to-end; every hunk intentional.
- `[ADVISORY]` Refactor pre-image list (what changed, how many instances, in which files) saved to the handoff.

---

## §Compile

**Principle.** Every batch of edits ends with a build. Errors block handoff; warnings are triaged. Errors that were not in the pre-edit build but appear in the post-edit build are the edit's responsibility.

### Build commands per engine

**LaTeX (`latexmk -pdf`)**

```bash
latexmk -pdf main.tex         # preferred: handles BibTeX / biber / multiple passes
# fallback:
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

The third `pdflatex` pass resolves forward references. `latexmk` handles this automatically.

**Quarto (`quarto render`)**

```bash
quarto render paper.qmd       # detects engine from yaml; runs pandoc + PDF engine
```

**Pandoc (`pandoc`)**

```bash
pandoc paper.md -o paper.pdf --citeproc --from markdown
# or with pandoc-crossref for figure/table refs:
pandoc paper.md -o paper.pdf --filter pandoc-crossref --citeproc
```

**Markdown (various)**

For Markdown rendered via a static-site generator (MkDocs, Jekyll, Hugo, Zola), use the project's build command. There's no universal default.

### Reading build output

After any build, read the log:

1. **Errors.** Halt the build. Must be fixed before handoff.
2. **Warnings.** Classified below. Triage each.
3. **`??` in output.** Unresolved cross-references — treat as errors for Verify purposes (`writing/SKILL.md` §Three Concurrent Disciplines).

### Warning triage heuristics

| Warning class | Default action | Notes |
|---|---|---|
| `Overfull hbox` | Ignore unless egregious | Line overruns the text margin. Cosmetic in draft; fix before submission. |
| `Underfull hbox` | Ignore | Stretched spacing. Cosmetic. |
| `Underfull vbox` | Ignore in drafts | Fixable with manual pagebreaks later. |
| `Reference(s) undefined` | **Escalate** | Unresolved `\ref`. `[BLOCKING]`. |
| `Citation(s) undefined` | **Escalate** | Missing BibTeX entry or stale `.aux`. `[BLOCKING]`. |
| `LaTeX Error: File not found` | **Escalate** | Missing figure, `\input`, or package. `[BLOCKING]`. |
| `Package <X> Warning: ...` | Read and judge | Often signals a real problem; triage case-by-case. |
| `No \title given` / `No \author given` | Ignore if draft; fix before submission | |
| `LaTeX Warning: Label(s) may have changed` | Re-run the build | Normal on first pass; persists → investigate. |
| Pandoc warning `[WARNING] Could not find reference for ...` | **Escalate** | Missing citation. `[BLOCKING]`. |
| Pandoc `[WARNING] This document format requires nonempty ...` | Read and judge | Often a YAML metadata issue. |

### Error-escalation rules

- **Build errors introduced by the edit:** the edit is responsible. Fix before handoff.
- **Build errors already present before the edit (the document was already broken):** flag in the handoff — this is usually an upstream issue (missing package, bad path); escalate to the researcher unless the edit should include the fix.
- **Warnings newly introduced:** triage per table above. If `[BLOCKING]`-class, fix; otherwise list in handoff.
- **Warnings present before and after the edit:** note as pre-existing, do not touch unless the task scope includes build-hygiene.

### Build output in handoff

For non-trivial edits, include in the handoff:

- Build command used.
- Pass / fail.
- Number of warnings, broken out by class (new vs pre-existing).
- Each new `[BLOCKING]`-class warning listed with file + line.

### Compile Gated Checklist

- `[BLOCKING]` Document builds after the edit. Command used is stated in handoff.
- `[BLOCKING]` No new unresolved cross-references (`??` in output, `undefined references` warnings) introduced by the edit.
- `[BLOCKING]` No new undefined citations introduced by the edit.
- `[BLOCKING]` No new `File not found` errors introduced by the edit.
- `[ADVISORY]` Build warnings enumerated in handoff (new vs pre-existing).
- `[ADVISORY]` Each new warning has a ≤1-line triage rationale.

---

## Reviewer verdict protocol

Walk §Refactor (if the task performed a refactor) and §Compile top to bottom; never halt on a failure; return APPROVE / REVISE.
