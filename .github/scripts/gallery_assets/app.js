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

  function templateSourceUrl(t) {
    var path = t && t.github_path ? String(t.github_path).replace(/^\/+/, '') : '';
    return path ? (REPO_URL + '/tree/main/' + path) : REPO_URL;
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
    external:  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><path d="M15 3h6v6"/><path d="M10 14L21 3"/></svg>',
    sparkles:  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>',
    star:      '<svg viewBox="0 0 24 24" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    tasks:     '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 6h10"/><path d="M11 12h10"/><path d="M11 18h10"/><path d="m3 6 2 2 4-4"/><path d="m3 12 2 2 4-4"/><path d="m3 18 2 2 4-4"/></svg>',
    sections:  '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="5" rx="1"/><rect x="3" y="11" width="18" height="3" rx="1"/><rect x="3" y="16" width="18" height="4" rx="1"/></svg>',
    clock:     '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    repeat:    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 3v6h-6"/></svg>',
    circle:    '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/></svg>'
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
    btn.setAttribute('title', themeLabel(mode));
    btn.setAttribute('aria-pressed', mode === 'dark' ? 'true' : 'false');
    btn.addEventListener('click', function () {
      var next = cycleTheme(readTheme());
      writeTheme(next);
      applyTheme(next);
      btn.innerHTML = themeIcon(next);
      btn.setAttribute('aria-label', themeLabel(next));
      btn.setAttribute('title', themeLabel(next));
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

  function buildSpotlightPreview(rows, taskCount) {
    var MAX = 5;
    var shown = rows.slice(0, MAX);
    var rest = rows.length - shown.length;
    var countLabel = taskCount != null
      ? taskCount + '\u202ftask' + (taskCount !== 1 ? 's' : '')
      : '';
    var html = '<div class="spotlight-preview-header">' +
      '<span class="spotlight-preview-label">Task list</span>' +
      (countLabel ? '<span class="spotlight-preview-count">' + esc(countLabel) + '</span>' : '') +
      '</div>';
    shown.forEach(function (r) {
      var content = r.content.replace(/@[\w-]+/g, '').trim();
      if (r.type === 'section') {
        html += '<div class="preview-row section">' + esc(content) + '</div>';
      } else {
        html += '<div class="preview-row task">' +
          '<span class="preview-task-icon" aria-hidden="true">' + ICONS.circle + '</span>' +
          '<span class="preview-task-text">' + esc(content) + '</span>' +
          '</div>';
      }
    });
    if (rest > 0) html += '<div class="preview-more">+\u202f' + rest + ' more</div>';
    return html;
  }

  function buildStats(t) {
    var stats = [];
    if (t.task_count)
      stats.push('<span>' + ICONS.tasks + '\u202f' + t.task_count + '\u202ftask' + (t.task_count !== 1 ? 's' : '') + '</span>');
    if (t.section_count)
      stats.push('<span>' + ICONS.sections + '\u202f' + t.section_count + '\u202fsection' + (t.section_count !== 1 ? 's' : '') + '</span>');
    if (t.estimated_duration)
      stats.push('<span>' + ICONS.clock + '\u202f' + esc(formatDuration(t.estimated_duration)) + '</span>');
    if (t.recurrence_suggestion)
      stats.push('<span>' + ICONS.repeat + '\u202f' + esc(t.recurrence_suggestion) + '</span>');
    if (!stats.length) return '';
    var sep = '<span class="sep" aria-hidden="true">·</span>';
    return stats.join(sep);
  }

  function buildFactGrid(t) {
    var facts = [];
    if (t.task_count) {
      facts.push(['Tasks', t.task_count + '\u202ftask' + (t.task_count !== 1 ? 's' : '')]);
    }
    if (t.section_count) {
      facts.push(['Sections', t.section_count + '\u202fsection' + (t.section_count !== 1 ? 's' : '')]);
    }
    if (t.estimated_duration) {
      facts.push(['Duration', formatDuration(t.estimated_duration)]);
    }
    if (t.recurrence_suggestion) {
      facts.push(['Repeat', t.recurrence_suggestion]);
    }
    if (!facts.length) return '';
    return '<div class="tpl-fact-grid">' + facts.map(function (fact) {
      return '<div class="tpl-fact">' +
        '<span class="tpl-fact-label">' + esc(fact[0]) + '</span>' +
        '<strong class="tpl-fact-value">' + esc(fact[1]) + '</strong>' +
      '</div>';
    }).join('') + '</div>';
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
      ? '<div class="spotlight-preview">' + buildSpotlightPreview(t.rows, t.task_count) + '</div>'
      : '';
    var actionBtn = t.csv_url
      ? '<a class="btn-primary" href="' + esc(t.csv_url) + '" download ' +
        'aria-label="Download CSV for ' + esc(t.name) + '" ' +
        'data-stop>' + ICONS.download + '<span>Download CSV</span></a>'
      : '';
    return '' +
      '<div class="spotlight-section">' +
        '<h2 class="section-heading spotlight-heading">' + ICONS.star + ' Template Spotlight</h2>' +
        '<div class="spotlight-card tpl-card-clickable" tabindex="0" role="button" ' +
           'data-slug="' + esc(t.slug) + '" data-type="' + esc(t.type || 'template') + '" ' +
           'aria-label="Open details for ' + esc(t.name) + '">' +
          '<div class="spotlight-body">' +
            '<span class="spotlight-badge">Featured Template</span>' +
            '<h2 class="spotlight-name"><a href="' + esc(templateSourceUrl(t)) + '" target="_blank" rel="noopener noreferrer" data-stop>' + esc(t.name) + '</a></h2>' +
            (t.description ? '<p class="spotlight-desc">' + esc(t.description) + '</p>' : '') +
            (tags ? '<div class="spotlight-tags">' + tags + '</div>' : '') +
            (stats ? '<div class="spotlight-stats">' + stats + '</div>' : '') +
            '<div class="spotlight-footer">' + actionBtn +
              '<span class="spotlight-meta">' + metaLine + '</span>' +
            '</div>' +
           '</div>' +
           previewHtml +
         '</div>' +
      '</div>';
  }

  function buildTemplateCard(t) {
    var tags = (t.tags || []).map(function (tag) {
      var active = state.tags.indexOf(tag) !== -1;
      return '<button type="button" class="tag tag-toggle" data-tag="' + esc(tag) + '" ' +
        'aria-pressed="' + (active ? 'true' : 'false') + '" ' +
        'aria-label="Toggle filter ' + esc(tag) + '">' + esc(tag) + '</button>';
    }).join('');
    var facts = buildFactGrid(t);
    var metaLine = [
      t.author  ? 'by ' + esc(t.author)  : '',
      t.version ? 'v' + esc(t.version) : ''
    ].filter(Boolean).join(' \u00b7 ');
    var previewHtml = '';
    var previewLabel = t.type === 'prompt' ? 'Inputs' : 'Task preview';
    var previewCount = '';
    if (t.type === 'template' && t.rows && t.rows.length) {
      previewHtml = '<div class="tpl-preview">' + buildPreview(t.rows) + '</div>';
      if (t.task_count) {
        previewCount = t.task_count + '\u202ftask' + (t.task_count !== 1 ? 's' : '');
      }
    } else if (t.type === 'prompt' && t.inputs && t.inputs.length) {
      var chips = t.inputs.map(function (i) {
        return '<span class="input-chip">' + esc(i) + '</span>';
      }).join('');
      previewHtml = '<div class="tpl-inputs">' + chips + '</div>';
      previewCount = t.inputs.length + '\u202finput' + (t.inputs.length !== 1 ? 's' : '');
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
    var tagsSection = tags
      ? '<div class="tpl-card-section">' +
          '<div class="tpl-section-label">Tags</div>' +
          '<div class="tpl-tags">' + tags + '</div>' +
        '</div>'
      : '';
    var factsSection = facts
      ? '<div class="tpl-card-section">' +
          '<div class="tpl-section-label">Overview</div>' +
          facts +
        '</div>'
      : '';
    var previewSection = previewHtml
      ? '<div class="tpl-card-aside">' +
          '<div class="tpl-card-section tpl-card-section-preview">' +
            '<div class="tpl-preview-head">' +
              '<span class="tpl-section-label">' + previewLabel + '</span>' +
              (previewCount ? '<span class="tpl-preview-count">' + esc(previewCount) + '</span>' : '') +
            '</div>' +
            previewHtml +
          '</div>' +
        '</div>'
      : '';
    return '<div class="tpl-card tpl-card-clickable" tabindex="0" role="button" ' +
      'data-slug="' + esc(t.slug) + '" data-type="' + esc(t.type) + '" ' +
      'aria-label="Open details for ' + esc(t.name) + '">' +
      '<div class="tpl-card-main">' +
        '<div class="tpl-card-copy">' +
          '<div class="tpl-card-header">' +
            '<span class="tpl-type-badge">' + badgeLabel + '</span>' +
            '<h3 class="tpl-title"><a href="' + esc(templateSourceUrl(t)) + '" target="_blank" rel="noopener noreferrer" data-stop>' + esc(t.name) + '</a></h3>' +
            (t.description ? '<p class="tpl-desc">' + esc(t.description) + '</p>' : '') +
          '</div>' +
          factsSection +
          tagsSection +
        '</div>' +
        previewSection +
      '</div>' +
      '<div class="tpl-card-footer">' +
        '<span class="tpl-meta">' + metaLine + '</span>' +
        actionBlock +
      '</div>' +
    '</div>';
  }

  function buildRailCard(t) {
    var badgeLabel = t.type === 'prompt' ? 'AI Prompt' : 'Template';
    return '<a class="rail-card" href="' + esc(templateSourceUrl(t)) + '" target="_blank" rel="noopener noreferrer" data-stop ' +
      'data-slug="' + esc(t.slug) + '" data-type="' + esc(t.type) + '" ' +
      'aria-label="Open details for ' + esc(t.name) + '">' +
      '<span class="rail-card-badge">' + badgeLabel + '</span>' +
      '<div class="rail-card-name">' + esc(t.name) + '</div>' +
      (t.description ? '<div class="rail-card-desc">' + esc(t.description) + '</div>' : '') +
      '<div class="rail-card-meta">' + (t.mtime ? esc(t.mtime) : '') + '</div>' +
    '</a>';
  }

  function recentlyUpdated(n) {
    var withMtime = TEMPLATES.filter(function (t) { return t.mtime; });
    if (!withMtime.length) return [];
    // When a single date covers ≥50% of templates it indicates a bulk automated
    // update (e.g. a CI workflow bumping many meta.yml files at once). Exclude
    // those entries so the rail only surfaces genuine, distinct manual updates.
    var counts = {};
    withMtime.forEach(function (t) { counts[t.mtime] = (counts[t.mtime] || 0) + 1; });
    var bulkThreshold = Math.ceil(withMtime.length / 2);
    var meaningful = withMtime.filter(function (t) { return counts[t.mtime] < bulkThreshold; });
    return meaningful
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

  function applyTagFilter(items, tags, match) {
    if (!tags.length) return items;
    if (match === 'or') {
      return items.filter(function (t) {
        var ts = t.tags || [];
        for (var i = 0; i < tags.length; i++) {
          if (ts.indexOf(tags[i]) !== -1) return true;
        }
        return false;
      });
    }
    return items.filter(function (t) {
      var ts = t.tags || [];
      for (var i = 0; i < tags.length; i++) {
        if (ts.indexOf(tags[i]) === -1) return false;
      }
      return true;
    });
  }

  function applySortAndFilter(items, opts) {
    opts = opts || {};
    var useTags = opts.useTags !== false;
    var filtered = useTags ? applyTagFilter(items, state.tags, state.match) : items;
    var fn = SORT_FNS[state.sort] || SORT_FNS['name-asc'];
    return filtered.slice().sort(fn);
  }

  function buildMatchControl() {
    var opts = [['and', 'AND'], ['or', 'OR']];
    var btns = opts.map(function (o) {
      var active = state.match === o[0];
      return '<button type="button" class="seg-btn" data-match="' + o[0] + '" ' +
        'aria-pressed="' + (active ? 'true' : 'false') + '">' + o[1] + '</button>';
    }).join('');
    return '<div class="segmented" role="group" aria-label="Match tags">' +
      '<span class="segmented-label">Match:</span>' + btns + '</div>';
  }

  function buildFilterBar(availableTags) {
    if (!availableTags.length) return '';
    var chips = availableTags.map(function (tag) {
      var active = state.tags.indexOf(tag) !== -1;
      return '<button type="button" class="tag-filter" ' +
        'aria-pressed="' + (active ? 'true' : 'false') + '" ' +
        'data-tag="' + esc(tag) + '">' + esc(tag) + '</button>';
    }).join('');
    var matchControl = state.tags.length > 1 ? buildMatchControl() : '';
    var clearBtn = state.tags.length
      ? '<button type="button" class="btn-secondary" data-clear-filters>Clear filters</button>'
      : '';
    var help = state.tags.length > 1
      ? '<span class="filter-bar-help">' +
          (state.match === 'or'
            ? 'Showing templates with any selected tag.'
            : 'Showing templates with all selected tags.') +
        '</span>'
      : '';
    return '<div class="filter-bar" role="group" aria-label="Tag filters">' +
      '<span class="filter-bar-label">Filter by tag:</span>' +
      chips + matchControl + clearBtn + help + '</div>';
  }

  function buildTagCloud(limit) {
    var counts = {};
    TEMPLATES.forEach(function (t) {
      (t.tags || []).forEach(function (tag) {
        counts[tag] = (counts[tag] || 0) + 1;
      });
    });
    var allTags = Object.keys(counts);
    if (!allTags.length) return '';
    allTags.sort(function (a, b) {
      return counts[b] - counts[a] || a.localeCompare(b);
    });
    if (typeof limit === 'number' && limit > 0) allTags = allTags.slice(0, limit);
    var chips = allTags.map(function (tag) {
      return '<button type="button" class="tag-cloud-chip" data-tag-cloud="' + esc(tag) + '" ' +
        'aria-label="Browse templates tagged ' + esc(tag) + '">' +
        '<span>' + esc(tag) + '</span>' +
        '<span class="tag-cloud-count" aria-hidden="true">' + counts[tag] + '</span>' +
        '</button>';
    }).join('');
    return '<section class="tag-cloud" aria-label="Browse by tag">' +
      '<h2 class="tag-cloud-heading">Browse by tag</h2>' +
      '<div class="tag-cloud-list">' + chips + '</div>' +
      '</section>';
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

    var recents = recentlyUpdated(4);
    var recentsHtml = '';
    if (recents.length) {
      recentsHtml =
        '<section class="recent-rail" aria-label="Recently updated templates">' +
          '<h2 class="section-heading rail-heading">' + ICONS.clock + ' Recently updated</h2>' +
          '<div class="recent-grid">' +
            recents.map(buildRailCard).join('') +
          '</div>' +
        '</section>';
    }

    var html = buildSpotlight(SPOTLIGHT) + recentsHtml + buildTagCloud(20);
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
    setHeadingTitle('Todoist Playbook - Template Gallery');
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

    if (!trimmed && !state.tags.length) {
      renderHome();
      return;
    }

    var useText = state.mode !== 'tags' && !!trimmed;
    var useTags = state.mode !== 'text';

    var base;
    if (useText) {
      var q = trimmed.toLowerCase();
      base = SEARCH_INDEX
        .filter(function (e) {
          return e.name.indexOf(q) !== -1 ||
                 e.description.indexOf(q) !== -1 ||
                 e.category.indexOf(q) !== -1 ||
                 e.tags.some(function (t) { return t.indexOf(q) !== -1; });
        })
        .map(function (e) { return e.template; });
    } else {
      base = TEMPLATES.slice();
    }

    var allTagsSet = {};
    base.forEach(function (t) { (t.tags || []).forEach(function (x) { allTagsSet[x] = 1; }); });
    var availableTags = Object.keys(allTagsSet).sort();

    var visible = applySortAndFilter(base, { useTags: useTags });

    var summary;
    if (useText) {
      summary = visible.length === 0
        ? 'No results for <strong>' + esc(trimmed) + '</strong>'
        : '<strong>' + visible.length + '</strong> result' +
          (visible.length !== 1 ? 's' : '') +
          ' for <strong>' + esc(trimmed) + '</strong>';
    } else if (state.tags.length) {
      summary = '<strong>' + visible.length + '</strong> template' +
        (visible.length !== 1 ? 's' : '') +
        ' tagged ' + (state.match === 'or' ? 'with any of' : 'with all of') + ' ' +
        state.tags.map(function (t) { return '<em>' + esc(t) + '</em>'; }).join(', ');
      if (state.mode === 'text' && trimmed) {
        summary += ' <span class="search-summary-note">(text query ignored — Tags mode)</span>';
      }
    } else {
      summary = 'Browse all <strong>' + visible.length + '</strong> templates';
    }
    if (state.mode === 'tags' && trimmed) {
      summary += ' <span class="search-summary-note">(text query ignored — Tags mode)</span>';
    } else if (state.mode === 'text' && state.tags.length && trimmed) {
      summary += ' <span class="search-summary-note">(tag filters ignored — Text mode)</span>';
    }

    var body = visible.length === 0
      ? '<div class="no-results">' +
          '<div class="no-results-icon" aria-hidden="true">🔍</div>' +
          '<p>No templates matched. Try different keywords, fewer tags, or switch the match mode.</p>' +
          '<div class="no-results-actions">' +
            (trimmed ? '<button type="button" class="btn-secondary" data-clear-search>Clear search</button>' : '') +
            (state.tags.length ? '<button type="button" class="btn-secondary" data-clear-filters>Clear tag filters</button>' : '') +
            '<a class="btn-secondary" href="#/">Browse all categories</a>' +
          '</div>' +
        '</div>'
      : buildSortRow() +
        buildFilterBar(availableTags) +
        '<div class="template-grid">' + visible.map(buildTemplateCard).join('') + '</div>';

    container.innerHTML =
      '<p class="search-summary" role="status" aria-live="polite" aria-atomic="true">' +
      summary + '</p>' + body;
    document.getElementById('breadcrumb').style.display = 'none';
    setHeadingTitle((trimmed ? 'Search: ' + trimmed : 'Browse by tag') + ' — Todoist Playbook');
  }

  function renderBrowse() {
    renderSearch('');
  }

  function setHeadingTitle(t) { document.title = t; }

  // ── State (sort, tag filter, query, search mode, match logic) ───────────
  var state = {
    sort: 'name-asc',
    tags: [],
    query: '',
    view: 'home',
    cat: null,
    mode: 'all',   // 'all' | 'text' | 'tags'
    match: 'and'   // 'and' | 'or'
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
    state.mode = (params.mode === 'text' || params.mode === 'tags') ? params.mode : 'all';
    state.match = (params.match === 'or') ? 'or' : 'and';
  }

  function buildRouteHash() {
    var route = '';
    if (state.view === 'category' && state.cat) {
      route = 'category/' + encodeURIComponent(state.cat);
    } else if (state.view === 'search' && state.query) {
      route = 'search/' + encodeURIComponent(state.query);
    } else if (state.view === 'browse') {
      route = 'browse';
    }
    var params = [];
    if (state.tags.length) params.push('tags=' + encodeURIComponent(state.tags.join(',')));
    if (state.sort && state.sort !== 'name-asc') params.push('sort=' + encodeURIComponent(state.sort));
    if (state.mode && state.mode !== 'all') params.push('mode=' + encodeURIComponent(state.mode));
    if (state.match && state.match !== 'and') params.push('match=' + encodeURIComponent(state.match));
    var qs = params.join('&');
    if (!route && !qs) return '';
    return '#/' + route + (qs ? '?' + qs : '');
  }

  function syncHashFromState() {
    var newHash = buildRouteHash() || '';
    var current = window.location.hash || '';
    if (current !== newHash) {
      var base = window.location.pathname + window.location.search;
      history.replaceState(null, '', base + newHash);
    }
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
    } else if (route === 'browse') {
      state.view = 'browse';
      state.query = '';
      syncSearchFromState();
      renderBrowse();
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
    syncSearchControlsVisibility();
    syncModeControl();
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

    var buttonsHtml = '';
    var captionHtml = '';
    if (template.type === 'template' && template.csv_url) {
      buttonsHtml += '<a class="btn-primary" href="' + esc(template.csv_url) + '" download ' +
        'aria-label="Download CSV for ' + esc(template.name) + '">' +
        ICONS.download + '<span>Download CSV</span></a>';
      captionHtml = '<span class="download-caption">Open in Todoist \u2192 Import from CSV</span>';
    } else if (template.type === 'prompt' && template.prompt_url) {
      buttonsHtml += '<a class="btn-primary" href="' + esc(template.prompt_url) +
        '" target="_blank" rel="noopener noreferrer" ' +
        'aria-label="View prompt for ' + esc(template.name) + '">' +
        '<span>View Prompt</span>' + ICONS.external + '</a>';
    }
    if (template.github_path) {
      buttonsHtml += '<a class="btn-secondary" href="' + REPO_URL + '/blob/main/' +
        esc(template.github_path) + '" target="_blank" rel="noopener noreferrer" ' +
        'aria-label="Open ' + esc(template.name) + ' source on GitHub">' +
        ICONS.github + '<span>Open on GitHub</span></a>';
    }
    modalActions.innerHTML = buttonsHtml
      ? '<div class="modal-action-group">' +
          '<div class="modal-action-buttons">' + buttonsHtml + '</div>' +
          captionHtml +
        '</div>'
      : '';

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

  // ── State helpers ─────────────────────────────────────────────────────────
  function rerenderCurrentView() {
    if (state.view === 'category') renderCategory(state.cat);
    else if (state.view === 'search') renderSearch(state.query);
    else if (state.view === 'browse') renderBrowse();
    else renderHome();
    syncSearchControlsVisibility();
    syncModeControl();
    syncHashFromState();
  }

  function toggleTag(tag) {
    if (!tag) return;
    var ix = state.tags.indexOf(tag);
    if (ix === -1) state.tags.push(tag);
    else state.tags.splice(ix, 1);

    if (state.view === 'home') {
      if (state.tags.length) {
        state.view = 'browse';
        window.location.hash = buildRouteHash();
        return;
      }
      renderHome();
      syncHashFromState();
      return;
    }
    if (state.view === 'browse' && !state.tags.length) {
      state.view = 'home';
      window.location.hash = '';
      return;
    }
    rerenderCurrentView();
  }

  function syncSearchControlsVisibility() {
    var el = document.getElementById('search-controls');
    if (!el) return;
    el.hidden = !(state.view === 'search' || state.view === 'browse');
  }

  function syncModeControl() {
    var el = document.getElementById('search-controls');
    if (!el) return;
    var btns = el.querySelectorAll('.seg-btn[data-mode]');
    Array.prototype.forEach.call(btns, function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-mode') === state.mode ? 'true' : 'false');
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
          state.view = 'search';
          state.query = q;
          window.location.hash = buildRouteHash();
        } else if (state.tags.length) {
          state.view = 'browse';
          state.query = '';
          window.location.hash = buildRouteHash();
        } else if (/^#\/(?:search|browse)/.test(window.location.hash)) {
          window.location.hash = '';
        }
      }, 150);
    });

    clear.addEventListener('click', function () {
      input.value = '';
      clear.hidden = true;
      if (state.tags.length) {
        state.view = 'browse';
        state.query = '';
        window.location.hash = buildRouteHash();
      } else {
        window.location.hash = '';
      }
      input.focus();
    });
  }

  // ── Delegated handlers ───────────────────────────────────────────────────
  function setupDelegation() {
    function openCard(card) {
      if (!card) return;
      var template = TEMPLATE_LOOKUP[card.dataset.type + ':' + card.dataset.slug];
      if (!template) return;
      var deepHash = '#/template/' + encodeURIComponent(card.dataset.type) +
        '/' + encodeURIComponent(card.dataset.slug);
      history.pushState(null, '', deepHash);
      openModal(template);
    }

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
        if (state.view === 'browse') {
          state.view = 'home';
          window.location.hash = '';
          return;
        }
        rerenderCurrentView();
        return;
      }
      var cloudChip = e.target.closest && e.target.closest('.tag-cloud-chip');
      if (cloudChip) {
        toggleTag(cloudChip.getAttribute('data-tag-cloud'));
        return;
      }
      var cardTag = e.target.closest && e.target.closest('.tag-toggle');
      if (cardTag) {
        toggleTag(cardTag.getAttribute('data-tag'));
        return;
      }
      var tagBtn = e.target.closest && e.target.closest('.tag-filter');
      if (tagBtn) {
        toggleTag(tagBtn.getAttribute('data-tag'));
        return;
      }
      var modeBtn = e.target.closest && e.target.closest('.seg-btn[data-mode]');
      if (modeBtn) {
        var newMode = modeBtn.getAttribute('data-mode');
        if (newMode && state.mode !== newMode) {
          state.mode = newMode;
          if (state.view === 'home') {
            // Mode control isn't shown on home, but be safe
            syncModeControl();
            return;
          }
          rerenderCurrentView();
        }
        return;
      }
      var matchBtn = e.target.closest && e.target.closest('.seg-btn[data-match]');
      if (matchBtn) {
        var newMatch = matchBtn.getAttribute('data-match');
        if (newMatch && state.match !== newMatch) {
          state.match = newMatch;
          rerenderCurrentView();
        }
        return;
      }
      // Card open
      if (card && (!inner || inner === card)) {
        e.preventDefault();
        openCard(card);
      }
    });

    document.addEventListener('change', function (e) {
      if (e.target && e.target.id === 'sort-select') {
        state.sort = e.target.value;
        rerenderCurrentView();
      }
    });

    var btnBack = document.getElementById('btn-back');
    if (btnBack) btnBack.addEventListener('click', function () {
      window.location.hash = '';
    });

    document.addEventListener('keydown', function (e) {
      var card = e.target.closest && e.target.closest('.tpl-card-clickable');
      if (!card) return;
      if (e.target !== card) return;
      if (e.key !== 'Enter' && e.key !== ' ') return;
      e.preventDefault();
      openCard(card);
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
          if (state.tags.length) {
            state.view = 'browse';
            state.query = '';
            window.location.hash = buildRouteHash();
          } else {
            window.location.hash = '';
          }
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
  function setupHeaderStat() {
    var el = document.getElementById('header-stat');
    if (!el || !TEMPLATES.length) return;
    var tplCount = TEMPLATES.length;
    var catCount = Object.keys(groupByCategory(TEMPLATES)).length;
    var parts = [tplCount + ' template' + (tplCount !== 1 ? 's' : '')];
    if (catCount) parts.push(catCount + ' categor' + (catCount !== 1 ? 'ies' : 'y'));
    el.textContent = parts.join(' \u00b7 ');
  }

  function init() {
    setupThemeToggle();
    setupHeaderStat();
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
