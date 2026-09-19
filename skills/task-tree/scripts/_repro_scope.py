"""Saved-input boundaries and guards for a frozen build selection."""
from __future__ import annotations

import threading

from _repro import build_graph
from _repro_state import (
    Change, HashCache, ReproStateError, absolute, directory_dep_nodes,
    output_nodes, read_lock, read_run_record, spec_hash, step_nodes,
)


def _owners(graph, path):
    return [(s, out) for s in graph.steps for out in s.outs
            if path == out.path.resolved or path.startswith(out.path.resolved + '/')]


def boundary_inputs(graph, names, paths, cache=None, lock=None, consumers=None):
    """Describe actual consumed files whose registered producers are out of scope."""
    from _repro_acceptance import baseline
    cache = cache if cache is not None else HashCache(paths.cache_file)
    lock = read_lock(paths.lock_file) if lock is None else lock
    names = set(names)
    rows = {}
    baselines = {}
    for step in graph.steps:
        if step.name not in names or (consumers is not None and step.name not in consumers):
            continue
        for dep in step.deps:
            owners = _owners(graph, dep.resolved)
            if not owners:
                continue
            producer, out = max(owners, key=lambda pair: len(pair[1].path.resolved))
            if producer.name in names:
                continue
            key = (dep.logical, dep.resolved, producer.name)
            if key not in rows:
                digest = cache.path_state(absolute(paths.project_root, dep.resolved))
                if producer.name not in baselines:
                    try:
                        baselines[producer.name] = baseline(producer, paths, lock.get(producer.name))
                    except ReproStateError:
                        baselines[producer.name] = {}
                evidence = baselines[producer.name]
                recorded = evidence.get('outputs', {}).get(out.path.logical)
                actual = cache.path_state(absolute(paths.project_root, out.path.resolved)) if recorded else None
                provenance = ('missing' if digest is None else 'unverified' if recorded is None else
                              'matches successful output' if actual == recorded else 'differs from successful output')
                rows[key] = dict(logical=dep.logical, resolved=dep.resolved, producer=producer.name,
                                 task=producer.task_path, digest=digest, provenance=provenance,
                                 sidecar=out.sidecar is not None,
                                 consumers=[], producer_outcome=read_run_record(paths, producer.name).get('outcome'))
            rows[key]['consumers'].append(step.name)
    return list(rows.values())


def check_boundary_receipt(entry, graph, paths, cache, lock, boundary=()):
    """Compare saved input bytes even when ordinary graph tracking uses a sidecar."""
    from _repro_acceptance import identity, lock_state, read_json, receipt_path
    receipt = read_json(receipt_path(paths, entry.step.name), {})
    state = receipt.get('state', {})
    if (not receipt or receipt.get('id') != identity({k: v for k, v in receipt.items() if k != 'id'})
            or {key: state.get(key) for key in ('deps', 'products')} != lock_state(lock)):
        receipt = {}
    recorded = receipt.get('boundary_inputs', [])
    from _repro_acceptance import read_ledger
    accepted = read_ledger(paths)['steps'].get(entry.step.name, {})
    if accepted.get('baseline', {}).get('lock') == lock_state(lock):
        recorded = accepted.get('boundary_inputs', accepted.get('baseline', {}).get('boundary_inputs', recorded))
    entry.boundary_inputs = recorded
    verified_paths = {item['logical'] for item in recorded}
    if lock is not None:
        for item in boundary:
            if item['sidecar'] and item['logical'] not in verified_paths:
                entry.changes.append(Change(item['logical'], 'boundary', 'unverified'))
                if entry.status == 'fresh':
                    entry.status = 'stale'
                    entry.reason = f"saved input {item['logical']} needs a full-byte baseline"
    current_paths = {dep.logical: dep.resolved for dep in entry.step.deps}
    for item in recorded:
        resolved = current_paths.get(item['logical'])
        if resolved is None:
            continue  # Removing a declared dependency already changes the spec.
        current = cache.path_state(absolute(paths.project_root, resolved))
        if current == item['digest']:
            continue
        entry.changes.append(Change(item['logical'], 'boundary', 'missing' if current is None else 'changed'))
        if entry.status == 'fresh':
            entry.status = 'stale'
            entry.reason = f"saved input {item['logical']} {'missing' if current is None else 'changed'}"


def _execution_contract(graph, names):
    """Only selected executable definitions and their artifact ownership matter."""
    contract = {}
    outputs = output_nodes(graph)
    for name in sorted(names):
        step = graph.step(name)
        if step is None:
            contract[name] = None
            continue
        deps, products = step_nodes(step, outputs)
        deps += directory_dep_nodes(graph, step)
        paths = {d.resolved for d in step.deps} | {out.path.resolved for out in step.outs}
        # Also detect another output nested below an output owned by this step.
        ownership = sorted((path, owner.name, owner.task_path, out.path.resolved,
                            out.path.logical, out.sidecar.resolved if out.sidecar else None)
                           for path in paths for owner in graph.steps for out in owner.outs
                           if path == out.path.resolved or path.startswith(out.path.resolved + '/')
                           or out.path.resolved.startswith(path + '/'))
        contract[name] = dict(task=step.task_path, spec=spec_hash(step), deps=sorted(deps),
                              products=sorted(products), ownership=ownership)
    # Duplicate step names can be omitted by the graph parser. Retain those
    # diagnostics when they name a selected step, regardless of declaration order.
    contract['_duplicates'] = sorted(f.message for f in graph.findings
                                    if 'already used' in f.message and any(repr(n) in f.message for n in names))
    return contract


class BuildGuard:
    def __init__(self, graph, root, names, signature=None):
        from _repro_acceptance import source_signature
        self.root, self.names = root, frozenset(names)
        self.signature = source_signature(root) if signature is None else signature
        self.contract = _execution_contract(graph, self.names)
        self.cache = {}
        self.lock = threading.RLock()

    def check(self):
        from _repro_acceptance import source_signature
        with self.lock:
            signature = source_signature(self.root, self.cache)
            if signature == self.signature:
                return
            current = build_graph(self.root)
            updated = _execution_contract(current, self.names)
            changed = [name for name in self.contract if self.contract[name] != updated.get(name)]
            if changed:
                raise ReproStateError('selected execution declarations or configuration changed: '
                                      + ', '.join(changed) + '; retry affected work')
            self.signature = signature
