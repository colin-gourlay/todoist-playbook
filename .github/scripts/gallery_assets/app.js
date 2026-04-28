/* Todoist Playbook — Gallery app
 *
 * Loads template data from the in-page JSON island, renders home/category/
 * search views, hash-based routing for deep links, and an accessible modal
 * with focus trap, inert background, and chained-modal focus stack.
 */
(function () {
  'use strict';

  // ── Data island load ──────────────────────────────────────────────────────
  var dataNode = document.getElementById('tp-data');
  var DATA;
  try {
    DATA = JSON.parse(dataNode.textContent);
  } catch (e) {
    console.error('Failed to parse template data:', e);
    DATA = { templates: [], categoryMeta: {}, spotlight: null, build: {} };
  }
  var TEMPLATES      = DATA.templates || [];
  var CATEGORY_META  = DATA.categoryMeta || {};
  var SPOTLIGHT      = DATA.spotlight || null;
  var BUILD          = DATA.build || {};
  var REPO_URL       = DATA.repoUrl || 'https://github.com/colin-gourlay/todoist-playbook';

  var TEMPLATE_LOOKUP = {};
  TEMPLATES.forEach(function (t) { TEMPLATE_LOOKUP[t.type + ':' + t.slug] = t; });

  var SEARCH_INDEX = TEMPLATES.map(function (t) {
    return {
      template: t,
      name: (t.name || '').toLowerCase(),
      description: (t.description || '').toLowerCase(),
      category: (t.category || '').toLowerCase(),
      tags: (t.tags || []).map(function (x) { return x.toLowerCase(); })
    };
  });

  // ── Helpers ───────────────────────────────────────────────────────────────
  function esc(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function catIcon(slug)  { return CATEGORY_META[slug] ? CATEGORY_META[slug][0] : '📁'; }
  function catLabel(slug) {
    if (CATEGORY_META[slug]) return CATEGORY_META[slug][1];
    return slug.replace(/-/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  /* Stable hash → HSL accent for category icon backgrounds. */
  function catAccent(slug) {
    var h = 0;
    for (var i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0;
    var hue = h % 360;
    return 'hsl(' + hue + ', 70%, 92%)';
  }

  function groupByCategory(templates) {
    var map = {};
    templates.forEach(function (t) {
      var c = t.category || 'uncategorised';
      if (!map[c]) map[c] = [];
      map[c].push(t);
    });
    return map;
  }

  function formatDuration(d) {
    if (!d) return '';
    return d.replace(/m$/, '\u202fmin').replace(/h$/, '\u202fhr');
  }

  // ── Inline SVG icons (lucide-style) ───────────────────────────────────────
  var ICONS = {
    search:   '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/></svg>',
    close:    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    download: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>',
    arrow:    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>',
    back:     '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>',
    github:   '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor" stroke="none"><path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.11.82-.26.82-.58v-2c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.74.08-.74 1.21.09 1.85 1.24 1.85 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.66-.3-5.46-1.33-5.46-5.93 0-1.31.47-2.39 1.24-3.23-.13-.3-.54-1.52.11-3.17 0 0 1.01-.33 3.31 1.23a11.5 11.5 0 0 1 6.02 0c2.3-1.56 3.31-1.23 3.31-1.23.66 1.65.25 2.87.12 3.17.77.84 1.24 1.92 1.24 3.23 0 4.61-2.81 5.62-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.21.7.83.58A12 12 0 0 0 12 .5z"/></svg>',
    sun:      '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    moon:     '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    auto:     '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3v18"/><path d="M12 3a9 9 0 0 1 0 18"/></svg>',
    external: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><path d="M15 3h6v6"/><path d="M10 14L21 3"/></svg>'
  };

  // ── Theme management ─────────────────────────────────────────────────────
  var THEME_KEY = 'tp-theme';
  function readTheme() {
    try { return localStorage.getItem(THEME_KEY) || 'system'; } catch (e) { return 'system'; }
  }
  function writeTheme(v) {
    try { localStorage.setItem(THEME_KEY, v); } catch (e) { /* ignore */ }
  }
  function applyTheme(mode) {
    var root = document.documentElement;
    if (mode === 'system') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', mode);
    }
    var darkActive =
      mode === 'dark' ||
      (mode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', darkActive ? '#1c2128' : '#d34244');
  }
  function cycleTheme(cur) {
    return cur === 'system' ? 'light' : cur === 'light' ? 'dark' : 'system';
  }
  function themeIcon(mode) {
    return mode === 'dark' ? ICONS.moon : mode === 'light' ? ICONS.sun : ICONS.auto;
  }
  function themeLabel(mode) {
    return mode === 'dark' ? 'Dark theme' : mode === 'light' ? 'Light theme' : 'System theme';
  }

  function setupThemeToggle() {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    var mode = readTheme();
    applyTheme(mode);
    btn.innerHTML = themeIcon(mode);
    btn.setAttribute('aria-label', themeLabel(mode));
    btn.setAttribute('aria-pressed', mode === 'dark' ? 'true' : 'false');
    btn.addEventListener('click', function () {
      var next = cycleTheme(readTheme());
      writeTheme(next);
      applyTheme(next);
      btn.innerHTML = themeIcon(next);
      btn.setAttribute('aria-label', themeLabel(next));
      btn.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
    });
    // Update theme-color when system preference changes (only meaningful in 'system')
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) mq.addEventListener('change', function () {
      if (readTheme() === 'system') applyTheme('system');
    });
  }

  // ── Markdown rendering (sanitised) ───────────────────────────────────────
  function sanitiseMarkdown(md) {
    if (!md) return '';
    var raw;
    if (typeof window.marked !== 'undefined' && window.marked.parse) {
      try {
        raw = window.marked.parse(md, { mangle: false, headerIds: false, breaks: false });
      } catch (e) {
        return '<pre>' + esc(md) + '</pre>';
      }
    } else {
      return '<pre>' + esc(md) + '</pre>';
    }
    if (typeof window.DOMPurify !== 'undefined' && window.DOMPurify.sanitize) {
      try {
        return window.DOMPurify.sanitize(raw, {
          USE_PROFILES: { html: true },
          ADD_ATTR: ['target', 'rel']
        });
      } catch (e) {
        return '<pre>' + esc(md) + '</pre>';
      }
    }
    return raw;
  }

  // Add DOMPurify hook for safe external links once available
  if (typeof window.DOMPurify !== 'undefined' && window.DOMPurify.addHook) {
    window.DOMPurify.addHook('afterSanitizeAttributes', function (node) {
      if (node.tagName === 'A' && node.getAttribute('href')) {
        var href = node.getAttribute('href');
        if (/^https?:|^mailto:/i.test(href)) {
          node.setAttribute('rel', 'noopener noreferrer');
          node.setAttribute('target', '_blank');
        }
      }
    });
  }

  // ── Builders ──────────────────────────────────────────────────────────────
  function buildPreview(rows) {
    var MAX = 7;
    var shown = rows.slice(0, MAX);
    var rest = rows.length - shown.length;
    var html = '';
    shown.forEach(function (r) {
      var cls = r.type === 'section' ? 'section' : 'task';
      var content = r.content.replace(/@[\w-]+/g, '').trim();
      html += '<div class="preview-row ' + cls + '">' + esc(content) + '</div>';
    });
    if (rest > 0) html += '<div class="preview-more">+\u202f' + rest + ' more</div>';
    return html;
  }

  function buildStats(t) {
    var stats = [];
    if (t.task_count)
      stats.push('<span>\u2714\ufe0f ' + t.task_count + '\u202ftask' + (t.task_count !== 1 ? 's' : '') + '</span>');
    if (t.section_count)
      stats.push('<span>\u25b8 ' + t.section_count + '\u202fsection' + (t.section_count !== 1 ? 's' : '') + '</span>');
    if (t.estimated_duration)
      stats.push('<span>\u23f1\ufe0f ' + esc(formatDuration(t.estimated_duration)) + '</span>');
    if (t.recurrence_suggestion)
      stats.push('<span>\u{1F501} ' + esc(t.recurrence_suggestion) + '</span>');
    if (!stats.length) return '';
    var sep = '<span class="sep" aria-hidden="true">·</span>';
    return stats.join(sep);
  }

  function buildSpotlight(t) {
    if (!t) return '';
    var tags = (t.tags || []).map(function (tag) {
      return '<span class="tag">' + esc(tag) + '</span>';
    }).join('');
    var stats = buildStats(t);
    var metaLine = [
      t.author  ? 'by ' + esc(t.author)  : '',
      t.version ? 'v' + esc(t.version) : ''
    ].filter(Boolean).join(' \u00b7 ');
    var previewHtml = (t.rows && t.rows.length)
      ? '<div class="spotlight-preview">' + buildPreview(t.rows) + '</div>'
      : '';
    var actionBtn = t.csv_url
      ? '<a class="btn-primary" href="' + esc(t.csv_url) + '" download ' +
        'aria-label="Download CSV for ' + esc(t.name) + '" ' +
        'data-stop>' + ICONS.download + '<span>Download CSV</span></a>'
      : '';
    return '' +
      '<div class="spotlight-section">' +
        '<div class="spotlight-heading"><span aria-hidden="true">⭐</span> Template Spotlight</div>' +
        '<button type="button" class="spotlight-card tpl-card-clickable" ' +
          'data-slug="' + esc(t.slug) + '" data-type="' + esc(t.type || 'template') + '" ' +
          'aria-label="Open details for ' + esc(t.name) + '">' +
          '<div class="spotlight-body">' +
            '<span class="spotlight-badge">Featured Template</span>' +
            '<h2 class="spotlight-name">' + esc(t.name) + '</h2>' +
            (t.description ? '<p class="spotlight-desc">' + esc(t.description) + '</p>' : '') +
            (tags ? '<div class="spotlight-tags">' + tags + '</div>' : '') +
            (stats ? '<div class="spotlight-stats">' + stats + '</div>' : '') +
            '<div class="spotlight-footer">' + actionBtn +
              '<span class="spotlight-meta">' + metaLine + '</span>' +
            '</div>' +
          '</div>' +
          previewHtml +
        '</button>' +
      '</div>';
  }

  function buildTemplateCard(t) {
    var tags = (t.tags || []).map(function (tag) {
      return '<span class="tag">' + esc(tag) + '</span>';
    }).join('');
    var stats = buildStats(t);
    var metaLine = [
      t.author  ? 'by ' + esc(t.author)  : '',
      t.version ? 'v' + esc(t.version) : ''
    ].filter(Boolean).join(' \u00b7 ');
    var previewHtml = '';
    if (t.type === 'template' && t.rows && t.rows.length) {
      previewHtml = '<div class="tpl-preview">' + buildPreview(t.rows) + '</div>';
    } else if (t.type === 'prompt' && t.inputs && t.inputs.length) {
      var chips = t.inputs.map(function (i) {
        return '<span class="input-chip">' + esc(i) + '</span>';
      }).join('');
      previewHtml = '<div class="tpl-inputs">' +
        '<div class="tpl-inputs-label">Inputs</div>' + chips + '</div>';
    }
    var actionBlock = '';
    if (t.type === 'template' && t.csv_url) {
      actionBlock = '<div class="btn-action-block">' +
        '<a class="btn-primary" href="' + esc(t.csv_url) + '" download ' +
        'aria-label="Download CSV for ' + esc(t.name) + '" data-stop>' +
        ICONS.download + '<span>Download CSV</span></a>' +
        '<span class="download-caption">Open in Todoist → Import from CSV</span>' +
        '</div>';
    } else if (t.type === 'prompt' && t.prompt_url) {
      actionBlock = '<a class="btn-primary" href="' + esc(t.prompt_url) + '" ' +
        'aria-label="View prompt for ' + esc(t.name) + '" data-stop>' +
        '<span>View Prompt</span></a>';
    }
    var badgeLabel = t.type === 'prompt' ? 'AI Prompt' : 'Template';
    return '<button type="button" class="tpl-card tpl-card-clickable" ' +
      'data-slug="' + esc(t.slug) + '" data-type="' + esc(t.type) + '" ' +
      'aria-label="Open details for ' + esc(t.name) + '">' +
      '<div class="tpl-card-header">' +
        '<span class="tpl-type-badge">' + badgeLabel + '</span>' +
        '<h3 class="tpl-title">' + esc(t.name) + '</h3>' +
        (t.description ? '<p class="tpl-desc">' + esc(t.description) + '</p>' : '') +
      '</div>' +
      (tags  ? '<div class="tpl-tags">' + tags + '</div>' : '') +
      (stats ? '<div class="tpl-stats">' + stats + '</div>' : '') +
      previewHtml +
      '<div class="tpl-card-footer">' +
        '<span class="tpl-meta">' + metaLine + '</span>' +
        actionBlock +
      '</div>' +
    '</button>';
  }

  function buildRailCard(t) {
    return '<button type="button" class="rail-card" ' +
      'data-slug="' + esc(t.slug) + '" data-type="' + esc(t.type) + '" ' +
      'aria-label="Open details for ' + esc(t.name) + '">' +
      '<div class="rail-card-name">' + esc(t.name) + '</div>' +
      '<div class="rail-card-meta">' + (t.mtime ? esc(t.mtime) : '') + '</div>' +
    '</button>';
  }

  function recentlyUpdated(n) {
    return TEMPLATES.slice()
      .filter(function (t) { return t.mtime; })
      .sort(function (a, b) { return (a.mtime < b.mtime) ? 1 : (a.mtime > b.mtime ? -1 : 0); })
      .slice(0, n);
  }

  // ── Sorting & filtering ──────────────────────────────────────────────────
  var SORT_FNS = {
    'name-asc':    function (a, b) { return a.name.localeCompare(b.name); },
    'name-desc':   function (a, b) { return b.name.localeCompare(a.name); },
    'tasks-desc':  function (a, b) { return (b.task_count || 0) - (a.task_count || 0); },
    'version-desc':function (a, b) {
      function key(t) {
        var p = (t.version || '0.0.0').split('.').map(function (x) { return parseInt(x, 10) || 0; });
        return [p[0] || 0, p[1] || 0, p[2] || 0];
      }
      var ka = key(a), kb = key(b);
      for (var i = 0; i < 3; i++) if (ka[i] !== kb[i]) return kb[i] - ka[i];
      return 0;
    },
    'recent-desc': function (a, b) {
      var am = a.mtime || '', bm = b.mtime || '';
      return am < bm ? 1 : am > bm ? -1 : 0;
    }
  };

  function applySortAndFilter(items) {
    var filtered = items;
    if (state.tags.length) {
      filtered = items.filter(function (t) {
        return state.tags.every(function (tag) {
          return (t.tags || []).indexOf(tag) !== -1;
        });
      });
    }
    var fn = SORT_FNS[state.sort] || SORT_FNS['name-asc'];
    return filtered.slice().sort(fn);
  }

  function buildFilterBar(availableTags) {
    if (!availableTags.length) return '';
    var chips = availableTags.map(function (tag) {
      var active = state.tags.indexOf(tag) !== -1;
      return '<button type="button" class="tag-filter" ' +
        'aria-pressed="' + (active ? 'true' : 'false') + '" ' +
        'data-tag="' + esc(tag) + '">' + esc(tag) + '</button>';
    }).join('');
    var clearBtn = state.tags.length
      ? '<button type="button" class="btn-secondary" data-clear-filters>Clear filters</button>'
      : '';
    return '<div class="filter-bar" role="group" aria-label="Tag filters">' +
      '<span class="filter-bar-label">Filter by tag:</span>' +
      chips + clearBtn + '</div>';
  }

  function buildSortRow() {
    var opts = [
      ['name-asc',     'Name (A–Z)'],
      ['name-desc',    'Name (Z–A)'],
      ['tasks-desc',   'Tasks (high → low)'],
      ['version-desc', 'Version (newest)'],
      ['recent-desc',  'Recently updated']
    ];
    var html = opts.map(function (o) {
      return '<option value="' + o[0] + '"' + (state.sort === o[0] ? ' selected' : '') +
        '>' + o[1] + '</option>';
    }).join('');
    return '<div class="toolbar"><div class="sort-row">' +
      '<label for="sort-select">Sort:</label>' +
      '<select id="sort-select">' + html + '</select>' +
      '</div></div>';
  }

  // ── Views ─────────────────────────────────────────────────────────────────
  function renderHome() {
    var groups = groupByCategory(TEMPLATES);
    var cats = Object.keys(groups).sort();
    var container = document.getElementById('container');

    var recents = recentlyUpdated(6);
    var recentsHtml = '';
    if (recents.length) {
      recentsHtml =
        '<section class="recent-rail" aria-label="Recently updated templates">' +
          '<h2 class="rail-heading">Recently updated</h2>' +
          '<div class="rail-scroll" tabindex="0" role="region" ' +
            'aria-label="Recently updated templates, scrollable">' +
            recents.map(buildRailCard).join('') +
          '</div>' +
        '</section>';
    }

    var html = buildSpotlight(SPOTLIGHT) + recentsHtml;
    html += '<p class="intro">Browse <strong>' + TEMPLATES.length +
      '</strong> templates across <strong>' + cats.length + '</strong> categories.</p>';
    html += '<div class="category-grid">';

    cats.forEach(function (cat) {
      var items = groups[cat];
      var icon = catIcon(cat);
      var label = catLabel(cat);
      var count = items.length;
      var MAX_PREVIEW = 4;
      var previews = items.slice(0, MAX_PREVIEW);
      var more = count - previews.length;
      var previewItems = previews.map(function (t) {
        return '<li>' + esc(t.name) + '</li>';
      }).join('');
      var moreHtml = more > 0 ? '<li class="cat-more">+\u202f' + more + ' more</li>' : '';
      html +=
        '<a class="cat-card" href="#/category/' + encodeURIComponent(cat) + '" ' +
          'aria-label="Browse ' + esc(label) + ' templates">' +
          '<span class="cat-icon-wrap" aria-hidden="true" style="--cat-accent:' +
            esc(catAccent(cat)) + '">' + icon + '</span>' +
          '<h2 class="cat-title">' + esc(label) + '</h2>' +
          '<div class="cat-count">' + count + '\u202ftemplate' +
            (count !== 1 ? 's' : '') + '</div>' +
          '<ul class="cat-previews">' + previewItems + moreHtml + '</ul>' +
          '<span class="cat-arrow">View all ' + ICONS.arrow + '</span>' +
        '</a>';
    });
    html += '</div>';
    container.innerHTML = html;
    document.getElementById('breadcrumb').style.display = 'none';
    setHeadingTitle('Todoist Playbook — Template Gallery');
  }

  function renderCategory(cat) {
    var groups = groupByCategory(TEMPLATES);
    var items = groups[cat] || [];
    var label = catLabel(cat);
    var icon = catIcon(cat);
    var container = document.getElementById('container');

    var allTagsSet = {};
    items.forEach(function (t) { (t.tags || []).forEach(function (x) { allTagsSet[x] = 1; }); });
    var availableTags = Object.keys(allTagsSet).sort();

    var visibleItems = applySortAndFilter(items);

    var html = '' +
      '<div class="cat-detail-header">' +
        '<span class="cat-detail-icon-wrap" aria-hidden="true" style="--cat-accent:' +
          esc(catAccent(cat)) + '">' + icon + '</span>' +
        '<div>' +
          '<h2 class="cat-detail-title">' + esc(label) + '</h2>' +
          '<div class="cat-detail-count">' + visibleItems.length + ' of ' + items.length +
            '\u202ftemplate' + (items.length !== 1 ? 's' : '') + '</div>' +
        '</div>' +
      '</div>' +
      buildSortRow() +
      buildFilterBar(availableTags) +
      '<div class="template-grid">' + visibleItems.map(buildTemplateCard).join('') + '</div>';

    container.innerHTML = html;
    document.getElementById('crumb-label').textContent = icon + ' ' + label;
    document.getElementById('breadcrumb').style.display = 'block';
    setHeadingTitle(label + ' — Todoist Playbook');
  }

  function renderSearch(query) {
    var trimmed = (query || '').trim();
    var container = document.getElementById('container');
    if (!trimmed) {
      renderHome();
      return;
    }
    var q = trimmed.toLowerCase();
    var results = SEARCH_INDEX
      .filter(function (e) {
        return e.name.indexOf(q) !== -1 ||
               e.description.indexOf(q) !== -1 ||
               e.category.indexOf(q) !== -1 ||
               e.tags.some(function (t) { return t.indexOf(q) !== -1; });
      })
      .map(function (e) { return e.template; });

    var allTagsSet = {};
    results.forEach(function (t) { (t.tags || []).forEach(function (x) { allTagsSet[x] = 1; }); });
    var availableTags = Object.keys(allTagsSet).sort();

    var visibleResults = applySortAndFilter(results);

    var summary = visibleResults.length === 0
      ? 'No results for <strong>' + esc(trimmed) + '</strong>'
      : '<strong>' + visibleResults.length + '</strong> result' +
        (visibleResults.length !== 1 ? 's' : '') +
        ' for <strong>' + esc(trimmed) + '</strong>';

    var body = visibleResults.length === 0
      ? '<div class="no-results">' +
          '<div class="no-results-icon" aria-hidden="true">🔍</div>' +
          '<p>No templates matched your search. Try different keywords or browse by category.</p>' +
          '<div class="no-results-actions">' +
            '<button type="button" class="btn-secondary" data-clear-search>Clear search</button>' +
            '<a class="btn-secondary" href="#/">Browse all categories</a>' +
          '</div>' +
        '</div>'
      : buildSortRow() +
        buildFilterBar(availableTags) +
        '<div class="template-grid">' + visibleResults.map(buildTemplateCard).join('') + '</div>';

    container.innerHTML =
      '<p class="search-summary" role="status" aria-live="polite" aria-atomic="true">' +
      summary + '</p>' + body;
    document.getElementById('breadcrumb').style.display = 'none';
    setHeadingTitle('Search: ' + trimmed + ' — Todoist Playbook');
  }

  function setHeadingTitle(t) { document.title = t; }

  // ── State (sort, tag filter, query) ──────────────────────────────────────
  var state = {
    sort: 'name-asc',
    tags: [],
    query: '',
    view: 'home',
    cat: null
  };

  // ── Hash routing ─────────────────────────────────────────────────────────
  // Routes:
  //   ''                           → home
  //   #/category/<slug>?tags=a,b   → category
  //   #/search/<encoded>?tags=a,b  → search
  //   #/template/<type>/<slug>     → home/category + open modal
  function parseHash() {
    var h = window.location.hash || '';
    var parts = h.replace(/^#\/?/, '').split('?');
    var route = parts[0] || '';
    var qs = parts[1] || '';
    var qParams = {};
    qs.split('&').forEach(function (kv) {
      if (!kv) return;
      var eq = kv.indexOf('=');
      var k = decodeURIComponent(eq >= 0 ? kv.slice(0, eq) : kv);
      var v = eq >= 0 ? decodeURIComponent(kv.slice(eq + 1)) : '';
      qParams[k] = v;
    });
    return { route: route, params: qParams };
  }

  function applyTagsFromParams(params) {
    state.tags = params.tags ? params.tags.split(',').filter(Boolean) : [];
  }

  function handleRoute() {
    var p = parseHash();
    var route = p.route;
    applyTagsFromParams(p.params);
    if (p.params.sort) state.sort = p.params.sort;

    var m;
    if ((m = route.match(/^category\/(.+)$/))) {
      state.view = 'category';
      state.cat = decodeURIComponent(m[1]);
      state.query = '';
      syncSearchFromState();
      renderCategory(state.cat);
    } else if ((m = route.match(/^search\/(.+)$/))) {
      state.view = 'search';
      state.query = decodeURIComponent(m[1]);
      syncSearchFromState();
      renderSearch(state.query);
    } else if ((m = route.match(/^template\/([^/]+)\/(.+)$/))) {
      var type = decodeURIComponent(m[1]);
      var slug = decodeURIComponent(m[2]);
      var t = TEMPLATE_LOOKUP[type + ':' + slug];
      // Render category context if we know it, else home
      if (t && t.category) {
        state.view = 'category';
        state.cat = t.category;
        renderCategory(t.category);
      } else {
        state.view = 'home';
        renderHome();
      }
      if (t) openModal(t);
    } else {
      state.view = 'home';
      state.query = '';
      syncSearchFromState();
      renderHome();
    }
  }

  function navigate(hashWithoutLeadingHash) {
    window.location.hash = '#/' + hashWithoutLeadingHash;
  }

  function syncSearchFromState() {
    var input = document.getElementById('search-input');
    if (!input) return;
    if (input.value !== state.query) input.value = state.query;
    var clear = document.getElementById('search-clear');
    if (clear) clear.hidden = !state.query;
  }

  // ── Modal ─────────────────────────────────────────────────────────────────
  var modalBackdrop, modalTitleEl, modalSubtitle, modalBody, modalActions, modalCloseBtn;
  var focusStack = [];

  function getFocusables(container) {
    return Array.prototype.slice.call(container.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
      'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter(function (el) { return el.offsetParent !== null || el === container; });
  }

  function setBackgroundInert(on) {
    ['site-header', 'breadcrumb', 'main', 'site-footer'].forEach(function (id) {
      var el = document.getElementById(id) || document.querySelector('.' + id);
      if (!el) return;
      if (on) {
        el.setAttribute('inert', '');
        el.setAttribute('aria-hidden', 'true');
      } else {
        el.removeAttribute('inert');
        el.removeAttribute('aria-hidden');
      }
    });
  }

  function openModal(template) {
    if (!template) return;
    if (!modalBackdrop) modalCacheEls();

    focusStack.push(document.activeElement);
    modalTitleEl.textContent = template.name;

    var subParts = [];
    if (template.category) subParts.push(catLabel(template.category));
    if (template.version)  subParts.push('v' + template.version);
    if (template.author)   subParts.push('by ' + template.author);
    modalSubtitle.textContent = subParts.join(' \u00b7 ');

    var actionsHtml = '';
    if (template.type === 'template' && template.csv_url) {
      actionsHtml += '<div class="modal-action-group">' +
        '<a class="btn-primary" href="' + esc(template.csv_url) + '" download ' +
        'aria-label="Download CSV for ' + esc(template.name) + '">' +
        ICONS.download + '<span>Download CSV</span></a>' +
        '<span class="download-caption">Open in Todoist → Import from CSV</span>' +
        '</div>';
    } else if (template.type === 'prompt' && template.prompt_url) {
      actionsHtml += '<a class="btn-primary" href="' + esc(template.prompt_url) +
        '" target="_blank" rel="noopener noreferrer" ' +
        'aria-label="View prompt for ' + esc(template.name) + '">' +
        '<span>View Prompt</span>' + ICONS.external + '</a>';
    }
    if (template.github_path) {
      actionsHtml += '<a class="btn-secondary" href="' + REPO_URL + '/blob/main/' +
        esc(template.github_path) + '" target="_blank" rel="noopener noreferrer" ' +
        'aria-label="Open ' + esc(template.name) + ' source on GitHub">' +
        ICONS.github + '<span>Open on GitHub</span></a>';
    }
    modalActions.innerHTML = actionsHtml;

    if (template.readme && template.readme.trim()) {
      modalBody.classList.remove('empty');
      modalBody.innerHTML = sanitiseMarkdown(rewriteReadmeAssets(template.readme, template));
      wireReadmeLinks(template);
    } else {
      modalBody.classList.add('empty');
      modalBody.innerHTML = '<p>No README is available for this template yet.</p>';
    }

    modalBackdrop.classList.add('open');
    modalBackdrop.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    setBackgroundInert(true);
    modalBody.scrollTop = 0;
    modalCloseBtn.focus();
  }

  function closeModal() {
    if (!modalBackdrop) return;
    if (!modalBackdrop.classList.contains('open')) return;
    modalBackdrop.classList.remove('open');
    modalBackdrop.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setBackgroundInert(false);
    var prev = focusStack.pop();
    if (prev && typeof prev.focus === 'function') prev.focus();
    // Pop hash back if it points at template
    if (/^#\/template\//.test(window.location.hash)) {
      if (history.length > 1) history.back();
      else history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  }

  function rewriteReadmeAssets(md, ctx) {
    // Rewrite relative <img src="..."> and [text](relative) links that don't map to
    // a copied template/prompt path so that they resolve to absolute repo URLs.
    var basePath = (ctx && ctx.github_path) || '';
    var baseUrl = REPO_URL + '/blob/main/' + basePath + '/';
    var rawBase = REPO_URL.replace('github.com', 'raw.githubusercontent.com') +
      '/main/' + basePath + '/';
    return md.replace(/!\[([^\]]*)\]\(([^)\s]+)(\s+[^)]*)?\)/g, function (m, alt, src, title) {
      if (/^https?:|^data:|^#/.test(src)) return m;
      if (src.indexOf('csv-templates/') === 0 || src.indexOf('prompt-templates/') === 0) return m;
      return '![' + alt + '](' + rawBase + src + (title || '') + ')';
    }).replace(/\[([^\]]+)\]\(([^)\s]+)(\s+[^)]*)?\)/g, function (m, text, href, title) {
      if (/^https?:|^mailto:|^#/.test(href)) return m;
      if (href.indexOf('csv-templates/') === 0 || href.indexOf('prompt-templates/') === 0) return m;
      // If it points at a known sibling slug, keep relative — wireReadmeLinks intercepts it
      var cleaned = href.split('#')[0].split('?')[0].replace(/\/+$/, '');
      var segs = cleaned.split('/').filter(function (s) { return s && s !== '.' && s !== '..'; });
      var lastSeg = segs.length ? segs[segs.length - 1].replace(/\.(md|csv)$/i, '') : '';
      if (lastSeg && (TEMPLATE_LOOKUP['template:' + lastSeg] || TEMPLATE_LOOKUP['prompt:' + lastSeg])) {
        return m;
      }
      return '[' + text + '](' + baseUrl + href + (title || '') + ')';
    });
  }

  function wireReadmeLinks(template) {
    modalBody.querySelectorAll('a[href]').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (/^https?:|^mailto:|^#/.test(href)) {
        a.setAttribute('target', '_blank');
        a.setAttribute('rel', 'noopener noreferrer');
        return;
      }
      var cleaned = href.split('#')[0].split('?')[0].replace(/\/+$/, '');
      if (!cleaned) return;
      var segs = cleaned.split('/').filter(function (s) { return s && s !== '.' && s !== '..'; });
      if (!segs.length) return;
      var lastSeg = segs[segs.length - 1].replace(/\.(md|csv)$/i, '');
      var target = TEMPLATE_LOOKUP['template:' + lastSeg] || TEMPLATE_LOOKUP['prompt:' + lastSeg];
      if (target) {
        a.addEventListener('click', function (e) {
          e.preventDefault();
          openModal(target);
        });
      }
    });
  }

  function modalCacheEls() {
    modalBackdrop = document.getElementById('modal-backdrop');
    modalTitleEl  = document.getElementById('modal-title');
    modalSubtitle = document.getElementById('modal-subtitle');
    modalBody     = document.getElementById('modal-body');
    modalActions  = document.getElementById('modal-actions');
    modalCloseBtn = document.getElementById('modal-close');

    modalCloseBtn.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', function (e) {
      if (e.target === modalBackdrop) closeModal();
    });
  }

  // ── Search input wiring ──────────────────────────────────────────────────
  var searchDebounce;
  function setupSearch() {
    var input  = document.getElementById('search-input');
    var clear  = document.getElementById('search-clear');
    if (!input || !clear) return;

    input.addEventListener('input', function () {
      var q = input.value;
      clear.hidden = !q;
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(function () {
        if (q) {
          window.location.hash = '#/search/' + encodeURIComponent(q);
        } else if (/^#\/search\//.test(window.location.hash)) {
          window.location.hash = '';
        }
      }, 150);
    });

    clear.addEventListener('click', function () {
      input.value = '';
      clear.hidden = true;
      window.location.hash = '';
      input.focus();
    });
  }

  // ── Delegated handlers ───────────────────────────────────────────────────
  function setupDelegation() {
    document.addEventListener('click', function (e) {
      // Skip clicks on real links/buttons within a clickable card
      var inner = e.target.closest && e.target.closest('a, button');
      var card = e.target.closest && e.target.closest('.tpl-card-clickable, .rail-card');

      if (e.target.closest && e.target.closest('[data-clear-search]')) {
        var input = document.getElementById('search-input');
        if (input) input.value = '';
        window.location.hash = '';
        if (input) input.focus();
        return;
      }
      if (e.target.closest && e.target.closest('[data-clear-filters]')) {
        state.tags = [];
        if (state.view === 'category') renderCategory(state.cat);
        else if (state.view === 'search') renderSearch(state.query);
        return;
      }
      var tagBtn = e.target.closest && e.target.closest('.tag-filter');
      if (tagBtn) {
        var tag = tagBtn.dataset.tag;
        var ix = state.tags.indexOf(tag);
        if (ix === -1) state.tags.push(tag);
        else state.tags.splice(ix, 1);
        if (state.view === 'category') renderCategory(state.cat);
        else if (state.view === 'search') renderSearch(state.query);
        return;
      }
      // Card open
      if (card && (!inner || inner === card)) {
        var template = TEMPLATE_LOOKUP[card.dataset.type + ':' + card.dataset.slug];
        if (template) {
          var deepHash = '#/template/' + encodeURIComponent(card.dataset.type) +
            '/' + encodeURIComponent(card.dataset.slug);
          history.pushState(null, '', deepHash);
          openModal(template);
        }
      }
    });

    document.addEventListener('change', function (e) {
      if (e.target && e.target.id === 'sort-select') {
        state.sort = e.target.value;
        if (state.view === 'category') renderCategory(state.cat);
        else if (state.view === 'search') renderSearch(state.query);
      }
    });

    var btnBack = document.getElementById('btn-back');
    if (btnBack) btnBack.addEventListener('click', function () {
      window.location.hash = '';
    });
  }

  // ── Keyboard ─────────────────────────────────────────────────────────────
  function setupKeyboard() {
    document.addEventListener('keydown', function (e) {
      // Escape: close modal, else clear search
      if (e.key === 'Escape') {
        if (modalBackdrop && modalBackdrop.classList.contains('open')) {
          closeModal();
          e.preventDefault();
          return;
        }
        var input = document.getElementById('search-input');
        if (input && input.value) {
          input.value = '';
          var clear = document.getElementById('search-clear');
          if (clear) clear.hidden = true;
          window.location.hash = '';
          e.preventDefault();
        }
        return;
      }
      // "/" focuses search when not typing
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        var ae = document.activeElement;
        var inField = ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA' || ae.isContentEditable);
        if (!inField) {
          var input2 = document.getElementById('search-input');
          if (input2) { input2.focus(); e.preventDefault(); }
        }
        return;
      }
      // Focus trap inside modal
      if (e.key === 'Tab' && modalBackdrop && modalBackdrop.classList.contains('open')) {
        var dialog = modalBackdrop.querySelector('.modal-dialog');
        if (!dialog) return;
        var focusables = getFocusables(dialog);
        if (!focusables.length) { e.preventDefault(); return; }
        var first = focusables[0];
        var last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          last.focus(); e.preventDefault();
        } else if (!e.shiftKey && document.activeElement === last) {
          first.focus(); e.preventDefault();
        }
      }
    });
  }

  // ── Service worker registration ─────────────────────────────────────────
  function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    if (window.location.protocol === 'file:') return;
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () { /* noop */ });
    });
  }

  // ── Init ─────────────────────────────────────────────────────────────────
  function init() {
    setupThemeToggle();
    modalCacheEls();
    setupSearch();
    setupDelegation();
    setupKeyboard();
    window.addEventListener('hashchange', handleRoute);
    handleRoute();
    registerSW();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
