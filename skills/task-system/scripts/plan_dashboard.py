#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard from a .plan/ directory tree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import walk_plan
from task_query import tree_to_json


DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plan Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
:root {
  --bg: #ffffff; --bg-alt: #f8f9fa; --bg-sidebar: #f0f1f3;
  --text: #1a1a2e; --text-muted: #6c757d; --border: #dee2e6;
  --accent: #0366d6; --accent-hover: #0256b9;
  --status-not-started: #e0e0e0; --status-in-progress: #bbdefb;
  --status-implemented: #fff9c4; --status-revise: #ffcdd2;
  --status-approved: #c8e6c9;
  --status-not-started-text: #333; --status-in-progress-text: #0d47a1;
  --status-implemented-text: #e65100; --status-revise-text: #b71c1c;
  --status-approved-text: #1b5e20;
}
[data-theme="dark"] {
  --bg: #1a1a2e; --bg-alt: #16213e; --bg-sidebar: #0f3460;
  --text: #e0e0e0; --text-muted: #a0a0a0; --border: #333;
  --accent: #58a6ff; --accent-hover: #79b8ff;
  --status-not-started: #444; --status-in-progress: #1a3a5c;
  --status-implemented: #4a3800; --status-revise: #5c1a1a;
  --status-approved: #1a3a1a;
  --status-not-started-text: #ccc; --status-in-progress-text: #90caf9;
  --status-implemented-text: #ffe082; --status-revise-text: #ef9a9a;
  --status-approved-text: #a5d6a7;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; }
.summary-bar { display: flex; align-items: center; gap: 16px; padding: 12px 20px;
  background: var(--bg-alt); border-bottom: 1px solid var(--border); flex-shrink: 0; }
.summary-bar h1 { font-size: 18px; margin-right: auto; }
.summary-stat { font-size: 13px; color: var(--text-muted); }
.summary-stat strong { color: var(--text); }
.controls { display: flex; gap: 8px; align-items: center; }
.controls button, .controls select { padding: 4px 10px; border: 1px solid var(--border);
  border-radius: 4px; background: var(--bg); color: var(--text); cursor: pointer; font-size: 13px; }
.controls button:hover { background: var(--bg-alt); }
.controls button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.main-layout { display: flex; flex: 1; overflow: hidden; }
.sidebar { width: 280px; min-width: 200px; overflow-y: auto; padding: 12px;
  background: var(--bg-sidebar); border-right: 1px solid var(--border); flex-shrink: 0; }
.content { flex: 1; overflow-y: auto; padding: 24px; }
.tree-item { cursor: pointer; padding: 3px 0; user-select: none; }
.tree-item:hover { color: var(--accent); }
.tree-item.selected { font-weight: 600; color: var(--accent); }
.tree-children { margin-left: 16px; }
.tree-toggle { display: inline-block; width: 16px; font-size: 10px; color: var(--text-muted); }
.status-badge { display: inline-block; padding: 1px 6px; border-radius: 10px;
  font-size: 11px; font-weight: 500; margin-left: 6px; }
.status-not-started { background: var(--status-not-started); color: var(--status-not-started-text); }
.status-in-progress { background: var(--status-in-progress); color: var(--status-in-progress-text); }
.status-implemented { background: var(--status-implemented); color: var(--status-implemented-text); }
.status-revise { background: var(--status-revise); color: var(--status-revise-text); }
.status-approved { background: var(--status-approved); color: var(--status-approved-text); }
.task-detail h1 { font-size: 22px; margin-bottom: 8px; }
.task-detail .meta { color: var(--text-muted); font-size: 13px; margin-bottom: 16px; }
.task-detail .meta span { margin-right: 16px; }
.task-detail details { margin: 12px 0; border: 1px solid var(--border); border-radius: 6px; }
.task-detail summary { padding: 8px 12px; cursor: pointer; font-weight: 600;
  background: var(--bg-alt); border-radius: 6px; }
.task-detail .section-body { padding: 12px; }
.task-detail .section-body pre { background: var(--bg-alt); padding: 12px;
  border-radius: 4px; overflow-x: auto; font-size: 13px; }
.task-detail .section-body code { font-size: 13px; }
.task-detail .section-body ul { padding-left: 20px; }
.task-detail .section-body li { margin: 4px 0; }
.task-detail .section-body blockquote { border-left: 3px solid var(--accent);
  padding: 8px 12px; margin: 8px 0; background: var(--bg-alt); }
.kanban { display: flex; gap: 16px; padding: 16px; overflow-x: auto; min-height: 400px; }
.kanban-col { min-width: 220px; flex: 1; background: var(--bg-alt);
  border-radius: 8px; padding: 12px; }
.kanban-col h3 { font-size: 14px; margin-bottom: 12px; padding-bottom: 8px;
  border-bottom: 2px solid var(--border); }
.kanban-card { padding: 10px; margin-bottom: 8px; background: var(--bg);
  border: 1px solid var(--border); border-radius: 6px; cursor: pointer; font-size: 13px; }
.kanban-card:hover { border-color: var(--accent); }
.kanban-card .card-path { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.dag-container { padding: 16px; }
.dag-controls { margin-bottom: 12px; }
.search-box { padding: 6px 10px; border: 1px solid var(--border); border-radius: 4px;
  background: var(--bg); color: var(--text); width: 100%; margin-bottom: 8px; font-size: 13px; }
.hidden { display: none !important; }
</style>
</head>
<body>

<div class="summary-bar">
  <h1 id="plan-title">Plan Dashboard</h1>
  <span class="summary-stat" id="stat-total"></span>
  <span class="summary-stat" id="stat-progress"></span>
  <span class="summary-stat" id="stat-updated"></span>
  <div class="controls">
    <button id="btn-tree" class="active" onclick="showView('tree')">Tree</button>
    <button id="btn-dag" onclick="showView('dag')">DAG</button>
    <button id="btn-kanban" onclick="showView('kanban')">Kanban</button>
    <select id="filter-status" onchange="applyFilters()">
      <option value="">All statuses</option>
      <option value="not-started">Not started</option>
      <option value="in-progress">In progress</option>
      <option value="implemented">Implemented</option>
      <option value="revise">Revise</option>
      <option value="approved">Approved</option>
    </select>
    <button onclick="toggleTheme()" title="Toggle dark/light mode">◑</button>
  </div>
</div>

<div class="main-layout">
  <div class="sidebar" id="sidebar">
    <input type="text" class="search-box" id="search-box" placeholder="Search tasks..." oninput="applyFilters()">
    <div id="tree-root"></div>
  </div>
  <div class="content" id="content">
    <div id="view-detail" class="task-detail"></div>
    <div id="view-dag" class="dag-container hidden"></div>
    <div id="view-kanban" class="kanban hidden"></div>
  </div>
</div>

<script>
const TASK_DATA = __TASK_DATA_JSON__;
const md = window.markdownit({ html: true, linkify: true });
let currentView = 'tree';
let selectedPath = '';
const taskByPath = {};

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function sanitizeMermaid(s) { return s.replace(/"/g, "'").replace(/[\\[\\](){}]/g, ''); }

function buildIndex(task) { taskByPath[task.path] = task; for (const c of task.children) buildIndex(c); }

function init() {
  document.documentElement.setAttribute('data-theme',
    localStorage.getItem('dashboard-theme') || 'light');
  mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
  buildIndex(TASK_DATA);
  renderSummary();
  renderTree();
  renderKanban();
  selectTask(TASK_DATA);
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('dashboard-theme', next);
}

function showView(view) {
  currentView = view;
  document.querySelectorAll('.controls button').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + view).classList.add('active');
  document.getElementById('view-detail').classList.toggle('hidden', view === 'kanban' || view === 'dag');
  document.getElementById('view-dag').classList.toggle('hidden', view !== 'dag');
  document.getElementById('view-kanban').classList.toggle('hidden', view !== 'kanban');
  document.getElementById('sidebar').classList.toggle('hidden', view === 'kanban');
  if (view === 'dag') renderDag();
}

function renderSummary() {
  const all = flattenTasks(TASK_DATA);
  const leaves = all.filter(t => t.is_leaf);
  const approved = leaves.filter(t => t.effective_status === 'approved').length;
  document.getElementById('plan-title').textContent = TASK_DATA.title || 'Plan Dashboard';
  document.getElementById('stat-total').innerHTML =
    `<strong>${leaves.length}</strong> leaf tasks, <strong>${all.length - leaves.length}</strong> branches`;
  document.getElementById('stat-progress').innerHTML =
    `<strong>${approved}/${leaves.length}</strong> approved`;
  const dates = all.map(t => t.updated).filter(Boolean).sort();
  if (dates.length) document.getElementById('stat-updated').textContent = 'Updated: ' + dates[dates.length - 1];
}

function flattenTasks(task) {
  let result = [task];
  for (const c of task.children) result = result.concat(flattenTasks(c));
  return result;
}

function renderTree() {
  const root = document.getElementById('tree-root');
  root.innerHTML = '';
  for (const child of TASK_DATA.children) {
    root.appendChild(buildTreeNode(child));
  }
}

function buildTreeNode(task) {
  const div = document.createElement('div');
  const item = document.createElement('div');
  item.className = 'tree-item';
  item.dataset.path = task.path;

  const toggle = document.createElement('span');
  toggle.className = 'tree-toggle';
  toggle.textContent = task.children.length ? '▸' : ' ';

  const label = document.createElement('span');
  const name = task.path.split('/').pop() || task.title;
  label.textContent = name + ': ' + (task.title || '');

  const badge = document.createElement('span');
  badge.className = 'status-badge status-' + task.effective_status;
  badge.textContent = task.effective_status;

  if (!task.is_leaf) {
    const approved = task.children.filter(c => c.effective_status === 'approved').length;
    const progress = document.createElement('span');
    progress.className = 'status-badge';
    progress.style.background = 'transparent';
    progress.style.color = 'var(--text-muted)';
    progress.textContent = `${approved}/${task.children.length}`;
    item.appendChild(toggle);
    item.appendChild(label);
    item.appendChild(badge);
    item.appendChild(progress);
  } else {
    item.appendChild(toggle);
    item.appendChild(label);
    item.appendChild(badge);
  }

  item.onclick = (e) => {
    e.stopPropagation();
    if (task.children.length) {
      const children = div.querySelector('.tree-children');
      if (children) {
        children.classList.toggle('hidden');
        toggle.textContent = children.classList.contains('hidden') ? '▸' : '▾';
      }
    }
    selectTask(task);
  };

  div.appendChild(item);

  if (task.children.length) {
    const childrenDiv = document.createElement('div');
    childrenDiv.className = 'tree-children';
    for (const child of task.children) {
      childrenDiv.appendChild(buildTreeNode(child));
    }
    div.appendChild(childrenDiv);
  }

  return div;
}

function selectTask(task) {
  selectedPath = task.path;
  document.querySelectorAll('.tree-item').forEach(el => {
    el.classList.toggle('selected', el.dataset.path === task.path);
  });

  const detail = document.getElementById('view-detail');
  const status = task.effective_status;

  let metaHtml = '';
  if (task.path) metaHtml += `<span>Path: <code>${escapeHtml(task.path)}</code></span>`;
  metaHtml += `<span>Status: <span class="status-badge status-${escapeHtml(status)}">${escapeHtml(status)}</span></span>`;
  if (task.review_status && task.review_status !== '~')
    metaHtml += `<span>Review: ${escapeHtml(task.review_status)}</span>`;
  if (task.integration_status && task.integration_status !== '~')
    metaHtml += `<span>Integration: ${escapeHtml(task.integration_status)}</span>`;
  if (task.depends_on.length)
    metaHtml += `<span>Depends on: ${task.depends_on.map(d => escapeHtml(d)).join(', ')}</span>`;
  if (task.script) metaHtml += `<span>Script: <code>${escapeHtml(task.script)}</code></span>`;
  if (task.tags.length) metaHtml += `<span>Tags: ${task.tags.map(t => escapeHtml(t)).join(', ')}</span>`;

  const bodyHtml = md.render(task.body || '');

  const sections = parseBodySections(task.body || '');
  let sectionsHtml = '';
  for (const sec of sections) {
    const open = (sec.name === 'Steps' || sec.name === 'Results') ? ' open' : '';
    const rendered = md.render(sec.content);
    let summaryExtra = '';
    if (sec.name === 'Steps') {
      const checked = (sec.content.match(/- \\[x\\]/gi) || []).length;
      const total = (sec.content.match(/- \\[[ x]\\]/gi) || []).length;
      if (total) summaryExtra = ` (${checked}/${total})`;
    }
    sectionsHtml += `<details${open}><summary>${sec.name}${summaryExtra}</summary>` +
      `<div class="section-body">${rendered}</div></details>`;
  }

  detail.innerHTML = `<h1>${escapeHtml(task.title || task.path || 'Root')}</h1>` +
    `<div class="meta">${metaHtml}</div>` +
    (sectionsHtml || `<div class="section-body">${bodyHtml}</div>`);
}

function parseBodySections(body) {
  const lines = body.split('\\n');
  const sections = [];
  let current = null;
  for (const line of lines) {
    const match = line.match(/^## (.+)$/);
    if (match) {
      if (current) sections.push(current);
      current = { name: match[1], content: '' };
    } else if (current) {
      current.content += line + '\\n';
    }
  }
  if (current) sections.push(current);
  return sections;
}

function renderKanban() {
  const container = document.getElementById('view-kanban');
  const statuses = ['not-started', 'in-progress', 'implemented', 'revise', 'approved'];
  const labels = {'not-started': 'Not Started', 'in-progress': 'In Progress',
    'implemented': 'Implemented', 'revise': 'Revise', 'approved': 'Approved'};
  const all = flattenTasks(TASK_DATA).filter(t => t.is_leaf && t.path);

  container.innerHTML = '';
  for (const status of statuses) {
    const col = document.createElement('div');
    col.className = 'kanban-col';
    const tasks = all.filter(t => t.effective_status === status);
    col.innerHTML = `<h3>${labels[status]} (${tasks.length})</h3>`;
    for (const task of tasks) {
      const card = document.createElement('div');
      card.className = 'kanban-card';
      card.innerHTML = `<div>${escapeHtml(task.title || task.path)}</div><div class="card-path">${escapeHtml(task.path)}</div>`;
      card.onclick = () => { showView('tree'); selectTask(task); };
      col.appendChild(card);
    }
    container.appendChild(col);
  }
}

async function renderDag() {
  const container = document.getElementById('view-dag');
  const target = selectedPath ? taskByPath[selectedPath] : TASK_DATA;
  const task = target || TASK_DATA;

  if (!task.children.length) {
    container.innerHTML = '<p>No subtasks to visualize.</p>';
    return;
  }

  const statusColors = {
    'not-started': '#e0e0e0', 'in-progress': '#bbdefb',
    'implemented': '#fff9c4', 'revise': '#ffcdd2', 'approved': '#c8e6c9'
  };

  let mermaidCode = 'graph LR\\n';
  for (const child of task.children) {
    const s = child.effective_status;
    const color = statusColors[s] || '#e0e0e0';
    mermaidCode += `    ${child.path.split('/').pop()}["${sanitizeMermaid(child.title || child.path)}"]\\n`;
    mermaidCode += `    style ${child.path.split('/').pop()} fill:${color}\\n`;
  }
  for (const child of task.children) {
    for (const dep of child.depends_on) {
      mermaidCode += `    ${dep} --> ${child.path.split('/').pop()}\\n`;
    }
  }

  container.innerHTML = `<div class="dag-controls">` +
    `<strong>DAG for:</strong> ${escapeHtml(task.title || task.path || 'root')}</div>` +
    `<div class="mermaid">${mermaidCode}</div>`;

  try { await mermaid.run({ nodes: container.querySelectorAll('.mermaid') }); } catch(e) { container.innerHTML += '<p style="color:var(--status-revise-text)">DAG error: ' + escapeHtml(e.message) + '</p>'; }
}

function findTask(task, path) {
  if (task.path === path) return task;
  for (const c of task.children) {
    const found = findTask(c, path);
    if (found) return found;
  }
  return null;
}

function taskMatches(task, status, search) {
  if (status && task.effective_status !== status) return false;
  if (search && !(task.title || '').toLowerCase().includes(search) &&
      !(task.path || '').toLowerCase().includes(search)) return false;
  return true;
}

function anyDescendantMatches(task, status, search) {
  if (taskMatches(task, status, search)) return true;
  for (const c of task.children) {
    if (anyDescendantMatches(c, status, search)) return true;
  }
  return false;
}

function applyFilters() {
  const status = document.getElementById('filter-status').value;
  const search = document.getElementById('search-box').value.toLowerCase();
  document.querySelectorAll('.tree-item').forEach(el => {
    const path = el.dataset.path || '';
    const task = taskByPath[path];
    if (!task) return;
    const visible = anyDescendantMatches(task, status, search);
    el.style.display = visible ? '' : 'none';
  });
}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an HTML dashboard from a .plan/ tree.")
    parser.add_argument("--plan-root", required=True, help="Path to the plan root directory")
    parser.add_argument("--output", default="", help="Output HTML path (default: <plan-root>/dashboard.html)")
    return parser.parse_args(argv)


def generate_dashboard(plan_root: Path, output_path: Path | None = None) -> Path:
    root = walk_plan(plan_root)
    data = tree_to_json(root)

    if output_path is None:
        output_path = plan_root / "dashboard.html"

    data_json = json.dumps(data, indent=2)
    data_json = data_json.replace("<", "\\u003c").replace(">", "\\u003e")
    html = DASHBOARD_HTML.replace("__TASK_DATA_JSON__", data_json)

    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {output_path}")
    return output_path


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = Path(args.plan_root)
    output = Path(args.output) if args.output else None
    generate_dashboard(plan_root, output)


if __name__ == "__main__":
    main()
