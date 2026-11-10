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


FILTER_DEFS = ['reproWithin', 'reproTasks', 'reproLineageKey', 'reproLineage', 'parentPath', 'REPRO_CLOUD', 'REPRO_STATES', 'REPRO_GLYPHS',
    'reproStatusIndex', 'reproStateOf', 'reproChannels', 'reproTaskTitle', 'WORKSPACE_STATUSES', 'emptyWorkspaceFilters',
    'workspaceStrings', 'workspaceScopeRoots', 'workspaceScopeFromSelection', 'normalizeWorkspaceFilters', 'workspaceAnchorKey',
    'normalizeLineageFilter', 'workspaceFilterCount', 'workspaceFiltersForHash', 'workspaceLineage', 'workspaceStepIndex',
    'lineageAnchorLabel', 'workspaceTaskTitle', 'workspaceScopeAdd', 'workspaceTasks', 'workspaceStepMatches',
    'workspaceTaskMatches', 'workspaceVisibility', 'workspaceFacetCounts', 'workspaceResultCount', 'workspaceGraph']

# Statuses and reported step states over the LINEAGE graph. `fit` and `report`
# are stale only through `tidy`; their own state is fresh.
FILTER_FIXTURE = """
var statusOf={data:'approved',clean:'implemented',model:'in-progress','model/fit':'revise','model/report':'not-started',docs:'approved',notes:'postponed',other:'archived'};
tasks.forEach(t=>{t.status=statusOf[t.path];});
var SEARCH_INDEX=[{path:'',title:'Root',status:'in-progress'}].concat(tasks.map(t=>({path:t.path,title:t.path,status:t.status})));
var stepStatus=[['raw','fresh'],['tidy','stale'],['fit','stale','fresh'],['report','stale','fresh'],['docs-build','missing'],['note','failed'],['other','unverified']].map(([name,status,local_status])=>({name,status,local_status}));
var _reproData={graph,status:{steps:stepStatus}},_workspaceFilters=emptyWorkspaceFilters();
function use(f){_workspaceFilters=normalizeWorkspaceFilters(f);return workspaceVisibility();}
function matched(f){return sorted(use(f).matches);}
"""


def filter_run(body, extra_defs=(), prelude=''):
    definitions = _extract_js_defs(FILTER_DEFS + list(extra_defs))
    source = ("const assert=require('node:assert/strict');var pathTitles={},SEARCH_INDEX=[],_workspaceLineageMemo=null,_workspaceStepMemo=null,activePath='';\n"
              + prelude + definitions + '\n' + LINEAGE + FILTER_FIXTURE + body)
    result = subprocess.run([NODE, '-e', source], text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


def test_facets_and_together_with_negation():
    filter_run("""
assert.deepEqual(matched({status:{neg:true,values:['archived','postponed']}}),['','clean','data','docs','model','model/fit','model/report']);
assert.deepEqual(matched({scope:{in:['model']}}),['model','model/fit','model/report']);
assert.deepEqual(matched({scope:{out:['model','docs']}}),['','clean','data','notes','other']);
assert.deepEqual(matched({scope:{in:['model'],out:['model/fit']}}),['model','model/report'],'In and Not in combine');
assert.deepEqual(matched({status:{values:['in-progress','revise']},scope:{in:['model']}}),['model','model/fit'],'facets AND, values OR');
var v=use({scope:{in:['model/fit']}});
assert(v.visible.has('model')&&v.visible.has('')&&!v.matches.has('model'),'ancestors show as context');
""")


def test_counts_apply_every_other_facet():
    filter_run("""
use({status:{values:['revise']},scope:{in:['model'],out:['model/report']}});
assert.deepEqual(workspaceFacetCounts('status'),{'in-progress':1,revise:1},'status counts ignore the status facet only');
assert.deepEqual(workspaceFacetCounts('scope-in'),{'model/fit':1,model:1,'':1},'each subtree list skips only itself');
use({status:{values:['not-started','revise']},scope:{in:['model'],out:['model/report']}});
assert.deepEqual(workspaceFacetCounts('scope-out'),{'model/fit':1,'model/report':1,model:2,'':2});
assert.deepEqual(workspaceFacetCounts('steps'),{stale:1});
use({steps:['failed']});
assert.deepEqual(workspaceFacetCounts('steps'),{fresh:1,stale:3,missing:1,failed:1,unverified:1});
assert.deepEqual(workspaceFacetCounts('status'),{postponed:1},'a zero-count value is absent');
""")


def test_step_state_matches_the_reported_state():
    filter_run("""
assert.deepEqual(matched({steps:['stale']}),['clean','model/fit','model/report'],'a step stale through its producer matches stale');
assert.deepEqual(workspaceGraph(graph).steps.map(s=>s.name).sort(),['fit','report','tidy'],'Graph drops steps outside the states');
assert.deepEqual(matched({steps:['fresh']}),['data']);
assert.deepEqual(matched({steps:['stale'],lineage:[{step:'tidy',direction:'up'}]}),['clean'],'the owned step must also pass the dependency filter');
assert.equal(workspaceResultCount(use({steps:['stale','missing']})),'<b>4</b> of 9 tasks · <b>4</b> of 7 steps');
_reproData=null;_workspaceStepMemo=null;
assert.equal(matched({steps:['stale']}).length,9,'step states wait for the graph');
""")


def test_each_anchor_walks_its_own_direction():
    filter_run("""
use({lineage:[{step:'fit',direction:'up'},{step:'note',direction:'down'}]});
assert.deepEqual(sorted(workspaceLineage().steps),['docs-build','fit','note','raw','tidy']);
use({lineage:[{step:'fit',direction:'down'},{task:'docs',direction:'both'}]});
assert.deepEqual(sorted(workspaceLineage().steps),['docs-build','fit','note','report']);
assert.deepEqual(matched({lineage:[{step:'gone'}]}).length,9);
assert.deepEqual(_workspaceFilters.lineage,[],'an anchor the graph no longer has is dropped');
""")


def test_hash_round_trips_and_legacy_forms_load():
    filter_run("""
var f=normalizeWorkspaceFilters({status:{neg:true,values:['postponed','bogus']},steps:['stale','nope'],scope:{in:['model/fit','model'],out:['model/fit/x']},lineage:[{task:'docs',direction:'up'},{step:'fit'},{task:'docs'},{task:''}]});
assert.deepEqual(f,{status:{neg:true,values:['postponed']},steps:['stale'],scope:{in:['model'],out:['model/fit/x']},lineage:[{task:'docs',direction:'up'},{step:'fit',direction:'both'}]});
assert.deepEqual(normalizeWorkspaceFilters(JSON.parse(JSON.stringify(workspaceFiltersForHash(f)))),f);
assert.equal(workspaceFiltersForHash(emptyWorkspaceFilters()),undefined);
var legacy=normalizeWorkspaceFilters({statuses:['revise'],tasks:null,lineage:{anchors:[{step:'fit'},{task:'docs'}],direction:'up'}});
assert.deepEqual(legacy.status,{neg:false,values:['revise']});
assert.deepEqual(legacy.lineage,[{step:'fit',direction:'up'},{task:'docs',direction:'up'}],'a shared direction applies to every anchor');
var all=SEARCH_INDEX.map(t=>t.path);
assert.deepEqual(normalizeWorkspaceFilters({tasks:all.filter(p=>!p.startsWith('model'))}).scope,{in:[],out:['model']});
assert.deepEqual(normalizeWorkspaceFilters({tasks:['model/fit','model/report']}).scope,{in:['model/fit','model/report'],out:[]});
assert.deepEqual(normalizeWorkspaceFilters({tasks:all}).scope,{in:[],out:[]},'a full selection is no filter');
assert.deepEqual(normalizeWorkspaceFilters({hidden:['docs','notes']}).scope,{in:[],out:['docs','notes']},'a hidden list maps to Not in');
assert.deepEqual(workspaceFiltersForHash(normalizeWorkspaceFilters({scope:{out:['docs']}})),{scope:{in:[],out:['docs']}});
var v=use({tasks:['model/fit','model/report']});
assert(v.visible.has('model')&&!v.matches.has('model'),'an unselected parent of a selected child shows as context');
""")


def test_hiding_a_leaf_keeps_its_single_child_parent_and_its_steps():
    filter_run("""
tasks.push({path:'model/fit/tune',title:'model/fit/tune',status:'in-progress'});SEARCH_INDEX.push(tasks[tasks.length-1]);
steps.push({name:'tune',task:'model/fit/tune'});edges.push({from:'fit',to:'tune',via:'fit.csv'});stepStatus.push({name:'tune',status:'fresh'});
_workspaceFilters=normalizeWorkspaceFilters({scope:{in:['model/fit']}});
assert.deepEqual(sorted(workspaceVisibility().matches),['model/fit','model/fit/tune']);
workspaceScopeAdd('model/fit/tune','out');
assert.deepEqual(_workspaceFilters.scope,{in:['model/fit'],out:['model/fit/tune']},'hiding adds to Not in and keeps In');
assert.deepEqual(sorted(workspaceVisibility().matches),['model/fit'],'the single-child parent still matches');
assert.deepEqual(workspaceGraph(graph).steps.map(s=>s.name),['fit'],'and its own step stays in Graph');
workspaceScopeAdd('data','in');workspaceScopeAdd('model/fit/tune/x','out');
assert.deepEqual(_workspaceFilters.scope,{in:['data','model/fit'],out:['model/fit/tune']},'show only keeps Not in; covered descendants drop');
assert.deepEqual(sorted(workspaceVisibility().matches),['data','model/fit']);
""")


def test_root_is_context_under_a_dependency_filter_unless_it_owns_a_member_step():
    filter_run("""
var v=use({lineage:[{step:'raw',direction:'down'}]});
assert(!v.matches.has('')&&v.visible.has(''),'the root shows as context');
steps.push({name:'setup',task:''});edges.push({from:'setup',to:'raw',via:'setup.csv'});stepStatus.push({name:'setup',status:'fresh'});
v=use({lineage:[{step:'tidy',direction:'up'}]});
assert(v.matches.has(''),'a root that owns a member step matches');
""")


def test_filtered_graph_keeps_chains_through_a_hidden_task():
    filter_run("""
use({scope:{out:['clean']},lineage:[{step:'raw',direction:'down'},{step:'gone'}]});
var view=workspaceGraph(graph);
assert.deepEqual(view.steps.map(s=>s.name).sort(),['fit','raw','report']);
assert.deepEqual(_workspaceFilters.lineage,[{step:'raw',direction:'down'}],'an anchor the graph no longer has is dropped');
assert(!workspaceTaskMatches('docs')&&workspaceTaskMatches('model/fit'));
""")


def test_unavailable_graph_is_reported_in_the_filter_bar():
    filter_run("""
_reproData=null;
var host={hidden:true,innerHTML:'',contains(){return false;},querySelector(){return null;}};
var document={activeElement:null,getElementById:id=>id==='workspace-filter-bar'?host:null};
var escapeHtml=x=>x,escapeAttr=x=>x;
_workspaceFilters=normalizeWorkspaceFilters({lineage:[{step:'raw',direction:'down'}]});
renderWorkspaceFilterBar();
assert(!host.hidden&&host.innerHTML.includes('graph unavailable')&&host.innerHTML.includes('Downstream of'));
assert(host.innerHTML.includes('<b>9</b> of 9 tasks')&&!host.innerHTML.includes('steps'));
""", extra_defs=['LINEAGE_DIRECTIONS', 'LINEAGE_ARROWS', 'workspaceSummarize', 'workspaceGlyphHTML', 'workspaceStateHTML',
                 'workspaceChipHTML', 'renderWorkspaceFilterBar'])


def test_anchor_sets_are_built_once_across_visibility_calls():
    filter_run("""
_workspaceFilters=normalizeWorkspaceFilters({lineage:[{step:'raw',direction:'down'}]});
var calls=0,real=workspaceTasks;workspaceTasks=function(){calls++;return real();};
var first=workspaceVisibility(),afterFirst=calls;
workspaceVisibility();workspaceVisibility();
assert.equal(afterFirst,2,'one catalog read for the memo, one for the visibility pass');
assert.equal(calls,afterFirst+2,'later calls read the catalog once each and reuse the memo sets');
assert(first.matches.has('data')&&!first.matches.has('docs'));
""")
