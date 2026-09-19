"""Topology and geometry contracts for the workspace DAG."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_dashboard import _extract_js_defs

NODE = shutil.which('node')
pytestmark = pytest.mark.skipif(not NODE, reason='Node required')


def run(body):
    definitions = _extract_js_defs(['reproWithin', 'reproRoots', 'reproMatches', 'reproProject',
        'reproHierarchy', 'reproHierarchyLayout', 'reproBranchExpansion', 'reproTasks', 'reproTaskTitle', 'parentPath'])
    source = "const assert=require('node:assert/strict');var pathTitles={};\n" + definitions + '\n' + body
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


FIXTURE = """
var tasks=['p','p/child','p/child/nested','peer','logical'].map(path=>({path,title:'Repeated',status:'in-progress'}));
var steps=[['setup','p','on-demand'],['build','p/child','required'],['nested','p/child/nested','required'],['report','p','required'],['independent','peer','required']].map(([name,task,tier])=>({name,task,tier}));
var edges=[['setup','build'],['build','nested'],['nested','report'],['setup','report']].map(([from,to])=>({from,to,via:from+'.csv'}));
var graph={steps,step_edges:edges,dependencies:{tasks,boundaries:{'':{nodes:['task:p','task:logical','task:peer'],edges:[{from:'task:logical',to:'task:p',evidence:[{kind:'logical',from:'logical',to:'p',declaration:'p depends_on: logical'}]}]}}}};
var nav={roots:[],tier:'all',mode:'scope',anchor:'',expanded:[]};
function model(){return reproHierarchy(graph,nav,reproProject(graph,nav,[]));}
"""


def test_nested_folds_and_logical_evidence():
    run(FIXTURE + """
assert.deepEqual(model().nodes.map(n=>n.id),['task:logical','task:p','task:peer']);
nav.expanded=['p'];var m=model();
assert.deepEqual(m.nodes.map(n=>n.id),['task:logical','task:p','setup','report','task:p/child','task:peer']);
assert(m.edges.some(e=>e.from==='setup'&&e.to==='task:p/child'));
assert(m.edges.some(e=>e.from==='task:p/child'&&e.to==='report'));
assert(!m.edges.some(e=>e.from===e.to));
assert(m.edges.some(e=>e.from==='task:logical'&&e.to==='task:p'&&e.evidence[0].kind==='logical'));
nav.expanded=['p','p/child'];m=model();assert(m.nodes.some(n=>n.id==='task:p/child/nested'));
assert(!m.nodes.some(n=>n.id==='nested'));
nav.expanded=['p/child'];assert(model().nodes.length===3);
nav.expanded.push('p');assert(model().nodes.some(n=>n.id==='build'));
""")


def test_subtree_tier_intersection_trace_and_hidden_edges():
    run(FIXTURE + """
nav.roots=reproRoots(['p/child','p','peer']);assert.deepEqual(nav.roots,['p','peer']);
nav.roots=['p/child'];nav.tier='required';var p=reproProject(graph,nav,[]);
assert.deepEqual(p.matches.map(s=>s.name),['build','nested']);
assert(p.boundary.some(b=>b.hidden==='setup'&&b.reasons.includes('tier')&&b.reasons.includes('subtree')));
nav.mode='upstream';nav.anchor='nested';nav.expanded=['p','p/child','p/child/nested'];p=reproProject(graph,nav,[]);
assert.deepEqual(p.steps.map(s=>s.name),['setup','build','nested']);
assert(!reproWithin('peer-2','peer'));
assert.deepEqual(p.edges.map(e=>[e.from,e.to]),[['setup','build'],['build','nested']]);
nav.expanded=[];assert(model().nodes.some(n=>n.id==='task:p'));
""")


def test_layout_no_overlapping_siblings_and_real_edge_geometry():
    run(FIXTURE + """
nav.expanded=['p','p/child','p/child/nested'];var m=model(),l=reproHierarchyLayout(m);
var again=reproHierarchyLayout(model());assert.deepEqual(l.pos,again.pos);
for(let a of m.nodes)for(let b of m.nodes){if(a.id>=b.id||a.parent!==b.parent)continue;let x=l.pos[a.id],y=l.pos[b.id];assert(x.x+x.width<=y.x||y.x+y.width<=x.x||x.y+x.height<=y.y||y.y+y.height<=x.y,`overlap ${a.id} ${b.id}`);}
function ancestor(a,b){while(b){if(a===b)return true;b=m.nodes.find(n=>n.id===b)?.parent;}return false;}
for(let e of l.edges)for(let n of m.nodes){if(ancestor(n.id,e.from)||ancestor(n.id,e.to))continue;let b=l.pos[n.id];for(let i=1;i<e.points.length;i++){let [x,y]=e.points[i-1],[xx,yy]=e.points[i];assert(x===xx||y===yy,'orthogonal');let hit=x===xx?x>b.x&&x<b.x+b.width&&Math.max(y,yy)>b.y&&Math.min(y,yy)<b.y+b.height:y>b.y&&y<b.y+b.height&&Math.max(x,xx)>b.x&&Math.min(x,xx)<b.x+b.width;assert(!hit,`edge ${e.from} → ${e.to} crosses ${n.id}`);}}
""")


@pytest.mark.parametrize('kind', ['chain', 'fan', 'disconnected', 'cycle'])
def test_shape_visibility_and_cycle_layout_termination(kind):
    run("""
var tasks=Array.from({length:20},(_,i)=>({path:'t'+i,title:'T'+i}));
var steps=tasks.map((t,i)=>({name:'s'+i,task:t.path,tier:'required'}));
var kind=""" + json.dumps(kind) + """,edges=[];
for(let i=1;i<20;i++){if(kind==='chain'||kind==='cycle')edges.push({from:'s'+(i-1),to:'s'+i,via:'f'+i});if(kind==='fan')edges.push({from:'s0',to:'s'+i,via:'f'+i});}
if(kind==='chain')edges.push({from:'s0',to:'s19',via:'shortcut'});
if(kind==='cycle')edges.push({from:'s19',to:'s0',via:'cycle'});
var graph={steps,step_edges:edges,dependencies:{tasks,boundaries:{}}},nav={roots:[],tier:'all',mode:'scope',expanded:tasks.map(t=>t.path)};
var m=reproHierarchy(graph,nav,reproProject(graph,nav,[])),l=reproHierarchyLayout(m);
assert.equal(m.nodes.filter(n=>n.type==='step').length,20);assert.equal(l.edges.length,edges.length);
for(let e of l.edges){assert(e.evidence.length===1);assert(Number.isFinite(l.pos[e.from].x));}
""")


def test_inherited_logical_prerequisites_and_order_independent_closure():
    run("""
var tasks=['a','b','c','c/child'].map(path=>({path,title:path}));
var logical=[{kind:'logical',from:'b',to:'c',declaration:'c depends_on b'},{kind:'logical',from:'a',to:'b',declaration:'b depends_on a'}];
var graph={steps:[{name:'result',task:'c/child',tier:'required'}],step_edges:[],dependencies:{tasks,boundaries:{'':{edges:logical.map(e=>({from:'task:'+e.from,to:'task:'+e.to,evidence:[e]}))}}}};
var nav={roots:['c/child'],tier:'required',mode:'scope',expanded:[]};
var m=reproHierarchy(graph,nav,reproProject(graph,nav,[]));
assert(m.nodes.some(n=>n.id==='task:a'));assert(m.nodes.some(n=>n.id==='task:b'));assert(m.nodes.some(n=>n.id==='task:c/child'));
assert(m.edges.some(e=>e.from==='task:a'&&e.to==='task:b'));
assert(m.logicalBoundary.some(e=>e.from==='b'&&e.to==='c'));
graph.dependencies.boundaries[''].edges.reverse();
var other=reproHierarchy(graph,nav,reproProject(graph,nav,[]));assert.deepEqual(other.nodes.map(n=>n.id),m.nodes.map(n=>n.id));
""")


def test_accepted_step_keeps_fresh_state_and_actual_run_details():
    definitions = _extract_js_defs(['renderReproDetail', 'reproStatusIndex', 'reproStateOf',
        'reproDetailRow', 'reproPathList', 'reproOutLabel', 'reproButton', 'reproDuration',
        'reproTaskTitle', 'reproProject', 'reproMatches', 'reproWithin', 'escapeHtml', 'escapeAttr'])
    script = """
var host={innerHTML:''},document={getElementById:()=>host};
var _reproInspectorClosed=false,pathTitles={},REPRO_GLYPHS={fresh:'●'};
var _reproNav={roots:[],tier:'all',mode:'scope'};
var _reproData={graph:{steps:[{name:'check',task:'report',cmd:'verify',tier:'required',kind:'check',deps:[{logical:'input.csv'}],outs:[],dependency_origins:{'input.csv':[{kind:'declared'}]}}],step_edges:[]},status:{steps:[{name:'check',status:'fresh',reason:'up to date',duration:2,last_run:1700000000,log_tail:'Actual execution log',acceptance:{reason:'Reviewed documentation-only edit',evidence:{'review.md':'digest'}}}]}};
renderReproDetail('check');console.log(host.innerHTML);
"""
    result = subprocess.run([NODE, '-e', definitions + script], text=True, capture_output=True, check=True)
    assert 'fresh' in result.stdout and 'Reviewed documentation-only edit' in result.stdout
    assert 'review.md' in result.stdout and 'Actual execution log' in result.stdout
    assert 'Last run' in result.stdout and 'check step' in result.stdout
    assert 'Declared input' in result.stdout and '[object Object]' not in result.stdout


def test_bounded_branch_expansion_replaces_only_descendants_and_counts_projection():
    run(FIXTURE + """
nav.expanded=['p','p/child','p/child/nested','peer'];
const original=JSON.stringify(nav), plan=depth=>reproBranchExpansion(graph,nav,[],'p',depth);
const one=plan('1'), two=plan('2'), all=plan('all');
assert.equal(one.visible,true);
assert.deepEqual(one.expanded,['peer','p']);
assert.deepEqual(two.expanded,['peer','p','p/child']);
assert.deepEqual([one.tasks+one.steps,two.tasks+two.steps,all.tasks+all.steps],[4,6,7]);
assert.equal(JSON.stringify(nav),original);
nav.expanded=[];
assert.equal(reproBranchExpansion(graph,nav,[],'p/child','2').visible,false);
nav.roots=['p'];
assert.equal(reproBranchExpansion(graph,nav,[],'peer','2').visible,false);
nav.tier='required';
assert.equal(plan('1').steps,1);
nav.mode='upstream';nav.anchor='nested';
assert.equal(plan('all').steps,3); // trace follows the on-demand producer, omits report
assert.equal(nav.anchor,'nested');
""")


ROUTE_GEOMETRY = """
function assertDistinct(l){
 const segments=[];
 for(const [edge,e] of l.edges.entries())for(let j=1;j<e.points.length;j++){
   const a=e.points[j-1],b=e.points[j];assert(a[0]===b[0]||a[1]===b[1]);
   if(a[0]!==b[0]||a[1]!==b[1])segments.push({edge,a,b,h:a[1]===b[1]});
 }
 for(let i=0;i<segments.length;i++)for(let j=i+1;j<segments.length;j++){
   const a=segments[i],b=segments[j];if(a.edge===b.edge||a.h!==b.h)continue;
   const axis=a.h?0:1,fixed=1-axis;
   if(Math.abs(a.a[fixed]-b.a[fixed])>1e-7)continue;
   const overlap=Math.min(Math.max(a.a[axis],a.b[axis]),Math.max(b.a[axis],b.b[axis]))-Math.max(Math.min(a.a[axis],a.b[axis]),Math.min(b.a[axis],b.b[axis]));
   assert(overlap<=1e-7,`Shared route: ${l.edges[a.edge].from} → ${l.edges[a.edge].to} / ${l.edges[b.edge].from} → ${l.edges[b.edge].to}`);
 }
}
"""


def test_cycle_members_have_distinct_ranks_without_absorbing_downstream_nodes():
    run(ROUTE_GEOMETRY + """
const ids=['heterogeneity','treasury','elasticity','paper','downstream','isolated'];
const pairs=[['heterogeneity','treasury'],['heterogeneity','elasticity'],['heterogeneity','paper'],['treasury','paper'],['elasticity','paper'],['paper','heterogeneity'],['paper','downstream']];
const model={nodes:ids.map(id=>({id,type:'task',parent:null,children:[]})),edges:pairs.map(([from,to])=>({from,to,evidence:[{from,to}]}))};
const l=reproHierarchyLayout(model);assertDistinct(l);
assert.equal(new Set(ids.slice(0,4).map(id=>l.pos[id].x)).size,4);
assert(l.pos.heterogeneity.x<l.pos.treasury.x&&l.pos.treasury.x<l.pos.paper.x);
assert(l.pos.downstream.x>l.pos.paper.x);
assert.equal(l.edges.filter(e=>e.cycle).length,6);
assert(!model.nodes.find(n=>n.id==='downstream').cycle);
assert(!model.nodes.find(n=>n.id==='isolated').cycle);
assert(l.edges.slice(0,6).every(e=>e.cycleKind==='Task-group cycle'));
assert.deepEqual(l.edges.map(e=>[e.from,e.to]),pairs);
""")


def test_nested_lanes_and_ports_do_not_share_segments():
    run(ROUTE_GEOMETRY + """
const tasks=['p','p/a','p/b','p/c','q'];
const steps=Array.from({length:30},(_,i)=>({name:'s'+i,task:tasks[1+i%3],tier:'required'}));
const edges=[];for(let i=1;i<30;i++)for(let j=Math.max(0,i-3);j<i;j++)edges.push({from:'s'+j,to:'s'+i,via:'out'+j});
const graph={steps,step_edges:edges,dependencies:{tasks:tasks.map(path=>({path,title:path})),boundaries:{}}};
const nav={roots:[],tier:'all',mode:'scope',expanded:tasks};
const m=reproHierarchy(graph,nav,reproProject(graph,nav,[])),l=reproHierarchyLayout(m);assertDistinct(l);
assert.equal(l.edges.length,edges.length);
""")


def test_step_cycle_label_and_short_adjacent_routes():
    run(ROUTE_GEOMETRY + """
const make=edges=>({nodes:['a','b','c','d'].map(id=>({id,type:'step',parent:null,children:[]})),edges:edges.map(([from,to])=>({from,to,evidence:[]}))});
let l=reproHierarchyLayout(make([['a','b'],['a','c'],['a','d'],['b','c'],['c','d']]));assertDistinct(l);
assert(l.edges.every(e=>!e.cycle));
assert(l.edges.find(e=>e.from==='a'&&e.to==='b').points.length<=4);
l=reproHierarchyLayout(make([['a','b'],['b','a'],['b','c']]));assertDistinct(l);
assert.equal(l.edges.filter(e=>e.cycleKind==='Step cycle').length,2);
assert.equal(l.model.nodes.filter(n=>n.cycle).length,2);
""")


def test_dense_fan_in_reserves_readable_ports_inside_target_card():
    run(ROUTE_GEOMETRY + """
const ids=Array.from({length:20},(_,i)=>'producer-'+i).concat('target');
const model={nodes:ids.map(id=>({id,type:'step',parent:null,children:[]})),edges:ids.slice(0,-1).map(from=>({from,to:'target',evidence:[]}))};
const l=reproHierarchyLayout(model);assertDistinct(l);
const ports=l.edges.map(e=>e.points.at(-1)[1]).sort((a,b)=>a-b),box=l.pos.target;
assert(ports[0]>box.y&&ports.at(-1)<box.y+box.height);
assert(ports.every((y,i)=>!i||y-ports[i-1]>=7));
""")


def test_logical_connection_to_an_expanded_descendant_has_valid_route():
    run(ROUTE_GEOMETRY + """
const child={id:'child',type:'task',parent:'parent',children:[]};
const model={nodes:[{id:'parent',type:'task',parent:null,children:[child]},child],edges:[{from:'parent',to:'child',evidence:[{kind:'logical'}]}]};
const l=reproHierarchyLayout(model);assertDistinct(l);
assert.equal(l.edges.length,1);assert(l.edges[0].points.every(p=>p.every(Number.isFinite)));
""")


def test_disconnected_graphs_and_isolated_cards_have_separate_bands():
    run(ROUTE_GEOMETRY + """
const ids=['a','b','c','d','e','solo-1','solo-2','solo-3','solo-4'];
const pairs=[['a','b'],['b','c'],['c','a'],['d','e']];
const make=()=>({nodes:ids.map(id=>({id,type:'task',parent:null,children:[]})),edges:pairs.map(([from,to])=>({from,to,evidence:[]}))});
const m=make(),l=reproHierarchyLayout(m),bands=l.bands.filter(b=>!b.parent);assertDistinct(l);
assert.deepEqual(bands.map(b=>b.ids),[['a','b','c'],['d','e'],['solo-1','solo-2','solo-3','solo-4']]);
assert.deepEqual(bands.map(b=>b.isolated),[false,false,true]);
assert.equal(bands[2].label,'No connections in this view');
for(let i=1;i<bands.length;i++)assert(bands[i].y>=bands[i-1].y+bands[i-1].height+32);
for(const e of l.edges){const band=bands.find(b=>b.ids.includes(e.from));assert(band.ids.includes(e.to));assert(e.points.every(p=>p[1]>=band.y&&p[1]<band.y+band.height));}
assert.deepEqual(Object.keys(l.pos).sort(),ids.sort());assert.deepEqual(l.edges.map(e=>[e.from,e.to]),pairs);
assert.deepEqual(l.pos,reproHierarchyLayout(make()).pos);
assert.equal(l.pos['solo-1'].y,l.pos['solo-3'].y);assert(l.pos['solo-4'].y>l.pos['solo-1'].y);
""")


def test_nested_internal_graph_stays_connected_without_containment_edges():
    run(ROUTE_GEOMETRY + """
const tasks=['a','a/left','a/right','a/empty','b','c','solo'];
const steps=[{name:'input',task:'a/left',tier:'required'},{name:'output',task:'a/right',tier:'on-demand'},{name:'other-in',task:'b',tier:'required'},{name:'other-out',task:'c',tier:'required'}];
const graph={steps,step_edges:[{from:'input',to:'output',via:'a.csv'},{from:'other-in',to:'other-out',via:'b.csv'}],dependencies:{tasks:tasks.map(path=>({path,title:path})),boundaries:{}}};
const nav={roots:[],tier:'all',mode:'scope',expanded:['a','a/left','a/right']};
const layout=()=>reproHierarchyLayout(reproHierarchy(graph,nav,reproProject(graph,nav,[])));
let l=layout();assertDistinct(l);
let root=l.bands.filter(b=>!b.parent);assert.deepEqual(root.map(b=>b.ids),[['task:a'],['task:b','task:c'],['task:solo']]);
assert(!root[0].isolated); // visible internal edges make this an independent graph
const nested=l.bands.filter(b=>b.parent==='task:a');assert.deepEqual(nested.map(b=>b.ids),[['task:a/left','task:a/right'],['task:a/empty']]);
assert.equal(l.edges.length,2);assert(l.pos['task:a'].x<=l.pos.input.x);
nav.tier='required';l=layout();assertDistinct(l);root=l.bands.filter(b=>!b.parent);
assert(root.find(b=>b.isolated).ids.includes('task:a'));assert.equal(l.edges.length,1);
nav.roots=['a'];nav.tier='all';l=layout();assert.equal(l.edges.length,1);assert(!l.bands.find(b=>!b.parent).isolated);
""")


def test_lower_nested_band_can_route_outside_parent_without_crossing_earlier_graph():
    run(ROUTE_GEOMETRY + """
const a={id:'a',type:'step',parent:'parent',children:[]},b={id:'b',type:'step',parent:'parent',children:[]};
const c={id:'c',type:'step',parent:'parent',children:[]},d={id:'d',type:'step',parent:'parent',children:[]};
const model={nodes:[{id:'parent',type:'task',parent:null,children:[a,b,c,d]},a,b,c,d,{id:'outside',type:'step',parent:null,children:[]}],edges:[['a','b'],['c','d'],['d','outside']].map(([from,to])=>({from,to,evidence:[]}))};
const l=reproHierarchyLayout(model);assertDistinct(l);
assert.deepEqual(l.bands.filter(b=>b.parent==='parent').map(b=>b.ids),[['a','b'],['c','d']]);
const edge=l.edges.find(e=>e.to==='outside');
for(const id of ['a','b']){const box=l.pos[id];for(let i=1;i<edge.points.length;i++){const [x,y]=edge.points[i-1],[xx,yy]=edge.points[i];const hit=x===xx?x>box.x&&x<box.x+box.width&&Math.max(y,yy)>box.y&&Math.min(y,yy)<box.y+box.height:y>box.y&&y<box.y+box.height&&Math.max(x,xx)>box.x&&Math.min(x,xx)<box.x+box.width;assert(!hit,`escaping route crosses ${id}`);}}
assert.equal(l.edges.length,3);
""")
