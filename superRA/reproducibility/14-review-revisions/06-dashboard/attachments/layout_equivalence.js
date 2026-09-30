/* The reformatted reproHierarchyLayout returns the same positions, bands, and
   routes as the one-line original on random nested models.
   node superRA/reproducibility/14-review-revisions/06-dashboard/attachments/layout_equivalence.js */
const fs = require('fs'), path = require('path');
const here = __dirname, dashboard = path.join(here, '../../../../../skills/task-tree/scripts/templates/dashboard.js');
const source = fs.readFileSync(dashboard, 'utf8');
function slice(from, to) { const a = source.indexOf(from); return source.slice(a, source.indexOf(to, a)); }
eval(fs.readFileSync(path.join(here, 'layout_before.js'), 'utf8').replace('function reproHierarchyLayout(', 'function beforeLayout('));
eval(slice('function reproStronglyConnected(', '/* Each node on a cycle'));
eval(slice('function reproHierarchyLayout(', 'function reproEdgeLabel(').replace('function reproHierarchyLayout(', 'function afterLayout('));
let seed = 1;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function makeModel() {
  const nodes = []; let count = 0;
  function build(parent, depth) {
    const n = {id: (rnd() < .5 ? 'task:' : 's') + (count++), type: 'task', parent: parent ? parent.id : null, children: []};
    nodes.push(n);
    if (depth < 3 && rnd() < .4) { const k = 1 + Math.floor(rnd() * 5); for (let i = 0; i < k; i++) n.children.push(build(n, depth + 1)); }
    else if (rnd() < .5) n.type = 'step';
    return n;
  }
  const roots = 1 + Math.floor(rnd() * 8);
  for (let i = 0; i < roots; i++) build(null, 0);
  const edges = [], m = Math.floor(rnd() * nodes.length * 2);
  for (let i = 0; i < m; i++) {
    const a = nodes[Math.floor(rnd() * nodes.length)], b = nodes[Math.floor(rnd() * nodes.length)];
    if (a !== b) edges.push({from: a.id, to: b.id, evidence: [{kind: rnd() < .3 ? 'logical' : 'inferred'}]});
  }
  return {nodes, edges};
}
function clone(m) {
  const byId = {}, nodes = m.nodes.map(n => byId[n.id] = Object.assign({}, n, {children: []}));
  m.nodes.forEach(n => byId[n.id].children = n.children.map(c => byId[c.id]));
  return {nodes, edges: m.edges.map(e => Object.assign({}, e))};
}
function shape(l) {
  return JSON.stringify({pos: l.pos, bands: l.bands, width: l.width, height: l.height,
    edges: l.edges.map(e => ({from: e.from, to: e.to, points: e.points, d: e.d}))});
}
const models = 3000;
for (let t = 0; t < models; t++) {
  const m = makeModel();
  if (shape(beforeLayout(clone(m))) !== shape(afterLayout(clone(m)))) { console.error('layout differs on model ' + t); process.exit(1); }
}
console.log(models + ' random models: identical layouts');
