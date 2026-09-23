"""The committed build record `repro-builds.json`: what git cannot know about a build.

One entry per step, overwritten at each successful build: `lock_id` (a hash of
the step's lock entry, so a record the lock has moved past is detectable),
`built_at`, `platform` (OS and CPU architecture), and `env` (hashes of the
configured `env_deps` and the stdout of the optional `env_probe`). No host or
user name. Older entries live in git history. Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import threading
import time

BUILDS = 'repro-builds.json'
PROBE_TIMEOUT = 120
_write_lock = threading.Lock()  # parallel builds tear down on threads


def lock_id(depends_on: dict, produces: dict) -> str:
    blob = json.dumps({'depends_on': depends_on, 'produces': produces}, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def platform_name() -> str:
    return f'{platform.system()} {platform.machine()}'


def run_probe(command, project_root) -> dict:
    """{'probe': stdout} on success, else {'probe_error': why}."""
    try:
        done = subprocess.run(command, shell=True, cwd=str(project_root), capture_output=True,  # noqa: S602
                              text=True, timeout=PROBE_TIMEOUT, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'probe_error': type(exc).__name__}
    if done.returncode != 0:
        return {'probe_error': f'exit {done.returncode}'}
    return {'probe': done.stdout.strip()}


def probe_once(graph, project_root) -> dict:
    """The env_probe result, run at most once per graph (one build or one explain)."""
    if not getattr(graph, '_env_probe_result', None):
        command = graph.config.env_probe
        graph._env_probe_result = run_probe(command, project_root) if command else {'probe': None}
    return graph._env_probe_result


def env_dep_nodes(graph) -> list[str]:
    from _repro import _path_ref
    return [_path_ref(raw, graph.config.variables)[0].logical for raw in graph.config.env_deps]


def read_builds(text) -> dict:
    try:
        value = json.loads(text) if text else {}
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


def record_build(graph, step, paths, receipt) -> None:
    """Write the step's entry after a successful build, from the verified receipt."""
    deps = receipt['state']['deps']
    env = {'deps': {node: deps[node] for node in env_dep_nodes(graph) if node in deps}}
    env.update({k: v for k, v in probe_once(graph, paths.project_root).items() if v is not None})
    entry = {'lock_id': lock_id(deps, receipt['state']['products']), 'built_at': time.time(),
             'platform': platform_name(), 'env': env}
    from _repro_acceptance import atomic_json, read_json
    path = paths.project_root / BUILDS
    with _write_lock:
        builds = read_json(path, {})
        builds[step.name] = entry
        atomic_json(path, builds)


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


def differences(record, here) -> list[str]:
    """Human-readable fields where the builder's environment and this machine's differ."""
    out = []
    if record.get('platform') != here['platform']:
        out.append(f"platform ({record.get('platform')} there, {here['platform']} here)")
    theirs, ours = record.get('env', {}), here['env']
    for node, value in theirs.get('deps', {}).items():
        if ours['deps'].get(node) != value:
            out.append(node)
    if 'probe' in theirs or 'probe_error' in theirs:
        if theirs.get('probe') != ours.get('probe'):
            out.append('env_probe' + _first_difference(theirs.get('probe'), ours.get('probe')))
    return out


def _first_difference(theirs, ours) -> str:
    if theirs is None or ours is None:
        return ' (failed there)' if theirs is None else ' (failed here)'
    a, b = theirs.splitlines(), ours.splitlines()
    for number, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            return f' line {number}: {x.strip()!r} there, {y.strip()!r} here'
    return f' ({len(a)} line(s) there, {len(b)} here)'
