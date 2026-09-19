/* ══════════════════════════════════════════════════════════════════════════
   STANDALONE MODE — server-less single-file export.
   ──────────────────────────────────────────────────────────────────────────
   The live dashboard fetches HTML/JSON fragments from the FastAPI server
   (/nav, /nav/<path>, /node/<path>, /api/children-graph?root=<path>,
   /api/*). A file
   opened via file:// has no server, so generate_dashboard() pre-renders every
   one of those fragments with the SAME Jinja partials the server uses and
   embeds them here as a {url -> fragment} map. The fetch shim below resolves
   the client's fetch() calls from that map (and no-ops the server-only /api/*
   writes), so navigation, view-switching, lazy nav loads, and markdown/figure
   rendering all work offline with zero network calls for task data. Server-only
   affordances (comments, worktree switch, SSE auto-refresh) are degraded: their
   controls are hidden in the template and their fetches resolve to empty.
   ══════════════════════════════════════════════════════════════════════════ */
/* Build a fake Response that yields a pre-rendered fragment (or [] for the
   comment/summary JSON endpoints). Mirrors just enough of the fetch Response
   contract for the existing loaders: ok, status, text(), json(). */
function _standaloneResponse(payload, found) {
  return Promise.resolve({
    ok: found,
    status: found ? 200 : 404,
    text: function () { return Promise.resolve(found ? payload : ''); },
    json: function () { return Promise.resolve(found ? payload : null); },
  });
}

/* Resolve a fetch URL against the embedded data instead of the network.
   - Exact fragment hits (/nav, /node/<path>, /api/children-graph?root=<path>,
     /nav/<path>) return their pre-rendered HTML/JSON. The map is
     keyed by the raw (decoded) path, but the children-graph loader builds its
     URL with encodeURIComponent(path), which escapes the '/' in
     multi-segment paths to %2F. We decode before the lookup so an encoded
     request (/api/children-graph?root=a%2Fb) and a raw request
     (/node/a/b) both match the map.
   - Comment GETs return [] / {} so loadComments + the summary badge no-op.
   - Worktree GET returns a single-entry payload so the selector stays hidden.
   - Server-only writes (POST/PATCH/DELETE /api/*) resolve ok with no effect;
     their UI controls are hidden in standalone mode, so they are never reached
     in normal use — this only keeps a stray call from throwing. */
function standaloneFetch(url) {
  if (STANDALONE_FRAGMENTS.hasOwnProperty(url)) {
    return _standaloneResponse(STANDALONE_FRAGMENTS[url], true);
  }
  var decoded = decodeURIComponent(url);
  if (decoded !== url && STANDALONE_FRAGMENTS.hasOwnProperty(decoded)) {
    return _standaloneResponse(STANDALONE_FRAGMENTS[decoded], true);
  }
  if (/\/comments($|\?)/.test(url)) return _standaloneResponse([], true);
  if (url.indexOf('/api/comments/summary') !== -1) return _standaloneResponse({}, true);
  if (url.indexOf('/api/worktrees') !== -1) {
    return _standaloneResponse({ launch_wt_id: '', worktrees: [] }, true);
  }
  return _standaloneResponse(null, false);
}

/* Replace window.fetch wholesale when window.STANDALONE is true (set by the
   inline config script in base.html before this file loads). Every task-data
   load in this page goes through fetch(); routing them here guarantees zero
   network calls for task content from a file:// open. */
if (window.STANDALONE) {
  window.fetch = function (input) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    return standaloneFetch(url);
  };
}

/* ── Markdown-it setup ── */
/* Syntax-highlight fenced code via highlight.js when a known language tag is
   present; unknown/absent tags fall through to markdown-it's default escaping
   (today's plain rendering). The `hljs` class on <code> is what the theme CSS
   targets, and `language-<lang>` mirrors markdown-it's own convention. */
function highlightFence(code, lang) {
  if (lang && window.hljs && hljs.getLanguage(lang)) {
    try {
      var out = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value;
      return '<pre><code class="hljs language-' + lang + '">' + out + '</code></pre>';
    } catch (e) { /* fall through to plain rendering */ }
  }
  return '';  /* '' -> markdown-it uses its default escaped <pre><code> */
}
var md = window.markdownit({ html: true, linkify: true, highlight: highlightFence });
md.use(texmath, { engine: katex, delimiters: 'dollars' });

/* ── Active worktree (the ?wt= dimension of the URL) ──
   The active worktree is carried in location.search as `?wt=<id>`, separate from
   the task path in location.hash. ACTIVE_WT is the resolved id ('' = the launch
   worktree, which the server serves by default and keeps out of the URL). Every
   server fetch goes through wtUrl() so all panels render this worktree; the SSE
   connect and PROJECT_ROOT follow it too. In standalone (file://) mode there is
   no server and ?wt= is meaningless: ACTIVE_WT stays '' and wtUrl() returns the
   URL untouched so the exact-string fetch shim still matches. */
function readActiveWt() {
  if (window.STANDALONE) return '';
  try { return new URLSearchParams(location.search).get('wt') || ''; }
  catch (e) { return ''; }
}
var ACTIVE_WT = readActiveWt();

/* Append the active `?wt=` to a same-origin server URL, merging with any query
   string the URL already carries (e.g. /api/children-graph?root=<path>,
   /export?root=<path>).
   No-op when ACTIVE_WT is '' (launch worktree) or in standalone mode. */
function wtUrl(url) {
  if (!ACTIVE_WT) return url;
  var sep = url.indexOf('?') === -1 ? '?' : '&';
  return url + sep + 'wt=' + encodeURIComponent(ACTIVE_WT);
}

function encodeRepoPath(path) {
  var splitAt = path.search(/[?#]/);
  var body = splitAt === -1 ? path : path.slice(0, splitAt);
  var suffix = splitAt === -1 ? '' : path.slice(splitAt);
  return body.split('/').map(function(part) {
    return encodeURIComponent(part);
  }).join('/') + suffix;
}

function repoFileHref(path) {
  if (REPO_FILE_BASE) return REPO_FILE_BASE.replace(/\/+$/, '') + '/' + encodeRepoPath(path);
  return '';
}

/* Undo markdown-it's percent-encoding of a link href, which turns `my file.md`
   into `my%20file.md` and `résumé.pdf` into `r%C3%A9sum%C3%A9.pdf`. /api/open
   takes a real filesystem path in a JSON body, so the encoding has to come off
   here. A malformed sequence (a literal `%` in a filename) keeps the raw text. */
function decodePathHref(path) {
  try {
    return decodeURIComponent(path);
  } catch (e) {
    return path;
  }
}

function isRelativeResource(value) {
  return !!value
    && value.charAt(0) !== '/'
    && value.indexOf('//') !== 0
    && !/^[A-Za-z][A-Za-z0-9+.-]*:/.test(value);
}

function artifactDirectory(path) {
  var i = (path || '').lastIndexOf('/');
  return i === -1 ? '' : path.slice(0, i);
}

/* Resolve a link from a companion's own directory while staying inside the
   owning task's public artifact surface: attachments/** only, matching the
   server's _validated_parts contract. */
function resolveArtifactRelativePath(sourcePath, href) {
  if (!isRelativeResource(href) || href.charAt(0) === '#') return '';
  var clean = href.replace(/[?#].*$/, '');
  try { clean = decodeURIComponent(clean); } catch (e) {}
  var base = artifactDirectory(sourcePath);
  var parts = (base ? base.split('/') : []).concat(clean.split('/'));
  var out = [];
  for (var i = 0; i < parts.length; i++) {
    var part = parts[i];
    if (!part || part === '.') continue;
    if (part === '..') {
      if (!out.length) return '';
      out.pop();
    } else {
      out.push(part);
    }
  }
  if (out.length < 2 || out[0] !== 'attachments') return '';
  return out.join('/');
}

/* Membership oracle for in-tree task references. Every task's tree path, as a
   set, so renderMarkdown can decide whether a relative body link points at a
   real task in this tree (-> internal navigation) or at a plain file (-> the
   vscode:// rewrite). Built from the full tree both render paths pass in, so it
   is complete even though the sidebar nav lazy-loads deep branches. */
var TASK_PATHS = (function () {
  var set = {};
  ALL_TASK_PATHS.forEach(function (p) { set[p] = true; });
  return set;
})();

/* Resolve a task-relative href (`task.md`, `../merge/task.md`, `sibling/task.md`)
   against the active task's tree path and, if it names a real task, return that
   task's canonical tree path; otherwise null (caller keeps the vscode:// path).
   A target is an in-tree task when, after dropping a trailing `/task.md` or a
   bare trailing `/`, the normalized tree path is in TASK_PATHS. */
function resolveInternalTaskPath(href, taskPath, contentBaseDir) {
  /* Strip any #fragment / ?query — they don't affect which task is referenced. */
  var clean = href.replace(/[?#].*$/, '');
  if (!clean) return null;

  /* Base segments: the directory of the active task. An href rooted at the
     resolved root's name (ROOT_PREFIX, e.g. `superRA/...`) resolves from the
     tree root instead of the active task's dir. The literal `superRA/` and
     legacy `.plan/` prefixes stay accepted for any root and migrated prose. */
  var segs;
  var rootRoots = [];
  if (ROOT_PREFIX) rootRoots.push(ROOT_PREFIX + '/');
  if (rootRoots.indexOf('superRA/') === -1) rootRoots.push('superRA/');
  if (rootRoots.indexOf('.plan/') === -1) rootRoots.push('.plan/');
  var matchedRoot = null;
  for (var ri = 0; ri < rootRoots.length; ri++) {
    if (clean.indexOf(rootRoots[ri]) === 0) { matchedRoot = rootRoots[ri]; break; }
  }
  if (matchedRoot !== null) {
    segs = clean.slice(matchedRoot.length).split('/');
  } else if (clean.charAt(0) === '/') {
    return null;  /* filesystem-absolute, not a tree path */
  } else {
    segs = (taskPath ? taskPath.split('/') : [])
      .concat(contentBaseDir ? contentBaseDir.split('/') : [])
      .concat(clean.split('/'));
  }

  /* Normalize . / .. segments into a clean tree path. */
  var out = [];
  for (var i = 0; i < segs.length; i++) {
    var s = segs[i];
    if (s === '' || s === '.') continue;
    if (s === '..') { if (out.length) out.pop(); else return null; continue; }
    out.push(s);
  }

  /* Drop a trailing `task.md` (or bare trailing slash already handled by the
     empty-segment skip) so a directory ref and a task.md ref both canonicalize
     to the same tree path. */
  if (out.length && out[out.length - 1] === 'task.md') out.pop();

  var path = out.join('/');
  return TASK_PATHS[path] ? path : null;
}

/**
 * Render markdown text via markdown-it, then post-process:
 * - In-tree task references -> internal hash navigation (#/<task-path>)
 * - Other relative file paths -> vscode://file/{resolved_root}/{task-rel path}
 * - Image src -> /files/{src}
 * - Wrap each block-level element in a .commentable-block container
 *   with data-section and data-block attributes (when sectionName given)
 */
function renderMarkdown(text, sectionName, taskPath, contentBase) {
  /* markdown-it runs with html:true so agent-authored HTML (layouts, diagrams,
     callouts) survives. Exports are published, so every render result is
     untrusted reader input — sanitize before it touches the DOM. DOMPurify's
     default allowlist strips scripts/iframes/event handlers/javascript: URLs;
     ADD_ATTR keeps class/style so authored HTML can use inline styles and the
     dashboard CSS tokens. <details>/<summary> are on the default allowlist. */
  var html = DOMPurify.sanitize(md.render(text), { ADD_ATTR: ['style', 'class'] });
  var container = document.createElement('div');
  container.innerHTML = html;

  /* Base directory for resolving relative paths within a task, derived from the
     resolved task root (any --root, not just `superRA`). Two bases:
     - taskDirRel: the task's dir relative to the resolved root (`taskPath/`),
       prepended to RESOLVED_ROOT (absolute) for the local vscode://file link.
     - repoPathPrefix: the same path prefixed with the root's repo-relative name
       (ROOT_PREFIX), passed to repoFileHref for the GitHub branch. */
  var artifactPath = contentBase && contentBase.artifactPath;
  var contentBaseDir = artifactPath ? artifactDirectory(artifactPath) : '';
  var taskDirRel = taskPath ? taskPath + '/' : '';
  var contentDirRel = taskDirRel + (contentBaseDir ? contentBaseDir + '/' : '');
  var rootRel = ROOT_PREFIX ? ROOT_PREFIX + '/' : '';
  var repoPathPrefix = rootRel + contentDirRel;
  /* The GitHub-branch prefix uses the repo-root-relative root path (so a tree
     below the repo root keeps its `docs/...` prefix); /files/ and vscode keep
     ROOT_PREFIX / RESOLVED_ROOT. */
  var repoRootRel = REPO_ROOT_PREFIX ? REPO_ROOT_PREFIX + '/' : '';
  var repoLinkPrefix = repoRootRel + contentDirRel;

  /* Rewrite relative links. A relative href that resolves to a real task in
     this tree becomes an internal hash link (#/<task-path>) so it focuses that
     card via the existing hashchange/setActive router; everything else (scripts,
     figures, paths outside the tree) keeps the vscode://file rewrite. */
  container.querySelectorAll('a[href]').forEach(function(a) {
    var href = a.getAttribute('href');
    var stepMatch=href&&href.match(/#step-([A-Za-z0-9][A-Za-z0-9._-]*)$/);
    if(stepMatch&&isRelativeResource(href)){
      var owner=href.startsWith('#')&&!artifactPath?taskPath:resolveInternalTaskPath(href,taskPath,contentBaseDir);
      if(owner!==null){a.setAttribute('href','#/'+owner+'?step='+encodeURIComponent(stepMatch[1]));a.classList.add('task-link');a.removeAttribute('target');return;}
    }
    if (href && isRelativeResource(href) && !href.startsWith('#')) {
      var internal = resolveInternalTaskPath(href, taskPath, contentBaseDir);
      if (internal !== null) {
        a.setAttribute('href', '#/' + internal);
        a.removeAttribute('target');
        a.classList.add('task-link');
      } else {
        /* Genuine file link. GitHub artifact exports keep GitHub-style anchors;
           local/editor links translate those anchors to VS Code's path:line[:col]
           form because vscode://file ignores a #L... fragment. */
        if (artifactPath) {
          var artifactTarget = resolveArtifactRelativePath(artifactPath, href);
          if (artifactTarget) {
            a.setAttribute('href', artifactOpenHref(taskPath, artifactTarget));
            a.setAttribute('target', '_blank');
            /* An attachment sits on disk under its task, so a local-open server
               hands it to the right application like any other file link; the
               raw /api/artifact href stays for modifier/middle clicks. The
               resolver already decoded and normalized the target. */
            if (window.LOCAL_OPEN) {
              a.setAttribute('data-open-path', taskRelOpenPath(taskPath, artifactTarget));
            }
          }
          return;
        }
        if (window.DOC_MODE) {
          /* Doc pages cite repo files by repo-root-relative path (the authoring
             contract), so the href IS the repo path — resolve it against the repo
             root, not the doc node's dir. A link to a sibling export the build
             emits beside the site (DOC_LOCAL_LINKS) is a build artifact, not a
             repo file, so it stays a plain relative href. */
          var docClean = href.replace(/[?#].*$/, '');
          if (DOC_LOCAL_LINKS.indexOf(docClean) !== -1) {
            a.setAttribute('target', '_blank');
            return;
          }
          if (REPO_FILE_BASE) {
            a.setAttribute('href', repoFileHref(href));
            a.setAttribute('target', '_blank');
          }
          /* No REPO_FILE_BASE (e.g. a local doc-mode preview): leave the
             repo-relative href untouched rather than forging a vscode:// path
             against the docs root, which would not resolve. */
          return;
        }
        if (REPO_FILE_BASE) {
          a.setAttribute('href', repoFileHref(repoLinkPrefix + href));
        } else {
          var relHref = href;
          var loc = '';
          var lm = relHref.match(/#L(\d+)(?:C(\d+))?(?:-L?\d+(?:C\d+)?)?$/);
          if (lm) {
            loc = ':' + lm[1] + (lm[2] ? ':' + lm[2] : '');
            relHref = relHref.slice(0, lm.index);
          }
          a.setAttribute('href', 'vscode://file/' + RESOLVED_ROOT + '/' + contentDirRel + relHref + loc);
          /* With the local-open route a plain click hands the file to the
             application this machine uses for its type; the vscode:// href above
             stays for modifier/middle clicks (and carries the line anchor, which
             an OS-level open cannot). Same project-root-relative composition the
             /files/ route is handed — but decoded: /files/ rides a URL path that
             the server decodes, while /api/open takes the path in a JSON body,
             which nothing decodes. */
          if (window.LOCAL_OPEN) {
            a.setAttribute('data-open-path', rootRel + contentDirRel + decodePathHref(relHref));
          }
        }
        a.setAttribute('target', '_blank');
      }
    }
  });

  /* Rewrite relative image sources. In server mode they resolve via the /files/
     route; in standalone mode there is no server, so resolve them relative to
     the dashboard file (STANDALONE_PLAN_DIR points at the embedded task tree)
     so figures load from a file:// open. */
  container.querySelectorAll('img[src]').forEach(function(img) {
    var src = img.getAttribute('src');
    if (src && isRelativeResource(src)) {
      if (artifactPath) {
        var artifactImage = resolveArtifactRelativePath(artifactPath, src);
        var artifactImageUrl = artifactImage
          ? artifactResourceUrl(taskPath, artifactImage)
          : '';
        if (artifactImageUrl) img.setAttribute('src', artifactImageUrl);
      } else if (window.STANDALONE) {
        /* Prefer the base64 data URI embedded at build time (figure-portable in a
           moved/offline file). Key it exactly as the build helper does: taskPath +
           '/' + src for a task body, bare src for the root body. Fall back to the
           relative-path rewrite when no embedded bytes exist for this src. */
        var key = taskPath ? taskPath + '/' + src : src;
        if (STANDALONE_IMAGES.hasOwnProperty(key)) {
          img.setAttribute('src', STANDALONE_IMAGES[key]);
        } else {
          var rel = taskPath ? STANDALONE_PLAN_DIR + taskPath + '/' + src : STANDALONE_PLAN_DIR + src;
          img.setAttribute('src', rel);
        }
      } else {
        /* Server mode: the /files/ route resolves relative to project_root
           (= resolved-root parent), so the path must carry the root's
           repo-relative name plus the task dir — the same repoPathPrefix the
           GitHub/relative-link branch builds (ROOT_PREFIX + '/' + taskPath + '/'). */
        img.setAttribute('src', wtUrl('/files/' + repoPathPrefix + src));
      }
    }
  });

  /* Wrap top-level block elements in commentable containers */
  if (sectionName) {
    var blockTags = ['P','UL','OL','PRE','BLOCKQUOTE','TABLE','H1','H2','H3','H4','H5','H6'];
    var children = Array.from(container.childNodes);
    var blockIndex = 0;
    for (var i = 0; i < children.length; i++) {
      var child = children[i];
      if (child.nodeType === 1 && blockTags.indexOf(child.tagName) >= 0) {
        var wrapper = document.createElement('div');
        wrapper.className = 'commentable-block';
        wrapper.setAttribute('data-section', sectionName);
        wrapper.setAttribute('data-block', blockIndex);
        container.insertBefore(wrapper, child);
        /* The comment "+" gutter button needs the server to persist a comment;
           in standalone mode there is no server, so omit it — no dead control. */
        if (!window.STANDALONE) {
          var btn = document.createElement('button');
          btn.className = 'comment-gutter-btn';
          btn.textContent = '+';
          btn.setAttribute('onclick', 'showCommentForm(this)');
          wrapper.appendChild(btn);
        }
        wrapper.appendChild(child);
        blockIndex++;
      }
    }
  }

  return container.innerHTML;
}

/* ── Theme toggle ── */
(function() {
  var saved = localStorage.getItem('dashboard-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

function toggleTheme() {
  var html = document.documentElement;
  var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('dashboard-theme', next);
}

/* Shared navigation state: layout changes do not change what is selected or filtered. */
var _workspaceFilters={statuses:[],tasks:null};
var _treeSidebarHidden=false;
var _filterExpanded=new Set(['']);
function normalizeWorkspaceFilters(value) {
  value=value||{};
  var selected=Array.isArray(value.tasks)?Array.from(new Set(value.tasks.filter(function(p){return typeof p==='string';}))).sort():null;
  if(selected===null&&Array.isArray(value.hidden)&&value.hidden.length)selected=workspaceTasks().filter(function(t){return !value.hidden.some(function(p){return typeof p==='string'&&reproWithin(t.path,p);});}).map(function(t){return t.path;});
  return {statuses:Array.isArray(value.statuses)?Array.from(new Set(value.statuses.filter(function(s){return ['not-started','in-progress','implemented','revise','approved','archived','postponed'].includes(s);}))).sort():[],tasks:selected};
}
function workspaceTasks() {
  var tasks={};
  (SEARCH_INDEX||[]).forEach(function(t){tasks[t.path]=t;});
  if(_reproData)(_reproData.graph.dependencies&&_reproData.graph.dependencies.tasks||[]).forEach(function(t){tasks[t.path]=Object.assign({},tasks[t.path],t);});
  return Object.values(tasks).sort(function(a,b){return a.path.localeCompare(b.path);});
}
function workspaceTaskMatches(path, task) {
  if(_workspaceFilters.tasks!==null&&!_workspaceFilters.tasks.includes(path))return false;
  if(!_workspaceFilters.statuses.length)return true;
  task=task||workspaceTasks().find(function(t){return t.path===path;});
  return !!task&&_workspaceFilters.statuses.includes(task.status);
}
function workspaceVisibility() {
  var tasks=workspaceTasks(),matches=new Set(),visible=new Set();
  tasks.forEach(function(t){if(workspaceTaskMatches(t.path,t)){matches.add(t.path);visible.add(t.path);var p=t.path;while(p){p=parentPath(p);visible.add(p);}}});
  return {matches:matches,visible:visible};
}
function workspaceGraph(graph) {
  var archived=graph.dependencies&&graph.dependencies.archived_tasks||[];
  if(archived.length){var catalog=workspaceTasks(),known=new Set(graph.dependencies.tasks.map(function(t){return t.path;})),extra=catalog.filter(function(t){return archived.includes(t.path)&&!known.has(t.path);});graph=Object.assign({},graph,{dependencies:Object.assign({},graph.dependencies,{tasks:graph.dependencies.tasks.concat(extra)})});}
  if(_workspaceFilters.tasks===null&&!_workspaceFilters.statuses.length)return graph;
  var visibility=workspaceVisibility(),steps=(graph.steps||[]).filter(function(s){return visibility.matches.has(s.task);}),names=new Set(steps.map(function(s){return s.name;}));
  var dependencies=Object.assign({},graph.dependencies),boundaries={};
  Object.keys(dependencies.boundaries||{}).forEach(function(k){var b=dependencies.boundaries[k];boundaries[k]=Object.assign({},b,{edges:(b.edges||[]).filter(function(e){return visibility.visible.has(e.from)&&visibility.visible.has(e.to);})});});
  dependencies.tasks=(dependencies.tasks||[]).filter(function(t){return visibility.visible.has(t.path);});
  dependencies.edges=(dependencies.edges||[]).filter(function(e){return visibility.visible.has(e.from)&&visibility.visible.has(e.to);});
  dependencies.boundaries=boundaries;
  return Object.assign({},graph,{dependencies:dependencies,tasks:(graph.tasks||[]).filter(function(t){return visibility.visible.has(t.path);}),steps:steps,step_edges:(graph.step_edges||[]).filter(function(e){return names.has(e.from)&&names.has(e.to);})});
}
function workspaceWriteHistory() {
  if(restoring)return;
  var hash=reproHash();
  if(location.hash!==hash)history.pushState({wt:ACTIVE_WT},'',hash);
}
function applyWorkspaceFilters(changed) {
  var visibility=workspaceVisibility();
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node){
    node.style.display=visibility.visible.has(node.dataset.path)?'':'none';
    node.classList.toggle('filter-context',visibility.visible.has(node.dataset.path)&&!visibility.matches.has(node.dataset.path));
    var steps=node.querySelector(':scope > .task-children > .nav-step-list');if(steps)steps.hidden=!visibility.matches.has(node.dataset.path);
  });
  var nav=document.getElementById('nav-tree'),empty=document.getElementById('navigation-empty');
  if(nav){if(!empty){empty=document.createElement('p');empty.id='navigation-empty';empty.className='repro-hint';nav.prepend(empty);}empty.hidden=visibility.visible.size>0;empty.textContent='No tasks match these filters.';}
  updateWorkspaceFilterSummary();refreshRovingTabindex();
  if(changed){
    if(_workspaceFilters.statuses.length){var ancestors=Array.from(visibility.visible).filter(function(p){return !visibility.matches.has(p);});restoreExpandedNavPaths(ancestors);ancestors.forEach(function(p){if(!_reproNav.expanded.includes(p))_reproNav.expanded.push(p);});}
    workspaceWriteHistory();
    if(currentView==='reproduction'&&_reproData)drawReproView(document.getElementById('view-reproduction'),_reproData);
    renderReproDetail(_reproSelected);
  }
}
function updateWorkspaceFilterSummary() {
  var host=document.getElementById('workspace-filter-summary');if(!host)return;
  var active=_workspaceFilters.statuses.length+(_workspaceFilters.tasks===null?0:1);
  host.hidden=!active;
  host.innerHTML=(_workspaceFilters.statuses.length?'<span>Status: '+escapeHtml(_workspaceFilters.statuses.join(', '))+'</span>':'')
    +(_workspaceFilters.tasks!==null?'<span>'+_workspaceFilters.tasks.length+' of '+workspaceTasks().length+' tasks selected</span>':'')
    +'<button class="hc-btn" onclick="clearWorkspaceFilters()">Clear filters</button>';
  var trigger=document.getElementById('filter-trigger');if(trigger){trigger.textContent=active?'Filter · '+active:'Filter';trigger.classList.toggle('active',!!active);}
  var notice=document.getElementById('selection-filter-notice');if(notice){notice.hidden=workspaceTaskMatches(activePath);notice.textContent='Hidden by filters. Clear filters to show this task in navigation.';}
  if(typeof reproSizeWorkspace==='function')reproSizeWorkspace();
}
function openWorkspaceFilter() {
  var dialog=document.getElementById('workspace-filter');
  document.getElementById('workspace-task-query').value='';
  renderWorkspaceFilter();dialog.showModal();
  loadReproData(false).then(renderWorkspaceFilter).catch(function(){});
}
function closeWorkspaceFilter() {document.getElementById('workspace-filter').close();document.getElementById('filter-trigger').focus();}
function renderWorkspaceFilter() {
  var host=document.getElementById('workspace-status-options');if(!host)return;
  host.innerHTML=['not-started','in-progress','implemented','revise','approved','archived','postponed'].map(function(status){return '<label><input type="checkbox" data-filter-status="'+status+'"'+(_workspaceFilters.statuses.includes(status)?' checked':'')+'> '+status+'</label>';}).join('');
  renderWorkspaceTaskOptions();
}
function renderWorkspaceTaskOptions() {
  var host=document.getElementById('workspace-task-options');if(!host)return;
  var q=document.getElementById('workspace-task-query').value.trim().toLowerCase(),tasks=workspaceTasks(),byPath={},children={};
  tasks.forEach(function(t){byPath[t.path]=t;children[t.path]=[];});
  tasks.forEach(function(t){if(t.path&&children[parentPath(t.path)])children[parentPath(t.path)].push(t.path);});
  var matches=new Set(tasks.filter(function(t){return (t.path+' '+t.title).toLowerCase().includes(q);}).map(function(t){return t.path;})),visible=new Set(matches);
  Array.from(matches).forEach(function(p){while(p){p=parentPath(p);visible.add(p);}});
  function branch(path){
    if(!visible.has(path))return '';
    var task=byPath[path],kids=children[path],descendants=tasks.filter(function(t){return reproWithin(t.path,path);}),selected=descendants.filter(function(t){return _workspaceFilters.tasks===null||_workspaceFilters.tasks.includes(t.path);}).length;
    var open=q?true:_filterExpanded.has(path),hasKids=kids.length>0;
    return '<div class="filter-task-branch"><div class="filter-task-row">'
      +(hasKids?'<button type="button" class="filter-task-fold" data-filter-fold="'+escapeAttr(path)+'" aria-expanded="'+open+'" aria-label="'+(open?'Collapse ':'Expand ')+escapeAttr(task.title||path||'Project root')+'">'+(open?'▾':'▸')+'</button>':'<span class="filter-task-leaf"></span>')
      +'<label><input type="checkbox" data-filter-task="'+escapeAttr(path)+'"'+(selected===descendants.length?' checked':'')+(selected>0&&selected<descendants.length?' data-partial="true"':'')+'><span>'+escapeHtml(task.title||path||'Project root')+'<small>'+escapeHtml(path||'Project root')+'</small></span></label>'
      +(hasKids?'<span class="filter-task-count">'+selected+'/'+descendants.length+'</span>':'')+'</div>'
      +(hasKids?'<div class="filter-task-children"'+(open?'':' hidden')+'>'+kids.map(branch).join('')+'</div>':'')+'</div>';
  }
  var roots=tasks.filter(function(t){return !t.path||!byPath[parentPath(t.path)];});
  host.innerHTML=roots.map(function(t){return branch(t.path);}).join('')||'<p>No tasks match.</p>';
  host.querySelectorAll('[data-partial]').forEach(function(input){input.indeterminate=true;});
}
function selectAllWorkspaceTasks(selected) {
  _workspaceFilters.tasks=selected?null:[];renderWorkspaceTaskOptions();applyWorkspaceFilters(true);
}
function clearWorkspaceFilters() {
  _workspaceFilters={statuses:[],tasks:null};applyWorkspaceFilters(true);renderWorkspaceFilter();
}
function workspaceSearchRecords() {
  var records=(SEARCH_INDEX||[]).slice();
  if(_reproData)(_reproData.graph.steps||[]).forEach(function(s){
    records.push({kind:'Step',step:s.name,path:s.task,title:s.name,slug:s.name,text:reproTaskTitle(s.task)});
    (s.outs||[]).forEach(function(out){var file=reproOutLabel(out);records.push({kind:'File',step:s.name,path:s.task,title:file,slug:file,text:s.name+' '+reproTaskTitle(s.task)});});
  });
  return records;
}
function syncTreeSteps() {
  if(!_reproData)return;
  var byTask={};(_reproData.graph.steps||[]).forEach(function(s){(byTask[s.task]||(byTask[s.task]=[])).push(s);});
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node){
    var steps=byTask[node.dataset.path]||[],children=node.querySelector(':scope > .task-children');
    if(!steps.length){var old=children&&children.querySelector(':scope > .nav-step-list');if(old)old.remove();return;}
    if(!children){children=document.createElement('div');children.className='task-children';children.style.display='none';node.appendChild(children);node.dataset.needsLoad='false';var caret=node.querySelector(':scope > .task-row > .task-toggle');if(caret){caret.classList.remove('leaf');caret.textContent='▸';}}
    var list=children.querySelector(':scope > .nav-step-list');if(!list){list=document.createElement('div');list.className='nav-step-list';children.prepend(list);}
    list.innerHTML=steps.map(function(s){return '<button type="button" class="nav-step'+(s.name===_reproSelected?' is-selected':'')+'" data-tree-step="'+escapeAttr(s.name)+'"'+(s.name===_reproSelected?' aria-current="true"':'')+'>'+escapeHtml(s.name)+'</button>';}).join('');
  });
}
function updateNavigationToggle() {
  var button=document.getElementById('navigation-toggle');if(!button)return;
  var graph=currentView==='reproduction',visible=graph?!_reproReaderClosed:!_treeSidebarHidden;
  button.textContent=(visible?'Hide ':'Show ')+(graph?'details':'sidebar');
  button.setAttribute('aria-controls',graph?'task-preview':'sidebar');button.setAttribute('aria-expanded',String(visible));
  document.getElementById('workspace').classList.toggle('tree-sidebar-hidden',_treeSidebarHidden);
  var hamburger=document.getElementById('nav-hamburger');if(hamburger)hamburger.hidden=graph;
}
function toggleNavigationPane() {
  if(currentView==='reproduction'){reproSetReader(_reproReaderClosed);updateNavigationToggle();return;}
  _treeSidebarHidden=!_treeSidebarHidden;
  try{localStorage.setItem('dashboard-tree-hidden',JSON.stringify(_treeSidebarHidden));}catch(e){}
  updateNavigationToggle();
  if(!_treeSidebarHidden&&window.innerWidth<=900)openDrawer();
}
function initWorkspaceControls() {
  try{_treeSidebarHidden=JSON.parse(localStorage.getItem('dashboard-tree-hidden'))===true;}catch(e){}
  updateNavigationToggle();
  var dialog=document.getElementById('workspace-filter');
  dialog.addEventListener('change',function(event){
    var input=event.target;
    if(input.dataset.filterStatus){var statuses=new Set(_workspaceFilters.statuses);if(input.checked)statuses.add(input.dataset.filterStatus);else statuses.delete(input.dataset.filterStatus);_workspaceFilters.statuses=Array.from(statuses).sort();}
    else if(input.hasAttribute('data-filter-task')){
      var path=input.dataset.filterTask,tasks=workspaceTasks(),selected=new Set(_workspaceFilters.tasks===null?tasks.map(function(t){return t.path;}):_workspaceFilters.tasks);
      tasks.forEach(function(t){if(reproWithin(t.path,path)){if(input.checked)selected.add(t.path);else selected.delete(t.path);}});
      _workspaceFilters.tasks=selected.size===tasks.length?null:Array.from(selected).sort();renderWorkspaceTaskOptions();
      var replacement=Array.from(dialog.querySelectorAll('[data-filter-task]')).find(function(el){return el.dataset.filterTask===path;});if(replacement)replacement.focus({preventScroll:true});
    }
    applyWorkspaceFilters(true);
  });
  dialog.addEventListener('click',function(e){var fold=e.target.closest('[data-filter-fold]');if(fold){var path=fold.dataset.filterFold;if(_filterExpanded.has(path))_filterExpanded.delete(path);else _filterExpanded.add(path);renderWorkspaceTaskOptions();var next=Array.from(dialog.querySelectorAll('[data-filter-fold]')).find(function(el){return el.dataset.filterFold===path;});if(next)next.focus();return;}if(e.target===dialog){var r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeWorkspaceFilter();}});
  loadReproData(false).then(function(){syncTreeSteps();updateSidebar(activePath);applyWorkspaceFilters(false);renderReproDetail(_reproSelected);}).catch(function(){});
}

/* ── View switching ── Workspace (master-detail drill-down) vs Kanban board ── */
var currentView = 'workspace';

function showView(view) {
  view=view==='reproduction'?'reproduction':'workspace';
  var reader=document.getElementById('task-preview'), scroll=reader.scrollTop, pageScroll=window.scrollY;
  var previousView=currentView;currentView=view;
  ['workspace','reproduction'].forEach(function(v){document.getElementById('btn-'+v).classList.toggle('active',v===view);});
  var workspace=document.getElementById('workspace');
  workspace.classList.remove('hidden');workspace.classList.toggle('dag-mode',view==='reproduction');
  workspace.classList.toggle('dag-reader-closed',_reproReaderClosed);
  document.getElementById('view-reproduction').classList.toggle('hidden',view!=='reproduction');
  document.getElementById('dag-reader-controls').classList.toggle('hidden',view!=='reproduction');
  updateNavigationToggle();
  if(view==='reproduction') {
    reproSizeWorkspace();_reproEntered=true;
    if(!restoring&&previousView==='workspace'&&activePath)reproRevealOwner(_reproSelected?activePath:parentPath(activePath));
    renderReproView(false);
  } else {
    _lastSidebarUpdate=updateSidebar(activePath);
    renderReproDetail(_reproSelected);
  }
  if(!restoring)workspaceWriteHistory();
  requestAnimationFrame(function(){reader.scrollTop=scroll;if(view==='workspace')window.scrollTo(0,pageScroll);});
}

/* ════════════════════════════════════════════════════════════════════════
   Full-text search-and-navigate (command palette)
   ──────────────────────────────────────────────────────────────────────
   Searches node titles AND flattened body text over SEARCH_INDEX, ranks
   matches, and on selection navigates exactly as a sidebar click via
   setActive() (same hash-routing, active highlight, scroll). No network at
   query time — the index is embedded; in server mode it is refreshed on a
   structural full-reload (refreshSearchIndex). Keyboard: '/' or Ctrl/Cmd-K
   opens; ↑/↓ move the active result, Enter opens it, Esc dismisses.
   ════════════════════════════════════════════════════════════════════════ */
var _searchResults = [];      /* current result records, in ranked order */
var _searchActiveIdx = -1;    /* index of the aria-selected result */
var SEARCH_MAX_RESULTS = 20;

/* Score one record against a lowercased query. Title hits outrank body hits;
   an earlier match position and a word-start match rank higher. Returns a
   positive score on a match, 0 on no match. */
function scoreSearchRecord(rec, q) {
  var title = (rec.title || '').toLowerCase();
  var slug = (rec.slug || '').toLowerCase();
  var text = (rec.text || '').toLowerCase();
  var score = 0;
  var ti = title.indexOf(q);
  if (ti !== -1) {
    score += 1000 - Math.min(ti, 100);
    if (ti === 0 || /\s/.test(title.charAt(ti - 1))) score += 200;  /* word start */
  }
  if (slug.indexOf(q) !== -1) score += 300;
  var bi = text.indexOf(q);
  if (bi !== -1) score += 100 - Math.min(Math.floor(bi / 10), 90);
  return score;
}

/* A short body snippet centered on the first query hit, with the match wrapped
   in <mark>. HTML-escaped so body text can't inject markup. */
function searchSnippet(rec, q) {
  var text = rec.text || '';
  var lower = text.toLowerCase();
  var i = lower.indexOf(q);
  if (i === -1) return '';
  var start = Math.max(0, i - 30);
  var slice = text.slice(start, i + q.length + 50);
  var pre = start > 0 ? '…' : '';
  var matchStart = i - start;
  var before = escapeHtml(slice.slice(0, matchStart));
  var hit = escapeHtml(slice.slice(matchStart, matchStart + q.length));
  var after = escapeHtml(slice.slice(matchStart + q.length));
  return pre + before + '<mark>' + hit + '</mark>' + after + '…';
}

function runSearch(query) {
  var q = (query || '').trim().toLowerCase();
  if (!q) return [];
  var scored = [], records=workspaceSearchRecords();
  for (var i = 0; i < records.length; i++) {
    var s = scoreSearchRecord(records[i], q);
    if (s > 0) scored.push({ rec: records[i], score: s });
  }
  scored.sort(function(a, b) { return b.score - a.score; });
  return scored.slice(0, SEARCH_MAX_RESULTS).map(function(x) { return x.rec; });
}

function renderSearchResults(query) {
  var list = document.getElementById('search-palette-results');
  var input = document.getElementById('search-palette-input');
  if (!list) return;
  _searchResults = runSearch(query);
  _searchActiveIdx = _searchResults.length ? 0 : -1;
  if (!query.trim()) {
    list.innerHTML = '';
    input.setAttribute('aria-expanded', 'false');
    return;
  }
  if (!_searchResults.length) {
    list.innerHTML = '<li class="search-palette-empty">No matches.</li>';
    input.setAttribute('aria-expanded', 'false');
    return;
  }
  var q = query.trim().toLowerCase();
  list.innerHTML = _searchResults.map(function(rec, idx) {
    var snippet = searchSnippet(rec, q);
    var pathLabel = (rec.kind||'Task')+' · '+(rec.path||'root')+(workspaceTaskMatches(rec.path||'')?'':' · Hidden by filters');
    return '<li class="search-result" role="option" data-idx="' + idx + '"'
      + (idx === 0 ? ' aria-selected="true"' : '')
      + ' onmousedown="onSearchResultClick(event, ' + idx + ')">'
      + '<span class="search-result-title">' + escapeHtml(rec.title || pathLabel) + '</span>'
      + '<span class="search-result-path">' + escapeHtml(pathLabel) + '</span>'
      + (snippet ? '<span class="search-result-snippet">' + snippet + '</span>' : '')
      + '</li>';
  }).join('');
  input.setAttribute('aria-expanded', 'true');
}

function highlightSearchResult(idx) {
  var list = document.getElementById('search-palette-results');
  if (!list) return;
  var items = list.querySelectorAll('.search-result');
  items.forEach(function(el, i) {
    if (i === idx) {
      el.setAttribute('aria-selected', 'true');
      el.scrollIntoView({ block: 'nearest' });
    } else {
      el.removeAttribute('aria-selected');
    }
  });
  _searchActiveIdx = idx;
}

function chooseSearchResult(idx) {
  var rec = _searchResults[idx];
  if (!rec) return;
  closeSearchPalette();
  if(rec.step)revealReproStep(rec.step);
  else {reproSelectTask(rec.path||'');if(currentView==='reproduction'){reproRevealOwner(parentPath(rec.path||''));drawReproView(document.getElementById('view-reproduction'),_reproData);reproCenter();}}
}

function onSearchResultClick(event, idx) {
  /* mousedown (not click) so the choice fires before the input's blur tears the
     palette down. */
  event.preventDefault();
  chooseSearchResult(idx);
}

function onSearchPaletteInput() {
  renderSearchResults(document.getElementById('search-palette-input').value);
}

function onSearchPaletteKeydown(event) {
  if (event.key === 'Escape') {
    event.preventDefault();
    closeSearchPalette();
  } else if (event.key === 'ArrowDown') {
    event.preventDefault();
    if (_searchResults.length) highlightSearchResult((_searchActiveIdx + 1) % _searchResults.length);
  } else if (event.key === 'ArrowUp') {
    event.preventDefault();
    if (_searchResults.length) highlightSearchResult((_searchActiveIdx - 1 + _searchResults.length) % _searchResults.length);
  } else if (event.key === 'Enter') {
    event.preventDefault();
    if (_searchActiveIdx >= 0) chooseSearchResult(_searchActiveIdx);
  }
}

function openSearchPalette() {
  var backdrop = document.getElementById('search-palette-backdrop');
  var palette = document.getElementById('search-palette');
  var input = document.getElementById('search-palette-input');
  if (!palette || !input) return;
  backdrop.classList.add('open');
  palette.classList.add('open');
  input.value = '';
  renderSearchResults('');
  input.focus();
  loadReproData(false).then(function(){if(palette.classList.contains('open'))renderSearchResults(input.value);}).catch(function(){});
}

function closeSearchPalette() {
  var backdrop = document.getElementById('search-palette-backdrop');
  var palette = document.getElementById('search-palette');
  if (backdrop) backdrop.classList.remove('open');
  if (palette) palette.classList.remove('open');
}

/* Refresh the embedded index from the server after a structural full-reload so
   live search reflects the current tree. No-op in standalone (no server). */
async function refreshSearchIndex() {
  if (window.STANDALONE) return;
  try {
    var resp = await fetch(wtUrl('/api/search-index'));
    if (resp.ok) SEARCH_INDEX = await resp.json();
  } catch (e) { /* keep the embedded index on failure */ }
}

/* Global key shortcut: '/' or Ctrl/Cmd-K opens the palette (unless the user is
   already typing in a field). */
document.addEventListener('keydown', function(event) {
  var inField = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement && document.activeElement.tagName);
  if ((event.key === 'k' || event.key === 'K') && (event.metaKey || event.ctrlKey)) {
    event.preventDefault();
    openSearchPalette();
  } else if (event.key === '/' && !inField) {
    event.preventDefault();
    openSearchPalette();
  }
});

/* ── Uncap helper: remove max-height after expand transition finishes ── */
function uncapAfterTransition(el) {
  var done = false;
  function finish() {
    if (done) return;
    done = true;
    el.removeEventListener('transitionend', handler);
    if (el.classList.contains('open')) el.classList.add('uncapped');
  }
  /* Wait for el's OWN max-height transition (0.3s) — not the shorter opacity/
     padding transitions (0.2s), and not a child's bubbled transitionend.
     Removing the listener on the first event of any property would fire before
     max-height finishes and leave content clipped at the animated cap. */
  function handler(e) {
    if (e.target === el && e.propertyName === 'max-height') finish();
  }
  el.addEventListener('transitionend', handler);
  /* Fallback: transitionend can be missed (interrupted/reduced-motion, or
     content shorter than the animated cap). Uncap unconditionally after the
     transition window so long bodies are never left capped. */
  setTimeout(finish, 400);
}

function recapForCollapse(el) {
  el.classList.remove('uncapped');
  el.style.maxHeight = el.scrollHeight + 'px';
  el.offsetHeight; /* force layout */
  el.classList.remove('open');
  el.style.maxHeight = '';
}

/* ── Section expand/collapse (inside task body) ── */
function toggleSection(toggleEl, event) {
  event.stopPropagation();
  var content = toggleEl.nextElementSibling;
  var icon = toggleEl.querySelector('.section-icon');
  var preview = toggleEl.querySelector('.section-preview');

  var wasOpen = content.classList.contains('open');

  if (wasOpen) {
    /* Collapse */
    icon.classList.remove('expanded');
    recapForCollapse(content);
    if (preview) preview.style.display = '';
  } else {
    /* Expand */
    content.classList.add('open');
    icon.classList.add('expanded');
    uncapAfterTransition(content);

    /* Determine section name from parent's data-section or the label */
    var sectionWrapper = toggleEl.closest('[data-section]');
    var sectionName = sectionWrapper ? sectionWrapper.getAttribute('data-section') : '';

    /* Get the task path for resolving relative paths */
    var taskNode = toggleEl.closest('.task-node');
    var taskPath = taskNode ? taskNode.dataset.path : '';

    /* Lazy-render markdown on first expand */
    var renderedMd = content.querySelector('.rendered-md');
    if (renderedMd && !renderedMd.dataset.rendered) {
      var tmpl = renderedMd.querySelector('script[type="text/x-markdown"]');
      if (tmpl) {
        renderedMd.innerHTML = renderMarkdown(tmpl.textContent, sectionName, taskPath);
        renderedMd.dataset.rendered = 'true';
      }
      if (sectionName === REPRO_SECTION) renderReproStepTable(renderedMd, taskPath);
    }
    if (preview) preview.style.display = 'none';

    /* Load comments for this task's section */
    if (taskNode) {
      loadComments(taskNode.dataset.path);
    }
  }
}

/* ── Search/Filter (client-side, descendant-aware) ── */
/* Fold-state snapshot captured the moment a filter becomes active (from the
   no-filter state), so clearing the filter restores the user's prior folds
   instead of leaving the tree force-expanded. Null whenever no filter is
   active. Keyed by data-path -> expanded?(bool). */
var preFilterFoldState = null;

/* Debounce entry point: base.html wires oninput/onchange straight to this
   name, so keeping it as the debounced wrapper (rather than editing those
   attributes) coalesces a fast keystroke burst into one tree scan instead of
   one full descendant scan per keystroke. */
var FILTER_DEBOUNCE_MS = 150;
var _filterDebounceTimer = null;
function applyFilters() {
  clearTimeout(_filterDebounceTimer);
  _filterDebounceTimer = setTimeout(applyFiltersNow, FILTER_DEBOUNCE_MS);
}

function applyFiltersNow() { applyWorkspaceFilters(false); }

/* Single post-order pass: each node's own row is evaluated once and combined
   bottom-up with its already-computed children, so no subtree is walked more
   than once per applyFiltersNow() call (the prior nodeMatchesStatus/
   nodeMatchesSearch each independently re-recursed a node's whole subtree,
   on top of applyFiltersToNode's own recursion into children — a row at
   depth d was visited once per ancestor).

   Status-match and search-match are accumulated independently across the
   subtree (a node's returned statusMatch/searchMatch is true if *any* node in
   its subtree — itself or a descendant — matches that filter alone), then
   ANDed for the node's own visibility. This reproduces the prior
   nodeMatchesStatus(el) && nodeMatchesSearch(el) semantics exactly, including
   its cross-descendant case: a branch can show as visible when one descendant
   satisfies the status pill and a different descendant satisfies the search
   text, with neither descendant matching both on its own. */
function applyFiltersToNode(el, status, search) {
  var statusMatch = !status || el.dataset.status === status;
  var searchMatch = !search;
  if (search) {
    var titleEl = el.querySelector(':scope > .task-row > .task-title-text');
    var slugEl = el.querySelector(':scope > .task-row > .task-slug');
    var title = titleEl ? titleEl.textContent.toLowerCase() : '';
    var slug = slugEl ? slugEl.textContent.toLowerCase() : '';
    var path = (el.dataset.path || '').toLowerCase();
    searchMatch = title.includes(search) || slug.includes(search) || path.includes(search);
  }
  el.querySelectorAll(':scope > .task-children > .task-node').forEach(function(child) {
    var childResult = applyFiltersToNode(child, status, search);
    if (childResult.statusMatch) statusMatch = true;
    if (childResult.searchMatch) searchMatch = true;
  });
  var visible = statusMatch && searchMatch;
  el.classList.toggle('hidden', !visible);
  return { statusMatch: statusMatch, searchMatch: searchMatch };
}

/* Record each loaded non-leaf nav node's expanded state by path, so it can be
   restored verbatim when the filter clears. */
function snapshotNavFolds() {
  var state = {};
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node) {
    var toggle = node.querySelector(':scope > .task-row > .task-toggle');
    if (!toggle || toggle.classList.contains('leaf')) return;
    var p = node.dataset.path;
    if (p === undefined) return;
    state[p] = toggle.classList.contains('expanded');
  });
  return state;
}

/* Set one node's fold open/closed without lazy-loading (search must not pull
   in deep branches). Mirrors expandNavNode's class/display contract. */
function setNavFold(node, open) {
  var toggle = node.querySelector(':scope > .task-row > .task-toggle');
  var children = node.querySelector(':scope > .task-children');
  if (!toggle || toggle.classList.contains('leaf') || !children) return;
  toggle.classList.toggle('expanded', open);
  children.style.display = open ? '' : 'none';
  var row = node.querySelector(':scope > .task-row');
  if (row) row.setAttribute('aria-expanded', open ? 'true' : 'false');
}

/* Restore folds from a snapshot; any node that appeared since (e.g. a branch
   the user lazy-loaded while searching) defaults to collapsed. */
function restoreNavFolds(state) {
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node) {
    var p = node.dataset.path;
    if (p === undefined) return;
    setNavFold(node, state[p] === true);
  });
}

/* After filtering, expand the ancestor chain of every still-visible matching
   row so matches are on screen. A node is a "match anchor" if it is not hidden
   and its own row matches (independent of descendants); we expand all of its
   ancestors. Operates only on rows already in the DOM. */
function revealFilterMatches(status, search) {
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node) {
    if (node.classList.contains('hidden')) return;
    if (!nodeOwnRowMatches(node, status, search)) return;
    /* Walk up through ancestor .task-node containers, expanding each. */
    var parent = node.parentElement
      ? node.parentElement.closest('.task-node') : null;
    while (parent) {
      setNavFold(parent, true);
      parent = parent.parentElement
        ? parent.parentElement.closest('.task-node') : null;
    }
  });
}

/* Whether this node's OWN row (not its descendants) satisfies the filter. */
function nodeOwnRowMatches(el, status, search) {
  if (status && el.dataset.status !== status) return false;
  if (search) {
    var titleEl = el.querySelector(':scope > .task-row > .task-title-text');
    var slugEl = el.querySelector(':scope > .task-row > .task-slug');
    var title = titleEl ? titleEl.textContent.toLowerCase() : '';
    var slug = slugEl ? slugEl.textContent.toLowerCase() : '';
    var path = (el.dataset.path || '').toLowerCase();
    if (!(title.includes(search) || slug.includes(search) || path.includes(search))) {
      return false;
    }
  }
  return true;
}

/* ── Kanban rendering ──
   Cards carry data-path (server-escaped) rather than an inline onclick built
   by interpolating the task path — a delegated listener on the container
   reads it back, mirroring onChildCardClick's pattern. */
/* ════════════════════════════════════════════════════════════════════════
   Reproduction view — reviewing the build graph the task tree declares
   ──────────────────────────────────────────────────────────────────────
   Two payloads back this view: /api/repro/graph (what the `## Reproduction`
   sections declare) and /api/repro/status (what the committed lock says each
   step's freshness is, plus its log tail). Both are fetched once and cached
   here; the node detail panel and the task-page step table read the same cached
   pair, so opening a task costs no request, and the standalone export embeds
   one snapshot of each.

   Nodes come from the graph and take their state from the status payload, so
   the graph still renders when the runner cannot read the lock (Python < 3.11
   has no tomllib) — every step then reads `unknown` under a banner.
   ════════════════════════════════════════════════════════════════════════ */

var REPRO_SECTION = 'Reproduction';

/* Every state ships its glyph and its word beside the colour: the palette's
   own comment names the pairs a red-green reader cannot separate by hue. */
var REPRO_STATES = [
  { key: 'fresh',    glyph: '●' },
  { key: 'stale',    glyph: '◐' },
  { key: 'missing',  glyph: '○' },
  { key: 'failed',   glyph: '✕' },
  { key: 'external', glyph: '⊘' },
  { key: 'unknown', glyph: '?' }
];
var REPRO_GLYPHS = {};
REPRO_STATES.forEach(function(s) { REPRO_GLYPHS[s.key] = s.glyph; });

var _reproData = null, _reproPending = null, _reproLoadSeq = 0;
var _reproSelected = '', _reproLinkOwner = null;
var _reproNav = { roots: [], view: 'graph', mode: 'scope', anchor: '', selected: '', expanded: [] };
var _reproEntered = false, _reproReaderFull = false, _reproReaderClosed = false, _reproLegacyReveal = false;
var _reproContext = [], _reproNotice = '', _reproLayoutCache = null;
var _reproViewport = { x: 0, y: 0, zoom: 1 }, _reproWorktrees = {};
var _reproInspectorClosed = false, _reproFitNext = true;

/* Pure projection: filters select matches; tracing retains actual dependencies. */
function reproWithin(path, root) { return root === '' || path === root || path.indexOf(root + '/') === 0; }
function reproRoots(roots) {
  return Array.from(new Set(roots)).sort().filter(function(root, i, all) {
    return !all.some(function(other) { return other !== root && reproWithin(root, other); });
  });
}
function reproMatches(step, nav) {
  return (!nav.roots.length || nav.roots.some(function(root) { return reproWithin(step.task, root); }));
}
function reproProject(graph, nav, context) {
  var byName = {}, incoming = {}, outgoing = {};
  (graph.steps || []).forEach(function(s) { byName[s.name] = s; incoming[s.name] = []; outgoing[s.name] = []; });
  (graph.step_edges || []).forEach(function(e) {
    if (byName[e.from] && byName[e.to]) { outgoing[e.from].push(e); incoming[e.to].push(e); }
  });
  var matches = (graph.steps || []).filter(function(s) { return reproMatches(s, nav); });
  var visible = new Set(nav.mode === 'scope' ? matches.map(function(s) { return s.name; }) : []);
  function walk(start, edges, direction, recurse) {
    var queue = [start], visited = new Set(queue);
    while (queue.length) {
      var name = queue.shift(); visible.add(name);
      (edges[name] || []).forEach(function(e) {
        var next = e[direction]; visible.add(next);
        if (recurse && !visited.has(next)) { visited.add(next); queue.push(next); }
      });
    }
  }
  if (nav.anchor && byName[nav.anchor] && nav.mode !== 'scope') {
    if (['nearby', 'upstream', 'both'].indexOf(nav.mode) !== -1) walk(nav.anchor, incoming, 'from', nav.mode !== 'nearby');
    if (['nearby', 'downstream', 'both'].indexOf(nav.mode) !== -1) walk(nav.anchor, outgoing, 'to', nav.mode !== 'nearby');
  }
  (context || []).forEach(function(n) { if (byName[n]) visible.add(n); });
  var boundary = [];
  (graph.step_edges || []).forEach(function(e) {
    if (visible.has(e.from) === visible.has(e.to)) return;
    var hidden = byName[visible.has(e.from) ? e.to : e.from];
    if (!hidden) return;
    var reasons = [];
    if (nav.roots.length && !nav.roots.some(function(r) { return reproWithin(hidden.task, r); })) reasons.push('subtree');
    if (!reasons.length) reasons.push('focus');
    boundary.push({ edge: e, hidden: hidden.name, visible: visible.has(e.from) ? e.from : e.to,
      direction: visible.has(e.from) ? 'Downstream' : 'Upstream', reasons: reasons });
  });
  return { matches: matches, steps: (graph.steps || []).filter(function(s) { return visible.has(s.name); }),
    edges: (graph.step_edges || []).filter(function(e) { return visible.has(e.from) && visible.has(e.to); }),
    boundary: boundary, incoming: incoming, outgoing: outgoing, byName: byName };
}
function reproSearch(steps, query) {
  query = query.toLowerCase().trim();
  return steps.filter(function(s) {
    return [s.name, s.task, reproTaskTitle(s.task)].concat((s.outs || []).map(reproOutLabel))
      .join(' ').toLowerCase().indexOf(query) !== -1;
  });
}
function reproHash() {
  var state={expanded:_reproNav.expanded||[],selected:_reproSelected||'',layout:currentView==='reproduction'?'graph':'tree',filters:_workspaceFilters};
  return '#/'+activePath+'?'+(activeArtifactPath?'attachment='+encodeURIComponent(activeArtifactPath)+'&':'')+'repro='+encodeURIComponent(JSON.stringify(state));
}
function reproReadHash() {
  var params=new URLSearchParams((location.hash||'').split('?').slice(1).join('?'));
  var raw=params.get('repro'), step=params.get('step');
  if(!raw&&!step){_workspaceFilters={statuses:[],tasks:null};_reproSelected='';_reproNav.selected='';var previous=restoring;restoring=true;showView('workspace');restoring=previous;applyWorkspaceFilters(false);return false;}
  try {
    var n=raw?JSON.parse(raw):{};
    _workspaceFilters=normalizeWorkspaceFilters(n.filters);
    _reproNav={roots:[],view:'graph',mode:'scope',anchor:'',
      expanded:Array.isArray(n.expanded)?n.expanded.filter(function(p){return typeof p==='string';}):[],
      selected:step||(typeof n.selected==='string'?n.selected:'')};
    _reproSelected=_reproNav.selected;_reproContext=[];_reproNotice='';
    _reproLinkOwner=step?parseHash():null;
    _reproInspectorClosed=false;_reproEntered=true;
    _reproLegacyReveal=!!step||!!(n.roots||n.mode||n.tier)||!Array.isArray(n.expanded);
    _reproFitNext=!(history.state&&history.state.rpViewport);
    if(!_reproFitNext)_reproViewport=Object.assign({},history.state.rpViewport);
    var previous=restoring;restoring=true;showView(n.layout==='tree'?'workspace':'reproduction');restoring=previous;
    applyWorkspaceFilters(false);
    if(n.layout==='tree')loadReproData(false).then(function(){renderReproDetail(_reproSelected);syncTreeSteps();});
    return true;
  } catch(e){return false;}
}
function reproNavigate(patch, overview) {
  if(patch.expanded)_reproNav.expanded=patch.expanded;
  if(typeof patch.selected==='string')_reproNav.selected=patch.selected;
  _reproNav.roots=[];_reproNav.mode='scope';_reproNav.anchor='';
  _reproSelected=_reproNav.selected;_reproContext=[];_reproNotice='';
  if(overview)_reproFitNext=true;
  var hash=reproHash();
  if(location.hash!==hash)history.pushState({wt:ACTIVE_WT},'',hash);
  if(currentView==='reproduction')drawReproView(document.getElementById('view-reproduction'),_reproData);
}

/* Coalesce the graph and status requests and ignore superseded loads. */
async function loadReproData(force) {
  if (_reproData && !force) return _reproData;
  if (_reproPending && !force) return _reproPending;
  var seq = ++_reproLoadSeq;
  var pending = (async function() {
    var g = await fetch(wtUrl('/api/repro/graph'));
    var s = await fetch(wtUrl('/api/repro/status'));
    if (!g.ok || !s.ok) throw new Error('reproduction data unavailable');
    var loaded = { graph: await g.json(), status: await s.json() };
    if (seq === _reproLoadSeq) _reproData = loaded;
    return loaded;
  })();
  _reproPending = pending;
  try { return await pending; } finally { if (_reproPending === pending) _reproPending = null; }
}

/* step name -> its status entry, for the states the graph's nodes wear. */
function reproStatusIndex(data) {
  var byName = {};
  (data.status.steps || []).forEach(function(e) { byName[e.name] = e; });
  return byName;
}

function reproStateOf(entry) { return entry ? entry.status : 'unknown'; }

function reproTaskTitle(path) {
  if (path === '') return pathTitles[''] || 'Root';
  return pathTitles[path] || path.split('/').pop();
}

function renderReproView(force) {
  var container = document.getElementById('view-reproduction');
  if (!container) return;
  if (!_reproData && !container.firstChild) container.innerHTML = '<div class="repro-empty">Loading the reproduction graph…</div>';
  var wt = ACTIVE_WT;
  loadReproData(force).then(function(data) {
    if (wt === ACTIVE_WT && data === _reproData) {
      var selected=(data.graph.steps||[]).find(function(s){return s.name===_reproSelected;});
      var reveal=!!selected&&_reproLegacyReveal;
      if(_reproLinkOwner!==null&&(!selected||selected.task!==_reproLinkOwner)){
        _reproNotice='Step '+_reproSelected+' is not declared in '+reproTaskTitle(_reproLinkOwner)+'.';
        _reproSelected='';_reproNav.selected='';selected=null;reveal=false;
      }
      _reproLinkOwner=null;
      if(reveal)reproRevealOwner(selected.task);
      _reproLegacyReveal=false;
      if(selected&&selected.task!==activePath){var was=restoring;restoring=true;setActive(selected.task);restoring=was;}
      drawReproView(container, data);
      if(reveal){_reproViewport.zoom=1;reproCenter();}
    }
  }).catch(function(e) {
    if (wt === ACTIVE_WT) container.innerHTML = '<div class="repro-empty">Could not load the reproduction graph: '
      + escapeHtml(e.message) + '</div>';
  });
}
function reproButton(label, action, value, accessibleLabel) {
  return '<button type="button" class="hc-btn"'+(accessibleLabel?' aria-label="'+escapeAttr(accessibleLabel)+'"':'')+' data-rp-action="' + action + '" data-value="'
    + escapeAttr(value || '') + '">' + escapeHtml(label) + '</button>';
}
function reproTasks(graph) {
  if (graph.dependencies) return (graph.dependencies.tasks || []).map(function(t) { return t.path; });
  var paths = new Set();
  (graph.tasks || []).forEach(function(t) { paths.add(t.path); });
  (graph.steps || []).forEach(function(s) { var p = s.task; paths.add(p); while (p) { p = parentPath(p); if (p) paths.add(p); } });
  return Array.from(paths).sort();
}

/* Project real endpoints through the nearest folded ancestor. Logical edges
   terminate at task boundaries; file edges retain their exact step evidence. */
function reproHierarchy(graph, nav, project) {
  var tasks = {}, children = {}, own = {}, nodes = [], edges = [], reps = {}, taskReps = {};
  var paths = reproTasks(graph), expanded = new Set(nav.expanded || []);
  var wanted = new Set(project.steps.map(function(s) { return s.name; }));
  (graph.dependencies && graph.dependencies.tasks || []).forEach(function(t) { tasks[t.path] = t; });
  paths.forEach(function(p) { tasks[p] = tasks[p] || {path:p, title:reproTaskTitle(p), status:''}; children[p] = []; own[p] = []; });
  paths.forEach(function(p) { var parent = parentPath(p); if (p && children[parent]) children[parent].push(p); });
  project.steps.forEach(function(s) { (own[s.task] || (own[s.task] = [])).push(s); });
  function matchesTask(p) { return !nav.roots.length || nav.roots.some(function(r) { return reproWithin(p,r); }); }
  var needed = new Set();
  paths.forEach(function(p) { if (nav.mode === 'scope' && matchesTask(p)) needed.add(p); });
  project.steps.forEach(function(s) { needed.add(s.task); });
  /* Logical prerequisites remain boundary context in a narrower scope. */
  var logical = [];
  Object.values(graph.dependencies && graph.dependencies.boundaries || {}).forEach(function(b) {
    b.edges.forEach(function(e) { (e.evidence || []).forEach(function(r) {
      if (r.kind === 'logical' && !logical.some(function(o) {return o.declaration === r.declaration;})) logical.push(r);
    }); });
  });
  var previousSize=-1;
  while(previousSize!==needed.size){previousSize=needed.size;Array.from(needed).forEach(function(p){while(p){p=parentPath(p);if(tasks[p])needed.add(p);}});logical.forEach(function(e){if(needed.has(e.to))needed.add(e.from);});}
  function visit(p, parent) {
    if (!needed.has(p)) return null;
    var id = 'task:' + p, descendants = project.steps.filter(function(s) { return reproWithin(s.task,p); });
    var kids = (children[p] || []).filter(function(c) {return needed.has(c);});
    var node = {id:id, task:p, type:'task', title:tasks[p].title, status:tasks[p].status,
      parent:parent, steps:descendants, outside:!matchesTask(p), expandable:kids.length > 0 || (own[p] || []).length > 0,
      expanded:expanded.has(p), children:[]};
    nodes.push(node); taskReps[p] = id;
    if (node.expanded && node.expandable) {
      (own[p] || []).forEach(function(s) { var n = {id:s.name, type:'step', step:s, parent:id, children:[]}; nodes.push(n); node.children.push(n); reps[s.name] = s.name; });
      kids.forEach(function(c) { var n = visit(c,id); if (n) node.children.push(n); });
    } else {
      descendants.forEach(function(s) {reps[s.name] = id;});
      paths.forEach(function(c) {if (reproWithin(c,p)) taskReps[c] = id;});
    }
    return node;
  }
  // Scope roots are the forest's visible boundary, while context keeps its owner.
  var roots = nav.roots.length ? nav.roots.slice() : paths.filter(function(p) { return p && !tasks[parentPath(p)]; });
  if (!nav.roots.length && tasks['']) roots = (children[''] || []).slice();
  project.steps.forEach(function(s) { if (!nav.roots.length && !s.task) return; if (!roots.some(function(r) {return reproWithin(s.task,r);})) roots.push(s.task); });
  logical.forEach(function(e) { if (needed.has(e.from) && !roots.some(function(r) {return reproWithin(e.from,r);})) roots.push(e.from); });
  if (!nav.roots.length && (own[''] || []).length) {
    (own[''] || []).forEach(function(s) { nodes.push({id:s.name,type:'step',step:s,parent:null,children:[]}); reps[s.name] = s.name; });
  }
  if (!roots.length && tasks[''] && !(own[''] || []).length) roots.push('');
  roots = reproRoots(roots).filter(function(p) {return tasks[p];});
  roots.forEach(function(p) { visit(p,null); });
  var bundled = {};
  function edge(from,to,evidence) {
    if (!from || !to || from === to) return;
    var key = JSON.stringify([from,to]);
    if (!bundled[key]) { bundled[key] = {from:from,to:to,evidence:[]}; edges.push(bundled[key]); }
    bundled[key].evidence.push(evidence);
  }
  project.edges.forEach(function(e) { edge(reps[e.from],reps[e.to],e); });
  logical.forEach(function(e) { edge(taskReps[e.from],taskReps[e.to],e); });
  return {nodes:nodes,edges:edges,reps:reps,taskReps:taskReps,logicalBoundary:logical.filter(function(e){return needed.has(e.to)&&(!taskReps[e.from]||!taskReps[e.to]);})};
}

function reproBranchExpansion(graph, nav, context, path, depth) {
  var project=reproProject(graph,nav,context), current=reproHierarchy(graph,nav,project);
  var visible=current.nodes.some(function(n){return n.type==='task'&&n.task===path&&!n.outside;})
    || (path===''&&!nav.roots.length);
  var levels=depth==='all'?Infinity:Number(depth), base=path?path.split('/').length:0;
  var expanded=(nav.expanded||[]).filter(function(p){return !reproWithin(p,path);});
  reproTasks(graph).forEach(function(p){
    var relative=(p?p.split('/').length:0)-base;
    if(reproWithin(p,path)&&relative<levels)expanded.push(p);
  });
  var candidate=reproHierarchy(graph,Object.assign({},nav,{expanded:expanded}),project);
  var branch=candidate.nodes.filter(function(n){return reproWithin(n.type==='task'?n.task:n.step.task,path);});
  return {visible:visible,expanded:expanded,total:candidate.nodes.length,
    tasks:branch.filter(function(n){return n.type==='task';}).length,
    steps:branch.filter(function(n){return n.type==='step';}).length};
}
function reproCloseGraphDetail() {
  var host=document.getElementById('repro-edge-detail');if(!host||!host.firstChild)return;
  host.innerHTML='';var canvas=document.querySelector('.repro-canvas');if(canvas)canvas.focus({preventScroll:true});
}
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
function reproEdgeLabel(lay,e){
  function name(id){var n=lay.model.nodes.find(function(n){return n.id===id;});return n&&n.type==='task'?(n.title||reproTaskTitle(n.task)):id;}
  return name(e.from)+' → '+name(e.to)+(e.cycle?' · '+e.cycleKind:'');
}
function reproHighlightEdge(container,wire){
  container.querySelectorAll('.is-edge-endpoint,.is-edge-active').forEach(function(el){el.classList.remove('is-edge-endpoint','is-edge-active');});
  container.classList.toggle('has-edge-focus',!!wire);
  var label=container.querySelector('#repro-connection-label');if(label)label.textContent=wire?wire.getAttribute('aria-label'):'';
  if(!wire)return;wire.classList.add('is-edge-active');
  container.querySelectorAll('[data-node-id]').forEach(function(node){if(node.dataset.nodeId===wire.dataset.from||node.dataset.nodeId===wire.dataset.to)node.classList.add('is-edge-endpoint');});
}
function reproBindEdges(container){
  container.onpointerover=function(e){var wire=e.target.closest('.rp-wire');if(wire)reproHighlightEdge(container,wire);};
  container.onpointerout=function(e){if(e.target.closest('.rp-wire'))reproHighlightEdge(container,container.querySelector('.rp-wire:focus'));};
  ['focusin','focusout'].forEach(function(type){container.removeEventListener(type,reproEdgeFocus);container.addEventListener(type,reproEdgeFocus);});
}
function reproEdgeFocus(event){reproHighlightEdge(event.currentTarget,event.type==='focusin'?event.target.closest('.rp-wire'):null);}
function reproGraphHTML(lay,statuses) {
  var html='<svg class="repro-edges" width="'+lay.width+'" height="'+lay.height+'"><defs><marker id="rp-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/></marker><marker id="rp-arrow-cycle" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z"/></marker><marker id="rp-arrow-active" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>';
  html+=lay.edges.map(function(e,i){return '<path class="rp-wire-halo" d="'+e.d+'"/><path class="rp-wire'+(e.cycle?' is-cycle':'')+(e.evidence.some(function(r){return (r.from||r.producer)===_reproSelected||(r.to||r.consumer)===_reproSelected;})?' is-lit':'')+'" id="rp-edge-'+escapeAttr(encodeURIComponent(JSON.stringify([e.from,e.to])))+'" tabindex="0" role="button" aria-label="'+escapeAttr(reproEdgeLabel(lay,e))+'" data-rp-action="edge" data-value="'+i+'" data-from="'+escapeAttr(e.from)+'" data-to="'+escapeAttr(e.to)+'" d="'+e.d+'" marker-end="url(#rp-arrow)"><title>'+escapeHtml(reproEdgeLabel(lay,e)+' · '+e.evidence.length+' connections')+'</title></path>';}).join('')+'</svg>';
  html+=lay.bands.filter(function(b){return b.label;}).map(function(b){return '<div class="rp-component-label" role="heading" aria-level="3" data-component-parent="'+escapeAttr(b.parent||'')+'" data-component-kind="'+(b.isolated?'isolated':'connected')+'" style="left:'+b.x+'px;top:'+b.y+'px;width:'+b.width+'px">'+escapeHtml(b.label)+'</div>';}).join('');
  html+=lay.model.nodes.map(function(n){var p=lay.pos[n.id],style='left:'+p.x+'px;top:'+p.y+'px;width:'+p.width+'px;height:'+p.height+'px';
    if(n.type==='step') {var st=reproStateOf(statuses[n.id]);return '<button class="repro-node rp-'+st+(n.cycle?' is-cycle':'')+(n.id===_reproSelected?' is-selected':'')+'" data-rp-action="select" data-value="'+escapeAttr(n.id)+'" data-node-id="'+escapeAttr(n.id)+'" data-step="'+escapeAttr(n.id)+'" id="'+reproNodeId(n.id)+'" style="'+style+'"><span class="repro-node-name">'+escapeHtml(n.id)+'</span><span class="repro-node-state">'+(REPRO_GLYPHS[st]||'?')+' '+st+(n.cycle?' · '+n.cycleKind:'')+(n.step.kind==='check'?' · check':'')+(!reproMatches(n.step,_reproNav)?' · Outside scope':'')+'</span></button>';}
    var counts={};n.steps.forEach(function(s){var st=reproStateOf(statuses[s.name]);counts[st]=(counts[st]||0)+1;});
    var containsSelected=!n.expanded&&n.steps.some(function(s){return s.name===_reproSelected;});
    var summary=(n.outside?'Outside scope · ':'')+n.steps.length+' steps'+(n.steps.length?' · ':'')+Object.keys(counts).map(function(k){return (REPRO_GLYPHS[k]||'?')+' '+k+' '+counts[k];}).join(' · ');
    return '<section class="rp-task'+(n.cycle?' is-cycle':'')+(n.expanded&&n.expandable?' rp-expanded':'')+(!_reproSelected&&n.task===activePath?' is-selected':'')+'" data-node-id="'+escapeAttr(n.id)+'" data-task="'+escapeAttr(n.task)+'" style="'+style+'"><div class="rp-task-head">'+(n.expandable?reproButton(n.expanded?'▾':'▸','fold',n.task,(n.expanded?'Fold ':'Expand ')+(n.title||reproTaskTitle(n.task))):'')+'<button class="rp-task-title" title="'+escapeAttr(n.title||reproTaskTitle(n.task))+'" data-rp-action="task" data-value="'+escapeAttr(n.task)+'">'+escapeHtml(n.title||reproTaskTitle(n.task))+'</button></div><div class="rp-task-meta"><span class="badge badge-'+escapeAttr(n.status)+'">'+escapeHtml(n.status)+'</span> <span class="rp-task-path" title="'+escapeAttr(n.task)+'">'+escapeHtml(n.task||'Project root')+'</span><span class="rp-task-freshness" title="'+escapeAttr(summary)+'">'+(n.cycle?'<span class="rp-cycle-label" aria-label="'+escapeAttr(n.cycleKind)+'" title="'+escapeAttr(n.cycleKind)+'">↻ Cycle · </span>':'')+'<span class="rp-task-summary"'+(containsSelected?' hidden':'')+'>'+escapeHtml(summary)+'</span><span class="rp-selected-inside"'+(containsSelected?'':' hidden')+'>Contains selected step</span></span>'+'</div></section>';
  }).join('');return html;
}
function reproHeadHTML() {
  return '<div class="repro-head"><div class="repro-heading"><strong>Project graph</strong></div></div>';
}
function reproControlsHTML() {
  return '<div class="repro-controls">'+reproButton('Project overview','overview')+'</div>';
}
function drawReproView(container,data) {
  if(!container||!data)return;
  (data.graph.dependencies && data.graph.dependencies.tasks || []).forEach(function(t){pathTitles[t.path]=t.title;});
  var focused=document.activeElement,focusId=focused&&focused.id;
  var openMenu=container.querySelector('.rp-menu[open]');
  var menuKey=openMenu&&openMenu.dataset.rpMenu;
  var visibleGraph=workspaceGraph(data.graph),project=reproProject(visibleGraph,_reproNav,_reproContext),statuses=reproStatusIndex(data),paths=reproTasks(data.graph);
  if(_reproSelected&&!(data.graph.steps||[]).some(function(s){return s.name===_reproSelected;})){_reproNotice='The selected step was removed. Select another step.';_reproSelected='';_reproNav.selected='';}
  if(_reproNav.anchor&&!project.byName[_reproNav.anchor]){_reproNav.anchor='';_reproNav.mode='scope';project=reproProject(data.graph,_reproNav,[]);}
  var missing=_reproNav.roots.filter(function(r){return paths.indexOf(r)<0;});
  var model=reproHierarchy(visibleGraph,_reproNav,project);
  var signature=JSON.stringify([model.nodes.map(function(n){return [n.id,n.parent,n.expanded];}),model.edges]);
  var oldCanvas=container.querySelector('.repro-canvas'),same=_reproLayoutCache&&_reproLayoutCache.signature===signature&&oldCanvas;
  if(oldCanvas){_reproViewport.x-=oldCanvas.scrollLeft;_reproViewport.y-=oldCanvas.scrollTop;oldCanvas.scrollLeft=0;oldCanvas.scrollTop=0;}
  var oldLayout=_reproLayoutCache&&_reproLayoutCache.layout, lay=same?_reproLayoutCache.layout:reproHierarchyLayout(model);
  lay.model=model;model.nodes.forEach(function(n){n.cycle=!!lay.cycles[n.id];n.cycleKind=lay.cycles[n.id]||'';});
  var anchor=_reproPreserve||_reproSelected||'task:'+activePath;_reproPreserve='';
  if(!same&&oldLayout&&oldLayout.pos[anchor]&&lay.pos[anchor]&&!_reproFitNext){_reproViewport.x+=(oldLayout.pos[anchor].x-lay.pos[anchor].x)*_reproViewport.zoom;_reproViewport.y+=(oldLayout.pos[anchor].y-lay.pos[anchor].y)*_reproViewport.zoom;}
  _reproLayoutCache={signature:signature,layout:lay};
  var findings=(data.graph.findings||[]).concat(data.status.findings||[]).filter(function(f,i,a){return a.findIndex(function(o){return JSON.stringify(o)===JSON.stringify(f);})===i;});
  var notice=missing.length?'Selected subtree was removed or archived: '+missing.join(', ')+'. Use Whole project to recover.':!workspaceTaskMatches(activePath)?'Selected task is hidden by filters.':!model.taskReps[activePath]&&activePath?'This task is not in the active project graph.':'';
  var errors=findings.filter(function(f){return f.severity==='error';}).length;
  var diagnosticLabel=(errors?errors+' error'+(errors===1?'':'s'):'')+(errors&&findings.length>errors?' · ':'')+(findings.length>errors?(findings.length-errors)+' warning'+(findings.length-errors===1?'':'s'):'');
  var outside=project.steps.filter(function(s){return !reproMatches(s,_reproNav);}).length;
  container.innerHTML=reproHeadHTML()+reproControlsHTML(data,project)
    +'<div class="repro-summary"><span>'+project.matches.length+' steps'+(outside?' · '+outside+' outside scope':'')+(window.STANDALONE?' · snapshot':'')+'</span><details class="rp-menu rp-legend-menu" data-rp-menu="legend"><summary>Status key</summary><div class="rp-menu-body">'+reproLegendHTML(project.matches,statuses,data.status)+'</div></details>'
    +(findings.length?'<details class="rp-menu rp-diagnostics" data-rp-menu="diagnostics"><summary>'+escapeHtml(diagnosticLabel)+(errors?' · graph blocked':'')+'</summary><div class="rp-menu-body">'+reproFindingsHTML(findings)+'</div></details>':'')
    +(data.status.unavailable?'<span class="repro-hint">State unavailable</span>':'')+'</div>'
    +'<p id="repro-notice" role="status">'+escapeHtml(_reproNotice||notice)+'</p>'
    +'<div class="repro-stage"><div class="repro-canvas" tabindex="0" aria-label="Dependency graph. Scroll or drag to pan; pinch to zoom. Arrow keys pan, plus and minus zoom, zero fits."><div class="repro-plot" style="width:'+lay.width+'px;height:'+lay.height+'px">'+reproGraphHTML(lay,statuses)+'</div></div>'
    +(!model.nodes.length?'<p class="repro-empty">'+((_workspaceFilters.tasks!==null||_workspaceFilters.statuses.length)?'No tasks match these filters. Use Clear filters to restore all tasks.':paths.length?'No active tasks are available in the project graph.':'No active tasks in this tree.')+'</p>':'')
    +'<div class="repro-viewport-controls" aria-label="Graph viewport"><button class="hc-btn" data-rp-action="zoom-out" aria-label="Zoom out">−</button><span id="repro-zoom"></span><button class="hc-btn" data-rp-action="zoom-in" aria-label="Zoom in">+</button>'+reproButton('Fit','fit')+'</div><span class="repro-gesture-hint">Scroll to pan · pinch to zoom</span><div id="repro-connection-label" role="status"></div><div id="repro-edge-detail"></div></div>'
    +'<div class="repro-footer"><span id="repro-selection" title="'+escapeAttr(_reproSelected||activePath)+'">'+escapeHtml(_reproSelected||reproTaskTitle(activePath))+'</span></div>';


  if(same){var fresh=container.querySelector('.repro-canvas');oldCanvas.querySelector('.repro-plot').innerHTML=reproGraphHTML(lay,statuses);fresh.replaceWith(oldCanvas);}
  container.onclick=onReproClick;
  reproBindEdges(container);
  container.onkeydown=function(e){if(e.key==='Escape'){container.querySelectorAll('.rp-menu[open]').forEach(function(menu){menu.open=false;menu.querySelector('summary').focus();});reproCloseGraphDetail();}if((e.key==='Enter'||e.key===' ')&&e.target.matches('.rp-wire')){e.preventDefault();onReproClick(e);}};
  reproBindHead(container);reproBindViewport(container);renderReproDetail(_reproSelected);reproReaderControls();reproSizeWorkspace();
  if(menuKey){var menu=container.querySelector('[data-rp-menu="'+menuKey+'"]');if(menu)menu.open=true;}
  if(_reproFitNext){_reproFitNext=false;reproFit();}else reproTransform();
  if(focusId){var target=document.getElementById(focusId);if(target)target.focus({preventScroll:true});}
}
var _reproPreserve='';
function reproEvidenceHTML(evidence){
  return '<ul>'+evidence.map(function(e){return '<li>'+escapeHtml(e.kind==='logical'?'Logical prerequisite · '+e.declaration:(e.producer||e.from)+' → '+(e.consumer||e.to)+' via '+e.via)+'</li>';}).join('')+'</ul>';
}
function reproLogicalBoundaryHTML(model){
  if(!model.logicalBoundary.length)return '';
  return '<details class="repro-boundaries" open><summary>Inherited logical prerequisites outside this view</summary>'+model.logicalBoundary.map(function(e){return '<div>'+reproButton(reproTaskTitle(e.from),'task',e.from)+' → '+reproButton(reproTaskTitle(e.to),'task',e.to)+'<p>'+escapeHtml(e.declaration)+' · Applies to scoped descendant work.</p></div>';}).join('')+'</details>';
}
function reproReaderControls(){
  var toggle=document.getElementById('navigation-toggle');if(toggle){toggle.setAttribute('aria-expanded',String(!_reproReaderClosed));toggle.classList.toggle('active',!_reproReaderClosed);toggle.textContent=_reproReaderClosed?'Show details':'Hide details';toggle.title=_reproReaderClosed?'Show details':'Hide details';}
  var selection=document.getElementById('repro-selection');if(selection){selection.textContent=_reproSelected||reproTaskTitle(activePath);selection.title=_reproSelected||activePath;}
  updateNavigationToggle();
  var host=document.getElementById('dag-reader-controls');if(host)host.innerHTML=reproButton('Show in graph','show-selected',activePath)+reproButton((_reproReaderFull||_reproReaderCompact)?'Back to graph':'Read full width','full-reader')+reproButton('Hide details','close-reader');
  if(host&&_reproData){var edges=(_reproData.graph.dependencies&&_reproData.graph.dependencies.edges||[]).filter(function(e){return e.from===activePath||e.to===activePath;});
    if(edges.length)host.innerHTML+='<details class="rp-task-deps"><summary>Task dependencies ('+edges.length+')</summary>'+edges.map(function(e){var other=e.to===activePath?e.from:e.to;return '<div>'+reproButton((e.to===activePath?'Prerequisite: ':'Dependent: ')+reproTaskTitle(other),'task',other)+reproEvidenceHTML(e.evidence||[])+'</div>';}).join('')+'</details>';
  }
  if(host)host.parentElement.style.setProperty('--dag-reader-offset',(host.offsetHeight+12+parseFloat(getComputedStyle(host.parentElement).paddingTop||0))+'px');
}
async function reproOpenDeclaration() {
  var selected=_reproSelected;
  _reproSelected='';_reproNav.selected='';renderReproDetail('');syncTreeSteps();
  if(location.hash!==reproHash())history.pushState({wt:ACTIVE_WT},'',reproHash());
  if(currentView==='reproduction'){
    reproSetReader(true);_reproReaderFull=true;
    document.getElementById('workspace').classList.add('dag-full-reader');reproReaderControls();
  }
  var path=activePath;
  await loadActiveNode(path);
  if(activePath!==path)return;
  var section=document.querySelector('#active-node [data-section="Reproduction"]');
  if(section){var content=section.querySelector('.section-content');if(content&&!content.classList.contains('open'))toggleSection(section.querySelector('.section-toggle'),{stopPropagation:function(){}});section.scrollIntoView({block:'start'});var row=document.getElementById('step-'+selected);if(row)row.classList.add('is-selected');}
}
function reproFocus(path) {
  loadReproData(false).then(function(){
    reproRevealOwner(parentPath(path));
    if(currentView!=='reproduction')showView('reproduction');
    reproSelectTask(path);reproNavigate({},false);_reproViewport.zoom=1;reproCenter();
  });
}
function reproRevealOwner(path){
  var expanded=new Set(_reproNav.expanded||[]);var p=path;expanded.add(p);while(p){p=parentPath(p);expanded.add(p);}_reproNav.expanded=Array.from(expanded);
}
function reproSelectTask(path){
  _reproNav.selected='';_reproSelected='';_reproInspectorClosed=false;
  setActive(path);renderReproDetail('');reproReaderControls();
  var notice=document.getElementById('repro-notice');if(notice)notice.textContent='';
  document.querySelectorAll('.rp-task').forEach(function(n){
    n.classList.toggle('is-selected',n.dataset.task===path);
    var indicator=n.querySelector('.rp-selected-inside'),summary=n.querySelector('.rp-task-summary');
    if(indicator)indicator.hidden=true;if(summary)summary.hidden=false;
  });
}

var _reproReaderPreference=null, _reproReaderSizes={side:420,bottom:300}, _reproReaderPlacement='side', _reproReaderCompact=false;
function reproPaneBounds(){
  var ws=document.getElementById('workspace'),width=ws.clientWidth,height=ws.clientHeight,side=width>=1100;
  var min=side?300:Math.min(220,Math.max(160,height*.3));
  return {placement:side?'side':'bottom',split:side?height>=320:height>=(width<=620?620:570),automatic:side?height>=420:height>=650,min:Math.round(min),max:Math.round(Math.max(min,side?width-530:height-(width<=620?390:340)-10))};
}
function reproPersistReader(){try{localStorage.setItem('dashboard-dag-preview',JSON.stringify({visible:_reproReaderPreference,side:_reproReaderSizes.side,bottom:_reproReaderSizes.bottom}));}catch(e){}}
function reproSizeWorkspace() {
  var workspace=document.getElementById('workspace');
  if(currentView!=='reproduction'||!workspace)return;
  workspace.style.setProperty('--dag-top',Math.max(0,workspace.getBoundingClientRect().top)+'px');
  var bounds=reproPaneBounds();_reproReaderPlacement=bounds.placement;
  _reproReaderClosed=!_reproReaderFull&&(_reproReaderPreference===null?!bounds.automatic:!_reproReaderPreference);
  _reproReaderCompact=!_reproReaderClosed&&!_reproReaderFull&&!bounds.split;
  workspace.classList.toggle('dag-full-reader',_reproReaderFull||_reproReaderCompact);
  workspace.classList.toggle('dag-reader-bottom',bounds.placement==='bottom');
  workspace.classList.toggle('dag-reader-closed',_reproReaderClosed);
  var size=Math.max(bounds.min,Math.min(bounds.max,_reproReaderSizes[bounds.placement]));
  workspace.style.setProperty('--dag-preview-size',size+'px');
  var divider=document.getElementById('dag-preview-resizer');
  if(divider){divider.setAttribute('aria-orientation',bounds.placement==='side'?'vertical':'horizontal');divider.setAttribute('aria-label',bounds.placement==='side'?'Resize task preview width':'Resize task preview height');divider.setAttribute('aria-valuemin',String(bounds.min));divider.setAttribute('aria-valuemax',String(bounds.max));divider.setAttribute('aria-valuenow',String(Math.round(size)));}
  reproReaderControls();
}
function initReproReader(){
  try{var saved=JSON.parse(localStorage.getItem('dashboard-dag-preview'));if(saved){if(typeof saved.visible==='boolean')_reproReaderPreference=saved.visible;['side','bottom'].forEach(function(key){if(Number.isFinite(saved[key])&&saved[key]>=120)_reproReaderSizes[key]=saved[key];});}}catch(e){}
  var divider=document.getElementById('dag-preview-resizer'),ws=document.getElementById('workspace'),drag=null;
  if(!divider)return;
  function update(value){var bounds=reproPaneBounds();_reproReaderSizes[bounds.placement]=Math.max(bounds.min,Math.min(bounds.max,Math.round(value)));reproSizeWorkspace();}
  function move(e){if(!drag||e.pointerId!==drag.id)return;if(reproPaneBounds().placement!==drag.placement){finish(e);return;}update(drag.size+(drag.placement==='side'?drag.x-e.clientX:drag.y-e.clientY));}
  function finish(e){if(!drag)return;drag=null;ws.classList.remove('dag-resizing');try{divider.releasePointerCapture(e.pointerId);}catch(error){}window.removeEventListener('pointermove',move);window.removeEventListener('pointerup',finish);window.removeEventListener('pointercancel',finish);reproPersistReader();}
  divider.addEventListener('pointerdown',function(e){if(e.button!==0)return;e.preventDefault();divider.focus({preventScroll:true});drag={id:e.pointerId,x:e.clientX,y:e.clientY,size:Number(divider.getAttribute('aria-valuenow')),placement:_reproReaderPlacement};ws.classList.add('dag-resizing');try{divider.setPointerCapture(e.pointerId);}catch(error){}window.addEventListener('pointermove',move);window.addEventListener('pointerup',finish);window.addEventListener('pointercancel',finish);});
  divider.addEventListener('keydown',function(e){var bounds=reproPaneBounds(),step=e.shiftKey?48:16,value=Number(divider.getAttribute('aria-valuenow')),increase=bounds.placement==='side'?'ArrowLeft':'ArrowUp',decrease=bounds.placement==='side'?'ArrowRight':'ArrowDown';if(e.key===increase)value+=step;else if(e.key===decrease)value-=step;else if(e.key==='Home')value=bounds.min;else if(e.key==='End')value=bounds.max;else return;e.preventDefault();update(value);reproPersistReader();});
}
window.addEventListener('resize',reproSizeWorkspace);
new ResizeObserver(reproSizeWorkspace).observe(document.querySelector('.header'));
document.addEventListener('pointerdown',function(e){
  if(currentView!=='reproduction')return;
  document.querySelectorAll('#view-reproduction .rp-menu[open]').forEach(function(menu){if(!menu.contains(e.target))menu.open=false;});
});
function reproSetReader(open) {
  _reproReaderPreference=!!open;_reproReaderClosed=!open;reproPersistReader();
  var workspace=document.getElementById('workspace');
  workspace.classList.toggle('dag-reader-closed',!open);
  if(!open){_reproReaderFull=false;workspace.classList.remove('dag-full-reader');}
  reproSizeWorkspace();
  if(!open){var toggle=document.getElementById('navigation-toggle');if(toggle)toggle.focus({preventScroll:true});}
}
function reproBindHead(container) {
  container.querySelectorAll('.rp-menu').forEach(function(menu){menu.ontoggle=function(){if(menu.open)container.querySelectorAll('.rp-menu').forEach(function(other){if(other!==menu)other.open=false;});};});
}
function reproBoundaryHTML(project) {
  var groups = {};
  project.boundary.forEach(function(b) { var key = b.visible + '|' + b.direction; (groups[key] = groups[key] || []).push(b); });
  return '<div class="repro-boundaries">' + Object.keys(groups).map(function(key) {
    var items = groups[key];
    return '<details><summary>' + escapeHtml(items[0].visible) + ' · ' + items[0].direction + ' · '
      + new Set(items.map(function(b) { return b.hidden; })).size + ' hidden neighbors ('
      + Array.from(new Set(items.flatMap(function(b) { return b.reasons; }))).join(', ') + ')</summary>'
      + items.map(function(b) { return '<div>' + reproButton('Reveal ' + b.hidden, 'reveal', b.hidden)
        + ' via ' + escapeHtml(b.edge.via || '') + '</div>'; }).join('') + '</details>';
  }).join('') + '</div>';
}
function reproTransform() {
  var plot = document.querySelector('#view-reproduction .repro-plot');
  if (!plot) return;
  plot.style.transform = 'translate(' + _reproViewport.x + 'px,' + _reproViewport.y + 'px) scale(' + _reproViewport.zoom + ')';
  plot.classList.toggle('is-zoomed-out', _reproViewport.zoom < 0.55);
  if(currentView==='reproduction')history.replaceState(Object.assign({},history.state||{},{rpViewport:Object.assign({},_reproViewport)}),'',location.href);
  document.getElementById('repro-zoom').textContent = Math.round(_reproViewport.zoom * 100) + '%';
}
function reproFit() {
  var canvas = document.querySelector('#view-reproduction .repro-canvas');
  if (!canvas || !_reproLayoutCache) return;
  var lay = _reproLayoutCache.layout;
  _reproViewport = { x: 12, y: 12, zoom: Math.min(1, (canvas.clientWidth - 24) / lay.width, (canvas.clientHeight - 24) / lay.height) };
  reproTransform();
}
function reproCenter() {
  var canvas = document.querySelector('#view-reproduction .repro-canvas');
  var layout=_reproLayoutCache&&_reproLayoutCache.layout;
  var pos=layout&&layout.pos[(_reproSelected&&layout.model.reps[_reproSelected])||layout.model.taskReps[activePath]||'task:'+activePath];
  if (!canvas || !pos) return;
  _reproViewport.x = canvas.clientWidth / 2 - (pos.x + pos.width / 2) * _reproViewport.zoom;
  _reproViewport.y = canvas.clientHeight / 2 - (pos.y + Math.min(pos.height,108) / 2) * _reproViewport.zoom;
  reproTransform();
}
function reproZoomAt(canvas, zoom, x, y) {
  zoom=Math.max(0.05,Math.min(3,zoom));
  var ratio=zoom/_reproViewport.zoom;
  _reproViewport.x=x-(x-_reproViewport.x)*ratio;
  _reproViewport.y=y-(y-_reproViewport.y)*ratio;
  _reproViewport.zoom=zoom;reproTransform();
}
function reproBindViewport(container) {
  var canvas = container.querySelector('.repro-canvas');
  if (!canvas || canvas._rpBound) return;
  canvas._rpBound=true;
  var drag=null, gesture=null;
  function point(e) {
    var rect=canvas.getBoundingClientRect();
    return {x:Number.isFinite(e.clientX)?e.clientX-rect.left:canvas.clientWidth/2,
      y:Number.isFinite(e.clientY)?e.clientY-rect.top:canvas.clientHeight/2};
  }
  canvas.addEventListener('wheel',function(e){
    e.preventDefault();
    if(gesture)return;
    var unit=e.deltaMode===1?16:e.deltaMode===2?canvas.clientHeight:1;
    if(e.ctrlKey){var at=point(e);reproZoomAt(canvas,_reproViewport.zoom*Math.exp(-e.deltaY*unit*0.01),at.x,at.y);}
    else{_reproViewport.x-=e.deltaX*unit;_reproViewport.y-=e.deltaY*unit;reproTransform();}
  },{passive:false});
  canvas.addEventListener('gesturestart',function(e){
    e.preventDefault();gesture={zoom:_reproViewport.zoom,scale:e.scale||1};drag=null;
  },{passive:false});
  canvas.addEventListener('gesturechange',function(e){
    e.preventDefault();if(!gesture)return;
    var at=point(e);reproZoomAt(canvas,gesture.zoom*e.scale/gesture.scale,at.x,at.y);
  },{passive:false});
  canvas.addEventListener('gestureend',function(e){e.preventDefault();gesture=null;},{passive:false});
  canvas.onpointerdown = function(e) {
    if(e.button!==0||e.target.closest('button, [data-rp-action]'))return;
    drag={id:e.pointerId,x:e.clientX,y:e.clientY,panX:_reproViewport.x,panY:_reproViewport.y};
    canvas.setPointerCapture(e.pointerId);canvas.focus({preventScroll:true});canvas.classList.add('is-panning');
  };
  canvas.onpointermove=function(e){if(drag&&drag.id===e.pointerId){
    _reproViewport.x=drag.panX+e.clientX-drag.x;_reproViewport.y=drag.panY+e.clientY-drag.y;reproTransform();
  }};
  canvas.onpointerup=canvas.onpointercancel=canvas.onlostpointercapture=function(){drag=null;canvas.classList.remove('is-panning');};
  canvas.onkeydown=function(e){
    if(e.target!==canvas)return;
    var offsets={ArrowLeft:[40,0],ArrowRight:[-40,0],ArrowUp:[0,40],ArrowDown:[0,-40]};
    if(offsets[e.key]){e.preventDefault();_reproViewport.x+=offsets[e.key][0];_reproViewport.y+=offsets[e.key][1];reproTransform();}
    else if(['+','=','-'].indexOf(e.key)>=0){e.preventDefault();reproZoomAt(canvas,_reproViewport.zoom*(e.key==='-'?0.8:1.25),canvas.clientWidth/2,canvas.clientHeight/2);}
    else if(e.key==='0'){e.preventDefault();reproFit();}
    else if(e.key.toLowerCase()==='c'){e.preventDefault();reproCenter();}
  };
}

function reproLegendHTML(steps, byName, status) {
  var counts = {}, checks = 0;
  steps.forEach(function(s) {
    var st = reproStateOf(byName[s.name]);
    counts[st] = (counts[st] || 0) + 1;
    if (s.kind === 'check') checks++;
  });
  var items = REPRO_STATES.map(function(s) {
    var n = counts[s.key] || 0;
    return '<span class="repro-legend-item rp-' + s.key + (n ? '' : ' is-off') + '">'
      + '<span class="repro-glyph">' + s.glyph + '</span>' + s.key
      + '<span class="repro-count">' + n + '</span></span>';
  });
  items.push('<span class="repro-legend-item is-kind' + (checks ? '' : ' is-off') + '">'
    + '<span class="repro-glyph">✓</span>check step<span class="repro-count">' + checks + '</span></span>');
  var banner = status.unavailable
    ? '<div class="repro-findings">Runner state is unavailable, so every step reads <code>unknown</code>: '
      + escapeHtml(status.unavailable) + '</div>'
    : '';
  return '<div class="repro-legend">' + items.join('') + '</div>' + banner;
}

function reproFindingsHTML(findings) {
  if (!findings || !findings.length) return '';
  var rows = findings.map(function(f) {
    return '<li><span class="repro-sev' + (f.severity === 'warning' ? ' is-warning' : '') + '">['
      + escapeHtml(String(f.severity).toUpperCase()) + ']</span>'
      + (typeof f.task_path==='string' ? reproButton(f.task_path||'Project root','task',f.task_path) : '')
      + escapeHtml(f.message) + '</li>';
  }).join('');
  var errors = findings.filter(function(f) { return f.severity === 'error'; }).length;
  var warnings = findings.length - errors;
  var parts = [];
  if (errors) parts.push(errors + ' error' + (errors === 1 ? '' : 's')
    + ' — graph is not executable. Dependency cycles retain parsed steps for inspection; malformed declarations can omit steps');
  if (warnings) parts.push(warnings + ' warning' + (warnings === 1 ? '' : 's')
    + ' — valid active steps are drawn; inspect the dependency evidence below');
  return '<div class="repro-findings">' + escapeHtml(parts.join('; ')) + '.<ul>'
    + rows + '</ul></div>';
}

function reproNodeId(name) {
  return 'repro-node-' + name.replace(/[^A-Za-z0-9_-]/g, '_');
}

function reproDuration(seconds) {
  if (seconds == null) return '';
  if (seconds < 1) return Math.round(seconds * 1000) + 'ms';
  if (seconds < 60) return seconds.toFixed(1) + 's';
  return Math.floor(seconds / 60) + 'm' + Math.round(seconds % 60) + 's';
}

function onReproClick(event) {
  var control = event.target.closest('[data-rp-action]');
  if (control) {
    event.preventDefault();
    var action = control.dataset.rpAction, value = control.dataset.value;
    var menu=control.closest('.rp-menu');if(menu)menu.open=false;
    if(action==='task')reproSelectTask(value);
    else if(action==='find-task'||action==='focus'||action==='explore')reproFocus(value);
    else if(action==='overview'||action==='clear'){_workspaceFilters={statuses:[],tasks:null};applyWorkspaceFilters(false);reproNavigate({expanded:[]},true);}
    else if(action==='show-selected'){if(_reproSelected){_reproReaderFull=false;showView('reproduction');reproSizeWorkspace();if(_reproReaderCompact)reproSetReader(false);revealReproStep(_reproSelected);}else reproFocus(activePath);}
    else if(action==='full-reader'){if(_reproReaderCompact){reproSetReader(false);return;}_reproReaderFull=!_reproReaderFull;document.getElementById('workspace').classList.toggle('dag-full-reader',_reproReaderFull);reproSizeWorkspace();var focus=document.querySelector('#dag-reader-controls [data-rp-action=full-reader]');if(focus)focus.focus({preventScroll:true});}
    else if(action==='close-reader')reproSetReader(false);
    else if(action==='reader')reproSetReader(_reproReaderClosed);
    else if(action==='declaration')reproOpenDeclaration();
    else if(action==='copy-command')reproCopyCommand(control);
    else if(action==='fold'){
      var expanded=new Set(_reproNav.expanded||[]);_reproPreserve='task:'+value;
      if(expanded.has(value))expanded.delete(value);else expanded.add(value);
      reproNavigate({expanded:Array.from(expanded)},false);
      var toggle=Array.from(document.querySelectorAll('[data-rp-action=fold]')).find(function(b){return b.dataset.value===value;});if(toggle)toggle.focus({preventScroll:true});
    }
    else if(action==='edge'){
      var edge=_reproLayoutCache.layout.edges[Number(value)],host=document.getElementById('repro-edge-detail');
      host.innerHTML=reproButton('Close','close-edge')+'<h3>'+escapeHtml(reproEdgeLabel(_reproLayoutCache.layout,edge))+'</h3>'+reproEvidenceHTML(edge.evidence);
    }
    else if(action==='close-edge')reproCloseGraphDetail();
    else if(action==='refresh')renderReproView(true);
    else if(action==='open'||action==='related')revealReproStep(value);
    else if(action==='select')selectReproStep(value);
    else if (action === 'fit') reproFit();
    else if (action === 'center') reproCenter();
    else if (action === 'zoom-in' || action === 'zoom-out') {
      var canvas = document.querySelector('#view-reproduction .repro-canvas');
      if (canvas) {
        reproZoomAt(canvas,_reproViewport.zoom*(action==='zoom-in'?1.25:0.8),canvas.clientWidth/2,canvas.clientHeight/2);
      }
    } else if (action === 'close-detail') {
      _reproInspectorClosed = true;
      renderReproDetail('');
      var selected = document.getElementById(reproNodeId(_reproSelected));
      if (selected) selected.focus({ preventScroll: true });
    }
    return;
  }
  var node = event.target.closest('.repro-node');
  if (node && node.dataset.step) { selectReproStep(node.dataset.step); return; }
  var link = event.target.closest('.repro-task-link');
  if (link && link.dataset.path !== undefined) reproSelectTask(link.dataset.path);
}

function selectReproStep(name) {
  var step=(_reproData.graph.steps||[]).find(function(s){return s.name===name;});if(!step)return;
  _reproSelected = name;
  _reproNav.selected = name;
  var oldRestoring=restoring;restoring=true;setActive(step.task);restoring=oldRestoring;reproReaderControls();
  _reproInspectorClosed = false;
  if (location.hash !== reproHash()) history.pushState({ wt: ACTIVE_WT }, '', reproHash());
  var container = document.getElementById('view-reproduction');
  if (!container) return;
  container.querySelectorAll('.repro-node').forEach(function(n) {
    n.classList.toggle('is-selected', n.dataset.step === name);
  });
  container.querySelectorAll('.rp-task').forEach(function(node){
    node.classList.remove('is-selected');
    var contains=!node.classList.contains('rp-expanded')&&reproWithin(step.task,node.dataset.task);
    var indicator=node.querySelector('.rp-selected-inside'),summary=node.querySelector('.rp-task-summary');
    if(indicator)indicator.hidden=!contains;if(summary)summary.hidden=contains;
  });
  container.querySelectorAll('.repro-edges path').forEach(function(p) {
    var edge=_reproLayoutCache&&_reproLayoutCache.layout.edges[Number(p.dataset.value)];
    p.classList.toggle('is-lit', !!edge&&edge.evidence.some(function(r){return (r.from||r.producer)===name||(r.to||r.consumer)===name;}));
  });
  renderReproDetail(name);
  syncTreeSteps();
  var reader=document.getElementById('task-preview');if(reader)reader.scrollTop=0;
  var heading=document.querySelector('.repro-detail-title');if(heading)heading.focus({preventScroll:true});

}

function reproFileList(files) {
  if (!files.length) return '<p class="repro-hint">No files declared.</p>';
  return '<ul class="repro-files">' + files.map(function(file) {
    var ref=file.path||file, logical=ref.logical||'', resolved=ref.resolved||logical;
    var slash=logical.lastIndexOf('/'), leaf=logical.slice(slash+1), dir=logical.slice(0,slash+1);
    var href=REPO_FILE_BASE?repoFileHref(resolved):vscodeFileUri(resolved.startsWith('/')?resolved:PROJECT_ROOT+'/'+resolved);
    var link='<a href="'+escapeAttr(href)+'" target="_blank"'+(window.LOCAL_OPEN&&!REPO_FILE_BASE?' data-open-path="'+escapeAttr(resolved)+'"':'')+'>'+escapeHtml(leaf||logical)+'</a>';
    return '<li><div class="repro-file-name">'+link+'</div>'+(dir?'<div class="repro-file-dir">'+escapeHtml(dir)+'</div>':'')
      +(file.note?'<div class="repro-file-note">'+escapeHtml(file.note)+'</div>':'')+'</li>';
  }).join('')+'</ul>';
}
function reproDisclosure(key, label, content, open) {
  return '<details class="repro-disclosure" data-detail-section="'+key+'"'+(open?' open':'')+'><summary>'+label+'</summary><div class="repro-disclosure-body">'+content+'</div></details>';
}
function renderReproDetail(name) {
  var host=document.getElementById('repro-detail');
  if(!host)return;
  var step=_reproData&&(_reproData.graph.steps||[]).find(function(s){return s.name===name;});
  var visible=!!step&&!_reproInspectorClosed;
  document.getElementById('task-preview').classList.toggle('step-reading',visible);
  if(!visible){host.innerHTML='';host.removeAttribute('data-step');return;}
  var same=host.dataset.step===name, previousState=host.dataset.state, opened=new Set(Array.from(host.querySelectorAll('details[open]')).map(function(el){return el.dataset.detailSection;}));
  var entry=reproStatusIndex(_reproData)[name], state=reproStateOf(entry), related=reproProject(_reproData.graph,_reproNav,[]);
  var external={};(_reproData.graph.external_inputs||[]).filter(function(e){return (e.consumers||[]).indexOf(name)!==-1;}).forEach(function(e){external[e.logical]=e;});
  var inputs=(step.deps||[]).map(function(d){
    var origins=(step.dependency_origins&&step.dependency_origins[d.logical]||[]).map(function(o){return typeof o==='string'?o:({declared:'Declared input',script:'Script',include:'Included source',environment:'Environment'}[o.kind]||o.kind)+(o.via?' via '+o.via:'');});
    if(external[d.logical])origins.push(external[d.logical].exists?'External input · available':'External input · missing');
    return {path:d,note:origins.join(' · ')};
  });
  var outs=(step.outs||[]).map(function(o){return {path:o.path,note:o.sidecar?'Freshness checked via '+o.sidecar.logical:''};});
  var connections=['incoming','outgoing'].map(function(direction){
    var grouped={};(related[direction][name]||[]).forEach(function(e){var other=direction==='incoming'?e.from:e.to;(grouped[other]||(grouped[other]=[])).push(e.via);});
    return '<section><h4>'+(direction==='incoming'?'Uses':'Used by')+'</h4>'+(Object.keys(grouped).map(function(other){return '<div class="repro-related">'+reproButton(other,'related',other)+(!workspaceTaskMatches(related.byName[other].task)?'<span class="repro-hint">Hidden from navigation</span>':'')+reproPathList(Array.from(new Set(grouped[other])))+'</div>';}).join('')||'<p class="repro-hint">No connected steps.</p>')+'</section>';
  }).join('');
  var evidence='';
  if(entry&&entry.local_status&&entry.local_status!==state)evidence+='<p><strong>For saved inputs: '+escapeHtml(entry.local_status)+'</strong> — '+escapeHtml(entry.local_reason||'')+'</p>';
  if(entry&&entry.boundary_inputs&&entry.boundary_inputs.length)evidence+='<h4>Saved inputs</h4>'+reproFileList(entry.boundary_inputs.map(function(b){return {logical:b.logical,resolved:b.resolved,note:b.provenance+' · '+b.producer};}));
  if(entry&&entry.acceptance)evidence+='<h4>Reviewed reuse</h4><p>'+escapeHtml(entry.acceptance.reason||'Reviewed unchanged output')+'</p>'+reproPathList(Object.keys(entry.acceptance.evidence||{}));
  if(entry&&entry.last_run)evidence+='<p>Last run: '+escapeHtml(new Date(entry.last_run*1000).toLocaleString())+(entry.duration!=null?' · '+reproDuration(entry.duration):'')+'</p>';
  else if(entry&&entry.duration!=null)evidence+='<p>Duration: '+reproDuration(entry.duration)+'</p>';
  if(entry&&entry.log_tail)evidence+='<h4>Run log</h4><pre class="repro-log">'+escapeHtml(entry.log_tail)+'</pre>';
  var command=step.cmd||step.cmd_logical||'', declared=step.cmd_logical||command;
  var code=escapeHtml(command);if(window.hljs&&hljs.getLanguage('bash'))code=hljs.highlight(command,{language:'bash',ignoreIllegals:true}).value;
  var title=name.replace(/[-_]+/g,' ');title=title.charAt(0).toUpperCase()+title.slice(1);
  host.dataset.step=name;host.dataset.state=state;
  host.innerHTML='<article class="repro-detail"><div class="repro-detail-context">'+reproButton('← Back to task','task',step.task)+'<span>'+(step.kind==='check'?'Check step':'Build step')+'</span></div>'
    +'<header class="repro-detail-head"><h2 class="repro-detail-title" tabindex="-1">'+escapeHtml(title)+'</h2><code class="repro-detail-name">'+escapeHtml(name)+'</code></header>'
    +'<div class="repro-status-line"><span class="repro-step-state rp-'+state+'"><span class="repro-glyph">'+(REPRO_GLYPHS[state]||'?')+'</span> '+escapeHtml(state)+'</span><span>'+escapeHtml(entry?entry.reason:'Runner state unavailable')+'</span></div>'
    +'<div class="repro-detail-actions">'+reproButton('View declaration','declaration')+(currentView==='workspace'?reproButton('Show in graph','show-selected',step.task):'')+'</div>'
    +'<section class="repro-detail-section"><div class="repro-section-head"><h3>Command</h3>'+reproButton('Copy command','copy-command')+'</div><p class="repro-hint">Run from the project directory.</p><pre class="repro-command"><code class="hljs language-bash">'+code+'</code></pre><span class="repro-copy-status" role="status"></span>'
    +(declared!==command?reproDisclosure('declared','Declared command','<pre class="repro-command"><code>'+escapeHtml(declared)+'</code></pre>',opened.has('declared')):'')+'</section>'
    +'<section class="repro-detail-section"><h3>Outputs <span>'+outs.length+'</span></h3>'+reproFileList(outs.slice(0,3))+(outs.length>3?reproDisclosure('outputs','Show '+(outs.length-3)+' more outputs',reproFileList(outs.slice(3)),opened.has('outputs')):'')+'</section>'
    +reproDisclosure('inputs','Inputs <span>'+inputs.length+'</span>',reproFileList(inputs),opened.has('inputs'))
    +reproDisclosure('connections','Connected steps <span>'+new Set((related.incoming[name]||[]).map(function(e){return e.from;}).concat((related.outgoing[name]||[]).map(function(e){return e.to;}))).size+'</span>',connections,opened.has('connections'))
    +(Object.keys(step.params||{}).length?reproDisclosure('params','Parameters','<dl class="repro-params">'+Object.keys(step.params).map(function(key){return reproDetailRow(escapeHtml(key),'<code>'+escapeHtml(JSON.stringify(step.params[key]))+'</code>');}).join('')+'</dl>',opened.has('params')):'')
    +(evidence?reproDisclosure('evidence','Run & evidence',evidence,opened.has('evidence')||(state==='failed'&&(!same||previousState!=='failed'))):'')+'</article>';
}
async function reproCopyCommand(button) {
  var step=_reproData&&_reproData.graph.steps.find(function(s){return s.name===_reproSelected;});if(!step)return;
  var message=document.querySelector('#repro-detail .repro-copy-status');
  try{await navigator.clipboard.writeText(step.cmd||step.cmd_logical||'');button.textContent='Copied';if(message)message.textContent='Command copied.';}
  catch(e){if(message)message.textContent='Could not copy. Select the command text to copy it.';}
}

function reproDetailRow(label, valueHtml) {
  return '<dt>' + label + '</dt><dd>' + valueHtml + '</dd>';
}

/* An out's logical path, naming the sidecar when one stands in for it: the
   runner hashes the sidecar instead, so a large intermediate reading fresh is
   only explicable with the substitution on screen. */
function reproOutLabel(out) {
  return out.path.logical + (out.sidecar ? ' (hashed via ' + out.sidecar.logical + ')' : '');
}

function reproPathList(paths) {
  if (!paths.length) return '<span class="repro-path">—</span>';
  return '<ul>' + paths.map(function(p) {
    return '<li><span class="repro-path">' + escapeHtml(p) + '</span></li>';
  }).join('') + '</ul>';
}

/* Open the Reproduction view on one step — the target of a task-page step row.
   A step the current scope hides widens the scope rather than landing on
   a canvas the step is not on. */
function revealReproStep(name, owner) {
  var wt=ACTIVE_WT;
  return loadReproData(false).then(function(data){
    if(wt!==ACTIVE_WT)return;
    var step=(data.graph.steps||[]).find(function(s){return s.name===name;});
    if(!step||(owner!==undefined&&step.task!==owner)){
      _reproNotice='Step '+name+' is not declared'+(owner!==undefined?' in '+reproTaskTitle(owner):' in this project')+'.';
      if(currentView!=='reproduction')showView('reproduction');
      drawReproView(document.getElementById('view-reproduction'),data);return;
    }
    _reproNav.roots=[];_reproNav.mode='scope';_reproNav.anchor='';
    _reproInspectorClosed=false;reproRevealOwner(step.task);
    selectReproStep(name);
    if(currentView==='reproduction'){drawReproView(document.getElementById('view-reproduction'),data);_reproViewport.zoom=1;reproCenter();}
    syncTreeSteps();
  });
}

/* Each rendered step row provides the canonical Markdown anchor. */
function renderReproStepTable(renderedMd, taskPath) {
  loadReproData(false).then(function(data) {
    if (!renderedMd.isConnected) return;
    var steps = (data.graph.steps || []).filter(function(s) { return s.task === taskPath; });
    if (!steps.length) return;
    var byName = reproStatusIndex(data);
    var rows = steps.map(function(s) {
      var entry = byName[s.name];
      var state = reproStateOf(entry);
      var outs = (s.outs || []).map(reproOutLabel).join(', ');
      return '<tr id="step-'+escapeAttr(s.name)+'"><td><button class="repro-step-name" type="button" data-step="'
        + escapeAttr(s.name) + '">' + escapeHtml(s.name) + '</button>'
        + (s.kind === 'check' ? ' <span class="repro-check-tag">✓</span>' : '') + '</td>'
        + '<td><span class="repro-step-state rp-' + state + '"><span class="repro-glyph">'
        + (REPRO_GLYPHS[state] || '?') + '</span>' + escapeHtml(state) + '</span></td>'
        + '<td>' + escapeHtml(entry ? entry.reason : 'runner state unavailable') + '</td>'
        + '<td class="repro-outs">' + escapeHtml(outs || '—') + '</td></tr>';
    }).join('');
    var old = renderedMd.querySelector(':scope > .repro-steps');
    if (old) old.remove();
    var host = document.createElement('div');
    host.className = 'repro-steps';
    host.innerHTML = '<table><thead><tr><th>Step</th><th>State</th><th>Reason</th><th>Outs</th>'
      + '</tr></thead><tbody>' + rows + '</tbody></table>';
    host.onclick = function(event) {
      var btn = event.target.closest('.repro-step-name');
      if (btn && btn.dataset.step) revealReproStep(btn.dataset.step);
    };
    renderedMd.insertBefore(host, renderedMd.firstChild);
  }).catch(function() { /* no graph payload: the raw YAML block still stands */ });
}

/* Re-run every step table already on the active card (a build moved the lock). */
function refreshReproStepTables() {
  document.querySelectorAll(
    '#active-node [data-section="' + REPRO_SECTION + '"] .rendered-md[data-rendered]'
  ).forEach(function(el) {
    var node = el.closest('.task-node');
    renderReproStepTable(el, node ? node.dataset.path : '');
  });
}

/* A build rewrote the lock: drop the cached payloads and repaint whatever is
   showing them. */
function onReproUpdated() {
  _reproData = null;
  if (currentView === 'reproduction') renderReproView(true);
  else loadReproData(true).then(function(){refreshReproStepTables();syncTreeSteps();applyWorkspaceFilters(false);renderReproDetail(_reproSelected);}).catch(function() {});
}

/* ════════════════════════════════════════════════════════════════════════
   activePath hash router — the single source of truth for navigation.
   ──────────────────────────────────────────────────────────────────────
   `activePath` names the task currently shown in the main panel. Everything
   else (sidebar highlight, breadcrumb, active-node body, children DAG) is a
   pure function of it. The URL hash mirrors it verbatim: `#/<task/path>`,
   `#/` (or empty) = the root. setActive() is the one entry point; the
   browser's own back/forward stack drives navigation via popstate.
   ════════════════════════════════════════════════════════════════════════ */

var activePath = '';        /* owning task; '' = root */
var activeArtifactPath = ''; /* attachment selected in the normal reading pane */
var restoring = false;      /* true while applying a load/popstate hash — suppress pushState */
var _moveFocusOnLoad = false; /* set per user-nav so loadActiveNode lands focus on the new heading */
/* The in-flight (or last-settled) updateSidebar() promise from the current
   setActive() call — a completion hook that patchCardBadgeWhenReady awaits
   instead of polling for the sidebar row to land. */
var _lastSidebarUpdate = Promise.resolve();

/* A path -> display-title lookup. sidebar-nav populates this from /nav; until
   then the breadcrumb falls back to the path slug. */
var pathTitles = {};

/* ── Tab title ──
   Dashboards of the same repo differ only by worktree, so the tab reads
   "<active page> · <where it lives>" — the page leads because tabs truncate
   from the right. SITE_TITLE is the server-rendered <title>, i.e. the tree's
   own name: the right name for the root node, and the second half wherever
   there is no worktree to name. The page half tracks navigation in every mode;
   only the second half is mode-dependent. */
var SITE_TITLE = document.title;
var _tabTaskTitle = '';   /* display title of the task the main panel shows */

/* Name the active task in the tab. */
function setTabTitle(title) {
  _tabTaskTitle = title || '';
  refreshTabTitle();
}

/* Repaint from current state — also called when the worktree half lands
   (fetchWorktrees resolves after the first render) or changes. */
function refreshTabTitle() {
  var name = _tabTaskTitle || SITE_TITLE;
  /* A doc site and a downloaded export have no worktree — and must not name one
     that does not exist where the file ends up — so they carry their own name as
     the second half. Live, that half is the worktree, absent until its fetch
     lands. */
  var context = (window.DOC_MODE || window.STANDALONE)
    ? SITE_TITLE
    : (_wtTabLabels[ACTIVE_WT || _launchWtId] || '');
  document.title = (context && context !== name) ? (name + ' · ' + context) : name;
}

/* Read location.hash as `#/<task/path>` -> the path verbatim ('' for root). */
function parseHash() {
  var h = location.hash || '';
  if (h.charAt(0) === '#') h = h.slice(1);   /* strip leading # */
  if (h.charAt(0) === '/') h = h.slice(1);   /* strip leading / */
  var query = h.indexOf('?');
  return query === -1 ? h : h.slice(0, query);
}

function parseArtifactHash() {
  var h = location.hash || '';
  var query = h.indexOf('?');
  if (query === -1) return '';
  var params = new URLSearchParams(h.slice(query + 1));
  return params.get('attachment') || '';
}

/* The one navigation entry point. Sets activePath, writes history (unless
   restoring), then refreshes every derived region. */
function setActive(path, artifactPath) {
  path = path || '';
  if(!restoring){_reproSelected='';_reproNav.selected='';renderReproDetail('');}
  activePath = path;
  activeArtifactPath = artifactPath || '';

  if (!restoring) {
    var hash = reproHash();
    /* Relative '#/...' keeps location.search (the ?wt=) intact, so a task-path
       navigation never drops the active worktree from the URL. */
    if (location.hash !== hash) history.pushState({ path: path, wt: ACTIVE_WT }, '', hash);
    /* User-initiated navigation: land focus on the new card heading once it
       paints (a11y — SR users follow focus to the new content). Suppressed on
       initial load / popstate restores (restoring=true), which must not steal
       focus from the page. */
    _moveFocusOnLoad = true;
  }

  /* A node click always means "show me the workspace." */
  if (activeArtifactPath) showView('workspace');

  updateBreadcrumb(path, activeArtifactPath);
  /* The header VS Code button opens the active task's file, so it follows nav. */
  updateWorktreeOpenHref();
  _lastSidebarUpdate = updateSidebar(path).then(function(){syncTreeSteps();applyWorkspaceFilters(false);});
  if (activeArtifactPath) {
    loadActiveArtifact(path, activeArtifactPath);
    var children = document.getElementById('children-dag');
    if (children) children.innerHTML = '';
  } else {
    loadActiveNode(path);
    loadChildrenDag(path);
  }

  /* Chrome: a selection means "done navigating" — auto-hide the unpinned
     overlay and close the narrow-screen drawer. Defined in the sidebar-chrome
     module below; guard so the router still works if it ever loads first. */
  if (typeof onNavigationChrome === 'function') onNavigationChrome();
  updateWorkspaceFilterSummary();
}

/* Rebuild the breadcrumb from the active path: root › seg › … › active.
   Each non-active crumb is a button that ascends by setting that ancestor
   active; the active crumb is inert. */
function updateBreadcrumb(path, artifactPath) {
  var crumbs = document.getElementById('crumbs');
  if (!crumbs) return;
  crumbs.innerHTML = '';

  var segs = path ? path.split('/') : [];

  function addCrumb(label, crumbPath, isActive) {
    var btn = document.createElement('button');
    btn.className = 'crumb' + (isActive ? ' active' : '');
    btn.textContent = label;
    if (isActive) {
      btn.setAttribute('aria-current', 'page');
      btn.disabled = true;
    } else {
      btn.addEventListener('click', function() { setActive(crumbPath); });
    }
    crumbs.appendChild(btn);
  }

  function addSep() {
    var sep = document.createElement('span');
    sep.className = 'crumb-sep';
    sep.textContent = '›';
    crumbs.appendChild(sep);
  }

  /* Root crumb (active when at the root). In doc-mode the literal "root" slug is
     task anatomy — label it with the site title (the tree root's title, carried
     by the header-title element). */
  var rootLabel = 'root';
  if (window.DOC_MODE) {
    var hdr = document.getElementById('header-title');
    if (hdr && hdr.textContent.trim()) rootLabel = hdr.textContent.trim();
  }
  addCrumb(rootLabel, '', segs.length === 0 && !artifactPath);

  var accumulated = '';
  for (var i = 0; i < segs.length; i++) {
    accumulated = i === 0 ? segs[i] : accumulated + '/' + segs[i];
    addSep();
    /* Prefer the real title once the sidebar supplies it; fall back to slug. */
    var label = pathTitles[accumulated] || segs[i];
    addCrumb(label, accumulated, i === segs.length - 1 && !artifactPath);
  }
  if (artifactPath) {
    addSep();
    addCrumb(artifactPath.replace(/^attachments\//, ''), path, true);
  }
}

/* ── Region content loaders ──
   updateSidebar is implemented below (sidebar-nav); loadActiveNode and
   loadChildrenDag fill the main panel (this task). The active node's body and
   the children DAG are pure functions of activePath, refetched on every nav. */

/* Active-node card: the focused detail view for the current task. Fetch the
   body-only /node/<path> partial and wrap it in a `.task-node[data-path]` so
   the existing section + comment pipeline (toggleSection, loadComments,
   updateSectionBadges, the comment forms) works byte-for-byte as in the old
   tree body — every one of those walks up to `.task-node[data-path]`. The
   breadcrumb already shows the path, so the card header is just title + status.
   Sections default to EXPANDED here (this is the detail view, not a tree row). */
/* Chrome-button glyphs. Both are 2px-stroke outlines on the same 24-unit grid,
   inheriting the button's currentColor, so the card-head and header controls read
   as one family — a solid brand mark beside an outline glyph is exactly the "looks
   off" this chrome pass exists to fix, and the button's label already says which
   editor it opens.
   EDITOR_ICON: code brackets, for the control that opens a file in the editor. */
var EDITOR_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"'
  + ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
  + '<path d="m16 18 6-6-6-6"></path><path d="m8 6-6 6 6 6"></path></svg>';

/* OPEN_ICON: file leaving its box, for the control that hands the file to
   whatever application the machine uses for its type — no editor named. */
var OPEN_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"'
  + ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
  + '<path d="M14 3h7v7"></path><path d="M21 3 11 13"></path>'
  + '<path d="M19 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h6"></path></svg>';

/* vscode://file deep-link to an absolute local path (a file or a folder). The
   single place the `vscode://file/` scheme is composed, shared by the per-task
   task.md link and the header open-worktree link. */
function vscodeFileUri(absPath) {
  return 'vscode://file/' + absPath;
}

/* vscode://file deep-link to a task's task.md. Derives from the resolved task
   root (RESOLVED_ROOT absolute for local links, ROOT_PREFIX repo-relative for
   the GitHub branch) so it points at the same on-disk file the body's relative
   links resolve against, for any root — not just a `superRA/` under PROJECT_ROOT. */
function taskFileVscodeHref(path) {
  var rel = (path ? path + '/' : '') + 'task.md';
  if (REPO_FILE_BASE) {
    return repoFileHref((REPO_ROOT_PREFIX ? REPO_ROOT_PREFIX + '/' : '') + rel);
  }
  return vscodeFileUri(RESOLVED_ROOT + '/' + rel);
}

/* A file under a task's directory as a project-root-relative path — the address
   /api/open takes. Same composition the /files/ route is handed (ROOT_PREFIX +
   '/' + taskPath + …), so both agree for any --root, a nested tree, and a
   rootless forest. `rel` is task.md for the task itself, or an attachment's
   task-relative path. */
function taskRelOpenPath(path, rel) {
  return (ROOT_PREFIX ? ROOT_PREFIX + '/' : '') + (path ? path + '/' : '') + rel;
}

function taskFileOpenPath(path) {
  return taskRelOpenPath(path, 'task.md');
}

/* Report a failed or refused open. The only visible result of a successful open
   is on the researcher's desktop, so without this a refusal reads as a dead
   button. Transient, single-slot, dismisses itself. */
function showOpenError(msg) {
  var el = document.getElementById('open-toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'open-toast';
    el.className = 'open-toast';
    el.setAttribute('role', 'status');
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('visible');
  clearTimeout(showOpenError._timer);
  showOpenError._timer = setTimeout(function() { el.classList.remove('visible'); }, 6000);
}

/* Hand a project-root-relative path to the server for opening on its own host.
   `target` is 'native' (the OS default application for the file type) or 'editor'
   (this worktree's VS Code window). When no editor CLI is installed the route
   answers with a vscode:// URI to follow instead — the pre-route behavior. */
function openLocalPath(path, target) {
  return fetch(wtUrl('/api/open'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: path, target: target || 'native' })
  }).then(function(resp) {
    return resp.json().catch(function() { return {}; }).then(function(data) {
      if (!resp.ok) throw new Error(data.detail || ('HTTP ' + resp.status));
      if (data.status === 'fallback' && data.uri) window.location.href = data.uri;
    });
  }).catch(function(err) {
    showOpenError('Could not open ' + path + (err && err.message ? ' — ' + err.message : ''));
  });
}

document.addEventListener('click',function(e){
  var link=e.target.closest&&e.target.closest('a.task-link');
  if(!link||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
  var href=link.getAttribute('href');if(!href||!href.startsWith('#/'))return;
  e.preventDefault();var parts=href.slice(2).split('?'),params=new URLSearchParams(parts.slice(1).join('?'));
  if(params.has('step'))revealReproStep(params.get('step'),parts[0]);else reproSelectTask(parts[0]);
});

/* One delegated handler for every local-open control: the card-head button, the
   header VS Code button, body file links, attachment links, and the artifact
   pane's Open button all carry data-open-path. A plain left-click opens on the
   server's host; a modifier or middle click falls through to the element's own
   vscode:// or /api/artifact href, so the browser's own "open elsewhere"
   gestures still work. */
document.addEventListener('click', function(e) {
  if (!window.LOCAL_OPEN) return;
  var el = (e.target && e.target.closest) ? e.target.closest('[data-open-path]') : null;
  if (!el) return;
  if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  e.preventDefault();
  openLocalPath(el.getAttribute('data-open-path'), el.getAttribute('data-open-target'));
});

async function loadActiveNode(path) {
  var region = document.getElementById('active-node');
  if (!region) return;

  /* Guard against a slow fetch landing after the user has navigated away. */
  var token = (loadActiveNode._token = (loadActiveNode._token || 0) + 1);

  var slug = path ? path.split('/').pop() : '';

  try {
    var resp = await fetch(wtUrl('/node/' + path));
    if (token !== loadActiveNode._token) return;  /* superseded */
    if (!resp.ok) {
      region.innerHTML = '<p style="color:var(--text-mute)">Could not load this task.</p>';
      /* The card names no task now, so neither may the tab — leaving the
         previously shown task there would describe a page that is gone. Falls
         back to the tree's own name, exactly as a cold load of a bad link. */
      setTabTitle('');
      return;
    }
    var body = await resp.text();
    if (token !== loadActiveNode._token) return;  /* superseded */

    /* Read title + status after the fetch resolves: updateSidebar (started in
       the same setActive tick) has had time to materialize the row, so its
       data-status and the indexed title are usually available even on a fresh
       descent. Both fall back gracefully when the sidebar row isn't in yet. */
    /* At the root, path/slug are empty; the tracker falls back to "root", but a
       doc page's root is the site itself, so use the site title there. */
    var rootTitle = 'root';
    if (window.DOC_MODE) {
      var hdrEl = document.getElementById('header-title');
      if (hdrEl && hdrEl.textContent.trim()) rootTitle = hdrEl.textContent.trim();
    }
    var title = pathTitles[path] || slug || rootTitle;
    /* The tab names this task; at the root the tree's own name is that name. */
    setTabTitle(path ? title : SITE_TITLE);
    var status = navRowStatus(path);
    /* With the local-open route the button hands task.md to whatever application
       this machine uses for markdown; without it, today's vscode:// deep link. */
    var openNative = window.LOCAL_OPEN && !REPO_FILE_BASE;
    var fileButtonTitle = REPO_FILE_BASE ? 'Open task.md on GitHub'
      : (openNative ? 'Open task.md in the default application' : 'Open task.md in VS Code');
    var fileButtonLabel = REPO_FILE_BASE ? 'GitHub' : (openNative ? 'Open' : 'VS Code');
    var fileButtonIcon = openNative ? OPEN_ICON : EDITOR_ICON;

    region.innerHTML =
      '<header class="active-node-head">'
      + '<h2 class="active-node-title" tabindex="-1"></h2>'
      + ((status && !window.DOC_MODE) ? '<span class="badge badge-' + status + '">' + status + '</span>' : '')
      /* Open this task's task.md in the configured file target. */
      + '<a class="open-btn" target="_blank" title="' + fileButtonTitle + '">'
      + fileButtonIcon + '<span>' + fileButtonLabel + '</span></a>'
      /* Share/Export: download this node's subtree as a standalone HTML file.
         Server-backed (/export), so it is omitted in standalone mode — a
         downloaded file has no server to re-export from. */
      + (window.STANDALONE ? '' :
         '<button class="share-btn" type="button" title="Download this subtree as a standalone HTML file">Share</button>')
      + '</header>'
      /* Wrap the body in a real .task-node so the comment/section helpers,
         which all resolve via `.task-node[data-path]`, find their context. */
      + '<div class="task-node active-node-body" data-path="' + escapeAttr(path) + '">' + body + '</div>'
      + '';

    /* Set the title via textContent (avoids HTML injection from titles). In
       doc-mode the slug is task anatomy — show the title alone. */
    var titleEl = region.querySelector('.active-node-title');
    if (titleEl) titleEl.textContent = (slug && !window.DOC_MODE) ? (slug + ' · ' + title) : title;

    /* Point the file button at this task's task.md. Set the href as a property
       (not an attribute string) so the path needs no escaping; it stays the
       modifier-click target even when the plain click goes through /api/open. */
    var vsBtn = region.querySelector('.open-btn');
    if (vsBtn) {
      vsBtn.href = taskFileVscodeHref(path);
      if (openNative) vsBtn.setAttribute('data-open-path', taskFileOpenPath(path));
    }

    /* Wire the Share button via a closure over `path` — an inline onclick can't
       carry the path safely (a quoted path breaks the double-quoted attribute). */
    var shareBtn = region.querySelector('.share-btn');
    if (shareBtn) shareBtn.onclick = function() { shareSubtree(path); };

    /* a11y: on a user-initiated navigation, move focus to the new heading so
       keyboard/SR users land on the freshly-loaded content. Consume the flag so
       SSE-driven re-renders of the same card never yank focus. */
    if (_moveFocusOnLoad && titleEl) {
      _moveFocusOnLoad = false;
      titleEl.focus({ preventScroll: true });
    }

    /* Expand every section by default and render its markdown + comments.
       Scope to the card's own top-level section wrappers — renderMarkdown adds
       nested [data-section] commentable-blocks, which must not be re-revealed. */
    var taskNode = region.querySelector('.task-node[data-path]');
    if (taskNode) {
      taskNode.querySelectorAll(':scope > [data-section]').forEach(function(wrapper) {
        revealCardSection(wrapper, path);
      });
      loadComments(path);
    }

    /* If the sidebar row hadn't landed yet, the status badge is missing. The
       deep-descent ancestor-walk in updateSidebar can outlast this fetch, so
       patch the badge once the row materializes (best-effort, single retry). */
    if (!status) patchCardBadgeWhenReady(path, token);
    /* Same race for the title: the tab is on the path slug until that row lands. */
    if (path && !pathTitles[path]) patchTabTitleWhenReady(path, token);
  } catch (e) {
    if (token !== loadActiveNode._token) return;
    region.innerHTML = '<p style="color:var(--st-rev-t)">Load error: ' + escapeHtml(e.message) + '</p><button type="button" class="hc-btn" id="retry-task-load">Retry</button>';
    region.querySelector('#retry-task-load').onclick=function(){loadActiveNode(path);};
    setTabTitle('');   /* same card/tab agreement as the not-ok branch above */
  }
}

/* Share/Export: hand off to the server's /export route, which returns the
   subtree's standalone HTML with Content-Disposition: attachment so the browser
   saves it directly. A bare-path root exports the whole tree; a task path scopes
   to that subtree. We navigate a hidden anchor (not location.href) so the
   attachment download never replaces the dashboard page. Server-only — the
   button is omitted in standalone mode. */
function shareSubtree(path) {
  var url = wtUrl('/export' + (path ? '?root=' + encodeURIComponent(path) : ''));
  var a = document.createElement('a');
  a.href = url;
  a.download = '';   /* let Content-Disposition pick the filename */
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/* Attachment data and full-pane rendering helpers. */
var _artifactPreviewToken = 0;
var _artifactManifests = {};
var _attachmentExpanded = {};

function artifactApiUrl(taskPath, artifactPath, download) {
  var url = '/api/artifact?task=' + encodeURIComponent(taskPath || '')
    + '&path=' + encodeURIComponent(artifactPath || '');
  if (download) url += '&download=true';
  return wtUrl(url);
}

function artifactManifestEntry(taskPath, artifactPath) {
  var manifest = _artifactManifests[taskPath];
  if (!manifest && window.STANDALONE && window.STANDALONE_ARTIFACTS) {
    manifest = STANDALONE_ARTIFACTS.manifests[taskPath];
  }
  var files = manifest && manifest.files ? manifest.files : [];
  for (var i = 0; i < files.length; i++) {
    if (files[i].path === artifactPath) return files[i];
  }
  return null;
}

function standaloneArtifactDataUrl(taskPath, entry) {
  if (!window.STANDALONE || !entry || !window.STANDALONE_ARTIFACTS) return '';
  var exported = entry.export || {};
  if (exported.status === 'figure' && exported.image_key
      && window.STANDALONE_IMAGES
      && STANDALONE_IMAGES.hasOwnProperty(exported.image_key)) {
    return STANDALONE_IMAGES[exported.image_key];
  }
  var taskContents = STANDALONE_ARTIFACTS.contents[taskPath] || {};
  var payload = taskContents[entry.path];
  if (!payload || payload.encoding !== 'base64') return '';
  return 'data:' + (payload.mime || entry.mime || 'application/octet-stream')
    + ';base64,' + payload.data;
}

function artifactResourceUrl(taskPath, artifactPath) {
  if (!window.STANDALONE) return artifactApiUrl(taskPath, artifactPath, false);
  var entry = artifactManifestEntry(taskPath, artifactPath);
  return standaloneArtifactDataUrl(taskPath, entry) || (entry && entry.repo_url) || '';
}

function artifactOpenHref(taskPath, artifactPath) {
  return artifactResourceUrl(taskPath, artifactPath) || '#';
}

function artifactDownloadHref(taskPath, entry) {
  if (!entry) return '';
  if (!window.STANDALONE) return artifactApiUrl(taskPath, entry.path, true);
  return standaloneArtifactDataUrl(taskPath, entry) || entry.repo_url || '';
}

function standaloneArtifactText(taskPath, entry) {
  var taskContents = window.STANDALONE_ARTIFACTS
    && STANDALONE_ARTIFACTS.contents[taskPath];
  var payload = taskContents && taskContents[entry.path];
  if (!payload || payload.encoding !== 'base64') {
    return Promise.reject(new Error('This file was not embedded in the export.'));
  }
  try {
    var binary = atob(payload.data);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return Promise.resolve(new TextDecoder('utf-8').decode(bytes));
  } catch (e) {
    return Promise.reject(new Error('The embedded file could not be decoded.'));
  }
}

function readArtifactText(taskPath, entry) {
  if (window.STANDALONE) return standaloneArtifactText(taskPath, entry);
  return fetch(artifactApiUrl(taskPath, entry.path, false)).then(function(resp) {
    if (!resp.ok) {
      if (resp.status === 413) throw new Error('Preview unavailable: file exceeds the preview limit.');
      throw new Error('Preview unavailable (' + resp.status + ').');
    }
    return resp.text();
  });
}

function formatArtifactBytes(value) {
  var size = Number(value) || 0;
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(size < 10 * 1024 ? 1 : 0) + ' KiB';
  return (size / (1024 * 1024)).toFixed(1) + ' MiB';
}

function artifactUnavailableReason(entry) {
  if (entry.previewable) return '';
  if (!entry.download_only) return 'Preview unavailable — file exceeds the preview limit.';
  return 'Download only — active or unsupported content is never rendered.';
}

function buildArtifactPreviewHead(taskPath, entry) {
  var head = document.createElement('header');
  head.className = 'artifact-preview-head';
  var heading = document.createElement('h3');
  heading.textContent = entry.path;
  head.appendChild(heading);
  var actions = document.createElement('div');
  actions.className = 'artifact-actions';
  /* Open matches the card head's task.md button: on a local-open server a plain
     click hands the attachment to this machine's default application, and the
     /api/artifact href stays the modifier/middle-click target — the same pair
     an attachment link in a task body already carries. */
  var openHref = artifactOpenHref(taskPath, entry.path);
  if (openHref && openHref !== '#') {
    var open = document.createElement('a');
    open.className = 'artifact-action';
    open.href = openHref;
    open.target = '_blank';
    open.textContent = 'Open';
    if (window.LOCAL_OPEN) {
      open.title = 'Open in the default application';
      open.setAttribute('data-open-path', taskRelOpenPath(taskPath, entry.path));
    }
    actions.appendChild(open);
  }
  var downloadHref = artifactDownloadHref(taskPath, entry);
  if (downloadHref) {
    var download = document.createElement('a');
    download.className = 'artifact-action';
    download.href = downloadHref;
    download.textContent = 'Download';
    if (downloadHref.indexOf('data:') === 0) download.download = entry.name;
    else download.target = '_blank';
    actions.appendChild(download);
  }
  head.appendChild(actions);
  return head;
}

function renderArtifactCode(text, language) {
  var pre = document.createElement('pre');
  var code = document.createElement('code');
  if (language && window.hljs && hljs.getLanguage(language)) {
    try {
      code.className = 'hljs language-' + language;
      code.innerHTML = hljs.highlight(text, {
        language: language,
        ignoreIllegals: true,
      }).value;
    } catch (e) {
      code.textContent = text;
    }
  } else {
    code.textContent = text;
  }
  pre.appendChild(code);
  return pre;
}

/* Attachments share the task tree and the normal reading pane. They are
   navigation-only pseudo-nodes: the owning task remains activePath, while the
   attachment path is the optional second part of the URL state. */
function attachmentManifest(taskPath) {
  return _artifactManifests[taskPath]
    || (window.STANDALONE && window.STANDALONE_ARTIFACTS
      && STANDALONE_ARTIFACTS.manifests[taskPath])
    || null;
}

function fetchAttachmentManifest(taskPath) {
  var embedded = attachmentManifest(taskPath);
  if (embedded) return Promise.resolve(embedded);
  if (window.STANDALONE) return Promise.resolve(null);
  return fetch(wtUrl('/api/artifacts?task=' + encodeURIComponent(taskPath || '')))
    .then(function(resp) { return resp.ok ? resp.json() : null; });
}

function attachmentTree(entries) {
  var root = { directories: {}, files: [] };
  (entries || []).forEach(function(entry) {
    var parts = entry.path.replace(/^attachments\//, '').split('/');
    var cursor = root;
    for (var i = 0; i < parts.length - 1; i++) {
      cursor.directories[parts[i]] = cursor.directories[parts[i]]
        || { directories: {}, files: [] };
      cursor = cursor.directories[parts[i]];
    }
    cursor.files.push({ name: parts[parts.length - 1], entry: entry });
  });
  return root;
}

function renderAttachmentLevel(owner, tree, level, taskLevel) {
  var list = document.createElement('ul');
  list.className = 'attachment-tree-level';
  list.setAttribute('role', 'group');
  Object.keys(tree.directories).sort().forEach(function(name) {
    var item = document.createElement('li');
    item.className = 'attachment-directory';
    item.setAttribute('role', 'none');
    var directory = document.createElement('button');
    directory.type = 'button';
    directory.className = 'attachment-directory-row';
    directory.setAttribute('role', 'treeitem');
    directory.setAttribute('aria-level', String(taskLevel + level + 2));
    directory.setAttribute('aria-expanded', 'true');
    directory.tabIndex = -1;
    directory.innerHTML =
      '<span class="attachment-directory-caret" aria-hidden="true">▾</span>';
    var label = document.createElement('span');
    label.className = 'attachment-directory-label';
    label.textContent = name;
    directory.appendChild(label);
    var nested = renderAttachmentLevel(
      owner, tree.directories[name], level + 1, taskLevel
    );
    directory.onclick = function(event) {
      event.stopPropagation();
      var expanded = directory.getAttribute('aria-expanded') === 'true';
      directory.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      nested.hidden = expanded;
    };
    item.appendChild(directory);
    item.appendChild(nested);
    list.appendChild(item);
  });
  tree.files.sort(function(a, b) { return a.name.localeCompare(b.name); })
    .forEach(function(file) {
      var item = document.createElement('li');
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'attachment-file-row';
      button.setAttribute('role', 'treeitem');
      button.setAttribute('aria-level', String(taskLevel + level + 2));
      button.tabIndex = -1;
      button.dataset.artifactOwner = owner;
      button.dataset.artifactPath = file.entry.path;
      button.setAttribute('aria-label', 'Open attachment ' + file.entry.path);
      button.innerHTML = '<span class="attachment-file-icon" aria-hidden="true">◇</span>';
      var name = document.createElement('span');
      name.className = 'attachment-file-name';
      name.textContent = file.name;
      button.appendChild(name);
      var kind = document.createElement('span');
      kind.className = 'attachment-file-kind';
      kind.textContent = file.entry.kind;
      button.appendChild(kind);
      button.classList.toggle(
        'nav-active',
        owner === activePath && file.entry.path === activeArtifactPath
      );
      button.onclick = function(event) {
        event.stopPropagation();
        setActive(owner, file.entry.path);
      };
      item.appendChild(button);
      list.appendChild(item);
    });
  return list;
}

function renderAttachmentBranch(taskPath, manifest) {
  var node = document.getElementById(navNodeId(taskPath));
  if (!node) return;
  var old = node.querySelector(':scope > .attachment-branch');
  var wasExpanded = old
    ? old.classList.contains('expanded')
    : !!_attachmentExpanded[taskPath];
  if (old) old.remove();
  var files = manifest && manifest.files ? manifest.files : [];
  if (!files.length) return;

  var branch = document.createElement('div');
  branch.className = 'attachment-branch' + (wasExpanded ? ' expanded' : '');
  branch.dataset.owner = taskPath;
  var toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'attachment-branch-toggle';
  toggle.tabIndex = -1;
  toggle.setAttribute('role', 'treeitem');
  var taskRow = node.querySelector(':scope > .task-row');
  var taskLevel = Number(taskRow && taskRow.getAttribute('aria-level')) || 1;
  toggle.setAttribute('aria-level', String(taskLevel + 1));
  toggle.setAttribute('aria-expanded', wasExpanded ? 'true' : 'false');
  toggle.innerHTML = '<span class="attachment-branch-caret" aria-hidden="true">▸</span>'
    + '<span>Attachments</span><span class="attachment-branch-count">'
    + files.length + '</span>';
  var children = document.createElement('div');
  children.className = 'attachment-branch-children';
  children.setAttribute('role', 'group');
  children.hidden = !wasExpanded;
  children.appendChild(
    renderAttachmentLevel(taskPath, attachmentTree(files), 0, taskLevel)
  );
  toggle.onclick = function(event) {
    event.stopPropagation();
    var expanded = !branch.classList.contains('expanded');
    _attachmentExpanded[taskPath] = expanded;
    branch.classList.toggle('expanded', expanded);
    children.hidden = !expanded;
    toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  };
  branch.appendChild(toggle);
  branch.appendChild(children);
  if (!window.STANDALONE) {
    var sink = document.createElement('span');
    sink.className = 'artifact-event-sink';
    sink.dataset.artifactOwner = taskPath;
    sink.setAttribute('sse-swap', 'artifacts:' + taskPath);
    sink.setAttribute('hx-swap', 'none');
    branch.appendChild(sink);
  }
  var childrenContainer = node.querySelector(':scope > .task-children');
  node.insertBefore(branch, childrenContainer || null);
  if (window.htmx) htmx.process(branch);
  refreshRovingTabindex();
}

function loadAttachmentBranches(scope) {
  var nodes = (scope || document).querySelectorAll('.task-node[data-path]');
  nodes.forEach(function(node) {
    var owner = node.dataset.path || '';
    fetchAttachmentManifest(owner).then(function(manifest) {
      if (!manifest) return;
      _artifactManifests[owner] = manifest;
      renderAttachmentBranch(owner, manifest);
    }).catch(function() {
      /* Soft-fail: a missing manifest just leaves the Attachments branch absent
         from this background sidebar decoration, not a user-initiated navigation
         that needs an error state. */
    });
  });
}

function renderActiveArtifactBody(taskPath, entry, body, token) {
  if (!entry.previewable) {
    var unavailable = document.createElement('p');
    unavailable.className = 'artifact-state artifact-state-unavailable';
    unavailable.textContent = artifactUnavailableReason(entry);
    body.appendChild(unavailable);
    return;
  }
  if (entry.kind === 'image') {
    var image = document.createElement('img');
    image.className = 'artifact-image-preview';
    image.src = artifactResourceUrl(taskPath, entry.path);
    image.alt = entry.name;
    body.appendChild(image);
    return;
  }
  if (entry.kind === 'pdf') {
    var frame = document.createElement('iframe');
    frame.className = 'artifact-pdf-preview';
    frame.setAttribute('sandbox', '');
    frame.title = 'PDF preview: ' + entry.name;
    frame.src = artifactResourceUrl(taskPath, entry.path);
    body.appendChild(frame);
    return;
  }
  body.textContent = 'Loading preview…';
  readArtifactText(taskPath, entry).then(function(text) {
    if (token !== _artifactPreviewToken || taskPath !== activePath
        || entry.path !== activeArtifactPath) return;
    body.innerHTML = '';
    if (entry.kind === 'markdown') {
      var markdown = document.createElement('div');
      markdown.className = 'rendered-md artifact-markdown-preview';
      markdown.innerHTML = renderMarkdown(
        text, null, taskPath, { artifactPath: entry.path }
      );
      body.appendChild(markdown);
    } else if (entry.kind === 'notebook') {
      body.appendChild(renderNotebookPreview(text, taskPath, entry.path));
    } else {
      var languages = { python: 'python', julia: 'julia', r: 'r' };
      body.appendChild(renderArtifactCode(text, languages[entry.kind] || ''));
    }
  }).catch(function(error) {
    if (token !== _artifactPreviewToken) return;
    body.innerHTML = '<p class="artifact-state artifact-state-unavailable"></p>';
    body.firstChild.textContent = error.message;
  });
}

function loadActiveArtifact(taskPath, artifactPath) {
  var region = document.getElementById('active-node');
  if (!region) return;
  var token = ++_artifactPreviewToken;
  region.innerHTML = '<p class="artifact-state">Loading attachment…</p>';
  fetchAttachmentManifest(taskPath).then(function(manifest) {
    if (token !== _artifactPreviewToken || taskPath !== activePath
        || artifactPath !== activeArtifactPath) return;
    _artifactManifests[taskPath] = manifest;
    renderAttachmentBranch(taskPath, manifest);
    var entry = artifactManifestEntry(taskPath, artifactPath);
    if (!entry) throw new Error('This attachment is unavailable.');
    region.innerHTML = '';
    var head = document.createElement('header');
    head.className = 'active-node-head attachment-active-head';
    var heading = document.createElement('h2');
    heading.className = 'active-node-title';
    heading.tabIndex = -1;
    heading.textContent = entry.name;
    /* An attachment is a page in its own right, so the tab names it too. */
    setTabTitle(entry.name);
    head.appendChild(heading);
    var owner = document.createElement('button');
    owner.type = 'button';
    owner.className = 'attachment-owner-action';
    owner.textContent = 'Back to task';
    owner.onclick = function() { setActive(taskPath); };
    head.appendChild(owner);
    var actions = buildArtifactPreviewHead(taskPath, entry)
      .querySelector('.artifact-actions');
    if (actions) head.appendChild(actions);
    region.appendChild(head);
    var meta = document.createElement('p');
    meta.className = 'attachment-active-meta';
    meta.textContent = entry.path + ' · ' + entry.kind + ' · '
      + formatArtifactBytes(entry.size);
    region.appendChild(meta);
    var body = document.createElement('div');
    body.className = 'artifact-preview-body attachment-active-body';
    region.appendChild(body);
    renderActiveArtifactBody(taskPath, entry, body, token);
    document.querySelectorAll('.attachment-file-row').forEach(function(row) {
      row.classList.toggle('nav-active',
        row.dataset.artifactOwner === taskPath
        && row.dataset.artifactPath === artifactPath);
    });
    if (_moveFocusOnLoad) {
      _moveFocusOnLoad = false;
      heading.focus({ preventScroll: true });
    }
  }).catch(function(error) {
    if (token !== _artifactPreviewToken) return;
    region.innerHTML = '<p class="artifact-state artifact-state-unavailable"></p>';
    region.firstChild.textContent = error.message;
    /* The pane names no attachment now, so neither may the tab. */
    setTabTitle('');
  });
}

function refreshAttachmentManifest(taskPath, manifest) {
  _artifactManifests[taskPath] = manifest;
  renderAttachmentBranch(taskPath, manifest);
  if (taskPath === activePath && activeArtifactPath) {
    loadActiveArtifact(taskPath, activeArtifactPath);
  }
}

/* notebookjs supplies the notebook/worksheet/cell model. Its permissive default
   renderers are replaced once with this dashboard's existing safe stack. */
var _notebookRenderContext = null;

function notebookJoin(value) {
  if (Array.isArray(value)) return value.map(notebookJoin).join('');
  return value == null ? '' : String(value);
}

function notebookUnsupported(label) {
  var fallback = document.createElement('div');
  fallback.className = 'nb-unsupported-output';
  fallback.setAttribute('role', 'note');
  fallback.textContent = 'Unsupported notebook content: ' + label;
  return fallback;
}

function notebookLanguage(cell) {
  var ctx = _notebookRenderContext || {};
  var notebook = ctx.notebook || {};
  var metadata = notebook.metadata || {};
  var value = (cell.raw && cell.raw.language)
    || metadata.language
    || (metadata.kernelspec && metadata.kernelspec.language)
    || (metadata.language_info && metadata.language_info.name)
    || '';
  return String(value).toLowerCase() === 'r' ? 'r' : String(value).toLowerCase();
}

function utf8ToBase64(value) {
  var bytes = new TextEncoder().encode(value);
  var binary = '';
  for (var i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary);
}

function notebookAttachmentDataUrl(bundle) {
  if (!bundle || typeof bundle !== 'object') return '';
  if (bundle['image/png']) {
    return 'data:image/png;base64,' + notebookJoin(bundle['image/png']).replace(/\s/g, '');
  }
  if (bundle['image/jpeg']) {
    return 'data:image/jpeg;base64,' + notebookJoin(bundle['image/jpeg']).replace(/\s/g, '');
  }
  if (bundle['image/svg+xml']) {
    var safeSvg = DOMPurify.sanitize(notebookJoin(bundle['image/svg+xml']), {
      USE_PROFILES: { svg: true, svgFilters: true },
    });
    return 'data:image/svg+xml;base64,' + utf8ToBase64(safeSvg);
  }
  return '';
}

function materializeNotebookAttachments(markdown, attachments) {
  var warnings = [];
  var text = markdown.replace(/attachment:([^\s)"'<>]+)/g, function(match, encodedName) {
    var name = encodedName;
    try { name = decodeURIComponent(encodedName); } catch (e) {}
    var value = notebookAttachmentDataUrl(attachments && attachments[name]);
    if (!value) {
      if (warnings.indexOf(name) === -1) warnings.push(name);
      return match;
    }
    return value;
  });
  return { text: text, warnings: warnings };
}

function renderNotebookHtml(value) {
  var ctx = _notebookRenderContext || {};
  var holder = document.createElement('div');
  holder.className = 'nb-html-output rendered-md';
  holder.innerHTML = renderMarkdown(
    notebookJoin(value),
    null,
    ctx.taskPath || '',
    { artifactPath: ctx.artifactPath || '' }
  );
  return holder;
}

function renderNotebookLatex(value) {
  var holder = document.createElement('div');
  holder.className = 'nb-latex-output rendered-md';
  try {
    holder.innerHTML = DOMPurify.sanitize(katex.renderToString(
      notebookJoin(value),
      { displayMode: true, throwOnError: false, trust: false }
    ), { ADD_ATTR: ['style', 'class'] });
  } catch (e) {
    holder.textContent = notebookJoin(value);
  }
  return holder;
}

function renderNotebookSvg(value) {
  var holder = document.createElement('div');
  holder.className = 'nb-svg-output';
  holder.innerHTML = DOMPurify.sanitize(notebookJoin(value), {
    USE_PROFILES: { svg: true, svgFilters: true },
  });
  return holder;
}

function renderNotebookOutput(raw) {
  raw = raw || {};
  if (raw.output_type === 'stream') {
    var stream = renderArtifactCode(notebookJoin(raw.text), '');
    stream.classList.add('nb-stream-output');
    return stream;
  }
  if (raw.output_type === 'error' || raw.output_type === 'pyerr') {
    var traceback = raw.traceback
      ? notebookJoin(Array.isArray(raw.traceback) ? raw.traceback.join('\n') : raw.traceback)
      : [raw.ename, raw.evalue].filter(Boolean).join(': ');
    var error = renderArtifactCode(traceback, '');
    error.classList.add('nb-error-output');
    return error;
  }

  var bundle = raw.data || raw;
  var safeFormats = [
    'image/png', 'png', 'image/jpeg', 'jpeg',
    'image/svg+xml', 'text/svg+xml', 'svg',
    'text/html', 'html', 'text/markdown',
    'text/latex', 'latex', 'text/plain', 'text',
  ];
  var format = safeFormats.find(function(name) {
    return bundle[name] !== undefined && bundle[name] !== null;
  });
  if (!format) {
    var formats = Object.keys(bundle).filter(function(name) {
      return name.indexOf('/') !== -1 || name === 'javascript';
    });
    return notebookUnsupported(formats.length ? formats.join(', ') : (raw.output_type || 'unknown output'));
  }
  var value = bundle[format];
  if (format === 'image/png' || format === 'png'
      || format === 'image/jpeg' || format === 'jpeg') {
    var image = document.createElement('img');
    image.className = 'nb-image-output';
    var subtype = (format === 'image/jpeg' || format === 'jpeg') ? 'jpeg' : 'png';
    image.src = 'data:image/' + subtype + ';base64,' + notebookJoin(value).replace(/\s/g, '');
    image.alt = 'Notebook output';
    return image;
  }
  if (format === 'image/svg+xml' || format === 'text/svg+xml' || format === 'svg') {
    return renderNotebookSvg(value);
  }
  if (format === 'text/html' || format === 'html' || format === 'text/markdown') {
    return renderNotebookHtml(value);
  }
  if (format === 'text/latex' || format === 'latex') {
    return renderNotebookLatex(value);
  }
  return renderArtifactCode(notebookJoin(value), '');
}

function installNotebookAdapter() {
  if (!window.nb || nb._superraAdapterInstalled) return !!window.nb;
  nb._superraAdapterInstalled = true;
  nb.executeJavaScript = false;
  nb.sanitizer = function(value) {
    return DOMPurify.sanitize(value, { ADD_ATTR: ['style', 'class'] });
  };
  nb.markdown = function(value) {
    var ctx = _notebookRenderContext || {};
    return renderMarkdown(
      notebookJoin(value),
      null,
      ctx.taskPath || '',
      { artifactPath: ctx.artifactPath || '' }
    );
  };
  nb.highlighter = function(value, pre, code, language) {
    if (!language || !window.hljs || !hljs.getLanguage(language)) return value;
    try {
      return hljs.highlight(value, {
        language: language,
        ignoreIllegals: true,
      }).value;
    } catch (e) {
      return value;
    }
  };

  nb.Output.prototype.render = function() {
    var outer = document.createElement('div');
    outer.className = 'nb-output';
    outer.appendChild(renderNotebookOutput(this.raw));
    this.el = outer;
    return outer;
  };
  nb.Cell.prototype.render = function() {
    var cell = document.createElement('section');
    cell.className = 'nb-cell nb-' + (this.type || 'unknown') + '-cell';
    if (this.type === 'markdown') {
      var attached = materializeNotebookAttachments(
        notebookJoin(this.raw.source),
        this.raw.attachments || {}
      );
      var markdown = document.createElement('div');
      markdown.className = 'rendered-md';
      var ctx = _notebookRenderContext || {};
      markdown.innerHTML = renderMarkdown(
        attached.text,
        null,
        ctx.taskPath || '',
        { artifactPath: ctx.artifactPath || '' }
      );
      cell.appendChild(markdown);
      attached.warnings.forEach(function(name) {
        cell.appendChild(notebookUnsupported('cell attachment ' + name));
      });
    } else if (this.type === 'raw') {
      var raw = document.createElement('pre');
      raw.className = 'nb-raw-cell';
      raw.textContent = notebookJoin(this.raw.source);
      cell.appendChild(raw);
    } else if (this.type === 'code') {
      var source = this.input ? notebookJoin(this.input.raw) : notebookJoin(this.raw.source || this.raw.input);
      if (source) {
        var input = document.createElement('div');
        input.className = 'nb-input';
        input.appendChild(renderArtifactCode(source, notebookLanguage(this)));
        cell.appendChild(input);
      }
      (this.outputs || []).forEach(function(output) {
        cell.appendChild(output.render());
      });
    } else {
      cell.appendChild(notebookUnsupported('cell type ' + (this.type || 'unknown')));
    }
    this.el = cell;
    return cell;
  };
  return true;
}

function renderNotebookPreview(rawText, taskPath, artifactPath) {
  var outer = document.createElement('div');
  outer.className = 'notebook-preview';
  if (!installNotebookAdapter()) {
    outer.appendChild(notebookUnsupported('notebook renderer unavailable'));
    return outer;
  }
  var parsed;
  try {
    parsed = JSON.parse(rawText);
  } catch (e) {
    outer.appendChild(notebookUnsupported('invalid notebook JSON'));
    return outer;
  }
  if (!parsed || typeof parsed !== 'object'
      || (!Array.isArray(parsed.cells)
          && !(Array.isArray(parsed.worksheets) && parsed.worksheets.length))) {
    outer.appendChild(notebookUnsupported('missing cells'));
    return outer;
  }
  _notebookRenderContext = {
    taskPath: taskPath,
    artifactPath: artifactPath,
    notebook: parsed,
  };
  try {
    var rendered = nb.parse(parsed).render();
    var staging = document.createElement('div');
    staging.appendChild(rendered);
    outer.innerHTML = DOMPurify.sanitize(staging.innerHTML, {
      ADD_ATTR: ['style', 'class', 'data-prompt-number', 'data-language'],
    });
  } catch (e) {
    outer.innerHTML = '';
    outer.appendChild(notebookUnsupported('malformed notebook structure'));
  } finally {
    _notebookRenderContext = null;
  }
  return outer;
}

/* Open one section in the active-node card: mirror toggleSection's expand
   branch (open + uncap + lazy-render the x-markdown payload) without the toggle
   event, since the card opens sections programmatically rather than on click. */
function revealCardSection(wrapper, taskPath) {
  var content = wrapper.querySelector(':scope > .section-content');
  var toggle = wrapper.querySelector(':scope > .section-toggle');
  if (!content) return;
  var icon = toggle ? toggle.querySelector('.section-icon') : null;
  var preview = toggle ? toggle.querySelector('.section-preview') : null;
  var sectionName = wrapper.getAttribute('data-section') || '';

  content.classList.add('open');
  if (icon) icon.classList.add('expanded');
  uncapAfterTransition(content);
  if (preview) preview.style.display = 'none';

  var renderedMd = content.querySelector('.rendered-md');
  if (renderedMd && !renderedMd.dataset.rendered) {
    var tmpl = renderedMd.querySelector('script[type="text/x-markdown"]');
    if (tmpl) {
      renderedMd.innerHTML = renderMarkdown(tmpl.textContent, sectionName, taskPath);
      renderedMd.dataset.rendered = 'true';
    }
    if (sectionName === REPRO_SECTION) renderReproStepTable(renderedMd, taskPath);
  }
}

/* Status of a task from its sidebar row, when that row is in the DOM (the
   nav rows carry data-status). Falls back to '' so the caller omits the badge
   for a deep-link target whose row hasn't materialized yet. */
function navRowStatus(path) {
  var row = document.getElementById(navNodeId(path));
  return row ? (row.dataset.status || '') : '';
}

/* Wait for the sidebar update kicked off by the same setActive() call to
   finish materializing the row (a completion hook on updateSidebar's promise,
   not a fixed-interval poll), then inject the status badge into the card
   header. Bails if the card has since navigated away (token mismatch) or the
   row never appeared. Best-effort cosmetic fill for fresh deep descents. */
function patchCardBadgeWhenReady(path, token) {
  _lastSidebarUpdate.then(function() {
    if (token !== loadActiveNode._token) return;        /* navigated away */
    var status = navRowStatus(path);
    var head = document.querySelector('#active-node .active-node-head');
    if (status && head && !head.querySelector('.badge')) {
      var badge = document.createElement('span');
      badge.className = 'badge badge-' + status;
      badge.textContent = status;
      head.appendChild(badge);
    }
  });
}

/* Same deep-descent race for the tab: pathTitles is harvested from the sidebar
   row, so a fresh descent names the tab after the path slug until the row lands.
   Re-read the title once this tick's sidebar update settles. */
function patchTabTitleWhenReady(path, token) {
  _lastSidebarUpdate.then(function() {
    if (token !== loadActiveNode._token) return;        /* navigated away */
    if (pathTitles[path]) setTabTitle(pathTitles[path]);
  });
}

/* Children panel: the active node's direct children, rendered as clickable
   `.child-card`s — never a mermaid graph (the key inversion: subtasks live in
   the main panel). A single GET /api/children-graph?root=<path> supplies the
   child set (path, slug, title, status) and the inter-child dependency edges
   as JSON — no mermaid source, no text parsing; the root is special-cased
   (empty root would return the global graph, unrelated to this panel).
   Children with no inter-dependency get a flat grid; children with at least
   one inter-child dependency get the same cards in a layered topological flow
   with per-card `↳ after:` footers. Output is cached per (path,
   child-status+edge-signature) so navigating back to an unchanged node
   restores the built HTML; a child whose status or sibling deps changed busts
   the cache and re-renders. */
var _childrenDagCache = {};   /* path -> { sig, html } */

async function loadChildrenDag(path) {
  var region = document.getElementById('children-dag');
  if (!region) return;

  var token = (loadChildrenDag._token = (loadChildrenDag._token || 0) + 1);

  /* The root's children aren't reachable via /api/children-graph?root=''
     (empty root selects the global graph), and the root never has inter-child
     deps — read its direct children straight off the top-level nav rows,
     always in the DOM. */
  if (!path) {
    var rootKids = rootChildrenFromNav();
    var rootSig = childrenSig(rootKids, {});
    renderChildren(region, path, rootSig, function() {
      return '<button class="hc-btn" onclick="reproFocus(activePath)">Show in graph</button>' + (rootKids.length ? buildChildGrid(rootKids) : '');
    });
    return;
  }

  var resp, payload;
  try {
    resp = await fetch(wtUrl('/api/children-graph?root=' + encodeURIComponent(path)));
    if (token !== loadChildrenDag._token) return;  /* superseded */
    if (!resp.ok) { region.innerHTML = ''; return; }
    payload = await resp.json();
    if (token !== loadChildrenDag._token) return;  /* superseded */
  } catch (e) {
    region.innerHTML = '<p style="color:var(--st-rev-t)">Subtasks error: ' + e.message + '</p>';
    return;
  }

  var info = childrenGraphFromPayload(payload);

  /* Leaf node: no children -> render nothing (card-only view). */
  if (info.children.length === 0) {
    _childrenDagCache[path] = { sig: '', html: '' };
    region.innerHTML = '';
    return;
  }

  var sig = childrenSig(info.children, info.edges);
  renderChildren(region, path, sig, function() {
    return '<button class="hc-btn" onclick="reproFocus(activePath)">Show in graph</button>' + buildChildGrid(info.children);
  });
}

/* Cache signature: child paths + title + status + their direct-sibling deps,
   so a title edit, a status change, or a dependency change forces a
   re-render — a title-only edit would otherwise be masked by a hit on the
   stale-but-still-matching path/status/deps signature. */
function childrenSig(children, edges) {
  return children.map(function(c) {
    var deps = (edges[c.path] || []).slice().sort().join(',');
    return c.path + ':' + c.status + ':' + (c.title || '') + ':' + deps;
  }).join('|');
}

/* Restore from cache when (path, sig) is unchanged; otherwise build, cache,
   and inject. The cards' delegated click handler is the static markup's
   onclick, so cached HTML stays clickable with no re-wiring. */
function renderChildren(region, path, sig, build) {
  var cached = _childrenDagCache[path];
  if (cached && cached.sig === sig) {
    region.innerHTML = cached.html;
    return;
  }
  var html = build();
  region.innerHTML = html;
  _childrenDagCache[path] = { sig: sig, html: html };
}

/* Turn a GET /api/children-graph?root=<path> JSON payload into the
   direct-children set plus the inter-child dependency edges the flow/grid
   builders consume. `edges[childPath]` is the list of sibling paths that
   child directly depends on, straight off the server payload — no text
   parsing, no separate color->status map to keep in sync. Titles prefer the
   payload's own (non-lossy) title, falling back to the shared pathTitles
   lookup and then the slug. `hasEdges` is true when at least one child has a
   sibling dependency. */
function childrenGraphFromPayload(payload) {
  var children = (payload.children || []).map(function(c) {
    return {
      path: c.path,
      slug: c.slug,
      title: c.title || pathTitles[c.path] || c.slug,
      status: c.status || '',
    };
  });
  var edges = payload.edges || {};
  return { children: children, edges: edges, hasEdges: Object.keys(edges).length > 0 };
}

/* Root's direct children, read off the top-level nav rows (always inlined). */
function rootChildrenFromNav() {
  var out = [];
  var rootNode = document.getElementById('task-root');
  var container = rootNode
    ? rootNode.querySelector(':scope > .task-children')
    : document.getElementById('nav-tree');
  if (!container) return out;
  container.querySelectorAll(':scope > .task-node').forEach(function(node) {
    var p = node.dataset.path;
    if (!p) return;
    out.push({
      path: p,
      slug: p.split('/').pop(),
      title: pathTitles[p] || p.split('/').pop(),
      status: node.dataset.status || '',
    });
  });
  return out;
}

/* One clickable child card: slug + title + status badge, descending via the
   delegated onChildCardClick on the enclosing container. `depPaths` (optional)
   appends a `↳ after: <slug…>` footer naming the card's direct sibling deps. */
function childCardHTML(c, depPaths) {
  var deps = '';
  if (depPaths && depPaths.length) {
    var slugs = depPaths.map(function(d) {
      return '<span class="dep-slug">' + escapeHtml(d.split('/').pop()) + '</span>';
    }).join('<span class="dep-label">, </span>');
    deps = '<span class="child-card-deps"><span class="dep-arrow">↳</span>'
      + '<span class="dep-label">after: </span>' + slugs + '</span>';
  }
  return '<button class="child-card' + (depPaths && depPaths.length ? ' has-deps' : '')
    + '" data-path="' + escapeAttr(c.path) + '">'
    + (c.slug ? '<span class="child-card-slug">' + escapeHtml(c.slug) + '</span>' : '')
    + '<span class="child-card-title">' + escapeHtml(c.title) + '</span>'
    + (c.status ? '<span class="badge badge-' + c.status + '">' + c.status + '</span>' : '')
    + deps
    + '</button>';
}

var SUBTASK_HEADER = '<div class="dag-controls"><strong>Subtasks</strong>'
  + '<span class="dag-hint">— click to drill in</span></div>';

/* Flat clickable grid for children with no inter-dependency. */
function buildChildGrid(children) {
  var cards = children.map(function(c) { return childCardHTML(c, null); }).join('');
  return SUBTASK_HEADER
    + '<div class="child-grid" onclick="onChildCardClick(event)">' + cards + '</div>';
}

/* Layered dependency flow: the same cards grouped into topological tiers in
   execution order (tier 0 = children depending on no sibling; tier k = children
   whose sibling deps all sit in earlier tiers), stacked top->bottom with a
   subtle inter-tier flow cue. Each dependent card footers `↳ after:` with its
   direct sibling deps. Cycle-safe: a pass that places no remaining child drops
   the leftovers into the final tier instead of looping. */
function buildChildFlow(children, edges) {
  var byPath = {};
  children.forEach(function(c) { byPath[c.path] = c; });
  /* Keep only deps that point at an actual sibling in this child set. */
  var deps = {};
  children.forEach(function(c) {
    deps[c.path] = (edges[c.path] || []).filter(function(d) { return byPath[d]; });
  });

  var placed = {};
  var remaining = children.map(function(c) { return c.path; });
  var tiers = [];
  while (remaining.length) {
    var tier = remaining.filter(function(p) {
      return deps[p].every(function(d) { return placed[d]; });
    });
    if (tier.length === 0) tier = remaining.slice();   /* cycle -> flush rest */
    tier.forEach(function(p) { placed[p] = true; });
    tiers.push(tier);
    remaining = remaining.filter(function(p) { return !placed[p]; });
  }

  var tierHTML = tiers.map(function(tier, i) {
    var cards = tier.map(function(p) {
      return childCardHTML(byPath[p], deps[p]);
    }).join('');
    var sep = i < tiers.length - 1 ? '<div class="flow-sep" aria-hidden="true"></div>' : '';
    return '<div class="flow-tier">' + cards + '</div>' + sep;
  }).join('');

  return SUBTASK_HEADER
    + '<div class="child-flow" onclick="onChildCardClick(event)">' + tierHTML + '</div>';
}

/* Delegated click for both the grid and the flow: descend to the clicked child. */
function onChildCardClick(event) {
  var card = event.target.closest('.child-card');
  if (card && card.dataset.path !== undefined) setActive(card.dataset.path);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, function(c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}
function escapeAttr(s) { return escapeHtml(s).replace(/'/g, '&#39;'); }

/* popstate (back/forward): re-apply the URL without writing new history.
   The worktree lives in location.search and the task path in location.hash, so a
   single back/forward step can cross a ?wt= boundary. Detect that first: if the
   active worktree changed, re-point everything to the new worktree (sidebar, SSE,
   PROJECT_ROOT) before applying the hash; otherwise it's a plain task-path step. */
window.addEventListener('popstate', function() {
  var urlWt = readActiveWt();
  if (urlWt !== ACTIVE_WT) {
    applyWorktree(urlWt, parseHash(), parseArtifactHash());
    return;
  }
  restoring = true;
  setActive(parseHash(), parseArtifactHash());
  restoring = false;
  reproReadHash();
});

/* hashchange (manual address-bar hash edit): navigate to the new hash without
   writing new history. setActive's own pushState mutates location.hash and
   re-fires this event, so no-op when the hash already matches activePath;
   otherwise apply it in restoring mode (no extra pushState/history entry). */
window.addEventListener('hashchange', function() {
  if (parseHash() === activePath && parseArtifactHash() === activeArtifactPath) {
    reproReadHash();
    return;
  }
  restoring = true;
  setActive(parseHash(), parseArtifactHash());
  restoring = false;
  reproReadHash();
});

/* Resolve the initial hash on load (default the root), normalize it with
   replaceState so reload/back land cleanly, then activate it. */
function initRouter() {
  var path = parseHash();
  var artifactPath = parseArtifactHash();
  var routeParams = new URLSearchParams((location.hash || '').split('?').slice(1).join('?'));
  var reproState = routeParams.get('repro'), stepState=routeParams.get('step');
  restoring = true;
  history.replaceState(
    { path: path, attachment: artifactPath, wt: ACTIVE_WT },
    '',
    '#/'+path+(routeParams.toString()?'?'+routeParams.toString():'')
  );
  setActive(path, artifactPath);
  restoring = false;
  if (reproState || stepState) reproReadHash();
}

/* ════════════════════════════════════════════════════════════════════════
   Sidebar navigation tree — fills #nav-tree and is the only place the sidebar's
   fold state and active highlight live.
   ──────────────────────────────────────────────────────────────────────
   The sidebar is navigation-only: rows carry no task body. Two affordances per
   row — the disclosure caret folds children *in the sidebar only* (a local
   state independent of activePath), and the row label calls setActive(). The
   active highlight, ancestor auto-expand, and scroll-into-view are derived
   from activePath via updateSidebar(), so there is no second source of truth.
   ════════════════════════════════════════════════════════════════════════ */

/* Fetch the body-free nav tree, populate #nav-tree, then index its titles so
   the breadcrumb can show real titles. Resolves once the inline rows exist;
   deeper (>=3) branches stay lazy until their caret first opens. */
async function loadNavTree() {
  var container = document.getElementById('nav-tree');
  if (!container) return;
  try {
    var resp = await fetch(wtUrl('/nav'));
    if (!resp.ok) return;
    container.innerHTML = await resp.text();
    markLazyNodes();
    syncTreeSteps();
    indexNavTitles(container);
    applyTreeAria();   /* tree roles + roving tabindex on the freshly-injected rows */
    loadAttachmentBranches(container);
    /* Bind the freshly-injected rows' declarative sse-swap="task:<path>" to the
       live EventSource. htmx only wires sse-swap elements it has processed, and
       innerHTML injection bypasses that — so process the new subtree explicitly.
       Without this the sidebar never live-updates on a task:<path> event. */
    if (window.htmx) htmx.process(container);
  } catch (e) { /* best-effort: a failed sidebar must not block the router */ }
}

/* nav_node.html marks depth>=3 children for lazy load via an inline <script>
   that sets dataset.needsLoad. Those scripts do NOT run when the fragment is
   injected via innerHTML, so flag them here instead: a node carrying an empty
   .task-children container (children exist server-side but weren't inlined) is
   exactly a lazy branch. Leaf nodes have no .task-children at all, so they are
   never flagged. Idempotent; re-run after every nav fragment injection. */
function markLazyNodes() {
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node) {
    var kids = node.querySelector(':scope > .task-children');
    if (kids && kids.children.length === 0 && node.dataset.needsLoad !== 'false') {
      node.dataset.needsLoad = 'true';
    }
  });
}

/* Harvest path -> title from every nav row currently in the DOM into the
   shared pathTitles map (used by updateBreadcrumb). Idempotent; re-run after
   lazy loads bring more rows in. */
function indexNavTitles(scope) {
  (scope || document).querySelectorAll('#nav-tree .task-node').forEach(function(node) {
    var p = node.dataset.path;
    if (!p) return;
    var titleEl = node.querySelector(':scope > .task-row > .task-title-text');
    if (titleEl) pathTitles[p] = titleEl.textContent;
  });
}

/* DOM id of a nav row, mirroring nav_node.html's id attribute (path with '/'
   replaced by '-', falling back to 'root' when empty) — the root task (empty
   path) is `task-root`, not `task-`. */
function navNodeId(path) {
  return 'task-' + ((path || '').replace(/\//g, '-') || 'root');
}

/* Caret/label click handling, delegated from #nav-tree so it survives the
   innerHTML swaps from /nav and lazy /nav/{path} loads. */
function initSidebarEvents() {
  var container = document.getElementById('nav-tree');
  if (!container) return;
  container.addEventListener('click', function(ev) {
    var step=ev.target.closest('[data-tree-step]');if(step){ev.stopPropagation();revealReproStep(step.dataset.treeStep);return;}
    var toggle = ev.target.closest('.task-toggle');
    if (toggle && container.contains(toggle) && !toggle.classList.contains('leaf')) {
      ev.stopPropagation();
      toggleNavCaret(toggle.closest('.task-node'));
      return;
    }
    var row = ev.target.closest('.task-row');
    if (row && container.contains(row)) {
      var node = row.closest('.task-node');
      if (node && node.dataset.path !== undefined) setActive(node.dataset.path);
    }
  });
}

/* Fold/unfold one node's children in the sidebar only — never touches
   activePath. On first open of a lazy (>=3 depth) branch, fetch its children
   via /nav/{path} and index the new titles. */
async function toggleNavCaret(node) {
  if (!node) return;
  var toggle = node.querySelector(':scope > .task-row > .task-toggle');
  var children = node.querySelector(':scope > .task-children');
  if (!toggle || !children) return;

  var row = node.querySelector(':scope > .task-row');

  if (toggle.classList.contains('expanded')) {
    toggle.classList.remove('expanded');
    children.style.display = 'none';
    if (row) row.setAttribute('aria-expanded', 'false');
    refreshRovingTabindex();   /* rows just hidden may have held the tabbable row */
    return;
  }

  toggle.classList.add('expanded');
  children.style.display = '';
  if (row) row.setAttribute('aria-expanded', 'true');
  if (node.dataset.needsLoad === 'true') {
    node.dataset.needsLoad = 'false';
    await loadNavChildren(node);
  }
  syncTreeSteps();applyWorkspaceFilters(false);refreshRovingTabindex();
}

/* Lazily fetch a node's body-free children into its .task-children container.
   Returns true on success. Best-effort: a failed branch leaves the caret open
   but empty and never throws. */
async function loadNavChildren(node) {
  var path = node.dataset.path;
  var children = node.querySelector(':scope > .task-children');
  if (!path || !children) return false;
  try {
    var resp = await fetch(wtUrl('/nav/' + path));
    if (!resp.ok) return false;
    children.innerHTML = await resp.text();
    markLazyNodes();
    syncTreeSteps();
    indexNavTitles(children);
    applyTreeAria();   /* tree roles + roving tabindex on the newly-loaded rows */
    loadAttachmentBranches(children);
    /* Wire the lazily-loaded rows' sse-swap to the EventSource (see loadNavTree). */
    if (window.htmx) htmx.process(children);
    return true;
  } catch (e) { return false; }
}

/* Expand a node's children in the sidebar (no toggle of activePath). Loads
   lazily if needed so the next segment of an ancestor walk is present. */
async function expandNavNode(node) {
  if (!node) return;
  var toggle = node.querySelector(':scope > .task-row > .task-toggle');
  var children = node.querySelector(':scope > .task-children');
  if (!toggle || toggle.classList.contains('leaf') || !children) return;
  toggle.classList.add('expanded');
  children.style.display = '';
  var row = node.querySelector(':scope > .task-row');
  if (row) row.setAttribute('aria-expanded', 'true');
  if (node.dataset.needsLoad === 'true') {
    node.dataset.needsLoad = 'false';
    await loadNavChildren(node);
  }
}

/* Snapshot every currently-expanded nav node's path, so a sidebar rebuild can
   put the tree back the way the user left it instead of folding to the root.
   Returns data-path values for nodes whose own caret is open. */
function getExpandedNavPaths() {
  var paths = [];
  document.querySelectorAll('#nav-tree .task-node').forEach(function(node) {
    var toggle = node.querySelector(':scope > .task-row > .task-toggle');
    if (toggle && toggle.classList.contains('expanded') && node.dataset.path !== undefined) {
      paths.push(node.dataset.path);
    }
  });
  return paths;
}

/* Re-open the given paths after a fresh /nav rebuild. Shallow-to-deep so each
   parent is expanded (lazy-loading its children into the DOM) before its
   descendants are reached — deeper paths need their ancestor's lazy-loaded
   children in the DOM to be found at all. Paths that share a depth have no
   such dependency on each other, so each depth level's expandNavNode fetches
   run concurrently; only crossing to the next depth level waits. Best-effort:
   paths whose task was deleted are simply absent and skipped. */
async function restoreExpandedNavPaths(paths) {
  if (!paths || !paths.length) return;
  var byDepth = {};
  paths.forEach(function(p) {
    var depth = p ? p.split('/').length : 0;
    (byDepth[depth] = byDepth[depth] || []).push(p);
  });
  var depths = Object.keys(byDepth).map(Number).sort(function(a, b) { return a - b; });
  for (var i = 0; i < depths.length; i++) {
    await Promise.all(byDepth[depths[i]].map(function(p) {
      var node = document.getElementById(navNodeId(p));
      return node ? expandNavNode(node) : Promise.resolve();
    }));
  }
}

/* updateSidebar(path): the activePath-derived sidebar refresh. Highlights
   exactly the matching row, expands its full ancestor chain AND the current
   page's own children (lazy-loading any branch not yet in the DOM via the
   proven ancestor-walk-and-await loop), and scrolls it into view. Entirely
   best-effort — a failed sidebar branch never throws and never blocks the main
   panel, which fetches by full path. */
async function updateSidebar(path) {
  var container = document.getElementById('nav-tree');
  if (!container) return;

  /* Exactly one active row: clear the previous highlight + aria-selected. */
  container.querySelectorAll('.task-row.nav-active').forEach(function(r) {
    r.classList.remove('nav-active');
    r.removeAttribute('aria-selected');
  });

  try {
    /* The root/umbrella container (path "") holds every top-level task but is
       named by no path segment, so the segment walk below never reaches it. On a
       fresh deep-link load it starts collapsed, which leaves even a top-level
       target hidden inside a display:none .task-children. Expand it first so the
       ancestor chain is fully revealed. */
    var rootNode = document.getElementById(navNodeId(''));
    if (rootNode) await expandNavNode(rootNode);

    /* Walk root -> target, expanding (and lazy-loading) each ancestor so the
       next segment's node is in the DOM before we reach it. */
    var segs = path ? path.split('/') : [];
    var accumulated = '';
    for (var i = 0; i < segs.length - 1; i++) {
      accumulated = i === 0 ? segs[i] : accumulated + '/' + segs[i];
      var ancestor = document.getElementById(navNodeId(accumulated));
      if (!ancestor) break;  /* branch unresolvable in the current tree */
      await expandNavNode(ancestor);
    }
  } catch (e) { /* swallow: sidebar reveal is best-effort */ }

  var target = document.getElementById(navNodeId(path));
  if (!target) return;

  /* Show the current page's own children too: a selected branch reads more
     naturally expanded one level than as a closed caret the user must re-open
     to see what they just navigated into. Leaf nodes are a no-op (guarded in
     expandNavNode). */
  syncTreeSteps();
  await expandNavNode(target);

  var row = target.querySelector(':scope > .task-row');
  if (row) {
    row.classList.add('nav-active');
    row.setAttribute('aria-selected', 'true');
    /* Roving tabindex follows the active row so a subsequent Tab into the tree
       lands on it. (applyTreeAria also keeps roles current after any lazy load
       the ancestor walk just triggered.) */
    applyTreeAria();
    syncTreeSteps();applyWorkspaceFilters(false);
    requestAnimationFrame(function() {
      row.scrollIntoView({ block: 'nearest' });
    });
  }
}

/* ── Back-compat alias ──
   revealTask(path)/showTreeAndExpand(path) were the giant-tree reveal
   primitive; Kanban cards still call it to drill to the task in the Workspace.
   The deep-link ancestor-walk that expands the sidebar lives in updateSidebar
   above. */
function revealTask(path) { showView('workspace'); setActive(path); }
function showTreeAndExpand(path) { return revealTask(path); }

/* ════════════════════════════════════════════════════════════════════════
   Sidebar chrome — pin/unpin auto-hide, resizable width, narrow-screen drawer.
   ──────────────────────────────────────────────────────────────────────
   Pure presentation: none of this touches activePath. The workspace carries
   the mode class (.sb-pinned / .sb-unpinned / .sb-drawer) and the live
   --sidebar-width custom property; the sidebar slides via transform so pin and
   reveal stay smooth. Pin state + chosen width persist in localStorage.
   ════════════════════════════════════════════════════════════════════════ */
var SB_WIDTH_MIN = 200, SB_WIDTH_DEFAULT = 280;
var SB_NARROW = 860;                 /* px: below this the sidebar is a drawer */
/* px: a touch device in landscape needs at least this much width to carry the
   side-by-side pinned layout; below it (or in portrait) touch falls to drawer. */
var SB_TOUCH_PIN_MIN = 860;
var sbPinned = true;                 /* set from localStorage on init */
var sbWidth = SB_WIDTH_DEFAULT;
var _sbHideTimer = null;             /* auto-hide grace-delay timer (unpinned) */

function workspaceEl() { return document.getElementById('workspace'); }

/* Capability detection: a coarse-pointer / no-hover device (phone, tablet) has
   no usable hover, so the hover-reveal .sb-unpinned mode is unreachable by tap.
   Cached matchMedia, re-evaluated when an iPad gains/loses a trackpad keyboard
   (the `change` listener in initSidebarChrome re-applies the mode). */
var _sbTouchMQ = (typeof window.matchMedia === 'function')
  ? window.matchMedia('(hover: none), (pointer: coarse)') : null;
function sbIsTouch() { return !!(_sbTouchMQ && _sbTouchMQ.matches); }

/* Portrait orientation (touch tablets in portrait always get the drawer, so a
   12.9" iPad at 1024×1366 portrait is treated as a tablet, not a desktop). */
var _sbPortraitMQ = (typeof window.matchMedia === 'function')
  ? window.matchMedia('(orientation: portrait)') : null;
function sbIsPortrait() { return !!(_sbPortraitMQ && _sbPortraitMQ.matches); }

/* Whether the current viewport forces drawer mode (overrides pin state). */
function sbIsNarrow() { return window.innerWidth <= SB_NARROW; }

/* Touch drawer trigger: portrait, or narrow, or the user collapsed the pinned
   sidebar to the drawer (sbPinned=false maps to drawer on touch, not auto-hide).
   Landscape + enough room + pinned keeps the side-by-side persistent layout. */
function sbTouchWantsDrawer() {
  return sbIsPortrait() || sbIsNarrow()
    || window.innerWidth < SB_TOUCH_PIN_MIN || !sbPinned;
}

/* Apply the chosen width as the workspace custom property + sync the resizer's
   aria-valuenow. Clamped by the caller. */
function applySidebarWidth(w) {
  sbWidth = w;
  renderSidebarWidth(w);
}

/* Paint a width without touching the sbWidth preference: the mode re-clamp
   in applySidebarMode shows a narrower width while a drawer cap binds, but the
   user's chosen width must survive rotating back to a roomier layout. */
function renderSidebarWidth(w) {
  var ws = workspaceEl();
  if (ws) ws.style.setProperty('--sidebar-width', w + 'px');
  var rz = document.getElementById('sidebar-resizer');
  if (rz) {
    rz.setAttribute('aria-valuenow', String(w));
    rz.setAttribute('aria-valuemax', String(sidebarWidthMax()));
  }
}

/* Reachable max for the current mode: the drawer is CSS-capped at 86vw, so
   the JS cap matches and the handle never runs past the drawer's real edge. */
function sidebarWidthMax() {
  var ws = workspaceEl();
  if (ws && ws.classList.contains('sb-drawer')) {
    return Math.max(SB_WIDTH_MIN, Math.floor(window.innerWidth * 0.86));
  }
  return Math.max(SB_WIDTH_MIN,window.innerWidth-360);
}

function clampSidebarWidth(w) {
  if (isNaN(w)) return SB_WIDTH_DEFAULT;
  return Math.max(SB_WIDTH_MIN, Math.min(sidebarWidthMax(), Math.round(w)));
}

/* Set the workspace mode class from capability, pin state, and viewport.
   Two disjoint paths, never mixed:
   - Touch (coarse pointer / no hover): pinned-or-drawer only, never the
     hover-reveal .sb-unpinned (unreachable by tap). Drawer when portrait /
     narrow / not enough room / collapsed; persistent pinned otherwise.
   - Mouse/desktop: the original model — narrow wins (drawer), else
     pinned/unpinned per the stored pin state, hover-reveal intact. */
function applySidebarMode() {
  var ws = workspaceEl();
  if (!ws) return;
  var touch = sbIsTouch();
  var drawer, pinned, unpinned;
  if (touch) {
    drawer = sbTouchWantsDrawer();
    pinned = !drawer;
    unpinned = false;             /* never hover-reveal on touch */
  } else {
    var narrow = sbIsNarrow();
    drawer = narrow;
    pinned = !narrow && sbPinned;
    unpinned = !narrow && !sbPinned;
  }
  ws.classList.toggle('sb-touch', touch);
  ws.classList.toggle('sb-drawer', drawer);
  ws.classList.toggle('sb-pinned', pinned);
  ws.classList.toggle('sb-unpinned', unpinned);
  /* Mirror drawer mode onto <body>: the hamburger lives in the header (outside
     the workspace), so the header chrome keys off the body class to show it
     above the 860px width breakpoint (touch landscape collapsed to drawer). */
  document.body.classList.toggle('sb-drawer-mode', drawer);
  /* The drawer cap (86vw) can be tighter than the desktop max: show the
     clamped width but keep the sbWidth preference intact. */
  renderSidebarWidth(clampSidebarWidth(sbWidth));
  if (!unpinned) {
    /* Leaving the unpinned hover context: clear any reveal state. */
    ws.classList.remove('sb-revealed');
    clearTimeout(_sbHideTimer);
  }
  if (!drawer) closeDrawer();   /* a resize/rotate out of drawer drops it */
  syncPinToggle();
}

function syncPinToggle() {
  var btn = document.getElementById('pin-toggle');
  if (!btn) return;
  btn.setAttribute('aria-pressed', sbPinned ? 'true' : 'false');
  if (sbIsTouch()) {
    /* On touch the two pin states map to persistent-pinned <-> drawer, not
       pinned <-> auto-hide (there is no hover to reveal an auto-hidden bar). */
    if (sbPinned) {
      btn.setAttribute('aria-label', 'Collapse sidebar to drawer');
      btn.title = 'Pinned — tap to collapse to a drawer';
    } else {
      btn.setAttribute('aria-label', 'Pin sidebar (keep open)');
      btn.title = 'Drawer — tap to pin open';
    }
  } else if (sbPinned) {
    btn.setAttribute('aria-label', 'Unpin sidebar (auto-hide)');
    btn.title = 'Pinned — click to auto-hide';
  } else {
    btn.setAttribute('aria-label', 'Pin sidebar (keep open)');
    btn.title = 'Auto-hide — click to pin';
  }
}

/* Pin toggle: flip pinned/unpinned, persist, re-apply mode. On touch this maps
   pinned <-> drawer; on desktop pinned <-> auto-hide. A no-op on viewports that
   force the drawer regardless (narrow / portrait) beyond persisting the choice. */
function toggleSidebarPin() {
  sbPinned = !sbPinned;
  try { localStorage.setItem('dashboard-sidebar-pinned', sbPinned ? '1' : '0'); } catch (e) {}
  applySidebarMode();
}

/* ── Unpinned auto-hide: hover the rail/edge to reveal, mouse-leave to hide ── */
function revealSidebar() {
  var ws = workspaceEl();
  if (!ws || !ws.classList.contains('sb-unpinned')) return;
  clearTimeout(_sbHideTimer);
  ws.classList.add('sb-revealed');
}
/* Hide after a short grace delay so a brief cursor slip off the edge doesn't
   snap it shut. A navigation selection calls this with delay=0. */
function hideSidebar(delay) {
  var ws = workspaceEl();
  if (!ws || !ws.classList.contains('sb-unpinned')) return;
  clearTimeout(_sbHideTimer);
  _sbHideTimer = setTimeout(function() {
    ws.classList.remove('sb-revealed');
  }, delay == null ? 220 : delay);
}

function initSidebarChrome() {
  /* Restore persisted pin + width. */
  try {
    var savedPin = localStorage.getItem('dashboard-sidebar-pinned');
    if (savedPin !== null) sbPinned = savedPin === '1';
    var savedW = parseInt(localStorage.getItem('dashboard-sidebar-width'), 10);
    if (!isNaN(savedW)) sbWidth = Math.max(SB_WIDTH_MIN,savedW);
  } catch (e) {}
  applySidebarWidth(sbWidth);
  applySidebarMode();

  var sidebar = document.getElementById('sidebar');

  /* Hover-reveal: the retracted sidebar's visible edge is the hover target (the
     rail is pure decoration above it). Entering reveals; leaving starts the
     grace-delay hide. */
  if (sidebar) {
    sidebar.addEventListener('mouseenter', revealSidebar);
    sidebar.addEventListener('mouseleave', function() { hideSidebar(); });
  }

  initSidebarResizer();

  /* Re-evaluate mode on viewport changes (debounced via rAF). */
  var rafPending = false;
  window.addEventListener('resize', function() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(function() { rafPending = false; applySidebarMode(); });
  });

  /* Re-evaluate when input capability changes (an iPad gains/loses a pointer
     when a trackpad keyboard attaches/detaches) or the device is rotated —
     a portrait iPad must drop the persistent sidebar for the drawer. */
  function onCapabilityChange() { applySidebarMode(); }
  [_sbTouchMQ, _sbPortraitMQ].forEach(function(mq) {
    if (!mq) return;
    if (mq.addEventListener) mq.addEventListener('change', onCapabilityChange);
    else if (mq.addListener) mq.addListener(onCapabilityChange);  /* older Safari */
  });
}

/* ── Resizable width: pointer drag + keyboard (←/→) on the separator handle ── */
function initSidebarResizer() {
  var rz = document.getElementById('sidebar-resizer');
  var ws = workspaceEl();
  if (!rz || !ws) return;

  var dragging = false;

  function onMove(ev) {
    if (!dragging) return;
    /* Width = pointer X relative to the sidebar's left edge: the workspace
       edge when laid out beside the content, the viewport edge (0) when the
       drawer is fixed to the viewport. */
    var left = ws.classList.contains('sb-drawer') ? 0 : ws.getBoundingClientRect().left;
    applySidebarWidth(clampSidebarWidth(ev.clientX - left));
  }
  function onUp(ev) {
    if (!dragging) return;
    dragging = false;
    ws.classList.remove('sb-resizing');
    document.body.classList.remove('sb-resizing-active');
    try { rz.releasePointerCapture(ev.pointerId); } catch (e) {}
    window.removeEventListener('pointermove', onMove);
    window.removeEventListener('pointerup', onUp);
    window.removeEventListener('pointercancel', onUp);
    persistSidebarWidth();
  }
  rz.addEventListener('pointerdown', function(ev) {
    /* The handle is laid out beside the content (pinned/unpinned) or on the
       open drawer's edge; a closed drawer hides it, so refuse a stray press. */
    if (ws.classList.contains('sb-drawer') && !ws.classList.contains('sb-drawer-open')) return;
    ev.preventDefault();
    dragging = true;
    ws.classList.add('sb-resizing');
    document.body.classList.add('sb-resizing-active');
    /* Unpinned + drag: keep the sidebar revealed so the user sees the resize. */
    revealSidebar();
    /* Capture the pointer so a touch that leaves the strip keeps driving the
       drag; the listeners sit on window so the drag still ends cleanly when
       capture is unavailable. */
    try { rz.setPointerCapture(ev.pointerId); } catch (e) {}
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('pointercancel', onUp);
  });

  /* Keyboard: ←/← nudge by 16px, Home/End jump to clamp bounds. */
  rz.addEventListener('keydown', function(ev) {
    var step = ev.shiftKey ? 48 : 16;
    var next = null;
    var shown=Number(rz.getAttribute('aria-valuenow'));
    if (ev.key === 'ArrowLeft')       next = shown - step;
    else if (ev.key === 'ArrowRight') next = shown + step;
    else if (ev.key === 'Home')       next = SB_WIDTH_MIN;
    else if (ev.key === 'End')        next = sidebarWidthMax();
    if (next === null) return;
    ev.preventDefault();
    revealSidebar();
    applySidebarWidth(clampSidebarWidth(next));
    persistSidebarWidth();
  });
}

function persistSidebarWidth() {
  try { localStorage.setItem('dashboard-sidebar-width', String(sbWidth)); } catch (e) {}
}

/* ── Narrow-screen overlay drawer ──
   Toggled by the header hamburger. Open: show backdrop, trap focus inside the
   sidebar, Esc closes, and any navigation (setActive) closes it. Works only in
   drawer mode (narrow); on desktop the hamburger is hidden. */
var _drawerLastFocus = null;       /* element to restore focus to on close */

function toggleDrawer() {
  var ws = workspaceEl();
  if (!ws) return;
  if (ws.classList.contains('sb-drawer-open')) closeDrawer();
  else openDrawer();
}

function openDrawer() {
  var ws = workspaceEl();
  if (!ws || !ws.classList.contains('sb-drawer')) return;
  _drawerLastFocus = document.activeElement;
  ws.classList.add('sb-drawer-open');
  var ham = document.getElementById('nav-hamburger');
  if (ham) { ham.setAttribute('aria-expanded', 'true'); ham.setAttribute('aria-label', 'Close navigation'); }
  /* Move focus into the drawer so SR/keyboard users land inside it. */
  var first = drawerFocusables()[0];
  if (first) first.focus();
  document.addEventListener('keydown', drawerKeydown, true);
}

function closeDrawer() {
  var ws = workspaceEl();
  if (!ws || !ws.classList.contains('sb-drawer-open')) return;
  ws.classList.remove('sb-drawer-open');
  var ham = document.getElementById('nav-hamburger');
  if (ham) { ham.setAttribute('aria-expanded', 'false'); ham.setAttribute('aria-label', 'Open navigation'); }
  document.removeEventListener('keydown', drawerKeydown, true);
  /* Restore focus to the opener (hamburger) for keyboard continuity. */
  if (_drawerLastFocus && document.contains(_drawerLastFocus)) _drawerLastFocus.focus();
  else if (ham) ham.focus();
  _drawerLastFocus = null;
}

/* Focusable elements inside the open drawer, for the focus trap. */
function drawerFocusables() {
  var sidebar = document.getElementById('sidebar');
  if (!sidebar) return [];
  return Array.prototype.filter.call(
    sidebar.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"]), .task-row[tabindex="0"]'),
    function(el) { return el.offsetParent !== null || el === document.activeElement; }
  );
}

/* Esc closes; Tab/Shift+Tab cycle within the drawer (focus trap). */
function drawerKeydown(ev) {
  var ws = workspaceEl();
  if (!ws || !ws.classList.contains('sb-drawer-open')) return;
  if (ev.key === 'Escape') {
    ev.preventDefault();
    closeDrawer();
    return;
  }
  if (ev.key !== 'Tab') return;
  var f = drawerFocusables();
  if (f.length === 0) return;
  var first = f[0], last = f[f.length - 1];
  if (ev.shiftKey && document.activeElement === first) {
    ev.preventDefault(); last.focus();
  } else if (!ev.shiftKey && document.activeElement === last) {
    ev.preventDefault(); first.focus();
  }
}

/* Called from setActive after a navigation: auto-hide the unpinned overlay and
   close the drawer (a selection is a "done navigating" signal). */
function onNavigationChrome() {
  hideSidebar(0);
  closeDrawer();
}

/* ════════════════════════════════════════════════════════════════════════
   Keyboard navigation for the sidebar tree (role="tree", roving tabindex).
   ──────────────────────────────────────────────────────────────────────
   Exactly one row is tab-focusable at a time (roving tabindex); arrows move
   focus among the *visible* rows, →/← expand/collapse (or move in/out), and
   Enter/Space activate via setActive. ARIA (role, aria-expanded, aria-level,
   aria-selected) is applied to the injected rows after every nav load.
   ════════════════════════════════════════════════════════════════════════ */

/* Apply tree ARIA + roving tabindex to every nav row currently in the DOM.
   Idempotent; re-run after each /nav and lazy /nav/{path} injection. Rows are
   treeitems, their .task-children containers are groups, depth -> aria-level. */
function applyTreeAria() {
  var root = document.getElementById('nav-tree');
  if (!root) return;
  root.querySelectorAll('.task-node').forEach(function(node) {
    var row = node.querySelector(':scope > .task-row');
    if (!row) return;
    row.setAttribute('role', 'treeitem');
    row.setAttribute('aria-level', String(nodeDepth(node)));
    /* Label: "<slug> — <title>, <status>" for a meaningful SR announcement. */
    if (!row.getAttribute('aria-label')) {
      var slug = node.dataset.path ? node.dataset.path.split('/').pop() : 'root';
      var titleEl = row.querySelector('.task-title-text');
      var title = titleEl ? titleEl.textContent.trim() : '';
      var label = (slug ? slug : 'root') + (title ? ' — ' + title : '');
      if (node.dataset.status) label += ', ' + node.dataset.status;
      row.setAttribute('aria-label', label);
    }
    var toggle = row.querySelector(':scope > .task-toggle');
    var children = node.querySelector(':scope > .task-children');
    if (toggle && !toggle.classList.contains('leaf') && children) {
      children.setAttribute('role', 'group');
      row.setAttribute('aria-expanded',
        toggle.classList.contains('expanded') ? 'true' : 'false');
    } else {
      row.removeAttribute('aria-expanded');
    }
    /* Roving tabindex: default every row out of the tab order; the active row
       (or the first row) is made tabbable by refreshRovingTabindex. */
    if (!row.hasAttribute('tabindex')) row.setAttribute('tabindex', '-1');
  });
  refreshRovingTabindex();
}

/* 1-based aria-level from the number of .task-children ancestors. */
function nodeDepth(node) {
  var level = 1, p = node.parentElement;
  while (p) {
    if (p.classList && p.classList.contains('task-children')) level++;
    p = p.parentElement;
  }
  return level;
}

/* Ensure exactly one row is tabbable (tabindex=0): the active row if present,
   else the first visible row. Everything else is tabindex=-1. */
function refreshRovingTabindex() {
  var root = document.getElementById('nav-tree');
  if (!root) return;
  var rows = root.querySelectorAll(
    '.task-row, .attachment-branch-toggle, '
    + '.attachment-directory-row, .attachment-file-row'
  );
  rows.forEach(function(r) { r.setAttribute('tabindex', '-1'); });
  var active = root.querySelector('.attachment-file-row.nav-active')
    || root.querySelector('.task-row.nav-active');
  var target = (active && isRowVisible(active)) ? active : firstVisibleRow();
  if (target) target.setAttribute('tabindex', '0');
}

/* Visible = the row's node and all ancestor groups are displayed (not folded,
   not filtered out). */
function isRowVisible(row) {
  var el = row;
  while (el && el.id !== 'nav-tree') {
    if (el.nodeType === 1) {
      if (el.hidden) return false;
      var cs = el.style && el.style.display === 'none';
      if (cs || (el.classList && el.classList.contains('hidden'))) return false;
    }
    el = el.parentElement;
  }
  return true;
}

function firstVisibleRow() {
  var root = document.getElementById('nav-tree');
  if (!root) return null;
  var rows = root.querySelectorAll(
    '.task-row, .attachment-branch-toggle, '
    + '.attachment-directory-row, .attachment-file-row'
  );
  for (var i = 0; i < rows.length; i++) {
    if (isRowVisible(rows[i])) return rows[i];
  }
  return null;
}

/* Ordered list of currently-visible rows (document order = visual order). */
function visibleRows() {
  var root = document.getElementById('nav-tree');
  if (!root) return [];
  return Array.prototype.filter.call(
    root.querySelectorAll(
      '.task-row, .attachment-branch-toggle, '
      + '.attachment-directory-row, .attachment-file-row'
    ), isRowVisible);
}

/* Move roving focus to a row: make it the only tabbable row and focus it. */
function focusRow(row) {
  if (!row) return;
  var root = document.getElementById('nav-tree');
  if (root) root.querySelectorAll(
    '.task-row, .attachment-branch-toggle, '
    + '.attachment-directory-row, .attachment-file-row'
  ).forEach(function(r) {
    r.setAttribute('tabindex', '-1');
  });
  row.setAttribute('tabindex', '0');
  row.focus();
  row.scrollIntoView({ block: 'nearest' });
}

/* Keyboard handler for the tree, delegated from #nav-tree (survives row swaps).
   ↑/↓ move among visible rows; →/← expand/collapse or move in/out; Enter/Space
   activate; Home/End jump to first/last visible row. */
function initTreeKeyboard() {
  var root = document.getElementById('nav-tree');
  if (!root) return;
  root.addEventListener('keydown', function(ev) {
    var row = ev.target.closest ? ev.target.closest(
      '.task-row, .attachment-branch-toggle, '
      + '.attachment-directory-row, .attachment-file-row'
    ) : null;
    if (!row || !root.contains(row)) return;
    var isTask = row.classList.contains('task-row');
    var node = isTask ? row.closest('.task-node') : null;
    var toggle = isTask ? row.querySelector(':scope > .task-toggle') : null;
    var isAttachmentParent = row.classList.contains('attachment-branch-toggle')
      || row.classList.contains('attachment-directory-row');
    var isParent = isAttachmentParent
      || (toggle && !toggle.classList.contains('leaf'));
    var expanded = isAttachmentParent
      ? row.getAttribute('aria-expanded') === 'true'
      : (isParent && toggle.classList.contains('expanded'));
    var rows = visibleRows();
    var idx = rows.indexOf(row);

    switch (ev.key) {
      case 'ArrowDown':
        ev.preventDefault();
        if (idx >= 0 && idx < rows.length - 1) focusRow(rows[idx + 1]);
        break;
      case 'ArrowUp':
        ev.preventDefault();
        if (idx > 0) focusRow(rows[idx - 1]);
        break;
      case 'ArrowRight':
        ev.preventDefault();
        if (isTask) {
          var attachmentChild = node.querySelector(
            ':scope > .attachment-branch > .attachment-branch-toggle'
          );
          if (attachmentChild) {
            focusRow(attachmentChild);
          } else if (isParent && !expanded) {
            toggleNavCaret(node).then(function() { applyTreeAria(); });
          } else if (isParent && expanded && idx < rows.length - 1) {
            focusRow(rows[idx + 1]);
          }
        } else if (isParent && !expanded) {
          row.click();
        } else if (isParent && expanded && idx < rows.length - 1) {
          focusRow(rows[idx + 1]);
        }
        break;
      case 'ArrowLeft':
        ev.preventDefault();
        if (!isTask && isParent && expanded) {
          row.click();
        } else if (!isTask) {
          if (row.classList.contains('attachment-branch-toggle')) {
            var ownerRow = row.closest('.task-node')
              .querySelector(':scope > .task-row');
            if (ownerRow) focusRow(ownerRow);
            break;
          }
          var parentGroup = row.parentElement
            ? row.parentElement.parentElement : null;
          var parentDirectory = parentGroup
            ? parentGroup.closest('.attachment-directory') : null;
          var parentControl = parentDirectory
            ? parentDirectory.querySelector(':scope > .attachment-directory-row')
            : row.closest('.attachment-branch')
              .querySelector(':scope > .attachment-branch-toggle');
          if (parentControl) focusRow(parentControl);
        } else if (isParent && expanded) {
          toggleNavCaret(node);                 /* collapse */
          applyTreeAria();
        } else {
          /* Move to parent row. */
          var parentNode = node.parentElement
            ? node.parentElement.closest('.task-node') : null;
          var prow = parentNode
            ? parentNode.querySelector(':scope > .task-row') : null;
          if (prow) focusRow(prow);
        }
        break;
      case 'Enter':
      case ' ':
        if (isTask) {
          ev.preventDefault();
          if (node && node.dataset.path !== undefined) setActive(node.dataset.path);
        }
        break;
      case 'Home':
        ev.preventDefault();
        if (rows.length) focusRow(rows[0]);
        break;
      case 'End':
        ev.preventDefault();
        if (rows.length) focusRow(rows[rows.length - 1]);
        break;
    }
  });
}

/* ════════════════════════════════════════════════════════════════════════
   Live reload — the single-active-node SSE model.
   ──────────────────────────────────────────────────────────────────────
   Under master-detail the only open, detailed node is `activePath`; every
   other node is a body-free sidebar row. So the heavy capture/restore tree
   machinery is gone — the only state to preserve across a `task:<path>` echo
   is "is this the active card?" (re-fetch /node and re-render) and "is its
   parent the active node?" (re-render the children-DAG). htmx still owns the
   declarative `sse-swap="task:<path>"` outerHTML swap on each sidebar row and
   the summary bar; nothing here calls setActive from the server channel.

   Three watcher events (plan_dashboard.py): `task:<path>` (content edit,
   payload = body-free nav row), `summary-updated` (header bar, htmx-only),
   and `full-reload` (structural add/delete or worktree switch).
   ════════════════════════════════════════════════════════════════════════ */

/* parent('a/b/c') -> 'a/b'; parent('a') -> '' (root); parent('') -> null. */
function parentPath(path) {
  if (!path) return null;
  var i = path.lastIndexOf('/');
  return i === -1 ? '' : path.slice(0, i);
}

/* A task:<path> content edit arrived (dispatched from sseBeforeMessage, i.e. just
   *before* htmx swaps that path's body-free sidebar row). The fresh nav fragment
   carries no nav-active class, so the active highlight is wiped when the active
   row is the one swapped. Refresh only the detail-panel parts that depend on the
   changed task:
     - path === activePath  -> re-render the active card by re-running
       loadActiveNode (same /node fetch + section render + loadComments pipeline
       as a fresh navigation, without touching activePath / history), and re-assert
       the nav-active highlight the imminent row swap will clear. The highlight
       reads the row htmx is about to replace, so defer it past the swap.
     - parent(path) === activePath -> re-render the children panel (the changed
       task is a sibling card). loadChildrenDag's own (path, child-status+edge+
       title signature) cache makes this a no-op when nothing card-relevant
       changed. Deferred with the pathTitles reindex below, because the root
       panel (activePath === '') builds its cards from pathTitles rather than a
       server fetch — starting it before the reindex would bake the pre-edit
       title into a freshly (mis-)cached render. */
function onTaskUpdate(path) {
  var oldNode = document.getElementById(navNodeId(path));
  var oldBranch = oldNode
    && oldNode.querySelector(':scope > .attachment-branch');
  if (oldBranch) {
    _attachmentExpanded[path] = oldBranch.classList.contains('expanded');
  }
  /* Re-harvest pathTitles from the freshly-swapped row (deferred past the
     swap, same as the highlight re-assert above) so a title edit propagates
     to the breadcrumb and — for a changed sibling card — the children panel,
     without a structural full-reload. */
  setTimeout(function() {
    indexNavTitles();
    var manifest = attachmentManifest(path);
    if (manifest) renderAttachmentBranch(path, manifest);
    updateBreadcrumb(activePath, activeArtifactPath);
    if (path === activePath) {
      if (activeArtifactPath) loadActiveArtifact(path, activeArtifactPath);
      else loadActiveNode(path);
      _lastSidebarUpdate = updateSidebar(path);
    }
    if (path !== activePath && parentPath(path) === activePath) {
      loadChildrenDag(activePath);
    }
  }, 0);
}

/* ── full-reload: a structural add/delete within the active worktree ──
   The tree shape changed, so rebuild the whole sidebar from /nav, then re-run
   setActive(activePath) to restore highlight + breadcrumb + main panel + folds.
   If activePath no longer exists, fall back to its nearest surviving ancestor
   and replaceState the corrected hash (no new history entry — this is a server
   signal, not a user navigation). A worktree switch is a client navigation now
   (applyWorktree), not a server full-reload, so this only fires for in-worktree
   structural edits and never crosses worktrees. */
async function onFullReload() {
  var wt = ACTIVE_WT;
  /* Capture the open branches before the rebuild wipes them, so the tree
     reopens where the user left it instead of folding back to the root. */
  var expanded = getExpandedNavPaths();
  /* The tree just changed structurally (and a worktree switch can route
     through here too) — a cached children-panel render keyed to the old
     shape must not survive into the rebuilt tree. */
  _childrenDagCache = {};
  await loadNavTree();
  await restoreExpandedNavPaths(expanded);
  /* The tree shape/content changed — refresh the search index so live search
     reflects the new state. */
  await refreshSearchIndex();
  /* Refresh PROJECT_ROOT/selector before re-rendering the active card so the VS
     Code button bakes in the current worktree's root. */
  await fetchWorktrees();
  if(wt!==ACTIVE_WT)return;
  var wanted=activePath,target = resolveSurvivingPath(wanted);
  restoring = true;
  if (target !== wanted) {
    /* Relative '#/...' preserves the ?wt= in location.search. */
    history.replaceState({ path: target, wt: ACTIVE_WT }, '', '#/' + target);
  }
  setActive(target, target === wanted ? activeArtifactPath : '');
  restoring = false;
  if (currentView === 'reproduction') renderReproView(true);
  else loadReproData(true).then(function(){syncTreeSteps();applyWorkspaceFilters(false);renderReproDetail(_reproSelected);}).catch(function(){});
}

/* Nearest still-present path at or above `path`, by walking up until a nav row
   exists; '' (root) always survives. The sidebar tree has just been reloaded,
   so a missing row means that task dir was deleted. */
function resolveSurvivingPath(path) {
  var p = path;
  while (p) {
    if (document.getElementById(navNodeId(p))) return p;
    p = parentPath(p);
  }
  return '';  /* root */
}

/* ── Comment UI: suppress SSE node-swap after local comment changes ── */
var _commentEditPaths = {};  /* taskPath -> timestamp of last local comment op */
var _activeCommentEdit = null; /* { textarea: el, ... } — at most one open editor */

/* ── htmx SSE pre-message: the single dispatch point for task:<path> edits ──
   htmx owns the declarative `sse-swap="task:<path>"` swap of the body-free
   sidebar row. We hook sseBeforeMessage (not sseMessage) because the row swap is
   `hx-swap="outerHTML"`: htmx fires sseMessage on the *old* element AFTER it has
   been detached by the swap, so a body-level sseMessage listener never sees it.
   sseBeforeMessage fires on the still-attached row, before the swap, and bubbles
   to body — so it's the reliable place to react.

   event.target is the matched sidebar row (data-path); event.data is the new
   body-free fragment. Two responsibilities:
     1. Comment-edit suppression: a local comment write records a timestamp in
        _commentEditPaths; when the watcher's own echo for that path lands within
        3s, preventDefault so htmx doesn't clobber the freshly-edited row, clear
        the window, and skip the detail-panel refresh (re-fetching /node mid-edit
        would clobber the open editor).
     2. Detail-panel refresh: otherwise dispatch onTaskUpdate. The active-card and
        children-DAG refreshes are independent fetches, but re-asserting the
        nav-active highlight reads the row the swap is about to replace, so that
        part is deferred to after the swap (see onTaskUpdate). */
function withinCommentEditWindow(taskPath) {
  var ts = _commentEditPaths[taskPath];
  return !!(ts && (Date.now() - ts) < 3000);
}
document.body.addEventListener('htmx:sseBeforeMessage', function(event) {
  var artifactOwner = event.target && event.target.dataset
    ? event.target.dataset.artifactOwner
    : undefined;
  if (artifactOwner !== undefined) {
    event.preventDefault();
    try {
      var artifactData = event.detail && event.detail.data !== undefined
        ? event.detail.data
        : event.data;
      refreshAttachmentManifest(artifactOwner, JSON.parse(artifactData));
    } catch (e) {
      if (artifactOwner === activePath && activeArtifactPath) {
        var activeRegion = document.getElementById('active-node');
        if (activeRegion) {
          activeRegion.innerHTML =
            '<p class="artifact-state artifact-state-unavailable">'
            + 'The updated attachment list could not be read.</p>';
        }
      }
    }
    return;
  }
  var taskPath = event.target && event.target.dataset ? event.target.dataset.path : undefined;
  if (taskPath === undefined) return;  /* not a sidebar row (summary bar / full-reload) */
  if (withinCommentEditWindow(taskPath)) {
    event.preventDefault();
    delete _commentEditPaths[taskPath];
    return;
  }
  onTaskUpdate(taskPath);
  /* Recompute the sidebar comment-count badges after the row swap settles.
     Debounced so a burst of task: events (e.g. a script touching several
     tasks) collapses to a single /api/comments/summary fetch and a single
     badge repaint instead of one per event. */
  scheduleTreeCommentBadgeRefresh();
});

/* ── Worktree selector ──
   "Switching" is a navigation, not a server mutation: the selector pushes a new
   ?wt= into the URL and re-renders this tab's panels against that worktree. No
   POST, no all-clients SSE reload — other tabs viewing other worktrees are
   untouched. The option value is the worktree's ?wt= token (wt_id); the launch
   worktree's token is '' so its URL stays clean (`/` with no ?wt=). The current
   selection follows the URL (ACTIVE_WT), falling back to the launch worktree. */

/* The launch worktree's id from the last /api/worktrees fetch, used to map the
   empty (default) selector value <-> the launch worktree. */
var _launchWtId = '';
/* path (project root) of each worktree by its wt_id, so PROJECT_ROOT can follow
   the active ?wt= without another round-trip. */
var _wtProjectRoots = {};
/* resolved task-root absolute path of each worktree by its wt_id, so
   RESOLVED_ROOT / ROOT_PREFIX (the file-link base) can follow the active ?wt=. */
var _wtResolvedRoots = {};
/* Human name of each worktree by its wt_id, for the tab title's worktree half. */
var _wtTabLabels = {};

/* What to call a worktree: its branch, or its directory name when it has none
   (detached HEAD). The selector decorates this with the plan title and the
   agent marker; the tab title uses it bare. */
function worktreeLabel(wt) {
  return wt.branch || wt.path.split('/').pop();
}

/* Signature of the last-rendered worktree option set (ids + labels + active
   id). Lets a refresh-on-open re-fetch skip the innerHTML rebuild when nothing
   changed, so reopening the dropdown never flickers the native popup. */
var _wtSignature = '';

function populateWorktreeSelector(data) {
  var selector = document.getElementById('worktree-selector');
  var select = document.getElementById('worktree-select');
  if (!selector || !select) return;

  /* Hide if single worktree or no data */
  if (!data || !data.worktrees || data.worktrees.length <= 1) {
    selector.style.display = 'none';
    _wtSignature = '';
    return;
  }

  /* The active worktree = the URL's ?wt=, defaulting to the launch worktree when
     the URL names none. Match the option whose token equals that id. */
  var activeId = ACTIVE_WT || _launchWtId;

  /* Skip the rebuild when the option set and selection are unchanged — a
     refresh-on-open fires this on every dropdown click, and rewriting the
     options under an open native picker would collapse it. */
  var signature = activeId + '|' + data.worktrees.map(function(wt) {
    return (wt.wt_id || '') + ':' + (wt.branch || '') + ':' + (wt.plan_title || '') + ':' + (wt.is_agent ? 1 : 0);
  }).join('|');
  if (signature === _wtSignature && select.options.length) {
    selector.style.display = 'flex';
    return;
  }
  _wtSignature = signature;

  /* Build options */
  select.innerHTML = '';
  data.worktrees.forEach(function(wt) {
    var opt = document.createElement('option');
    /* Value is the ?wt= token. The launch worktree carries '' so selecting it
       navigates to a clean `/` (handled in switchWorktree). */
    var token = (wt.wt_id === data.launch_wt_id) ? '' : (wt.wt_id || '');
    opt.value = token;
    var label = worktreeLabel(wt);
    if (wt.plan_title) label += ' — ' + wt.plan_title;
    if (wt.is_agent) label = '[agent] ' + label;
    opt.textContent = label;
    if (wt.is_agent) opt.style.opacity = '0.6';
    if ((wt.wt_id || '') === activeId) opt.selected = true;
    select.appendChild(opt);
  });

  selector.style.display = 'flex';
}

/* The header VS Code button. With the local-open route it opens the ACTIVE task's
   file in the VS Code window already holding this worktree (the route passes the
   worktree folder alongside the file, so several worktrees of one repo each land
   in their own window); setActive re-points it as the researcher navigates.
   Without the route it keeps its vscode:// deep link to the worktree root
   (PROJECT_ROOT, re-pointed per ?wt= in fetchWorktrees). Labelled "VS Code" —
   "Workspace" is the #btn-workspace view toggle in the same header. Hidden in
   GitHub-file mode, which has no local checkout; doc-mode hides it via the shared
   .open-btn rule and standalone omits it from the template. Idempotent. */
function updateWorktreeOpenHref() {
  var btn = document.getElementById('worktree-open-btn');
  if (!btn) return;
  if (REPO_FILE_BASE) { btn.style.display = 'none'; return; }
  if (!btn.innerHTML) btn.innerHTML = EDITOR_ICON + '<span>VS Code</span>';
  if (window.LOCAL_OPEN) {
    btn.href = taskFileVscodeHref(activePath);
    btn.setAttribute('data-open-path', taskFileOpenPath(activePath));
    btn.setAttribute('data-open-target', 'editor');
    btn.title = "Open this task's file in this worktree's VS Code window";
  } else {
    btn.href = vscodeFileUri(PROJECT_ROOT);
    btn.title = 'Open this worktree in VS Code';
  }
  btn.style.display = '';
}

function fetchWorktrees() {
  /* Returns the fetch promise so onFullReload / applyWorktree can await the
     refreshed worktree metadata before re-rendering the active card (whose VS
     Code button bakes in PROJECT_ROOT). */
  return fetch(wtUrl('/api/worktrees'))
    .then(function(r) { return r.ok ? r.json() : null; })
    .then(function(data) {
      if (!data) return;
      _launchWtId = data.launch_wt_id || '';
      /* Index each worktree's project root and resolved task root by its ?wt=
         token so PROJECT_ROOT / RESOLVED_ROOT / ROOT_PREFIX can follow the
         active worktree (each worktree's root may sit at a different path and
         even a different basename). */
      _wtProjectRoots = {};
      _wtResolvedRoots = {};
      _wtTabLabels = {};
      data.worktrees.forEach(function(wt) {
        _wtProjectRoots[wt.wt_id || ''] = wt.path;
        _wtResolvedRoots[wt.wt_id || ''] = wt.plan_root || '';
        _wtTabLabels[wt.wt_id || ''] = worktreeLabel(wt);
      });
      /* Point PROJECT_ROOT / RESOLVED_ROOT at the URL's worktree so every
         vscode://file/ href resolves against the worktree this tab is bound to.
         The non-empty guard preserves the baked-in roots in standalone (file://)
         mode, where the fetch shim returns an empty worktree list. */
      var activeId = ACTIVE_WT || _launchWtId;
      var root = _wtProjectRoots[activeId];
      if (root) PROJECT_ROOT = root;
      var resolved = _wtResolvedRoots[activeId];
      if (resolved) {
        RESOLVED_ROOT = resolved;
        ROOT_PREFIX = resolved.split('/').filter(function(s) { return s; }).pop() || '';
      }
      populateWorktreeSelector(data);
      updateWorktreeOpenHref();
      /* This fetch lands after the first card render, and again on every
         worktree switch — the tab's worktree half follows it. */
      refreshTabTitle();
    })
    .catch(function() { /* graceful: hide selector */ });
}

/* Selector onchange: navigate this tab to the chosen worktree. The empty value
   is the launch worktree (clean `/`); a non-empty value sets ?wt=<token>. We
   keep the current task path (location.hash) so the same task opens in the new
   worktree when it exists; applyWorktree's sidebar rebuild falls back to the
   nearest surviving ancestor when it does not. */
function switchWorktree(token) {
  token = token || '';
  if (token === ACTIVE_WT) return;
  var hash = location.hash || '';
  var search = token ? ('?wt=' + encodeURIComponent(token)) : '';
  history.pushState(
    { path: parseHash(), attachment: parseArtifactHash(), wt: token },
    '',
    location.pathname + search + hash
  );
  applyWorktree(token, parseHash(), parseArtifactHash());
}

/* Re-point the whole tab at worktree *wtId* (the ?wt= token) without a full page
   reload: update ACTIVE_WT, reconnect the live-reload stream to the new
   worktree, refresh PROJECT_ROOT + the selector, then rebuild the sidebar and
   re-render the panels for *path* (or its nearest surviving ancestor). Used by
   the selector and by back/forward across a ?wt= boundary. */
async function applyWorktree(wtId, path, artifactPath) {
  _reproWorktrees[ACTIVE_WT]={nav:JSON.parse(JSON.stringify(_reproNav)),viewport:Object.assign({},_reproViewport),entered:_reproEntered,view:currentView,readerFull:_reproReaderFull,context:_reproContext.slice(),inspectorClosed:_reproInspectorClosed,notice:_reproNotice,filters:JSON.parse(JSON.stringify(_workspaceFilters))};
  ACTIVE_WT = wtId || '';
  var remembered=_reproWorktrees[ACTIVE_WT];
  _workspaceFilters=normalizeWorkspaceFilters(remembered&&remembered.filters);
  _reproNav=remembered?remembered.nav:{roots:[],view:'graph',mode:'scope',anchor:'',selected:'',expanded:[]};
  _reproViewport=remembered?remembered.viewport:{x:0,y:0,zoom:1};
  _reproReaderFull=!!(remembered&&remembered.readerFull&&_reproReaderPreference!==false);
  reproSizeWorkspace();
  document.getElementById('workspace').classList.toggle('dag-full-reader',_reproReaderFull||_reproReaderCompact);
  document.getElementById('workspace').classList.toggle('dag-reader-closed',_reproReaderClosed);
  _reproEntered=!!remembered;_reproSelected=_reproNav.selected;
  _reproData=null;_reproPending=null;_reproLoadSeq++;_reproLayoutCache=null;_reproContext=remembered?remembered.context:[];_reproInspectorClosed=!!(remembered&&remembered.inspectorClosed);_reproNotice=remembered?remembered.notice:'';_reproFitNext=!remembered;
  /* Children panels are per-worktree data — a cache entry from the worktree
     being left must not leak into the newly active one. */
  _childrenDagCache = {};
  _artifactManifests = {};
  _attachmentExpanded = {};
  reconnectSse();
  await loadNavTree();
  await refreshSearchIndex();
  await fetchWorktrees();
  var target = resolveSurvivingPath(path || '');
  restoring = true;
  if (target !== (path || '')) {
    history.replaceState({ path: target, wt: ACTIVE_WT }, '', location.pathname + location.search + '#/' + target);
  }
  setActive(target, target === (path || '') ? (artifactPath || '') : '');
  showView(remembered?remembered.view:'workspace');
  history.replaceState({wt:ACTIVE_WT},'',reproHash());
  applyWorkspaceFilters(false);
  restoring = false;
}

/* Re-point the htmx SSE stream at the active worktree's /events. The htmx sse
   extension caches its EventSource in the connect element's internalData; close
   the old one, rewrite sse-connect to carry the new ?wt=, then re-process the
   element so the extension opens a fresh source and re-binds every sse-swap
   listener under it (summary bar, full-reload sentinel, and — after the sidebar
   rebuild re-runs htmx.process — the nav rows). No-op in standalone mode. */
function reconnectSse() {
  if (window.STANDALONE || !window.htmx) return;
  var main = document.querySelector('.main-content');
  if (!main) return;
  var data = htmx.getInternalData ? htmx.getInternalData(main) : null;
  if (data && data.sseEventSource) {
    try { data.sseEventSource.close(); } catch (e) {}
    data.sseEventSource = null;
  }
  main.setAttribute('sse-connect', wtUrl('/events'));
  htmx.process(main);
}

/* Refresh the worktree list whenever the user reaches for the dropdown, so a
   worktree created or removed since page load shows up without a manual page
   refresh. The signature guard in populateWorktreeSelector makes this a no-op
   when nothing changed, so reopening never flickers the popup. focus covers
   keyboard; mousedown covers the click that opens the native picker. */
function initWorktreeSelectorRefresh() {
  var select = document.getElementById('worktree-select');
  if (!select) return;
  /* Opening the dropdown by mouse fires both mousedown and focus on the same
     click; opening by keyboard fires focus alone. Coalesce same-tick pairs
     into a single fetch. */
  var pending = false;
  var refresh = function() {
    if (pending) return;
    pending = true;
    setTimeout(function() { pending = false; }, 0);
    fetchWorktrees();
  };
  select.addEventListener('mousedown', refresh);
  select.addEventListener('focus', refresh);
}

/* Fetch worktrees on page load */
updateWorktreeOpenHref();  /* reveal off the baked-in PROJECT_ROOT before the fetch resolves */
fetchWorktrees();
initWorktreeSelectorRefresh();

/* ── SSE full-reload: structural changes (task added/deleted, worktree switch) ──
   #sse-full-reload carries hx-swap="none", so htmx never mutates the DOM for this
   event — the sse extension calls api.swap with a none-spec and fires no
   htmx:beforeSwap. The reliable signal is htmx:sseBeforeMessage on the element
   itself (the same hook task:<path> rows use); use it purely as a trigger to
   rebuild the sidebar and restore activePath. */
var fullReloadEl = document.getElementById('sse-full-reload');
if (fullReloadEl) {
  fullReloadEl.addEventListener('htmx:sseBeforeMessage', function() { onFullReload(); });
}

/* ── SSE repro-updated: a build rewrote the committed lock ──
   Same hx-swap="none" trigger-only pattern as full-reload; the payload is empty
   because the client re-fetches both reproduction payloads itself. */
var reproUpdatedEl = document.getElementById('sse-repro-updated');
if (reproUpdatedEl) {
  reproUpdatedEl.addEventListener('htmx:sseBeforeMessage', function() { onReproUpdated(); });
}

/* ── Comment UI functions ── */

function showCommentForm(btn) {
  var block = btn.closest('.commentable-block');
  /* If a form already exists in this block, just focus it */
  var existing = block.querySelector('.comment-form');
  if (existing) { existing.querySelector('textarea').focus(); return; }

  var form = document.createElement('div');
  form.className = 'comment-form';
  var ta = document.createElement('textarea');
  ta.placeholder = 'Add a comment...';
  var submitBtn = document.createElement('button');
  submitBtn.textContent = 'Comment';

  function submitComment() {
    var body = ta.value.trim();
    if (!body) return;

    var section = block.getAttribute('data-section');
    var blockIndex = parseInt(block.getAttribute('data-block'), 10);
    /* Extract text preview: first 60 chars of the block's text */
    var blockContent = block.querySelector('p, ul, ol, pre, blockquote, table, h1, h2, h3, h4, h5, h6');
    var textPreview = blockContent ? blockContent.textContent.substring(0, 60) : '';

    var taskNode = block.closest('.task-node');
    var taskPath = taskNode ? taskNode.dataset.path : '';

    /* Remember which sections are open before reloading comments */
    var openSections = [];
    taskNode.querySelectorAll('.section-content.open').forEach(function(sec) {
      var toggle = sec.previousElementSibling;
      var label = toggle ? toggle.querySelector('.section-label') : null;
      if (label) openSections.push(label.textContent);
    });

    _commentEditPaths[taskPath] = Date.now();
    fetch(wtUrl('/api/task/' + taskPath + '/comment'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        section: section,
        block_index: blockIndex,
        text_preview: textPreview,
        body: body
      })
    }).then(function(resp) {
      if (resp.ok) {
        form.remove();
        loadComments(taskPath);
      }
    });
  }

  submitBtn.onclick = submitComment;
  var cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.classList.add('btn-secondary');
  cancelBtn.onclick = function() { form.remove(); };
  ta.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      submitComment();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      form.remove();
    }
  });
  form.appendChild(ta);
  form.appendChild(submitBtn);
  form.appendChild(cancelBtn);
  block.appendChild(form);
  ta.focus();
}

/* Resolve the task node that holds a task's commentable blocks + sections.
   Those live in the active-node card (#active-node), not the body-free sidebar
   rows — and both carry `.task-node[data-path]`, with the sidebar row first in
   the DOM. So prefer the card; fall back to a global match for any caller that
   runs before the card exists. */
function commentTaskNode(taskPath) {
  var card = document.querySelector('#active-node .task-node[data-path="' + taskPath + '"]');
  return card || document.querySelector('.task-node[data-path="' + taskPath + '"]');
}

function loadComments(taskPath) {
  fetch(wtUrl('/api/task/' + taskPath + '/comments'))
    .then(function(resp) { return resp.ok ? resp.json() : []; })
    .then(function(comments) {
      /* Find the task node holding this task's commentable blocks (the card). */
      var taskNode = commentTaskNode(taskPath);
      if (!taskNode) return;

      /* Remove existing comment threads in this task */
      taskNode.querySelectorAll('.comment-thread').forEach(function(t) { t.remove(); });
      taskNode.querySelectorAll('.comment-orphan-warning').forEach(function(w) { w.remove(); });

      /* Group comments by section + block_index */
      var grouped = {};
      var orphaned = [];
      for (var i = 0; i < comments.length; i++) {
        var c = comments[i];
        var key = c.anchor.section + '::' + c.anchor.block_index;
        /* Check if the target block exists. CSS.escape guards against a
           section name (task-file content, e.g. a `##` header) containing a
           `"` — unescaped, that throws and aborts comment loading for the
           whole task. */
        var block = taskNode.querySelector(
          '.commentable-block[data-section="' + CSS.escape(c.anchor.section) + '"][data-block="' + CSS.escape(String(c.anchor.block_index)) + '"]'
        );
        if (block) {
          if (!grouped[key]) grouped[key] = { block: block, comments: [] };
          grouped[key].comments.push(c);
        } else {
          orphaned.push(c);
        }
      }

      /* Render grouped comments below their blocks */
      for (var key in grouped) {
        var entry = grouped[key];
        var thread = renderCommentThread(entry.comments, taskPath);
        entry.block.appendChild(thread);
      }

      /* Render orphaned comments at the section level */
      if (orphaned.length > 0) {
        var orphanBySection = {};
        for (var j = 0; j < orphaned.length; j++) {
          var sec = orphaned[j].anchor.section;
          if (!orphanBySection[sec]) orphanBySection[sec] = [];
          orphanBySection[sec].push(orphaned[j]);
        }
        for (var secName in orphanBySection) {
          var sectionDiv = taskNode.querySelector('[data-section="' + CSS.escape(secName) + '"] .section-content');
          if (sectionDiv && sectionDiv.classList.contains('open')) {
            var warning = document.createElement('div');
            warning.className = 'comment-orphan-warning';
            warning.textContent = 'Orphaned comments (anchor lost):';
            sectionDiv.appendChild(warning);
            var thread2 = renderCommentThread(orphanBySection[secName], taskPath);
            sectionDiv.appendChild(thread2);
          }
        }
      }

      /* Update section header badges with unresolved counts */
      updateSectionBadges(taskPath, comments);
    });
}

function renderCommentThread(comments, taskPath) {
  var thread = document.createElement('div');
  thread.className = 'comment-thread';
  for (var i = 0; i < comments.length; i++) {
    (function(c) {
      var item = document.createElement('div');
      item.className = 'comment-item' + (c.resolved ? ' comment-resolved' : '');

      var meta = document.createElement('div');
      meta.className = 'comment-meta';
      var ts = c.timestamp.substring(0, 16).replace('T', ' ');
      meta.textContent = (c.author || 'anonymous') + ' · ' + ts;

      var body = document.createElement('div');
      body.className = 'comment-body';
      body.textContent = c.body;

      var actions = document.createElement('div');
      actions.classList.add('comment-actions');

      var editBtn = document.createElement('button');
      editBtn.textContent = 'Edit';
      editBtn.classList.add('comment-action-btn');
      editBtn.onclick = function() { startEditComment(item, body, c, taskPath); };

      var resolveBtn = document.createElement('button');
      resolveBtn.textContent = c.resolved ? 'Unresolve' : 'Resolve';
      resolveBtn.classList.add('comment-action-btn');
      resolveBtn.onclick = function() { resolveComment(taskPath, c.id); };

      var deleteBtn = document.createElement('button');
      deleteBtn.textContent = 'Delete';
      deleteBtn.classList.add('comment-action-btn', 'comment-action-btn--danger');
      deleteBtn.onclick = function() { deleteComment(taskPath, c.id); };

      actions.appendChild(editBtn);
      actions.appendChild(resolveBtn);
      actions.appendChild(deleteBtn);
      item.appendChild(meta);
      item.appendChild(body);
      item.appendChild(actions);
      thread.appendChild(item);
    })(comments[i]);
  }
  return thread;
}

function updateSectionBadges(taskPath, comments) {
  var taskNode = commentTaskNode(taskPath);
  if (!taskNode) return;

  /* Count unresolved comments per section */
  var counts = {};
  for (var i = 0; i < comments.length; i++) {
    var c = comments[i];
    if (!c.resolved) {
      var sec = c.anchor.section;
      counts[sec] = (counts[sec] || 0) + 1;
    }
  }

  /* Update or create badges on each section-toggle */
  taskNode.querySelectorAll('[data-section]').forEach(function(wrapper) {
    var sectionName = wrapper.getAttribute('data-section');
    var toggle = wrapper.querySelector('.section-toggle');
    if (!toggle) return;

    var badge = toggle.querySelector('.section-comment-badge');
    var count = counts[sectionName] || 0;

    if (count > 0) {
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'section-comment-badge';
        toggle.appendChild(badge);
      }
      badge.textContent = count;
      badge.title = count + ' unresolved comment' + (count > 1 ? 's' : '');
    } else if (badge) {
      badge.remove();
    }
  });
}

/* ── Tree-level comment badges (bubble up through collapsed ancestors) ── */
/* Debounce window so a burst of SSE task: events triggers exactly one
   refresh (see the htmx:sseBeforeMessage handler above). */
var COMMENT_BADGE_DEBOUNCE_MS = 150;
var _commentBadgeRefreshTimer = null;
function scheduleTreeCommentBadgeRefresh() {
  clearTimeout(_commentBadgeRefreshTimer);
  _commentBadgeRefreshTimer = setTimeout(updateTreeCommentBadges, COMMENT_BADGE_DEBOUNCE_MS);
}

function updateTreeCommentBadges() {
  fetch(wtUrl('/api/comments/summary'))
    .then(function(resp) { return resp.ok ? resp.json() : {}; })
    .then(function(summary) {
      /* Build a map: target task-row element -> aggregated count */
      var targetCounts = new Map();

      for (var taskPath in summary) {
        var count = summary[taskPath];
        if (count <= 0) continue;

        var node = document.querySelector('.task-node[data-path="' + taskPath + '"]');
        if (!node) {
          /* Node not in DOM (lazy-loaded children). Walk up path segments
             until we find an ancestor that IS rendered. */
          var parts = taskPath.split('/');
          while (parts.length > 1 && !node) {
            parts.pop();
            node = document.querySelector('.task-node[data-path="' + parts.join('/') + '"]');
          }
          if (!node) continue;
        }

        /* Walk up ancestors: if an ancestor's children container is hidden,
           the current node isn't visible — bubble the badge to that ancestor.
           Stop as soon as we reach an ancestor whose children are shown. */
        var target = node;
        var parent = node.parentElement;
        while (parent) {
          var ancestorNode = parent.closest('.task-node');
          if (!ancestorNode) break;
          var ancestorChildren = ancestorNode.querySelector(':scope > .task-children');
          if (ancestorChildren && ancestorChildren.style.display === 'none') {
            target = ancestorNode;
          } else {
            break;
          }
          parent = ancestorNode.parentElement;
        }

        var targetRow = target.querySelector(':scope > .task-row');
        if (!targetRow) continue;

        var prev = targetCounts.get(targetRow) || 0;
        targetCounts.set(targetRow, prev + count);
      }

      /* Swap old badges for new in one synchronous pass — clearing only now,
         with the replacement set already computed, means existing badges
         never disappear while the fetch is in flight (no flicker window). */
      document.querySelectorAll('.tree-comment-badge').forEach(function(b) { b.remove(); });

      /* Render badges on the target rows — insert after the last
         badge/progress element so the badge sits near visible content
         rather than at the far end of the flex row */
      targetCounts.forEach(function(count, row) {
        var badge = document.createElement('span');
        badge.className = 'tree-comment-badge';
        badge.textContent = count;
        badge.title = count + ' unresolved comment' + (count > 1 ? 's' : '');
        var anchor = row.querySelector('.task-progress') || row.querySelector('.badge');
        if (anchor && anchor.nextSibling) {
          row.insertBefore(badge, anchor.nextSibling);
        } else if (anchor) {
          anchor.after(badge);
        } else {
          row.appendChild(badge);
        }
      });
    });
}

function _dismissActiveEdit() {
  /* Close the currently-open comment editor if any.
     Auto-saves if content changed, otherwise cancels.
     Does NOT call loadComments — caller can safely set up a new editor on any task. */
  if (!_activeCommentEdit) return;
  var prev = _activeCommentEdit;
  _activeCommentEdit = null;
  var newBody = prev.textarea.value.trim();
  var changed = newBody && newBody !== prev.originalText;
  /* Restore DOM: show original body + actions, remove textarea + controls */
  prev.bodyEl.textContent = changed ? newBody : prev.originalText;
  prev.bodyEl.style.display = '';
  prev.controls.remove();
  prev.textarea.remove();
  prev.actionsDiv.style.display = '';
  /* Fire-and-forget API save if content changed */
  if (changed) {
    _commentEditPaths[prev.taskPath] = Date.now();
    fetch(wtUrl('/api/task/' + prev.taskPath + '/comment/' + prev.commentId), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body: newBody })
    });
  }
}

function startEditComment(item, bodyEl, comment, taskPath) {
  /* Single-edit mode: close any already-open editor first */
  _dismissActiveEdit();

  /* Replace body text with an editable textarea + Save/Cancel */
  var originalText = comment.body;
  var actionsDiv = item.querySelector('div:last-child'); /* Edit/Resolve/Delete container */
  actionsDiv.style.display = 'none';

  var ta = document.createElement('textarea');
  ta.value = originalText;
  ta.classList.add('comment-edit-textarea');

  var controls = document.createElement('div');
  controls.classList.add('comment-actions');

  var saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save';
  saveBtn.classList.add('comment-edit-btn');

  var cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.classList.add('comment-edit-btn', 'btn-secondary');

  function saveEdit() {
    _activeCommentEdit = null;
    var newBody = ta.value.trim();
    if (!newBody || newBody === originalText) { cancelEdit(); return; }
    _commentEditPaths[taskPath] = Date.now();
    fetch(wtUrl('/api/task/' + taskPath + '/comment/' + comment.id), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body: newBody })
    }).then(function(resp) {
      if (resp.ok) loadComments(taskPath);
    });
  }

  function cancelEdit() {
    _activeCommentEdit = null;
    bodyEl.textContent = originalText;
    bodyEl.style.display = '';
    controls.remove();
    ta.remove();
    actionsDiv.style.display = '';
  }

  saveBtn.onclick = saveEdit;
  cancelBtn.onclick = cancelEdit;

  ta.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      saveEdit();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEdit();
    }
  });

  controls.appendChild(saveBtn);
  controls.appendChild(cancelBtn);

  bodyEl.style.display = 'none';
  bodyEl.parentNode.insertBefore(ta, bodyEl.nextSibling);
  ta.parentNode.insertBefore(controls, ta.nextSibling);
  ta.focus();
  ta.selectionStart = ta.selectionEnd = ta.value.length;

  _activeCommentEdit = {
    textarea: ta, controls: controls,
    bodyEl: bodyEl, actionsDiv: actionsDiv, originalText: originalText,
    taskPath: taskPath, commentId: comment.id
  };
}

function resolveComment(taskPath, commentId) {
  _commentEditPaths[taskPath] = Date.now();
  fetch(wtUrl('/api/task/' + taskPath + '/comment/' + commentId), { method: 'PATCH' })
    .then(function(resp) { if (resp.ok) loadComments(taskPath); });
}

function deleteComment(taskPath, commentId) {
  _commentEditPaths[taskPath] = Date.now();
  fetch(wtUrl('/api/task/' + taskPath + '/comment/' + commentId), { method: 'DELETE' })
    .then(function(resp) { if (resp.ok) loadComments(taskPath); });
}

/* ── Page load: populate the sidebar, then start the hash router ──
   The nav rows must exist before initRouter's first setActive so the active
   highlight lands on a real row (deep hashes still lazy-load their ancestors
   inside updateSidebar). Sidebar load is awaited but best-effort. */
document.addEventListener('DOMContentLoaded', async function() {
  initReproReader();
  initSidebarChrome();    /* pin/resize/drawer chrome — pure presentation */
  initSidebarEvents();
  initTreeKeyboard();      /* roving-tabindex keyboard nav on #nav-tree */
  await loadNavTree();
  initRouter();
  initWorkspaceControls();
  updateTreeCommentBadges();
});
