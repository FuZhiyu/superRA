"""Output cleaners: make a rerun that changes nothing visible reproduce its bytes.

``reproduction.normalize`` in ``superRA/config.yaml`` maps a file glob to a
cleaner, tried in order, first match wins:

- ``builtin:pdf`` — ``normalize_pdf.py`` beside this module, run through uv;
- any other string — a shell command run from the project root, ``{path}``
  replaced by the quoted file path, else the path appended; it rewrites the file
  in place, and a nonzero exit fails the step;
- ``off`` — no cleaner.

A glob without ``/`` matches the file name, one with ``/`` the declared logical
path. The defaults (``*.pdf: builtin:pdf``) follow the configured entries, so
``"*.pdf": off`` turns PDF cleaning off and ``"*": off`` turns every cleaner off.

Steps run with ``SOURCE_DATE_EPOCH`` fixed unless the environment already sets
it. Stdlib only.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
BUILTINS = {"builtin:pdf": SCRIPTS_DIR / "normalize_pdf.py"}
DEFAULT_RULES = {"*.pdf": "builtin:pdf"}
OFF = "off"
SOURCE_DATE_EPOCH = "315532800"  # 1980-01-01, the earliest date ZIP-based formats can store


class CleanerFailed(Exception):
    """A project cleaner command exited nonzero."""


def step_env() -> dict[str, str]:
    """The environment a step and its cleaners run in."""
    env = dict(os.environ)
    env.setdefault("SOURCE_DATE_EPOCH", SOURCE_DATE_EPOCH)
    return env


def rules(configured: dict[str, str]) -> list[tuple[str, str]]:
    return list(configured.items()) + [(g, a) for g, a in DEFAULT_RULES.items() if g not in configured]


def cleaner_for(logical: str, rule_list: list[tuple[str, str]]) -> str | None:
    name = logical.rsplit("/", 1)[-1]
    for pattern, action in rule_list:
        if fnmatch.fnmatchcase(logical if "/" in pattern else name, pattern):
            return None if action == OFF else action
    return None


def config_errors(configured: dict[str, str]) -> list[str]:
    return [f"normalize entry {glob!r}: unknown cleaner {action!r}; expected one of {sorted(BUILTINS)}"
            for glob, action in configured.items() if action.startswith("builtin:") and action not in BUILTINS]


def out_files(logical: str, path: Path) -> list[tuple[str, Path]]:
    """(logical, absolute) for a declared out at *path*: the file itself, or every file under a directory."""
    if path.is_file():
        return [(logical, path)]
    if not path.is_dir():
        return []
    return sorted((f"{logical}/{f.relative_to(path).as_posix()}", f)
                  for f in path.rglob("*") if f.is_file())


@dataclass
class Outcome:
    changed: list[str] = field(default_factory=list)  # logical paths whose bytes the cleaners rewrote
    unchanged: list[str] = field(default_factory=list)
    skipped: dict[str, list[str]] = field(default_factory=dict)  # reason -> logical paths left as written

    def skip(self, reason: str, logical: str) -> None:
        self.skipped.setdefault(reason, []).append(logical)


def clean(files: list[tuple[str, Path]], configured: dict[str, str], project_root: Path) -> Outcome:
    """Apply the matching cleaner to each file in place; raise CleanerFailed on a failing project command."""
    rule_list, outcome, env = rules(configured), Outcome(), step_env()
    by_cleaner: dict[str, list[tuple[str, Path]]] = {}
    for logical, path in files:
        cleaner = cleaner_for(logical, rule_list)
        if cleaner and _online_only(path):
            outcome.skip("online-only; download to clean", logical)
        elif cleaner:
            by_cleaner.setdefault(cleaner, []).append((logical, path))
    for cleaner, group in by_cleaner.items():
        before = {logical: _digest(path) for logical, path in group}
        if cleaner in BUILTINS:
            _run_builtin(cleaner, group, outcome, env)
        else:
            for logical, path in group:
                command = (cleaner.replace("{path}", shlex.quote(str(path))) if "{path}" in cleaner
                           else f"{cleaner} {shlex.quote(str(path))}")
                result = subprocess.run(command, shell=True, cwd=project_root, env=env,  # noqa: S602 - a configured cleaner
                                        capture_output=True, text=True, check=False)
                if result.returncode:
                    tail = (result.stderr or result.stdout).strip().splitlines()[-1:] or [""]
                    raise CleanerFailed(f"cleaner {cleaner!r} exited {result.returncode} on {logical}: {tail[0]}")
        skipped = {p for paths in outcome.skipped.values() for p in paths}
        for logical, path in group:
            if logical in skipped:
                continue
            (outcome.changed if _digest(path) != before[logical] else outcome.unchanged).append(logical)
    return outcome


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _online_only(path: Path) -> bool:
    """Reading this file would download it."""
    from _repro_state import SF_DATALESS, file_flags, has_placeholder_xattr
    info = path.stat()
    return bool(file_flags(info) & SF_DATALESS) or (info.st_size == 0 and has_placeholder_xattr(path))


def _run_builtin(cleaner: str, group: list[tuple[str, Path]], outcome: Outcome, env: dict[str, str]) -> None:
    uv = shutil.which("uv")
    if uv is None:
        for logical, _ in group:
            outcome.skip("uv not found; install uv to clean them", logical)
        return
    result = subprocess.run([uv, "run", "--quiet", "--script", str(BUILTINS[cleaner]), "--json",
                             *(str(path) for _, path in group)],
                            env=env, capture_output=True, text=True, check=False)
    try:
        records = json.loads(result.stdout)
    except ValueError:
        tail = (result.stderr or result.stdout).strip().splitlines()[-1:] or [f"exit {result.returncode}"]
        for logical, _ in group:
            outcome.skip(f"{cleaner} failed: {tail[0]}", logical)
        return
    logical_of = {str(path): logical for logical, path in group}
    for record in records:
        if record["result"] == "skipped":
            outcome.skip(record["reason"], logical_of[record["path"]])
