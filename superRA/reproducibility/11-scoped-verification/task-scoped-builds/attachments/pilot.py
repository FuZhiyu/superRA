"""Exercise an existing registered project in a disposable copy, without analyses."""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[5]
    target = 'reproducibility/04-dashboard-view/scalable-navigation#dashboard-navigation-projection-check'
    records = []
    with tempfile.TemporaryDirectory(prefix='superra-scope-pilot-') as directory:
        root = Path(directory)
        shutil.copytree(repo / 'skills/task-tree/scripts', root / 'skills/task-tree/scripts',
                        ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache', '*.pyc'))
        task = Path('superRA') / target.split('#')[0] / 'task.md'
        destination = root / task
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / task, destination)
        # Keep the existing declaration intact, with neutral grouping ancestors
        # so this bounded pilot does not depend on unrelated task declarations.
        for parent in destination.parents:
            if parent == root:
                break
            if parent != destination.parent:
                (parent / 'task.md').write_text('---\ntitle: Pilot group\nstatus: not-started\ndepends_on: []\n---\n')
        runner = root / 'skills/task-tree/scripts/repro_run.py'

        def run(*arguments):
            started = time.monotonic()
            result = subprocess.run([sys.executable, str(runner), '--root', str(root / 'superRA'), *arguments],
                                    cwd=root, capture_output=True, text=True, timeout=180)
            records.append({'args': list(arguments), 'seconds': round(time.monotonic() - started, 4),
                            'exit_code': result.returncode})
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            return result.stdout

        def evidence():
            return {p.relative_to(root).as_posix(): p.read_bytes()
                    for p in [root / 'pytask.lock', *sorted((root / '.superra-repro/runs').glob('*.json'))]
                    if p.exists()}

        run('build', target)
        initial = evidence()
        assert len(list((root / '.superra-repro/runs').glob('*.json'))) == 1
        status = json.loads(run('status', target, '--json'))
        assert status['ok'] and status['summary']['total'] == 1 and not status['upstream']
        for _ in range(3):
            run('build', target)
            run('status', target, '--json')
        assert evidence() == initial
        run('build', target, '--force', '--dry-run')
        assert evidence() == initial
        run('build', target, '--upstream', '--force')
        assert evidence() != initial
        final = json.loads(run('status', target, '--upstream', '--json'))
        assert final['ok'] and final['summary']['total'] == 1
    warm_build = [r['seconds'] for r in records[2:8] if r['args'][0] == 'build']
    warm_status = [r['seconds'] for r in records[2:8] if r['args'][0] == 'status']
    report = {'project': 'isolated registered superRA task/source copy', 'target': target,
              'coverage': 'One existing registered projection check; no research analyses or browser capture.',
              'selected_steps': [s['name'] for s in final['steps']],
              'unrelated_steps_executed': False, 'unchanged_evidence_preserved': True,
              'dry_run_evidence_preserved': True,
              'warm_build_median_seconds': statistics.median(warm_build),
              'warm_status_median_seconds': statistics.median(warm_status), 'commands': records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
