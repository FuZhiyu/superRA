# Version-Control Setup

Stage 4. **Offer git with what it gives the researcher:** a saved snapshot of every change, the ability to go back to any of them, and the isolated reproduction run. Declined: stop here.

## A project without git

1. **Draft `.gitignore` with the researcher before `git init`.** Propose excluding data, generated outputs, caches, environments, and large binaries, listing each directory with its size (`du -sh`); add `.superra-repro/`, `superRA/superra-dashboard.log`, and `superRA/superra-dashboard.pid`. Ambiguous files — a small hand-curated input, the figures the paper includes — are the researcher's call.
2. **Write a data-handling note** into the project's `CLAUDE.md` / `AGENTS.md`, creating the file if absent: where raw and derived data live, that they are never committed, and how a new copy of the project gets them.
3. **Stop the dashboard** (`./superRA/superra dashboard stop`); `git init` moves its run files.
4. **`git init`, then commit the untouched project as the baseline** with `.gitignore` and the note. Before committing, confirm `git status` lists no data or file over 50 MB.
5. **Commit `superRA/` separately,** per `superRA:using-superra` §Commits, and restart the dashboard.

## A project already in git

- **Check what `.gitignore` misses:** tracked data files, files over 50 MB, and `.superra-repro/`. Report the tracked files, untracking nothing without the researcher; add the `.superra-repro/` line in the `superRA/` commit.
- **Commit `superRA/` on a topic branch,** per `superRA:using-superra` §Commits.
