# Protect

Protect decides what the permanent record should contain and how each kept result should be guarded before agents write that record. Permanent results documentation is a valid protection mechanism. Add drift tests, document builds, outline checks, or other existing mechanisms only where the researcher selects them.

Creating new protection artifacts is scoped to the tasks this integration reopens or changes.

Load `superplan/references/task-tree-design.md` and `superplan/references/consolidation.md` when forming the task-tree choices.

## Steps

1. **Survey the provisional record.** Walk the task tree, result files, existing documentation, and relevant outputs. Identify reader-distinguishable findings and maintenance outcomes, not every intermediate number.
2. **Propose the protection, documentation, and consolidation choices.** Give a recommendation plus meaningful alternatives for:
   - which results to keep or drop;
   - the form and durable home of the final user-facing documentation and result files;
   - the durable task home and consolidation disposition for each affected subtree; and
   - the protection mechanism for each kept result: permanent documentation alone, documentation plus a drift test, or another existing mechanism appropriate to the artifact.
3. **Ask the researcher before permanent documentation is written.** Present concrete options rather than a blank request:
   ```text
   Proposed permanent record and protection:
   - <result>: keep in <artifact>; task result at <durable task home>;
     <documentation-only | documentation + drift test | other>
   - <result>: drop from the permanent record
   - <subtree>: <keep | fold into named owner | remove after protected content moves>

   Alternatives:
   - <meaningful alternative documentation, consolidation, or protection choice>

   Which option should I use? What should I add, remove, or protect differently?
   ```
4. **Create selected pre-maturation protection.** When the choices add automated checks or another protection artifact before maturation, dispatch the `Stage: protection` creator and reviewer with the canonical templates.
5. **Record the decision.** Create one `integrate(protect): …` commit after any selected protection artifacts pass review. Its body records the affected task scope, confirmed kept and dropped results, permanent artifact paths, durable task homes and consolidation dispositions, and protection mechanisms. Use an empty commit when Protect changes no files.
6. **Run the existing protection suite and proceed.** Carry the decision commit into Mature & Consolidate.
