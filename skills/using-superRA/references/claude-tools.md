# Claude Tool Reference

These skills were originally authored around Claude Code's tool names. On Claude, the canonical terms are already native:

| Skill term | Claude meaning |
|------------|----------------|
| `AskUserQuestion` | question tool |
| `Skill` | invoke the named skill |
| `TodoWrite` | task-tracking tool |
| `Agent(subagent_type: "superRA:implementer")` | spawn the named implementer agent |
| `Agent(subagent_type: "superRA:reviewer")` | spawn the named reviewer agent |
| `SendMessage` | message an existing warm agent |
| parallel agent dispatch | use ordinary subagent fan-out |

Claude remains the primary harness. Keep the shared workflow behavior in canonical `skills/` and put harness-specific mapping rules in these adapter references rather than forking the workflow text.
