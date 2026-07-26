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
4. **Dispatch the protection creator.** `Stage: protection`, canonical implementer template. Record the selected results, durable homes, and mechanisms in the affected tasks' working `## Results`; create only the selected automated protection.
5. **Dispatch the protection reviewer.** `Stage: protection`, canonical reviewer template. When drift tests were selected, apply `result-protection/references/drift-test-quality.md`.
6. **Run the protection suite and commit.** The protection commit (`integrate(protect): …`) records the choices and any new automated protection. Mature & Consolidate consumes those choices after Sync.
