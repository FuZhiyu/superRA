# /// script
# requires-python = ">=3.11"
# dependencies = ["pytask>=0.6,<0.7", "pytask-parallel", "pyyaml"]
# ///
"""Exercise dependency-guided work and reviewed reuse through the public CLI."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[5]
CLI = REPO / "skills/task-tree/scripts/cli.py"


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def task(root: Path, path: str, body: str = "", *, deps: str = "[]",
         status: str = "not-started") -> None:
    write(root, f"superRA/{path}/task.md",
          f"---\ntitle: {path}\nstatus: {status}\ndepends_on: {deps}\n---\n"
          f"\n## Objective\n\nFixture task.\n{body}")


def run(root: Path, *args: str) -> str:
    if args[0] == "repro":
        argv = ["repro", "--root", str(root / "superRA"), *args[1:]]
    else:
        argv = [*args, "--root", str(root / "superRA")]
    result = subprocess.run([sys.executable, str(CLI), *argv], cwd=root,
                            text=True, capture_output=True)
    assert result.returncode == 0, (argv, result.stdout, result.stderr)
    return result.stdout


def step(name: str, command: str, deps: list[str], outs: list[str] | None) -> str:
    return (f"  - name: {name}\n    cmd: {command}\n    deps: {json.dumps(deps)}\n"
            + ("    kind: check\n" if outs is None
               else f"    outs: {json.dumps(outs)}\n"))


def reproduction(steps: str) -> str:
    return f"\n## Reproduction\n\n```yaml\ntier: required\nsteps:\n{steps}```\n"


def verify(base: Path) -> None:
    logical = base / "logical"
    task(logical, "design")
    task(logical, "analysis", deps="[design]")
    assert [row["path"] for row in json.loads(run(logical, "task", "frontier", "--json"))] == ["design"]
    task(logical, "design", status="approved")
    assert [row["path"] for row in json.loads(run(logical, "task", "frontier", "--json"))] == ["analysis"]

    root = base / "reproduction"
    root.mkdir()
    # Pytask discovers a Git boundary independently of the task-root argument.
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    task(root, "source", reproduction(step("source", "sh Code/a.sh",
         ["Code/a.sh", "Code/shared.sh"], ["output/a.txt"])))
    task(root, "consumer", reproduction(
        step("consumer", "sh Code/b.sh", ["Code/b.sh", "Code/shared.sh", "output/a.txt"], ["output/b.txt"])
        + step("check", "sh Code/check.sh", ["Code/check.sh", "output/b.txt"], None)))
    write(root, "Code/shared.sh", "value() { printf '7\\n'; }\n")
    write(root, "Code/a.sh", "set -eu\n. Code/shared.sh\nmkdir -p output\n"
          "value > output/a.txt\necho source >> events.txt\n")
    write(root, "Code/b.sh", "set -eu\n. Code/shared.sh\n"
          "echo $(($(cat output/a.txt) + $(value))) > output/b.txt\necho consumer >> events.txt\n")
    write(root, "Code/check.sh", 'set -eu\ntest "$(cat output/b.txt)" = 14\necho check >> events.txt\n')
    assert [row["path"] for row in json.loads(run(root, "task", "frontier", "--json"))] == ["source"]
    context = json.loads(run(root, "task", "read", "consumer", "--json"))
    assert [row["path"] for row in context["dependencies"]] == ["source"]
    run(root, "task", "check", "--category", "dependency", "--json")
    run(root, "repro", "build")
    lock = (root / "pytask.lock").read_bytes()
    events = (root / "events.txt").read_text()

    write(root, "Code/shared.sh", (root / "Code/shared.sh").read_text()
          + "# Documentation only: value returns seven.\n")
    impact = json.loads(run(root, "repro", "impact", "Code/shared.sh", "--json"))
    assert {row["step"] for row in impact["direct"]} == {"source", "consumer"}
    baseline = json.loads(run(root, "repro", "explain", "source", "--json"))
    assert "Documentation only" in json.dumps(baseline)
    write(root, "review.md", "Inspected the verified baseline diff and Code/a.sh: only a trailing "
          "comment in shared.sh changed. The sourced value function and its call site remain "
          "identical. Existing source output remains valid. Consumer calculation is reviewed separately.\n")
    args = ["repro", "accept", "source", "--reason", "Helper documentation only",
            "--review", "Code/shared.sh=Only a trailing comment changed; value and its call site are identical",
            "--evidence", "review.md", "--json"]
    proposal = json.loads(run(root, *args))
    run(root, *args, "--apply", proposal["token"])
    assert (root / "pytask.lock").read_bytes() == lock
    assert (root / "events.txt").read_text() == events
    run(root, "repro", "status", "source", "--json")

    # Changed calculation/assertion: equivalence is not established, so execute.
    write(root, "Code/b.sh", (root / "Code/b.sh").read_text().replace("+ $(value)", "+ $(value) + 1"))
    write(root, "Code/check.sh", (root / "Code/check.sh").read_text().replace("= 14", "= 15"))
    run(root, "repro", "build")
    events = (root / "events.txt").read_text().splitlines()
    assert events.count("source") == 1
    assert events.count("consumer") == 2 and events.count("check") == 2
    assert (root / "output/b.txt").read_text().strip() == "15"
    run(root, "repro", "status")
    run(root, "repro", "build", "source", "--force")
    assert (root / "events.txt").read_text().splitlines().count("source") == 2


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix=".workflow-journey-", dir=REPO) as directory:
        verify(Path(directory))
    print("PASS: logical and inferred readiness; shared-helper impact; reviewed reuse; "
          "independent calculation/check execution; routine freshness; forced execution.")
