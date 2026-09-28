#!/usr/bin/env python3
"""Materialize the two-clone staleness scenario for the diagnosis evaluation.

Usage: python3 two_clone_scenario.py <empty-dir> [--check]

Clone `coauthor/` builds and commits `repro-lock.json`; clone `you/` shares
`output/` through a Dropbox that has synced only part of the coauthor's work.
Prints the path of the clone the evaluated agent works in. Each clone carries
`superRA/superra`, a shim that runs this checkout's task-tree CLI. `--check`
also asserts that `explain .` there reports the causes the grading key expects.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CLI = Path(__file__).resolve().parents[5] / "skills/task-tree/scripts/cli.py"

CONFIG = """\
reproduction:
  vars:
    OUT: output
  runners:
    sh: sh {script}
"""

SHIM = f"""#!/bin/sh
if command -v uv >/dev/null 2>&1; then
  exec uv run --quiet --script "{CLI}" "$@"
fi
exec python3 "{CLI}" "$@"
"""

ENV = {k: v for k, v in os.environ.items() if k != "SUPERRA_REPRO_REEXEC"}  # set when run as a repro step

STYLE = '"""Plot style.\n\nShared colors for every figure.\n"""\nCOLOR = "navy"\n'


def task(title, steps):
    return f"""---
title: "{title}"
status: implemented
depends_on: []
---

## Objective

{title}.

## Reproduction

```yaml
steps:
{steps}```
"""


def step(name, cmd, deps, outs=(), kind=None):
    lines = [f"  - name: {name}"] + ([f"    kind: {kind}"] if kind else [])
    lines += [f"    cmd: {cmd}", "    deps:"] + [f'      - "{d}"' for d in deps]
    if outs:
        lines += ["    outs:"] + [f'      - "{o}"' for o in outs]
    return "\n".join(lines) + "\n"


def emit(name, value):
    return f"mkdir -p output\necho {name} {value} > output/{name}.txt\n"


TASKS = {
    "01-estimation": step("est", "sh Code/est.sh", ["Code/est.sh"], ["${OUT}/est.txt"]),
    "02-paper": step("paper", "sh Code/paper.sh", ["Code/paper.sh", "${OUT}/est.txt"], ["${OUT}/paper.txt"]),
    "03-figure": step("figure", "sh Code/figure.sh", ["Code/figure.sh", "Code/style.py"], ["${OUT}/figure.txt"]),
    "04-panel": step("panel", "sh Code/panel.sh", ["Code/panel.sh"], ["${OUT}/panel.txt"]),
    "05-robustness": step("robust", "sh Code/robust.sh", ["Code/robust.sh"], ["${OUT}/robust.txt"])
    + step("check-robust", "test -s output/robust.txt", ["${OUT}/robust.txt"], kind="check"),
    "06-summary": step("summary", "sh Code/summary.sh", ["Code/summary.sh"], ["${OUT}/summary.txt"]),
}


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(root, *args):
    return subprocess.run(
        ["git", "-c", "user.name=Co Author", "-c", "user.email=coauthor@example.com",
         "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()


def build(root, *targets):
    subprocess.run([str(root / "superRA/superra"), "repro", "build", *targets], cwd=root, env=ENV, check=True,
                   stdout=subprocess.DEVNULL)


def commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)


def main(dest):
    dest = Path(dest).resolve()
    a, b = dest / "coauthor", dest / "you"
    if a.exists() or b.exists():
        sys.exit(f"{dest} already holds a scenario")

    write(a, "superRA/config.yaml", CONFIG)
    write(a, "superRA/superra", SHIM)
    (a / "superRA/superra").chmod(0o755)
    for name, steps in TASKS.items():
        write(a, f"superRA/{name}/task.md", task(name, steps))
    for name in ("est", "panel", "robust", "summary"):
        write(a, f"Code/{name}.sh", emit(name, "v1"))
    write(a, "Code/paper.sh", "{ echo paper; cat output/est.txt; } > output/paper.txt\n")
    write(a, "Code/figure.sh", "mkdir -p output\ncat Code/style.py > /dev/null\necho fig > output/figure.txt\n")
    write(a, "Code/style.py", STYLE)
    write(a, ".gitignore", "output/\n.superra-repro/\n")
    git(a, "init", "-q")
    commit(a, "Initial analysis code")
    build(a, ".")
    commit(a, "Build all results")

    git(dest, "clone", "-q", str(a), str(b))
    shutil.copytree(a / "output", b / "output")  # Dropbox syncs the first build

    # Coauthor: new estimates, a docstring edit, a panel built on a merged branch, new robustness.
    write(a, "Code/est.sh", emit("est", "v2"))
    build(a, ".")
    commit(a, "Update estimation sample")
    write(a, "Code/style.py", STYLE.replace("Shared colors", "Shared colours"))
    commit(a, "Tidy plot style module")
    git(a, "checkout", "-qb", "panel-fix")
    write(a, "Code/panel.sh", emit("panel", "v2"))
    build(a, "04-panel")
    commit(a, "Fix panel construction")
    git(a, "checkout", "-q", "main")
    git(a, "merge", "-q", "--no-ff", "panel-fix", "-m", "Merge branch 'panel-fix'")
    write(a, "Code/robust.sh", emit("robust", "v2"))
    build(a, "05-robustness")
    commit(a, "Rerun robustness")

    # You: pull code and lock; Dropbox has synced only robust.txt; summary.txt was hand-edited here.
    git(b, "pull", "-q", "--no-rebase")
    shutil.copy(a / "output/robust.txt", b / "output/robust.txt")
    write(b, "output/summary.txt", "summary v1 (edited)\n")
    return b


EXPECTED = {  # step -> causes of its rows in `explain .`
    "est": {"other-build"}, "paper": {"input-changed", "other-build"}, "figure": {"input-changed"},
    "panel": {"other-build"}, "summary": {"unknown-output"},
}


def check(b):
    run = subprocess.run([str(b / "superRA/superra"), "repro", "explain", ".", "--json"], cwd=b, env=ENV, check=True,
                         capture_output=True, text=True)
    data = json.loads(run.stdout)
    causes = {}
    for entry in data["steps"]:
        causes.setdefault(entry["name"], set()).update(r["cause"] for r in entry.get("rows", []))
    got = {name: c for name, c in causes.items() if c}
    assert got == EXPECTED, got
    statuses = {e["name"]: (e["status"], e["reason"]) for e in data["steps"]}
    assert statuses["robust"][0] == "fresh", statuses  # synced
    assert statuses["check-robust"][0] == "fresh" and "not run here" in statuses["check-robust"][1], statuses  # passed in the lock

    # The sync-lag rows carry the relation fact diagnosing.md keys on.
    text = subprocess.run([str(b / "superRA/superra"), "repro", "explain", "."], cwd=b, env=ENV, check=True,
                          capture_output=True, text=True).stdout
    for name, node in (("est", "est.txt"), ("paper", "est.txt"), ("paper", "paper.txt"), ("panel", "panel.txt")):
        row = next(line for line in text.splitlines()
                   if line.strip().startswith(f"{name} ") and f"${{OUT}}/{node}" in line)
        current = row.split("; current ", 1)[1]
        assert "; earlier commit, " in current and " behind HEAD)" in current, row


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    if len(args) != 1:
        sys.exit(__doc__)
    clone = main(args[0])
    if "--check" in sys.argv:
        check(clone)
    print(clone)
