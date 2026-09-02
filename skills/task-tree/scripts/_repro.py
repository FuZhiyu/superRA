#!/usr/bin/env python3
"""Reproduction graph model for the task tree.

Turns a task tree into a validated build graph: parse each task's
``## Reproduction`` section and the ``reproduction:`` key of
``superRA/config.yaml``, resolve variables, expand Julia ``include`` closures,
infer step-to-step and task-to-task edges, and report findings.

Stdlib only. This module never executes a build; the runner, the task CLI, the
dashboard, and the reminder hook all consume the graph it returns.

The contract this implements is ``references/task-file-contract.md``
§Reproduction Section.
"""

from __future__ import annotations

import os
import posixpath
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from _task_io import Task, parse_body_sections, walk_plan
from _task_validate import Finding


REPRO_SECTION = "Reproduction"
CONFIG_FILENAME = "config.yaml"
CONFIG_KEY = "reproduction"
CATEGORY = "reproduction"

TIERS = ("canon", "local")
DEFAULT_TIER = "local"
STEP_KINDS = ("build", "check")

SECTION_KEYS = ("tier", "steps")
STEP_KEYS = ("name", "cmd", "runner", "script", "deps", "outs", "kind", "params")
CONFIG_KEYS = ("vars", "runners", "env_deps", "code_roots")

STEP_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VAR_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


# ---------------------------------------------------------------------------
# Bounded YAML subset parser
# ---------------------------------------------------------------------------

class YamlSubsetError(ValueError):
    """Text outside the YAML subset the reproduction contract pins."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        self.message = message
        super().__init__(f"line {line}: {message}" if line else message)


# Rejected value openers, mapped to the construct they start. Pinning them by
# first character is what keeps the subset bounded: anything a reader would have
# to guess at is refused rather than half-parsed.
_REJECTED_OPENERS = {
    "&": "anchors",
    "*": "aliases",
    "!": "tags",
    "|": "literal block scalars",
    ">": "folded block scalars",
    "{": "inline mappings",
    "}": "inline mappings",
    "?": "explicit keys",
    "%": "directives",
    "`": "reserved indicators",
    "@": "reserved indicators",
}

# Implicit scalar typing, matching PyYAML's YAML 1.1 resolvers so the two
# parsers agree on every value, not just on strings. Sexagesimals are the one
# resolver left out — they are unreachable from path, command, and param text.
_NULL_RE = re.compile(r"^(?:~|null|Null|NULL)$")
_BOOL_TRUE = {"yes", "Yes", "YES", "true", "True", "TRUE", "on", "On", "ON"}
_BOOL_FALSE = {"no", "No", "NO", "false", "False", "FALSE", "off", "Off", "OFF"}
_INT_RE = re.compile(
    r"^[-+]?(?:0b[01_]+|0x[0-9a-fA-F_]+|0[0-7_]+|0|[1-9][0-9_]*)$"
)
_FLOAT_RE = re.compile(
    r"^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?"
    r"|[-+]?\.[0-9_]+(?:[eE][-+][0-9]+)?"
    r"|[-+]?\.(?:inf|Inf|INF)"
    r"|\.(?:nan|NaN|NAN))$"
)


def _resolve_plain(raw: str) -> Any:
    """Type a plain (unquoted) scalar the way PyYAML's implicit resolvers do."""
    if _NULL_RE.match(raw):
        return None
    if raw in _BOOL_TRUE:
        return True
    if raw in _BOOL_FALSE:
        return False
    if _INT_RE.match(raw):
        body = raw.replace("_", "")
        sign, digits = (body[0], body[1:]) if body[0] in "+-" else ("+", body)
        if digits.startswith(("0b", "0B")):
            value = int(digits[2:], 2)
        elif digits.startswith(("0x", "0X")):
            value = int(digits[2:], 16)
        elif len(digits) > 1 and digits.startswith("0"):
            value = int(digits, 8)
        else:
            value = int(digits)
        return -value if sign == "-" else value
    if _FLOAT_RE.match(raw):
        body = raw.replace("_", "")
        lowered = body.lower().lstrip("+-")
        if lowered == ".inf":
            return float("-inf") if body.startswith("-") else float("inf")
        if lowered == ".nan":
            return float("nan")
        return float(body)
    return raw


def _unescape_double(inner: str, line: int) -> str:
    escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "0": "\0"}
    out: list[str] = []
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        if i + 1 >= len(inner):
            raise YamlSubsetError("dangling backslash in a double-quoted scalar", line)
        nxt = inner[i + 1]
        if nxt not in escapes:
            raise YamlSubsetError(
                f"unsupported escape '\\{nxt}' in a double-quoted scalar", line
            )
        out.append(escapes[nxt])
        i += 2
    return "".join(out)


def _strip_comment(raw: str, line: int) -> str:
    """Drop a trailing ``#`` comment, honouring quoted spans."""
    quote: str | None = None
    for i, ch in enumerate(raw):
        if quote is not None:
            if ch == "\\" and quote == '"':
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or raw[i - 1] in " \t"):
            return raw[:i]
    if quote is not None:
        raise YamlSubsetError("unterminated quoted scalar", line)
    return raw


def _split_outside_quotes(text: str, sep: str, line: int) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in text:
        if quote is not None:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == sep:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if quote is not None:
        raise YamlSubsetError("unterminated quoted scalar", line)
    parts.append("".join(buf))
    return parts


def _quoted_end(raw: str, quote: str) -> int:
    """Index just past the closing quote of a quoted scalar, or -1."""
    i = 1
    while i < len(raw):
        ch = raw[i]
        if quote == '"' and ch == "\\":
            i += 2
            continue
        if ch == quote:
            if quote == "'" and i + 1 < len(raw) and raw[i + 1] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    return -1


def _parse_scalar(raw: str, line: int, *, flow: bool = False) -> Any:
    raw = raw.strip()
    if not raw:
        return None
    head = raw[0]
    if head in _REJECTED_OPENERS:
        raise YamlSubsetError(
            f"{_REJECTED_OPENERS[head]} are outside the reproduction YAML subset", line
        )
    if head in "\"'":
        end = _quoted_end(raw, head)
        if end < 0:
            raise YamlSubsetError("unterminated quoted scalar", line)
        if raw[end:].strip():
            raise YamlSubsetError("trailing content after a quoted scalar", line)
        inner = raw[1:end - 1]
        return _unescape_double(inner, line) if head == '"' else inner.replace("''", "'")
    if head == "[":
        if flow:
            raise YamlSubsetError("nested inline lists are outside the subset", line)
        if not raw.endswith("]"):
            raise YamlSubsetError("unterminated inline list", line)
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [
            _parse_scalar(item, line, flow=True)
            for item in _split_outside_quotes(inner, ",", line)
        ]
    # An unquoted item of an inline list is a flow scalar, where YAML reserves
    # the flow indicators. A ``${VAR}`` path needs quotes here — PyYAML rejects
    # it otherwise, and the two parsers must agree on every accepted text.
    if flow and any(ch in raw for ch in "{}[],"):
        raise YamlSubsetError(
            f"inline-list item {raw!r} contains a flow indicator; quote it "
            f'(e.g. "{raw}") or use a block list',
            line,
        )
    return _resolve_plain(raw)


@dataclass(frozen=True)
class _Line:
    number: int
    indent: int
    text: str


def _tokenize(text: str) -> list[_Line]:
    lines: list[_Line] = []
    for number, raw in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"), 1):
        stripped = _strip_comment(raw, number).rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if stripped.lstrip(" ").startswith("\t"):
            raise YamlSubsetError("tabs may not indent a line", number)
        lines.append(_Line(number, indent, stripped.strip()))
    return lines


def _is_list_item(text: str) -> bool:
    return text == "-" or text.startswith("- ")


def _split_key(text: str, line: int) -> tuple[str, str] | None:
    """Split ``key: value`` at the first structural colon, or return None."""
    quote: str | None = None
    for i, ch in enumerate(text):
        if quote is not None:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch == ":" and (i + 1 == len(text) or text[i + 1] in " \t"):
            key_raw = text[:i].strip()
            if not key_raw:
                raise YamlSubsetError("mapping key is empty", line)
            key = _parse_scalar(key_raw, line)
            if not isinstance(key, str):
                key = key_raw
            return key, text[i + 1:].strip()
    return None


def _parse_block(lines: list[_Line], start: int, indent: int) -> tuple[Any, int]:
    if _is_list_item(lines[start].text):
        return _parse_list(lines, start, indent)
    return _parse_mapping(lines, start, indent)


def _parse_mapping(lines: list[_Line], start: int, indent: int) -> tuple[dict, int]:
    result: dict = {}
    i = start
    while i < len(lines) and lines[i].indent >= indent:
        line = lines[i]
        if line.indent > indent:
            raise YamlSubsetError("unexpected indentation", line.number)
        split = _split_key(line.text, line.number)
        if split is None:
            raise YamlSubsetError(
                f"expected 'key: value', found {line.text!r}", line.number
            )
        key, value_text = split
        if key in result:
            raise YamlSubsetError(f"duplicate mapping key {key!r}", line.number)
        if value_text:
            result[key] = _parse_scalar(value_text, line.number)
            i += 1
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt is not None and nxt.indent > indent:
            result[key], i = _parse_block(lines, i + 1, nxt.indent)
        elif nxt is not None and nxt.indent == indent and _is_list_item(nxt.text):
            # A block list may sit at its key's own indent.
            result[key], i = _parse_list(lines, i + 1, indent)
        else:
            result[key] = None
            i += 1
    return result, i


def _parse_list(lines: list[_Line], start: int, indent: int) -> tuple[list, int]:
    result: list = []
    i = start
    while i < len(lines) and lines[i].indent == indent:
        line = lines[i]
        if not _is_list_item(line.text):
            break
        body = line.text[1:].strip()
        i += 1
        if not body:
            if i < len(lines) and lines[i].indent > indent:
                item, i = _parse_block(lines, i, lines[i].indent)
                result.append(item)
            else:
                result.append(None)
            continue
        if _split_key(body, line.number) is None:
            result.append(_parse_scalar(body, line.number))
            continue
        # ``- key: value`` opens a mapping whose continuation lines sit at the
        # column the key starts in.
        item_indent = indent + (len(line.text) - len(line.text[1:].lstrip()))
        virtual = [_Line(line.number, item_indent, body)]
        while i < len(lines) and lines[i].indent >= item_indent:
            virtual.append(lines[i])
            i += 1
        item, consumed = _parse_mapping(virtual, 0, item_indent)
        if consumed < len(virtual):
            raise YamlSubsetError("unexpected indentation", virtual[consumed].number)
        result.append(item)
    if i < len(lines) and lines[i].indent > indent:
        raise YamlSubsetError("unexpected indentation", lines[i].number)
    return result, i


def parse_yaml_subset(text: str) -> Any:
    """Parse the bounded YAML subset the reproduction contract pins.

    Accepts block mappings, block lists, inline lists of scalars, plain and
    quoted scalars, and comments. Raises ``YamlSubsetError`` on anchors, tags,
    multi-line scalars, inline mappings, and malformed structure. Scalar typing
    follows PyYAML, so a file this parser accepts reads identically under
    ``yaml.safe_load``.
    """
    lines = _tokenize(text)
    if not lines:
        return None
    base = lines[0].indent
    if any(line.indent < base for line in lines):
        raise YamlSubsetError("inconsistent top-level indentation", lines[0].number)
    value, consumed = _parse_block(lines, 0, base)
    if consumed < len(lines):
        raise YamlSubsetError("unexpected content", lines[consumed].number)
    return value


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^[ \t]*(?P<marker>```+|~~~+)[ \t]*(?P<info>\S*)[ \t]*$")


def extract_repro_block(section: str) -> str:
    """Return the YAML text of a ``## Reproduction`` section body.

    The body is exactly one fenced ``yaml`` block. Prose outside the fence is a
    contract violation and raises ``YamlSubsetError``.
    """
    inner: list[str] | None = None
    closed = False
    collecting = False
    for number, line in enumerate(section.split("\n"), 1):
        fence = _FENCE_RE.match(line)
        if fence and not collecting:
            if closed:
                raise YamlSubsetError(
                    "a Reproduction section holds exactly one fenced yaml block", number
                )
            if fence.group("info") != "yaml":
                raise YamlSubsetError(
                    f"the fence must be ```yaml, found {fence.group('info') or '(none)'!r}",
                    number,
                )
            collecting = True
            inner = []
            continue
        if fence and collecting:
            collecting = False
            closed = True
            continue
        if collecting:
            inner.append(line)
        elif line.strip():
            raise YamlSubsetError(
                "prose outside the fenced yaml block is not allowed in a "
                "Reproduction section",
                number,
            )
    if collecting:
        raise YamlSubsetError("the fenced yaml block is never closed")
    if inner is None:
        raise YamlSubsetError("the section body must be one fenced yaml block")
    return "\n".join(inner)


# ---------------------------------------------------------------------------
# Graph data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PathRef:
    """A graph node path in both forms.

    ``logical`` keeps the ``${VAR}`` spelling and is the node id, so a lock file
    written from one checkout does not embed its author or branch. ``resolved``
    is what the runner hashes.
    """

    logical: str
    resolved: str

    def to_dict(self) -> dict:
        return {"logical": self.logical, "resolved": self.resolved}


@dataclass(frozen=True)
class Out:
    """A declared output, with the optional sidecar the runner hashes instead."""

    path: PathRef
    sidecar: PathRef | None = None

    def to_dict(self) -> dict:
        return {
            "path": self.path.to_dict(),
            "sidecar": self.sidecar.to_dict() if self.sidecar else None,
        }


@dataclass
class Step:
    """One build unit: a command, the files it reads, and the files it writes."""

    name: str
    task_path: str
    tier: str = DEFAULT_TIER
    kind: str = "build"
    cmd: str = ""
    cmd_logical: str = ""
    runner: str | None = None
    script: PathRef | None = None
    declared_deps: list[PathRef] = field(default_factory=list)
    deps: list[PathRef] = field(default_factory=list)
    outs: list[Out] = field(default_factory=list)
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "task": self.task_path,
            "tier": self.tier,
            "kind": self.kind,
            "cmd": self.cmd,
            "cmd_logical": self.cmd_logical,
            "runner": self.runner,
            "script": self.script.to_dict() if self.script else None,
            "declared_deps": [d.to_dict() for d in self.declared_deps],
            "deps": [d.to_dict() for d in self.deps],
            "outs": [o.to_dict() for o in self.outs],
            "params": self.params,
        }


@dataclass
class ReproConfig:
    """Project-wide reproduction config from ``superRA/config.yaml``."""

    variables: dict[str, str] = field(default_factory=dict)
    runners: dict[str, str] = field(default_factory=dict)
    env_deps: list[str] = field(default_factory=list)
    code_roots: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "vars": dict(self.variables),
            "runners": dict(self.runners),
            "env_deps": list(self.env_deps),
            "code_roots": list(self.code_roots),
        }


@dataclass
class ExternalInput:
    """A dep at the graph boundary: read by a step, produced by none."""

    path: PathRef
    consumers: list[str]
    exists: bool

    def to_dict(self) -> dict:
        return {
            **self.path.to_dict(),
            "consumers": list(self.consumers),
            "exists": self.exists,
        }


@dataclass
class Graph:
    """The whole reproduction graph plus the findings its construction raised."""

    config: ReproConfig = field(default_factory=ReproConfig)
    steps: list[Step] = field(default_factory=list)
    tiers: dict[str, str] = field(default_factory=dict)          # task path -> tier
    producers: dict[str, str] = field(default_factory=dict)      # resolved out -> step
    step_edges: list[tuple[str, str, str]] = field(default_factory=list)
    task_edges: list[tuple[str, str]] = field(default_factory=list)
    external_inputs: list[ExternalInput] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def step(self, name: str) -> Step | None:
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def steps_for(self, task_path: str) -> list[Step]:
        return [s for s in self.steps if s.task_path == task_path]


def graph_to_dict(graph: Graph) -> dict:
    """Serialize a graph to the JSON shape the CLI and dashboard consume."""
    return {
        "config": graph.config.to_dict(),
        "tasks": [
            {
                "path": path,
                "tier": tier,
                "steps": [s.name for s in graph.steps_for(path)],
            }
            for path, tier in sorted(graph.tiers.items())
        ],
        "steps": [s.to_dict() for s in graph.steps],
        "step_edges": [
            {"from": src, "to": dst, "via": via} for src, dst, via in graph.step_edges
        ],
        "task_edges": [{"from": src, "to": dst} for src, dst in graph.task_edges],
        "external_inputs": [e.to_dict() for e in graph.external_inputs],
        "findings": [f.to_dict() for f in graph.findings],
    }


# ---------------------------------------------------------------------------
# Julia include closures
# ---------------------------------------------------------------------------

_INCLUDE_CALL_RE = re.compile(r"\binclude\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)")
_JULIA_STRING_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"$')


def _julia_source(text: str) -> str:
    """Strip ``#`` line comments so a commented-out include is not followed."""
    return "\n".join(_strip_comment_naive(line) for line in text.split("\n"))


def _strip_comment_naive(line: str) -> str:
    quote: str | None = None
    for i, ch in enumerate(line):
        if quote is not None:
            if ch == "\\":
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#":
            return line[:i]
    return line


def _include_target(arg: str) -> str | None:
    """Resolve one ``include(...)`` argument to a path relative to the includer.

    Returns None when the argument is not a static string literal or a
    ``joinpath`` of ``@__DIR__`` and string literals.
    """
    arg = arg.strip()
    literal = _JULIA_STRING_RE.match(arg)
    if literal:
        return literal.group(1)
    if arg.startswith("joinpath(") and arg.endswith(")"):
        segments: list[str] = []
        for part in arg[len("joinpath("):-1].split(","):
            part = part.strip()
            if part == "@__DIR__":
                segments.append(".")
                continue
            piece = _JULIA_STRING_RE.match(part)
            if not piece:
                return None
            segments.append(piece.group(1))
        return posixpath.join(*segments) if segments else None
    return None


def include_closure(
    entry: Path, project_root: Path
) -> tuple[list[str], list[str]]:
    """Return (transitive included files, warnings) for a Julia entry point.

    Paths come back project-root-relative and POSIX-separated, sorted, and
    exclude *entry* itself. An ``include`` whose argument is not statically
    resolvable, or whose target is missing on disk, is reported as a warning
    rather than dropped silently.
    """
    found: list[str] = []
    warnings_out: list[str] = []
    seen: set[Path] = set()
    pending = [entry]
    while pending:
        current = pending.pop()
        try:
            resolved = current.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        try:
            text = current.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in _INCLUDE_CALL_RE.finditer(_julia_source(text)):
            arg = match.group(1)
            target = _include_target(arg)
            if target is None:
                warnings_out.append(
                    f"{_relative(current, project_root)}: "
                    f"include({arg.strip()}) is not a static path; declare it "
                    f"as a dep if the step reads it"
                )
                continue
            child = (current.parent / target).resolve()
            rel = _relative(child, project_root)
            if not child.is_file():
                warnings_out.append(
                    f"{_relative(current, project_root)}: include target {rel} "
                    f"does not exist"
                )
                continue
            if child not in seen:
                found.append(rel)
                pending.append(child)
    return sorted(set(found)), warnings_out


def _relative(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

ShellRunner = Callable[[str, Path], str]


def _default_shell_runner(command: str, cwd: Path) -> str:
    completed = subprocess.run(
        command, shell=True, cwd=str(cwd), capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"exit {completed.returncode}")
    return completed.stdout.strip()


def resolve_variables(
    raw: Any,
    project_root: Path,
    *,
    env: dict[str, str] | None = None,
    shell_runner: ShellRunner | None = None,
) -> tuple[dict[str, str], list[str]]:
    """Evaluate the ``vars`` mapping once, returning (values, error messages).

    Each entry is a literal scalar, ``env: NAME``, or ``shell: "…"``.
    """
    env = os.environ if env is None else env
    run_shell = shell_runner or _default_shell_runner
    values: dict[str, str] = {}
    errors: list[str] = []
    if raw is None:
        return values, errors
    if not isinstance(raw, dict):
        return values, ["config 'vars' must be a mapping of names to values"]
    for name, spec in raw.items():
        if isinstance(spec, dict):
            if set(spec) == {"env"}:
                var_name = str(spec["env"])
                if var_name not in env:
                    errors.append(
                        f"variable {name!r} reads environment variable "
                        f"{var_name!r}, which is not set"
                    )
                    continue
                values[name] = env[var_name]
            elif set(spec) == {"shell"}:
                try:
                    values[name] = run_shell(str(spec["shell"]), project_root)
                except Exception as exc:  # noqa: BLE001 - reported as a finding
                    errors.append(f"variable {name!r} shell command failed: {exc}")
            else:
                errors.append(
                    f"variable {name!r} must be a literal, 'env: NAME', or "
                    f"'shell: \"…\"'"
                )
        elif spec is None:
            values[name] = ""
        else:
            values[name] = str(spec)
    return values, errors


def interpolate(text: str, variables: dict[str, str]) -> tuple[str, list[str]]:
    """Substitute ``${VAR}`` references, returning (text, unknown names)."""
    unknown: list[str] = []

    def _sub(match: re.Match) -> str:
        name = match.group(1)
        if name in variables:
            return variables[name]
        unknown.append(name)
        return match.group(0)

    return VAR_REF_RE.sub(_sub, text), unknown


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def config_path(plan_root: Path) -> Path:
    return plan_root / CONFIG_FILENAME


def load_project_config(plan_root: Path) -> tuple[dict, list[str]]:
    """Return (the ``reproduction:`` mapping, error messages) from config.yaml.

    A missing file is not an error: a tree with no config still has a graph.
    """
    path = config_path(plan_root)
    if not path.is_file():
        return {}, []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, [f"{CONFIG_FILENAME} could not be read: {exc}"]
    try:
        document = parse_yaml_subset(text)
    except YamlSubsetError as exc:
        return {}, [f"{CONFIG_FILENAME}: {exc}"]
    if document is None:
        return {}, []
    if not isinstance(document, dict):
        return {}, [f"{CONFIG_FILENAME} must be a mapping of concern keys"]
    section = document.get(CONFIG_KEY)
    if section is None:
        return {}, []
    if not isinstance(section, dict):
        return {}, [f"{CONFIG_FILENAME}: '{CONFIG_KEY}' must be a mapping"]
    errors = [
        f"{CONFIG_FILENAME}: unknown '{CONFIG_KEY}' key {key!r}; "
        f"expected one of {list(CONFIG_KEYS)}"
        for key in section
        if key not in CONFIG_KEYS
    ]
    return section, errors


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    return [str(value)]


# ---------------------------------------------------------------------------
# Step construction
# ---------------------------------------------------------------------------

def _norm(path: str) -> str:
    return posixpath.normpath(path.strip()) if path.strip() else path


def _path_ref(raw: str, variables: dict[str, str]) -> tuple[PathRef, list[str]]:
    resolved, unknown = interpolate(raw, variables)
    return PathRef(logical=_norm(raw), resolved=_norm(resolved)), unknown


class _StepError(ValueError):
    """A step definition that cannot be turned into a graph node."""


def _build_step(
    raw: Any,
    task_path: str,
    tier: str,
    config: ReproConfig,
    project_root: Path,
    warn: Callable[[str], None],
) -> Step:
    if not isinstance(raw, dict):
        raise _StepError("each entry of 'steps' must be a mapping")
    unknown_keys = [k for k in raw if k not in STEP_KEYS]
    if unknown_keys:
        raise _StepError(
            f"unknown step key {unknown_keys[0]!r}; expected one of {list(STEP_KEYS)}"
        )

    name = raw.get("name")
    if not isinstance(name, str) or not STEP_NAME_RE.match(name):
        raise _StepError(f"step 'name' must be a slug, found {name!r}")

    kind = raw.get("kind") or "build"
    if kind not in STEP_KINDS:
        raise _StepError(f"step {name!r} has kind {kind!r}; expected one of {list(STEP_KINDS)}")

    variables = config.variables
    unknown_vars: list[str] = []
    step = Step(name=name, task_path=task_path, tier=tier, kind=kind)

    has_cmd = raw.get("cmd") is not None
    has_runner = raw.get("runner") is not None
    if has_cmd == has_runner:
        raise _StepError(
            f"step {name!r} must declare either 'cmd' or 'runner' + 'script'"
        )

    if has_cmd:
        step.cmd_logical = str(raw["cmd"])
    else:
        runner = str(raw["runner"])
        script = raw.get("script")
        if not isinstance(script, str) or not script.strip():
            raise _StepError(f"step {name!r} declares 'runner' without a 'script'")
        template = config.runners.get(runner)
        if template is None:
            raise _StepError(
                f"step {name!r} names runner {runner!r}, which config.yaml does not define"
            )
        if "{script}" not in template:
            raise _StepError(
                f"runner template {runner!r} must contain '{{script}}'"
            )
        step.runner = runner
        script_ref, unknown = _path_ref(script, variables)
        unknown_vars += unknown
        step.script = script_ref
        step.cmd_logical = template.replace("{script}", script_ref.logical)

    step.cmd, unknown = interpolate(step.cmd_logical, variables)
    unknown_vars += unknown

    params = raw.get("params")
    if params is not None:
        if not isinstance(params, dict) or any(
            isinstance(v, (dict, list)) for v in params.values()
        ):
            raise _StepError(f"step {name!r} 'params' must be a flat mapping")
        step.params = params

    for entry in _step_path_entries(raw.get("deps"), name, "deps"):
        if not isinstance(entry, str):
            raise _StepError(f"step {name!r} 'deps' entries must be paths")
        ref, unknown = _path_ref(entry, variables)
        unknown_vars += unknown
        step.declared_deps.append(ref)

    outs_raw = _step_path_entries(raw.get("outs"), name, "outs")
    if kind == "check" and outs_raw:
        raise _StepError(
            f"check step {name!r} declares outs; a check step records a stamp, "
            f"not a product"
        )
    for entry in outs_raw:
        if isinstance(entry, str):
            ref, unknown = _path_ref(entry, variables)
            unknown_vars += unknown
            step.outs.append(Out(path=ref))
            continue
        if not isinstance(entry, dict) or set(entry) - {"path", "sidecar"} or "path" not in entry:
            raise _StepError(
                f"step {name!r} 'outs' entries are a path, or 'path:' with an "
                f"optional 'sidecar:'"
            )
        ref, unknown = _path_ref(str(entry["path"]), variables)
        unknown_vars += unknown
        sidecar = None
        if entry.get("sidecar") is not None:
            sidecar, unknown = _path_ref(str(entry["sidecar"]), variables)
            unknown_vars += unknown
        step.outs.append(Out(path=ref, sidecar=sidecar))

    if unknown_vars:
        missing = ", ".join(f"${{{v}}}" for v in sorted(set(unknown_vars)))
        raise _StepError(
            f"step {name!r} references unknown variable {missing}; "
            f"define it under reproduction.vars in {CONFIG_FILENAME}"
        )

    step.deps = _expand_deps(step, config, project_root, warn)
    return step


def _step_path_entries(value: Any, name: str, key: str) -> list:
    if value is None:
        return []
    if not isinstance(value, list):
        raise _StepError(f"step {name!r} '{key}' must be a list")
    return value


def _expand_deps(
    step: Step,
    config: ReproConfig,
    project_root: Path,
    warn: Callable[[str], None],
) -> list[PathRef]:
    """Declared deps + the script + Julia include closures + config env deps."""
    ordered: list[PathRef] = []
    seen: set[str] = set()

    def _add(ref: PathRef) -> None:
        if ref.logical not in seen:
            seen.add(ref.logical)
            ordered.append(ref)

    if step.script is not None:
        _add(step.script)
    for ref in step.declared_deps:
        _add(ref)

    for ref in list(ordered):
        if not ref.resolved.endswith(".jl"):
            continue
        entry = project_root / ref.resolved
        if not entry.is_file():
            continue
        included, include_warnings = include_closure(entry, project_root)
        for message in include_warnings:
            warn(f"step {step.name!r}: {message}")
        for rel in included:
            _add(PathRef(logical=rel, resolved=rel))

    for raw in config.env_deps:
        _add(PathRef(logical=_norm(raw), resolved=_norm(raw)))
    return ordered


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_graph(
    plan_root: Path,
    *,
    project_root: Path | None = None,
    root: Task | None = None,
    env: dict[str, str] | None = None,
    shell_runner: ShellRunner | None = None,
) -> Graph:
    """Parse the tree into a validated reproduction graph.

    Every problem becomes a ``Finding`` on the returned graph; the walk never
    raises, so a partially broken tree still yields the steps that do parse.
    """
    plan_root = Path(plan_root)
    project_root = Path(project_root) if project_root else plan_root.resolve().parent
    tree = root if root is not None else walk_plan(plan_root)

    graph = Graph()
    findings = graph.findings

    def _finding(task_path: str, severity: str, message: str) -> None:
        findings.append(
            Finding(
                task_path=task_path, category=CATEGORY, severity=severity, message=message
            )
        )

    raw_config, config_errors = load_project_config(plan_root)
    for message in config_errors:
        _finding("", "error", message)
    variables, var_errors = resolve_variables(
        raw_config.get("vars"), project_root, env=env, shell_runner=shell_runner
    )
    for message in var_errors:
        _finding("", "error", f"{CONFIG_FILENAME}: {message}")
    runners = raw_config.get("runners") or {}
    if not isinstance(runners, dict):
        _finding("", "error", f"{CONFIG_FILENAME}: 'runners' must be a mapping")
        runners = {}
    graph.config = ReproConfig(
        variables=variables,
        runners={str(k): str(v) for k, v in runners.items()},
        env_deps=[_norm(p) for p in _string_list(raw_config.get("env_deps"))],
        code_roots=[_norm(p) for p in _string_list(raw_config.get("code_roots"))],
    )

    tasks = _iter_tasks(tree)
    step_names: dict[str, str] = {}

    for task in tasks:
        section = parse_body_sections(task.body).get(REPRO_SECTION)
        if section is None:
            continue
        try:
            document = parse_yaml_subset(extract_repro_block(section))
        except YamlSubsetError as exc:
            _finding(task.path, "error", f"## {REPRO_SECTION}: {exc}")
            continue
        if document is None:
            document = {}
        if not isinstance(document, dict):
            _finding(
                task.path, "error", f"## {REPRO_SECTION}: the block must be a mapping"
            )
            continue
        for key in document:
            if key not in SECTION_KEYS:
                _finding(
                    task.path,
                    "error",
                    f"## {REPRO_SECTION}: unknown key {key!r}; "
                    f"expected one of {list(SECTION_KEYS)}",
                )
        tier = document.get("tier") or DEFAULT_TIER
        if tier not in TIERS:
            _finding(
                task.path,
                "error",
                f"## {REPRO_SECTION}: tier {tier!r}; expected one of {list(TIERS)}",
            )
            tier = DEFAULT_TIER
        graph.tiers[task.path] = tier

        raw_steps = document.get("steps") or []
        if not isinstance(raw_steps, list):
            _finding(task.path, "error", f"## {REPRO_SECTION}: 'steps' must be a list")
            continue
        for raw_step in raw_steps:
            try:
                step = _build_step(
                    raw_step,
                    task.path,
                    tier,
                    graph.config,
                    project_root,
                    lambda message, path=task.path: _finding(path, "warning", message),
                )
            except _StepError as exc:
                _finding(task.path, "error", f"## {REPRO_SECTION}: {exc}")
                continue
            owner = step_names.get(step.name)
            if owner is not None:
                _finding(
                    task.path,
                    "error",
                    f"step name {step.name!r} is already used by task "
                    f"{owner or '(root)'}; step names are unique across the tree",
                )
                continue
            step_names[step.name] = task.path
            graph.steps.append(step)

    _link(graph, project_root)
    _check_task_edges(graph, tree)
    return graph


def _iter_tasks(task: Task) -> list[Task]:
    collected = [task]
    for child in task.children:
        collected.extend(_iter_tasks(child))
    return collected


def _link(graph: Graph, project_root: Path) -> None:
    """Infer step edges from out/dep matching and classify boundary inputs."""
    findings = graph.findings

    for step in graph.steps:
        for out in step.outs:
            owner = graph.producers.get(out.path.resolved)
            if owner is not None:
                findings.append(
                    Finding(
                        task_path=step.task_path,
                        category=CATEGORY,
                        severity="error",
                        message=(
                            f"out {out.path.logical} is declared by both step "
                            f"{owner!r} and step {step.name!r}; one step owns each out"
                        ),
                    )
                )
                continue
            graph.producers[out.path.resolved] = step.name

    producer_paths = sorted(graph.producers, key=len, reverse=True)
    externals: dict[str, ExternalInput] = {}
    edges: set[tuple[str, str, str]] = set()

    for step in graph.steps:
        for dep in step.deps:
            producer = _producing_step(dep.resolved, producer_paths, graph.producers)
            if producer is not None:
                if producer != step.name:
                    edges.add((producer, step.name, dep.logical))
                continue
            exists = (project_root / dep.resolved).exists()
            entry = externals.get(dep.logical)
            if entry is None:
                externals[dep.logical] = ExternalInput(
                    path=dep, consumers=[step.name], exists=exists
                )
            elif step.name not in entry.consumers:
                entry.consumers.append(step.name)
            if not exists:
                findings.append(
                    Finding(
                        task_path=step.task_path,
                        category=CATEGORY,
                        severity="warning",
                        message=(
                            f"step {step.name!r} depends on {dep.logical}, which no "
                            f"step produces and which is not on disk"
                        ),
                    )
                )

    graph.step_edges = sorted(edges)
    graph.external_inputs = [externals[key] for key in sorted(externals)]

    owner = {s.name: s.task_path for s in graph.steps}
    graph.task_edges = sorted(
        {
            (owner[src], owner[dst])
            for src, dst, _ in graph.step_edges
            if owner[src] != owner[dst]
        }
    )


def _producing_step(
    dep: str, producer_paths: list[str], producers: dict[str, str]
) -> str | None:
    """Match a dep to its producer, treating a directory out as its whole subtree."""
    if dep in producers:
        return producers[dep]
    for out in producer_paths:
        if dep.startswith(out + "/"):
            return producers[out]
    return None


def _check_task_edges(graph: Graph, root: Task) -> None:
    """Warn when data flows against the declared sibling ``depends_on`` order."""
    parents: dict[str, str] = {}
    siblings: dict[str, list[str]] = {}
    deps: dict[str, list[str]] = {}

    def _walk(task: Task) -> None:
        child_paths = [c.path for c in task.children]
        for child in task.children:
            parents[child.path] = task.path
            siblings[child.path] = child_paths
            deps[child.path] = [
                f"{task.path}/{d}".lstrip("/") for d in child.depends_on
            ]
            _walk(child)

    _walk(root)

    for producer_task, consumer_task in graph.task_edges:
        pair = _sibling_pair(producer_task, consumer_task, parents)
        if pair is None:
            continue
        producer_side, consumer_side = pair
        if _declares_dependency(producer_side, consumer_side, deps):
            graph.findings.append(
                Finding(
                    task_path=producer_task,
                    category=CATEGORY,
                    severity="warning",
                    message=(
                        f"produces files read by {consumer_task or '(root)'}, but "
                        f"depends_on orders {producer_side.rsplit('/', 1)[-1]!r} "
                        f"after {consumer_side.rsplit('/', 1)[-1]!r}"
                    ),
                )
            )


def _sibling_pair(
    producer: str, consumer: str, parents: dict[str, str]
) -> tuple[str, str] | None:
    """Lift two task paths to the sibling level where ``depends_on`` compares."""
    producer_chain = _ancestry(producer, parents)
    consumer_chain = _ancestry(consumer, parents)
    common = ""
    for a, b in zip(producer_chain, consumer_chain):
        if a != b:
            break
        common = a
    producer_side = _child_of(common, producer_chain)
    consumer_side = _child_of(common, consumer_chain)
    if producer_side is None or consumer_side is None or producer_side == consumer_side:
        return None
    return producer_side, consumer_side


def _ancestry(path: str, parents: dict[str, str]) -> list[str]:
    chain = [path]
    while path in parents:
        path = parents[path]
        chain.append(path)
    return list(reversed(chain))


def _child_of(common: str, chain: list[str]) -> str | None:
    for i, entry in enumerate(chain):
        if entry == common:
            return chain[i + 1] if i + 1 < len(chain) else None
    return None


def _declares_dependency(
    start: str, target: str, deps: dict[str, list[str]]
) -> bool:
    """True when *start* depends on *target*, directly or through siblings."""
    pending = list(deps.get(start, []))
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        pending.extend(deps.get(current, []))
    return False


# ---------------------------------------------------------------------------
# task check entry point
# ---------------------------------------------------------------------------

def check_reproduction(plan_root: Path, root: Task | None = None) -> list[Finding]:
    """Return the ``reproduction`` findings for a tree.

    Never-built outs are runner state, not a finding, so a fresh clone with a
    complete graph checks clean.
    """
    return build_graph(plan_root, root=root).findings
