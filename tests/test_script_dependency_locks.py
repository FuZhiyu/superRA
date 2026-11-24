"""Shipped and development commands run with committed dependency locks.

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
COMMAND_SUFFIXES = (".md", ".sh", ".py", ".json", ".yml", ".yaml")
DEV_TREES = ("tests", "docs", "scripts", ".github")
HISTORICAL_DOCS = ("docs/drafts", "docs/plans", "docs/showcase-fixtures")
BLOCK = re.compile(r"^# /// script\n(.*?)^# ///$", re.S | re.M)
REQUIREMENT = re.compile(r"^([A-Za-z0-9._-]+)(?:\[([^\]]*)\])?\s*(.*)$")
FIXED_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
# A global uv option can take a separate shell word as its value.
OPTION_VALUE = r"""(?:"[^"`]*"|'[^'`]*'|[^-\s`;&|'"][^\s`;&|]*)"""
UV_COMMAND = rf"(?<![\w-])uv\s+(?:-[^\s`;&|]+\s+(?:{OPTION_VALUE}\s+)?)*?"
AD_HOC = re.compile(
    UV_COMMAND + r"(?:run\b[^`;&|]*?(?<![\w-])(?:--with(?:-editable|-requirements)?(?![\w-])|-w)"
    r"|tool\s+run\b)|(?<![\w/-])uvx\s+"
)


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


def canonical(
    name: str, extras: list[str] | str | None, specifier: str | None, marker: str | None
) -> tuple:
    if isinstance(extras, str):
        extras = [e.strip() for e in extras.split(",") if e.strip()]
    return (
        re.sub(r"[-_.]+", "-", name).lower(),
        tuple(sorted(extras or ())),
        tuple(sorted(s.strip().replace(" ", "") for s in (specifier or "").split(",") if s.strip())),
        (marker or "").strip().replace('"', "'"),
    )


def declared(requirement: str) -> tuple:
    package, _, marker = requirement.partition(";")
    name, extras, specifier = REQUIREMENT.match(package.strip()).groups()
    return canonical(name, extras, specifier, marker)


SCRIPTS = [
    script
    for script in shipped_files((".py",)) + sorted((ROOT / "tests").rglob("*.py"))
    if script.suffix == ".py" and (metadata(script) or {}).get("dependencies")
]

# Task records and historical documents keep the commands that were run at the time.
DEV_TEXT = [ROOT / name for name in ("CLAUDE.md", "README.md", "RELEASE-NOTES.md")] + sorted(
    p
    for top in DEV_TREES
    for p in (ROOT / top).rglob("*")
    if p.is_file()
    and p.suffix in COMMAND_SUFFIXES
    and p != Path(__file__).resolve()
    and not any(p.is_relative_to(ROOT / directory) for directory in HISTORICAL_DOCS)
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
        canonical(r["name"], r.get("extras"), r.get("specifier"), r.get("marker"))
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


def logical_lines(text: str):
    """Yield (first line number, command) with backslash-continued lines joined."""
    start, parts = 0, []
    for number, line in enumerate(text.splitlines(), 1):
        if not parts:
            start = number
        stripped = line.rstrip()
        continued = stripped.endswith("\\")
        parts.append(stripped[:-1] if continued else stripped)
        if not continued:
            yield start, " ".join(parts)
            parts = []
    if parts:
        yield start, " ".join(parts)


@pytest.mark.parametrize(
    "command",
    [
        "uv run --with package==1.0 python example.py",
        "uv run --with=package==1.0 python example.py",
        "uv run -w package==1.0 python example.py",
        "uv run -wpackage==1.0 python example.py",
        "uv --no-config -q run --with package==1.0 python example.py",
        'uv --directory "working directory" run --with package==1.0 python example.py',
        "uv run --with-editable . python example.py",
        "uv run --with-requirements requirements.txt python example.py",
        "uv tool run --from package==1.0 program",
        "uv --offline tool run --from package==1.0 program",
        "uvx package==1.0",
    ],
)
def test_ad_hoc_detection(command):
    assert AD_HOC.search(command)


@pytest.mark.parametrize(
    "text",
    [
        "Use `uv run --script x.py`. Avoid `--with`.",
        "uv --no-config run --script x.py",
        "uv run --script x.py && other --with argument",
    ],
)
def test_ad_hoc_detection_accepts_locked_commands(text):
    assert not AD_HOC.search(text)


def test_logical_lines_join_continuations():
    text = "\n".join(
        ["uv run --no-project \\", "  --with requests==1.0 \\", "  python x.py", "plain"]
    )
    commands = list(logical_lines(text))
    assert commands == [(1, "uv run --no-project    --with requests==1.0    python x.py"), (4, "plain")]
    assert AD_HOC.search(commands[0][1])


def test_no_ad_hoc_installs():
    violations = []
    for path in shipped_files(COMMAND_SUFFIXES) + DEV_TEXT:
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in logical_lines(text):
            if AD_HOC.search(line):
                violations.append(f"{path.relative_to(ROOT)}:{number}")
    assert not violations, "use uv run --script with a committed lock:\n" + "\n".join(violations)
