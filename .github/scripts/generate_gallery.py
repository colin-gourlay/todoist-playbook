#!/usr/bin/env python3
"""Generate a browsable Template Gallery as a self-contained static HTML page.

Usage:
    python3 generate_gallery.py

Environment variables:
    TEMPLATES_DIR         Path to the templates folder (default: templates)
    PROMPT_TEMPLATES_DIR  Path to the prompt-templates folder (default: prompt-templates)
    OUTPUT_DIR            Path to the output folder (default: docs)
"""

import csv
import json
import os
import re
import shutil
import sys

TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "templates")
PROMPT_TEMPLATES_DIR = os.environ.get("PROMPT_TEMPLATES_DIR", "prompt-templates")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "docs")

# Category display metadata: slug -> (emoji, human-readable label)
CATEGORY_META = {
    "personal-systems":         ("🔁", "Personal Systems"),
    "engineering":              ("💻", "Engineering"),
    "agile":                    ("🔄", "Agile"),
    "career":                   ("🧑\u200d💼", "Career"),
    "creative":                 ("🎙", "Creative"),
    "saas-management":          ("☁️", "SaaS Management"),
    "professional-development": ("🎓", "Professional Development"),
    "brand-and-social":         ("🌐", "Brand & Social"),
    "radio-show-systems":       ("📻", "Radio Show Systems"),
    "content-generation":       ("🤖", "Content Generation"),
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_meta(path):
    """Parse a simple meta.yml file without a YAML library."""
    meta = {"tags": [], "inputs": []}
    in_list = None  # name of the current list key being parsed
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            # Detect start of a list block (e.g. "tags:" or "inputs:" with no value)
            m_list = re.match(r"^(tags|inputs):\s*$", line)
            if m_list:
                in_list = m_list.group(1)
                continue
            if in_list:
                m = re.match(r"^\s+-\s+(.+)$", line)
                if m:
                    meta[in_list].append(m.group(1).strip())
                    continue
                # Any non-indented line ends the list block
                if line and not line[0].isspace():
                    in_list = None
            m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if m:
                key = m.group(1)
                value = m.group(2).strip().strip("\"'")
                if key not in ("tags", "inputs"):
                    in_list = None
                    meta[key] = value
    return meta


def parse_csv_rows(path):
    """Return all valid (section/task) rows from a template CSV."""
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_type = row.get("TYPE", "").strip()
                content = row.get("CONTENT", "").strip()
                if row_type in ("section", "task") and content:
                    rows.append({
                        "type": row_type,
                        "content": content,
                        "priority": row.get("PRIORITY", "").strip(),
                        "indent": row.get("INDENT", "1").strip(),
                    })
    except Exception as exc:
        print(f"Warning: could not parse {path}: {exc}", file=sys.stderr)
    return rows


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def load_templates():
    templates = []

    # Load CSV templates
    if os.path.isdir(TEMPLATES_DIR):
        for slug in sorted(os.listdir(TEMPLATES_DIR)):
            template_dir = os.path.join(TEMPLATES_DIR, slug)
            if not os.path.isdir(template_dir):
                continue
            meta_path = os.path.join(template_dir, "meta.yml")
            csv_path = os.path.join(template_dir, "template.csv")
            if not os.path.exists(meta_path):
                continue
            meta = parse_meta(meta_path)
            rows = parse_csv_rows(csv_path) if os.path.exists(csv_path) else []
            task_count = sum(1 for r in rows if r["type"] == "task")
            section_count = sum(1 for r in rows if r["type"] == "section")
            templates.append({
                "slug": slug,
                "name": meta.get("name", slug),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "tags": meta.get("tags", []),
                "estimated_duration": meta.get("estimated_duration", ""),
                "recurrence_suggestion": meta.get("recurrence_suggestion", ""),
                "author": meta.get("author", ""),
                "version": meta.get("version", ""),
                "task_count": task_count,
                "section_count": section_count,
                "rows": rows,
                "csv_url": f"templates/{slug}/template.csv",
                "prompt_url": "",
                "inputs": [],
                "type": "template",
            })

    # Load prompt templates
    if os.path.isdir(PROMPT_TEMPLATES_DIR):
        for slug in sorted(os.listdir(PROMPT_TEMPLATES_DIR)):
            template_dir = os.path.join(PROMPT_TEMPLATES_DIR, slug)
            if not os.path.isdir(template_dir):
                continue
            meta_path = os.path.join(template_dir, "meta.yml")
            if not os.path.exists(meta_path):
                continue
            meta = parse_meta(meta_path)
            templates.append({
                "slug": slug,
                "name": meta.get("name", slug),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "tags": meta.get("tags", []),
                "estimated_duration": "",
                "recurrence_suggestion": "",
                "author": meta.get("author", ""),
                "version": meta.get("version", ""),
                "task_count": 0,
                "section_count": 0,
                "rows": [],
                "csv_url": "",
                "prompt_url": f"prompt-templates/{slug}/prompt.md",
                "inputs": meta.get("inputs", []),
                "type": "prompt",
            })

    return templates


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(templates):
    templates_json = json.dumps(templates, ensure_ascii=False)
    category_meta_json = json.dumps(CATEGORY_META, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todoist Playbook — Template Gallery</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --red: #db4035;
      --red-dark: #b83227;
      --red-light: #fdecea;
      --bg: #fafafa;
      --card-bg: #ffffff;
      --text: #202020;
      --muted: #666666;
      --border: #e5e5e5;
      --tag-bg: #f0f0f0;
      --section-color: #7b68ee;
      --radius: 10px;
      --shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.05);
      --shadow-hover: 0 8px 24px rgba(0,0,0,0.12);
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
    }}

    /* ── Header ── */
    .site-header {{
      background: var(--red);
      color: #fff;
      padding: 2rem 1rem 1.75rem;
      text-align: center;
    }}
    .site-header h1 {{
      font-size: 1.8rem;
      font-weight: 800;
      letter-spacing: -0.03em;
    }}
    .site-header p {{
      margin-top: 0.4rem;
      opacity: 0.88;
      font-size: 1rem;
    }}

    /* ── Breadcrumb bar ── */
    .breadcrumb {{
      display: none;
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 0.75rem 1.5rem;
    }}
    .breadcrumb button {{
      background: none;
      border: none;
      cursor: pointer;
      color: var(--red);
      font-size: 0.9rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0;
    }}
    .breadcrumb button:hover {{ text-decoration: underline; }}
    .breadcrumb .crumb-sep {{ color: var(--muted); margin: 0 0.4rem; }}
    .breadcrumb .crumb-current {{
      color: var(--text);
      font-weight: 600;
      font-size: 0.9rem;
    }}

    /* ── Container ── */
    .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem; }}

    /* ── Intro text ── */
    .intro {{ font-size: 0.95rem; color: var(--muted); margin-bottom: 1.75rem; }}

    /* ── Category grid ── */
    .category-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.25rem;
    }}

    /* ── Category card ── */
    .cat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 1.5rem;
      cursor: pointer;
      transition: box-shadow 0.18s, transform 0.18s;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      color: inherit;
      text-decoration: none;
    }}
    .cat-card:hover {{
      box-shadow: var(--shadow-hover);
      transform: translateY(-2px);
    }}
    .cat-card:focus-visible {{
      outline: 3px solid var(--red);
      outline-offset: 2px;
    }}
    .cat-icon {{ font-size: 2.2rem; line-height: 1; }}
    .cat-title {{ font-size: 1.1rem; font-weight: 700; }}
    .cat-count {{
      font-size: 0.82rem;
      color: var(--red);
      font-weight: 600;
    }}
    .cat-previews {{
      list-style: none;
      font-size: 0.82rem;
      color: var(--muted);
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}
    .cat-previews li::before {{ content: "▸ "; opacity: 0.4; }}
    .cat-more {{
      font-size: 0.78rem;
      color: var(--muted);
      font-style: italic;
    }}
    .cat-arrow {{
      margin-top: auto;
      font-size: 0.82rem;
      color: var(--red);
      font-weight: 600;
    }}

    /* ── Category detail heading ── */
    .cat-detail-header {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 1.5rem;
    }}
    .cat-detail-icon {{ font-size: 2rem; line-height: 1; }}
    .cat-detail-title {{ font-size: 1.4rem; font-weight: 700; }}
    .cat-detail-count {{ font-size: 0.9rem; color: var(--muted); margin-top: 0.15rem; }}

    /* ── Template grid ── */
    .template-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.25rem;
    }}

    /* ── Template card ── */
    .tpl-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: box-shadow 0.18s;
    }}
    .tpl-card:hover {{ box-shadow: var(--shadow-hover); }}

    .tpl-card-header {{ padding: 1.1rem 1.1rem 0.5rem; }}
    .tpl-type-badge {{
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--red);
      background: var(--red-light);
      border-radius: 999px;
      padding: 0.18rem 0.55rem;
      margin-bottom: 0.4rem;
    }}
    .tpl-title {{ font-size: 1.05rem; font-weight: 700; }}
    .tpl-desc {{ font-size: 0.87rem; color: var(--muted); margin-top: 0.3rem; }}

    .tpl-tags {{
      padding: 0.4rem 1.1rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
    }}
    .tag {{
      padding: 0.18rem 0.55rem;
      background: var(--tag-bg);
      border-radius: 999px;
      font-size: 0.74rem;
      color: var(--muted);
    }}

    .tpl-stats {{
      padding: 0.25rem 1.1rem 0.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      font-size: 0.78rem;
      color: var(--muted);
    }}

    /* Preview rows */
    .tpl-preview {{
      margin: 0 1.1rem 0.75rem;
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
      font-size: 0.79rem;
    }}
    .preview-row {{
      padding: 0.25rem 0.6rem;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .preview-row:last-child {{ border-bottom: none; }}
    .preview-row.section {{
      font-weight: 600;
      background: #fafafa;
      color: var(--section-color);
      font-size: 0.73rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .preview-row.task {{ color: var(--text); padding-left: 1.1rem; }}
    .preview-more {{
      padding: 0.25rem 0.6rem;
      color: var(--muted);
      font-size: 0.74rem;
      background: #fafafa;
    }}

    /* Prompt inputs */
    .tpl-inputs {{ margin: 0 1.1rem 0.75rem; font-size: 0.82rem; }}
    .tpl-inputs-label {{ font-weight: 600; color: var(--muted); margin-bottom: 0.25rem; }}
    .input-chip {{
      display: inline-block;
      background: var(--tag-bg);
      border-radius: 999px;
      padding: 0.15rem 0.5rem;
      margin: 0.1rem 0.15rem 0.1rem 0;
      font-size: 0.74rem;
      font-family: monospace;
      color: var(--text);
    }}

    .tpl-card-footer {{
      padding: 0.75rem 1.1rem;
      margin-top: auto;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }}
    .tpl-meta {{ font-size: 0.74rem; color: var(--muted); }}
    .btn-primary {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.45rem 0.9rem;
      background: var(--red);
      color: #fff;
      border-radius: var(--radius);
      font-size: 0.82rem;
      font-weight: 600;
      text-decoration: none;
      transition: background 0.15s;
      white-space: nowrap;
    }}
    .btn-primary:hover {{ background: var(--red-dark); }}

    /* ── Responsive ── */
    @media (max-width: 540px) {{
      .site-header h1 {{ font-size: 1.4rem; }}
      .category-grid, .template-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<header class="site-header">
  <h1>📋 Todoist Playbook</h1>
  <p>Curated templates for getting things done</p>
</header>

<nav class="breadcrumb" id="breadcrumb" aria-label="Breadcrumb">
  <button id="btn-back" aria-label="Back to all categories">← All Categories</button>
  <span class="crumb-sep" aria-hidden="true">/</span>
  <span class="crumb-current" id="crumb-label"></span>
</nav>

<div class="container" id="container">
  <!-- Populated by JavaScript -->
</div>

<script>
const TEMPLATES = {templates_json};
const CATEGORY_META = {category_meta_json};

// ── Helpers ──────────────────────────────────────────────────────────────────

function esc(str) {{
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}}

function catIcon(slug) {{
  return CATEGORY_META[slug] ? CATEGORY_META[slug][0] : '📁';
}}

function catLabel(slug) {{
  if (CATEGORY_META[slug]) return CATEGORY_META[slug][1];
  return slug.replace(/-/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}}

function groupByCategory(templates) {{
  const map = {{}};
  templates.forEach(t => {{
    const c = t.category || 'uncategorised';
    if (!map[c]) map[c] = [];
    map[c].push(t);
  }});
  return map;
}}

function formatDuration(d) {{
  if (!d) return '';
  return d.replace(/m$/, '\u202fmin').replace(/h$/, '\u202fhr');
}}

// ── Category home view ────────────────────────────────────────────────────────

function renderHome() {{
  const groups = groupByCategory(TEMPLATES);
  const cats = Object.keys(groups).sort();
  const container = document.getElementById('container');

  let html = `<p class="intro">Browse <strong>${{TEMPLATES.length}}</strong> templates across <strong>${{cats.length}}</strong> categories.</p>
<div class="category-grid">`;

  cats.forEach(cat => {{
    const items = groups[cat];
    const icon = catIcon(cat);
    const label = catLabel(cat);
    const count = items.length;
    const MAX_PREVIEW = 4;
    const previews = items.slice(0, MAX_PREVIEW);
    const more = count - previews.length;

    const previewItems = previews.map(t => `<li>${{esc(t.name)}}</li>`).join('');
    const moreHtml = more > 0 ? `<li class="cat-more">+\u202f${{more}} more</li>` : '';

    html += `
<div class="cat-card" role="button" tabindex="0"
     aria-label="Browse ${{esc(label)}} templates"
     data-category="${{esc(cat)}}">
  <div class="cat-icon">${{icon}}</div>
  <div class="cat-title">${{esc(label)}}</div>
  <div class="cat-count">${{count}}\u202ftemplate${{count !== 1 ? 's' : ''}}</div>
  <ul class="cat-previews">${{previewItems}}${{moreHtml}}</ul>
  <div class="cat-arrow">View all \u2192</div>
</div>`;
  }});

  html += '</div>';
  container.innerHTML = html;

  container.querySelectorAll('.cat-card').forEach(card => {{
    card.addEventListener('click', () => navigate(card.dataset.category));
    card.addEventListener('keydown', e => {{
      if (e.key === 'Enter' || e.key === ' ') navigate(card.dataset.category);
    }});
  }});
}}

// ── Template card ─────────────────────────────────────────────────────────────

function buildPreview(rows) {{
  const MAX = 7;
  const shown = rows.slice(0, MAX);
  const rest = rows.length - shown.length;
  let html = '';
  shown.forEach(r => {{
    const cls = r.type === 'section' ? 'section' : 'task';
    const content = r.content.replace(/@[\\w-]+/g, '').trim();
    html += `<div class="preview-row ${{cls}}">${{esc(content)}}</div>`;
  }});
  if (rest > 0) html += `<div class="preview-more">+\u202f${{rest}} more</div>`;
  return html;
}}

function buildTemplateCard(t) {{
  const tags = t.tags.map(tag => `<span class="tag">${{esc(tag)}}</span>`).join('');

  const stats = [];
  if (t.task_count)    stats.push(`\u2714\ufe0f ${{t.task_count}}\u202ftask${{t.task_count !== 1 ? 's' : ''}}`);
  if (t.section_count) stats.push(`\u25b8 ${{t.section_count}}\u202fsection${{t.section_count !== 1 ? 's' : ''}}`);
  if (t.estimated_duration) stats.push(`\u23f1\ufe0f ${{esc(formatDuration(t.estimated_duration))}}`);
  if (t.recurrence_suggestion) stats.push(`🔁 ${{esc(t.recurrence_suggestion)}}`);

  const metaLine = [
    t.author  ? `by ${{esc(t.author)}}`  : '',
    t.version ? `v${{esc(t.version)}}` : '',
  ].filter(Boolean).join(' \u00b7 ');

  let previewHtml = '';
  if (t.type === 'template' && t.rows.length) {{
    previewHtml = `<div class="tpl-preview">${{buildPreview(t.rows)}}</div>`;
  }} else if (t.type === 'prompt' && t.inputs && t.inputs.length) {{
    const chips = t.inputs.map(i => `<span class="input-chip">${{esc(i)}}</span>`).join('');
    previewHtml = `<div class="tpl-inputs">
  <div class="tpl-inputs-label">Inputs</div>${{chips}}</div>`;
  }}

  let actionBtn = '';
  if (t.type === 'template' && t.csv_url) {{
    actionBtn = `<a class="btn-primary" href="${{esc(t.csv_url)}}" download>\u2b07\ufe0f Download CSV</a>`;
  }} else if (t.type === 'prompt' && t.prompt_url) {{
    actionBtn = `<a class="btn-primary" href="${{esc(t.prompt_url)}}">View Prompt</a>`;
  }}

  const badgeLabel = t.type === 'prompt' ? 'AI Prompt' : 'Template';

  return `<div class="tpl-card">
  <div class="tpl-card-header">
    <span class="tpl-type-badge">${{badgeLabel}}</span>
    <div class="tpl-title">${{esc(t.name)}}</div>
    ${{t.description ? `<div class="tpl-desc">${{esc(t.description)}}</div>` : ''}}
  </div>
  ${{tags ? `<div class="tpl-tags">${{tags}}</div>` : ''}}
  ${{stats.length ? `<div class="tpl-stats">${{stats.join('<span style="margin:0 .2rem;opacity:.4">\u00b7</span>')}}</div>` : ''}}
  ${{previewHtml}}
  <div class="tpl-card-footer">
    <span class="tpl-meta">${{metaLine}}</span>
    ${{actionBtn}}
  </div>
</div>`;
}}

// ── Category detail view ──────────────────────────────────────────────────────

function renderCategory(cat) {{
  const groups = groupByCategory(TEMPLATES);
  const items = groups[cat] || [];
  const label = catLabel(cat);
  const icon = catIcon(cat);
  const container = document.getElementById('container');

  const html = `
<div class="cat-detail-header">
  <span class="cat-detail-icon">${{icon}}</span>
  <div>
    <div class="cat-detail-title">${{esc(label)}}</div>
    <div class="cat-detail-count">${{items.length}}\u202ftemplate${{items.length !== 1 ? 's' : ''}}</div>
  </div>
</div>
<div class="template-grid">
  ${{items.map(buildTemplateCard).join('')}}
</div>`;

  container.innerHTML = html;
  document.getElementById('crumb-label').textContent = `${{icon}} ${{label}}`;
  document.getElementById('breadcrumb').style.display = 'block';
}}

// ── Hash-based routing ────────────────────────────────────────────────────────

function navigate(cat) {{
  window.location.hash = '#/category/' + encodeURIComponent(cat);
}}

function handleRoute() {{
  const hash = window.location.hash;
  const match = hash.match(/^#\\/category\\/(.+)$/);
  if (match) {{
    renderCategory(decodeURIComponent(match[1]));
    document.getElementById('breadcrumb').style.display = 'block';
  }} else {{
    renderHome();
    document.getElementById('breadcrumb').style.display = 'none';
  }}
}}

document.getElementById('btn-back').addEventListener('click', () => {{
  window.location.hash = '';
}});

window.addEventListener('hashchange', handleRoute);
handleRoute();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: templates directory not found: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Disable Jekyll processing on GitHub Pages
    with open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w"):
        pass

    # Copy each template's CSV into the output directory so download links work
    for slug in os.listdir(TEMPLATES_DIR):
        template_dir = os.path.join(TEMPLATES_DIR, slug)
        csv_src = os.path.join(template_dir, "template.csv")
        if os.path.isdir(template_dir) and os.path.exists(csv_src):
            dest_dir = os.path.join(OUTPUT_DIR, "templates", slug)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(csv_src, os.path.join(dest_dir, "template.csv"))

    # Copy each prompt template's prompt.md into the output directory
    if os.path.isdir(PROMPT_TEMPLATES_DIR):
        for slug in os.listdir(PROMPT_TEMPLATES_DIR):
            template_dir = os.path.join(PROMPT_TEMPLATES_DIR, slug)
            prompt_src = os.path.join(template_dir, "prompt.md")
            if os.path.isdir(template_dir) and os.path.exists(prompt_src):
                dest_dir = os.path.join(OUTPUT_DIR, "prompt-templates", slug)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(prompt_src, os.path.join(dest_dir, "prompt.md"))

    templates = load_templates()
    html = generate_html(templates)

    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Gallery generated: {output_path} ({len(templates)} templates)")


if __name__ == "__main__":
    main()
