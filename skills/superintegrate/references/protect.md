# Protect

Protect decides what the permanent record should contain and how each kept result should be guarded before agents write that record. Permanent results documentation is a valid protection mechanism. Add drift tests, document builds, outline checks, or other existing mechanisms only where the researcher selects them.

Always run the existing protection suite on every integration pass. Creating new protection artifacts is scoped to the tasks this integration reopens or changes.

## Steps

1. **Survey the provisional record.** Walk the task tree, result files, existing documentation, and relevant outputs. Identify reader-distinguishable findings and maintenance outcomes, not every intermediate number.
2. **Propose the protection and documentation choices.** Give a recommendation plus meaningful alternatives for:
   - which results to keep or drop;
   - the form and durable home of the final user-facing documentation and result files; and
   - the protection mechanism for each kept result: permanent documentation alone, documentation plus a drift test, or another existing mechanism appropriate to the artifact.
3. **Ask the researcher before permanent documentation is written.** Present concrete options rather than a blank request:
   ```text
   Proposed permanent record and protection:
   - <result>: keep at <durable home>; <documentation-only | documentation + drift test | other>
   - <result>: drop from the permanent record

   Alternatives:
   - <meaningful alternative documentation shape or protection choice>

   Which option should I use? What should I add, remove, or protect differently?
   ```
4. **Create selected pre-maturation protection.** When the choices add automated checks or another protection artifact before maturation, dispatch the `Stage: protection` creator and reviewer with the canonical templates, then commit those artifacts as `integrate(protect): …`.
5. **Run the existing protection suite and proceed.** Carry the confirmed choices into Mature & Consolidate. When documentation alone is sufficient and Protect changes no files, skip task edits, creator/reviewer dispatch, and a separate Protect commit.
