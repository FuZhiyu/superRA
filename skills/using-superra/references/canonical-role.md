# Canonical Role Resolution

Load when a main-filled or harness-forced-inline seat must execute a canonical role spec.

From the directory containing `using-superra/SKILL.md`, resolve the selected role:

```bash
python3 scripts/resolve_role.py implementer
python3 scripts/resolve_role.py reviewer
```

Read the emitted absolute path before executing the seat. The resolver locates
`agents/` from its installed plugin package, not from the active project.
