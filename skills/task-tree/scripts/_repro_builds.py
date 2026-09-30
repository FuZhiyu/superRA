"""What a step was built on: the `built_on` field of each `repro-lock.json` entry.

`platform` — OS and CPU architecture; no host or user name. It never decides
freshness; `explain` compares it, and the builder's `env_deps` hashes, with this
machine. Stdlib only.
"""
from __future__ import annotations

import platform


def platform_name() -> str:
    return f'{platform.system()} {platform.machine()}'


def env_dep_nodes(graph) -> list[str]:
    from _repro import _path_ref
    return [_path_ref(raw, graph.config.variables)[0].logical for raw in graph.config.env_deps]


def builder_record(graph, entry) -> dict | None:
    """A lock entry's builder environment: its platform plus the `env_deps` hashes it read."""
    if not entry or not entry.get('built_on'):
        return None
    deps = entry.get('deps', {})
    return {'platform': entry['built_on'].get('platform'),
            'env': {'deps': {node: deps[node] for node in env_dep_nodes(graph) if node in deps}}}


def env_here(graph, paths, cache, record) -> dict:
    """This machine's values for the fields *record* carries."""
    from _repro_state import absolute
    here = {'platform': platform_name(), 'env': {'deps': {}}}
    for node in record.get('env', {}).get('deps', {}):
        dep = next((d for s in graph.steps for d in s.deps if d.logical == node), None)
        if dep is not None:
            here['env']['deps'][node] = cache.path_state(absolute(paths.project_root, dep.resolved))
    return here


def differences(record, here) -> list[str]:
    """Human-readable fields where the builder's environment and this machine's differ."""
    out = []
    if record.get('platform') != here['platform']:
        out.append(f"platform ({record.get('platform')} there, {here['platform']} here)")
    for node, value in record.get('env', {}).get('deps', {}).items():
        if here['env']['deps'].get(node) != value:
            out.append(node)
    return out
