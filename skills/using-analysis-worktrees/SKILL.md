---
name: using-analysis-worktrees
description: Utility (infrastructure, optional any phase). Use when you want an isolated workspace for parallel analysis work — creates git worktrees with data seeding and environment setup. Recommended for complex or multi-session analyses. Optional for simple analyses; a feature branch without a worktree is sufficient.
---

# Using Analysis Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple analyses simultaneously without switching.

**This is optional.** For simple analyses, a feature branch without a worktree is sufficient. Worktrees are recommended when:
- Running multiple analyses simultaneously
- The analysis may take multiple sessions and you want full isolation
- You need separate data copies or environment setup

**Core principle:** Systematic directory selection + data seeding + environment verification = reliable isolation.

**Announce at start:** "I'm using the using-analysis-worktrees skill to set up an isolated workspace."

## Directory Selection Process

Follow this priority order:

### 1. Check Existing Directories

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**If found:** Use that directory. If both exist, `.worktrees` wins.

### 2. Check CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**If preference specified:** Use it without asking.

### 3. Ask User

If no directory exists and no CLAUDE.md preference:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/superpowers/worktrees/<project-name>/ (global location)

Which would you prefer?
```

## Safety Verification

### For Project-Local Directories (.worktrees or worktrees)

**MUST verify directory is ignored before creating worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:**
1. Add appropriate line to .gitignore
2. Commit the change
3. Proceed with worktree creation

### For Global Directory (~/.config/superpowers/worktrees)

No .gitignore verification needed — outside project entirely.

## Creation Steps

### 1. Detect Project Name

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. Create Worktree

```bash
# Determine full path
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.config/superpowers/worktrees/*)
    path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"
    ;;
esac

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. Set Up Environment

Auto-detect and set up the analysis environment:

```bash
# Julia
if [ -f Project.toml ]; then
    julia --project=. -e 'using Pkg; Pkg.instantiate()'
fi

# Python
if [ -f pyproject.toml ]; then
    uv sync 2>/dev/null || pip install -e .
elif [ -f requirements.txt ]; then
    uv pip install -r requirements.txt 2>/dev/null || pip install -r requirements.txt
fi
```

### 4. Seed Data

**Invoke the `worktree-data-sync` skill** to materialize non-git data files in the new worktree:

```bash
python3 "${SKILL_DIR}/../worktree-data-sync/scripts/sync_worktree_data.py" \
    --to "$(pwd)" --mode seed --seed-sync-mode auto
```

This discovers gitignored data files, tracked symlinks, and annotated paths from the main worktree and materializes them in the new worktree (via symlink, copy-on-write, or regular copy depending on the auto mode).

**If data seeding fails:** Report what failed and ask the user whether to proceed without full data or investigate.

### 5. Verify Data Accessible

Check that key data files are accessible (not cloud-only placeholders):

```bash
# Check for Dropbox/iCloud cloud-only files
# On macOS, cloud-only files have the SF_DATALESS flag
for f in $(git ls-files --others --ignored --exclude-standard | head -10); do
    if [ -e "$f" ]; then
        echo "✓ $f accessible"
    else
        echo "✗ $f not accessible (cloud-only?)"
    fi
done
```

**If files are cloud-only:** Warn the user. They may need to download specific files before the analysis can proceed.

### 6. Report Location

```
Worktree ready at <full-path>
Environment: <Julia/Python version>
Data seeded: <N> files/directories materialized
Ready to analyze <topic>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md → Ask user |
| Directory not ignored | Add to .gitignore + commit |
| Data seeding fails | Report + ask |
| Cloud-only files | Warn user |
| No Project.toml/pyproject.toml | Skip environment setup |

## Common Mistakes

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always use `git check-ignore` before creating project-local worktree

### Skipping data seeding

- **Problem:** Analysis fails because data files don't exist in worktree
- **Fix:** Always run worktree-data-sync seed after creating worktree

### Assuming data is accessible

- **Problem:** Cloud storage files may be online-only stubs
- **Fix:** Verify files are actually readable, warn about cloud-only files

### Hardcoding setup commands

- **Problem:** Breaks on projects using different tools
- **Fix:** Auto-detect from project files (Project.toml, pyproject.toml, etc.)

## Red Flags

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Skip data seeding step
- Proceed without verifying data is accessible
- Assume directory location when ambiguous
- Skip CLAUDE.md check

**Always:**
- Follow directory priority: existing > CLAUDE.md > ask
- Verify directory is ignored for project-local
- Seed data after worktree creation
- Verify data accessibility
- Report worktree location and data status

## Integration

**Called by:**
- **planning-workflow** — When the user wants an isolated workspace before plan creation
- **execution-workflow** — Recommended for complex or multi-session analyses
- Any skill needing isolated workspace

**Depends on:**
- **superRA:worktree-data-sync** — REQUIRED for data seeding step

**Pairs with:**
- **merge-workflow** — REQUIRED for cleanup after work complete (final phase of finishing an analysis)
