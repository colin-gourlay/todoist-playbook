// Load template data from the JSON island injected at build time.
// The island uses type="application/json" which is not executable — CSP-safe.
const __DATA__ = JSON.parse(document.getElementById('tp-data').textContent);
const TEMPLATES = __DATA__.templates;
const CATEGORY_META = __DATA__.category_meta;
const SPOTLIGHT = __DATA__.spotlight;

// Lookup map keyed by "{type}:{slug}" so cards can resolve back to data.
const TEMPLATE_LOOKUP = {};
TEMPLATES.forEach(t => { TEMPLATE_LOOKUP[t.type + ':' + t.slug] = t; });

// Preprocessed lowercase search index — built once at load time
const SEARCH_INDEX = TEMPLATES.map(t => ({
  template: t,
  name: t.name.toLowerCase(),
  description: t.description.toLowerCase(),
  category: t.category.toLowerCase(),
  tags: t.tags.map(tag => tag.toLowerCase()),
}));

// ── Helpers ──────────────────────────────────────────────────────────────────

// esc() sanitises user-derived strings before inserting them into innerHTML.
// It escapes & < > " and ' to prevent XSS when building HTML snippets.
// Only static markup strings may skip esc(). README HTML is the only content
// that flows through DOMPurify.sanitize(marked.parse(...)) instead.
function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function catIcon(slug) {
  return CATEGORY_META[slug] ? CATEGORY_META[slug][0] : '📁';
}

function catLabel(slug) {
  if (CATEGORY_META[slug]) return CATEGORY_META[slug][1];
  return slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function groupByCategory(templates) {
  const map = {};
  templates.forEach(t => {
    const c = t.category || 'uncategorised';
    if (!map[c]) map[c] = [];
    map[c].push(t);
  });
  return map;
}

function formatDuration(d) {
  if (!d) return '';
  return d.replace(/m$/, '\u202fmin').replace(/h$/, '\u202fhr');
}

// ── Category home view ────────────────────────────────────────────────────────

function buildSpotlight(t) {
  if (!t) return '';

  // tag strings are user-derived — flow through esc()
  const tags = t.tags.map(tag => `<span class="tag">${esc(tag)}</span>`).join('');

  const stats = [];
  if (t.task_count)    stats.push(`\u2714\ufe0f ${t.task_count}\u202ftask${t.task_count !== 1 ? 's' : ''}`);
  if (t.section_count) stats.push(`\u25b8 ${t.section_count}\u202fsection${t.section_count !== 1 ? 's' : ''}`);
  if (t.estimated_duration) stats.push(`\u23f1\ufe0f ${esc(formatDuration(t.estimated_duration))}`);
  if (t.recurrence_suggestion) stats.push(`🔁 ${esc(t.recurrence_suggestion)}`);

  const metaLine = [
    t.author  ? `by ${esc(t.author)}`  : '',
    t.version ? `v${esc(t.version)}` : '',
  ].filter(Boolean).join(' \u00b7 ');

  const previewHtml = t.rows && t.rows.length
    ? `<div class="spotlight-preview">${buildPreview(t.rows)}</div>`
    : '';

  // csv_url is a same-origin relative path produced by the build — safe to use directly
  const actionBtn = t.csv_url
    ? `<a class="btn-primary" href="${esc(t.csv_url)}" download>\u2b07\ufe0f Download CSV</a>`
    : '';

  return `
<div class="spotlight-section">
  <div class="spotlight-heading">\u2b50 Template Spotlight</div>
  <div class="spotlight-card tpl-card-clickable"
       data-slug="${esc(t.slug)}" data-type="${esc(t.type || 'template')}"
       role="button" tabindex="0"
       aria-label="View details for ${esc(t.name)}">
    <div class="spotlight-body">
      <div class="spotlight-badge">Featured Template</div>
      <div class="spotlight-name">${esc(t.name)}</div>
      ${t.description ? `<div class="spotlight-desc">${esc(t.description)}</div>` : ''}
      ${tags ? `<div class="spotlight-tags">${tags}</div>` : ''}
      ${stats.length ? `<div class="spotlight-stats">${stats.join('<span class="stat-sep">\u00b7</span>')}</div>` : ''}
      <div class="spotlight-footer">
        ${actionBtn}
        <span class="spotlight-meta">${metaLine}</span>
      </div>
    </div>
    ${previewHtml}
  </div>
</div>`;
}

function renderHome() {
  const groups = groupByCategory(TEMPLATES);
  const cats = Object.keys(groups).sort();
  const container = document.getElementById('container');

  let html = buildSpotlight(SPOTLIGHT);
  html += `<p class="intro">Browse <strong>${TEMPLATES.length}</strong> templates across <strong>${cats.length}</strong> categories.</p>
<div class="category-grid">`;

  cats.forEach(cat => {
    const items = groups[cat];
    const icon = catIcon(cat);
    // catLabel returns a derived string — esc() it before innerHTML insertion
    const label = catLabel(cat);
    const count = items.length;
    const MAX_PREVIEW = 4;
    const previews = items.slice(0, MAX_PREVIEW);
    const more = count - previews.length;

    // template names are user-derived — flow through esc()
    const previewItems = previews.map(t => `<li>${esc(t.name)}</li>`).join('');
    const moreHtml = more > 0 ? `<li class="cat-more">+\u202f${more} more</li>` : '';

    html += `
<div class="cat-card" role="button" tabindex="0"
     aria-label="Browse ${esc(label)} templates"
     data-category="${esc(cat)}">
  <div class="cat-icon">${icon}</div>
  <div class="cat-title">${esc(label)}</div>
  <div class="cat-count">${count}\u202ftemplate${count !== 1 ? 's' : ''}</div>
  <ul class="cat-previews">${previewItems}${moreHtml}</ul>
  <div class="cat-arrow">View all \u2192</div>
</div>`;
  });

  html += '</div>';
  // container.innerHTML is safe: all user-derived content above flows through esc()
  container.innerHTML = html;

  container.querySelectorAll('.cat-card').forEach(card => {
    card.addEventListener('click', () => navigate(card.dataset.category));
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') navigate(card.dataset.category);
    });
  });
}

// ── Template card ─────────────────────────────────────────────────────────────

function buildPreview(rows) {
  const MAX = 7;
  const shown = rows.slice(0, MAX);
  const rest = rows.length - shown.length;
  let html = '';
  shown.forEach(r => {
    const cls = r.type === 'section' ? 'section' : 'task';
    // content is user-derived — strip Todoist @mentions then esc()
    const content = r.content.replace(/@[\w-]+/g, '').trim();
    html += `<div class="preview-row ${cls}">${esc(content)}</div>`;
  });
  if (rest > 0) html += `<div class="preview-more">+\u202f${rest} more</div>`;
  return html;
}

function buildTemplateCard(t) {
  // All user-derived strings (name, description, tags, slug, author, version) flow through esc()
  const tags = t.tags.map(tag => `<span class="tag">${esc(tag)}</span>`).join('');

  const stats = [];
  if (t.task_count)    stats.push(`\u2714\ufe0f ${t.task_count}\u202ftask${t.task_count !== 1 ? 's' : ''}`);
  if (t.section_count) stats.push(`\u25b8 ${t.section_count}\u202fsection${t.section_count !== 1 ? 's' : ''}`);
  if (t.estimated_duration) stats.push(`\u23f1\ufe0f ${esc(formatDuration(t.estimated_duration))}`);
  if (t.recurrence_suggestion) stats.push(`🔁 ${esc(t.recurrence_suggestion)}`);

  const metaLine = [
    t.author  ? `by ${esc(t.author)}`  : '',
    t.version ? `v${esc(t.version)}` : '',
  ].filter(Boolean).join(' \u00b7 ');

  let previewHtml = '';
  if (t.type === 'template' && t.rows.length) {
    previewHtml = `<div class="tpl-preview">${buildPreview(t.rows)}</div>`;
  } else if (t.type === 'prompt' && t.inputs && t.inputs.length) {
    // input names are user-derived — flow through esc()
    const chips = t.inputs.map(i => `<span class="input-chip">${esc(i)}</span>`).join('');
    previewHtml = `<div class="tpl-inputs">
  <div class="tpl-inputs-label">Inputs</div>${chips}</div>`;
  }

  let actionBtn = '';
  if (t.type === 'template' && t.csv_url) {
    // csv_url is a same-origin relative path produced by the build — safe to use directly
    actionBtn = `<a class="btn-primary" href="${esc(t.csv_url)}" download>\u2b07\ufe0f Download CSV</a>`;
  } else if (t.type === 'prompt' && t.prompt_url) {
    // prompt_url is a same-origin relative path produced by the build — safe to use directly
    actionBtn = `<a class="btn-primary" href="${esc(t.prompt_url)}">View Prompt</a>`;
  }

  const badgeLabel = t.type === 'prompt' ? 'AI Prompt' : 'Template';

  return `<div class="tpl-card tpl-card-clickable" data-slug="${esc(t.slug)}" data-type="${esc(t.type)}"
     role="button" tabindex="0" aria-label="View details for ${esc(t.name)}">
  <div class="tpl-card-header">
    <span class="tpl-type-badge">${badgeLabel}</span>
    <div class="tpl-title">${esc(t.name)}</div>
    ${t.description ? `<div class="tpl-desc">${esc(t.description)}</div>` : ''}
  </div>
  ${tags ? `<div class="tpl-tags">${tags}</div>` : ''}
  ${stats.length ? `<div class="tpl-stats">${stats.join('<span class="stat-sep">\u00b7</span>')}</div>` : ''}
  ${previewHtml}
  <div class="tpl-card-footer">
    <span class="tpl-meta">${metaLine}</span>
    ${actionBtn}
  </div>
</div>`;
}

// ── Category detail view ──────────────────────────────────────────────────────

function renderCategory(cat) {
  const groups = groupByCategory(TEMPLATES);
  const items = groups[cat] || [];
  // catLabel / catIcon return derived strings — esc() before innerHTML insertion
  const label = catLabel(cat);
  const icon = catIcon(cat);
  const container = document.getElementById('container');

  const html = `
<div class="cat-detail-header">
  <span class="cat-detail-icon">${icon}</span>
  <div>
    <div class="cat-detail-title">${esc(label)}</div>
    <div class="cat-detail-count">${items.length}\u202ftemplate${items.length !== 1 ? 's' : ''}</div>
  </div>
</div>
<div class="template-grid">
  ${items.map(buildTemplateCard).join('')}
</div>`;

  // container.innerHTML is safe: category label flows through esc(), cards use esc() throughout
  container.innerHTML = html;
  // Use textContent (not innerHTML) for the breadcrumb label — no markup needed here
  document.getElementById('crumb-label').textContent = `${icon} ${label}`;
  document.getElementById('breadcrumb').style.display = 'block';
}

// ── Search ────────────────────────────────────────────────────────────────────

function matchesQuery(entry, query) {
  return (
    entry.name.includes(query) ||
    entry.description.includes(query) ||
    entry.category.includes(query) ||
    entry.tags.some(tag => tag.includes(query))
  );
}

function renderSearch(query) {
  const trimmed = query.trim();
  const container = document.getElementById('container');

  if (!trimmed) {
    renderHome();
    document.getElementById('breadcrumb').style.display = 'none';
    return;
  }

  const q = trimmed.toLowerCase();
  const results = SEARCH_INDEX.filter(entry => matchesQuery(entry, q)).map(entry => entry.template);

  // search summary: query string is user-derived — flow through esc()
  let html = `<p class="search-summary" role="status" aria-live="polite">`;
  if (results.length === 0) {
    html += `No results for <strong>${esc(trimmed)}</strong>`;
  } else {
    html += `<strong>${results.length}</strong> result${results.length !== 1 ? 's' : ''} for <strong>${esc(trimmed)}</strong>`;
  }
  html += `</p>`;

  if (results.length === 0) {
    html += `<div class="no-results">
  <div class="no-results-icon">🔍</div>
  <p>No templates matched your search. Try different keywords or browse by category.</p>
</div>`;
  } else {
    html += `<div class="template-grid">${results.map(buildTemplateCard).join('')}</div>`;
  }

  // container.innerHTML is safe: search query flows through esc(), cards use esc() throughout
  container.innerHTML = html;
  document.getElementById('breadcrumb').style.display = 'none';
}

// ── Hash-based routing ────────────────────────────────────────────────────────

function navigate(cat) {
  window.location.hash = '#/category/' + encodeURIComponent(cat);
}

function handleRoute() {
  const hash = window.location.hash;
  const match = hash.match(/^#\/category\/(.+)$/);
  if (match) {
    renderCategory(decodeURIComponent(match[1]));
    document.getElementById('breadcrumb').style.display = 'block';
  } else {
    renderHome();
    document.getElementById('breadcrumb').style.display = 'none';
  }
}

document.getElementById('btn-back').addEventListener('click', () => {
  document.getElementById('search-input').value = '';
  document.getElementById('search-clear').style.display = 'none';
  window.location.hash = '';
});

// ── Search input wiring ───────────────────────────────────────────────────────

const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');

searchInput.addEventListener('input', () => {
  const query = searchInput.value;
  searchClear.style.display = query ? 'block' : 'none';
  renderSearch(query);
});

searchClear.addEventListener('click', () => {
  searchInput.value = '';
  searchClear.style.display = 'none';
  renderHome();
  document.getElementById('breadcrumb').style.display = 'none';
  searchInput.focus();
});

window.addEventListener('hashchange', () => {
  // When navigating via hash, clear any active search
  if (searchInput.value) {
    searchInput.value = '';
    searchClear.style.display = 'none';
  }
  handleRoute();
});
handleRoute();

// ── Markdown sanitization — OWASP A03 (Injection) ────────────────────────────
// marked.parse() does not sanitize raw HTML by default, so any README containing
// <script>, inline event handlers, or <iframe> would execute on this origin.
// DOMPurify strips all dangerous markup before the HTML is handed to innerHTML.
// Reference: https://owasp.org/Top10/A03_2021-Injection/

// Add a post-sanitize hook so external links always open safely in a new tab.
if (typeof DOMPurify !== 'undefined') {
  DOMPurify.addHook('afterSanitizeAttributes', node => {
    if (node.tagName === 'A' && node.hasAttribute('href')) {
      const href = node.getAttribute('href');
      if (/^https?:|^mailto:/i.test(href)) {
        node.setAttribute('target', '_blank');
        node.setAttribute('rel', 'noopener noreferrer');
      }
    }
  });
}

function renderMarkdown(md) {
  if (!md) return '';
  if (typeof marked !== 'undefined' && marked.parse) {
    try {
      const raw = marked.parse(md, { mangle: false, headerIds: false, breaks: false });
      if (typeof DOMPurify !== 'undefined') {
        // Only README HTML flows through DOMPurify — no other path renders untrusted HTML.
        return DOMPurify.sanitize(raw, {
          USE_PROFILES: { html: true },
          ADD_ATTR: ['target', 'rel'],
        });
      }
      return raw;
    } catch (e) { /* fall through to escaped fallback */ }
  }
  // Fallback: render as preformatted text — safe
  return '<pre>' + esc(md) + '</pre>';
}

// ── Template detail modal ─────────────────────────────────────────────────
const modalBackdrop = document.getElementById('modal-backdrop');
const modalTitleEl  = document.getElementById('modal-title');
const modalSubtitle = document.getElementById('modal-subtitle');
const modalBody     = document.getElementById('modal-body');
const modalActions  = document.getElementById('modal-actions');
const modalCloseBtn = document.getElementById('modal-close');

let lastFocusedElement = null;

function openModal(template) {
  if (!template) return;
  // Use textContent for plain strings — no markup injection risk
  modalTitleEl.textContent = template.name;

  const subParts = [];
  if (template.category) subParts.push(catLabel(template.category));
  if (template.version) subParts.push('v' + template.version);
  if (template.author)  subParts.push('by ' + template.author);
  modalSubtitle.textContent = subParts.join(' · ');

  // Action buttons — keep download/view available without leaving the modal.
  // csv_url and prompt_url are same-origin relative paths produced by the build.
  // All user-derived strings (name, slug, type) flow through esc().
  let actionsHtml = '';
  if (template.type === 'template' && template.csv_url) {
    actionsHtml += `<a class="btn-primary" href="${esc(template.csv_url)}" download>⬇️ Download CSV</a>`;
  } else if (template.type === 'prompt' && template.prompt_url) {
    actionsHtml += `<a class="btn-primary" href="${esc(template.prompt_url)}" target="_blank" rel="noopener noreferrer">View Prompt</a>`;
  }
  // modalActions.innerHTML is safe: actionsHtml uses only esc()-wrapped values and static markup
  modalActions.innerHTML = actionsHtml;

  if (template.readme && template.readme.trim()) {
    modalBody.classList.remove('empty');
    // README content is untrusted user markdown — MUST flow through DOMPurify.sanitize(marked.parse(...))
    // This is the only path in the app that renders untrusted HTML into the DOM.
    modalBody.innerHTML = renderMarkdown(template.readme);
  } else {
    modalBody.classList.add('empty');
    // Static string — safe to assign directly
    modalBody.innerHTML = '<p>No README is available for this template yet.</p>';
  }

  // Make any links to repo-relative paths still resolve sensibly. README files
  // often link to other templates with relative paths like
  // `../other-template/` or `../../group/other-template/`. On the deployed
  // gallery (a single-page site rooted at /) those resolve to URLs that 404,
  // so intercept them: if the final path segment matches a known template or
  // prompt slug, open that template's modal instead of navigating away.
  // This runs after DOMPurify, so the DOM is already sanitized.
  modalBody.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (!href) return;
    if (/^https?:|^mailto:|^#/.test(href)) {
      // External and mailto links already handled by the DOMPurify afterSanitizeAttributes hook;
      // ensure rel is always noopener noreferrer (belt-and-suspenders).
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
      return;
    }
    const cleaned = href.split('#')[0].split('?')[0].replace(/\/+$/, '');
    if (!cleaned) return;
    const segments = cleaned.split('/').filter(s => s && s !== '.' && s !== '..');
    if (!segments.length) return;
    const lastSeg = segments[segments.length - 1].replace(/\.(md|csv)$/i, '');
    const target = TEMPLATE_LOOKUP['template:' + lastSeg] || TEMPLATE_LOOKUP['prompt:' + lastSeg];
    if (target) {
      a.addEventListener('click', e => {
        e.preventDefault();
        openModal(target);
      });
    }
  });

  lastFocusedElement = document.activeElement;
  modalBackdrop.classList.add('open');
  modalBackdrop.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  modalBody.scrollTop = 0;
  modalCloseBtn.focus();
}

function closeModal() {
  if (!modalBackdrop.classList.contains('open')) return;
  modalBackdrop.classList.remove('open');
  modalBackdrop.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
    lastFocusedElement.focus();
  }
}

modalCloseBtn.addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', e => {
  if (e.target === modalBackdrop) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

// Delegated click + keyboard handlers for template cards. Clicks on links or
// buttons inside the card are left to bubble to their own handlers, so the
// existing primary action (download / view prompt) keeps working without
// opening the modal.
document.addEventListener('click', e => {
  const card = e.target.closest('.tpl-card-clickable');
  if (!card) return;
  if (e.target.closest('a, button')) return;
  const template = TEMPLATE_LOOKUP[card.dataset.type + ':' + card.dataset.slug];
  openModal(template);
});

document.addEventListener('keydown', e => {
  if (e.key !== 'Enter' && e.key !== ' ') return;
  const card = e.target.closest && e.target.closest('.tpl-card-clickable');
  if (!card || e.target !== card) return;
  e.preventDefault();
  const template = TEMPLATE_LOOKUP[card.dataset.type + ':' + card.dataset.slug];
  openModal(template);
});
