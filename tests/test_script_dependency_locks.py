"""Shipped scripts, skill text, and development commands install only pinned packages.

Static and offline: compares each script's inline metadata with its sidecar
lock, so it needs neither uv nor a network. Run from the repo root:

    uv run --script tests/run_tests.py tests/test_script_dependency_locks.py
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SHIPPED = ("skills", "hooks")
BLOCK = re.compile(r"^# /// script\n(.*?)^# ///$", re.S | re.M)
REQUIREMENT = re.compile(r"^([A-Za-z0-9._-]+)(?:\[([^\]]*)\])?\s*(.*)$")
FIXED_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
# `uv run --with <pkg>`, `uv tool run --from <pkg>`, and `uvx <pkg>`.
AD_HOC = re.compile(r"(?:--with(?:=|\s+)|--from(?:=|\s+)|(?<![\w/-])uvx\s+)(['\"]?)([A-Za-z0-9._-]+(?:\[[^\]]*\])?[^\s'\"]*)\1")


def is_test_file(path: Path) -> bool:
    return (
        path.name.startswith("test_")
        or path.name == "conftest.py"
        or "tests" in path.parts
        or "vendor" in path.parts
    )


def shipped_files(suffixes: tuple[str, ...]) -> list[Path]:
    return sorted(
        p
        for top in SHIPPED
        for p in (ROOT / top).rglob("*")
        if p.is_file() and not is_test_file(p.relative_to(ROOT)) and (p.suffix in suffixes or not p.suffix)
    )


def metadata(script: Path) -> dict | None:
    match = BLOCK.search(script.read_text(encoding="utf-8", errors="replace"))
    if not match:
        return None
    body = "\n".join(line[2:] if line.startswith("# ") else line[1:] for line in match.group(1).splitlines())
    return tomllib.loads(body)


def canonical(name: str, extras: list[str] | str | None, specifier: str | None) -> tuple:
    if isinstance(extras, str):
        extras = [e.strip() for e in extras.split(",") if e.strip()]
    return (
        re.sub(r"[-_.]+", "-", name).lower(),
        tuple(sorted(extras or ())),
        tuple(sorted(s.strip().replace(" ", "") for s in (specifier or "").split(",") if s.strip())),
    )


def declared(requirement: str) -> tuple:
    name, extras, specifier = REQUIREMENT.match(requirement.strip()).groups()
    return canonical(name, extras, specifier)


SCRIPTS = [
    p for p in shipped_files((".py",)) if p.suffix == ".py" and (metadata(p) or {}).get("dependencies")
] + [ROOT / "tests" / "run_tests.py"]

# Development text outside the shipped trees. Task records under `superRA/`
# keep the commands that were run at the time.
DEV_TEXT = [ROOT / "CLAUDE.md", ROOT / "README.md"] + sorted(
    p
    for p in (ROOT / "tests").rglob("*")
    if p.is_file() and p.suffix in (".md", ".sh", ".py") and p != Path(__file__).resolve()
) + sorted(p for p in (ROOT / "skills").rglob("*.py") if is_test_file(p.relative_to(ROOT)) and "vendor" not in p.parts)


def test_scripts_with_dependencies_are_found():
    assert SCRIPTS, "no shipped script declares dependencies; the discovery is broken"


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: str(p.relative_to(ROOT)))
def test_script_lock_matches_declared_dependencies(script: Path):
    meta = metadata(script)
    lock_path = script.with_name(script.name + ".lock")
    assert lock_path.is_file(), f"missing lock; run `UV_NO_CONFIG=1 uv lock --script {script.relative_to(ROOT)}`"
    lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))

    locked = {
        canonical(r["name"], r.get("extras"), r.get("specifier"))
        for r in lock.get("manifest", {}).get("requirements", [])
    }
    assert locked == {declared(d) for d in meta["dependencies"]}, "lock is stale; relock the script"
    assert lock.get("requires-python") == meta.get("requires-python")

    # A fixed script-level cutoff outranks a user-level `exclude-newer`, which
    # would otherwise make uv rewrite the lock on every run.
    cutoff = meta.get("tool", {}).get("uv", {}).get("exclude-newer")
    assert cutoff and FIXED_TIMESTAMP.match(cutoff), "script needs a fixed [tool.uv] exclude-newer timestamp"
    options = lock.get("options", {})
    assert options.get("exclude-newer") == cutoff
    assert "exclude-newer-span" not in options, "lock records a user-level relative cutoff"

    for package in lock.get("package", []):
        files = package.get("wheels", []) + ([package["sdist"]] if "sdist" in package else [])
        assert files, f"{package['name']} has no distribution files"
        assert all(f.get("hash", "").startswith("sha256:") for f in files), f"{package['name']} lacks hashes"


def test_ad_hoc_installs_are_pinned():
    unpinned = []
    for path in shipped_files((".md", ".sh", ".py", ".json", ".yml", ".yaml")) + DEV_TEXT:
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if "uv" not in line:
                continue
            for _, package in AD_HOC.findall(line):
                if "==" not in package and not package.startswith(("-", "<", "$", "{")):
                    unpinned.append(f"{path.relative_to(ROOT)}:{number}: {package}")
    assert not unpinned, "unpinned ad hoc installs:\n" + "\n".join(unpinned)
