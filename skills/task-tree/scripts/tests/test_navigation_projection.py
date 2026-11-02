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
    definitions = _extract_js_defs(['reproWithin', 'reproProject', 'reproStronglyConnected', 'reproCycleMembers',
        'reproHierarchy', 'reproHierarchyLayout', 'reproTasks', 'reproTaskTitle', 'parentPath'])
    source = "const assert=require('node:assert/strict');var pathTitles={};\n" + definitions + '\n' + body
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


FIXTURE = """
var tasks=['p','p/child','p/child/nested','peer','logical'].map(path=>({path,title:'Repeated',status:'in-progress'}));
var steps=[['setup','p'],['build','p/child'],['nested','p/child/nested'],['report','p'],['independent','peer']].map(([name,task])=>({name,task}));
var edges=[['setup','build'],['build','nested'],['nested','report'],['setup','report']].map(([from,to])=>({from,to,via:from+'.csv'}));
var graph={steps,step_edges:edges,dependencies:{tasks,logical:[{kind:'logical',from:'logical',to:'p',declaration:'p depends_on: logical'}]}};
var nav={expanded:[]};
function model(){return reproHierarchy(graph,nav,reproProject(graph));}
"""


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
var steps=tasks.map((t,i)=>({name:'s'+i,task:t.path}));
var kind=""" + json.dumps(kind) + """,edges=[];
for(let i=1;i<20;i++){if(kind==='chain'||kind==='cycle')edges.push({from:'s'+(i-1),to:'s'+i,via:'f'+i});if(kind==='fan')edges.push({from:'s0',to:'s'+i,via:'f'+i});}
if(kind==='chain')edges.push({from:'s0',to:'s19',via:'shortcut'});
if(kind==='cycle')edges.push({from:'s19',to:'s0',via:'cycle'});
var graph={steps,step_edges:edges,dependencies:{tasks}},nav={expanded:tasks.map(t=>t.path)};
var m=reproHierarchy(graph,nav,reproProject(graph)),l=reproHierarchyLayout(m);
assert.equal(m.nodes.filter(n=>n.type==='step').length,20);assert.equal(l.edges.length,edges.length);
for(let e of l.edges){assert(e.evidence.length===1);assert(Number.isFinite(l.pos[e.from].x));}
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


LINEAGE = """
var tasks=['data','clean','model','model/fit','model/report','docs','notes','other'].map(path=>({path,title:path,status:'in-progress'}));
var steps=[['raw','data'],['tidy','clean'],['fit','model/fit'],['report','model/report'],['docs-build','docs'],['note','notes'],['other','other']].map(([name,task])=>({name,task}));
var edges=[['raw','tidy'],['tidy','fit'],['fit','report'],['note','docs-build']].map(([from,to])=>({from,to,via:from+'.csv'}));
var graph={steps,step_edges:edges,dependencies:{tasks,logical:[{kind:'logical',from:'docs',to:'model',declaration:'model depends_on: docs'}]}};
const sorted=set=>Array.from(set).sort();
"""


def lineage_run(body):
    definitions = _extract_js_defs(['reproWithin', 'reproTasks', 'reproLineageKey', 'reproLineage', 'parentPath'])
    source = "const assert=require('node:assert/strict');\n" + definitions + '\n' + LINEAGE + body
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


def test_step_anchor_follows_file_edges_only():
    lineage_run("""
var up=reproLineage(graph,[{step:'fit'}],'up');
assert.deepEqual(sorted(up.steps),['fit','raw','tidy']);
assert.deepEqual(sorted(up.tasks),['clean','data','model/fit']);
var both=reproLineage(graph,[{step:'fit'}],'both');
assert.deepEqual(sorted(both.up.steps),['fit','raw','tidy']);assert.deepEqual(sorted(both.down.steps),['fit','report']);
assert(!both.steps.has('docs-build'),'a depends_on-only neighbour stays out of a step anchor');
assert(!both.edges.has('l\\ndocs\\nmodel'));
""")


def test_task_anchor_adds_depends_on_declared_on_an_ancestor():
    lineage_run("""
var up=reproLineage(graph,[{task:'model/fit'}],'up');
assert.deepEqual(sorted(up.steps),['docs-build','fit','note','raw','tidy']);
assert(up.tasks.has('docs')&&up.tasks.has('notes')&&!up.tasks.has('model/report'));
assert(up.edges.has('l\\ndocs\\nmodel')&&up.edges.has('f\\nnote\\ndocs-build'));
var down=reproLineage(graph,[{task:'docs'}],'down');
assert.deepEqual(sorted(down.steps),['docs-build','fit','report'],'a task reached through depends_on joins with its subtree');
assert.deepEqual(sorted(down.tasks),['docs','model','model/fit','model/report']);
var union=reproLineage(graph,[{step:'raw'},{task:'other'}],'down');
assert.deepEqual(sorted(union.steps),['fit','other','raw','report','tidy']);
""")


def test_filtered_graph_keeps_chains_through_a_hidden_task():
    definitions = _extract_js_defs(['reproWithin', 'reproTasks', 'reproLineageKey', 'reproLineage', 'parentPath',
        'normalizeLineageFilter', 'workspaceLineage', 'workspaceTasks', 'workspaceTaskMatches', 'workspaceVisibility', 'workspaceGraph'])
    source = "const assert=require('node:assert/strict');var pathTitles={},SEARCH_INDEX=[],_workspaceLineageMemo=null;\n" + definitions + '\n' + LINEAGE + """
var _reproData={graph,status:{steps:[]}};
var _workspaceFilters={statuses:[],tasks:tasks.map(t=>t.path).filter(p=>p!=='clean'),lineage:{anchors:[{step:'raw'},{step:'gone'}],direction:'down'}};
var view=workspaceGraph(graph);
assert.deepEqual(view.steps.map(s=>s.name).sort(),['fit','raw','report']);
assert.deepEqual(_workspaceFilters.lineage.anchors,[{step:'raw'}],'an anchor the graph no longer has is dropped');
assert(!workspaceTaskMatches('docs')&&workspaceTaskMatches('model/fit'));
"""
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


def _summary_source(extra):
    definitions = _extract_js_defs(['reproWithin', 'reproTasks', 'reproLineageKey', 'reproLineage', 'parentPath',
        'normalizeLineageFilter', 'workspaceLineage', 'workspaceTasks', 'workspaceTaskMatches', 'workspaceVisibility',
        'updateWorkspaceFilterSummary', 'lineageAnchorLabel'])
    return "const assert=require('node:assert/strict');var pathTitles={},SEARCH_INDEX=[],_workspaceLineageMemo=null,activePath='',_reproData=null;\n" + definitions + '\n' + LINEAGE + extra


def test_unavailable_graph_is_reported_in_the_filter_summary():
    source = _summary_source("""
var LINEAGE_DIRECTIONS={both:'B',up:'U',down:'D'},host={hidden:true,innerHTML:''};
var document={getElementById:id=>id==='workspace-filter-summary'?host:id==='filter-trigger'?{classList:{toggle(){}}}:null};
var escapeHtml=x=>x,escapeAttr=x=>x,reproTaskTitle=x=>x;
var _workspaceFilters={statuses:[],tasks:null,lineage:{anchors:[{step:'raw'}],direction:'down'}};
updateWorkspaceFilterSummary();
assert(!host.hidden&&host.innerHTML.includes('graph unavailable'));
""")
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


def test_anchor_sets_are_built_once_across_visibility_calls():
    source = _summary_source("""
_reproData={graph,status:{steps:[]}};
var _workspaceFilters={statuses:[],tasks:null,lineage:{anchors:[{step:'raw'}],direction:'down'}};
var calls=0,real=workspaceTasks;workspaceTasks=function(){calls++;return real();};
var first=workspaceVisibility(),afterFirst=calls;
workspaceVisibility();workspaceVisibility();
assert.equal(afterFirst,2,'one catalog read for the memo, one for the visibility pass');
assert.equal(calls,afterFirst+2,'later calls read the catalog once each and reuse the memo sets');
assert(first.matches.has('data')&&!first.matches.has('docs'));
""")
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr
