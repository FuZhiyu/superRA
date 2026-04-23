# Final form: consolidation discipline for Stage 2 `RESULTS.md`

Load this reference when you are either the **doc-writer subagent maturing `RESULTS.md` during `integration-workflow` Document** or the **doc-reviewer subagent reviewing that matured file**.

Consolidation **rewrites the file in place** before relocating it — it does not create a new file.

## The consolidation pass — four ordered commits

Sub-part A lands as **four separate commits, in order**. Each commit is independently recoverable — a session interruption mid-pass leaves the tree git-coherent and the next dispatch resumes at the first un-landed step. Do NOT bundle these into one commit: the atomicity is the whole point (a file move mixed with a fact-check edit is very hard to audit or revert).

### Commit 1 — Fact-check in place

Walk the fact-check checklist below against the Stage 1 `RESULTS.md` at the worktree root. No structural changes yet; only substitute wrong numbers with correct ones, strip unsupported claims, remove prohibited language, remove prohibited sections (Recommendations, Conclusions, Implications) unless the researcher explicitly requested them.

```bash
git add RESULTS.md
git commit -m "results: fact-check Stage 2 RESULTS.md"
```

**Validation before commit:** every cited number matches its source file (you opened each one and confirmed). No prohibited language patterns remain (grep the file if in doubt). No prohibited sections remain.

### Commit 2 — Restructure in place

Re-organize the now-fact-checked file. Still at worktree root, still Stage 1 figure paths. Changes:

- Restructure from task-indexed to reader-facing — by objective, data source, or result type. Task numbering from `PLAN.md` disappears.
- Merge related findings split across tasks (e.g., Task 3 built the sample, Task 5 ran the regression on it — combine into one section).
- Strip resolved reviewer caveats; surface unresolved limitations into a "Limitations" section.
- Add frontmatter per `baseline-io.md`. Stage 1 had none.

```bash
git add RESULTS.md
git commit -m "results: restructure Stage 2 RESULTS.md to reader-facing"
```

**Validation before commit:** no `## Task N` headings remain. Frontmatter is present at file top. Output shape matches the target layout (see §Output shape below).

### Commit 3 — Materialize figures

Copy figures from `results_attachments/` (worktree root, Stage 1 directory) into `${RESULTS_ATTACHMENTS_DIR}` (= `${RESULTS_DIR}/attachments`). Convert PDF→PNG if needed per `rich-content.md`. Update embed paths in `RESULTS.md` from `results_attachments/...` to `attachments/...` so they resolve correctly after Commit 4's relocation.

The file is still at worktree root at this point — only the figures and their embed paths have moved.

```bash
git add RESULTS.md ${RESULTS_ATTACHMENTS_DIR}/
git commit -m "results: materialize figures into ${RESULTS_DIR}/attachments"
```

**Validation before commit:** every figure embedded in `RESULTS.md` renders when previewed (every relative path resolves to a committed file). Every figure is a PNG (or the project's mandated format), not a PDF. `results_attachments/` at the worktree root still exists — do not delete it until after Commit 4 and the separate disposition pass.

### Commit 4 — Relocate

Move the file and the materialized attachments folder into the permanent location using `git mv` so history is preserved.

```bash
git mv RESULTS.md ${RESULTS_DIR}/RESULTS.md
# The attachments folder may have been created by Commit 3 already at
# ${RESULTS_ATTACHMENTS_DIR} (= ${RESULTS_DIR}/attachments) — in that case
# this step is just the RESULTS.md move. Otherwise git mv it too.
git commit -m "results: relocate RESULTS.md to ${RESULTS_DIR}"
```

**Validation before commit:** `git log --follow ${RESULTS_DIR}/RESULTS.md` shows the history back to the Stage 1 dev-log version. The file opens cleanly at its new location. Every figure-embed path resolves against the new location's `attachments/` folder.

After Commit 4, the doc-writer returns. The doc-reviewer dispatches against `${RESULTS_DIR}/RESULTS.md`.

## Fact-check checklist

Every matured `RESULTS.md` must pass this before integration review APPROVES. Go through it line by line.

### Claims and citations

- [ ] Every number, statistic, or factual claim is **backed by a link** to its source file (script, output CSV, figure, log). Citations are markdown links: `[text](../path/to/source)`.
- [ ] For each cited number, **open the source file** and confirm the number matches. No rounding inconsistencies. No stale values from before the last revision.
- [ ] Unsupported claims are flagged. If a claim cannot be cited, either cite it or remove it.

### Speculation and interpretation

The Stage 2 form documents what was found. It does **not** interpret, recommend, or speculate.

**Prohibited language patterns:**

- Speculation: "suggests", "indicates", "likely", "probably", "appears to", "this means", "implies", "shows that".
- Causal claims without an identification strategy: "because", "caused by", "due to".
- Subjective assessments: "excellent", "poor", "good", "bad", "successful", "failed", "robust", "reliable", "sophisticated".
- Quantitative adjectives without a definition: "significant", "strong", "weak", "accurate", "inaccurate".

**Acceptable alternatives:**

- "difference of X%", "within Y% of benchmark", "error rate of W%".
- "classified Z% of cases as X".
- "the regression coefficient is β = 0.12 (SE 0.04)".

**Exception:** if the researcher explicitly asked for interpretation (e.g., in `PLAN.md`'s objective or methodology section), allow it but flag the location in a reviewer note.

### Methodology

- [ ] Methodology sections **describe what was done**, not why. Why belongs in `PLAN.md`'s objective, not in the findings.
- [ ] Every methodological step links to the code file that implements it.
- [ ] Classification rules, filter criteria, and sample construction are shown in tables if they have branching logic.
- [ ] No evaluation of the methodology ("robust", "rigorous"). Just description.

### Results

- [ ] Tables present precise numbers. Compare against output files — no silent rounding.
- [ ] Units and formatting are consistent.
- [ ] Comparisons are factual ("X vs. benchmark Y: difference Z%"), not narrative ("good agreement", "significantly different").
- [ ] Figures are copied to the new `attachments/` directory and cited back to their original source path.
- [ ] Figure captions are descriptive — not "Figure 1".

### Prohibited sections

The following sections **must not appear** unless the researcher explicitly requested them:

- [ ] "Recommendations"
- [ ] "Conclusions" (interpretive)
- [ ] "Strategic Decision"
- [ ] "Implications"
- [ ] "Future Work"

A "Limitations" section that lists factual caveats (unresolved reviewer notes, data coverage gaps, known biases) is allowed and encouraged.

## Cross-consistency with project docs

Project-level docs (`CLAUDE.md` / `AGENTS.md` / `README.md`) are audited during `integration-workflow` Integrate per `refactor-and-integrate/references/codebase-integration.md` §Project Doc Audit. The doc-reviewer still checks that the matured `RESULTS.md` does not contradict them:

- [ ] **Methodology descriptions** in the matured RESULTS.md match the current code — no references to dropped approaches, superseded variable definitions, or removed processing steps
- [ ] **Headline results cited in project docs** (if any) match the matured RESULTS.md — no stale numbers from before the last revision
- [ ] **File paths and command names cited in RESULTS.md** are accurate — no references to moved, renamed, or deleted files

## Severity for integration review

When the doc-reviewer applies this checklist, classify issues:

- **Critical** — factual errors, unsupported claims, numbers that don't match sources. Blocks APPROVED.
- **Major** — speculation, interpretation, subjective language, prohibited sections. Blocks APPROVED.
- **Minor** — formatting, typos, citation path issues, missing alt text. Note but do not block.

Report issues in a plain checklist with line numbers and a specific proposed fix. Do not edit the file yourself as a reviewer — propose the fix and let the implementer apply it.

## Output shape after consolidation

A matured `RESULTS.md` typically contains:

1. **Frontmatter** (per `baseline-io.md`).
2. **Title and one-paragraph objective** pulled from `PLAN.md`'s objective section.
3. **Data section** — what data was used, with links to the code that loaded/cleaned it.
4. **Methodology section** — what was done, with links to scripts. Factual only.
5. **Results sections** organized by topic. Tables, figures, cited numbers.
6. **Limitations** (optional) — factual caveats.
7. **Reproducibility pointer** — one line stating the git commit and how to regenerate (e.g., "Reproduce via `make analysis` at commit `abcd123`").

Length: as long as the findings require. A two-page Stage 2 `RESULTS.md` is fine if the analysis was small. A fifteen-page one is fine if it wasn't. Do not pad.
