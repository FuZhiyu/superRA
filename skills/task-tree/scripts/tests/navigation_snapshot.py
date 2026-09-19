"""Capture only dependency metadata for a graph-only browser fixture.

Task bodies, comments, attachments, commands, logs and acceptance prose never
enter the output. File evidence is preserved as logical paths only.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plan_dashboard as dashboard


def capture(source):
    state = dashboard._build_worktree_state('graph-only', source)
    raw = dashboard._repro_graph_payload(state)
    status = dashboard._repro_status_payload(state, 'all')
    dependencies = raw['dependencies']
    graph = {
        'tasks': raw['tasks'],
        'steps': [{
            'name': s['name'], 'task': s['task'], 'tier': s['tier'], 'kind': s['kind'],
            'cmd': '[command omitted from graph-only fixture]',
            'deps': [{'logical': d['logical']} for d in s['deps']],
            'outs': [{'path': {'logical': o['path']['logical']},
                      'sidecar': {'logical': o['sidecar']['logical']} if o.get('sidecar') else None} for o in s['outs']],
        } for s in raw['steps']],
        'step_edges': raw['step_edges'], 'task_edges': raw['task_edges'],
        'dependencies': dependencies, 'findings': raw['findings'], 'external_inputs': [],
    }
    clean_status = {
        'tier': 'all', 'ok': status['ok'], 'summary': status['summary'],
        'findings': status['findings'],
        'steps': [{'name': s['name'], 'status': s['status'], 'reason': s['status'],
                   'duration': s.get('duration'), 'last_run': s.get('last_run')}
                  for s in status['steps']],
    }
    return {'graph': graph, 'status': clean_status}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = capture(args.source.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'steps': len(result['graph']['steps']), 'tasks': len(result['graph']['dependencies']['tasks']),
                      'edges': len(result['graph']['step_edges']), 'fields': sorted(result['graph']['steps'][0])}))
