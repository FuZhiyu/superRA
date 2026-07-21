/* ══════════════════════════════════════════════════════════════════════════
   STANDALONE MODE — server-less single-file export.
   ──────────────────────────────────────────────────────────────────────────
   The live dashboard fetches HTML/JSON fragments from the FastAPI server
   (/nav, /nav/<path>, /node/<path>, /api/children-graph?root=<path>, /kanban,
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
     /kanban, /nav/<path>) return their pre-rendered HTML/JSON. The map is
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
function resolveInternalTaskPath(href, taskPath) {
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
    segs = (taskPath ? taskPath.split('/') : []).concat(clean.split('/'));
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
 * - Scheme URIs (zotero:, mailto:, http(s):, …) -> left untouched
 * - Relative .pdf links -> /files/ (server) or STANDALONE_PLAN_DIR (standalone)
 * - Other relative file paths -> vscode://file/{resolved_root}/{task-rel path}
 * - Image src -> /files/{src}
 * - Wrap each block-level element in a .commentable-block container
 *   with data-section and data-block attributes (when sectionName given)
 */
function renderMarkdown(text, sectionName, taskPath) {
  /* markdown-it runs with html:true so agent-authored HTML (layouts, diagrams,
     callouts) survives. Exports are published, so every render result is
     untrusted reader input — sanitize before it touches the DOM. DOMPurify's
     default allowlist strips scripts/iframes/event handlers/javascript: URLs;
     ADD_ATTR keeps class/style so authored HTML can use inline styles and the
     dashboard CSS tokens. <details>/<summary> are on the default allowlist.
     ALLOWED_URI_REGEXP is DOMPurify's default scheme list plus `zotero` (the
     trace-link deeplink), so authored Zotero links survive sanitization while
     javascript: and untrusted data: links remain blocked. */
  var html = DOMPurify.sanitize(md.render(text), {
    ADD_ATTR: ['style', 'class'],
    ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|matrix|zotero):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  });
  var container = document.createElement('div');
  container.innerHTML = html;

  /* Base directory for resolving relative paths within a task, derived from the
     resolved task root (any --root, not just `superRA`). Two bases:
     - taskDirRel: the task's dir relative to the resolved root (`taskPath/`),
       prepended to RESOLVED_ROOT (absolute) for the local vscode://file link.
     - repoPathPrefix: the same path prefixed with the root's repo-relative name
       (ROOT_PREFIX), passed to repoFileHref for the GitHub branch. */
  var taskDirRel = taskPath ? taskPath + '/' : '';
  var rootRel = ROOT_PREFIX ? ROOT_PREFIX + '/' : '';
  var repoPathPrefix = rootRel + taskDirRel;
  /* The GitHub-branch prefix uses the repo-root-relative root path (so a tree
     below the repo root keeps its `docs/...` prefix); /files/ and vscode keep
     ROOT_PREFIX / RESOLVED_ROOT. */
  var repoRootRel = REPO_ROOT_PREFIX ? REPO_ROOT_PREFIX + '/' : '';
  var repoLinkPrefix = repoRootRel + taskDirRel;

  /* Rewrite relative links. A relative href that resolves to a real task in
     this tree becomes an internal hash link (#/<task-path>) so it focuses that
     card via the existing hashchange/setActive router; everything else (scripts,
     figures, paths outside the tree) keeps the vscode://file rewrite. */
  container.querySelectorAll('a[href]').forEach(function(a) {
    var href = a.getAttribute('href');
    /* Only genuine relative paths enter the task/file resolver. Scheme URIs
       (including zotero:, mailto:, vscode:, and file:) remain untouched. */
    if (href && !href.startsWith('#') && !/^[a-z][a-z0-9+.\-]*:/i.test(href)) {
      var internal = resolveInternalTaskPath(href, taskPath);
      if (internal !== null) {
        a.setAttribute('href', '#/' + internal);
        a.removeAttribute('target');
        a.classList.add('task-link');
      } else if (/\.pdf$/i.test(href.replace(/[?#].*$/, '')) && !window.DOC_MODE && !REPO_FILE_BASE) {
        /* PDFs are browser-viewable artifacts: route them through the live file
           server, or resolve beside the embedded task tree in standalone mode. */
        if (window.STANDALONE) {
          a.setAttribute('href', STANDALONE_PLAN_DIR + taskDirRel + href);
        } else {
          a.setAttribute('href', '/files/' + repoPathPrefix + href);
        }
        a.setAttribute('target', '_blank');
      } else {
        /* Genuine file link. GitHub artifact exports keep GitHub-style anchors;
           local/editor links translate those anchors to VS Code's path:line[:col]
           form because vscode://file ignores a #L... fragment. */
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
          var filePath = taskDirRel + href;
          var loc = '';
          var lm = filePath.match(/#L(\d+)(?:C(\d+))?(?:-L?\d+(?:C\d+)?)?$/);
          if (lm) {
            loc = ':' + lm[1] + (lm[2] ? ':' + lm[2] : '');
            filePath = filePath.slice(0, lm.index);
          }
          a.setAttribute('href', 'vscode://file/' + RESOLVED_ROOT + '/' + filePath + loc);
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
    if (src && !src.startsWith('http://') && !src.startsWith('https://') && !src.startsWith('/')) {
      if (window.STANDALONE) {
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
        img.setAttribute('src', '/files/' + repoPathPrefix + src);
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

/* ── View switching ── Workspace (master-detail drill-down) vs Kanban board ── */
var currentView = 'workspace';

function showView(view) {
  currentView = view;
  document.querySelectorAll('.header-controls .hc-btn').forEach(function(b) {
    b.classList.remove('active');
  });
  document.getElementById('btn-' + view).classList.add('active');
  document.getElementById('workspace').classList.toggle('hidden', view !== 'workspace');
  document.getElementById('view-kanban').classList.toggle('hidden', view !== 'kanban');
  if (view === 'kanban') renderKanbanView();
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
  var scored = [];
  for (var i = 0; i < SEARCH_INDEX.length; i++) {
    var s = scoreSearchRecord(SEARCH_INDEX[i], q);
    if (s > 0) scored.push({ rec: SEARCH_INDEX[i], score: s });
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
    var pathLabel = rec.path || 'root';
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
  setActive(rec.path || '');
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

function applyFiltersNow() {
  var status = document.getElementById('filter-status').value;
  var search = document.getElementById('search-box').value.toLowerCase();
  var active = !!status || !!search;

  if (active && preFilterFoldState === null) {
    preFilterFoldState = snapshotNavFolds();  /* entering filter mode */
  }

  document.querySelectorAll('#nav-tree > .task-node').forEach(function(el) {
    applyFiltersToNode(el, status, search);
  });

  if (active) {
    /* Matching rows live behind collapsed ancestors (the whole sidebar is
       folded by default), so `.hidden` removal alone leaves them invisible.
       Expand the ancestor chain of every still-visible match so matches are
       actually revealed. Scoped to rows already in the DOM — deep, not-yet
       lazy-loaded branches are intentionally not eagerly loaded to search. */
    revealFilterMatches(status, search);
  } else if (preFilterFoldState !== null) {
    restoreNavFolds(preFilterFoldState);  /* leaving filter mode */
    preFilterFoldState = null;
  }

  /* Visibility of rows changed -> keep exactly one row tab-focusable. */
  refreshRovingTabindex();
}

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
function onKanbanCardClick(event) {
  var card = event.target.closest('.kanban-card');
  if (card && card.dataset.path !== undefined) revealTask(card.dataset.path);
}

async function renderKanbanView() {
  var container = document.getElementById('view-kanban');
  container.onclick = onKanbanCardClick;
  try {
    var resp = await fetch(wtUrl('/kanban'));
    if (resp.ok) {
      container.innerHTML = await resp.text();
    } else {
      container.innerHTML = '<p style="color:var(--text-mute)">Could not load kanban view.</p>';
    }
  } catch(e) {
    container.innerHTML = '<p style="color:var(--st-rev-t)">Kanban render error: ' + e.message + '</p>';
  }
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

var activePath = '';        /* '' = root */
var restoring = false;      /* true while applying a load/popstate hash — suppress pushState */
var _moveFocusOnLoad = false; /* set per user-nav so loadActiveNode lands focus on the new heading */
/* The in-flight (or last-settled) updateSidebar() promise from the current
   setActive() call — a completion hook that patchCardBadgeWhenReady awaits
   instead of polling for the sidebar row to land. */
var _lastSidebarUpdate = Promise.resolve();

/* A path -> display-title lookup. sidebar-nav populates this from /nav; until
   then the breadcrumb falls back to the path slug. */
var pathTitles = {};

/* Read location.hash as `#/<task/path>` -> the path verbatim ('' for root). */
function parseHash() {
  var h = location.hash || '';
  if (h.charAt(0) === '#') h = h.slice(1);   /* strip leading # */
  if (h.charAt(0) === '/') h = h.slice(1);   /* strip leading / */
  return h;
}

/* The one navigation entry point. Sets activePath, writes history (unless
   restoring), then refreshes every derived region. */
function setActive(path) {
  path = path || '';
  activePath = path;

  if (!restoring) {
    var hash = '#/' + path;
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
  if (currentView !== 'workspace') showView('workspace');

  updateBreadcrumb(path);
  _lastSidebarUpdate = updateSidebar(path);
  loadActiveNode(path);
  loadChildrenDag(path);

  /* Chrome: a selection means "done navigating" — auto-hide the unpinned
     overlay and close the narrow-screen drawer. Defined in the sidebar-chrome
     module below; guard so the router still works if it ever loads first. */
  if (typeof onNavigationChrome === 'function') onNavigationChrome();
}

/* Rebuild the breadcrumb from the active path: root › seg › … › active.
   Each non-active crumb is a button that ascends by setting that ancestor
   active; the active crumb is inert. */
function updateBreadcrumb(path) {
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
  addCrumb(rootLabel, '', segs.length === 0);

  var accumulated = '';
  for (var i = 0; i < segs.length; i++) {
    accumulated = i === 0 ? segs[i] : accumulated + '/' + segs[i];
    addSep();
    /* Prefer the real title once the sidebar supplies it; fall back to slug. */
    var label = pathTitles[accumulated] || segs[i];
    addCrumb(label, accumulated, i === segs.length - 1);
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
/* VS Code wordmark, inline so it inherits the button's currentColor (mid-grey
   at rest, VS Code blue on hover). */
var VSCODE_ICON =
  '<svg viewBox="0 0 24 24" aria-hidden="true">'
  + '<path fill="currentColor" d="M23.15 2.587 18.21.21a1.494 1.494 0 0 0-1.705.29'
  + 'l-9.46 8.63-4.12-3.128a.999.999 0 0 0-1.276.057L.327 7.261A1 1 0 0 0 .326 8.74'
  + 'L3.899 12 .326 15.26a1 1 0 0 0 .001 1.479L1.65 17.94a.999.999 0 0 0 1.276.057'
  + 'l4.12-3.128 9.46 8.63a1.492 1.492 0 0 0 1.704.29l4.942-2.377A1.5 1.5 0 0 0 24 20.06'
  + 'V3.939a1.5 1.5 0 0 0-.85-1.352zm-5.146 14.861L10.826 12l7.178-5.448z"/></svg>';

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
    var status = navRowStatus(path);
    var fileButtonTitle = REPO_FILE_BASE ? 'Open task.md on GitHub' : 'Open task.md in VS Code';
    var fileButtonLabel = REPO_FILE_BASE ? 'GitHub' : 'VS Code';

    region.innerHTML =
      '<header class="active-node-head">'
      + '<h2 class="active-node-title" tabindex="-1"></h2>'
      + ((status && !window.DOC_MODE) ? '<span class="badge badge-' + status + '">' + status + '</span>' : '')
      /* Open this task's task.md in the configured file target. */
      + '<a class="vscode-btn" target="_blank" title="' + fileButtonTitle + '">'
      + VSCODE_ICON + '<span>' + fileButtonLabel + '</span></a>'
      /* Share/Export: download this node's subtree as a standalone HTML file.
         Server-backed (/export), so it is omitted in standalone mode — a
         downloaded file has no server to re-export from. */
      + (window.STANDALONE ? '' :
         '<button class="share-btn" type="button" title="Download this subtree as a standalone HTML file">Share</button>')
      + '</header>'
      /* Wrap the body in a real .task-node so the comment/section helpers,
         which all resolve via `.task-node[data-path]`, find their context. */
      + '<div class="task-node active-node-body" data-path="' + path + '">' + body + '</div>';

    /* Set the title via textContent (avoids HTML injection from titles). In
       doc-mode the slug is task anatomy — show the title alone. */
    var titleEl = region.querySelector('.active-node-title');
    if (titleEl) titleEl.textContent = (slug && !window.DOC_MODE) ? (slug + ' · ' + title) : title;

    /* Point the VS Code button at this task's task.md. Set the href as a
       property (not an attribute string) so the path needs no escaping. */
    var vsBtn = region.querySelector('.vscode-btn');
    if (vsBtn) vsBtn.href = taskFileVscodeHref(path);

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
  } catch (e) {
    if (token !== loadActiveNode._token) return;
    region.innerHTML = '<p style="color:var(--st-rev-t)">Load error: ' + e.message + '</p>';
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
      return rootKids.length ? buildChildGrid(rootKids) : '';
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
    return info.hasEdges
      ? buildChildFlow(info.children, info.edges)
      : buildChildGrid(info.children);
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
    applyWorktree(urlWt, parseHash());
    return;
  }
  restoring = true;
  setActive(parseHash());
  restoring = false;
});

/* hashchange (manual address-bar hash edit): navigate to the new hash without
   writing new history. setActive's own pushState mutates location.hash and
   re-fires this event, so no-op when the hash already matches activePath;
   otherwise apply it in restoring mode (no extra pushState/history entry). */
window.addEventListener('hashchange', function() {
  if (parseHash() === activePath) return;
  restoring = true;
  setActive(parseHash());
  restoring = false;
});

/* Resolve the initial hash on load (default the root), normalize it with
   replaceState so reload/back land cleanly, then activate it. */
function initRouter() {
  var path = parseHash();
  restoring = true;
  history.replaceState({ path: path, wt: ACTIVE_WT }, '', '#/' + path);
  setActive(path);
  restoring = false;
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
    indexNavTitles(container);
    applyTreeAria();   /* tree roles + roving tabindex on the freshly-injected rows */
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
  refreshRovingTabindex();
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
    indexNavTitles(children);
    applyTreeAria();   /* tree roles + roving tabindex on the newly-loaded rows */
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
  await expandNavNode(target);

  var row = target.querySelector(':scope > .task-row');
  if (row) {
    row.classList.add('nav-active');
    row.setAttribute('aria-selected', 'true');
    /* Roving tabindex follows the active row so a subsequent Tab into the tree
       lands on it. (applyTreeAria also keeps roles current after any lazy load
       the ancestor walk just triggered.) */
    applyTreeAria();
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
var SB_WIDTH_MIN = 200, SB_WIDTH_MAX = 480, SB_WIDTH_DEFAULT = 280;
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
  var ws = workspaceEl();
  if (ws) ws.style.setProperty('--sidebar-width', w + 'px');
  var rz = document.getElementById('sidebar-resizer');
  if (rz) rz.setAttribute('aria-valuenow', String(w));
}

function clampSidebarWidth(w) {
  if (isNaN(w)) return SB_WIDTH_DEFAULT;
  return Math.max(SB_WIDTH_MIN, Math.min(SB_WIDTH_MAX, Math.round(w)));
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
    if (!isNaN(savedW)) sbWidth = clampSidebarWidth(savedW);
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
    /* Width = cursor X relative to the workspace's left edge. */
    var rect = ws.getBoundingClientRect();
    applySidebarWidth(clampSidebarWidth(ev.clientX - rect.left));
  }
  function onUp() {
    if (!dragging) return;
    dragging = false;
    ws.classList.remove('sb-resizing');
    document.body.classList.remove('sb-resizing-active');
    window.removeEventListener('pointermove', onMove);
    window.removeEventListener('pointerup', onUp);
    persistSidebarWidth();
  }
  rz.addEventListener('pointerdown', function(ev) {
    /* Drag only makes sense for a fine pointer with the sidebar laid out
       (not drawer mode, not touch — the resizer is hidden there anyway). */
    if (sbIsNarrow() || sbIsTouch()) return;
    ev.preventDefault();
    dragging = true;
    ws.classList.add('sb-resizing');
    document.body.classList.add('sb-resizing-active');
    /* Unpinned + drag: keep the sidebar revealed so the user sees the resize. */
    revealSidebar();
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
  });

  /* Keyboard: ←/← nudge by 16px, Home/End jump to clamp bounds. */
  rz.addEventListener('keydown', function(ev) {
    var step = ev.shiftKey ? 48 : 16;
    var next = null;
    if (ev.key === 'ArrowLeft')       next = sbWidth - step;
    else if (ev.key === 'ArrowRight') next = sbWidth + step;
    else if (ev.key === 'Home')       next = SB_WIDTH_MIN;
    else if (ev.key === 'End')        next = SB_WIDTH_MAX;
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
  closeSearchSheet();
}

/* ── Phone search/filter sheet ────────────────────────────────────────────
   On phone the inline #search-box + #filter-status are hidden; the sheet adopts
   them (so search/filter logic is reused unchanged), shows them at a tappable
   size, and returns them to the header on close. Backdrop + Esc + focus trap
   mirror the drawer. The sheet closes on a status selection (a "done filtering"
   signal); free-text search keeps it open so typing isn't interrupted. */
var _searchSheetLastFocus = null;

function toggleSearchSheet() {
  var sheet = document.getElementById('search-sheet');
  if (sheet && sheet.classList.contains('open')) closeSearchSheet();
  else openSearchSheet();
}

function openSearchSheet() {
  var sheet = document.getElementById('search-sheet');
  var backdrop = document.getElementById('search-sheet-backdrop');
  var body = document.getElementById('search-sheet-body');
  var host = document.getElementById('search-host');
  var trigger = document.getElementById('search-trigger');
  if (!sheet || !backdrop || !body || !host) return;
  if (sheet.classList.contains('open')) return;
  _searchSheetLastFocus = document.activeElement;
  body.appendChild(host);              /* adopt the live search/filter elements */
  backdrop.classList.add('open');
  sheet.classList.add('open');
  if (trigger) trigger.setAttribute('aria-expanded', 'true');
  var search = document.getElementById('search-box');
  if (search) search.focus();
  document.addEventListener('keydown', searchSheetKeydown, true);
}

function closeSearchSheet() {
  var sheet = document.getElementById('search-sheet');
  if (!sheet || !sheet.classList.contains('open')) return;
  var backdrop = document.getElementById('search-sheet-backdrop');
  var host = document.getElementById('search-host');
  var controls = document.querySelector('.header-controls');
  var trigger = document.getElementById('search-trigger');
  sheet.classList.remove('open');
  if (backdrop) backdrop.classList.remove('open');
  /* Return the search/filter host to the header (just after the trigger button)
     so it is inline again when the viewport widens. */
  if (host && controls && trigger) controls.insertBefore(host, trigger.nextSibling);
  else if (host && controls) controls.appendChild(host);
  if (trigger) trigger.setAttribute('aria-expanded', 'false');
  document.removeEventListener('keydown', searchSheetKeydown, true);
  if (_searchSheetLastFocus && document.contains(_searchSheetLastFocus)) _searchSheetLastFocus.focus();
  else if (trigger) trigger.focus();
  _searchSheetLastFocus = null;
}

/* Focusable controls inside the open sheet, for the focus trap. */
function searchSheetFocusables() {
  var sheet = document.getElementById('search-sheet');
  if (!sheet) return [];
  return Array.prototype.filter.call(
    sheet.querySelectorAll('button, input, select, [href], [tabindex]:not([tabindex="-1"])'),
    function(el) { return el.offsetParent !== null || el === document.activeElement; }
  );
}

/* Esc closes; Tab/Shift+Tab cycle within the sheet (focus trap). */
function searchSheetKeydown(ev) {
  var sheet = document.getElementById('search-sheet');
  if (!sheet || !sheet.classList.contains('open')) return;
  if (ev.key === 'Escape') { ev.preventDefault(); closeSearchSheet(); return; }
  if (ev.key !== 'Tab') return;
  var f = searchSheetFocusables();
  if (f.length === 0) return;
  var first = f[0], last = f[f.length - 1];
  if (ev.shiftKey && document.activeElement === first) {
    ev.preventDefault(); last.focus();
  } else if (!ev.shiftKey && document.activeElement === last) {
    ev.preventDefault(); first.focus();
  }
}

/* Close the sheet when the user commits a status filter (a "done filtering"
   signal). Wired as a separate listener so applyFilters / the inline onchange
   stay unchanged; free-text typing in the search box leaves the sheet open.
   Also close it when the viewport widens past the 620px phone breakpoint while
   open (e.g. an iPhone rotated to landscape): the inline search returns to the
   header instead of stranding the adopted host inside the bottom sheet —
   mirrors the drawer's resize-up drop. */
function initSearchSheet() {
  var filter = document.getElementById('filter-status');
  if (filter) {
    filter.addEventListener('change', function() {
      var sheet = document.getElementById('search-sheet');
      if (sheet && sheet.classList.contains('open')) closeSearchSheet();
    });
  }
  var phoneMQ = window.matchMedia
    ? window.matchMedia('(max-width: 620px)') : null;
  if (phoneMQ) {
    /* Fires when crossing 620px in either direction; act only on widening out
       of phone width (no longer matches) while the sheet is open. */
    var onPhoneChange = function() {
      if (phoneMQ.matches) return;
      var sheet = document.getElementById('search-sheet');
      if (sheet && sheet.classList.contains('open')) closeSearchSheet();
    };
    if (phoneMQ.addEventListener) phoneMQ.addEventListener('change', onPhoneChange);
    else if (phoneMQ.addListener) phoneMQ.addListener(onPhoneChange);  /* older Safari */
  }
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
  var rows = root.querySelectorAll('.task-row');
  rows.forEach(function(r) { r.setAttribute('tabindex', '-1'); });
  var active = root.querySelector('.task-row.nav-active');
  var target = (active && isRowVisible(active)) ? active : firstVisibleRow();
  if (target) target.setAttribute('tabindex', '0');
}

/* Visible = the row's node and all ancestor groups are displayed (not folded,
   not filtered out). */
function isRowVisible(row) {
  var el = row;
  while (el && el.id !== 'nav-tree') {
    if (el.nodeType === 1) {
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
  var rows = root.querySelectorAll('.task-row');
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
    root.querySelectorAll('.task-row'), isRowVisible);
}

/* Move roving focus to a row: make it the only tabbable row and focus it. */
function focusRow(row) {
  if (!row) return;
  var root = document.getElementById('nav-tree');
  if (root) root.querySelectorAll('.task-row').forEach(function(r) {
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
    var row = ev.target.closest ? ev.target.closest('.task-row') : null;
    if (!row || !root.contains(row)) return;
    var node = row.closest('.task-node');
    var toggle = row.querySelector(':scope > .task-toggle');
    var isParent = toggle && !toggle.classList.contains('leaf');
    var expanded = isParent && toggle.classList.contains('expanded');
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
        if (isParent && !expanded) {
          /* Expand (may lazy-load); focus stays on the row. */
          toggleNavCaret(node).then(function() {
            applyTreeAria();
          });
        } else if (isParent && expanded) {
          /* Already open: move into the first visible child. */
          var after = visibleRows();
          var ai = after.indexOf(row);
          if (ai >= 0 && ai < after.length - 1) focusRow(after[ai + 1]);
        }
        break;
      case 'ArrowLeft':
        ev.preventDefault();
        if (isParent && expanded) {
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
        ev.preventDefault();
        if (node && node.dataset.path !== undefined) setActive(node.dataset.path);
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
  if (path === activePath) {
    loadActiveNode(path);
    /* Run after htmx's outerHTML row swap detaches the current row, so the
       highlight lands on the freshly-swapped (unhighlighted) replacement row.
       Track the promise too, so a patchCardBadgeWhenReady queued by the
       loadActiveNode() call just above awaits this update, not a stale one. */
    setTimeout(function() { if (path === activePath) _lastSidebarUpdate = updateSidebar(path); }, 0);
  }
  /* Re-harvest pathTitles from the freshly-swapped row (deferred past the
     swap, same as the highlight re-assert above) so a title edit propagates
     to the breadcrumb and — for a changed sibling card — the children panel,
     without a structural full-reload. */
  setTimeout(function() {
    indexNavTitles();
    updateBreadcrumb(activePath);
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
  var wanted = activePath;
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
  var target = resolveSurvivingPath(wanted);
  restoring = true;
  if (target !== wanted) {
    /* Relative '#/...' preserves the ?wt= in location.search. */
    history.replaceState({ path: target, wt: ACTIVE_WT }, '', '#/' + target);
  }
  setActive(target);
  restoring = false;
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
    var label = wt.branch || wt.path.split('/').pop();
    if (wt.plan_title) label += ' — ' + wt.plan_title;
    if (wt.is_agent) label = '[agent] ' + label;
    opt.textContent = label;
    if (wt.is_agent) opt.style.opacity = '0.6';
    if ((wt.wt_id || '') === activeId) opt.selected = true;
    select.appendChild(opt);
  });

  selector.style.display = 'flex';
}

/* Point the header "open worktree" button at the active worktree's checkout root
   (PROJECT_ROOT, re-pointed per ?wt= in fetchWorktrees), so subsequent per-task
   clicks land in that now-focused window. Hidden in GitHub-file mode, which has
   no local folder to open; doc-mode hides it via the shared .vscode-btn rule and
   standalone omits it from the template. Idempotent: safe to call repeatedly. */
function updateWorktreeOpenHref() {
  var btn = document.getElementById('worktree-open-btn');
  if (!btn) return;
  if (REPO_FILE_BASE) { btn.style.display = 'none'; return; }
  if (!btn.innerHTML) btn.innerHTML = VSCODE_ICON + '<span>Worktree</span>';
  btn.href = vscodeFileUri(PROJECT_ROOT);
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
      data.worktrees.forEach(function(wt) {
        _wtProjectRoots[wt.wt_id || ''] = wt.path;
        _wtResolvedRoots[wt.wt_id || ''] = wt.plan_root || '';
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
  history.pushState({ path: parseHash(), wt: token }, '', location.pathname + search + hash);
  applyWorktree(token, parseHash());
}

/* Re-point the whole tab at worktree *wtId* (the ?wt= token) without a full page
   reload: update ACTIVE_WT, reconnect the live-reload stream to the new
   worktree, refresh PROJECT_ROOT + the selector, then rebuild the sidebar and
   re-render the panels for *path* (or its nearest surviving ancestor). Used by
   the selector and by back/forward across a ?wt= boundary. */
async function applyWorktree(wtId, path) {
  ACTIVE_WT = wtId || '';
  /* Children panels are per-worktree data — a cache entry from the worktree
     being left must not leak into the newly active one. */
  _childrenDagCache = {};
  reconnectSse();
  await loadNavTree();
  await refreshSearchIndex();
  await fetchWorktrees();
  var target = resolveSurvivingPath(path || '');
  restoring = true;
  if (target !== (path || '')) {
    history.replaceState({ path: target, wt: ACTIVE_WT }, '', location.pathname + location.search + '#/' + target);
  }
  setActive(target);
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
  initSidebarChrome();    /* pin/resize/drawer chrome — pure presentation */
  initSidebarEvents();
  initSearchSheet();       /* phone search/filter sheet close-on-selection wiring */
  initTreeKeyboard();      /* roving-tabindex keyboard nav on #nav-tree */
  await loadNavTree();
  initRouter();
  updateTreeCommentBadges();
});
