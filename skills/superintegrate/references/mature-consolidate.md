# Mature & Consolidate

Once Integrate closes, every task this integration touched is a distillation candidate: its work is settled and verified. For each touched task, decide and execute as **one act** the structural fold (content merged into the parent, kept as its own task, directory removed) together with the results altitude (dropped / a folded pointer or one-line note / a short retained subsection / a matured reader-facing narrative at the durable home). Run this stage once, after Integrate, on final results — the fold actions are atomic over objective + results + directory and must not run on pre-Integrate state.

Screening and the user-facing proposal are orchestrator inline work, not a dispatched implementer, because consolidation is user-involving. Execution is dispatched.

## Step 1: Screen the whole affected tree (mandatory)

Load `superplan/references/task-tree-design.md` and survey every task and subtree the integration touched — including approved and in-flight update tasks — against its parent and other candidate durable owners. Run `superra task tree` and `superra task dag` as structural evidence for the manual survey. Identify every update-task, action-verb parent, and misplacement, and per touched subtree draft the distillation: each task's durable home, the structure change that realizes it, and the altitude its `## Results` distils to. Key results selected at Protect are never dropped; when a task's own output *is* a document, distil its `## Results` to a pointer to that document.

## Step 2: Ask the distillation question, one per touched subtree (always fires)

Ask one options-with-recommendation question per touched subtree (`AskUserQuestion`), across as many calls as the harness per-call limit takes. The question always fires — a clean subtree still gets one, with the recommended option carrying no fold ("keep as-is, mature at <home>"). Each question's options are that subtree's candidate consolidation actions plus an explicit keep-as-is option that lets the user veto; mark the orchestrator's screened recommendation first. The recommended option states the proposed structural action(s) and the resulting `## Results` altitude:

```text
Subtree <subtree-path> — consolidate how?
  ▸ [Recommended] Fold <task-a> into <parent> (results → one-line note);
    drop <task-c> (already in <parent> diff); <task-b> matures at <home>
  ▸ Keep all tasks as-is; mature each in place
  ▸ <other meaningful variant — e.g. a different durable home for <task-b>>
```

Material tree changes route through `superplan §User Feedback and Changing the Task Tree` for explicit approval — pruning a task whose result a reader would expect, merging substantive concerns, or a scope-expansion that invalidates downstream. Routine distillation is the recommended default the user can veto. Execution cannot begin before the answer.

## Step 3: Record, then dispatch execution

Fold each subtree's decision into `## Revision Notes` on the affected tasks, then dispatch implementer(s) to execute the distillation — structural folds and results altitude together, per subtree (fan out per subtree when large):

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: maturation
  Task: Execute the distillation for <subtree-path>
  Tasks in scope: <task paths in this subtree>

  Additionally: execute the recorded `## Revision Notes` distillation —
    structural folds per `superplan/references/consolidation.md`, and the
    `## Results` altitude per `task-tree/references/task-file-contract.md`
    §Results Shape (drop / pointer / short subsection / matured narrative),
    materializing figures with `report-in-markdown` where a matured home needs
    them. Edit task.md files in place; land one recoverable commit per task or
    logical group and report which sub-commits landed.
```

## Step 4: Whole-tree review

Dispatch one whole-tree reviewer for structure (not parallelized); results distillation may fan out per subtree when large:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: maturation
  Task: Verify consolidated structure and distilled results
  Git range: <BASE_SHA>..<HEAD_SHA>
  Tasks in scope: <whole affected tree>

  Additionally: verify the consolidated structure — no update-task or
    action-verb scaffolding left stranded, placement clean, Protect key
    results retained — and the distilled `## Results` per
    `task-tree/references/task-file-contract.md` §Results Shape.
    <prior-round adjudication notes if re-dispatching>
```

If a REVISE finding traces to the code, re-enter Integrate. On APPROVE, commit the consolidated, matured tree (`integrate(mature): …`).
