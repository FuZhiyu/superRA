# RESULTS.md Template

The findings document at the worktree root, created alongside `PLAN.md`. Mirrors the plan's task structure and gets updated after each step with key findings. This is the Stage 1 form — it matures into a permanent record at INTEGRATE Step 3 (see `superRA:handoff-doc`'s two-stage lifecycle).

**The canonical anatomy and inline-edit rules live in `superRA:handoff-doc`.** Load that skill for the six principles and the full per-task section structure. This template is a minimal starter scaffold.

## Starter Scaffold

```markdown
# [Analysis Name] — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** YYYY-MM-DD (Task N, Step M)
**Status:** In Progress

---

[Sections added as tasks complete — initially empty]
```

## Key Rules (see `superRA:handoff-doc` for the full treatment)

- One section per task, added as findings come in.
- Replace prior content on re-implementation; never append a second version.
- Reviewer caveats appear as a blockquoted note at the bottom of the section (replaced on re-review, not stacked; removed entirely when APPROVED with no remaining caveats).
- **Figures are always embedded with markdown image syntax**: `![caption](results_attachments/fig_name.png)`. The path is relative and the image file lives in `results_attachments/` at project root, committed to git. Full figure/math/table discipline in `skills/report-in-markdown/references/rich-content.md`.
- The document always reads as a single coherent current-state summary, not a changelog.
- Commit `RESULTS.md` and `results_attachments/` alongside each task's code commit.

## Per-Task Section Template

```markdown
## Task N: [Phase Name]

**Status:** Completed (Task N approved YYYY-MM-DD)

### Key Findings
- [primary result, with number]
- [secondary result]

### Row Counts / Sample
- Input: N rows
- After [operation]: N rows (delta: Δ)
- Final sample: N rows

### Figures and Tables
![Descriptive caption for fig A](results_attachments/fig_taskN_a.png)

![Descriptive caption for fig B](results_attachments/fig_taskN_b.png)

### Notes
- [any caveat, data quirk, or decision the reader needs to interpret the results]

> **⚠️ Reviewer caveat (implementation):** [only present if the implementation reviewer left one; replaced on re-review; removed when APPROVED]
```

Omit subsections that do not apply. Together with `PLAN.md`, this document forms a complete handoff: context + what happened + what was found.
