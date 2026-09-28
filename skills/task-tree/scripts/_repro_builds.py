"""What a step was built on: the `built_on` field of each `repro-lock.json` entry.

`platform` (OS and CPU architecture), and a digest of the optional `env_probe`
stdout, or `probe_error`; the probe text is stored once in the lock's top-level
`probes` table. No host or user name, and no probe line holding an absolute
path. It never decides freshness; `explain` compares it with this machine.
Stdlib only.
"""
from __future__ import annotations

import hashlib
import platform
import re
import subprocess
import threading

PROBE_TIMEOUT = 120
_probe_lock = threading.Lock()
_ABSOLUTE_PATH = re.compile(r'(?<![\w.:/~-])(?:~/|[A-Za-z]:\\|/[\w.@+-]+/)')


def platform_name() -> str:
    return f'{platform.system()} {platform.machine()}'


def run_probe(command, project_root) -> dict:
    """{'probe': digest, 'probe_text': stdout} on success, else {'probe_error': why}."""
    try:
        done = subprocess.run(command, shell=True, cwd=str(project_root), capture_output=True,  # noqa: S602
                              text=True, timeout=PROBE_TIMEOUT, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'probe_error': type(exc).__name__}
    if done.returncode != 0:
        return {'probe_error': f'exit {done.returncode}'}
    text = done.stdout.strip()
    for number, line in enumerate(text.splitlines(), 1):
        if _ABSOLUTE_PATH.search(line):
            return {'probe_error': f'line {number} holds an absolute path', 'refused_line': line}
    return {'probe': probe_digest(text), 'probe_text': text}


def probe_digest(text) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def probe_once(graph, project_root) -> dict:
    """The env_probe result, run at most once per graph (one build or one explain)."""
    with _probe_lock:
        if getattr(graph, '_env_probe_result', None) is None:
            command = graph.config.env_probe
            graph._env_probe_result = run_probe(command, project_root) if command else {}
    return graph._env_probe_result


def built_on(graph, project_root) -> tuple[dict, str | None]:
    """This build's `built_on` field and the probe text the lock stores beside it."""
    probe = probe_once(graph, project_root)
    return ({'platform': platform_name(), **{k: probe[k] for k in ('probe', 'probe_error') if k in probe}},
            probe.get('probe_text'))


def env_dep_nodes(graph) -> list[str]:
    from _repro import _path_ref
    return [_path_ref(raw, graph.config.variables)[0].logical for raw in graph.config.env_deps]


def builder_record(graph, entry) -> dict | None:
    """A lock entry's builder environment: its `built_on` plus the `env_deps` hashes it read."""
    if not entry or not entry.get('built_on'):
        return None
    on, deps = entry['built_on'], entry.get('deps', {})
    return {'platform': on.get('platform'),
            'env': {'deps': {node: deps[node] for node in env_dep_nodes(graph) if node in deps},
                    **{k: on[k] for k in ('probe', 'probe_error') if k in on}}}


def env_here(graph, paths, cache, record) -> dict:
    """This machine's values for the fields *record* carries."""
    from _repro_state import absolute
    here = {'platform': platform_name(), 'env': {'deps': {}}}
    for node in record.get('env', {}).get('deps', {}):
        dep = next((d for s in graph.steps for d in s.deps if d.logical == node), None)
        if dep is not None:
            here['env']['deps'][node] = cache.path_state(absolute(paths.project_root, dep.resolved))
    if {'probe', 'probe_error'} & set(record.get('env', {})):
        here['env'].update(probe_once(graph, paths.project_root))
    return here


def differences(record, here, probes) -> list[str]:
    """Human-readable fields where the builder's environment and this machine's differ.

    *probes* is the `probes` table of the lock *record* came from.
    """
    out = []
    if record.get('platform') != here['platform']:
        out.append(f"platform ({record.get('platform')} there, {here['platform']} here)")
    theirs, ours = record.get('env', {}), here['env']
    for node, value in theirs.get('deps', {}).items():
        if ours['deps'].get(node) != value:
            out.append(node)
    if 'probe' in theirs or 'probe_error' in theirs:
        if theirs.get('probe') != ours.get('probe'):
            text = probes.get(theirs.get('probe')) if theirs.get('probe') else None
            if theirs.get('probe') and text is None:
                out.append('env_probe (text not recorded there)')
            else:
                out.append('env_probe' + _first_difference(text, ours.get('probe_text')))
    return out


def _first_difference(theirs, ours) -> str:
    if theirs is None or ours is None:
        return ' (failed there)' if theirs is None else ' (failed here)'
    a, b = theirs.splitlines(), ours.splitlines()
    for number, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            return f' line {number}: {x.strip()!r} there, {y.strip()!r} here'
    return f' ({len(a)} line(s) there, {len(b)} here)'
