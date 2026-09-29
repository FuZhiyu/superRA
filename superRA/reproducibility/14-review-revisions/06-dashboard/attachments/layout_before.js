/* reproHierarchyLayout at 7acbc7f7, before the reformat; kept as the equivalence baseline. */
function reproHierarchyLayout(model) {
  var pos={},byId={},nodeParent={},levels={},routes=[];
  model.nodes.forEach(function(n){byId[n.id]=n;nodeParent[n.id]=n.parent;n.cycle=false;n.cycleKind='';});
  function direct(id,parent){while(byId[id]&&nodeParent[id]!==parent)id=nodeParent[id];return id;}
  function level(items,parent){
    var ids=items.map(function(n){return n.id;}).sort(),next={},index={},low={},stack=[],on=new Set(),groups=[],serial=0,groupOf={};
    ids.forEach(function(id){next[id]=[];});
    model.edges.forEach(function(e){var a=direct(e.from,parent),b=direct(e.to,parent);if(a&&b&&a!==b&&next[a]&&next[b]&&next[a].indexOf(b)<0)next[a].push(b);});
    function visit(id){index[id]=low[id]=serial++;stack.push(id);on.add(id);next[id].sort().forEach(function(to){if(index[to]===undefined){visit(to);low[id]=Math.min(low[id],low[to]);}else if(on.has(to))low[id]=Math.min(low[id],index[to]);});if(low[id]===index[id]){var group=[],v;do{v=stack.pop();on.delete(v);group.push(v);}while(v!==id);groups.push(group);}}
    ids.forEach(function(id){if(index[id]===undefined)visit(id);});
    groups.forEach(function(g,i){g.forEach(function(id){groupOf[id]=i;});});
    var incoming=groups.map(function(){return 0;}),out=groups.map(function(){return new Set();}),base=groups.map(function(){return 0;}),rank={};
    ids.forEach(function(id){next[id].forEach(function(to){var a=groupOf[id],b=groupOf[to];if(a!==b&&!out[a].has(b)){out[a].add(b);incoming[b]++;}});});
    var queue=groups.map(function(_,i){return i;}).filter(function(i){return !incoming[i];});
    while(queue.length){var gi=queue.shift(),remaining=groups[gi].slice(),ordered=[];
      while(remaining.length){remaining.sort(function(a,b){function score(id){return next[id].filter(function(to){return remaining.indexOf(to)>=0;}).length-remaining.filter(function(from){return next[from].indexOf(id)>=0;}).length;}return score(b)-score(a)||a.localeCompare(b);});ordered.push(remaining.shift());}
      ordered.forEach(function(id,i){rank[id]=base[gi]+i;if(ordered.length>1){byId[id].cycle=true;byId[id].cycleKind=ordered.some(function(key){return byId[key].type==='task';})?'Task-group cycle':'Step cycle';}});
      out[gi].forEach(function(to){base[to]=Math.max(base[to],base[gi]+ordered.length);if(!--incoming[to])queue.push(to);});
    }
    // Connectivity is projected between siblings; containment itself adds no edge.
    var neighbors={},incident=new Set(),visited=new Set(),bands=[],isolated=[];
    ids.forEach(function(id){neighbors[id]=new Set();});
    ids.forEach(function(id){next[id].forEach(function(to){neighbors[id].add(to);neighbors[to].add(id);});});
    model.edges.forEach(function(e){[direct(e.from,parent),direct(e.to,parent)].forEach(function(id){if(neighbors[id])incident.add(id);});});
    ids.forEach(function(id){if(visited.has(id))return;var pending=[id],members=[];visited.add(id);while(pending.length){var member=pending.shift();members.push(member);neighbors[member].forEach(function(to){if(!visited.has(to)){visited.add(to);pending.push(to);}});}members.sort();if(members.length===1&&!incident.has(id))isolated.push(id);else bands.push({ids:members,isolated:false});});
    if(isolated.length)bands.push({ids:isolated,isolated:true});
    var bandOf={};bands.forEach(function(band,i){band.tracks=[];band.channels={left:{},right:{}};band.showLabel=bands.length>1||band.isolated;band.label=band.isolated?'No connections in this view':(bands.filter(function(b){return !b.isolated;}).length>1?'Dependency group '+(i+1):'Connected dependencies');band.ids.forEach(function(id){bandOf[id]=band;});});
    var info={items:items,parent:parent,rank:rank,bands:bands,bandOf:bandOf,left:{},right:{}};levels[parent||'']=info;
    items.forEach(function(n){if(n.children.length)level(n.children,n.id);});
    model.edges.forEach(function(e){var a=direct(e.from,parent),b=direct(e.to,parent);if(a&&b&&a!==b&&groupOf[a]!==undefined&&groupOf[a]===groupOf[b]&&groups[groupOf[a]].length>1){e.cycle=true;if(!e.cycleKind)e.cycleKind=groups[groupOf[a]].some(function(id){return byId[id].type==='task';})?'Task-group cycle':'Step cycle';}});
  }
  model.edges.forEach(function(e){e.cycle=false;e.cycleKind='';});level(model.nodes.filter(function(n){return !n.parent;}),null);
  model.edges.forEach(function(e){if(e.cycle)[e.from,e.to].forEach(function(id){byId[id].cycle=true;byId[id].cycleKind=byId[id].cycleKind||e.cycleKind;});});
  function chain(id,common){var result=[];while(id&&id!==common){result.push(id);id=nodeParent[id];}return result;}
  var ports={};
  function port(id,side,i){var key=id+'|'+side;if(!ports[key])ports[key]=[];ports[key].push(i);}
  model.edges.forEach(function(e,i){var ancestors=chain(nodeParent[e.from],null),p=nodeParent[e.to];while(p&&ancestors.indexOf(p)<0)p=nodeParent[p];var common=p;
    var source=chain(e.from,common),target=chain(e.to,common),boundary=levels[common||''];
    var directRoute=source.length===1&&target.length===1&&boundary.rank[e.to]===boundary.rank[e.from]+1;
    var route={edge:e,index:i,common:common,source:source,target:target,direct:directRoute};routes.push(route);port(e.from,'right',i);port(e.to,'left',i);
    source.forEach(function(id){var list=levels[nodeParent[id]||''].right; (list[id]||(list[id]=[])).push(i);});
    target.forEach(function(id){var list=levels[nodeParent[id]||''].left; (list[id]||(list[id]=[])).push(i);});
    if(!directRoute){source.concat(target).forEach(function(id){var tracks=levels[nodeParent[id]||''].bandOf[id].tracks;if(tracks.indexOf(i)<0)tracks.push(i);});}
  });
  function size(parent){
    var info=levels[parent||''],offset=0;info.width=320;
    info.items.forEach(function(n){if(n.children.length)size(n.id);else{n.width=260;n.height=108;}n.height=Math.max(n.height,80+7*(ports[n.id+'|left']||[]).length,47+7*(ports[n.id+'|right']||[]).length);});
    info.bands.forEach(function(band){
      var widths={},heights={},xs={},x=24,top=(band.showLabel?48:24)+band.tracks.length*6;
      band.y=offset;band.trackTop=offset+(band.showLabel?36:12);
      ['left','right'].forEach(function(side){band.ids.forEach(function(id){var r=info.rank[id],channel=band.channels[side][r]||(band.channels[side][r]=[]);(info[side][id]||[]).forEach(function(i){channel.push(id+'|'+i);});});});
      if(band.isolated){
        var columns=Math.min(3,band.ids.length),rowY=0;
        for(var start=0;start<band.ids.length;start+=columns){var row=band.ids.slice(start,start+columns),rowHeight=0,rowX=24;row.forEach(function(id){var n=byId[id];n.x=rowX;n.y=offset+top+rowY;n.routeLeft=n.x-10;n.routeRight=n.x+n.width+10;rowX+=n.width+24;rowHeight=Math.max(rowHeight,n.height);});x=Math.max(x,rowX);rowY+=rowHeight+24;}
        band.height=top+rowY;band.width=x;
      }else{
        band.ids.forEach(function(id){var n=byId[id],r=info.rank[id];widths[r]=Math.max(widths[r]||0,n.width);});
        Object.keys(widths).map(Number).sort(function(a,b){return a-b;}).forEach(function(r){x+=12+band.channels.left[r].length*5;xs[r]=x;x+=widths[r]+12+band.channels.right[r].length*5+24;});
        band.ids.forEach(function(id){var n=byId[id],r=info.rank[id];n.x=xs[r];n.y=offset+top+(heights[r]||0);n.routeRight=xs[r]+widths[r]+10;n.routeLeft=xs[r]-10;heights[r]=(heights[r]||0)+n.height+28;});
        band.height=top+Math.max(0,...Object.values(heights))+12;band.width=x;
      }
      info.width=Math.max(info.width,band.width);offset+=band.height+36;
    });
    info.height=Math.max(48,offset);if(parent){byId[parent].width=info.width;byId[parent].height=108+info.height;}
  }
  size(null);
  function place(n,x,y){pos[n.id]={x:x+n.x,y:y+n.y,width:n.width,height:n.height,routeRight:x+n.routeRight,routeLeft:x+n.routeLeft};n.children.forEach(function(c){place(c,x+n.x,y+n.y+108);});}
  model.nodes.filter(function(n){return !n.parent;}).forEach(function(n){place(n,0,0);});
  function portY(id,side,i){var list=ports[id+'|'+side];return pos[id].y+(side==='right'?28:61.5)+7*(list.indexOf(i)+1);}
  function gutter(id,side,i){var info=levels[nodeParent[id]||''],list=info.bandOf[id].channels[side][info.rank[id]];return pos[id][side==='right'?'routeRight':'routeLeft']+(side==='right'?1:-1)*5*list.indexOf(id+'|'+i);}
  function track(id,i){var parent=nodeParent[id],band=levels[parent||''].bandOf[id];return (parent?pos[parent].y+108:0)+band.trackTop+band.tracks.indexOf(i)*6;}
  var routed=routes.map(function(route){var e=route.edge,i=route.index,a=pos[e.from],b=pos[e.to],points;
    if(route.direct){var x=gutter(e.from,'right',i);points=[[a.x+a.width,portY(e.from,'right',i)],[x,portY(e.from,'right',i)],[x,portY(e.to,'left',i)],[b.x,portY(e.to,'left',i)]];}
    else {function climb(ids,side){var id=ids[0],box=pos[id],points=[[side==='right'?box.x+box.width:box.x,portY(id,side,i)]];ids.forEach(function(current){var x=gutter(current,side,i);points.push([x,points[points.length-1][1]]);points.push([x,track(current,i)]);});return points;}points=climb(route.source,'right').concat(climb(route.target,'left').reverse());}
    points=points.filter(function(p,j){return !j||p[0]!==points[j-1][0]||p[1]!==points[j-1][1];});
    return Object.assign({},e,{points:points,d:points.map(function(p,j){return(j?'L':'M')+p[0]+','+p[1];}).join(' ')});
  });
  var bands=[];Object.values(levels).forEach(function(info){var x=info.parent?pos[info.parent].x:0,y=info.parent?pos[info.parent].y+108:0;info.bands.forEach(function(band){bands.push({parent:info.parent,ids:band.ids,isolated:band.isolated,label:band.showLabel?band.label:'',x:x+24,y:y+band.y,width:band.width-48,height:band.height});});});
  return {pos:pos,bands:bands,edges:routed,width:levels[''].width,height:levels[''].height,cycles:Object.fromEntries(model.nodes.filter(function(n){return n.cycle;}).map(function(n){return[n.id,n.cycleKind];})),model:model};
}
