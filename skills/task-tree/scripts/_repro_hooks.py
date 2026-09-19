"""Optional pytask hooks. Registered only by the runner's engine bridge."""
from pytask import hookimpl
from _pytask.outcomes import Skipped, SkippedAncestorFailed, SkippedUnchanged, WouldBeExecuted

from _repro_acceptance import capture_receipt, check_sources, read_ledger, supersede
from _repro_state import LockEntry, StepStatus, compute_status, read_lock, read_run_record, write_run_record


@hookimpl(tryfirst=True)
def pytask_execute_task_setup(session, task):
    context = task.attributes.get('superra')
    if not context:
        return
    # Preserve engine failure and dry-run cascade decisions before considering reuse.
    if any(m.name in ('skip_ancestor_failed', 'would_be_executed', 'skip', 'skipif') for m in task.markers):
        return
    graph, paths, step = context
    check_sources(graph)
    from _repro_scope import boundary_inputs, check_boundary_receipt
    boundary_status = StepStatus(step)
    boundary = boundary_inputs(graph, graph._execution_names, paths, task.attributes['superra_cache'], consumers={step.name})
    check_boundary_receipt(boundary_status, graph, paths, task.attributes['superra_cache'],
                           session.config.get('_superra_completed', {}).get(step.name)
                           or read_lock(paths.lock_file).get(step.name), boundary)
    if boundary_status.status != 'fresh':
        task.force_pending = True
        task.attributes['superra_retry_required'] = True
        task.markers[:] = [m for m in task.markers if m.name != 'skip_unchanged']
    if task.force_pending:
        if not session.config["dry_run"]:
            task.attributes["superra_attempt"] = True
            supersede(paths, step.name)
        return
    previous = read_lock(paths.lock_file).get(step.name)
    if previous and any(value.startswith('saved-input:') for value in previous.depends_on.values()):
        # Metadata may appear after a scoped build. Reuse its full-byte evidence
        # without rewriting the successful lock into a sidecar-based baseline.
        local = compute_status(graph, paths, targets=[f'{step.task_path or "."}#{step.name}'],
                               cache=task.attributes['superra_cache'],
                               completed_locks=session.config.get('_superra_completed', {})).entry(step.name)
        if local and local.status == 'fresh':
            raise SkippedUnchanged
    ledger = read_ledger(paths)
    if step.name not in ledger['steps']:
        return
    entry = compute_status(
        graph, paths, targets=[f'{step.task_path or "."}#{step.name}'], upstream=True,
        cache=task.attributes['superra_cache'], acceptance_ledger=ledger,
        completed_locks=session.config.get('_superra_completed', {}),
    ).entry(step.name)
    if entry and entry.status == 'fresh' and entry.acceptance:
        raise SkippedUnchanged
    # Invalid sidecar reuse may be invisible to pytask's sidecar hash.
    task.force_pending = True
    task.attributes['superra_retry_required'] = True
    task.markers[:] = [m for m in task.markers if m.name != 'skip_unchanged']
    if not session.config["dry_run"]:
        task.attributes["superra_attempt"] = True
        supersede(paths, step.name)


@hookimpl(wrapper=True)
def pytask_execute_task_teardown(session, task):
    result = yield
    context = task.attributes.get('superra')
    if context:
        graph, paths, step = context
        before = task.attributes.get('superra_before')
        if before is not None:
            check_sources(graph)
            receipt = capture_receipt(graph, step, paths, before)
            # pytask persists its lock only when the build ends. Descendants
            # must see successful work from this session when deciding reuse.
            session.config.setdefault('_superra_completed', {})[step.name] = LockEntry(
                depends_on=receipt['state']['deps'], produces=receipt['state']['products'],
            )
            record = read_run_record(paths, step.name)
            record['outcome'] = 'success'
            write_run_record(paths, step.name, record)
    return result


@hookimpl(tryfirst=True)
def pytask_execute_task_process_report(session, report):
    context = report.task.attributes.get('superra')
    if context and report.exc_info and not isinstance(report.exc_info[1], (Skipped, SkippedAncestorFailed, SkippedUnchanged, WouldBeExecuted)):
        graph, paths, step = context
        record = read_run_record(paths, step.name)
        if record.get('outcome') in ('running', 'pending') or report.task.attributes.get('superra_attempt'):
            record['outcome'] = 'failed'
            if report.task.attributes.get('superra_attempt'):
                record['forced'] = True
            record['error'] = str(report.exc_info[1])
            write_run_record(paths, step.name, record)
